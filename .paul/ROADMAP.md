---
description: "rastro — milestone and phase structure"
type: Roadmap
about: "rastro"
---

# Roadmap: rastro

## Overview

Acompanhamento das emendas parlamentares federais destinadas a um município, com o estado de execução traduzido para linguagem simples. Começa pela Fundação (comum à turma), segue pelos quatro módulos na ordem do fluxo de dados — `ingestao` → `nucleo` → `consulta` → `saida` — com o lote publicado como contrato central, primeiro com o recorte PB (todos os anos) e por fim expandindo para Brasil 2025 com medição de desempenho.

## Current Milestone

**v0.1 Initial Release** (v0.1.0)
Status: In progress
Phases: 0 of 6 complete

## Phases

| Phase | Name | Plans | Status | Completed |
|-------|------|-------|--------|-----------|
| 1 | Fundação | 3 | In progress (1/3) | - |
| 2 | Ingestão PB | TBD | Not started | - |
| 3 | Núcleo | TBD | Not started | - |
| 4 | Consulta | TBD | Not started | - |
| 5 | Saída | TBD | Not started | - |
| 6 | Expansão Brasil 2025 + desempenho | TBD | Not started | - |

## Phase Details

### Phase 1: Fundação

**Goal:** Scaffold com CI que falha quando deve, banco com as restrições de dados no schema, e deploy que só publica com CI verde.
**Depends on:** Nothing (first phase)
**Research:** Unlikely (ferramentas conhecidas)

**Scope:**
- uv workspace (4 módulos + app FastAPI) e web Next.js/shadcn
- PostgreSQL 16 com schema e restrições (versão ativa única, proveniência obrigatória), migrações
- Docker Compose (web, api, carga, db) e deploy condicionado ao CI verde

**Plans:**
- [x] 01-01: Scaffold do monorepo + CI que falha quando deve (PR #7)
- [ ] 01-02: Schema PostgreSQL com restrições + migrações + testes de restrição
- [ ] 01-03: Docker Compose + deploy gated por CI + proteção da `main`

### Phase 2: Ingestão PB

**Goal:** Baixar o ZIP da CGU por GET condicional (ETag), validar, filtrar PB, normalizar com proveniência por registro e publicar a versão com troca atômica.
**Depends on:** Phase 1 (schema e CI)
**Research:** Likely (formato real — `fonte-portal.md` da Sarah e do João Rafael)
**Research topics:** favorecido só por CNPJ e descarte de PF/empresário individual (JR ADR-0001/0004); descartes por município (JR ADR-0009); ETag × download diário

### Phase 3: Núcleo

**Goal:** Fase/estado derivado dos valores (inclui restos a pagar), tabela de tradução versionada com fonte, mudanças entre lotes.
**Depends on:** Phase 2 (lote publicado)
**Research:** Likely (5 estados JV vs `fase_simples` SA)

### Phase 4: Consulta

**Goal:** API `/api/v1` conforme OpenAPI, telas de município/emenda/autor/origem no Next com tipos gerados; previsto e recebido sem somar.
**Depends on:** Phase 3

### Phase 5: Saída

**Goal:** Assinaturas por filtro e limiar com chave anônima; alertas idempotentes por (assinatura, mudança) no painel.
**Depends on:** Phase 3 (mudanças entre lotes)

### Phase 6: Expansão Brasil 2025 + desempenho

**Goal:** Recorte Brasil 2025 na ingestão e consulta; baseline e metas de desempenho (QA-04/Q4) medidas.
**Depends on:** Phases 2–5

---
*Roadmap created: 2026-11-24*
*Last updated: 2026-11-24*
