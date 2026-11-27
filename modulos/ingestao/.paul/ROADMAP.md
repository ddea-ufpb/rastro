---
description: "rastro-ingestao — milestone and phase structure"
type: Roadmap
about: "rastro-ingestao"
---

# Roadmap: rastro-ingestao

## Overview

Módulo `ingestao` do Rastro, começando pelo Trabalho 2 do João Rafael: corpus de favorecidos PJ alinhado ao contrato do grupo, depois enriquecimento com modelo local e entrega consumível.

## Current Milestone
**v0.1 Trabalho 2** (v0.1.0)
Status: In progress
Phases: 1 of 4 complete (25%)
Prazo final: 2026-12-01

## Phases

| Phase | Name | Plans | Status | Completed |
|-------|------|-------|--------|-----------|
| 1 | Etapa 1 no contrato e enviada | 1/1 | ✅ Complete (PR #8) | 2026-11-27 |
| 2 | Gabarito de 40 itens | TBD | Not started | - |
| 3 | Enriquecedor (parser + agente) | TBD | Not started | - |
| 4 | Medição e entrega | TBD | Not started | - |

## Phase Details

### Phase 1: Etapa 1 no contrato e enviada
Renomear os campos do `corpus.jsonl` para o vocabulário do `CONTRATOS.md` (`Favorecido`, `RegistroFavorecido`, `codigo_emenda`, `*_centavos`) e, onde ele não fixa nome, para o `modelo-de-dados.md` do T1. Valor vira centavos inteiros (REQ-24 do T1). Depois, rebase sobre `origin/main`, push e PR. Prazo da E1 (24/11) já passou.

### Phase 2: Gabarito de 40 itens
Sorteio reprodutível (semente fixa) de 40 entidades entre as ambíguas, planilha para rotular, rótulos **feitos à mão pelo João**, commit datado **antes** de qualquer execução do modelo. Categorias: `prefeitura`, `autarquia`, `hospital`, `osc`, `consorcio`, `empresa`, `orgao_estadual`, `outro` (decisão de 2026-11-27).

### Phase 3: Enriquecedor (parser + agente)
Parser decide a natureza quando a `natureza` da fonte é inequívoca (~2 200 entidades). O modelo local (`qwen3:1.7b`, Ollama no Windows) decide só as ~137 ambíguas: categoria e se é a mesma entidade que outra de CNPJ diferente. Laço escrito à mão, teto configurável, lista branca, ferramentas `consultar_naturezas`, `buscar_semelhante`, `registrar`. Referência pobre e boa em arquivo.

### Phase 4: Medição e entrega
Duas execuções (spec pobre e boa) com as cinco medidas, matriz de confusão, três erros comentados e um que persistiu. `dados.jsonl`, `ESQUEMA.md`, `carregar.py`, relatório, linha da seção 5 do `CONTRATOS.md` e a decisão C4.

---
*Roadmap created: 2026-11-24 · phases defined: 2026-11-27*
