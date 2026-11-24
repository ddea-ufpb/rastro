import unittest

from avaliar import avaliar, etapa_coerente, sentido_da_frase, valores_da_frase
from tests.comum import corpus, gabarito


class TestValoresDaFrase(unittest.TestCase):
    def test_mil(self):
        self.assertEqual(
            valores_da_frase("reservou mais R$ 405 mil e pagou cerca de R$ 39 mil"), [405000, 39000]
        )

    def test_milhao_com_decimal(self):
        self.assertEqual(valores_da_frase("mais R$ 1,2 milhão foi garantido"), [1200000])

    def test_meio_milhao(self):
        self.assertEqual(valores_da_frase("quase meio milhão de reais a mais"), [500000])

    def test_valor_exato(self):
        self.assertEqual(valores_da_frase("pagou R$ 39.247,58 agora"), [39247.58])

    def test_mil_com_decimal(self):
        self.assertEqual(valores_da_frase("R$ 14,5 mil pingaram na conta"), [14500])

    def test_sem_valor(self):
        self.assertEqual(valores_da_frase("a emenda andou"), [])


class TestSentidoDaFrase(unittest.TestCase):
    def test_recuo(self):
        self.assertEqual(sentido_da_frase("o governo cancelou quase R$ 9 mil"), "recuo")

    def test_nova(self):
        self.assertEqual(sentido_da_frase("É uma emenda nova que acaba de entrar"), "nova")

    def test_removida(self):
        self.assertEqual(sentido_da_frase("A emenda sumiu da lista da CGU"), "removida")

    def test_avanco(self):
        self.assertEqual(sentido_da_frase("Mais R$ 9,8 mil caíram na conta"), "avanco")


class TestAvaliar(unittest.TestCase):
    def test_as_40_frases_humanas_passam(self):
        c = corpus()
        falhas = []
        for g in gabarito():
            r = avaliar(g["rotulo"]["frase"], "alta", c[g["id"]]["campos"], g["rotulo"]["tipo"])
            if not r["correta"]:
                falhas.append((g["id"], r))
        self.assertEqual(falhas, [])

    def test_valor_inventado_falha(self):
        campos = corpus()[gabarito()[0]["id"]]["campos"]  # +405.881,85 empenhado; +39.247,58 pago
        r = avaliar("O governo pagou R$ 2 milhões.", "alta", campos, "avanco")
        self.assertFalse(r["valor"])
        self.assertFalse(r["correta"])

    def test_valor_de_antes_e_depois_vale(self):
        campos = corpus()[gabarito()[0]["id"]]["campos"]  # empenhado 12.678.442,00 -> 13.084.323,85
        r = avaliar("A reserva passou de R$ 12,7 milhões para R$ 13,1 milhões.", "alta", campos, "avanco")
        self.assertTrue(r["valor"])

    def test_um_valor_certo_e_um_errado_falha(self):
        campos = corpus()[gabarito()[0]["id"]]["campos"]
        r = avaliar("Reservou mais R$ 405 mil e pagou R$ 2 milhões.", "alta", campos, "avanco")
        self.assertFalse(r["valor"])

    def test_etapa_coerente_nas_frases_humanas(self):
        c = corpus()
        incoerentes = [g["id"] for g in gabarito() if not etapa_coerente(g["rotulo"]["frase"], c[g["id"]]["campos"])]
        self.assertEqual(incoerentes, [])

    def test_etapa_que_nao_mudou(self):
        # item 7 do gabarito: só o pago mudou (+9.800,00); "empregado" é o empenhado escrito errado pelo modelo
        campos = corpus()[gabarito()[6]["id"]]["campos"]
        self.assertFalse(etapa_coerente("Valor empregado e pago foram aumentados em R$ 9.800,00.", campos))
        self.assertFalse(etapa_coerente("O valor liquidado subiu R$ 9,8 mil.", campos))
        self.assertTrue(etapa_coerente("Mais R$ 9,8 mil foram pagos.", campos))

    def test_sinonimos_de_cada_sentido(self):
        # exemplos da revisão adversária: frases certas que o léxico da rodada 1 reprovava
        casos = {
            "nova": ["Surgiu uma emenda de R$ 700 mil para a Saúde.", "Foi incluída uma emenda de R$ 700 mil.",
                     "Apareceu uma emenda de R$ 700 mil.", "Esta emenda é nova e reserva R$ 700 mil."],
            "removida": ["A emenda saiu do sistema.", "A emenda foi retirada da lista.", "A emenda não aparece mais."],
            "recuo": ["R$ 9 mil foram devolvidos.", "R$ 9 mil foram estornados.", "O governo tirou R$ 9 mil da emenda.",
                      "O governo desistiu de pagar R$ 9 mil."],
        }
        for esperado, frases in casos.items():
            for frase in frases:
                self.assertEqual(sentido_da_frase(frase), esperado, frase)

    def test_sentido_trocado_falha(self):
        campos = corpus()[gabarito()[0]["id"]]["campos"]
        r = avaliar("O governo cancelou R$ 405 mil.", "alta", campos, "avanco")
        self.assertFalse(r["sentido"])

    def test_jargao_falha(self):
        campos = corpus()[gabarito()[0]["id"]]["campos"]
        r = avaliar("Foram empenhados mais R$ 405 mil.", "alta", campos, "avanco")
        self.assertFalse(r["sem_jargao"])

    def test_formato(self):
        campos = corpus()[gabarito()[0]["id"]]["campos"]
        self.assertFalse(avaliar("", "alta", campos, "avanco")["formato"])
        self.assertFalse(avaliar("x" * 281, "alta", campos, "avanco")["formato"])
        self.assertFalse(avaliar("Mais R$ 405 mil.", "talvez", campos, "avanco")["formato"])


if __name__ == "__main__":
    unittest.main()
