import json
import tempfile
import unittest
from pathlib import Path

from agente import Ferramentas
from enriquecedor import carregar_entrada, executar
from sentido import sentido_por_regra
from tests.comum import gabarito
from tests.test_agente import ClienteFalso, chamada


def _item_e_frase_humana():
    item = carregar_entrada("gabarito")[0]
    frase = next(g["rotulo"]["frase"] for g in gabarito() if g["id"] == item["id"])
    return item, frase


class TestMemoriaConferida(unittest.TestCase):
    def setUp(self):
        self.item, self.humana = _item_e_frase_humana()
        self.sentido = sentido_por_regra(self.item["campos"])

    def _semelhante(self, f: Ferramentas) -> str:
        return f.executar("buscar_semelhante", {"sentido": self.sentido})

    def test_sem_a_opcao_lembra_tudo(self):
        f = Ferramentas("pobre")
        f.lembrar(self.sentido, "Educação", "A emenda aumentou o valor reservado.", self.item["campos"], "alta")
        self.assertIn("A emenda aumentou o valor reservado.", self._semelhante(f))

    def test_frase_que_nao_passa_na_conferencia_nao_entra_na_memoria(self):
        f = Ferramentas("pobre", so_conferidas=True)
        f.lembrar(self.sentido, "Educação", "A emenda aumentou o valor reservado.", self.item["campos"], "alta")
        self.assertEqual(self._semelhante(f), "nenhuma frase registrada ainda para esse sentido")

    def test_frase_conferida_entra_mascarada(self):
        f = Ferramentas("pobre", so_conferidas=True)
        f.lembrar(self.sentido, "Educação", self.humana, self.item["campos"], "alta")
        resposta = self._semelhante(f)
        self.assertIn("R$ X", resposta)
        self.assertNotIn("405", resposta)

    def test_sem_campos_nao_da_para_conferir(self):
        f = Ferramentas("pobre", so_conferidas=True)
        f.lembrar(self.sentido, "Educação", self.humana)
        self.assertEqual(self._semelhante(f), "nenhuma frase registrada ainda para esse sentido")


class TestEnriquecedorComMemoriaConferida(unittest.TestCase):
    def setUp(self):
        self.itens = carregar_entrada("gabarito")[:2]
        self.pasta = tempfile.TemporaryDirectory()
        self.saida = Path(self.pasta.name) / "saida.jsonl"

    def tearDown(self):
        self.pasta.cleanup()

    def _registrar(self, frase):
        return [chamada("registrar", {"resumo": frase, "confianca": "alta"})]

    def test_frase_ruim_nao_chega_ao_item_seguinte(self):
        ruim = "A emenda aumentou o valor reservado."
        cliente = ClienteFalso(self._registrar(ruim) + [chamada("buscar_semelhante", {"sentido": "avanco"})] + self._registrar(ruim))
        executar(self.itens, cliente, "pobre", self.saida, memoria_conferida=True, log=lambda *_: None)
        self.assertEqual(cliente.historicos[2][-1]["content"], "nenhuma frase registrada ainda para esse sentido")
        linhas = [json.loads(x) for x in self.saida.read_text(encoding="utf-8").splitlines()]
        self.assertTrue(all(l["memoria_conferida"] for l in linhas))

    def test_nao_mistura_com_execucao_sem_a_opcao(self):
        executar(self.itens[:1], ClienteFalso(self._registrar("Pagou R$ 1 mil.")), "pobre", self.saida, log=lambda *_: None)
        with self.assertRaises(ValueError):
            executar(self.itens, ClienteFalso(self._registrar("Pagou R$ 1 mil.")), "pobre", self.saida,
                     memoria_conferida=True, log=lambda *_: None)


if __name__ == "__main__":
    unittest.main()
