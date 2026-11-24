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
Phase: 1 of 6 (Fundação) — Planning
Plan: 01-01 created + audited, awaiting approval
Status: PLAN created, ready for APPLY
Last activity: 2026-11-24 — Enterprise audit on 01-01 (01-01-AUDIT.md)

Progress:
- Milestone: [░░░░░░░░░░] 0%
- Phase 1: [░░░░░░░░░░] 0%

## Loop Position

Current loop state:
```
PLAN ──▶ APPLY ──▶ UNIFY
  ✓        ○        ○     [Plan created, awaiting approval]
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
None yet.

### Blockers/Concerns
- `CONTRATOS.md` (FI-02) ausente — pré-requisito dos inits por módulo (não bloqueia Fase 1).
- Docker não disponível no ambiente local (WSL) — necessário para 01-02/01-03.

## Session Continuity

Last session: 2026-11-24
Stopped at: Plan 01-01 created
Next action: Run /paul:apply .paul/phases/01-fundacao/01-01-PLAN.md
Resume file: .paul/phases/01-fundacao/01-01-PLAN.md

---
*STATE.md — Updated after every significant action*
