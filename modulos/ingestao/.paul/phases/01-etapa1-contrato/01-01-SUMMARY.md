---
phase: 01-etapa1-contrato
plan: 01
subsystem: ingestao
tags: [python, jsonl, cgu, emendas, favorecidos, lgpd]

requires: []
provides:
  - corpus.jsonl da Etapa 1 com os nomes do CONTRATOS.md e do T1, valor em centavos inteiros
  - PR #8 aberto contra a main (https://github.com/ddea-ufpb/rastro/pull/8)
affects: [02-gabarito, 03-enriquecedor, 04-medicao-entrega]

tech-stack:
  added: []
  patterns:
    - "Dinheiro como int em centavos do parser até o JSON"
    - "Portões antes de push público: varredura LGPD + regeneração em checkout limpo"

key-files:
  created: []
  modified:
    - modulos/ingestao/coleta-favorecidos/coletor.py
    - modulos/ingestao/coleta-favorecidos/test_coletor.py
    - modulos/ingestao/coleta-favorecidos/corpus.jsonl
    - modulos/ingestao/coleta-favorecidos/REGRAS.md
    - modulos/ingestao/coleta-favorecidos/FONTE.md

key-decisions:
  - "Campos: cnpj, cnpj_raiz, razao_social, natureza, uf, municipio_nome, registros_favorecido[], quantidade_registros, valor_total_centavos"
  - "Unidade em centavos, embora ainda [decidir] no PR #5; pedido explícito ao grupo no PR #8"

patterns-established:
  - "Equivalência contra hash imutável antes de renomear dado versionado"

duration: ~1h
started: 2026-11-27T12:00:00-03:00
completed: 2026-11-27T13:10:00-03:00
description: "Corpus da Etapa 1 (2 353 entidades, 19 647 registros) no vocabulário do grupo, em centavos, enviado no PR #8"
type: Summary
about: "rastro-ingestao"
---

# Phase 1 Plan 01: Etapa 1 no contrato e enviada — Summary

**O corpus da Etapa 1 usa os nomes do `CONTRATOS.md` e do T1, com o dinheiro em centavos inteiros. Os valores são equivalentes, item a item, aos do commit original. A entrega foi enviada no PR #8.**

## Performance

| Metric | Value |
|--------|-------|
| Duration | ~1h |
| Started | 2026-11-27 12:00 |
| Completed | 2026-11-27 13:10 |
| Tasks | 3 completed (3 PASS no qualify) |
| Files modified | 5 de código/dado + `.paul/` |

## Acceptance Criteria Results

| Criterion | Status | Notes |
|-----------|--------|-------|
| AC-1: Campos no vocabulário do grupo | Pass | O script de equivalência confere o conjunto exato de chaves; nenhum nome antigo aparece |
| AC-2: Valor em centavos, sem perda | Pass | 2 353 entidades, 19 647 registros, `valor_centavos == Decimal(valor_recebido)*100`, 14 estornos negativos, todos `int`; `descartes.jsonl` idêntico (`cmp`) |
| AC-3: Reprodutível e testado | Pass | Duas rodadas com o mesmo sha256 `ff021e63…`; `python test_coletor.py` → ok |
| AC-4: Enviado sobre a main | Pass | Rebase limpo; PR #8 com 0 arquivos fora de `modulos/ingestao/`; 3 commits separados |
| AC-5: Reprodutível a partir do git, sem o zip | Pass | Worktree limpo em `HEAD`: apagou corpus e descartes, regerou, mesmo sha256 do versionado |
| AC-6: Nada de pessoa física no GitHub | Pass | 0 zip, 0 CPF formatado, 0 CPF mascarado; os 3 números de 11 dígitos são `valor_total_centavos` |

## Verification Results

```
extrato favorecidos-pb-2026-11-22.csv: 19647 pagamentos, 2353 entidades no corpus; descartes {...}
ff021e6374a4b51b9ff4aa9420f3dc52804b1d1e85a1f929973adba1523d5b34 *corpus.jsonl
99e4e7b8b1bea1ac5441fbc0f0800bf4a3d615c84cc1254bc9d672b980743c72 *descartes.jsonl
sha iguais · descartes identicos
equivalente: 2353 entidades, 19647 registros, 14 estornos negativos
checkout limpo reproduz o versionado
```

## Task Commits

| Task | Commit | Type | Description |
|------|--------|------|-------------|
| (E1 original, rebaseado) | `1d96739` | feat | Coletor, bruto, corpus, regras, descartes (antes `24017d4`) |
| Task 1 + 2 | `e2caf76` | feat | Nomes do contrato, centavos, corpus regerado, REGRAS/FONTE |
| Task 3 (processo) | `2485e38` | docs | `.paul/` do módulo: projeto, roadmap, plano e auditoria |

## Files Created/Modified

| File | Change | Purpose |
|------|--------|---------|
| `coletor.py` | Modified | `normalizar()` e `agrupar()` com os nomes novos; `valor_centavos` inteiro; docstring aponta o contrato |
| `test_coletor.py` | Modified | Nomes novos; teste de estorno em centavos (`-34705,63` → `-3470563`) |
| `corpus.jsonl` | Regenerated | Mesmos itens, nomes novos |
| `REGRAS.md` | Modified | R-VALOR em centavos, nova R-NOMES, tabela antigo → novo |
| `FONTE.md` | Modified | Linha apontando os nomes e a unidade |

## Decisions Made

| Decision | Rationale | Impact |
|----------|-----------|--------|
| Centavos inteiros na fronteira | REQ-24 do T1; sem perda em JSON | Se o grupo escolher reais no PR #5, é preciso um plano novo de renomeação |
| `municipio_nome` (sem IBGE) | Casar o IBGE é da ingestão definitiva (ADR-0010) | O consumidor recebe o nome como veio da fonte |

## Deviations from Plan

### Summary

| Type | Count | Impact |
|------|-------|--------|
| Auto-fixed | 2 | Nenhum no resultado |
| Scope additions | 0 | - |
| Deferred | 2 | Do audit (`assert` com `-O`, `municipio_ibge`) |

**1. Ordem commit/rebase.** O plano dizia rebase e depois commits. Fiz os commits antes e o rebase depois, porque o rebase exige a árvore limpa. O histórico final é o mesmo.

**2. FONTE.md.** O plano mandava trocar no FONTE.md a referência ao modelo de dados da Sarah, mas essa referência só existia na docstring do `coletor.py`, que foi trocada. No FONTE.md entrou uma linha nova apontando R-NOMES. A seção "Diferenças em relação ao contrato da Sarah" fala do formato da fonte (`fonte-portal.md`) e ficou como estava.

## Issues Encountered

| Issue | Resolution |
|-------|------------|
| A 1ª varredura LGPD media o `$?` do `head`, não do `grep` | Refeita com `grep -c` e exclusão de contexto hexadecimal; os 3 acertos foram inspecionados (valores em centavos) |

## Next Phase Readiness

**Ready:**
- O corpus está versionado e é reprodutível, que é a base do sorteio do gabarito.
- O Ollama 0.40.18 está instalado no Windows; o `qwen3:1.7b` está sendo baixado.

**Concerns:**
- O gabarito está atrasado (era 26/11) e **a rotulagem é humana**: o João precisa reservar tempo para rotular os 40 itens antes de qualquer execução do modelo.
- O `CONTRATOS.md` ainda é rascunho.

**Blockers:**
- None

---
*Built with PAUL Framework v1.4*
*Phase: 01-etapa1-contrato, Plan: 01*
*Completed: 2026-11-27*

**Nota de 2026-11-27 (depois do UNIFY):** a branch foi renomeada para `trabalho2/joao-rafael`, no padrão das outras do Trabalho 2. O rename pela API fechou o PR #8; os mesmos commits estão no PR #9 (https://github.com/ddea-ufpb/rastro/pull/9).
