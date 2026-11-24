# Arquitetura do Rastro — índice

Autor: João Rafael da Silva Sousa · DINF00071 · 2026.2
Base: FI-01 (Formulário de Ideação do Rastro, 19/11/2026), o brief do repositório (`README.md` de `ddea-ufpb/rastro`) e a coleta real do Trabalho 2 (`modulos/ingestao/coleta-favorecidos/`, 22/11/2026).

> **Rastro:** acompanha as emendas parlamentares federais ligadas aos municípios da Paraíba, da indicação ao pagamento, mostrando quem recebeu o dinheiro e em que fase cada emenda está, com a fonte oficial de cada informação (FI-01 §1.2).

Esta especificação dá ênfase ao que o meu FI-01 trouxe de próprio: **quem recebeu** (favorecido identificado só por CNPJ, com sugestões de mesma entidade que nunca entram em soma), **descartes visíveis** por município, e **alerta por e-mail** com entrega única.

## 1. Padrão escolhido: arc42 enxuto

O **arc42** (Starke e Hruschka) é o índice, e cada seção usa a notação que o enunciado pede. É o mesmo padrão das especificações da Sarah e do João Vitor, o que facilita a consolidação do grupo.

| Seção arc42 | Conteúdo | Notação | Arquivo |
| :-- | :-- | :-- | :-- |
| §1 Metas | Metas de qualidade, partes interessadas | texto | este README, seção 3 |
| §2 Restrições | Stack, dados, LGPD, prazo | texto | este README, seção 4 |
| §3 Contexto | Atores, sistemas externos, limites | C4 nível 1 (Mermaid) | [c4-contexto.md](c4-contexto.md) |
| §5 Blocos | Contêineres, quem escreve onde | C4 nível 2 (Mermaid) | [c4-conteineres.md](c4-conteineres.md) |
| §7 Implantação | Docker Compose | texto | fim de [c4-conteineres.md](c4-conteineres.md) |
| §9 Decisões | 10 decisões com o porquê | ADR (MADR) | [adr/](adr/) |
| §10 Qualidade | 5 cenários, um por item do envelope | Bass, Clements e Kazman (6 partes) | [qualidade.md](qualidade.md) |
| §12 Glossário | Domínio e sistema | texto | [glossario.md](glossario.md) |
| — Requisitos | REQ-01 a REQ-88, com módulo e telas | EARS | [requisitos.md](requisitos.md) |
| — Contratos | API, CLI, e-mails, fonte externa, modelo de dados | OpenAPI 3.1, Markdown, Mermaid ER | [contratos/](contratos/) |

As telas que consomem esta arquitetura estão em [`../telas/`](../telas/).

### Por que este padrão: as seis informações que o PAUL consome

| O PAUL precisa de | Onde está | Como vira entrada do PAUL |
| :-- | :-- | :-- |
| **Limites e vizinhos** | `c4-contexto.md` (seção "Limites"), `c4-conteineres.md` ("Quem escreve onde"), seção 6 deste README (módulos) | Escopo do `PROJECT.md` e *boundaries* de cada plano. Exemplo: "a API não escreve dado de fonte", "nenhuma fusão de CNPJs" |
| **Decisões e porquês** | `adr/0001`–`0010`, com opções descartadas | Decisões que o agente não reabre. Exemplo: "unir por nome foi descartado pelo caso dos 71 fundos municipais" |
| **Contratos** | `contratos/openapi.yaml` (17 operações com `x-modulo`), `cli.md`, `email-alerta.md`, `fonte-portal.md`, `modelo-de-dados.md` | Tasks com `files` e `verify` precisos. Exemplo: "`obter_favorecido` responde 422 para CNPJ de 13 dígitos" |
| **Requisitos testáveis** | `requisitos.md`: cada REQ com o teste que o verifica | U → *Then* em qualquer cenário; E → *When*; S → *Given* um estado; I → *Given* a condição indesejada; O → *Given* a opção ligada. "O SISTEMA DEVE …" é sempre o *Then*. A tabela final liga AC-1 a AC-3 do FI-01 aos REQ |
| **Qualidade com medida** | `qualidade.md`: QA-01 persistência, QA-02 API, QA-03 concorrência, QA-04 desempenho, QA-05 testes | ACs do envelope com número e ferramenta (0 misturas em 100 execuções, 0 e-mails duplicados, p95 do k6) |
| **Restrições** | seção 4 deste README, ADR-0004 (dado pessoal), ADR-0006 (e-mail) | Stack, hospedagem e LGPD que o *audit* cobra |

**Alternativas consideradas:** o arc42 completo teria seções vazias (§6, §8, §11) num MVP de 60 horas, e o agente trata seção vazia como decisão. O 4+1 pede visões, como a física, com pouco conteúdo aqui. Spec Kit e Kiro cobrem requisitos e tarefas, mas não têm lugar natural para C4 nem para cenários de qualidade.

### Referências

- Starke, G.; Hruschka, P. *arc42*. https://arc42.org
- Brown, S. *The C4 model*. https://c4model.com
- Nygard, M. *Documenting Architecture Decisions*, 2011; *MADR*. https://adr.github.io/madr/
- Mavin, A. et al. *Easy Approach to Requirements Syntax (EARS)*. IEEE RE, 2009.
- Bass, L.; Clements, P.; Kazman, R. *Software Architecture in Practice*, 4. ed., 2021.
- OpenAPI 3.1 (https://spec.openapis.org/oas/v3.1.0); RFC 9457 (*Problem Details for HTTP APIs*); WCAG 2.2.

## 2. O que muda em relação ao FI-01

| Lacuna do FI-01 §12 | Fechada por |
| :-- | :-- |
| Volume real da base PB | 31 840 linhas de pagamento no recorte, 19 647 de pessoa jurídica, 2 353 CNPJs (T2, `contratos/fonte-portal.md`) |
| Qual arquivo traz o CNPJ do favorecido | `EmendasParlamentares_PorFavorecido.csv`, no mesmo zip (`fonte-portal.md`) |
| MEI com nome de pessoa | Descartado como pessoa: 17 de 190 empresários individuais tinham o CPF no nome ([ADR-0004](adr/0004-descartar-pessoa-fisica-e-empresario-individual-antes-de-persistir.md)) |
| Município do favorecido | A fonte traz só o nome; o código IBGE é casado pelo nome (`fonte-portal.md`) |
| "Mudança de fase" | Fase derivada dos valores com restos a pagar ([ADR-0005](adr/0005-derivar-a-fase-dos-valores-e-traduzir-por-tabela-versionada.md)) e mudança calculada na publicação (REQ-34) |
| Confirmação do e-mail | Confirmação dupla e token de gestão no fragmento ([ADR-0006](adr/0006-alertar-por-email-com-confirmacao-dupla-e-entrega-unica.md)) |
| Tempo-limite da importação | ⟨30 min⟩ provisório (REQ-12), revisto depois de QA-04 |

Continuam abertos: o texto simples de cada fase precisa de revisão por alguém de orçamento (antes da feature 1); retenção de importações antigas (quando a feature 5 entrar); metas de desempenho (depois do baseline de QA-04); hospedagem e domínio do e-mail (com o grupo).

## 3. Metas (arc42 §1)

| Meta (prioridade) | Por quê | Onde é medida |
| :-- | :-- | :-- |
| 1. **Atribuição correta**: nenhum dinheiro atribuído a quem não recebeu | Risco principal do FI-01 (§4.4, §8.2) | REQ-21, REQ-30, REQ-37, ADR-0001, ADR-0005, QA-05 |
| 2. **Rastreabilidade**: todo valor leva à linha do arquivo oficial | Aposta central (FI-01 §4.4) | REQ-28, REQ-29, REQ-75, QA-02 |
| 3. **Consistência sob atualização e entrega única** | FI-01 §7.1 | REQ-10, REQ-65, QA-01, QA-03 |
| 4. **Nada some sem explicação**: descartes visíveis | FI-01 §8.4 | REQ-26, REQ-40, ADR-0009 |
| 5. **Desempenho medido** | FI-01 §7.2 | QA-04 |

| Parte interessada | Expectativa |
| :-- | :-- |
| Morador | Ver o que foi destinado à cidade e em que fase está, sem vocabulário técnico |
| Jornalista / controle social | Rastrear um valor até o pagamento e a entidade, com a fonte |
| Gestor municipal | Acompanhar o empenhado e não pago, com aviso por e-mail |
| Operador de dados | Importar sem medo de publicar dado quebrado; revisar sugestões |
| Parlamentares, entidades, pessoas na fonte, municípios com dado sujo (afetados) | Ver c4-contexto.md, "Afetados que não são usuários" |
| Grupo e professor | Ids estáveis, contratos com o módulo dono, decisões com o porquê |

## 4. Restrições (arc42 §2)

| Tipo | Restrição | Origem |
| :-- | :-- | :-- |
| Técnica | Python 3.12, FastAPI, PostgreSQL 16, asyncio + httpx, pytest; TypeScript + React (Vite), Vitest, Playwright + axe; k6; Docker Compose; GitHub Actions | FI-01 §6, ADR-0007, ADR-0008 |
| Máquina | 8 GB de RAM: importação em fluxo, sem carregar o zip em memória | FI-01 §10.3, REQ-88 |
| Dados | Só o zip público da CGU; bruto guardado com data, fora do Git | FI-01 §10.4, `fonte-portal.md` |
| Privacidade (LGPD) | Nenhum dado de pessoa física da fonte; único dado pessoal de usuário é o e-mail da assinatura, apagado ao cancelar | FI-01 §8, ADR-0004, ADR-0006 |
| Conteúdo | Sem ranking ou nota de parlamentar; sem palavras de acusação; aviso de que o sistema não avalia mérito | FI-01 §5, §8.4, REQ-52, REQ-82, REQ-83 |
| Escopo | Emendas federais ligadas à PB | FI-01 §5 |
| Organizacional | 60 h; conta Claude Pro; modelo local a partir da semana 8 (sugestões com `origem = modelo_local`) | FI-01 §10.3 |

## 5. Decisões (ADR)

| ADR | Decisão | Status |
| :-- | :-- | :-- |
| [0001](adr/0001-identificar-favorecido-so-por-cnpj-e-tratar-nome-parecido-como-sugestao.md) | Favorecido só por CNPJ; nome parecido vira sugestão, nunca soma | aceita |
| [0002](adr/0002-publicar-a-importacao-inteira-numa-transacao-do-postgresql.md) | Importação publicada numa transação, com ponteiro de vigente | aceita |
| [0003](adr/0003-exigir-proveniencia-em-todo-registro-e-devolve-la-na-api.md) | Proveniência `NOT NULL` por registro e devolvida com cada valor | aceita |
| [0004](adr/0004-descartar-pessoa-fisica-e-empresario-individual-antes-de-persistir.md) | Descartar pessoa física e empresário individual antes de persistir | aceita |
| [0005](adr/0005-derivar-a-fase-dos-valores-e-traduzir-por-tabela-versionada.md) | Fase derivada dos valores com restos a pagar; tradução por tabela versionada | aceita |
| [0006](adr/0006-alertar-por-email-com-confirmacao-dupla-e-entrega-unica.md) | E-mail com confirmação dupla e entrega única por mudança | aceita |
| [0007](adr/0007-usar-asyncio-com-escritor-unico-e-fila-de-alertas.md) | asyncio com escritor único na importação e fila nos alertas | aceita |
| [0008](adr/0008-separar-interface-react-vite-da-api-com-tipos-gerados.md) | Interface React + Vite separada da API, tipos gerados | aceita |
| [0009](adr/0009-expor-descartes-por-municipio-junto-do-resultado.md) | Descartes por município junto do resultado | aceita |
| [0010](adr/0010-separar-o-destinado-a-cidade-do-recebido-por-entidades-da-cidade.md) | No município, destinado e recebido separados, sem somar | aceita |

## 6. Mapa para os quatro módulos

O contrato principal do brief é **a importação publicada**: a ingestão publica; núcleo, consulta e saída leem, sem saber como o CSV é lido. A coluna "Módulo" de [requisitos.md](requisitos.md) e o `x-modulo` de cada operação seguem este mapa.

| Módulo | O que faz | Requisitos | Contratos | Telas |
| :-- | :-- | :-- | :-- | :-- |
| `ingestao` | Baixa, valida, normaliza, descarta com motivo, publica numa transação | REQ-01–09, 11, 12, 14–26, 28, 85, 86, 88 | `cli:importar`, `cli:importacoes`; `listar_importacoes`, `obter_importacao`; `fonte-portal.md` | O01, P09 |
| `nucleo` | Fase e tradução, mudanças entre importações, sugestões de mesma entidade | REQ-30–36, 38 | `cli:traducao`, `cli:sugestoes`; `listar_traducoes`; função `fase()` e `MudancaFase` | O02, P10 |
| `consulta` | API de leitura e agregações; contrato versionado | REQ-10, 13, 27, 29, 37, 39–60, 87 | `obter_status`, `listar_municipios`, `obter_municipio`, `listar_emendas`, `obter_emenda`, `listar_pagamentos_emenda`, `listar_favorecidos`, `obter_favorecido`, `obter_agregacoes`, `obter_parlamentar` | P01–P08 |
| `saida` | Assinaturas, e-mail, alertas com entrega única | REQ-61–74 | `criar_assinatura`, `confirmar_assinatura`, `obter_assinatura`, `excluir_assinatura`; `cli:alertas`; `email-alerta.md` | S01–S03 |
| todos | Interface transversal | REQ-75–84 | — | todas as telas web |

### Envelope de cada módulo

| Módulo | Persistência (só ele escreve) | API | Concorrência | Desempenho medido | Testes |
| :-- | :-- | :-- | :-- | :-- | :-- |
| `ingestao` | `Importacao`, `ImportacaoVigente`, `Emenda`, `Autor`, `Pagamento`, `Favorecido`, `NomeFavorecido`, `Descarte` | CLI + `listar_importacoes`, `obter_importacao` | Workers de leitura + escritor único, `ON CONFLICT (cnpj)` (REQ-14; QA-03) | Importação completa por etapa, 1/2/4 workers (REQ-85, REQ-88; QA-04) | regras R-*, AC-1 a AC-3, QA-01 |
| `nucleo` | `MudancaFase`, `SugestaoMesmaEntidade`, `VersaoTraducao`, `TraducaoFase` | `listar_traducoes`, `cli:sugestoes`, `cli:traducao` | Cálculo de mudanças e sugestões dentro da transação de publicação, com leitores em snapshot (REQ-10, REQ-34) | Tempo de mudanças + sugestões em `duracao_ms.publicacao` (QA-04) | `test_fase.py` com linhas reais, `test_sugestoes.py` |
| `consulta` | nenhuma tabela de fonte (lê a vigente) | 10 operações de leitura | Leituras `REPEATABLE READ` durante a publicação; limite por IP (REQ-10, REQ-58) | p95 de `obter_agregacoes` e `obter_municipio` com k6 (REQ-87) | QA-02 (Schemathesis), e2e das telas P |
| `saida` | `Assinatura`, `AlertaEnviado` | 4 operações de assinatura | Despachante com `asyncio.Queue` e `UNIQUE` da tripla (REQ-65–69) | Tempo para esvaziar 500 × 300 alertas no Mailpit (QA-03) | `test_despachante.py`, e2e das telas S |

## 7. Índice de arquivos

```
arquitetura/
├── README.md                ← este arquivo
├── c4-contexto.md           ← C4 nível 1
├── c4-conteineres.md        ← C4 nível 2 + implantação
├── adr/                     ← 0001 … 0010 (MADR)
├── requisitos.md            ← REQ-01 … REQ-88 (EARS)
├── contratos/
│   ├── openapi.yaml         ← API JSON, 17 operações
│   ├── cli.md               ← comandos do operador
│   ├── email-alerta.md      ← e-mails de confirmação e de alerta
│   ├── fonte-portal.md      ← formato real do zip da CGU (T2)
│   └── modelo-de-dados.md   ← entidades, restrições, ER
├── qualidade.md             ← QA-01 … QA-05
└── glossario.md
```
