# Esquema de `dados.jsonl`

Uma linha JSON por mudança de emenda entre dois lotes da CGU: o item do
`corpus.jsonl` da Etapa 1, sem alteração, mais os campos do enriquecimento.
Os nomes seguem o modelo de dados do Trabalho 1,
`especificacoes/joao-vitor/arquitetura/contratos/modelo-de-dados.md`, que
está na branch `trabalho1/joao-vitor` (PR #2 do ddea-ufpb/rastro) e ainda
não na `main`. O grupo ainda não tem um `CONTRATOS.md` comum.

Para usar sem ler o JSON: `python3 carregar.py dados.jsonl --banco rastro.db`
(ver o fim deste arquivo).

## Campos que vêm da Etapa 1

| Campo | Tipo | Obrigatório | Significado |
| :-- | :-- | :-- | :-- |
| `id` | texto | sim | `rastro-mud-<lote_novo sem hífens>-<codigo_emenda>` |
| `chave` | texto | sim | SHA-256 de `codigo_emenda\|lote_anterior\|lote_novo`, a chave de deduplicação |
| `texto` | texto | sim | Descrição determinística da mudança, gerada pelo coletor |
| `fonte` | texto | sim | Arquivo bruto e linha do CSV de onde a emenda veio |
| `coletado_em` | data `AAAA-MM-DD` | sim | Data da coleta do lote novo |
| `campos.codigo_emenda` | texto, 12 dígitos | sim | `Emenda.codigo` |
| `campos.lote_anterior` / `campos.lote_novo` | data `AAAA-MM-DD` | sim | `LoteImportacao.data_referencia` dos dois lotes comparados |
| `campos.presenca` | `alterada` \| `nova` \| `removida` | sim | Se a emenda está nos dois lotes, só no novo ou só no anterior |
| `campos.alteracoes[]` | lista | sim (vazia em `nova` e `removida`) | Cada campo que mudou: `campo`, `antes`, `depois` e, em valor, `diferenca_centavos` |
| `campos.estado_antes` / `campos.estado_depois` | `estado_execucao` ou nulo | sim | `sem_execucao` \| `empenhada` \| `liquidada` \| `paga_em_parte` \| `paga` (REQ-105 do Trabalho 1) |
| `campos.mudancas_lote[]` | lista de `{tipo, etapa}` | sim | As linhas de `MudancaLote` que a mudança gera: `nova_emenda`, `valor_alterado` (uma por etapa) e `estado_alterado` |
| `campos.emenda` | objeto | sim | A emenda no lote mais recente em que aparece, com os nomes de `Emenda` e os valores `*_centavos` |

## Campos do enriquecimento

| Campo | Tipo | Obrigatório | Significado |
| :-- | :-- | :-- | :-- |
| `sentido` | `avanco` \| `recuo` \| `nova` \| `removida` \| `correcao_cadastral` | sim | Decidido por **regra** (`sentido.py`), não pelo modelo. `avanco`: o dinheiro andou rumo ao pagamento. `recuo`: valor cancelado ou reduzido. `correcao_cadastral`: mudou só texto ou local. Não confundir com `MudancaLote.tipo` |
| `resumo` | texto, até 280 caracteres | sim; vazio quando `status = nao_resolvido` | A frase para o morador, escrita pelo modelo local |
| `confianca` | `alta` \| `media` \| `baixa` \| vazio | sim; vazio quando não resolvido | A confiança que o modelo declarou ao registrar |
| `justificativa` | texto | não | Por que o modelo escreveu a frase |
| `status` | `resolvido` \| `nao_resolvido` | sim | `nao_resolvido` quando o modelo não registrou uma frase válida dentro do teto de passos ou ficou indisponível |
| `motivo` | texto | sim; vazio quando resolvido | Por que não resolveu: `teto de passos` ou `modelo indisponível: …` |
| `passos` | inteiro ≥ 1 | sim | Chamadas ao modelo usadas no item |
| `segundos` | número | sim | Tempo do item |
| `modelo` | texto | sim | Modelo com tag, por exemplo `qwen3:1.7b` |
| `spec` | `pobre` \| `boa` | sim | Especificação usada (`referencia/<spec>.json`) |
| `max_passos` | inteiro | sim | Teto de passos da execução |

## Regra de uso

- **Não mostre** ao morador o `resumo` com `confianca = baixa` ou `status = nao_resolvido` sem revisão humana. O `carregar.py` marca esses itens com `revisar = 1`.
- O `sentido` é confiável, porque sai de regra. O `resumo` é texto de modelo e pode errar valor ou sentido: a taxa de erro medida está em `RELATORIO.md`.

## No banco (`carregar.py`)

| Tabela | Uma linha por | Origem |
| :-- | :-- | :-- |
| `LoteImportacao` | lote (data de referência), com `hash_sha256` do CSV | `coleta/bruto/lotes.json` |
| `MudancaLote` | emenda, tipo e etapa, como no Trabalho 1 | `campos.mudancas_lote` e `campos.alteracoes` |
| `ResumoMudanca` | emenda e par de lotes, chave (`lote_novo_id`, `codigo_emenda`) | `sentido`, `resumo`, `confianca`, `status`, `motivo`, `modelo`, `spec` e `revisar` |

`ResumoMudanca` é uma tabela nova, que o modelo de dados do Trabalho 1 não tem: ver a decisão C4 em `RELATORIO.md`. Emenda `removida` só entra em `ResumoMudanca`, porque o Trabalho 1 não tem um `MudancaLote.tipo` para ela.
