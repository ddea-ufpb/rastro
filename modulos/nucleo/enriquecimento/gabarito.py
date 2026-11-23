"""Gabarito da Etapa 2: sorteia 40 itens do corpus e confere a rotulagem.

    python3 gabarito.py sortear    # grava gabarito.jsonl com os rótulos vazios
    python3 gabarito.py conferir   # diz o que falta antes do commit

O sorteio é reproduzível: semente fixa e SHA-256 do corpus gravados em
gabarito.meta.json. `conferir` refaz o sorteio e falha se a lista de itens
não for a que a semente produz, então dá para provar que os itens foram
sorteados e não escolhidos.

A rotulagem é humana. Preencha à mão, em cada linha de gabarito.jsonl:
  rotulo.frase  uma frase dizendo o que mudou entre os lotes
  rotulo.tipo   uma das categorias de tipos.json
e faça o commit ANTES de qualquer execução do enriquecedor.

Só biblioteca padrão.
"""

from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CORPUS = AQUI.parent / "coleta" / "corpus.jsonl"
GABARITO = AQUI / "gabarito.jsonl"
META = AQUI / "gabarito.meta.json"
TIPOS = AQUI / "tipos.json"

SEMENTE = 20261123  # data do sorteio; mudar a semente muda os itens
TAMANHO = 40


def _sha256(caminho: Path) -> str:
    h = hashlib.sha256()
    with caminho.open("rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def _ler_jsonl(caminho: Path) -> list[dict]:
    with caminho.open(encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def _sorteio(corpus: list[dict]) -> list[dict]:
    # ordena por id para o sorteio não depender da ordem do arquivo
    ordenado = sorted(corpus, key=lambda d: d["id"])
    return random.Random(SEMENTE).sample(ordenado, TAMANHO)


def _rotulado(linha: dict) -> bool:
    r = linha.get("rotulo") or {}
    return bool((r.get("frase") or "").strip() or (r.get("tipo") or "").strip())


def sortear() -> int:
    if GABARITO.exists() and any(_rotulado(l) for l in _ler_jsonl(GABARITO)):
        print(f"{GABARITO.name} já tem rótulo preenchido; não sobrescrevo", file=sys.stderr)
        return 1
    corpus = _ler_jsonl(CORPUS)
    linhas = [
        {
            "id": d["id"],
            "chave": d["chave"],
            "presenca": d["campos"].get("presenca"),
            "texto": d["texto"],
            "rotulo": {"frase": "", "tipo": ""},
        }
        for d in _sorteio(corpus)
    ]
    GABARITO.write_text(
        "".join(json.dumps(l, ensure_ascii=False) + "\n" for l in linhas), encoding="utf-8"
    )
    META.write_text(
        json.dumps(
            {
                "semente": SEMENTE,
                "tamanho": TAMANHO,
                "corpus": str(CORPUS.relative_to(AQUI.parent)),
                "corpus_sha256": _sha256(CORPUS),
                "itens_no_corpus": len(corpus),
                "metodo": "random.Random(semente).sample(corpus ordenado por id, tamanho)",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    if not TIPOS.exists():
        TIPOS.write_text("[]\n", encoding="utf-8")
    print(f"OK: {len(linhas)} itens em {GABARITO.name}; defina as categorias em {TIPOS.name}")
    return 0


def conferir() -> int:
    problemas: list[str] = []
    meta = json.loads(META.read_text(encoding="utf-8"))
    if meta["corpus_sha256"] != _sha256(CORPUS):
        problemas.append("o corpus mudou desde o sorteio (SHA-256 diferente)")
    if meta["semente"] != SEMENTE or meta["tamanho"] != TAMANHO:
        problemas.append("semente ou tamanho diferentes dos gravados em gabarito.meta.json")

    corpus = {d["id"]: d for d in _ler_jsonl(CORPUS)}
    esperado = [d["id"] for d in _sorteio(list(corpus.values()))]
    linhas = _ler_jsonl(GABARITO)
    if [l["id"] for l in linhas] != esperado:
        problemas.append("a lista de itens não é a que a semente produz")

    tipos = json.loads(TIPOS.read_text(encoding="utf-8"))
    if not tipos:
        problemas.append(f"{TIPOS.name} está vazio: defina as categorias antes de rotular")

    faltando = []
    for n, l in enumerate(linhas, 1):
        d = corpus.get(l["id"])
        if d is None or d["chave"] != l["chave"]:
            problemas.append(f"linha {n}: {l['id']} não está no corpus com essa chave")
        r = l.get("rotulo") or {}
        if not (r.get("frase") or "").strip() or not (r.get("tipo") or "").strip():
            faltando.append(n)
        elif tipos and r["tipo"] not in tipos:
            problemas.append(f"linha {n}: tipo {r['tipo']!r} fora de {TIPOS.name}")
    if faltando:
        problemas.append(f"{len(faltando)} de {len(linhas)} itens sem frase ou tipo: linhas {faltando}")

    if problemas:
        print("\n".join(f"- {p}" for p in problemas), file=sys.stderr)
        return 1
    print(f"OK: {len(linhas)} itens rotulados, sorteio conferido. Pode fazer o commit.")
    return 0


if __name__ == "__main__":
    comandos = {"sortear": sortear, "conferir": conferir}
    if len(sys.argv) != 2 or sys.argv[1] not in comandos:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    sys.exit(comandos[sys.argv[1]]())
