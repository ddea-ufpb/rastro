import json
import unittest

from agente import Ferramentas, enriquecer_item
from cliente import CircuitoAberto, Disjuntor, ErroModelo, com_retry


def chamada(nome, argumentos):
    return {"role": "assistant", "content": "", "tool_calls": [{"function": {"name": nome, "arguments": argumentos}}]}


def texto(conteudo):
    return {"role": "assistant", "content": conteudo}


class ClienteFalso:
    def __init__(self, respostas):
        self.respostas = list(respostas)
        self.historicos = []

    def chat(self, mensagens, ferramentas):
        self.historicos.append([dict(m) for m in mensagens])
        r = self.respostas.pop(0)
        if isinstance(r, Exception):
            raise r
        return r


ITEM = {
    "id": "x",
    "texto": "Emenda 1: Valor Pago passou de R$ 0,00 para R$ 10.000,00 (+R$ 10.000,00).",
    "campos": {"presenca": "alterada", "emenda": {"funcao_nome": "Saúde"}},
}


def _rodar(respostas, spec="boa", max_passos=6):
    cliente = ClienteFalso(respostas)
    r = enriquecer_item(ITEM, "avanco", cliente, Ferramentas(spec), max_passos=max_passos)
    return r, cliente


class TestContrato(unittest.TestCase):
    def test_tres_ferramentas_com_required(self):
        for spec in ("pobre", "boa"):
            contrato = Ferramentas(spec).contrato()
            nomes = [f["function"]["name"] for f in contrato]
            self.assertEqual(nomes, ["consultar_glossario", "buscar_semelhante", "registrar"])
            for f in contrato:
                self.assertTrue(f["function"]["parameters"]["required"], f["function"]["name"])
            registrar = contrato[2]["function"]["parameters"]
            self.assertIn("confianca", registrar["required"])

    def test_boa_diz_quando_usar_e_pobre_nao(self):
        boa = {f["function"]["name"]: f["function"]["description"] for f in Ferramentas("boa").contrato()}
        pobre = {f["function"]["name"]: f["function"]["description"] for f in Ferramentas("pobre").contrato()}
        self.assertIn("ANTES", boa["consultar_glossario"])
        self.assertNotIn("ANTES", pobre["consultar_glossario"])

    def test_so_a_boa_tem_regras(self):
        self.assertIn("não encontrado", Ferramentas("pobre").executar("consultar_glossario", {"termo": "regras"}))
        self.assertNotIn("não encontrado", Ferramentas("boa").executar("consultar_glossario", {"termo": "regras"}))


class TestFerramentas(unittest.TestCase):
    def test_glossario_normaliza_termo(self):
        f = Ferramentas("boa")
        self.assertNotIn("não encontrado", f.executar("consultar_glossario", {"termo": "Empenhado "}))
        self.assertNotIn("não encontrado", f.executar("consultar_glossario", '{"termo": "valor empenhado"}'))
        self.assertIn("pagos", f.executar("consultar_glossario", {"termo": "Restos A Pagar Pagos"}).lower())

    def test_ferramenta_desconhecida(self):
        self.assertIn("desconhecida", Ferramentas("boa").executar("rm", {"x": 1}))

    def test_argumento_faltando(self):
        self.assertIn("obrigatório", Ferramentas("boa").executar("consultar_glossario", {}))


class TestLaco(unittest.TestCase):
    def test_registrar_com_argumentos_em_string_e_acento(self):
        r, _ = _rodar([chamada("registrar", '{"resumo": " Mais R$ 10 mil pagos. ", "confianca": "Média", "extra": 1}')])
        self.assertEqual(r["status"], "resolvido")
        self.assertEqual(r["confianca"], "media")
        self.assertEqual(r["resumo"], "Mais R$ 10 mil pagos.")
        self.assertEqual(r["passos"], 1)

    def test_chave_fundida_ou_com_acento(self):
        # visto no qwen3:1.7b: {"resumo confianca": "alta", "resumo": "..."}
        r, _ = _rodar([chamada("registrar", {"resumo confianca": "alta", "resumo": "Pagou R$ 10 mil."})])
        self.assertEqual((r["status"], r["confianca"]), ("resolvido", "alta"))
        r, _ = _rodar([chamada("registrar", {"Resumo": "Pagou R$ 10 mil.", "Confiança": "Baixa"})])
        self.assertEqual((r["status"], r["confianca"]), ("resolvido", "baixa"))

    def test_erro_diz_o_que_chegou(self):
        _, c = _rodar([chamada("registrar", {"frase": "Pagou R$ 10 mil."})] + [texto("x")] * 2, max_passos=2)
        self.assertIn("frase", c.historicos[1][-1]["content"])

    def test_ferramenta_desconhecida_volta_ao_modelo(self):
        r, c = _rodar([chamada("apagar", {}), chamada("registrar", {"resumo": "Pagou R$ 10 mil.", "confianca": "alta"})])
        self.assertEqual(r["status"], "resolvido")
        self.assertEqual(r["passos"], 2)
        self.assertIn("desconhecida", c.historicos[1][-1]["content"])

    def test_texto_sem_ferramenta_ganha_aviso(self):
        r, c = _rodar([texto("Pagou R$ 10 mil."), chamada("registrar", {"resumo": "Pagou R$ 10 mil.", "confianca": "alta"})])
        self.assertEqual(r["status"], "resolvido")
        self.assertIn("registrar", c.historicos[1][-1]["content"])

    def test_registrar_invalido_nao_encerra(self):
        r, c = _rodar([chamada("registrar", {"confianca": "alta"}), chamada("registrar", {"resumo": "x" * 300, "confianca": "alta"}),
                       chamada("registrar", {"resumo": "Pagou R$ 10 mil.", "confianca": "talvez"})], max_passos=3)
        self.assertEqual(r["status"], "nao_resolvido")
        self.assertIn("obrigatório", c.historicos[1][-1]["content"])
        self.assertIn("280", c.historicos[2][-1]["content"])

    def test_teto_de_passos(self):
        r, _ = _rodar([texto("oi")] * 3, max_passos=3)
        self.assertEqual(r["status"], "nao_resolvido")
        self.assertEqual(r["motivo"], "teto de passos")
        self.assertEqual(r["resumo"], "")
        self.assertEqual(r["passos"], 3)

    def test_erro_do_modelo_vira_nao_resolvido(self):
        r, _ = _rodar([ErroModelo("conexão recusada")])
        self.assertEqual(r["status"], "nao_resolvido")
        self.assertIn("modelo", r["motivo"])

    def test_buscar_semelhante_usa_so_o_que_foi_registrado(self):
        f = Ferramentas("boa")
        self.assertIn("nenhuma", f.executar("buscar_semelhante", {"sentido": "avanco"}))
        enriquecer_item(ITEM, "avanco", ClienteFalso([chamada("registrar", {"resumo": "Pagou R$ 10 mil.", "confianca": "alta"})]), f)
        self.assertIn("Pagou R$ 10 mil.", f.executar("buscar_semelhante", {"sentido": "avanco", "funcao": "Saúde"}))
        self.assertIn("nenhuma", f.executar("buscar_semelhante", {"sentido": "recuo"}))


class TestResiliencia(unittest.TestCase):
    def test_retry_limitado_com_backoff(self):
        esperas = []
        tentativas = []

        def falha():
            tentativas.append(1)
            raise ErroModelo("fora do ar")

        with self.assertRaises(ErroModelo):
            com_retry(falha, tentativas=3, base=1.0, dormir=esperas.append, aleatorio=lambda: 0.0)
        self.assertEqual(len(tentativas), 3)
        self.assertEqual(esperas, [1.0, 2.0])

    def test_disjuntor_abre_e_fecha(self):
        agora = [0.0]
        d = Disjuntor(falhas_max=2, espera=30.0, relogio=lambda: agora[0])
        d.falha(); d.falha()
        with self.assertRaises(CircuitoAberto):
            d.permitir()
        agora[0] = 31.0
        d.permitir()  # meio-aberto: deixa uma tentativa passar
        d.sucesso()
        d.permitir()


if __name__ == "__main__":
    unittest.main()
