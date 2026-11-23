"""Contrato de ferramentas e laço do agente (sem framework de agente).

O modelo recebe o item e o sentido já decidido por regra, consulta o
glossário e frases anteriores, e termina chamando `registrar`. As ferramentas
ficam numa lista branca; argumentos chegam como dict ou string JSON e são
normalizados antes de qualquer uso. Nada do que o modelo manda vai para shell
nem para eval.
"""

from __future__ import annotations

import json
import re
import time
import unicodedata
from pathlib import Path

from cliente import ErroModelo

AQUI = Path(__file__).resolve().parent
LIMITE = 280
CONFIANCAS = ("alta", "media", "baixa")
SENTIDOS = ("avanco", "recuo", "nova", "removida", "correcao_cadastral")

SISTEMA = (
    "Você escreve para moradores uma frase curta, em português simples, dizendo o que mudou "
    "numa emenda parlamentar entre dois lotes de dados da CGU. O sentido da mudança já foi "
    "decidido por regra e vem no item: a sua frase tem que comunicar esse sentido. Use as "
    "ferramentas e termine chamando registrar uma única vez."
)


_VALOR = re.compile(
    r"(?:quase\s+)?meio\s+milh[aã]o(?:\s+de\s+reais)?"
    r"|R\$\s*[\d.,]*\d(?:\s*(?:mil|milh(?:ão|ões|ao|oes)|bilh(?:ão|ões|ao|oes))\b)?"
    r"|\d[\d.,]*\s*(?:mil|milh(?:ão|ões|ao|oes)|bilh(?:ão|ões|ao|oes))\b(?:\s+de\s+reais)?",
    re.IGNORECASE,
)


def _mascarar(frase: str) -> str:
    return _VALOR.sub("R$ X", frase)


def _chave(s: str) -> str:
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return " ".join(s.lower().split())


class Ferramentas:
    def __init__(self, spec: str, pasta: Path = AQUI / "referencia"):
        if spec not in ("pobre", "boa"):
            raise ValueError("spec é 'pobre' ou 'boa'")
        self.spec = spec
        self.ref = json.loads((pasta / f"{spec}.json").read_text(encoding="utf-8"))
        self.glossario = {_chave(k): v for k, v in self.ref["glossario"].items()}
        self.registradas: list[dict] = []
        self._esquemas = {
            "consultar_glossario": {
                "type": "object",
                "properties": {"termo": {"type": "string", "description": "termo como aparece no item"}},
                "required": ["termo"],
            },
            "buscar_semelhante": {
                "type": "object",
                "properties": {
                    "sentido": {"type": "string", "enum": list(SENTIDOS)},
                    "funcao": {"type": "string", "description": "área da emenda, como Saúde ou Educação"},
                },
                "required": ["sentido"],
            },
            "registrar": {
                "type": "object",
                "properties": {
                    "resumo": {"type": "string", "description": f"a frase para o morador, até {LIMITE} caracteres"},
                    "confianca": {"type": "string", "enum": list(CONFIANCAS)},
                    "justificativa": {"type": "string", "description": "por que a frase diz isso"},
                },
                "required": ["resumo", "confianca"],
            },
        }
        self._executores = {"consultar_glossario": self._glossario, "buscar_semelhante": self._semelhante}

    def contrato(self) -> list[dict]:
        return [
            {"type": "function", "function": {"name": n, "description": self.ref["descricoes"][n], "parameters": e}}
            for n, e in self._esquemas.items()
        ]

    def normalizar(self, nome: str, argumentos) -> tuple[dict | None, str | None]:
        """Devolve (argumentos limpos, None) ou (None, mensagem de erro para o modelo)."""
        if isinstance(argumentos, str):
            try:
                argumentos = json.loads(argumentos) if argumentos.strip() else {}
            except json.JSONDecodeError:
                return None, "erro: os argumentos não são JSON válido"
        if not isinstance(argumentos, dict):
            return None, "erro: os argumentos têm que ser um objeto"
        esquema = self._esquemas[nome]
        argumentos = self._casar_chaves(argumentos, list(esquema["properties"]))
        limpos = {}
        for campo, prop in esquema["properties"].items():
            v = argumentos.get(campo)
            if v is None:
                continue
            if isinstance(v, bool) or not isinstance(v, (str, int, float)):  # todos os parâmetros são string
                return None, f"erro: {campo} tem que ser texto"
            v = " ".join(str(v).split())
            if "enum" in prop:
                v = _chave(v)
            if v:
                limpos[campo] = v
        faltando = [c for c in esquema["required"] if c not in limpos]
        if faltando:
            recebidas = ", ".join(argumentos.get("_recebidas", [])) or "nenhuma"
            return None, (
                f"erro: argumento obrigatório ausente: {', '.join(faltando)}. "
                f"Chaves recebidas: {recebidas}. Chaves aceitas: {', '.join(esquema['properties'])}."
            )
        for campo, prop in esquema["properties"].items():
            if "enum" in prop and campo in limpos and limpos[campo] not in prop["enum"]:
                return None, f"erro: {campo} tem que ser um de {', '.join(prop['enum'])}"
        return limpos, None

    @staticmethod
    def _casar_chaves(argumentos: dict, aceitas: list[str]) -> dict:
        """Leva a chave que o modelo mandou para a chave do esquema.

        Aceita caixa e acento diferentes ("Confiança") e chave fundida com outra
        ("resumo confianca", visto no qwen3:1.7b): vale a última palavra da chave
        que for uma chave aceita ainda não preenchida.
        """
        casados: dict = {"_recebidas": list(argumentos)}
        resto = []
        for k, v in argumentos.items():
            nk = _chave(str(k)).replace(" ", "_")
            if nk in aceitas and nk not in casados:
                casados[nk] = v
            else:
                resto.append((nk, v))
        for nk, v in resto:
            palavras = [p for p in nk.replace("-", "_").split("_") if p in aceitas and p not in casados]
            if palavras:
                casados[palavras[-1]] = v
        return casados

    def executar(self, nome: str, argumentos) -> str:
        if nome not in self._executores:
            return f"erro: ferramenta desconhecida '{nome}'. Use: {', '.join(self._esquemas)}"
        limpos, erro = self.normalizar(nome, argumentos)
        return erro or self._executores[nome](**limpos)

    def _glossario(self, termo: str) -> str:
        t = _chave(termo)
        if t in self.glossario:
            return self.glossario[t]
        contidos = [k for k in self.glossario if k in t]
        if contidos:
            return self.glossario[max(contidos, key=len)]
        return f"termo não encontrado. Termos disponíveis: {', '.join(self.glossario)}"

    def _semelhante(self, sentido: str, funcao: str | None = None) -> str:
        mesmos = [r for r in self.registradas if r["sentido"] == sentido]
        if funcao:
            mesma_area = [r for r in mesmos if _chave(r["funcao"]) == _chave(funcao)]
            mesmos = mesma_area or mesmos
        if not mesmos:
            return "nenhuma frase registrada ainda para esse sentido"
        # só o tom: os valores de outro item viram "R$ X" (na rodada 1 o modelo copiava os números)
        return json.dumps([_mascarar(r["resumo"]) for r in mesmos[-2:]], ensure_ascii=False)

    def lembrar(self, sentido: str, funcao: str, resumo: str) -> None:
        self.registradas.append({"sentido": sentido, "funcao": funcao, "resumo": resumo})


def _resultado(status, passos, inicio, relogio, resumo="", confianca="", justificativa="", motivo=""):
    return {
        "resumo": resumo,
        "confianca": confianca,
        "justificativa": justificativa,
        "status": status,
        "motivo": motivo,
        "passos": passos,
        "segundos": round(relogio() - inicio, 3),
    }


def enriquecer_item(item: dict, sentido: str, cliente, ferramentas: Ferramentas, max_passos: int = 6, relogio=time.monotonic) -> dict:
    inicio = relogio()
    funcao = (item["campos"].get("emenda") or {}).get("funcao_nome") or ""
    mensagens = [
        {"role": "system", "content": SISTEMA},
        {"role": "user", "content": f"Item: {item['texto']}\nSentido (decidido por regra, não mude): {sentido}\nÁrea: {funcao}"},
    ]
    contrato = ferramentas.contrato()
    for passo in range(1, max_passos + 1):
        try:
            resposta = cliente.chat(mensagens, contrato)
        except ErroModelo as e:
            return _resultado("nao_resolvido", passo, inicio, relogio, motivo=f"modelo indisponível: {e}")
        mensagens.append({k: resposta[k] for k in ("role", "content", "tool_calls") if k in resposta})
        chamadas = resposta.get("tool_calls") or []
        if not chamadas:
            aviso = "Sua resposta veio vazia." if not (resposta.get("content") or "").strip() else "Você respondeu em texto."
            mensagens.append({"role": "user", "content": f"{aviso} Responda chamando uma ferramenta; para entregar a frase, chame registrar."})
            continue
        for ch in chamadas:
            nome = (ch.get("function") or {}).get("name", "")
            argumentos = (ch.get("function") or {}).get("arguments", {})
            if nome == "registrar":
                limpos, erro = ferramentas.normalizar("registrar", argumentos)
                if not erro and len(limpos["resumo"]) > LIMITE:
                    erro = f"erro: o resumo tem {len(limpos['resumo'])} caracteres; o limite é {LIMITE}. Encurte e chame registrar de novo."
                if erro:
                    mensagens.append({"role": "tool", "tool_name": nome, "content": erro})
                    continue
                ferramentas.lembrar(sentido, funcao, limpos["resumo"])
                return _resultado(
                    "resolvido", passo, inicio, relogio,
                    resumo=limpos["resumo"], confianca=limpos["confianca"], justificativa=limpos.get("justificativa", ""),
                )
            mensagens.append({"role": "tool", "tool_name": nome, "content": ferramentas.executar(nome, argumentos)})
    return _resultado("nao_resolvido", max_passos, inicio, relogio, motivo="teto de passos")
