---
description: "Moradores conseguem saber o que foi destinado à cidade deles por emendas parlamentares federais e em que pé está, em linguagem simples e com a fonte de cada dado."
type: Project
about: "rastro"
---

# rastro

## What This Is

Aplicação que acompanha as emendas parlamentares federais destinadas a um município, com o estado de execução traduzido para linguagem que o morador entende. Importa os dados oficiais (Portal da Transparência/CGU) em lotes, normaliza e guarda a proveniência de cada registro, traduz as fases de execução (empenhado, liquidado, pago) por tabela versionada, expõe consulta por município e avisa quem assinou quando algo muda entre um lote e o seguinte. Projeto da disciplina DINF00071 (CI/UFPB, 2026.2), dividido em quatro módulos independentes: `ingestao`, `nucleo`, `consulta`, `saida`.

## Core Value

Moradores conseguem saber o que foi destinado à cidade deles por emendas parlamentares federais e em que pé está, em linguagem simples e com a fonte de cada dado.

## Current State

| Attribute | Value |
|-----------|-------|
| Type | Application |
| Version | 0.0.0 |
| Status | Initializing (nenhuma linha de aplicação escrita) |
| Last Updated | 2026-11-24 |

## Inputs (especificações)

Duas especificações individuais do Trabalho 1, ambas arc42 enxuto (C4, MADR, EARS, OpenAPI 3.1, cenários de qualidade de 6 partes). Decisão de init: **mesclar** — conflitos ficam como decisões abertas para `/paul:plan`.

| Spec | Autor | Conteúdo | Destaques |
|------|-------|----------|-----------|
| `especificacoes/joao-vitor/` | João Vitor Chaves | 19 telas (P01–P11, D01, S01–S05, O01–O02), 112 REQ, 10 ADRs, OpenAPI (20 ops) + AsyncAPI + CLI + modelo de dados, `verificar.py` (rastreabilidade) | Mapa explícito para os 4 módulos e envelope por módulo; assinaturas e alertas |
| `especificacoes/sarah-araujo/` | Sarah Araújo | 15 telas (A01–A15), 82 REQ, 9 ADRs, OpenAPI, `rotas-html.md`, `carga.md`, `fonte-portal.md`, modelo de dados | Fonte validada contra o arquivo real (T1): formato, ETag, 49% das linhas sem município único, restos a pagar, objeto do convênio |

## Requirements

### Core Features

- **Ingestão por lote** (`ingestao`): baixar o ZIP da CGU, validar, normalizar, guardar proveniência por registro (fonte, lote, data de extração) e publicar o lote de forma atômica.
- **Estado e diferença** (`nucleo`): derivar o estado de execução consolidado de cada emenda, traduzi-lo por tabela versionada e calcular as mudanças entre lotes.
- **Consulta por município** (`consulta`): API versionada e telas de busca por município, parlamentar e função; detalhe da emenda; agregações; previsto e recebido mostrados separados, sem somar.
- **Assinaturas e alertas** (`saida`): assinatura por filtro e limiar, alerta com entrega única por assinante. *(só na spec do João; ver decisões abertas)*
- **Transparência da origem**: tela de origem dos dados/lotes e da tabela de tradução, citação da emenda.

### Validated (Shipped)
None yet.

### Active (In Progress)
None yet.

### Planned (Next)
- Fase 1 (Fundação, comum à turma): scaffold com CI que falha quando deve, banco com as restrições de dados no schema, deploy que só publica com CI verde.
- Fases seguintes por módulo: a definir em `/paul:plan`.

### Out of Scope
- Emendas estaduais e municipais — fonte e estrutura diferentes, não cabem no prazo.
- Juízo sobre mérito, qualidade ou irregularidade da emenda — o sistema mostra o caminho do dinheiro, não opina.
- Classificar, pontuar ou ranquear parlamentares.
- Cruzamento com execução de obra em campo / dinheiro dentro da prefeitura (licitação, contrato) — sem fonte confiável.
- Cadastro de usuário além do necessário para assinatura de alerta; nenhum dado pessoal de visitante.
- Identificar favorecido pessoa física (nome/CPF).

## Target Users

**Primary:** Morador — saber o que foi destinado à cidade dele e em que pé está, sem vocabulário técnico (inclusive no celular).

**Secondary:**
- Jornalista local / controle social — rastrear um valor da indicação ao pagamento, citar e conferir na fonte; usar a API.
- Gestor municipal — acompanhar o que está empenhado e ainda não foi pago.
- Operador de dados — publicar só lotes válidos e saber por que um lote foi recusado.

**Afetados (não usuários):** parlamentares e prefeituras — não podem ter atribuído a si o que não aconteceu.

## Context

**Business Context:** Disciplina DINF00071 — Desenvolvimento Dirigido por Especificação com Agentes (CI/UFPB, 2026.2). Ciclo por módulo: Plan → Audit → Apply → Unify. O risco do sistema é de **atribuição**, não de privacidade: uma tradução errada de fase pode afirmar que um parlamentar deixou de executar algo que executou.

**Technical Context:** Um repositório, quatro módulos independentes (`modulos/{ingestao,nucleo,consulta,saida}`, cada um com `.paul/` próprio). Contrato principal: **o lote publicado** — a ingestão publica; núcleo, consulta e saída leem sem saber como o CSV é lido. Cada módulo entrega sozinho: persistência, API, componente concorrente, desempenho medido e testes. Fonte real (T1 da Sarah): ZIP único cumulativo da CGU, sem chave, com `GET` condicional por ETag.

## Constraints

### Technical Constraints
- Back-end Python 3.12 + FastAPI (consenso das duas specs).
- Quatro módulos independentes, cada um com o envelope completo (persistência, API, concorrência, desempenho medido, testes), testável sozinho com duplo do lote publicado.
- Publicação atômica: leitor nunca vê lote/carga pela metade (ambas as specs).
- Tradução de fase em tabela versionada e auditável, nunca regra escondida no código.
- Toda informação exibida carrega fonte, lote e data de extração.
- Arquivos de dados fora do Git.
- WCAG 2.2 AA, pt-BR.

### Business Constraints
- 60 horas de disciplina; prazo do semestre 2026.2.
- Fase 1 (Fundação) idêntica para toda a turma.
- `CONTRATOS.md` do grupo (FI-02) ainda não existe no repositório — pré-requisito listado no README.
- Hospedagem a definir com o professor.

### Compliance Constraints
- LGPD: só o que a fonte publica; favorecido pessoa física agregado, sem nome nem CPF; nenhum dado pessoal de usuários (no máximo chave anônima de assinante).
- Atribuição obrigatória da fonte (CGU; Siga Brasil se usado).

## Key Decisions

| Decision | Rationale | Date | Status |
|----------|-----------|------|--------|
| PAUL na raiz cobre o sistema inteiro; inits por módulo vêm depois e referenciam este | Visão de grupo antes da divisão por módulo | 2026-11-24 | Active |
| Especificações mescladas; conflitos decididos em `/paul:plan` | As duas specs são válidas e complementares | 2026-11-24 | Active |
| Python 3.12 + FastAPI no back-end | Consenso das duas specs | 2026-11-24 | Active |
| Publicação por lote/versão imutável com troca atômica | JV ADR-0001, SA ADR-0002 | 2026-11-24 | Active |
| Estado derivado dos valores/etapa mais avançada, traduzido por tabela versionada | JV ADR-0006/0008, SA ADR-0003 | 2026-11-24 | Active |
| Previsto e recebido na cidade em blocos separados, sem somar | JV ADR-0010, SA ADR-0008 | 2026-11-24 | Active |
| Nenhum ranking de parlamentares | Brief; JV REQ-71, SA ADR-0004 | 2026-11-24 | Active |
| Enterprise plan audit habilitado | README define o ciclo Plan → Audit → Apply → Unify | 2026-11-24 | Active |

### Decisões de stack (2026-11-24, /paul:plan)

| Decision | Rationale | Status |
|----------|-----------|--------|
| PostgreSQL 16 | Restrições no schema (versão ativa única), lock consultivo, leitores concorrentes reais | Active |
| Next.js + TypeScript + shadcn/ui | Escolha do usuário; tipos gerados do OpenAPI | Active |
| Docker Compose | Ambiente reproduzível; deploy só com CI verde | Active |
| Recorte: PB todos os anos primeiro, Brasil 2025 depois (fase 6) | Validado na T1; ETL e testes rápidos antes de escalar | Active |
| Módulo `saida` mantido (chave anônima, alertas no painel) | README exige os 4 módulos | Active |
| uv workspace: `modulos/<m>/` = pacote `rastro_<m>`, `app/` compõe FastAPI, `web/` = Next; import-linter impõe independência | README: cada módulo independente e testável sozinho | Active |

### Open Decisions

| Tema | João Vitor | Sarah | Decidir em |
|------|-----------|-------|------------|
| Estados de execução | 5 estados (ADR-0006, *proposta*) | `fase_simples` com restos a pagar | Fase 3 |
| Coleta | `rastro sincronizar` idempotente | Diária, GET condicional por ETag | Fase 2 |

## Success Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Lote interrompido não vaza (QA-01/Q1) | 0 leituras de lote não publicado em 20 falhas injetadas | - | Not started |
| Respostas conforme contrato (QA-02/Q2) | 100% válidas contra `openapi.yaml`; 0 respostas 500; `/openapi.json` = arquivo versionado | - | Not started |
| Leitura durante publicação (QA-03/Q3) | 0 respostas mistas entre lotes; 0 alertas duplicados | - | Not started |
| Desempenho da consulta (QA-04/Q4) | p95 < 100 ms (detalhe) / < 500 ms (página município) — baseline primeiro | - | Not started |
| ETL do ZIP completo | ≤ 10 min | - | Not started |
| Testes (QA-05/Q5) | 100% dos REQ com teste no CI; cobertura ≥ 80% por módulo; 100% dos ramos da regra de fase | - | Not started |
| Tradução com fonte | 100% dos termos com fonte; 0 expressões proibidas | - | Not started |
| Acessibilidade | 0 violações axe serious/critical | - | Not started |

## Tech Stack / Tools

| Layer | Technology | Notes |
|-------|------------|-------|
| Back-end | Python 3.12, FastAPI, Uvicorn, uv workspace | Consenso |
| Banco | PostgreSQL 16 | |
| Front-end | Next.js + TypeScript + shadcn/ui (pnpm, Node 24) | |
| Carga | Processo Python próprio (contêiner `carga` no Compose) | Detalhe na fase 2 |
| Deploy | Docker Compose | Host a definir |
| Contratos | OpenAPI 3.1 (+ AsyncAPI 3.0 se `saida` tiver eventos) | Validado no CI |
| Testes | pytest, ruff, Schemathesis/teste de contrato, Locust ou script httpx, axe | |
| CI | GitHub Actions | Merge bloqueado com CI vermelho |
| Fonte | Portal da Transparência (CGU), ZIP de emendas; IBGE (municípios); Siga Brasil opcional | Atribuição obrigatória |

## Links

| Resource | URL |
|----------|-----|
| Repository | github.com/ddea-ufpb/rastro |
| Spec João Vitor | `especificacoes/joao-vitor/README.md` |
| Spec Sarah | `especificacoes/sarah-araujo/README.md` |

---
*PROJECT.md — Updated when requirements or context change*
*Created: 2026-11-24*
