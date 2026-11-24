# Trabalho 1 — Telas e arquitetura · João Rafael da Silva Sousa

João Rafael da Silva Sousa · matrícula 20240102272 · DINF00071 · 24/11/2026

Especificação individual do sistema completo **Rastro**, feita a partir do meu FI-01 (Formulário de Ideação, 19/11/2026), alinhada ao brief do repositório (consulta por município, tradução por tabela versionada, nenhum ranking, os três papéis e os quatro módulos `ingestao`, `nucleo`, `consulta`, `saida`) e ancorada nos dados reais da coleta do Trabalho 2 (`modulos/ingestao/coleta-favorecidos/`, 22/11/2026).

O foco próprio desta versão vem do FI-01: **quem recebeu o dinheiro** (favorecido identificado só por CNPJ; nome parecido vira sugestão revisável e nunca entra em soma), **nada some sem explicação** (descartes por município visíveis) e **alerta por e-mail** com confirmação dupla e entrega única.

| Parte | Comece por | Conteúdo |
| :-- | :-- | :-- |
| (a) Interface | [telas/diretrizes.md](telas/diretrizes.md) → [telas/inventario.md](telas/inventario.md) | 15 telas (P01–P10, S01–S03, O01–O02), 4 atores, 3 superfícies (web, e-mail, CLI), mapa de navegação e 8 fluxos |
| (b) Arquitetura | [arquitetura/README.md](arquitetura/README.md) | arc42 enxuto: C4 1 e 2, mapa dos 4 módulos, 10 ADRs (MADR), 88 requisitos EARS com módulo e telas, OpenAPI 3.1 (17 operações), CLI, e-mails, contrato da fonte real, modelo de dados, 5 cenários de qualidade, glossário |
| Conferência | [verificar.py](verificar.py) | Confere fichas, estados, ações, navegação, requisitos, operações, links e contraste |

## Checklist do enunciado

**Parte (a), seção 2:**

- [x] 2.1 `diretrizes.md`: público, plataforma e orientação, tom de voz e de interface, 5 princípios verificáveis (3 a 5), referência visual (inspira / evitar), pt-BR e WCAG 2.2 AA.
- [x] 2.2 `inventario.md`: 15 telas (≥ 10) com id estável, nome, ator e superfície; mapa de navegação; cobertura de todos os atores e superfícies e dos fluxos principais.
- [x] 2.3 Uma ficha por tela com os 11 campos do template (Superfície · ator, Objetivo, Chega de / vai para, Mostra, Coleta, Ações, Estados, Regras, Requisitos · contrato, Acessibilidade, Anexo); objetivo em uma frase; Coleta no formato `campo · tipo · obrigatório?`; os 6 estados (carregando, vazio, erro, sucesso, offline, sem permissão).

**Diretivas da seção 2.4:**

| Diretiva | Como foi atendida | Conferida por |
| :-- | :-- | :-- |
| Id estável citado na ficha, no inventário e nos requisitos | Título da ficha, quadro do inventário e coluna "Telas" de `requisitos.md` | `verificar.py` (gera e confere a coluna) |
| Uma intenção por tela | "Objetivo" em uma frase | `verificar.py` |
| Todos os estados | Os 6 estados em toda ficha, cada um citando REQ ou ADR | `verificar.py` |
| Campos com nomes do modelo | `Entidade.campo` / `Schema.campo` de `modelo-de-dados.md` e `openapi.yaml` em Mostra e Coleta | revisão |
| Toda ação aponta um contrato | (`operação`), → Pxx (`operação`), (`cli:…`), (`email:…`) ou "ação local · sem chamada à API (REQ-81)" | `verificar.py` |
| Diretrizes escritas uma vez | Estados e elementos comuns em `diretrizes.md` | revisão |
| Intenção, não pixel | Fichas descrevem dado e comportamento | revisão |
| Mock como anexo | O anexo é opcional (seção 2.3); nenhuma ficha depende de mock, e o campo "Anexo" diz isso | revisão |

**Parte (b), seção 3.3:**

- [x] `README.md`: padrão (arc42 enxuto, recomendado na seção 3.2), referências e justificativa pelas 6 informações da seção 3.1; serve de índice.
- [x] `c4-contexto.md` e `c4-conteineres.md`.
- [x] `adr/`: 10 ADRs (≥ 3) no formato MADR, com opções descartadas.
- [x] `requisitos.md`: REQ-01…REQ-88 nos cinco moldes EARS, com origem, verificação, módulo e telas.
- [x] `contratos/`: `openapi.yaml` (17 operações, todas usadas por telas, validado), `cli.md`, `email-alerta.md`, `fonte-portal.md` (formato real do zip), `modelo-de-dados.md`.
- [x] `qualidade.md`: 5 cenários de 6 partes (persistência, API, concorrência, desempenho, testes).
- [x] `glossario.md`.

## Como conferir

```bash
pip install pyyaml openapi-spec-validator
python especificacoes/joao-rafael/verificar.py
```

Saída esperada: `OK · 15 telas · 88 requisitos · 17 operações HTTP · 5 comandos CLI · 10 ADRs`.

## Diferenças em relação às especificações da Sarah e do João Vitor

| Tema | Aqui | Por quê |
| :-- | :-- | :-- |
| Empresário individual | Descartado como pessoa | 17 de 190 tinham CPF no nome (T2; ADR-0004) |
| Mesma entidade | Só por CNPJ; sugestão revisável na CLI, nunca somada | FI-01 §8.3; caso dos 71 fundos municipais (ADR-0001) |
| Alerta | E-mail com confirmação dupla | FI-01 §3.1 e §8.1 escolheram o e-mail (ADR-0006) |
| Persistência | PostgreSQL com ponteiro de importação vigente | FI-01 §6 (ADR-0002) |
| Município | Destinado e recebido por entidades da cidade em blocos separados, mais descartes | ADR-0009, ADR-0010 |
