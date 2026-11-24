"""Carrega dados.jsonl no banco SQLite do módulo nucleo.

    python3 carregar.py dados.jsonl --banco rastro.db

Usa os nomes do modelo de dados do Trabalho 1
(especificacoes/joao-vitor/arquitetura/contratos/modelo-de-dados.md, na
branch trabalho1/joao-vitor, PR #2):
LoteImportacao, MudancaLote (uma linha por tipo e etapa) e a tabela nova
ResumoMudanca (uma linha por emenda e par de lotes, com a frase para o
morador). Cria as tabelas que faltarem; rodar de novo não duplica nada.
Cada frase passa pela mesma conferência do avaliador (formato, sentido,
valor, jargão e etapa citada); `conferida = 1` quando passa. Item não
conferido ou com confiança baixa entra com revisar = 1: a frase não deve ir
para a tela sem revisão. (Nas medições o modelo declarou confiança alta em
quase tudo, então a confiança dele sozinha não serve de filtro.) Tudo numa transação: se uma linha for
inválida, nada é gravado.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

from avaliar import avaliar, etapa_coerente

AQUI = Path(__file__).resolve().parent
LOTES = AQUI.parent / "coleta" / "bruto" / "lotes.json"
SENTIDOS = {"avanco", "recuo", "nova", "removida", "correcao_cadastral"}
STATUS = {"resolvido", "nao_resolvido"}

ESQUEMA = """
CREATE TABLE IF NOT EXISTS Fonte (
    id TEXT PRIMARY KEY, nome TEXT, url_download TEXT, habilitada BOOLEAN
);
CREATE TABLE IF NOT EXISTS LoteImportacao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fonte_id TEXT REFERENCES Fonte(id),
    arquivo_nome TEXT, hash_sha256 TEXT, data_referencia DATE,
    importado_em DATETIME, publicado_em DATETIME, estado TEXT,
    linhas_lidas INTEGER, linhas_aceitas INTEGER, linhas_rejeitadas INTEGER,
    motivo_falha TEXT, duracao_etl_ms TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_lote_fonte_hash
    ON LoteImportacao (fonte_id, hash_sha256) WHERE estado <> 'falhou';
CREATE TABLE IF NOT EXISTS MudancaLote (
    id INTEGER PRIMARY KEY,
    fonte_id TEXT REFERENCES Fonte(id),
    codigo_emenda TEXT NOT NULL,
    lote_anterior_id INTEGER NOT NULL REFERENCES LoteImportacao(id),
    lote_novo_id INTEGER REFERENCES LoteImportacao(id),
    tipo TEXT CHECK (tipo IN ('nova_emenda', 'valor_alterado', 'estado_alterado')),
    etapa TEXT,
    valor_antes_centavos INTEGER, valor_depois_centavos INTEGER,
    estado_antes TEXT, estado_depois TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_mudanca
    ON MudancaLote (lote_novo_id, codigo_emenda, tipo, COALESCE(etapa, '-'));
CREATE TABLE IF NOT EXISTS ResumoMudanca (
    lote_novo_id INTEGER NOT NULL REFERENCES LoteImportacao(id),
    codigo_emenda TEXT NOT NULL,
    lote_anterior_id INTEGER NOT NULL REFERENCES LoteImportacao(id),
    sentido TEXT NOT NULL CHECK (sentido IN ('avanco', 'recuo', 'nova', 'removida', 'correcao_cadastral')),
    resumo TEXT NOT NULL,
    confianca TEXT CHECK (confianca IN ('alta', 'media', 'baixa', '')),
    status TEXT NOT NULL CHECK (status IN ('resolvido', 'nao_resolvido')),
    motivo TEXT NOT NULL,
    conferida BOOLEAN NOT NULL,
    revisar BOOLEAN NOT NULL,
    modelo TEXT NOT NULL,
    spec TEXT NOT NULL,
    PRIMARY KEY (lote_novo_id, codigo_emenda)
);
"""


def _validar(l: dict, n: int) -> None:
    erros = []
    if l.get("sentido") not in SENTIDOS:
        erros.append(f"sentido {l.get('sentido')!r}")
    if l.get("status") not in STATUS:
        erros.append(f"status {l.get('status')!r}")
    if l.get("status") == "resolvido" and not l.get("resumo"):
        erros.append("resolvido sem resumo")
    if erros:
        raise ValueError(f"linha {n} ({l.get('id')}): {', '.join(erros)}")


def _lotes(con: sqlite3.Connection) -> dict[str, int]:
    con.execute(
        "INSERT OR IGNORE INTO Fonte (id, nome, url_download, habilitada) VALUES ('cgu', 'Portal da Transparência (CGU)', ?, 1)",
        ("https://portaldatransparencia.gov.br/download-de-dados/emendas-parlamentares/UNICO",),
    )
    ids = {}
    for l in json.loads(LOTES.read_text(encoding="utf-8")):
        con.execute(
            "INSERT OR IGNORE INTO LoteImportacao (fonte_id, arquivo_nome, hash_sha256, data_referencia, importado_em, estado) "
            "VALUES ('cgu', ?, ?, ?, ?, 'publicado')",
            (l["arquivo_bruto"], l["csv_sha256"], l["data_referencia"], l["coletado_em"]),
        )
        (ids[l["data_referencia"]],) = con.execute(
            "SELECT id FROM LoteImportacao WHERE fonte_id = 'cgu' AND hash_sha256 = ?", (l["csv_sha256"],)
        ).fetchone()
    return ids


def carregar(dados: Path, banco: Path) -> dict:
    linhas = [json.loads(x) for x in dados.read_text(encoding="utf-8").splitlines() if x.strip()]
    for n, l in enumerate(linhas, 1):
        _validar(l, n)
    con = sqlite3.connect(banco)
    try:
        with con:  # uma transação para as linhas: ou todas, ou nenhuma
            for comando in filter(str.strip, ESQUEMA.split(";")):
                con.execute(comando)
            lote = _lotes(con)
            for l in linhas:
                c = l["campos"]
                anterior, novo = lote[c["lote_anterior"]], lote[c["lote_novo"]]
                alteracoes = {a["campo"]: a for a in c["alteracoes"]}
                for m in c["mudancas_lote"]:
                    a = alteracoes.get(f"{m['etapa']}_centavos") if m["etapa"] else None
                    con.execute(
                        "INSERT OR IGNORE INTO MudancaLote (fonte_id, codigo_emenda, lote_anterior_id, lote_novo_id, tipo, etapa, "
                        "valor_antes_centavos, valor_depois_centavos, estado_antes, estado_depois) VALUES ('cgu', ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (c["codigo_emenda"], anterior, novo, m["tipo"], m["etapa"],
                         a["antes"] if a else None, a["depois"] if a else None, c["estado_antes"], c["estado_depois"]),
                    )
                conferida = (
                    l["status"] == "resolvido"
                    and avaliar(l["resumo"], l.get("confianca"), c, l["sentido"])["correta"]
                    and etapa_coerente(l["resumo"], c)
                )
                revisar = not conferida or l.get("confianca") == "baixa"
                con.execute(
                    "INSERT INTO ResumoMudanca (lote_novo_id, codigo_emenda, lote_anterior_id, sentido, resumo, confianca, status, motivo, "
                    "conferida, revisar, modelo, spec) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
                    "ON CONFLICT (lote_novo_id, codigo_emenda) DO UPDATE SET sentido = excluded.sentido, resumo = excluded.resumo, "
                    "confianca = excluded.confianca, status = excluded.status, motivo = excluded.motivo, conferida = excluded.conferida, "
                    "revisar = excluded.revisar, modelo = excluded.modelo, spec = excluded.spec",
                    (novo, c["codigo_emenda"], anterior, l["sentido"], l.get("resumo") or "", l.get("confianca") or "",
                     l["status"], l.get("motivo") or "", conferida, revisar, l.get("modelo") or "", l.get("spec") or ""),
                )
    finally:
        con.close()
    with sqlite3.connect(banco) as c:
        return {t: c.execute(f"SELECT count(*) FROM {t}").fetchone()[0] for t in ("LoteImportacao", "MudancaLote", "ResumoMudanca")}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dados", type=Path)
    ap.add_argument("--banco", type=Path, required=True)
    a = ap.parse_args(argv)
    contagem = carregar(a.dados, a.banco)
    print("OK: " + ", ".join(f"{t} {n}" for t, n in contagem.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
