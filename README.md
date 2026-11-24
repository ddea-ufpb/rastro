# Rastro

Acompanhamento das emendas parlamentares federais destinadas a um município, com o estado de
execução traduzido para linguagem que o morador entende.

> **Status:** Fase 1 (Fundação) em andamento, com o plano 01-01 concluído: scaffold do monorepo e CI
> que falha quando deve. Ainda não há funcionalidade de domínio. Andamento detalhado em
> [`.paul/STATE.md`](.paul/STATE.md) e [`.paul/ROADMAP.md`](.paul/ROADMAP.md).
>
> **Disciplina:** DINF00071 — Desenvolvimento Dirigido por Especificação com Agentes · CI/UFPB · 2026.2

---

## O problema

Emendas parlamentares destinam dinheiro federal a municípios, e o dado é público por obrigação
legal. Ainda assim, o morador não consegue responder a pergunta que importa: *aquela emenda para a
minha cidade virou alguma coisa?* O dado existe em CSV de dezenas de colunas, e o estado da execução
é descrito em vocabulário orçamentário — empenhado, liquidado, pago — que não diz nada a quem não
trabalha com orçamento público.

A consequência é que a transparência existe no papel e não existe na prática: quem fiscalizaria não
consegue ler, e quem consegue ler já é especialista.

## O que o sistema faz

Importa os dados oficiais em lotes, normaliza e guarda a proveniência de cada registro, traduz as
fases de execução para linguagem simples, expõe consulta por município e avisa quem assinou quando
alguma coisa muda entre um lote e o seguinte.

## Quem usa

| Papel | O que precisa |
|---|---|
| Morador | Saber o que foi destinado à cidade dele e em que pé está, sem vocabulário técnico |
| Jornalista local / controle social | Rastrear um valor da indicação ao pagamento, com a fonte de cada afirmação |
| Gestor municipal | Acompanhar o que está empenhado mas não executado |

## Fora de escopo (preliminar — o grupo fecha e justifica)

- Emendas estaduais e municipais: fonte e estrutura diferentes, não cabem no prazo.
- Juízo sobre mérito ou qualidade da emenda: o sistema mostra o caminho do dinheiro, não opina.
- Cruzamento com execução de obra em campo: não há fonte confiável.
- Cadastro de usuário além do necessário para assinatura de alerta.

## Módulos

Um repositório, quatro módulos independentes. Cada módulo tem persistência, API, componente
concorrente, desempenho medido e testes — os cinco, sozinho.

| # | Módulo | Responsável | O que faz |
|---|---|---|---|
| 1 | `ingestao` | *a definir* | Baixa, valida e normaliza os lotes oficiais; guarda proveniência por registro; publica o lote de forma atômica |
| 2 | `nucleo` | *a definir* | Calcula a diferença entre lotes e o estado de execução consolidado de cada emenda |
| 3 | `consulta` | *a definir* | API e busca por município, parlamentar e função; agregações; contrato versionado |
| 4 | `saida` | *a definir* | Assinaturas por filtro e limiar; disparo de alerta com entrega única por assinante |

**Contrato principal:** o lote publicado. A ingestão publica; núcleo, consulta e saída leem — e
nenhum deles sabe como o CSV da origem é lido.

## Dados e privacidade

Dado público e agregado, sem titular identificado. O risco aqui não é privacidade, é **atribuição**:
uma tradução errada de fase pode fazer o sistema afirmar que um parlamentar deixou de executar algo
que ele executou. Por isso:

- Toda informação exibida carrega a fonte, o lote e a data de extração.
- A tradução de fase é tabela versionada e auditável, nunca regra escondida no código.
- O sistema não classifica, não pontua e não ranqueia parlamentares.

**Fontes previstas:** Portal da Transparência / CGU (dados abertos, CSV com dicionário) e Siga Brasil
(Senado), com atribuição obrigatória da fonte.

## Stack

Decidida no `/paul:plan` a partir das três especificações do Trabalho 1. O registro das decisões e
dos pontos ainda abertos está em [`.paul/PROJECT.md`](.paul/PROJECT.md).

| Camada | Escolha |
|---|---|
| Back-end | Python 3.12, FastAPI, uv workspace (um pacote por módulo) |
| Banco | PostgreSQL 16, um schema por módulo; os módulos leem o lote publicado só por views, com papel só-leitura |
| Migrações | Alembic com SQL explícito, por módulo |
| Front-end | Next.js + TypeScript (strict) + shadcn/ui, pnpm, Node 24 |
| Implantação | Docker Compose; publica só com o CI verde |
| CI | GitHub Actions: ruff, import-linter, pytest isolado por módulo (cobertura ≥ 80%), lint/tipos/build do web |

Recorte do MVP: emendas federais da Paraíba, todos os anos. A expansão para Brasil 2025 fica na Fase 6.

## Estrutura do repositório

```
rastro/
├── README.md               # este arquivo — brief do projeto
├── pyproject.toml, uv.lock # raiz do uv workspace (ruff, pytest, import-linter)
├── modulos/
│   ├── ingestao/           # pacote rastro_ingestao (src/, tests/, .paul/)
│   ├── nucleo/             # pacote rastro_nucleo
│   ├── consulta/           # pacote rastro_consulta
│   └── saida/              # pacote rastro_saida
├── app/                    # rastro_app: compõe as rotas dos módulos num único FastAPI
├── web/                    # painel Next.js
├── especificacoes/         # Trabalho 1: telas e arquitetura de cada integrante
├── .paul/                  # PAUL do sistema: PROJECT, ROADMAP, STATE, planos por fase
├── .github/workflows/ci.yml
└── CONTRATOS.md            # FI-02 (rascunho no PR #5)
```

Os módulos não importam uns aos outros: o import-linter quebra o CI se isso acontecer, e cada módulo
roda os testes num ambiente que só contém ele mesmo.

## Como rodar

```bash
# Python (uv ≥ 0.11, Python 3.12)
uv sync --all-packages
uv run ruff check . && uv run ruff format --check . && uv run lint-imports
uv run --exact --package rastro-ingestao pytest modulos/ingestao   # um módulo, isolado
uv run pytest app
uv run uvicorn rastro_app.main:app --reload                         # GET /health

# Web (Node 24, pnpm)
cd web
export NEXT_TELEMETRY_DISABLED=1
pnpm install --frozen-lockfile
pnpm dev                                                            # http://localhost:3000
pnpm lint && pnpm typecheck && pnpm build
```

A partir do plano 01-02, os testes do banco precisam do Docker, que sobe o PostgreSQL 16 via
testcontainers.

## Artefatos de entrada do `/paul:init`

O init de cada módulo só roda depois que isto estiver no repositório:

- [ ] **FI-01 de cada integrante**, com as seções 7 e 8 escritas no nível do módulo
- [ ] **CONTRATOS.md** do grupo: os quatro módulos, os contratos entre pares que se tocam e o duplo de cada contrato. Há um rascunho no PR #5 (draft).
- [ ] **Teste de independência** respondido por cada integrante
- [x] **Telas do sistema** (Trabalho 1)
- [x] **Artefatos de arquitetura** (Trabalho 1)

As telas e a arquitetura do Trabalho 1 estão em [`especificacoes/`](especificacoes/), todas no
formato arc42 enxuto (C4, ADRs em MADR, requisitos em EARS, OpenAPI 3.1, cenários de qualidade):

| Integrante | Pasta | Telas | Requisitos | ADRs | Situação |
|---|---|---|---|---|---|
| Sarah Araújo | [`sarah-araujo/`](especificacoes/sarah-araujo/) | 15 | 82 | 9 | mesclado |
| João Vitor | [`joao-vitor/`](especificacoes/joao-vitor/) | 19 | 112 | 10 | mesclado |
| João Rafael | [`joao-rafael/`](especificacoes/joao-rafael/) | 15 | 88 | 10 | mesclado |

O PAUL da raiz (`.paul/`) junta as três especificações. Onde há consenso, ele já registra a decisão.
Onde divergem (favorecido por CNPJ, canal de alerta, modelo de fases), a questão fica aberta até a
fase em que precisa ser decidida.

## Como o trabalho é conduzido

Cada módulo roda o ciclo **Plan → Audit → Apply → Unify**: o plano declara critérios de aceitação
verificáveis, a auditoria revisa antes de qualquer código, a execução segue o plano aprovado e o
fechamento compara planejado com entregue.

A **Fase 1 (Fundação)** é a mesma para todos os projetos da turma: scaffold com CI que falha quando
deve, banco com as restrições de dados no schema, e deploy que só publica com o CI verde. A
diferença entre os projetos começa na Fase 2.

### Roteiro (v0.1)

| Fase | Entrega | Situação |
|---|---|---|
| 1. Fundação | 01-01 scaffold + CI · 01-02 schema PostgreSQL com restrições · 01-03 Compose + deploy só com CI verde + proteção da `main` | 01-01 concluído (PR #7); 01-02 planejado |
| 2. Ingestão PB | ZIP da CGU, validação, proveniência, publicação atômica | — |
| 3. Núcleo | Fase de execução derivada dos valores, tradução versionada, mudanças entre lotes | — |
| 4. Consulta | API `/api/v1` e telas no Next | — |
| 5. Saída | Assinaturas e alertas com entrega única | — |
| 6. Brasil 2025 + desempenho | Recorte nacional e metas de desempenho medidas | — |

## Licença

MIT.
