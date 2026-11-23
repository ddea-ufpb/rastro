import unittest

from sentido import sentido_por_regra
from tests.comum import corpus, gabarito


def _alterada(*alteracoes):
    return {
        "presenca": "alterada",
        "alteracoes": [
            {"campo": c, "antes": 0, "depois": 0, "diferenca_centavos": d} if d is not None
            else {"campo": c, "antes": "A", "depois": "B"}
            for c, d in alteracoes
        ],
    }


class TestSentidoPorRegra(unittest.TestCase):
    def test_acerta_os_40_do_gabarito(self):
        c = corpus()
        erros = [
            (g["id"], g["rotulo"]["tipo"], sentido_por_regra(c[g["id"]]["campos"]))
            for g in gabarito()
            if sentido_por_regra(c[g["id"]]["campos"]) != g["rotulo"]["tipo"]
        ]
        self.assertEqual(erros, [])

    def test_presenca_nova_e_removida(self):
        self.assertEqual(sentido_por_regra({"presenca": "nova", "alteracoes": []}), "nova")
        self.assertEqual(sentido_por_regra({"presenca": "removida", "alteracoes": []}), "removida")

    def test_cancelamento_e_recuo_mesmo_com_pagamento(self):
        campos = _alterada(("rap_cancelado_centavos", 100), ("rap_pago_centavos", 50))
        self.assertEqual(sentido_por_regra(campos), "recuo")

    def test_reducao_sem_pagamento_e_recuo(self):
        self.assertEqual(sentido_por_regra(_alterada(("empenhado_centavos", -100))), "recuo")

    def test_aumento_de_etapa_e_avanco(self):
        for campo in ("empenhado_centavos", "liquidado_centavos", "pago_centavos", "rap_pago_centavos"):
            self.assertEqual(sentido_por_regra(_alterada((campo, 1))), "avanco", campo)

    def test_so_texto_e_correcao_cadastral(self):
        self.assertEqual(sentido_por_regra(_alterada(("municipio_nome", None))), "correcao_cadastral")


if __name__ == "__main__":
    unittest.main()
