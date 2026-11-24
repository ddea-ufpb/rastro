---
phase: 01-fundacao
plan: 01
subsystem: infra
tags: [uv, workspace, fastapi, import-linter, nextjs, shadcn, github-actions, ci]

requires: []
provides:
  - uv workspace com 4 módulos independentes (rastro_ingestao, rastro_nucleo, rastro_consulta, rastro_saida) + rastro_app
  - app FastAPI com GET /health
  - web/ Next.js 16 + TS strict + shadcn/ui (pt-BR)
  - CI GitHub Actions (jobs python e web) que falha quando deve
affects: [01-02 schema, 01-03 deploy, todas as fases de módulo]

tech-stack:
  added: [uv 0.11, fastapi, uvicorn, pytest, pytest-cov, ruff 0.17, import-linter, next 16.4.6, react 19.3.0, shadcn 4.23.0 (base-nova), cn 0.5.2, pnpm 12.16.1, node 24]
  patterns:
    - "Testes de módulo com `uv run --exact --package rastro-<m>` (ambiente só com o módulo)"
    - "Cobertura mínima 80% com branch por módulo e no app"
    - "import-linter: independence entre módulos + layers (app acima)"
    - "Actions fixadas por SHA; permissions read-only; timeout 10 min"

key-files:
  created: [pyproject.toml, uv.lock, app/src/rastro_app/main.py, modulos/*/pyproject.toml, web/package.json, web/src/app/layout.tsx, web/src/app/page.tsx, .github/workflows/ci.yml, .nvmrc, .python-version]
  modified: [.gitignore]

key-decisions:
  - "typecheck = next typegen && tsc --noEmit (tipos globais do Next 16)"
  - "lint web com --max-warnings=0 (aviso conta como falha)"
  - "pacote npm cn (shadcn) aceito após checar procedência"

patterns-established:
  - "Quebra deliberada por categoria antes de confiar num gate de CI"
  - "Quebras revertidas por backup (cp), não git checkout (arquivos não rastreados)"

duration: ~60min
started: 2026-11-24T15:35:00-03:00
completed: 2026-11-24T16:25:00-03:00
description: "Monorepo uv com 4 módulos isolados + FastAPI + Next 16/shadcn e CI (GitHub Actions) verde, com prova de 9 categorias de falha"
type: Summary
about: "rastro"
---

# Phase 1 Plan 01: Scaffold do monorepo + CI Summary

**Monorepo uv com 4 módulos isolados (import cruzado e cobertura < 80% quebram o CI), app FastAPI, web Next 16 + shadcn em pt-BR e CI no GitHub verde no PR #7.**

## Performance

| Metric | Value |
|--------|-------|
| Duration | ~60 min |
| Tasks | 4 de 4 (3 auto + 1 checkpoint) |
| Files | 46 no commit `e77f215` |
| CI remoto | run 45467904119: python 15 s, web 32 s, success |

## Acceptance Criteria Results

| Criterion | Status | Notes |
|-----------|--------|-------|
| AC-1: Workspace instala e cada módulo testa sozinho | Pass | `uv sync --all-packages --locked`; 4× `uv run --exact --package` passam; em `consulta`, `rastro_ingestao`/`rastro_app`/`fastapi` não importáveis |
| AC-1b: Isolamento quebrado é detectado | Pass | Quebra b: exit 2, `ModuleNotFoundError: rastro_ingestao` |
| AC-1c: Cobertura mínima por módulo | Pass | Quebra c: exit 1, 16,67% < 80% |
| AC-2: App compõe a API | Pass | `GET /health` → 200 `{"status":"ok"}`, cobertura 100% |
| AC-3: Fronteiras entre módulos | Pass | 2 contratos KEPT; quebra a: exit 1, ambos BROKEN |
| AC-4: Web compila com tipos e lint | Pass | lint/typecheck/build exit 0 em clone limpo de `.next`; HTML com `lang="pt-BR"` e `>Rastro<` |
| AC-5: CI falha quando deve | Pass | 9 categorias com exit ≠ 0 (tabela abaixo); CI remoto verde com tudo íntegro |
| AC-6: Privilégio mínimo e cadeia fixada | Pass | `permissions: contents: read`; 5/5 `uses:` por SHA de 40 hex com `# vX`; `timeout-minutes: 10` nos 2 jobs; sem `pull_request_target`/segredos; actionlint 1.7.12 exit 0 |

## Verification Results — quebras deliberadas

Réplica local dos comandos do CI (`ci_python.sh` / sequência do job web). Cada quebra foi revertida por backup e conferida com `cmp`. Baseline final: python 0, web 0.

| # | Quebra | Arquivo | Comando | Exit | Erro |
|---|--------|---------|---------|------|------|
| a | import entre módulos (src) | modulos/consulta/src/rastro_consulta/__init__.py | `uv run lint-imports` | 1 | 2 contratos BROKEN |
| b | import entre módulos (tests) | modulos/consulta/tests/test_smoke.py | pytest isolado de consulta | 2 | ModuleNotFoundError: rastro_ingestao |
| c | cobertura < 80% | modulos/nucleo/src/rastro_nucleo/__init__.py | pytest isolado + `--cov-fail-under=80` | 1 | 16,67% |
| d | erro de tipo TS | web/src/app/page.tsx | `pnpm typecheck` / `pnpm build` | 2 / 1 | TS2322 |
| e | aviso de lint web | web/src/app/page.tsx | `pnpm lint` | 0 → **1** após `--max-warnings=0` | no-unused-vars |
| f | ruff lint | app/src/rastro_app/main.py | ci_python.sh | 1 | F401 `os` |
| g | ruff format | modulos/saida/src/rastro_saida/__init__.py | ci_python.sh | 1 | File would be reformatted |
| h | teste falhando em módulo | modulos/saida/tests/test_smoke.py | ci_python.sh | 1 | `assert 1 == 2`; os outros 3 módulos rodaram (status acumulado) |
| i | teste do app falhando | app/tests/test_health.py | ci_python.sh | 1 | `assert 200 == 201` |

Versões: uv 0.11.11, Python 3.12.3, ruff 0.17.6, Node 24.14.1, pnpm 12.16.1, next 16.4.6, react 19.3.0, shadcn CLI 4.23.0.

## Accomplishments

- Independência dos módulos imposta por máquina em dois níveis: import-linter (código) e ambiente exato (testes). É o contrato central do README transformado em gate.
- CI com gates negativos provados: nenhuma etapa usa `continue-on-error`, `|| true` ou supressões genéricas.
- Web pronta para a Fase 4, com shadcn e tipos de rota do Next.

## Task Commits

| Task | Commit | Type | Description |
|------|--------|------|-------------|
| Tasks 1–3 | `e77f215` | feat | Scaffold + CI (commit único, branch `fase1/01-01-scaffold`, PR #7) |
| Task 4 | — | checkpoint | CI remoto verde (run 45467904119), aprovado pelo usuário |

## Files Created/Modified

| File | Change | Purpose |
|------|--------|---------|
| `pyproject.toml`, `uv.lock`, `.python-version` | Created | Workspace, ruff, pytest, import-linter |
| `modulos/<m>/{pyproject.toml,src/rastro_<m>/__init__.py,tests/test_smoke.py}` ×4 | Created | Pacotes independentes |
| `app/{pyproject.toml,src/rastro_app/main.py,tests/test_health.py}` | Created | FastAPI + /health |
| `web/**` (21 arquivos) | Created | Next 16 + shadcn, pt-BR |
| `.github/workflows/ci.yml` | Created | Jobs python e web |
| `.nvmrc` | Created | Node 24 |
| `.gitignore` | Modified | `.next/`, caches, `.coverage`, `/data/` |

## Deviations from Plan

### Summary

| Type | Count | Impact |
|------|-------|--------|
| Auto-fixed | 4 | Essenciais; reforçam os gates |
| Scope additions | 1 | Assimilação da spec do João Rafael (pedido do usuário) |
| Deferred | 0 | — |

### Auto-fixed Issues

**1. Typecheck quebrado em clone limpo**
- **Found during:** Task 2
- **Issue:** `LayoutProps` é global gerado pelo Next 16; `tsc --noEmit` sem `.next/` falha (TS2304)
- **Fix:** `typecheck` = `next typegen && tsc --noEmit`
- **Verification:** `rm -rf .next && pnpm typecheck` → exit 0

**2. Aviso de lint não falhava**
- **Found during:** Task 2 (quebra e)
- **Issue:** `eslint` sai com 0 quando só há avisos; o CI não pegaria
- **Fix:** `eslint --max-warnings=0`
- **Verification:** quebra e' → exit 1

**3. Ruff isort tratava os pacotes do workspace como terceiros**
- **Found during:** Task 1
- **Fix:** `known-first-party` com os 5 pacotes; docstring longa quebrada em linhas

**4. `.gitignore` `data/` → `/data/`**
- **Issue:** `data/` ignoraria fixtures em qualquer nível (ex.: `tests/dados` futuros com outro nome)
- **Fix:** só a pasta `data/` da raiz

### Scope addition (pedido do usuário no checkpoint)

- Spec `especificacoes/joao-rafael/` (PR #6) conferida: já segue o layout das outras, `verificar.py` OK, sem links relativos quebrados. Assimilada em PROJECT.md (consensos reforçados, 4 decisões abertas novas) e em ROADMAP.md (tópicos de pesquisa da Fase 2). Não mesclada; a decisão é do usuário.

## Issues Encountered

| Issue | Resolution |
|-------|------------|
| `git checkout -- arquivo` não reverte arquivos não rastreados: as quebras a, b e c ficaram no disco | Revertidas à mão e conferidas com grep; daí em diante, revert por backup + `cmp` |
| shadcn 4.23 gera `import { cn } from "cn"` (pacote npm, não `@/lib/utils`) | Procedência conferida: mantenedor shadcn, repo shadcn-ui/cn, sem install scripts. Mantido |
| pnpm usa store em `/mnt/e/.pnpm-store` (sem hardlink entre filesystems no WSL) | Fora do repositório; só aviso |
| `eslint` lento no /mnt/e (~2 min) | Ambiente (NTFS via WSL); no CI levou 32 s o job todo |
| StarletteDeprecationWarning (httpx no testclient) | Origem na biblioteca; inofensivo. Revisitar quando o FastAPI trocar o cliente |

## Next Phase Readiness

**Ready:**
- Estrutura de pacotes onde 01-02 coloca o schema/migrações (dono provável: `rastro_ingestao` para tabelas de fonte; a decidir no plano)
- CI pronto para receber o job com PostgreSQL de serviço

**Concerns:**
- Merge na `main` ainda sem CI obrigatório (até 01-03)
- Docker ausente no WSL local → 01-02/01-03 precisam dele (ou usar só o Postgres de serviço do CI)
- Cobertura de 80% hoje é trivial (módulos sem código); passa a medir de verdade a partir da Fase 2

**Blockers:**
- None para 01-02 no CI; Docker local é pré-requisito para rodar o 01-02 fora do CI

---
*Built with PAUL Framework v1.4 · https://chrisai.cv/skool · https://youtube.com/@chris-ai-systems*
*Phase: 01-fundacao, Plan: 01*
*Completed: 2026-11-24*
