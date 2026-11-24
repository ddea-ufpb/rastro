import json
import re
import tempfile
import unittest
from pathlib import Path

from avaliar import valores_da_frase
from enriquecedor import carregar_entrada, executar
from tests.comum import corpus
from tests.test_agente import ClienteFalso, chamada
from traduzir import traduzir_texto

JARGAO = re.compile(r"\bempenh|\bliquid|restos a pagar|\bRAP\b", re.IGNORECASE)


class TestTraduzirTexto(unittest.TestCase):
    def test_tira_o_jargao_de_todo_o_corpus(self):
        sobrou = [i["id"] for i in corpus().values() if JARGAO.search(traduzir_texto(i["texto"]))]
        self.assertEqual(sobrou, [])

    def test_mantem_os_valores(self):
        for i in list(corpus().values())[:300]:
            self.assertEqual(valores_da_frase(traduzir_texto(i["texto"])), valores_da_frase(i["texto"]))

    def test_rotulos(self):
        self.assertEqual(
            traduzir_texto("Valor Empenhado passou de R$ 1,00 para R$ 2,00 (+R$ 1,00); Valor Liquidado passou de R$ 0,00"),
            "Valor reservado passou de R$ 1,00 para R$ 2,00 (+R$ 1,00); Valor aprovado para pagamento passou de R$ 0,00",
        )
        self.assertEqual(traduzir_texto("Valor Restos A Pagar Inscritos R$ 0,00"), "Valor deixado para pagar nos anos seguintes R$ 0,00")
        self.assertEqual(traduzir_texto("Valor Restos A Pagar Pagos R$ 5,00"), "Valor pago de anos anteriores R$ 5,00")
        self.assertEqual(traduzir_texto("Valor Restos A Pagar Cancelados R$ 0,00"), "Valor de anos anteriores cancelado R$ 0,00")

    def test_nao_mexe_no_resto(self):
        t = "Emenda 202612460001 (2026), de FULANO, função Saúde, local de aplicação JOÃO PESSOA - PB."
        self.assertEqual(traduzir_texto(t), t)


class TestEnriquecedorComTraducao(unittest.TestCase):
    def setUp(self):
        self.item = carregar_entrada("gabarito")[0]
        self.pasta = tempfile.TemporaryDirectory()
        self.saida = Path(self.pasta.name) / "saida.jsonl"

    def tearDown(self):
        self.pasta.cleanup()

    def _registrar(self):
        return [chamada("registrar", {"resumo": "Pagou R$ 1 mil.", "confianca": "alta"})]

    def test_modelo_ve_o_texto_traduzido_e_a_saida_guarda_o_original(self):
        cliente = ClienteFalso(self._registrar())
        executar([self.item], cliente, "pobre", self.saida, traduzir=True, log=lambda *_: None)
        visto = cliente.historicos[0][1]["content"]
        self.assertIsNone(JARGAO.search(visto))
        self.assertIn(traduzir_texto(self.item["texto"]), visto)
        (linha,) = [json.loads(x) for x in self.saida.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(linha["texto"], self.item["texto"])
        self.assertTrue(linha["entrada_traduzida"])

    def test_sem_traducao_nada_muda(self):
        cliente = ClienteFalso(self._registrar())
        executar([self.item], cliente, "pobre", self.saida, log=lambda *_: None)
        self.assertIn(self.item["texto"], cliente.historicos[0][1]["content"])
        (linha,) = [json.loads(x) for x in self.saida.read_text(encoding="utf-8").splitlines()]
        self.assertNotIn("entrada_traduzida", linha)

    def test_nao_mistura_execucao_traduzida_com_original(self):
        executar([self.item], ClienteFalso(self._registrar()), "pobre", self.saida, log=lambda *_: None)
        with self.assertRaises(ValueError):
            executar([self.item], ClienteFalso(self._registrar()), "pobre", self.saida, traduzir=True, log=lambda *_: None)


if __name__ == "__main__":
    unittest.main()
