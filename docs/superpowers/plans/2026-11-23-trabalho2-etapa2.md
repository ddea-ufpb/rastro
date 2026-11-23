# Trabalho 2, Etapa 2 (João Vitor) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enriquecer o corpus da Etapa 1 com uma frase em linguagem de morador escrita por um modelo local, medir duas especificações contra o gabarito humano e entregar dados carregáveis no módulo `nucleo`.

**Architecture:** O sentido da mudança (`avanco`, `recuo`, `nova`, `removida`) sai de uma regra (acerta 40/40 no gabarito). O modelo local só escreve a frase, num laço próprio com duas ferramentas de domínio e `registrar`. Um avaliador determinístico confere cada frase (formato, sentido, valores, jargão) e é validado primeiro nas 40 frases humanas.

**Tech Stack:** Python 3 só com biblioteca padrão (`urllib`, `json`, `sqlite3`, `unittest`); Ollama 0.33 local com `qwen3:1.7b`, `temperature: 0`, `seed: 42`, `think: false`.

**Spec:** tutorial do professor (Google Doc "trabalho2_tutorial_agente_coleta", seções 5 a 7) e as decisões do aluno nesta sessão: gabarito humano em `modulos/nucleo/enriquecimento/gabarito.jsonl` (commit 93cf3d9); tipo por regra; o modelo só escreve a frase.

## Global Constraints

- Nenhum framework de agente; o laço é escrito à mão. Bibliotecas de HTTP e parser são permitidas.
- Modelo por tag explícita (`qwen3:1.7b`), nunca `:latest`; `temperature: 0` em toda execução.
- Mínimo de 2 ferramentas de domínio + `registrar`; `description` diz QUANDO usar; parâmetros tipados com `required`; campo `confianca` em `registrar`.
- A referência entra por ferramenta, lida de arquivo (`referencia/pobre.json`, `referencia/boa.json`).
- Lista branca de ferramentas; nada de `eval` nem argumento do modelo no shell.
- Item não resolvido fica no arquivo de saída com `resumo` vazio e `motivo`.
- O gabarito não muda depois do commit 93cf3d9; a nenhuma execução é permitido ler `rotulo.frase` do gabarito.
- Nomes de campo seguem `especificacoes/joao-vitor/arquitetura/contratos/modelo-de-dados.md` (Trabalho 1): `codigo_emenda`, `estado_antes`, `estado_depois`, `tipo`, `etapa`, `*_centavos`. O campo novo de classificação chama `sentido`, para não colidir com `MudancaLote.tipo`.
- Frase com no máximo 280 caracteres (o mesmo limite de `TabelaTraducao.explicacao`).
- Chamada ao Ollama com retry limitado (3 tentativas, backoff exponencial com jitter) e circuit breaker (abre após 5 falhas seguidas, 30 s de espera).

## Review Focus

- O modelo devolve `arguments` como string JSON, com chave extra ou com `confianca` "Média": deve ser normalizado, não derrubar o laço (teste em Task 3).
- O modelo responde texto sem chamar ferramenta, ou chama ferramenta inexistente: o laço avisa e continua até o teto; no teto, grava `nao_resolvido` (teste em Task 3).
- O Ollama cai no meio da execução longa: o retry/breaker falha de forma explícita e a execução retoma sem duplicar itens já gravados (teste em Task 4).
- Valor por extenso na frase ("meio milhão", "R$ 1,2 milhão", "quase R$ 9 mil"): o avaliador reconhece e confere contra as diferenças do item (teste em Task 2).
- Rodar `carregar.py` duas vezes não duplica linhas no banco (teste em Task 6).

---

### Task 1: Sentido por regra

**Files:**
- Create: `modulos/nucleo/enriquecimento/sentido.py`
- Test: `modulos/nucleo/enriquecimento/tests/test_sentido.py`

**Interfaces:**
- Produces: `sentido_por_regra(campos: dict) -> str`, devolvendo `nova` | `removida` | `recuo` | `avanco` | `correcao_cadastral`.

- [ ] Teste: nos 40 itens de `gabarito.jsonl`, `sentido_por_regra(corpus[id]["campos"]) == rotulo["tipo"]` para todos; item com `rap_cancelado_centavos` subindo dá `recuo`; item só com campos de texto alterados dá `correcao_cadastral`.
- [ ] Rodar `python3 -m unittest discover -s tests`; esperar FAIL (módulo ausente).
- [ ] Implementar: `presenca` ≠ `alterada` → a própria presença; `rap_cancelado_centavos` > 0 → `recuo`; alguma diferença > 0 em empenhado, liquidado, pago ou rap_pago → `avanco`; alguma diferença < 0 → `recuo`; senão `correcao_cadastral`.
- [ ] Rodar os testes; esperar PASS.

### Task 2: Avaliador de frase

**Files:**
- Create: `modulos/nucleo/enriquecimento/avaliar.py`
- Test: `modulos/nucleo/enriquecimento/tests/test_avaliar.py`

**Interfaces:**
- Produces: `valores_da_frase(frase: str) -> list[float]` (reais); `sentido_da_frase(frase: str) -> str`; `avaliar(frase: str, confianca: str | None, campos: dict, sentido: str) -> dict[str, bool]` com as chaves `formato`, `sentido`, `valor`, `sem_jargao` e `correta` (todas verdadeiras).

- [ ] Testes: `valores_da_frase("reservou mais R$ 405 mil e pagou cerca de R$ 39 mil") == [405000, 39000]`; `"R$ 1,2 milhão"` → `[1200000]`; `"meio milhão"` → `[500000]`; `sentido_da_frase` dá `recuo` para "o governo cancelou quase R$ 9 mil" e `nova` para "É uma emenda nova"; `avaliar(...)["correta"]` é verdadeiro para as 40 frases humanas do gabarito (validação do avaliador).
- [ ] Rodar; esperar FAIL.
- [ ] Implementar: valor confere se fica a até 10% de alguma diferença absoluta do item (ou de algum valor da emenda, quando `nova`); sentido por léxico (cancel, reduz, recuo, corte → `recuo`; nova, primeira vez, entrou → `nova`; removid, sumiu, saiu da lista → `removida`; senão `avanco`); jargão proibido: `empenh`, `liquida`, `restos a pagar`, `RAP`; formato: frase não vazia, ≤ 280 caracteres e `confianca` em `alta|media|baixa`.
- [ ] Rodar; esperar PASS. Se alguma frase humana falhar, ajustar o léxico ou a tolerância e registrar o ajuste no relatório.

### Task 3: Cliente do modelo e laço do agente

**Files:**
- Create: `modulos/nucleo/enriquecimento/cliente.py`, `modulos/nucleo/enriquecimento/agente.py`, `modulos/nucleo/enriquecimento/referencia/pobre.json`, `modulos/nucleo/enriquecimento/referencia/boa.json`
- Test: `modulos/nucleo/enriquecimento/tests/test_agente.py`

**Interfaces:**
- Consumes: `sentido_por_regra` (Task 1).
- Produces: `class ClienteOllama(modelo: str, url: str = "http://localhost:11434", seed: int = 42)` com `.chat(mensagens: list[dict], ferramentas: list[dict]) -> dict` (a `message` do Ollama); `class Ferramentas(spec: str)` com `.contrato() -> list[dict]`, `.executar(nome: str, argumentos) -> str` e `.registradas`; `enriquecer_item(item: dict, sentido: str, cliente, ferramentas, max_passos: int = 6) -> dict` com `resumo`, `confianca`, `justificativa`, `status` (`resolvido`|`nao_resolvido`), `motivo`, `passos`, `segundos`.

- [ ] Testes com cliente falso (respostas roteirizadas): chamada a `registrar` com `arguments` em string JSON e `confianca` "Média" resolve o item com `confianca == "media"`; ferramenta desconhecida devolve erro ao modelo e o laço continua; texto sem ferramenta ganha um aviso e conta passo; estourar `max_passos` dá `status == "nao_resolvido"` e `motivo == "teto de passos"`; `consultar_glossario("Empenhado ")` acha o termo `empenhado`; o contrato tem 3 ferramentas, todas com `required`.
- [ ] Rodar; esperar FAIL.
- [ ] Implementar as ferramentas `consultar_glossario(termo)`, `buscar_semelhante(sentido, funcao)` (até 2 frases já registradas nesta execução, nunca do gabarito) e `registrar(resumo, confianca, justificativa)`. A especificação `pobre` usa só definições e descrições que dizem o que a ferramenta faz; a `boa` acrescenta, na referência, como dizer ao morador e regras de desempate, e nas descrições quando usar. O prompt de sistema é o mesmo nas duas.
- [ ] Rodar; esperar PASS.

### Task 4: Execução por linha de comando, com retomada

**Files:**
- Create: `modulos/nucleo/enriquecimento/enriquecedor.py`
- Test: `modulos/nucleo/enriquecimento/tests/test_agente.py` (acrescentar)

**Interfaces:**
- Consumes: Tasks 1 e 3.
- Produces: `python3 enriquecedor.py --spec {pobre,boa} --entrada {gabarito,corpus} --saida ARQ [--modelo qwen3:1.7b] [--max-passos 6] [--limite N]`; cada linha de saída = item do corpus + `sentido`, `resumo`, `confianca`, `justificativa`, `status`, `motivo`, `passos`, `segundos`, `modelo`, `spec`.

- [ ] Teste: com cliente falso, rodar duas vezes sobre a mesma saída grava cada id uma vez só; falha do cliente depois do retry grava `nao_resolvido` com o motivo do erro em vez de derrubar a execução, e o breaker aberto faz os itens seguintes falharem na hora.
- [ ] Rodar; esperar FAIL. Implementar. Rodar; esperar PASS.

### Task 5: Medição das duas execuções

**Files:**
- Create: `modulos/nucleo/enriquecimento/medir.py`; gerados em `modulos/nucleo/enriquecimento/execucoes/`: `exec1-pobre.jsonl`, `exec2-boa.jsonl`, `medidas.json`, `medidas.md`

**Interfaces:**
- Consumes: `avaliar` (Task 2), saída do Task 4.
- Produces: `python3 medir.py execucoes/exec1-pobre.jsonl execucoes/exec2-boa.jsonl` → por execução: formato válido, acurácia, tempo total, passos por item, não resolvidos, taxa de cada critério e matriz de confusão (`sentido` da regra × `sentido_da_frase`), mais a linha de base das frases humanas.

- [ ] Rodar `enriquecedor.py --spec pobre --entrada gabarito` e `--spec boa --entrada gabarito` com o modelo real; depois `medir.py`. Esperado: dois arquivos com 40 linhas cada e `medidas.md` com as cinco medidas por execução.
- [ ] Commit das execuções e das medidas.

### Task 6: Entrega ao projeto

**Files:**
- Create: `modulos/nucleo/enriquecimento/dados.jsonl` (gerado com `--spec boa --entrada corpus`), `modulos/nucleo/enriquecimento/ESQUEMA.md`, `modulos/nucleo/enriquecimento/carregar.py`
- Test: `modulos/nucleo/enriquecimento/tests/test_carregar.py`

**Interfaces:**
- Produces: `python3 carregar.py dados.jsonl --banco ARQ.db` cria, se faltarem, `Fonte`, `LoteImportacao`, `MudancaLote` (colunas do Trabalho 1) e a tabela nova `ResumoMudanca` (`lote_novo_id`, `codigo_emenda`, `sentido`, `resumo`, `confianca`, `status`, `motivo`, `modelo`, `spec`), e insere as linhas.

- [ ] Teste: carregar 3 itens (um de cada presença) num banco temporário dá 3 linhas em `ResumoMudanca`, as linhas de `MudancaLote` com `valor_antes_centavos`/`valor_depois_centavos` da etapa, e rodar de novo não duplica nada.
- [ ] Rodar; esperar FAIL. Implementar. Rodar; esperar PASS.
- [ ] Rodar o corpus inteiro em segundo plano (retomável) e carregar `dados.jsonl` num banco temporário.

### Task 7: Relatório

**Files:**
- Create: `modulos/nucleo/enriquecimento/RELATORIO.md`

- [ ] Escrever com os números de `medidas.json`: máquina (Apple M4, 10 núcleos, 16 GB, GPU integrada), modelo e tag, `temperature: 0` e o aviso de que pode variar entre rodadas; B1 (o que foi para regra e o que foi para o modelo, com a regra que acerta 40/40); contrato e laço; as duas execuções; a matriz de confusão; três erros comentados com o texto do item; um erro que persistiu nas duas; C4 (a linha do modelo de dados que muda: `MudancaLote.tipo` já é derivável por regra, e entra a entidade `ResumoMudanca`); o que fica para o aluno (confirmação escrita de um colega sobre `carregar.py`, vídeo opcional, `CONTRATOS.md` do grupo).
