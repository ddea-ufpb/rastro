---
description: "rastro — current position and accumulated context"
type: ProjectState
about: "rastro"
---

# Project State

## Project Reference

See: .paul/PROJECT.md (updated 2026-11-24)

**Core value:** Moradores conseguem saber o que foi destinado à cidade deles por emendas parlamentares federais e em que pé está, em linguagem simples e com a fonte de cada dado.
**Current focus:** v0.1 — Phase 1 Fundação

## Current Position

Milestone: v0.1 Initial Release
Phase: 1 of 6 (Fundação) — In progress
Plan: 01-01 complete (1 de 3 na fase)
Status: Ready for next PLAN (01-02)
Last activity: 2026-11-24 — UNIFY 01-01; SUMMARY criado; PR #7 verde

Progress:
- Milestone: [░░░░░░░░░░] 0%
- Phase 1: [███░░░░░░░] 33%

## Loop Position

Current loop state:
```
PLAN ──▶ APPLY ──▶ UNIFY
  ✓        ✓        ✓     [Loop complete - ready for next PLAN]
```

## Accumulated Context

### Decisions
- PAUL na raiz cobre o sistema; inits por módulo (`modulos/*/.paul/`) depois.
- Stack: PostgreSQL 16 + FastAPI + Next.js/shadcn + Docker Compose.
- Layout: uv workspace (`modulos/<m>/` = `rastro_<m>`, `app/`, `web/`); import-linter impõe independência.
- Recorte: PB todos os anos (fases 2–5), Brasil 2025 na fase 6. Módulo `saida` mantido.
- Enterprise plan audit habilitado.
- 2026-11-24: Audit 01-01 — 3 must-have + 7 strongly-recommended aplicados, 2 deferidos (proteção da main → 01-03). Verdict: conditionally acceptable → pronto p/ APPLY.

### Deferred Issues
| Issue | Origin | Effort | Revisit |
|-------|--------|--------|---------|
| StarletteDeprecationWarning (httpx no TestClient) | 01-01 | S | Quando FastAPI trocar o cliente |
| Dependabot/Renovate para actions por SHA | 01-01 audit | S | 01-03 |

### Blockers/Concerns
- `CONTRATOS.md` (FI-02) só como rascunho no PR #5 (draft) — pré-requisito dos inits por módulo.
- Spec João Rafael (PR #6) não mesclada; cita `modulos/ingestao/coleta-favorecidos/` inexistente no remoto.
- Proteção da `main` ausente até 01-03: CI falha mas não bloqueia merge.
- Docker não disponível no ambiente local (WSL) — necessário para 01-02/01-03.

## Session Continuity

Last session: 2026-11-24
Stopped at: Loop 01-01 fechado
Next action: /paul:plan para 01-02 (schema PostgreSQL + migrações)
Resume file: .paul/phases/01-fundacao/01-01-SUMMARY.md

---
*STATE.md — Updated after every significant action*
