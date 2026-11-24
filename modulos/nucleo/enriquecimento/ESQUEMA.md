# Esquema de `dados.jsonl`

Uma linha JSON por mudança de emenda entre dois lotes da CGU: o item do
`corpus.jsonl` da Etapa 1, sem alteração, mais os campos do enriquecimento.
Os nomes seguem o modelo de dados do Trabalho 1,
`especificacoes/joao-vitor/arquitetura/contratos/modelo-de-dados.md`, que
está na branch `trabalho1/joao-vitor` (PR #2 do ddea-ufpb/rastro) e ainda
não na `main`. O grupo ainda não tem um `CONTRATOS.md` comum. O modelo de
dados que está na `main` é o da Sarah; a equivalência de nomes está no fim
deste arquivo.

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

- O `sentido` é confiável, porque sai de regra. O `resumo` é texto de modelo e erra com frequência: na medição, 20% das frases da spec usada aqui passaram em todas as conferências (`RELATORIO.md`, seção 4).
- **Não mostre** ao morador um `resumo` sem conferência. O `carregar.py` confere cada frase com as mesmas regras do avaliador (formato, sentido, valor, jargão e etapa citada) e grava `conferida`; `revisar = 1` quando a frase não passou, quando não foi resolvida ou quando a confiança é baixa. A confiança do modelo sozinha não serve: ele declarou `alta` em quase tudo, inclusive nos erros.
- Onde `revisar = 1`, mostre o `texto_simples` da `TabelaTraducao` do Trabalho 1 para o `estado_depois`.

## No banco (`carregar.py`)

| Tabela | Uma linha por | Origem |
| :-- | :-- | :-- |
| `LoteImportacao` | lote (data de referência), com `hash_sha256` do CSV | `coleta/bruto/lotes.json` |
| `MudancaLote` | emenda, tipo e etapa, como no Trabalho 1 | `campos.mudancas_lote` e `campos.alteracoes` |
| `ResumoMudanca` | emenda e par de lotes, chave (`lote_novo_id`, `codigo_emenda`) | `sentido`, `resumo`, `confianca`, `status`, `motivo`, `modelo`, `spec`, mais `conferida` e `revisar`, calculados na carga |

`ResumoMudanca` é uma tabela nova, que o modelo de dados do Trabalho 1 não tem: ver a decisão C4 em `RELATORIO.md`. Emenda `removida` só entra em `ResumoMudanca`, porque o Trabalho 1 não tem um `MudancaLote.tipo` para ela.

## Equivalência com o modelo de dados da Sarah (`main`)

O modelo que está na `main` é
`especificacoes/sarah-araujo/arquitetura/contratos/modelo-dados.md`
(PostgreSQL, nomes em minúsculas). Esta tabela liga cada nome deste arquivo ao
equivalente de lá, para quem for juntar os dois.

### Entidades

| Aqui (Trabalho 1 do João Vitor) | Na `main` (Sarah) | Diferença |
| :-- | :-- | :-- |
| `LoteImportacao` | `versao_carga` | Lá, uma versão por carga, com `fonte_etag` e `ativa`. Aqui, um lote por data de referência, com `hash_sha256` do CSV |
| `Fonte` | `versao_carga.fonte_url` | Lá não há tabela de fonte |
| `MudancaLote` | não há | Lá não se grava a diferença entre versões. Dá para calcular comparando a `emenda` de duas versões |
| `ResumoMudanca` | não há | Tabela nova desta etapa (decisão C4 do `RELATORIO.md`) |
| `TabelaTraducao.texto_simples` | `termo_traduzido.traducao` | O texto a mostrar quando `revisar = 1`. Lá, a linha é achada por `termo_traduzido.fase = fase_simples` |
| `campos.emenda` | uma linha de `emenda` | Lá só entram emendas da PB (`Código UF IBGE = 2500000`). Este corpus tem emendas de todo o país |

### Campos da emenda (`campos.emenda` aqui, `emenda` lá)

| Aqui | Na `main` | Diferença |
| :-- | :-- | :-- |
| `codigo` (e `campos.codigo_emenda`) | `codigo_emenda` | Lá a chave é `id_emenda`, que cobre emenda sem código e código repetido |
| `ano` | `ano` | |
| `tipo` | `tipo_emenda` | |
| `numero` | `numero_emenda` | |
| `autor_codigo` · `autor_nome` | `autor_id` · `autor.nome` | Lá o autor é uma tabela à parte |
| `localidade_gasto` | `localidade_gasto` | |
| `municipio_ibge` | `municipio_codigo_ibge` | |
| `funcao_nome` · `subfuncao_nome` · `programa_nome` | `funcao` · `subfuncao` · `programa` | Aqui também ficam os códigos (`*_codigo`) |
| `acao_codigo` · `acao_nome` | `codigo_acao` · `acao_orcamentaria` | |
| `plano_orcamentario_codigo` · `plano_orcamentario_nome` | `plano_orcamentario` | |
| `empenhado_centavos` | `valor_empenhado` | **Unidade:** aqui, centavos em inteiro; lá, reais em `numeric(15,2)`. Divida por 100 |
| `liquidado_centavos` | `valor_liquidado` | idem |
| `pago_centavos` | `valor_pago` | idem |
| `rap_inscrito_centavos` | `rp_inscrito` | idem |
| `rap_cancelado_centavos` | `rp_cancelado` | idem |
| `rap_pago_centavos` | `rp_pago` | idem |
| `uf_ibge` · `uf_gasto` · `regiao` · `possui_apoiador` | não há | Lá a UF vira `abrangencia` (`municipal`, `estadual`, `multiplo`) |

### Estado da execução (`campos.estado_depois` aqui, `fase_simples` lá)

As duas regras usam o mesmo pagamento (`pago + rap_pago`) e o mesmo devido
(`empenhado − rap_cancelado`). Os nomes que mudam:

| Aqui (`estado_execucao`) | Na `main` (`fase_simples`, view `emenda_ativa`) |
| :-- | :-- |
| `paga_em_parte` | `paga_parcial` |
| `paga` | `paga` |
| `liquidada` | `liquidada` |
| `empenhada` | `empenhada` |
| `sem_execucao` | `empenhada`, ou `cancelada` quando o devido é zero |
| não há | `cancelada`: lá vem antes de tudo, quando o devido é zero ou negativo |

As regras só divergem quando o devido é zero ou negativo. No `dados.jsonl`
isso não acontece: recalculei a `fase_simples` dos 3 186 itens que têm
`estado_depois`, e todos deram o estado equivalente da tabela acima.
