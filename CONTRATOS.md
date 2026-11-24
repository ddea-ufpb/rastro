# CONTRATOS · Rastro (FI-02)

> **RASCUNHO para o grupo aprovar.** Escrito por João Vitor em 24/11/2026 a partir do que
> já está na `main`: o brief (`README.md`), a especificação do Trabalho 1 de João Vitor
> (`especificacoes/joao-vitor/`, em especial a ADR-0009) e a da Sarah
> (`especificacoes/sarah-araujo/arquitetura/contratos/modelo-dados.md`). Os pontos marcados
> **[decidir]** precisam de acordo do grupo antes de este arquivo valer como contrato.

O brief pede que este arquivo traga os quatro módulos, os contratos entre os pares que
se tocam e o duplo de cada contrato. As seções 2 e 3 cobrem os módulos e os contratos.
A seção 4 fixa o vocabulário que os esquemas dos módulos e os dados do Trabalho 2
devem usar.

## 1. Regra central

O contrato principal é o **lote publicado**. A `ingestao` publica; `nucleo`, `consulta` e
`saida` leem. Nenhum deles sabe como o CSV da origem é lido. Cada tabela tem um único
módulo dono, o único que escreve nela. Dado de fonte nunca é atualizado no lugar: cada
lote grava as suas próprias linhas.

## 2. Módulos

| Módulo | Responsável | O que faz | Dono das tabelas |
| :-- | :-- | :-- | :-- |
| `ingestao` | **[decidir]** | Baixa, valida e normaliza os lotes oficiais; guarda proveniência por registro; publica o lote de forma atômica | `Fonte`, `LoteImportacao`, `RejeicaoLote`, `PublicacaoAtiva`, `Autor`, `Emenda`, `RegistroExecucao`, `Favorecido`, `RegistroFavorecido` |
| `nucleo` | **[decidir]** | Calcula a diferença entre lotes e o estado de execução consolidado de cada emenda; mantém a tradução | `MudancaLote`, `TabelaTraducao`, `ResumoMudanca` (proposta, seção 6); view `v_emenda_estado` |
| `consulta` | **[decidir]** | API e busca por município, parlamentar e função; agregações; contrato versionado | `CacheConsulta` |
| `saida` | **[decidir]** | Assinaturas por filtro e limiar; alerta com entrega única por assinante | `Assinante`, `Assinatura`, `Alerta` |

## 3. Contratos entre módulos e o duplo de cada um

O duplo é o que o módulo consumidor usa nos próprios testes no lugar do módulo produtor,
para que cada módulo rode e seja testado sozinho.

| # | Produtor → consumidor | Contrato | Duplo para testar o consumidor sozinho |
| :-- | :-- | :-- | :-- |
| C1 | `ingestao` → todos | **Lote publicado:** `PublicacaoAtiva` aponta o lote vigente; as linhas dele estão em `Emenda`, `RegistroExecucao` e `RegistroFavorecido` | Banco de teste com um lote mínimo sintético (`tests/fixtures/lote_minimo.sql`) |
| C2 | `ingestao` → `nucleo` | **Porta** `calcular_mudancas(lote_anterior_id, lote_novo_id) -> int`, chamada dentro da transação de publicação; falha desfaz a publicação | Implementação falsa que registra as chamadas e devolve uma contagem fixa |
| C3 | `ingestao` → `saida` | **Evento** `lote.publicado`, emitido depois do commit, com `fonte_id`, `lote_novo_id`, `lote_anterior_id`, `quantidade_mudancas`, `publicado_em` (`especificacoes/joao-vitor/arquitetura/contratos/eventos.asyncapi.yaml`) | Publicador em memória: uma lista de eventos que o teste preenche |
| C4 | `nucleo` → `consulta`, `saida` | View `v_emenda_estado`, `MudancaLote`, `TabelaTraducao` e `ResumoMudanca` | Banco de teste carregado com `modulos/nucleo/enriquecimento/carregar.py` a partir de um recorte do `dados.jsonl` |
| C5 | `consulta`, `saida`, `nucleo`, `ingestao` → painel e jornalistas | Operações HTTP do `openapi.yaml`, cada uma marcada com `x-modulo` | Servidor falso gerado do `openapi.yaml`; teste de contrato no lado do painel |

Um teste de arquitetura falha se `nucleo`, `consulta` ou `saida` importar o leitor de CSV
da `ingestao`.

## 4. Vocabulário comum

Nomes que todo esquema, API e arquivo de dados do grupo usa. Quando as duas
especificações do Trabalho 1 divergem, a proposta vem primeiro e o outro nome fica
como equivalente.

| Conceito | Nome no contrato | Equivalente na spec da Sarah | Observação |
| :-- | :-- | :-- | :-- |
| Lote | `LoteImportacao` (`data_referencia`, `hash_sha256`) | `versao_carga` (`fonte_etag`, `ativa`) | **[decidir]** |
| Lote vigente | `PublicacaoAtiva` | `versao_carga.ativa` | |
| Código da emenda | `codigo_emenda` (12 dígitos) | `codigo_emenda`; chave `id_emenda` cobre emenda sem código | **[decidir]** se o contrato adota `id_emenda` |
| Valores | `*_centavos`, inteiro | `valor_*`, `rp_*` em reais `numeric(15,2)` | **[decidir]** a unidade na fronteira; a proposta é centavos, que não perde precisão em JSON |
| Etapas | `empenhado`, `liquidado`, `pago`, `rap_inscrito`, `rap_cancelado`, `rap_pago` | `valor_empenhado` … `rp_pago` | |
| Estado de execução | `estado_execucao`: `sem_execucao` < `empenhada` < `liquidada` < `paga_em_parte` < `paga` | `fase_simples`: `empenhada`, `liquidada`, `paga_parcial`, `paga`, `cancelada` | **[decidir]** se entra `cancelada`. Pagamento = `pago + rap_pago`; devido = `empenhado − rap_cancelado`. As duas regras dão o mesmo estado nos 3 186 itens do corpus do Trabalho 2 que têm estado |
| Tradução para o morador | `TabelaTraducao` (`estado_execucao`, `texto_simples`, `explicacao`, versão) | `termo_traduzido` (`traducao`, `explicacao`, `fonte_titulo`, `fonte_url`) | Proposta: manter a fonte obrigatória da Sarah |
| Mudança entre lotes | `MudancaLote`: `tipo` em `nova_emenda`, `valor_alterado`, `estado_alterado`; `etapa` | não há | |
| Pagamento a favorecido | `RegistroFavorecido`, `Favorecido` | `pagamento_favorecido` (`categoria_favorecido`) | Pessoa física não é gravada pelo nome |

## 5. Dados do Trabalho 2 de cada integrante

| Integrante | Recorte | Arquivo | Campos novos | Carga |
| :-- | :-- | :-- | :-- | :-- |
| João Vitor | Mudanças de emenda entre dois lotes | `modulos/nucleo/enriquecimento/dados.jsonl` (esquema em `ESQUEMA.md`) | `sentido`, `resumo`, `confianca`, `status`, `motivo` | `carregar.py` → `LoteImportacao`, `MudancaLote`, `ResumoMudanca` |
| Sarah | Emendas da PB com fase e função | **[preencher]** | **[preencher]** | **[preencher]** |
| João Rafael | Pagamentos a favorecidos da PB | **[preencher]** | **[preencher]** | **[preencher]** |

## 6. Mudança proposta pelo que foi medido no Trabalho 2

Acrescentar ao contrato C4 a tabela **`ResumoMudanca`** (`lote_novo_id`, `codigo_emenda`,
`sentido`, `resumo`, `confianca`, `conferida`, `revisar`, `modelo`, `spec`), com a regra:
**o painel só mostra o `resumo` quando `conferida = 1` e `revisar = 0`; nos outros casos,
mostra o `texto_simples` da `TabelaTraducao`.** Motivo: no gabarito, o melhor modelo local
acertou 20% das frases (auditado) e declarou confiança alta até nos erros
(`modulos/nucleo/enriquecimento/RELATORIO.md`, seção 6, decisão C4).

## 7. Decisões em aberto

1. Responsável por cada módulo.
2. Nome e campos do lote: `LoteImportacao` ou `versao_carga`.
3. Unidade dos valores na fronteira entre módulos.
4. Se `cancelada` entra no `estado_execucao`.
5. Se o contrato adota `id_emenda` para emenda sem código.
6. Linhas da seção 5 de Sarah e João Rafael.
