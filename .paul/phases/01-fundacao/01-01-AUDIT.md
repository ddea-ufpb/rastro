# Enterprise Plan Audit Report

**Plan:** .paul/phases/01-fundacao/01-01-PLAN.md
**Audited:** 2026-11-24
**Verdict:** Conditionally acceptable → aceitável após as melhorias aplicadas

---

## 1. Executive Verdict

Antes das correções: **conditionally acceptable**. A estrutura serve, mas o critério central do plano — "cada módulo testável sozinho" — não era provado. `uv run --package` sobre um venv montado com `--all-packages` deixa os outros três módulos importáveis. O import-linter só cobre `src/`, não `tests/`. Assim, um teste de `consulta` que importasse `rastro_ingestao` passaria verde. Isso é exatamente a falha silenciosa que o plano promete evitar. O workflow também estava sem privilégio mínimo e sem actions fixadas. Com as melhorias aplicadas, eu aprovaria.

## 2. What Is Solid

- **Fronteira por máquina (import-linter, contrato `independence` + `layers`)**: transforma o contrato central do README ("ninguém sabe como o CSV é lido") em verificação executável, não em convenção.
- **Prova de falha deliberada por categoria**: o critério "CI que falha quando deve" é testado de forma negativa, não presumido.
- **Escopo restrito**: banco, Compose e deploy ficam em 01-02/01-03. Nenhuma dependência de domínio entra antes da hora.
- **Push e PR atrás de checkpoint humano**: a ação externa (repositório da organização) precisa de autorização explícita.
- **Lockfiles com `--locked` / `--frozen-lockfile` no CI**: build determinístico do lado das dependências.

## 3. Enterprise Gaps Identified

1. Isolamento de módulo não provado: venv compartilhado e `tests/` fora do import-linter.
2. Nenhuma barreira de cobertura, embora PROJECT.md/QA-05 exijam ≥ 80% por módulo. O CI ficaria verde com zero testes reais.
3. Workflow sem `permissions:`: herda o token padrão, possivelmente com escrita.
4. Actions referenciadas por tag mutável: risco de cadeia de suprimento (tag reescrita).
5. Jobs sem `timeout-minutes`: um job travado consome até 6 h e viola a meta de pipeline < 10 min.
6. Scaffold web com versões não fixadas (`create-next-app`, `shadcn@latest`), sem `packageManager` e com risco de gerar `package-lock.json` junto do pnpm.
7. Telemetria do Next ativa no CI, contra a postura de não enviar dados desnecessários.
8. Evidência da prova de falha subespecificada: a "tabela" não dizia o que registrar, então não dava para reconstruir depois.
9. Risco de uma quebra deliberada ser commitada.
10. O CI falha, mas não bloqueia o merge: falta proteção de branch.
11. Sem Dependabot/Renovate para atualizar as actions fixadas por SHA.

## 4. Upgrades Applied to Plan

### Must-Have (Release-Blocking)

| # | Finding | Plan Section Modified | Change Applied |
|---|---------|----------------------|----------------|
| 1 | Isolamento de módulo não provado | AC-1, novo AC-1b, Task 1 action/verify, Task 3 action | `uv run --exact --package`; ferramentas de teste no grupo dev do módulo; quebra deliberada por import em `tests/` |
| 2 | Workflow sem privilégio mínimo | Novo AC-6, Task 3 action, verification | `permissions: contents: read`; proibidos `pull_request_target` e segredos |
| 3 | Nenhuma barreira de cobertura | Novo AC-1c, Task 1 action/verify, verification | `--cov-branch --cov-fail-under=80` por módulo e no app; quebra deliberada de cobertura |

### Strongly Recommended

| # | Finding | Plan Section Modified | Change Applied |
|---|---------|----------------------|----------------|
| 1 | Actions por tag mutável | AC-6, Task 3 action/verify | Fixar por SHA de 40 hex com comentário da versão; grep no verify |
| 2 | Sem timeout | AC-6, Task 3 action | `timeout-minutes: 10` por job |
| 3 | Scaffold web não reprodutível | Task 2 action, verification | `--use-pnpm`, `packageManager` fixado, só `pnpm-lock.yaml`, versões no SUMMARY |
| 4 | Telemetria Next | Task 2 action, Task 3 action | `NEXT_TELEMETRY_DISABLED=1` |
| 5 | Evidência subespecificada | Task 3 action | Registrar comando, arquivo, exit code, linha de erro e versões; `git diff --exit-code` |
| 6 | Quebra deliberada commitada / burlas | Boundaries | Proibido commitar quebras; proibidos `continue-on-error`, `|| true` e supressões genéricas |
| 7 | Falha de um módulo mascarando outros | Task 3 action | Matriz com `fail-fast: false` ou loop que acumula o status |

### Deferred (Can Safely Defer)

| # | Finding | Rationale for Deferral |
|---|---------|----------------------|
| 1 | Proteção da `main` (CI obrigatório para merge) | Já está escopada explicitamente no plano 01-03 da mesma fase, junto com o deploy condicionado. A Fase 1 não fecha sem ela. |
| 2 | Dependabot/Renovate para actions e lockfiles | Não há dependências de domínio ainda. Cabe no 01-03 ou no hardening da fase 6 sem risco imediato. |

## 5. Audit & Compliance Readiness

- **Evidência defensável**: sim, depois das correções. O SUMMARY registra cada quebra deliberada com comando, exit code e versões, e o CI no GitHub fica como registro externo (checkpoint).
- **Falhas silenciosas**: as três principais (isolamento, cobertura, mascaramento entre módulos) agora geram exit ≠ 0.
- **Reconstrução pós-incidente**: lockfiles, SHAs fixados e versões registradas permitem reproduzir o build.
- **Responsabilidade**: o push precisa de autorização humana. Ainda não há mapeamento de dono por módulo (o README traz "*a definir*"), o que cabe no `CONTRATOS.md` e não neste plano.

## 6. Final Release Bar

- **Antes de entregar**: AC-1 a AC-6 verdes localmente, CI verde no GitHub, tabela de quebras completa e nenhum resíduo no git.
- **Risco se entregue como está (pós-correção)**: o merge ainda não exige CI verde até o 01-03 sair. Mitigação: não mesclar nada além deste PR antes do 01-03.
- **Sign-off**: assinaria com as melhorias aplicadas e o 01-03 obrigatório para fechar a Fase 1.

---

**Summary:** Applied 3 must-have + 7 strongly-recommended upgrades. Deferred 2 items.
**Plan status:** Updated and ready for APPLY

---
*Audit performed by PAUL Enterprise Audit Workflow*
*Audit template version: 1.0*
