"""Testes das regras de normalização. Rodar: python -m pytest test_coletor.py (ou python test_coletor.py)."""
from coletor import CABECALHO, Descarte, cnpj_valido, normalizar


def reg(**over):
    base = dict(zip(CABECALHO, ['202571160002', '7116', 'BANCADA DA PARAIBA', '0002', 'Emenda de Bancada', '202510',
                                '11332636000157', 'FUNDO MUNICIPAL DE SAUDE  - FMSCI', 'Fundo Público da Administração Direta Municipal',
                                'Pessoa Jurídica', 'PB', 'CACHOEIRA DOS ÍNDIOS', '600000,00']))
    base.update(over)
    return {'_fonte': 'bruto/x.csv:2', '_campos': list(base.values()), **base}


def motivo(r):
    try:
        normalizar(r)
    except Descarte as d:
        return str(d)


def test_linha_valida():
    n = normalizar(reg())
    assert n['favorecido_nome'] == 'FUNDO MUNICIPAL DE SAUDE - FMSCI'  # R-TEXTO colapsa espaços
    assert n['pagamento']['valor_recebido'] == '600000.00'
    assert n['pagamento']['ano_mes'] == '202510'
    assert normalizar(reg(**{'UF Favorecido': '-1'}))['uf_favorecido'] is None  # R-UF


def test_sem_informacao_vira_nulo():
    n = normalizar(reg(**{'Código da Emenda': 'Sem informação', 'Natureza Jurídica': 'Sem informação'}))
    assert n['pagamento']['codigo_emenda'] is None and n['natureza_juridica'] is None


def test_descartes():
    assert motivo(reg(**{'Tipo Favorecido': 'Pessoa Fisica'})) == 'favorecido_pessoa_fisica'
    assert motivo(reg(**{'Natureza Jurídica': 'Empresário (Individual)'})) == 'favorecido_empresario_individual'
    assert motivo(reg(**{'Tipo Favorecido': 'Sem informação', 'Código do Favorecido': '-8'})) == 'favorecido_nao_identificado'
    assert motivo(reg(**{'Tipo Favorecido': 'Unidade Gestora', 'Código do Favorecido': '153065'})) == 'unidade_gestora_sem_cnpj'
    assert motivo(reg(**{'Tipo Favorecido': 'Inscrição Genéric', 'Código do Favorecido': 'EXUFPB087'})) == 'favorecido_tipo_desconhecido'
    assert motivo(reg(**{'Código do Favorecido': '11332636000158'})) == 'cnpj_invalido'
    assert motivo(reg(**{'Valor Recebido': '600.000,00'})) == 'valor_fora_do_formato'
    assert motivo(reg(**{'Ano/Mês': '202513'})) == 'ano_mes_fora_do_formato'


def test_cnpj():
    assert cnpj_valido('08761124000100')  # ESTADO DA PARAIBA, da fonte
    assert not cnpj_valido('00000000000000') and not cnpj_valido('0876112400010')


if __name__ == '__main__':
    for nome, f in list(globals().items()):
        if nome.startswith('test_'):
            f()
    print('ok')
