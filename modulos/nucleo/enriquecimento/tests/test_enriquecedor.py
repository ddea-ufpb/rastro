import json
import tempfile
import unittest
from pathlib import Path

from cliente import ClienteOllama, Disjuntor, ErroModelo
from enriquecedor import carregar_entrada, executar
from tests.test_agente import ClienteFalso, chamada


def _registrar(n):
    return [chamada("registrar", {"resumo": f"Pagou R$ {i} mil.", "confianca": "alta"}) for i in range(1, n + 1)]


class TestExecutar(unittest.TestCase):
    def setUp(self):
        self.itens = carregar_entrada("gabarito")[:3]
        self.pasta = tempfile.TemporaryDirectory()
        self.saida = Path(self.pasta.name) / "saida.jsonl"

    def tearDown(self):
        self.pasta.cleanup()

    def _linhas(self):
        return [json.loads(l) for l in self.saida.read_text(encoding="utf-8").splitlines()]

    def test_entrada_gabarito_nao_traz_rotulo(self):
        itens = carregar_entrada("gabarito")
        self.assertEqual(len(itens), 40)
        self.assertTrue(all("rotulo" not in i for i in itens))

    def test_linha_de_saida(self):
        executar(self.itens[:1], ClienteFalso(_registrar(1)), "boa", self.saida, log=lambda *_: None)
        (l,) = self._linhas()
        self.assertEqual(l["id"], self.itens[0]["id"])
        self.assertEqual(l["sentido"], "avanco")
        self.assertEqual(l["status"], "resolvido")
        self.assertEqual(l["spec"], "boa")
        self.assertIn("campos", l)

    def test_retomada_nao_duplica(self):
        executar(self.itens[:2], ClienteFalso(_registrar(2)), "boa", self.saida, log=lambda *_: None)
        executar(self.itens, ClienteFalso(_registrar(1)), "boa", self.saida, log=lambda *_: None)
        ids = [l["id"] for l in self._linhas()]
        self.assertEqual(ids, [i["id"] for i in self.itens])

    def test_retomada_recupera_frases_para_buscar_semelhante(self):
        executar(self.itens[:1], ClienteFalso(_registrar(1)), "boa", self.saida, log=lambda *_: None)
        cliente = ClienteFalso([chamada("buscar_semelhante", {"sentido": "avanco"})] + _registrar(1))
        executar(self.itens[:2], cliente, "boa", self.saida, log=lambda *_: None)
        self.assertIn("Pagou R$ X.", cliente.historicos[1][-1]["content"])

    def test_retomada_refaz_quem_falhou_por_modelo_fora_do_ar(self):
        executar(self.itens, ClienteFalso([ErroModelo("fora do ar")] * 3), "boa", self.saida, log=lambda *_: None)
        self.assertEqual([l["status"] for l in self._linhas()], ["nao_resolvido"] * 3)
        executar(self.itens, ClienteFalso(_registrar(3)), "boa", self.saida, log=lambda *_: None)
        linhas = self._linhas()
        self.assertEqual([l["id"] for l in linhas], [i["id"] for i in self.itens])
        self.assertEqual([l["status"] for l in linhas], ["resolvido"] * 3)

    def test_retomada_nao_refaz_teto_de_passos(self):
        executar(self.itens[:1], ClienteFalso([{"role": "assistant", "content": "oi"}] * 2), "boa", self.saida,
                 max_passos=2, log=lambda *_: None)
        r = executar(self.itens[:1], ClienteFalso([]), "boa", self.saida, max_passos=2, log=lambda *_: None)
        self.assertEqual(r["novos"], 0)
        self.assertEqual(self._linhas()[0]["motivo"], "teto de passos")

    def test_linha_truncada_no_fim_e_refeita(self):
        executar(self.itens[:2], ClienteFalso(_registrar(2)), "boa", self.saida, log=lambda *_: None)
        bruto = self.saida.read_text(encoding="utf-8")
        self.saida.write_text(bruto[:-40], encoding="utf-8")  # morreu no meio da escrita
        executar(self.itens[:2], ClienteFalso(_registrar(1)), "boa", self.saida, log=lambda *_: None)
        self.assertEqual([l["id"] for l in self._linhas()], [i["id"] for i in self.itens[:2]])

    def test_saida_de_outra_execucao_e_recusada(self):
        executar(self.itens[:1], ClienteFalso(_registrar(1)), "pobre", self.saida, log=lambda *_: None)
        with self.assertRaises(ValueError):
            executar(self.itens, ClienteFalso(_registrar(3)), "boa", self.saida, log=lambda *_: None)

    def test_max_passos_invalido(self):
        with self.assertRaises(ValueError):
            executar(self.itens, ClienteFalso([]), "boa", self.saida, max_passos=0, log=lambda *_: None)

    def test_modelo_fora_do_ar_nao_derruba_e_disjuntor_corta(self):
        chamadas = []
        cliente = ClienteOllama("qwen3:1.7b", disjuntor=Disjuntor(falhas_max=5, espera=60), dormir=lambda s: None)

        def post_quebrado(corpo):
            chamadas.append(1)
            raise ErroModelo("conexão recusada")

        cliente._post = post_quebrado
        executar(self.itens, cliente, "boa", self.saida, log=lambda *_: None)
        linhas = self._linhas()
        self.assertEqual([l["status"] for l in linhas], ["nao_resolvido"] * 3)
        self.assertIn("conexão recusada", linhas[0]["motivo"])
        self.assertIn("circuito aberto", linhas[2]["motivo"])
        self.assertEqual(len(chamadas), 5)  # 3 no primeiro item, 2 no segundo, 0 no terceiro


class TestCliente(unittest.TestCase):
    def test_recusa_latest_e_sem_tag(self):
        for modelo in ("qwen3:latest", "qwen3"):
            with self.assertRaises(ValueError):
                ClienteOllama(modelo)


if __name__ == "__main__":
    unittest.main()
