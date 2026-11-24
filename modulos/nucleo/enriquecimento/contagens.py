"""Recalcula as contagens que o RELATORIO.md cita e que não saem do medir.py nem do carregar.py.

    python3 contagens.py

Só lê arquivos versionados (corpus, gabarito, execucoes/ e dados.jsonl) e imprime
JSON. Não chama o modelo nem grava nada. As contagens de "cita a etapa que mudou"
são pós-hoc: o léxico abaixo foi escrito depois de ver as saídas e não faz parte
da métrica oficial (avaliar.py).
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

from avaliar import avaliar, etapa_coerente
from sentido import sentido_por_regra

AQUI = Path(__file__).resolve().parent
EXEC = AQUI / "execucoes"
CORPUS = AQUI.parent / "coleta" / "corpus.jsonl"
GABARITO = AQUI / "gabarito.jsonl"
DADOS = AQUI / "dados.jsonl"
ETAPAS_DE_EXECUCAO = {"empenhado_centavos", "liquidado_centavos", "pago_centavos"}
ITENS_DO_MAC = 1800  # o corpus rodou nos itens 1 a 1 800 no Mac e no resto num PC com GPU (RELATORIO.md, seção 5)

# Léxico pós-hoc de etapa: a frase cita a etapa que mudou se casa com o padrão dela.
ETAPA = {
    "empenhado": r"reserv|empenh|empreg",
    "liquidado": r"aprov|liquid|liber|atest",
    "pago": r"\bpag|caiu|ca[ií]ram|conta\b",
    "rap": r"anos? anteriores|anos seguintes|atrasad|restos|passado|pendente",
}
ARQUIVOS = {
    "rodada1/exec1-pobre": "rodada1/exec1-pobre.jsonl",
    "rodada1/exec2-boa": "rodada1/exec2-boa.jsonl",
    "rodada2/exec1-pobre": "rodada2/exec1-pobre.jsonl",
    "rodada2/exec2-boa": "rodada2/exec2-boa.jsonl",
    "segundo-modelo/exec2-boa-gemma4": "segundo-modelo/exec2-boa-gemma4.jsonl",
    "entrada-traduzida/exec1-pobre": "entrada-traduzida/exec1-pobre.jsonl",
    "entrada-traduzida/exec2-boa": "entrada-traduzida/exec2-boa.jsonl",
    "memoria-conferida/exec1-pobre-original": "memoria-conferida/exec1-pobre-original.jsonl",
    "memoria-conferida/exec1-pobre-traduzida": "memoria-conferida/exec1-pobre-traduzida.jsonl",
    "memoria-conferida/exec2-boa-traduzida": "memoria-conferida/exec2-boa-traduzida.jsonl",
}


def _jsonl(p: Path) -> list[dict]:
    with p.open(encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]


def _etapa(campo: str) -> str:
    return "rap" if campo.startswith("rap_") else campo.replace("_centavos", "")


def cita_etapa(frase: str, campos: dict) -> bool:
    """A frase nomeia ao menos uma etapa cujo valor mudou (pós-hoc)."""
    if campos["presenca"] != "alterada":
        return True
    mudaram = {_etapa(a["campo"]) for a in campos["alteracoes"] if a.get("diferenca_centavos")} & set(ETAPA)
    if not mudaram:
        return True
    f = (frase or "").lower()
    return any(re.search(ETAPA[e], f) for e in mudaram)


def _aprovada(l: dict, sentido: str) -> bool:
    return (l["status"] == "resolvido" and avaliar(l["resumo"], l.get("confianca"), l["campos"], sentido)["correta"]
            and etapa_coerente(l["resumo"], l["campos"]))


def _repetidas(linhas: list[dict]) -> int:
    c = Counter(l["resumo"] for l in linhas if l["resumo"])
    return sum(n - 1 for n in c.values() if n > 1)


def _molde(frase: str) -> str:
    return re.sub(r"R\$ [\d.,]+", "R$ N", frase)


def _rap(campos: dict) -> bool:
    return any(a["campo"].startswith("rap_") for a in campos["alteracoes"])


def _parte_do_corpus(linhas: list[dict]) -> dict:
    tipos: dict[str, list[int]] = {}
    conferidos = 0
    for l in linhas:
        ok = _aprovada(l, l["sentido"])
        conferidos += ok
        c = l["campos"]
        if c["presenca"] == "alterada":
            chave = ",".join(sorted(a["campo"] for a in c["alteracoes"]))
            t = tipos.setdefault(chave, [0, 0])
            t[0] += 1
            t[1] += ok
    n = len(linhas)
    return {
        "itens": n,
        "conferidos": conferidos,
        "nao_resolvidos": sum(l["status"] == "nao_resolvido" for l in linhas),
        "passos_por_item": round(sum(l["passos"] for l in linhas) / n, 2),
        "segundos_por_item": round(sum(l["segundos"] for l in linhas) / n, 1),
        "um_passo": sum(l["passos"] == 1 for l in linhas),
        "restos_a_pagar": sum(_rap(l["campos"]) for l in linhas),
        "por_tipo": {k: (v[0], round(100 * v[1] / v[0], 1)) for k, v in tipos.items()},
    }


def contagens() -> dict:
    gab = _jsonl(GABARITO)
    verdade = {g["id"]: g["rotulo"]["tipo"] for g in gab}
    ex = {nome: _jsonl(EXEC / arq) for nome, arq in ARQUIVOS.items()}
    corpus = _jsonl(CORPUS)
    dados = _jsonl(DADOS)
    r2 = ex["rodada2/exec1-pobre"] + ex["rodada2/exec2-boa"]

    def correta(l):
        return l["status"] == "resolvido" and avaliar(l["resumo"], l["confianca"], l["campos"], verdade[l["id"]])["correta"]

    erros_r2_pobre = [avaliar(l["resumo"], l["confianca"], l["campos"], verdade[l["id"]])
                      for l in ex["rodada2/exec1-pobre"] if not correta(l)]
    so_jargao = sum(1 for r in erros_r2_pobre if [k for k in ("formato", "sentido", "valor", "sem_jargao") if not r[k]] == ["sem_jargao"])
    rap_gab = [l["id"] for l in ex["rodada2/exec1-pobre"] if _rap(l["campos"])]
    falham = {nome: {l["id"] for l in ex[nome] if not correta(l)} for nome in ("rodada2/exec1-pobre", "rodada2/exec2-boa")}
    humanas = {l["id"]: {**l, "resumo": next(g["rotulo"]["frase"] for g in gab if g["id"] == l["id"])} for l in ex["rodada2/exec1-pobre"]}
    textos = [l["texto"] for l in ex["rodada2/exec1-pobre"]]
    por_sentido: dict[str, list[int]] = {}
    for l in dados:
        s = por_sentido.setdefault(l["sentido"], [0, 0])
        s[0] += _aprovada(l, l["sentido"])
        s[1] += 1

    return {
        "avanco_com_etapa_que_caiu": sum(
            1 for i in corpus
            if sentido_por_regra(i["campos"]) == "avanco"
            and any((a.get("diferenca_centavos") or 0) < 0 and a["campo"] in ETAPAS_DE_EXECUCAO for a in i["campos"]["alteracoes"])
        ),
        "repetidas": {k: _repetidas(v) for k, v in ex.items()},
        "frase_mais_repetida": {k: Counter(l["resumo"] for l in v if l["resumo"]).most_common(1)[0][1] for k, v in ex.items()},
        "r2_registrar_com_formato_valido": (
            sum(l["status"] == "resolvido" and avaliar(l["resumo"], l["confianca"], l["campos"], verdade[l["id"]])["formato"] for l in r2), len(r2)),
        "r2_confianca_alta": (sum(l["confianca"] == "alta" for l in r2), len(r2)),
        "r2_restos_a_pagar_falham_nas_duas": (sum(i in falham["rodada2/exec1-pobre"] and i in falham["rodada2/exec2-boa"] for i in rap_gab), len(rap_gab)),
        "gemma_registrar_no_primeiro_passo": sum(l["passos"] == 1 for l in ex["segundo-modelo/exec2-boa-gemma4"]),
        "r2_pobre_erros_so_jargao": (so_jargao, len(erros_r2_pobre)),
        "textos_com_rotulo_tecnico": sum(bool(re.search(r"empenh|liquid", t, re.IGNORECASE)) for t in textos),
        "textos_com_transferencias": sum("ransfer" in t for t in textos),
        "aprovada_e_cita_etapa": {
            k: sum(_aprovada(l, verdade[l["id"]]) and cita_etapa(l["resumo"], l["campos"]) for l in v) for k, v in ex.items()
        },
        "humanas_citam_etapa": (sum(cita_etapa(h["resumo"], h["campos"]) for h in humanas.values()), len(humanas)),
        "moldes": {k: len({_molde(l["resumo"]) for l in v}) for k, v in ex.items()},
        "molde_mais_comum": {k: Counter(_molde(l["resumo"]) for l in v).most_common(1)[0][1] for k, v in ex.items()},
        "empregado": {k: sum("empregad" in l["resumo"].lower() for l in v) for k, v in ex.items()},
        "corpus_mac": _parte_do_corpus(dados[:ITENS_DO_MAC]),
        "corpus_pc": _parte_do_corpus(dados[ITENS_DO_MAC:]),
        "conferidos_por_sentido": {k: tuple(v) for k, v in por_sentido.items()},
    }


def main() -> int:
    json.dump(contagens(), sys.stdout, ensure_ascii=False, indent=1)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
