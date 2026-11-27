---
description: "Todo pagamento de emenda ligada à PB chega ao banco com a entidade certa (por CNPJ) e a linha de origem, e nada é descartado sem motivo"
type: Project
about: "rastro-ingestao"
---

# rastro-ingestao

## What This Is

Módulo `ingestao` do Rastro: baixa o zip de emendas do Portal da Transparência (CGU), normaliza os pagamentos a favorecidos ligados à Paraíba, descarta com motivo o que não pode entrar (pessoa física, sem CNPJ) e publica cada importação de forma atômica. O trabalho atual é o Trabalho 2 do João Rafael: coleta dos favorecidos PJ (Etapa 1) e enriquecimento com modelo local, que decide se dois nomes são a mesma entidade e classifica a natureza (Etapa 2).

## Core Value

Todo pagamento de emenda ligada à PB chega ao banco com a entidade certa (por CNPJ) e a linha de origem, e nada é descartado sem motivo.

## Current State

| Attribute | Value |
|-----------|-------|
| Type | Application (pipeline de dados + CLI) |
| Version | 0.1.0 |
| Status | Prototype — Etapa 1 do T2 enviada (PR #8); Etapa 2 a fazer |
| Last Updated | 2026-11-27 |

## Requirements

### Core Features

- Coletar e normalizar os pagamentos a favorecidos PJ das emendas ligadas à PB, com proveniência por linha e descartes com motivo (T2 Etapa 1).
- Usar os nomes do `CONTRATOS.md` do grupo e, onde ele não fixa nome, os da spec do T1 (`especificacoes/joao-rafael/`).
- Decidir com modelo local se dois nomes de CNPJs diferentes são a mesma entidade e classificar a natureza (T2 Etapa 2).
- Entregar `dados.jsonl`, `ESQUEMA.md` e `carregar.py` que um colega consiga usar sem perguntar.

### Validated (Shipped)
- ✓ Corpus da Etapa 1 no vocabulário do grupo, em centavos, reprodutível de checkout limpo — Phase 1 (PR #8)

### Active (In Progress)
- [ ] Gabarito de 40 itens rotulado à mão (Phase 2).

### Planned (Next)
- [ ] Enriquecedor com laço próprio, ≥ 2 ferramentas de domínio + `registrar`, duas medições (spec pobre e boa).
- [ ] Entrega: `dados.jsonl`, `ESQUEMA.md`, `carregar.py`, relatório (até 01/12).

### Out of Scope
- Fusão de CNPJs diferentes — nome parecido vira sugestão, nunca soma (ADR-0001 do T1).
- Dado de pessoa física, inclusive empresário individual — descartado antes de persistir (ADR-0004 do T1).
- API, interface e alertas — são dos módulos `consulta` e `saida`.
- Framework de agentes — o tutorial do T2 proíbe; o laço é escrito à mão.

## Target Users

**Primary:** colegas do grupo que consomem a importação publicada (`nucleo`, `consulta`, `saida`).
- Precisam de nomes estáveis do `CONTRATOS.md` e de um script de carga que funcione.

**Secondary:** professor (avaliação do T2) e jornalista que confere a origem de um valor.

## Context

**Business Context:** disciplina DINF00071 (60 h). T2 com prazos: E1 24/11, gabarito 26/11, entrega final 01/12. Critérios C2 (nomes do CONTRATOS.md) e C4 (uma decisão que muda pelo que foi medido).

**Technical Context:** fonte = zip único da CGU (~47 MB, Windows-1252, `;`). Coleta de 22/11/2026: 31 840 linhas no recorte, 19 647 pagamentos PJ, 2 353 CNPJs, 12 193 descartes. `CONTRATOS.md` ainda é rascunho (PR #5).

## Constraints

### Technical Constraints
- Python 3.12, só stdlib e parser/HTTP; sem framework de agente.
- Modelo local com tag fixa (`qwen3:1.7b` primeiro), `temperature: 0`; máquina de 8 GB de RAM.
- Rodar o coletor duas vezes gera arquivo idêntico (sha256).

### Business Constraints
- Prazos do T2: 24/11 (E1), 26/11 (gabarito), 01/12 (final).
- Nomes do `CONTRATOS.md`; mudança de nome é proposta ao grupo, não decidida sozinha.

### Compliance Constraints
- LGPD: nenhum nome ou CPF de pessoa no corpus, nos descartes ou no git; zip original fora do git.

## Key Decisions

| Decision | Rationale | Date | Status |
|----------|-----------|------|--------|
| Nomes do CONTRATOS.md (`RegistroFavorecido`, `codigo_emenda`, `*_centavos`); demais da spec do T1 | Critério C2 do T2 | 2026-11-24 | Active |
| Alinhar a E1 antes de enviar | Escolha do autor, mesmo com o prazo de 24/11 | 2026-11-24 | Done (PR #8) |
| Dinheiro em centavos inteiros na fronteira | REQ-24 do T1; `*_centavos` ainda [decidir] no PR #5 | 2026-11-27 | Active |
| Categorias de natureza: prefeitura, autarquia, hospital, osc, consorcio, empresa, orgao_estadual, outro | 1 518 fornecedores e órgãos estaduais não cabem nas 5 do enunciado | 2026-11-27 | Active |
| Empresário individual descartado como pessoa | 17 de 190 com CPF no nome (ADR-0004 do T1) | 2026-11-22 | Active |
| Plan → Audit → Apply → Unify | Fluxo do README do repo | 2026-11-24 | Active |

## Success Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Itens no corpus | ≥ 150 | 2 353 | On track |
| Reexecução do coletor gera arquivo idêntico | sim | sim (sha256) | Achieved |
| Campos com nomes do CONTRATOS.md / T1 | 100% | 100% | Achieved |
| Gabarito em commit antes da 1ª execução | sim | - | Not started |
| Medições com as 5 medidas | 2 | 0 | Not started |

## Tech Stack / Tools

| Layer | Technology | Notes |
|-------|------------|-------|
| Linguagem | Python 3.12 | `csv`, `zipfile`, `hashlib`, `json` da stdlib |
| Modelo local | Ollama 0.40.18 (Windows) `qwen3:1.7b` | tag fixa, `temperature: 0`; i5-1135G7, 7,8 GB, sem GPU dedicada |
| Testes | `unittest` / pytest | regra com a linha real que a motivou |
| Destino | PostgreSQL (spec do T1) / SQLite no `carregar.py` | a decidir no plano da Etapa 2 |

## Links

| Resource | URL |
|----------|-----|
| Repository | https://github.com/ddea-ufpb/rastro |
| Spec T1 | `especificacoes/joao-rafael/` (PR #6) |
| Contrato do grupo | `CONTRATOS.md` (PR #5, rascunho) |

---
*Created: 2026-11-24*
*Last updated: 2026-11-27 after Phase 1*
