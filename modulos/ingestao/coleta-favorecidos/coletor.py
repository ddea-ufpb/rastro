"""Coletor dos favorecidos (pessoa jurídica) das emendas parlamentares ligadas à Paraíba.

Trabalho 2, Etapa 1 (DINF00071). Sem modelo: baixa, extrai, normaliza, deduplica e grava.

Uso:
    python coletor.py            # reaproveita o bruto mais recente em bruto/; se não houver, baixa
    python coletor.py --baixar   # baixa a fonte de novo e gera um bruto com a data de hoje

Saídas (nesta pasta): corpus.jsonl, descartes.jsonl.
Um item do corpus é uma entidade favorecida (um CNPJ), com os pagamentos que recebeu.
Nomes de campo seguem especificacoes/sarah-araujo/arquitetura/contratos/modelo-dados.md (pagamento_favorecido).
"""
import csv
import datetime
import hashlib
import io
import json
import re
import sys
import urllib.request
import zipfile
from pathlib import Path

URL = 'https://portaldatransparencia.gov.br/download-de-dados/emendas-parlamentares/UNICO'
AQUI = Path(__file__).resolve().parent
BRUTO = AQUI / 'bruto'
ARQ_EMENDAS = 'EmendasParlamentares.csv'
ARQ_FAVORECIDOS = 'EmendasParlamentares_PorFavorecido.csv'
CABECALHO = ['Código da Emenda', 'Código do Autor da Emenda', 'Nome do Autor da Emenda', 'Número da emenda',
             'Tipo de Emenda', 'Ano/Mês', 'Código do Favorecido', 'Favorecido', 'Natureza Jurídica',
             'Tipo Favorecido', 'UF Favorecido', 'Município Favorecido', 'Valor Recebido']
SEM_INFO = {'Sem informação', 'S/I'}
# Empresário individual é uma pessoa: o nome é o dela e às vezes traz o CPF inteiro (ver REGRAS.md, R-EI).
NATUREZA_PESSOA = 'Empresário (Individual)'
UF_PB_IBGE = '2500000'


class Descarte(Exception):
    """Item que não entra no corpus; a mensagem é o motivo."""


def ler_csv(dados: bytes):
    """Linhas da fonte: Windows-1252, separador ';', tudo entre aspas, fim de linha \\r\\n."""
    return csv.reader(io.StringIO(dados.decode('cp1252'), newline=''), delimiter=';')


# 1. OBTER — baixa a fonte e guarda o bruto antes de mexer -------------------------------------------

def baixar(destino_dir: Path):
    req = urllib.request.Request(URL, headers={'User-Agent': 'rastro-coletor/1.0'})
    with urllib.request.urlopen(req, timeout=300) as resp:
        dados = resp.read()
        cab = {k: resp.headers.get(k) for k in ('ETag', 'Last-Modified', 'Content-Length')}
        url_final = resp.geturl()
    hoje = datetime.date.today().isoformat()
    zip_path = destino_dir / f'EmendasParlamentares-{hoje}.zip'  # fora do git (.gitignore): tem pessoa física
    zip_path.write_bytes(dados)
    return zip_path, {'url': URL, 'url_final': url_final, 'coletado_em': hoje, **cab,
                      'sha256_zip': hashlib.sha256(dados).hexdigest()}


def obter(baixar_de_novo=False):
    """Devolve (caminho do extrato bruto, manifesto).

    O extrato é o recorte copiado byte a byte do CSV original: linhas de favorecido ligadas à PB
    (emenda com UF PB ou favorecido com UF PB, como em REQ-52), sem pessoa física nem empresário
    individual. Essas linhas do recorte viram descarte já aqui, guardando só a posição no arquivo original e o motivo.
    """
    extratos = sorted(BRUTO.glob('favorecidos-pb-*.csv'))
    if extratos and not baixar_de_novo:
        ext = extratos[-1]
        return ext, json.loads(ext.with_suffix('.manifesto.json').read_text(encoding='utf8'))

    zip_path, manifesto = baixar(BRUTO)
    z = zipfile.ZipFile(zip_path)
    emendas = ler_csv(z.read(ARQ_EMENDAS))
    cab = next(emendas)
    i_cod, i_uf = cab.index('Código da Emenda'), cab.index('Código UF IBGE')
    emendas_pb = {l[i_cod] for l in emendas if l[i_uf] == UF_PB_IBGE and l[i_cod] not in SEM_INFO}

    brutas = z.read(ARQ_FAVORECIDOS).split(b'\r\n')
    if brutas and brutas[-1] == b'':
        brutas.pop()
    cab = next(ler_csv(brutas[0]))
    if cab != CABECALHO:
        raise SystemExit(f'cabeçalho inesperado em {ARQ_FAVORECIDOS}: {cab}')
    i_cod, i_uf, i_tipo = cab.index('Código da Emenda'), cab.index('UF Favorecido'), cab.index('Tipo Favorecido')
    i_nat = cab.index('Natureza Jurídica')

    manter, descartes_pf, fora = [brutas[0]], [], 0
    for n, linha in enumerate(brutas[1:], start=2):
        campos = next(ler_csv(linha))
        if len(campos) != len(CABECALHO):
            manter.append(linha)  # normalizar() descarta com motivo e linha
            continue
        if campos[i_cod] not in emendas_pb and campos[i_uf] != 'PB':
            fora += 1
            continue
        motivo = motivo_tipo(campos[i_tipo], campos[i_nat])
        if motivo:  # fora do extrato: pode ser pessoa; guarda só posição e motivo
            descartes_pf.append({'fonte': f'{ARQ_FAVORECIDOS}:{n}', 'motivo': motivo})
            continue
        manter.append(linha)

    ext = BRUTO / f'favorecidos-pb-{manifesto["coletado_em"]}.csv'
    ext.write_bytes(b'\r\n'.join(manter) + b'\r\n')
    manifesto.update({
        'arquivo_original': ARQ_FAVORECIDOS,
        'linhas_original': len(brutas) - 1,
        'linhas_fora_do_recorte': fora,
        'linhas_no_extrato': len(manter) - 1,
        'emendas_pb': len(emendas_pb),
        'descartes_na_obtencao': descartes_pf,
        'licenca': 'Dados abertos do Portal da Transparência (CGU), Lei 12.527/2011; citar a fonte.',
    })
    ext.with_suffix('.manifesto.json').write_text(json.dumps(manifesto, ensure_ascii=False, indent=1), encoding='utf8')
    return ext, manifesto


# 2. EXTRAIR — do CSV para registros -----------------------------------------------------------------

def extrair(ext: Path):
    linhas = ler_csv(ext.read_bytes())
    cab = next(linhas)
    for n, campos in enumerate(linhas, start=2):
        yield {'_fonte': f'bruto/{ext.name}:{n}', '_campos': campos, **dict(zip(cab, campos))}


# 3. NORMALIZAR — uma regra por transformação ---------------------------------------------------------

def cnpj_valido(c: str) -> bool:
    if not re.fullmatch(r'\d{14}', c) or len(set(c)) == 1:
        return False
    def dv(base, pesos):
        r = sum(int(d) * p for d, p in zip(base, pesos)) % 11
        return '0' if r < 2 else str(11 - r)
    p1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    d1 = dv(c[:12], p1)
    return c[12] == d1 and c[13] == dv(c[:12] + d1, [6] + p1)


def motivo_tipo(tipo: str, natureza: str):
    """Só pessoa jurídica com CNPJ entra. Devolve o motivo do descarte, ou None."""
    if tipo == 'Pessoa Fisica':  # R-PF
        return 'favorecido_pessoa_fisica'
    if tipo == 'Unidade Gestora':  # R-UG
        return 'unidade_gestora_sem_cnpj'
    if tipo in ('Sem informação', 'Inválido'):  # R-SEMFAV
        return 'favorecido_nao_identificado'
    if tipo != 'Pessoa Jurídica':  # R-TIPO: ex. "Inscrição Genéric" com nome de pessoa
        return 'favorecido_tipo_desconhecido'
    if natureza == NATUREZA_PESSOA:  # R-EI
        return 'favorecido_empresario_individual'
    return None


def texto(s: str) -> str:  # R-TEXTO
    return re.sub(r'\s+', ' ', s).strip()


def nulo_se_sem_info(s: str):  # R-SEMINFO
    s = texto(s)
    return None if s in SEM_INFO else s


def normalizar(reg: dict) -> dict:
    if len(reg['_campos']) != len(CABECALHO):  # R-COLUNAS
        raise Descarte('numero_de_colunas_inesperado')
    motivo = motivo_tipo(reg['Tipo Favorecido'], reg['Natureza Jurídica'])  # já filtrado na obtenção; defesa em profundidade
    if motivo:
        raise Descarte(motivo)
    codigo = texto(reg['Código do Favorecido'])
    if not cnpj_valido(codigo):  # R-CNPJ
        raise Descarte('cnpj_invalido')
    nome = texto(reg['Favorecido'])
    if not nome:  # R-NOME
        raise Descarte('favorecido_nome_ausente')
    valor = reg['Valor Recebido']
    if not re.fullmatch(r'-?\d+,\d{2}', valor):  # R-VALOR (formato de REQ-48)
        raise Descarte('valor_fora_do_formato')
    ano_mes = reg['Ano/Mês']
    if not re.fullmatch(r'20\d{2}(0[1-9]|1[0-2])', ano_mes):  # R-ANOMES
        raise Descarte('ano_mes_fora_do_formato')
    return {
        'codigo_favorecido': codigo,
        'favorecido_nome': nome,
        'natureza_juridica': nulo_se_sem_info(reg['Natureza Jurídica']),
        'uf_favorecido': uf if re.fullmatch(r'[A-Z]{2}', uf := texto(reg['UF Favorecido'])) else None,  # R-UF
        'municipio_favorecido_nome': nulo_se_sem_info(reg['Município Favorecido']),
        'pagamento': {
            'codigo_emenda': nulo_se_sem_info(reg['Código da Emenda']),
            'ano_mes': ano_mes,
            'valor_recebido': valor.replace(',', '.'),  # string: sem float em dinheiro
            'fonte': reg['_fonte'],
        },
    }


# 4. DEDUPLICAR — chave estável: o CNPJ ---------------------------------------------------------------

def chave(codigo_favorecido: str) -> str:
    return hashlib.sha256(codigo_favorecido.encode()).hexdigest()[:16]


def agrupar(normalizados, coletado_em):
    itens = {}
    for r in normalizados:
        k = chave(r['codigo_favorecido'])
        if k not in itens:
            itens[k] = {
                'id': f'rastro-fav-{r["codigo_favorecido"]}',
                'texto': r['favorecido_nome'],
                'campos': {c: r[c] for c in ('codigo_favorecido', 'favorecido_nome', 'natureza_juridica',
                                             'uf_favorecido', 'municipio_favorecido_nome')} | {'pagamentos': []},
                'fonte': r['pagamento']['fonte'],
                'coletado_em': coletado_em,
                'chave': k,
            }
        it = itens[k]['campos']
        # Na T1 cada CNPJ tinha um nome só; se um dia vier outro, falha em vez de esconder.
        assert it['favorecido_nome'] == r['favorecido_nome'], (r['codigo_favorecido'], r['favorecido_nome'])
        it['pagamentos'].append(r['pagamento'])
    for it in itens.values():
        c = it['campos']
        c['total_pagamentos'] = len(c['pagamentos'])
        c['valor_recebido_total'] = f'{sum(int(p["valor_recebido"].replace(".", "")) for p in c["pagamentos"]) / 100:.2f}'
    return itens


# 5. GRAVAR — uma linha JSON por item, ordem estável -----------------------------------------------

def gravar(itens: dict, descartes: list):
    with open(AQUI / 'corpus.jsonl', 'w', encoding='utf8', newline='\n') as f:
        for k in sorted(itens):
            f.write(json.dumps(itens[k], ensure_ascii=False) + '\n')
    with open(AQUI / 'descartes.jsonl', 'w', encoding='utf8', newline='\n') as f:
        for d in descartes:
            f.write(json.dumps(d, ensure_ascii=False) + '\n')


def main(argv):
    ext, manifesto = obter(baixar_de_novo='--baixar' in argv)
    descartes = list(manifesto['descartes_na_obtencao'])
    normalizados = []
    for reg in extrair(ext):
        try:
            normalizados.append(normalizar(reg))
        except Descarte as d:
            descartes.append({'fonte': reg['_fonte'], 'motivo': str(d)})
    itens = agrupar(normalizados, manifesto['coletado_em'])
    gravar(itens, descartes)
    motivos = {}
    for d in descartes:
        motivos[d['motivo']] = motivos.get(d['motivo'], 0) + 1
    print(f'extrato {ext.name}: {len(normalizados)} pagamentos, {len(itens)} entidades no corpus; descartes {motivos}')


if __name__ == '__main__':
    main(sys.argv[1:])
