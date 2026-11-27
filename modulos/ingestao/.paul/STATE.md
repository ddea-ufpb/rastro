---
description: "rastro-ingestao — current position and accumulated context"
type: ProjectState
about: "rastro-ingestao"
---

# Project State

## Project Reference

See: .paul/PROJECT.md (updated 2026-11-27)

**Core value:** Todo pagamento de emenda ligada à PB chega ao banco com a entidade certa (por CNPJ) e a linha de origem, e nada é descartado sem motivo.
**Current focus:** Fase 2 — Gabarito de 40 itens

## Current Position

Milestone: v0.1 Trabalho 2
Phase: 2 of 4 (Gabarito de 40 itens)
Plan: Not started
Status: Ready to plan
Last activity: 2026-11-27 — Phase 1 complete (PR #9), transitioned to Phase 2

Progress:
- Milestone: [██░░░░░░░░] 25%
- Phase 2: [░░░░░░░░░░] 0%

## Loop Position

Current loop state:
```
PLAN ──▶ APPLY ──▶ UNIFY
  ✓        ✓        ✓     [Loop complete - ready for next PLAN]
```

## Accumulated Context

### Decisions
- Nomes do CONTRATOS.md (`RegistroFavorecido`, `codigo_emenda`, `*_centavos`); o resto da spec do T1.
- Plan → Audit → Apply → Unify (enterprise audit ligado).
- 2026-11-27: categorias de natureza `prefeitura`, `autarquia`, `hospital`, `osc`, `consorcio`, `empresa`, `orgao_estadual`, `outro`.
- 2026-11-27: modelo local via Ollama no Windows (WSL tem ~1 GB de RAM e só `qwen2.5:0.5b`).
- 2026-11-27: Phase 1 — campos `cnpj`, `cnpj_raiz`, `razao_social`, `natureza`, `uf`, `municipio_nome`, `registros_favorecido[]`, `quantidade_registros`, `valor_total_centavos`; dinheiro em centavos inteiros.
- 2026-11-27: Enterprise audit em 01-01-PLAN.md. Aplicados 2 must-have (portão LGPD, regeneração em checkout limpo), 3 strongly-recommended. Adiados 2. Verdict: conditionally acceptable.

### Deferred Issues
- `assert` de um nome por CNPJ some com `python -O` (audit 01-01; rever na ingestão definitiva).
- `municipio_ibge` não produzido (ADR-0010; ingestão definitiva).

### Blockers/Concerns
- Phase 2: gabarito venceu em 26/11; rotulagem é humana (João) e precisa de commit antes da 1ª execução do modelo.
- `CONTRATOS.md` é rascunho (PR #5): `*_centavos` ainda [decidir]; pedido feito no PR #9.

### Git State
Last commit: ver `git log` da branch (commit da fase 1)
Branch: trabalho2/joao-rafael (PR #9)
Feature branches merged: none (merge é do grupo)

## Session Continuity

Last session: 2026-11-27
Stopped at: Phase 1 complete, ready to plan Phase 2
Next action: /paul:plan for Phase 2
Resume file: .paul/ROADMAP.md

---
*STATE.md — Updated after every significant action*
