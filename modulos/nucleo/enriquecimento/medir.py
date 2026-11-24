"""Mede execuções do enriquecedor contra o gabarito humano.

    python3 medir.py execucoes/exec1-pobre.jsonl execucoes/exec2-boa.jsonl

Grava execucoes/medidas.json e execucoes/medidas.md. Por execução: formato
válido, acurácia, tempo total, passos por item, não resolvidos, taxa de cada
critério do avaliador, matriz de confusão (sentido do gabarito × sentido que a
frase comunica) e a lista de erros. A linha de base são as 40 frases humanas
passando pelo mesmo avaliador.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from avaliar import avaliar, etapa_coerente, sentido_da_frase

AQUI = Path(__file__).resolve().parent
GABARITO = AQUI / "gabarito.jsonl"
CORPUS = AQUI.parent / "coleta" / "corpus.jsonl"
SENTIDOS = ["avanco", "recuo", "nova", "removida", "correcao_cadastral"]
CRITERIOS = ["formato", "sentido", "valor", "sem_jargao"]


def _jsonl(caminho: Path) -> list[dict]:
    with caminho.open(encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def medir(linhas: list[dict], gabarito: list[dict]) -> dict:
    por_id = {l["id"]: l for l in linhas}
    faltando = [g["id"] for g in gabarito if g["id"] not in por_id]
    if faltando:
        raise ValueError(f"{len(faltando)} itens do gabarito sem linha na execução: {faltando[:3]}")
    colunas = SENTIDOS + ["nao_resolvido"]
    matriz = {s: {c: 0 for c in colunas} for s in SENTIDOS}
    soma = {c: 0 for c in CRITERIOS + ["correta"]}
    erros, tempo, passos, nao_resolvidos, auditadas = [], 0.0, 0, 0, 0
    for g in gabarito:
        l = por_id[g["id"]]
        verdade = g["rotulo"]["tipo"]
        tempo += l["segundos"]
        passos += l["passos"]
        if l["status"] != "resolvido":
            nao_resolvidos += 1
            matriz[verdade]["nao_resolvido"] += 1
            r = {c: False for c in soma}
        else:
            r = avaliar(l["resumo"], l["confianca"], l["campos"], verdade)
            matriz[verdade][sentido_da_frase(l["resumo"])] += 1
        for c in soma:
            soma[c] += r[c]
        auditadas += r["correta"] and etapa_coerente(l["resumo"], l["campos"])
        if not r["correta"]:
            erros.append({
                "id": l["id"], "texto": l["texto"], "resumo": l["resumo"], "motivo": l["motivo"],
                "falhou": [c for c in CRITERIOS if not r[c]], "gabarito": g["rotulo"]["frase"],
            })
    n = len(gabarito)
    return {
        "itens": n,
        "formato_valido": soma["formato"] / n,
        "acuracia": soma["correta"] / n,
        "acuracia_auditada": auditadas / n,
        "tempo_total_s": round(tempo, 1),
        "passos_por_item": passos / n,
        "nao_resolvidos": nao_resolvidos,
        "criterios": {c: soma[c] / n for c in CRITERIOS},
        "matriz": matriz,
        "erros": erros,
    }


def linha_de_base(gabarito: list[dict], corpus: dict[str, dict]) -> dict:
    linhas = [
        {**corpus[g["id"]], "resumo": g["rotulo"]["frase"], "confianca": "alta", "status": "resolvido",
         "motivo": "", "passos": 0, "segundos": 0.0}
        for g in gabarito
    ]
    return medir(linhas, gabarito)


def _pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def _md(nomes: list[str], medidas: list[dict], base: dict) -> str:
    out = ["# Medidas das execuções", "", "Gerado por `medir.py`. Gabarito: 40 itens rotulados à mão (commit 19fa624).", ""]
    out += ["| Medida | " + " | ".join(nomes) + " | frases humanas |", "| :-- | " + " | ".join("--:" for _ in nomes) + " | --: |"]
    linhas = [
        ("Formato válido", lambda m: _pct(m["formato_valido"])),
        ("Acurácia (passa nos 4 critérios)", lambda m: _pct(m["acuracia"])),
        ("Acurácia auditada (pós-hoc: etapa citada mudou)", lambda m: _pct(m["acuracia_auditada"])),
        ("Tempo total", lambda m: f"{m['tempo_total_s']:.0f} s"),
        ("Passos por item", lambda m: f"{m['passos_por_item']:.2f}"),
        ("Não resolvidos", lambda m: str(m["nao_resolvidos"])),
    ] + [(f"Critério: {c}", (lambda c: lambda m: _pct(m["criterios"][c]))(c)) for c in CRITERIOS]
    for rotulo, f in linhas:
        out.append(f"| {rotulo} | " + " | ".join(f(m) for m in medidas) + f" | {f(base)} |")
    for nome, m in zip(nomes, medidas):
        cols = [c for c in SENTIDOS + ["nao_resolvido"] if any(m["matriz"][s][c] for s in SENTIDOS)]
        out += ["", f"## Matriz de confusão: {nome}", "", "Linha: sentido do gabarito. Coluna: sentido que a frase comunica.", ""]
        out += ["| gabarito \\ frase | " + " | ".join(cols) + " |", "| :-- | " + " | ".join("--:" for _ in cols) + " |"]
        for s in SENTIDOS:
            if any(m["matriz"][s].values()):
                out.append(f"| {s} | " + " | ".join(str(m["matriz"][s][c]) for c in cols) + " |")
        out += ["", f"Erros ({len(m['erros'])}):", ""]
        out += [f"- `{e['id']}` falhou em {', '.join(e['falhou'])}: {e['resumo'] or '(' + e['motivo'] + ')'}" for e in m["erros"]]
    if len(medidas) >= 2:
        persistentes = sorted({e["id"] for e in medidas[0]["erros"]} & {e["id"] for e in medidas[1]["erros"]})
        out += ["", f"## Erros nas duas execuções ({len(persistentes)})", ""] + [f"- `{i}`" for i in persistentes]
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    gabarito = _jsonl(GABARITO)
    corpus = {d["id"]: d for d in _jsonl(CORPUS)}
    caminhos = [Path(a) for a in argv]
    medidas = [medir(_jsonl(p), gabarito) for p in caminhos]
    base = linha_de_base(gabarito, corpus)
    nomes = [p.stem for p in caminhos]
    destino = caminhos[0].parent
    (destino / "medidas.json").write_text(
        json.dumps({"linha_de_base_humana": base, **dict(zip(nomes, medidas))}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (destino / "medidas.md").write_text(_md(nomes, medidas, base), encoding="utf-8")
    for nome, m in zip(nomes, medidas):
        print(f"{nome}: acurácia {_pct(m['acuracia'])}, formato {_pct(m['formato_valido'])}, "
              f"{m['nao_resolvidos']} não resolvidos, {m['passos_por_item']:.2f} passos/item, {m['tempo_total_s']:.0f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
