import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from carregar import carregar
from sentido import sentido_por_regra
from tests.comum import corpus


def _amostra():
    """Uma emenda alterada com mudança de estado, uma nova e uma removida."""
    itens = list(corpus().values())
    def pago_subiu(i):
        return any(a["campo"] == "pago_centavos" and (a.get("diferenca_centavos") or 0) > 0 for a in i["campos"]["alteracoes"])

    alterada = next(
        i for i in itens
        if any(m["tipo"] == "estado_alterado" for m in i["campos"]["mudancas_lote"]) and sentido_por_regra(i["campos"]) == "avanco"
        and pago_subiu(i)
    )
    pago = next(a for a in alterada["campos"]["alteracoes"] if a["campo"] == "pago_centavos")["diferenca_centavos"]
    frase = f"Mais R$ {pago / 100:.2f} foram pagos.".replace(".", ",", 1) if pago < 100000 else f"Mais R$ {pago / 100000:.0f} mil foram pagos."
    nova = next(i for i in itens if i["campos"]["presenca"] == "nova")
    removida = next(i for i in itens if i["campos"]["presenca"] == "removida")
    return [
        {**alterada, "sentido": "avanco", "resumo": frase, "confianca": "alta", "status": "resolvido", "motivo": "", "modelo": "qwen3:1.7b", "spec": "boa"},
        {**nova, "sentido": "nova", "resumo": "Emenda nova.", "confianca": "baixa", "status": "resolvido", "motivo": "", "modelo": "qwen3:1.7b", "spec": "boa"},
        {**removida, "sentido": "removida", "resumo": "", "confianca": "", "status": "nao_resolvido", "motivo": "teto de passos", "modelo": "qwen3:1.7b", "spec": "boa"},
    ]


class TestCarregar(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.dados = Path(self.pasta.name) / "dados.jsonl"
        self.banco = Path(self.pasta.name) / "rastro.db"
        self.linhas = _amostra()
        self.dados.write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in self.linhas), encoding="utf-8")

    def tearDown(self):
        self.pasta.cleanup()

    def _q(self, sql, *args):
        with sqlite3.connect(self.banco) as c:
            return c.execute(sql, args).fetchall()

    def test_carrega_as_tres_tabelas(self):
        carregar(self.dados, self.banco)
        self.assertEqual(self._q("SELECT data_referencia, hash_sha256 FROM LoteImportacao ORDER BY id")[0][0], "2026-10-26")
        self.assertEqual(self._q("SELECT count(*) FROM LoteImportacao")[0][0], 2)
        self.assertEqual(self._q("SELECT count(*) FROM ResumoMudanca")[0][0], 3)
        esperado = sum(len(l["campos"]["mudancas_lote"]) for l in self.linhas)
        self.assertEqual(self._q("SELECT count(*) FROM MudancaLote")[0][0], esperado)

    def test_valores_da_etapa(self):
        carregar(self.dados, self.banco)
        alt = self.linhas[0]["campos"]
        m = next(m for m in alt["mudancas_lote"] if m["tipo"] == "valor_alterado")
        a = next(a for a in alt["alteracoes"] if a["campo"] == f"{m['etapa']}_centavos")
        linha = self._q(
            "SELECT valor_antes_centavos, valor_depois_centavos FROM MudancaLote WHERE codigo_emenda=? AND etapa=?",
            alt["codigo_emenda"], m["etapa"],
        )
        self.assertEqual(linha, [(a["antes"], a["depois"])])

    def test_revisar_baixa_confianca_e_nao_resolvido(self):
        carregar(self.dados, self.banco)
        r = dict(self._q("SELECT sentido, revisar FROM ResumoMudanca"))
        self.assertEqual(r, {"avanco": 0, "nova": 1, "removida": 1})

    def test_rodar_duas_vezes_nao_duplica(self):
        carregar(self.dados, self.banco)
        antes = [self._q(f"SELECT count(*) FROM {t}")[0][0] for t in ("LoteImportacao", "MudancaLote", "ResumoMudanca")]
        carregar(self.dados, self.banco)
        depois = [self._q(f"SELECT count(*) FROM {t}")[0][0] for t in ("LoteImportacao", "MudancaLote", "ResumoMudanca")]
        self.assertEqual(antes, depois)

    def test_frase_que_nao_passa_na_conferencia_vai_para_revisao(self):
        self.linhas[0]["resumo"] = "O governo pagou R$ 999 milhões."  # valor inventado, confiança alta
        self.dados.write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in self.linhas), encoding="utf-8")
        carregar(self.dados, self.banco)
        self.assertEqual(self._q("SELECT conferida, revisar FROM ResumoMudanca WHERE sentido='avanco'"), [(0, 1)])

    def test_carregar_de_novo_atualiza_o_resumo(self):
        carregar(self.dados, self.banco)
        self.linhas[0]["resumo"] = "Frase revisada."
        self.dados.write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in self.linhas), encoding="utf-8")
        carregar(self.dados, self.banco)
        self.assertEqual(self._q("SELECT resumo FROM ResumoMudanca WHERE sentido='avanco'"), [("Frase revisada.",)])

    def test_linha_invalida_para_sem_gravar(self):
        self.dados.write_text(json.dumps({**self.linhas[0], "sentido": "talvez"}) + "\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            carregar(self.dados, self.banco)
        self.assertEqual(self._q("SELECT count(*) FROM sqlite_master WHERE name='ResumoMudanca'")[0][0] and
                         self._q("SELECT count(*) FROM ResumoMudanca")[0][0], 0)


if __name__ == "__main__":
    unittest.main()
