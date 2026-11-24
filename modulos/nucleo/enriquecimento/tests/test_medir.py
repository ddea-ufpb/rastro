import unittest

from medir import medir
from tests.comum import corpus, gabarito


class TestMedir(unittest.TestCase):
    def test_medidas_basicas(self):
        g = gabarito()[:2]
        c = corpus()
        linhas = [
            {**c[g[0]["id"]], "sentido": "avanco", "resumo": "O governo reservou mais R$ 405 mil e pagou R$ 39 mil.",
             "confianca": "alta", "status": "resolvido", "motivo": "", "passos": 2, "segundos": 3.0},
            {**c[g[1]["id"]], "sentido": "avanco", "resumo": "", "confianca": "", "status": "nao_resolvido",
             "motivo": "teto de passos", "passos": 6, "segundos": 9.0},
        ]
        m = medir(linhas, g)
        self.assertEqual(m["itens"], 2)
        self.assertEqual(m["acuracia"], 0.5)
        self.assertEqual(m["formato_valido"], 0.5)
        self.assertEqual(m["nao_resolvidos"], 1)
        self.assertEqual(m["tempo_total_s"], 12.0)
        self.assertEqual(m["passos_por_item"], 4.0)
        self.assertEqual(m["matriz"]["avanco"]["avanco"], 1)
        self.assertEqual(m["matriz"]["avanco"]["nao_resolvido"], 1)
        self.assertEqual([e["id"] for e in m["erros"]], [g[1]["id"]])
        self.assertEqual(m["acuracia_auditada"], 0.5)

    def test_auditoria_reprova_etapa_que_nao_mudou(self):
        g = gabarito()[6:7]  # só o pago mudou
        linha = {**corpus()[g[0]["id"]], "sentido": "avanco", "resumo": "Valor empregado e pago aumentaram R$ 9.800,00.",
                 "confianca": "alta", "status": "resolvido", "motivo": "", "passos": 2, "segundos": 1.0}
        m = medir([linha], g)
        self.assertEqual((m["acuracia"], m["acuracia_auditada"]), (1.0, 0.0))

    def test_falta_item_do_gabarito(self):
        with self.assertRaises(ValueError):
            medir([], gabarito()[:1])


if __name__ == "__main__":
    unittest.main()
