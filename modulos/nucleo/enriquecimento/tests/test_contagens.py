"""Fixa as contagens que o RELATORIO.md cita e que não saem do medir.py nem do carregar.py."""

import unittest

from contagens import contagens


class TestContagensDoRelatorio(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = contagens()

    def test_secao_1_regra_de_sentido(self):
        self.assertEqual(self.c["avanco_com_etapa_que_caiu"], 47)

    def test_secao_4_rodadas(self):
        self.assertEqual(self.c["repetidas"]["rodada1/exec1-pobre"], 17)
        self.assertEqual(self.c["repetidas"]["rodada1/exec2-boa"], 14)
        self.assertEqual(self.c["repetidas"]["rodada2/exec1-pobre"], 2)
        self.assertEqual(self.c["repetidas"]["rodada2/exec2-boa"], 5)
        self.assertEqual(self.c["r2_registrar_com_formato_valido"], (78, 80))
        self.assertEqual(self.c["r2_confianca_alta"], (78, 80))
        self.assertEqual(self.c["r2_restos_a_pagar_falham_nas_duas"], (7, 9))

    def test_secao_4_segundo_modelo(self):
        self.assertEqual(self.c["gemma_registrar_no_primeiro_passo"], 23)

    def test_secao_4_entrada_traduzida(self):
        self.assertEqual(self.c["r2_pobre_erros_so_jargao"], (24, 28))
        self.assertEqual(self.c["textos_com_rotulo_tecnico"], 30)
        self.assertEqual(self.c["repetidas"]["entrada-traduzida/exec1-pobre"], 36)
        self.assertEqual(self.c["repetidas"]["entrada-traduzida/exec2-boa"], 35)
        self.assertEqual(self.c["frase_mais_repetida"]["entrada-traduzida/exec1-pobre"], 37)
        self.assertEqual(self.c["frase_mais_repetida"]["entrada-traduzida/exec2-boa"], 36)

    def test_secao_4_memoria_conferida(self):
        cita = self.c["aprovada_e_cita_etapa"]
        self.assertEqual(cita["rodada2/exec1-pobre"], 8)
        self.assertEqual(cita["memoria-conferida/exec1-pobre-original"], 23)
        self.assertEqual(cita["memoria-conferida/exec1-pobre-traduzida"], 1)
        self.assertEqual(cita["memoria-conferida/exec2-boa-traduzida"], 13)
        self.assertEqual(self.c["humanas_citam_etapa"], (37, 40))
        self.assertEqual(self.c["moldes"]["memoria-conferida/exec1-pobre-original"], 8)
        self.assertEqual(self.c["moldes"]["memoria-conferida/exec1-pobre-traduzida"], 5)
        self.assertEqual(self.c["moldes"]["memoria-conferida/exec2-boa-traduzida"], 8)
        self.assertEqual(self.c["molde_mais_comum"]["memoria-conferida/exec1-pobre-traduzida"], 36)
        self.assertEqual(self.c["empregado"]["memoria-conferida/exec1-pobre-original"], 22)
        self.assertEqual(self.c["textos_com_transferencias"], 35)

    def test_secao_5_corpus(self):
        mac, pc = self.c["corpus_mac"], self.c["corpus_pc"]
        self.assertEqual((mac["itens"], pc["itens"]), (1800, 1391))
        self.assertEqual((mac["conferidos"], pc["conferidos"]), (150, 411))
        self.assertEqual((mac["nao_resolvidos"], pc["nao_resolvidos"]), (26, 0))
        self.assertEqual((mac["passos_por_item"], pc["passos_por_item"]), (3.17, 2.0))
        self.assertEqual((mac["segundos_por_item"], pc["segundos_por_item"]), (10.4, 11.7))
        self.assertEqual((mac["um_passo"], pc["um_passo"]), (1, 466))
        self.assertEqual((mac["restos_a_pagar"], pc["restos_a_pagar"]), (462, 0))
        self.assertEqual(mac["por_tipo"]["rap_inscrito_centavos,rap_pago_centavos"], (425, 0.0))
        self.assertEqual(mac["por_tipo"]["empenhado_centavos"][1], 29.3)
        self.assertEqual(pc["por_tipo"]["empenhado_centavos"][1], 50.6)
        self.assertEqual(mac["por_tipo"]["liquidado_centavos"][1], 1.0)
        self.assertEqual(pc["por_tipo"]["liquidado_centavos"][1], 57.6)
        self.assertEqual(self.c["conferidos_por_sentido"],
                         {"avanco": (556, 2920), "recuo": (5, 60), "nova": (0, 206), "removida": (0, 5)})


if __name__ == "__main__":
    unittest.main()
