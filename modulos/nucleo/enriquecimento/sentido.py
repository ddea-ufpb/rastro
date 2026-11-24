"""Sentido da mudança de uma emenda entre dois lotes, decidido por regra.

Não vai para o modelo: esta regra acerta os 40 itens do gabarito humano
(ver RELATORIO.md, B1). Usar o modelo para isso seria trabalho de parser.
"""

ETAPAS_DE_AVANCO = ("empenhado_centavos", "liquidado_centavos", "pago_centavos", "rap_pago_centavos")


def sentido_por_regra(campos: dict) -> str:
    """Devolve nova | removida | recuo | avanco | correcao_cadastral."""
    if campos["presenca"] != "alterada":
        return campos["presenca"]
    diferencas = {
        a["campo"]: a["diferenca_centavos"]
        for a in campos["alteracoes"]
        if a.get("diferenca_centavos") is not None
    }
    if diferencas.get("rap_cancelado_centavos", 0) > 0:
        return "recuo"
    if any(diferencas.get(c, 0) > 0 for c in ETAPAS_DE_AVANCO):
        return "avanco"
    if any(d < 0 for d in diferencas.values()):
        return "recuo"
    return "correcao_cadastral"
