"""Enriquece itens do corpus com a frase para o morador.

    python3 enriquecedor.py --spec boa --entrada gabarito --saida execucoes/exec2-boa.jsonl
    python3 enriquecedor.py --spec boa --entrada corpus --saida dados.jsonl

A saída é retomável: rodar de novo pula os ids já gravados, e as frases já
registradas voltam para `buscar_semelhante`. Item não resolvido fica no
arquivo, com `resumo` vazio e `motivo`.

A entrada `gabarito` usa só os ids do gabarito; o rótulo humano nunca é lido.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from agente import Ferramentas, enriquecer_item
from cliente import ClienteOllama
from sentido import sentido_por_regra
from traduzir import traduzir_texto

AQUI = Path(__file__).resolve().parent
CORPUS = AQUI.parent / "coleta" / "corpus.jsonl"
GABARITO = AQUI / "gabarito.jsonl"
MODELO = "qwen3:1.7b"


def _jsonl(caminho: Path) -> list[dict]:
    if not caminho.exists():
        return []
    with caminho.open(encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def carregar_entrada(entrada: str) -> list[dict]:
    corpus = _jsonl(CORPUS)
    if entrada == "corpus":
        return corpus
    if entrada == "gabarito":
        por_id = {d["id"]: d for d in corpus}
        return [por_id[g["id"]] for g in _jsonl(GABARITO)]  # só o id: o rótulo fica de fora
    raise ValueError("entrada é 'gabarito' ou 'corpus'")


def _refazer(l: dict) -> bool:
    """Item que falhou por causa do servidor (não do modelo) volta para a fila na retomada."""
    return l["status"] != "resolvido" and l["motivo"].startswith("modelo indisponível")


def _ler_saida(saida: Path, spec: str, modelo: str, max_passos: int, log, traduzir: bool = False) -> list[dict]:
    """Linhas já gravadas que valem. Descarta a última se ficou truncada e as que vão ser refeitas."""
    if not saida.exists():
        return []
    validas, descartadas = [], 0
    for n, bruta in enumerate(saida.read_text(encoding="utf-8").splitlines(), 1):
        if not bruta.strip():
            continue
        try:
            l = json.loads(bruta)
        except json.JSONDecodeError:
            descartadas += 1
            log(f"linha {n} de {saida} truncada: o item será refeito")
            continue
        traduzida = l.get("entrada_traduzida", False)
        if (l["spec"], l["modelo"], l["max_passos"], traduzida) != (spec, modelo, max_passos, traduzir):
            raise ValueError(
                f"{saida} é de outra execução ({l['spec']}, {l['modelo']}, max_passos {l['max_passos']}, "
                f"entrada traduzida: {traduzida}); use outro --saida"
            )
        if _refazer(l):
            descartadas += 1
        else:
            validas.append(l)
    if descartadas:  # reescreve sem as linhas descartadas, para não duplicar ids
        tmp = saida.with_suffix(saida.suffix + ".tmp")
        tmp.write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in validas), encoding="utf-8")
        tmp.replace(saida)
    return validas


def executar(itens, cliente, spec: str, saida: Path, max_passos: int = 6, limite: int | None = None, modelo: str = "",
             log=print, traduzir: bool = False) -> dict:
    if max_passos < 1:
        raise ValueError("max_passos tem que ser ≥ 1")
    feitos = _ler_saida(saida, spec, modelo, max_passos, log, traduzir)
    ja = {l["id"] for l in feitos}
    ferramentas = Ferramentas(spec)
    for l in feitos:
        if l["status"] == "resolvido":
            ferramentas.lembrar(l["sentido"], (l["campos"].get("emenda") or {}).get("funcao_nome") or "", l["resumo"])
    pendentes = [i for i in itens if i["id"] not in ja][:limite]
    saida.parent.mkdir(parents=True, exist_ok=True)
    inicio = time.monotonic()
    with saida.open("a", encoding="utf-8") as f:
        for n, item in enumerate(pendentes, 1):
            sentido = sentido_por_regra(item["campos"])
            entrada = {**item, "texto": traduzir_texto(item["texto"])} if traduzir else item
            r = enriquecer_item(entrada, sentido, cliente, ferramentas, max_passos=max_passos)
            linha = {**item, "sentido": sentido, **r, "modelo": modelo, "spec": spec, "max_passos": max_passos}
            if traduzir:
                linha["entrada_traduzida"] = True
            f.write(json.dumps(linha, ensure_ascii=False) + "\n")
            f.flush()
            if n % 25 == 0 or n == len(pendentes):
                log(f"{n}/{len(pendentes)} itens, {time.monotonic() - inicio:.0f} s")
    return {"novos": len(pendentes), "ja_gravados": len(ja)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", choices=("pobre", "boa"), required=True)
    ap.add_argument("--entrada", choices=("gabarito", "corpus"), required=True)
    ap.add_argument("--saida", type=Path, required=True)
    ap.add_argument("--modelo", default=MODELO)
    ap.add_argument("--max-passos", type=int, default=6)
    ap.add_argument("--limite", type=int)
    ap.add_argument("--traduzir-entrada", action="store_true",
                    help="troca os rótulos técnicos do texto por regra (traduzir.py) antes de o modelo ler")
    a = ap.parse_args(argv)
    cliente = ClienteOllama(a.modelo)
    r = executar(carregar_entrada(a.entrada), cliente, a.spec, a.saida, a.max_passos, a.limite, a.modelo,
                 traduzir=a.traduzir_entrada)
    print(f"OK: {r['novos']} itens novos, {r['ja_gravados']} já estavam em {a.saida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
