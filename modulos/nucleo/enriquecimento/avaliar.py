"""Avaliação determinística de uma frase escrita para o morador.

Quatro critérios, todos conferíveis sem outro modelo:
  formato     frase não vazia, uma frase só, até 280 caracteres, confiança válida
  sentido     o sentido que a frase comunica é o da regra (sentido.py)
  valor       cita ao menos um valor, e todo valor citado bate com o item
  sem_jargao  não usa termo técnico de orçamento

A frase é `correta` quando passa nos quatro. O avaliador é validado nas 40
frases humanas do gabarito (tests/test_avaliar.py) antes de medir o modelo.
"""

from __future__ import annotations

import re
import unicodedata

LIMITE = 280  # o mesmo de TabelaTraducao.explicacao no modelo de dados do Trabalho 1
CONFIANCAS = ("alta", "media", "baixa")
TOLERANCIA = 0.10  # arredondamento de morador: "R$ 1,2 milhão" para 1.250.000

_ESCALA = {"mil": 1e3, "milhao": 1e6, "milhoes": 1e6, "bilhao": 1e9, "bilhoes": 1e9}
_VALOR = re.compile(
    r"(?P<meio>meio\s+milh[aã]o)"
    r"|(?P<rs>R\$\s*)?(?P<num>\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?)"
    r"(?:\s*(?P<esc>mil|milh(?:ão|ões|ao|oes)|bilh(?:ão|ões|ao|oes))\b)?",
    re.IGNORECASE,
)

# ordem importa: o primeiro que casar decide
_LEXICO = [
    ("recuo", r"cancel|reduz|\brecu(?:o|ou|ar)\b|\bcort|diminu|perdeu|n[aã]o (?:ser[aã]o?|vai|v[aã]o) mais"),
    ("removida", r"removid|sumiu|saiu da lista|deixou de aparecer"),
    ("nova", r"emenda nova|nova emenda|primeira vez|acaba de entrar|entrou (?:agora )?n[oa] (?:sistema|lista)"),
    ("correcao_cadastral", r"corrig|s[oó] (?:mudou|trocou) (?:o|a) (?:local|cadastro|nome)"),
]
_JARGAO = re.compile(r"\bempenh|\bliquid|restos a pagar|\bRAP\b", re.IGNORECASE)


def _sem_acento(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def valores_da_frase(frase: str) -> list[float]:
    """Valores em reais citados na frase. Só conta número com R$ ou com escala."""
    valores = []
    for m in _VALOR.finditer(frase):
        if m.group("meio"):
            valores.append(500000.0)
            continue
        if not (m.group("rs") or m.group("esc")):
            continue
        numero = float(m.group("num").replace(".", "").replace(",", "."))
        escala = _ESCALA[_sem_acento(m.group("esc")).lower()] if m.group("esc") else 1
        valores.append(round(numero * escala, 2))
    return valores


def sentido_da_frase(frase: str) -> str:
    baixa = frase.lower()
    for sentido, padrao in _LEXICO:
        if re.search(padrao, baixa):
            return sentido
    return "avanco"


def _candidatos(campos: dict) -> list[float]:
    """Valores que uma frase sobre este item pode citar, em reais."""
    c = []
    for a in campos["alteracoes"]:
        if a.get("diferenca_centavos") is not None:  # campo de valor: diferença, antes e depois
            c += [abs(a["diferenca_centavos"]) / 100, a["antes"] / 100, a["depois"] / 100]
    c = [v for v in c if v]
    if campos["presenca"] != "alterada":
        c += [v / 100 for k, v in campos["emenda"].items() if k.endswith("_centavos") and v]
    return c


def _bate(valor: float, candidatos: list[float]) -> bool:
    return any(abs(valor - c) <= TOLERANCIA * c for c in candidatos)


def _uma_frase(frase: str) -> bool:
    return not re.search(r"[.!?]\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ]", frase.strip())


def avaliar(frase: str, confianca: str | None, campos: dict, sentido: str) -> dict[str, bool]:
    frase = (frase or "").strip()
    valores = valores_da_frase(frase)
    candidatos = _candidatos(campos)
    r = {
        "formato": bool(frase) and len(frase) <= LIMITE and _uma_frase(frase) and confianca in CONFIANCAS,
        "sentido": bool(frase) and sentido_da_frase(frase) == sentido,
        "valor": bool(valores) and all(_bate(v, candidatos) for v in valores),
        "sem_jargao": bool(frase) and not _JARGAO.search(frase),
    }
    r["correta"] = all(r.values())
    return r
