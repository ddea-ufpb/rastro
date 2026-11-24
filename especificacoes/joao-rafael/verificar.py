"""Confere a coerência da especificação do Rastro (João Rafael).

Uso:
    python verificar.py             # confere e sai com 1 se algo falhar
    python verificar.py --escrever  # também regenera a coluna "Telas" de requisitos.md

Precisa de PyYAML. Com openapi-spec-validator instalado, também valida o OpenAPI.
"""
import re
import sys
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent
TELAS = RAIZ / "telas"
ARQ = RAIZ / "arquitetura"
REQS_MD = ARQ / "requisitos.md"

CAMPOS = [
    "Superfície · ator", "Objetivo", "Chega de / vai para", "Mostra", "Coleta",
    "Ações", "Estados", "Regras", "Requisitos · contrato", "Acessibilidade", "Anexo",
]
ESTADOS = ["carregando", "vazio", "erro", "sucesso", "offline", "sem permissão"]
ACAO_LOCAL = "ação local · sem chamada à API (REQ-81)"
RE_REQ = re.compile(r"REQ-(\d{2})")
RE_TELA = re.compile(r"\b([POS]\d{2})\b")
RE_CONTRATO = re.compile(r"\(`([a-z_]+(?::[a-z_]+)?)`")
CLI = {"cli:importar", "cli:importacoes", "cli:sugestoes", "cli:traducao", "cli:alertas"}
EMAIL = {"email:confirmacao", "email:alerta"}

erros = []


def falha(msg):
    erros.append(msg)


def blocos(texto):
    """Campo da ficha -> texto do campo (linha do campo + sub-itens)."""
    saida, atual = {}, None
    for linha in texto.splitlines():
        m = re.match(r"- \*\*(.+?):\*\*(.*)", linha)
        if m:
            atual = m.group(1)
            saida[atual] = m.group(2) + "\n"
        elif atual and linha.startswith("  "):
            saida[atual] += linha + "\n"
    return saida


def ler_requisitos():
    reqs = {}
    for linha in REQS_MD.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\| (REQ-\d{2}) \|", linha)
        if m:
            reqs[m.group(1)] = linha
    return reqs


def ler_operacoes():
    doc = yaml.safe_load((ARQ / "contratos" / "openapi.yaml").read_text(encoding="utf-8"))
    ops = {}
    for caminho in doc["paths"].values():
        for metodo, op in caminho.items():
            if metodo != "parameters":
                ops[op["operationId"]] = op.get("x-modulo")
    try:
        from openapi_spec_validator import validate
        validate(doc)
    except ImportError:
        print("aviso: openapi-spec-validator ausente; OpenAPI só foi lido, não validado")
    except Exception as e:  # noqa: BLE001 — qualquer violação do schema é falha
        falha(f"openapi.yaml inválido: {e}")
    return ops


def contraste(c1, c2):
    def lum(h):
        rgb = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        rgb = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
        return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
    a, b = sorted((lum(c1), lum(c2)), reverse=True)
    return (a + 0.05) / (b + 0.05)


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # console do Windows usa cp1252
    escrever = "--escrever" in sys.argv
    reqs = ler_requisitos()
    ops = ler_operacoes()
    fichas = {p.name[:3]: p for p in sorted(TELAS.glob("[POS][0-9][0-9]-*.md"))}
    citacoes = {r: set() for r in reqs}
    ops_usadas = set()
    vai_para, chega_de = {}, {}

    for tid, caminho in fichas.items():
        texto = caminho.read_text(encoding="utf-8")
        if not texto.startswith(f"## {tid} · "):
            falha(f"{tid}: título não começa com '## {tid} · '")
        b = blocos(texto)
        for campo in CAMPOS:
            if campo not in b:
                falha(f"{tid}: falta o campo '{campo}'")
        if list(b) != CAMPOS:
            falha(f"{tid}: campos fora de ordem ou extras: {list(b)}")
        if b.get("Objetivo", "").strip().count(". ") > 0:
            falha(f"{tid}: objetivo com mais de uma frase")
        # coleta no formato "campo · tipo · obrigatório?" (enunciado §2.3)
        coleta = b.get("Coleta", "")
        if not re.search(r"nenhum campo|· (obrigatório|opcional)", coleta):
            falha(f"{tid}: Coleta sem 'campo · tipo · obrigatório?'")
        # estados
        est = b.get("Estados", "")
        for e in ESTADOS:
            if f"**{e}:**" not in est:
                falha(f"{tid}: falta o estado '{e}'")
        for linha in est.splitlines()[1:]:
            if linha.startswith("  - **") and not re.search(r"REQ-\d{2}|ADR-\d{4}", linha):
                falha(f"{tid}: estado sem REQ/ADR: {linha.strip()[:60]}")
        # ações
        for linha in b.get("Ações", "").splitlines()[1:]:
            if not linha.startswith("  - "):
                continue
            contratos = RE_CONTRATO.findall(linha)
            if not contratos and ACAO_LOCAL not in linha:
                falha(f"{tid}: ação sem contrato: {linha.strip()[:70]}")
            for c in contratos:
                if c in CLI or c in EMAIL:
                    ops_usadas.add(c)
                elif c in ops:
                    ops_usadas.add(c)
                else:
                    falha(f"{tid}: contrato inexistente `{c}`")
        # navegação
        nav = b.get("Chega de / vai para", "")
        m_vai = re.search(r"Vai para:(.*)", nav)
        m_chega = re.search(r"Chega de:(.*)", nav)
        vai_para[tid] = set(RE_TELA.findall(m_vai.group(1))) if m_vai else set()
        chega_de[tid] = set(RE_TELA.findall(m_chega.group(1))) if m_chega else set()
        # requisitos citados
        for n in RE_REQ.findall(texto):
            r = f"REQ-{n}"
            if r not in reqs:
                falha(f"{tid}: cita {r}, que não existe")
            else:
                citacoes[r].add(tid)

    for origem, destinos in vai_para.items():
        for d in destinos:
            if d == origem:
                continue
            if d not in fichas:
                falha(f"{origem}: vai para {d}, que não tem ficha")
            elif origem not in chega_de[d]:
                falha(f"{origem} → {d}: {d} não lista {origem} em 'Chega de'")

    for op in ops:
        if op not in ops_usadas:
            falha(f"operação `{op}` não é usada por nenhuma tela")

    # requisitos citados fora das telas também precisam existir
    outros = list(ARQ.rglob("*.md")) + [ARQ / "contratos" / "openapi.yaml"]
    citado_fora = set()
    for p in outros:
        if p == REQS_MD:
            continue
        for n in RE_REQ.findall(p.read_text(encoding="utf-8")):
            r = f"REQ-{n}"
            if r not in reqs:
                falha(f"{p.relative_to(RAIZ)}: cita {r}, que não existe")
            citado_fora.add(r)
    for r in reqs:
        if not citacoes[r] and r not in citado_fora:
            falha(f"{r} não é citado por tela, ADR, contrato ou cenário")

    # coluna Telas
    linhas = REQS_MD.read_text(encoding="utf-8").splitlines()
    novas = []
    for linha in linhas:
        m = re.match(r"\| (REQ-\d{2}) \|", linha)
        if m:
            esperado = ", ".join(sorted(citacoes[m.group(1)])) or "—"
            partes = linha.split(" | ")
            atual = partes[-1].rstrip(" |")
            if atual != esperado:
                if escrever:
                    partes[-1] = esperado + " |"
                    linha = " | ".join(partes)
                else:
                    falha(f"{m.group(1)}: coluna Telas '{atual}' ≠ citações '{esperado}'")
        novas.append(linha)
    if escrever:
        REQS_MD.write_text("\n".join(novas) + "\n", encoding="utf-8")

    # links relativos em Markdown
    for p in RAIZ.rglob("*.md"):
        for alvo in re.findall(r"\]\(([^)#:]+?)(?:#[^)]*)?\)", p.read_text(encoding="utf-8")):
            if not (p.parent / alvo).exists():
                falha(f"{p.relative_to(RAIZ)}: link quebrado {alvo}")

    # contraste da paleta das diretrizes
    papel = "#FAF8F3"
    for cor in ("#1B1F23", "#4A5560", "#0B5563", "#C2410C"):
        if contraste(cor, papel) < 4.5:
            falha(f"contraste de {cor} sobre {papel} = {contraste(cor, papel):.2f} < 4,5")

    adrs = len(list((ARQ / "adr").glob("[0-9][0-9][0-9][0-9]-*.md")))
    if erros:
        print("\n".join(f"ERRO {e}" for e in erros))
        print(f"{len(erros)} problema(s)")
        sys.exit(1)
    print(f"OK · {len(fichas)} telas · {len(reqs)} requisitos · {len(ops)} operações HTTP · "
          f"{len(CLI)} comandos CLI · {adrs} ADRs")


if __name__ == "__main__":
    main()
