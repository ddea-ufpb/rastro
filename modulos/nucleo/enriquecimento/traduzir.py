"""Troca, por regra, os rótulos técnicos do texto do item antes de o modelo ler.

Nas medições, o modelo copiava "liquidado" e "empenhado" do texto de entrada e a
frase reprovava no critério sem jargão (24 dos 28 erros da spec pobre na rodada 2).
É tradução de rótulo fixo, trabalho de parser: os rótulos vêm do coletor
(ROTULO em coleta/coletor.py) e as palavras seguem a tradução do modelo de
dados da main (termo_traduzido: "dinheiro reservado", "pagamento autorizado",
"pagamento que ficou para os anos seguintes"). Para liquidado, "aprovado para
pagamento" mantém a palavra que a auditoria de etapa (avaliar.py) reconhece.

Só o texto enviado ao modelo muda; o dados.jsonl guarda o texto original.
"""

from __future__ import annotations

# Do mais longo para o mais curto: "Valor Restos A Pagar ..." antes de "Valor Pago".
TERMOS = [
    ("Valor Restos A Pagar Inscritos", "Valor deixado para pagar nos anos seguintes"),
    ("Valor Restos A Pagar Cancelados", "Valor de anos anteriores cancelado"),
    ("Valor Restos A Pagar Pagos", "Valor pago de anos anteriores"),
    ("Valor Empenhado", "Valor reservado"),
    ("Valor Liquidado", "Valor aprovado para pagamento"),
    ("Valor Pago", "Valor pago"),
]


def traduzir_texto(texto: str) -> str:
    for tecnico, simples in TERMOS:
        texto = texto.replace(tecnico, simples)
    return texto
