"""Carga do corpus e do gabarito para os testes."""

import json
from functools import lru_cache
from pathlib import Path

AQUI = Path(__file__).resolve().parent.parent
CORPUS = AQUI.parent / "coleta" / "corpus.jsonl"
GABARITO = AQUI / "gabarito.jsonl"


def _jsonl(caminho: Path) -> list[dict]:
    with caminho.open(encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


@lru_cache(maxsize=1)
def corpus() -> dict[str, dict]:
    return {d["id"]: d for d in _jsonl(CORPUS)}


@lru_cache(maxsize=1)
def gabarito() -> list[dict]:
    return _jsonl(GABARITO)
