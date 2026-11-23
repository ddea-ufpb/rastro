"""Adaptador do Ollama local, com retry limitado e circuit breaker.

O laço (agente.py) só conhece `.chat(mensagens, ferramentas) -> dict`; trocar
de servidor de modelo é trocar esta classe. Nos testes entra um cliente falso.
"""

from __future__ import annotations

import json
import random
import time
import urllib.error
import urllib.request


class ErroModelo(Exception):
    """Falha ao falar com o modelo (rede, HTTP, resposta inválida)."""


class CircuitoAberto(ErroModelo):
    """Muitas falhas seguidas: não tenta de novo até passar a espera."""


class Disjuntor:
    def __init__(self, falhas_max: int = 5, espera: float = 30.0, relogio=time.monotonic):
        self.falhas_max, self.espera, self.relogio = falhas_max, espera, relogio
        self.falhas = 0
        self.aberto_em: float | None = None

    def permitir(self) -> None:
        if self.aberto_em is None:
            return
        if self.relogio() - self.aberto_em < self.espera:
            raise CircuitoAberto(f"circuito aberto após {self.falhas} falhas seguidas")
        self.aberto_em = None  # meio-aberto: a próxima tentativa decide
        self.falhas = self.falhas_max - 1

    def sucesso(self) -> None:
        self.falhas, self.aberto_em = 0, None

    def falha(self) -> None:
        self.falhas += 1
        if self.falhas >= self.falhas_max:
            self.aberto_em = self.relogio()


def com_retry(fn, tentativas: int = 3, base: float = 1.0, dormir=time.sleep, aleatorio=random.random):
    """Chama fn até `tentativas` vezes, com espera base*2^i + jitter entre elas."""
    for i in range(tentativas):
        try:
            return fn()
        except CircuitoAberto:
            raise
        except ErroModelo:
            if i == tentativas - 1:
                raise
            dormir(base * 2**i + aleatorio() * 0.5)


class ClienteOllama:
    def __init__(
        self,
        modelo: str,
        url: str = "http://localhost:11434",
        seed: int = 42,
        timeout: float = 120.0,
        disjuntor: Disjuntor | None = None,
        dormir=time.sleep,
    ):
        if modelo.endswith(":latest") or ":" not in modelo:
            raise ValueError("fixe o modelo por tag explícita, por exemplo qwen3:1.7b")
        self.modelo, self.url, self.seed, self.timeout = modelo, url.rstrip("/"), seed, timeout
        self.disjuntor = disjuntor or Disjuntor()
        self.dormir = dormir

    def _post(self, corpo: dict) -> dict:
        req = urllib.request.Request(
            f"{self.url}/api/chat",
            data=json.dumps(corpo).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                dados = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, ConnectionError, json.JSONDecodeError) as e:
            raise ErroModelo(str(e)) from e
        if "message" not in dados:
            raise ErroModelo(f"resposta sem 'message': {str(dados)[:200]}")
        return dados["message"]

    def chat(self, mensagens: list[dict], ferramentas: list[dict]) -> dict:
        corpo = {
            "model": self.modelo,
            "messages": mensagens,
            "tools": ferramentas,
            "stream": False,
            "think": False,
            "options": {"temperature": 0, "seed": self.seed},
        }

        def uma_vez():
            self.disjuntor.permitir()
            try:
                msg = self._post(corpo)
            except ErroModelo:
                self.disjuntor.falha()
                raise
            self.disjuntor.sucesso()
            return msg

        return com_retry(uma_vez, dormir=self.dormir)
