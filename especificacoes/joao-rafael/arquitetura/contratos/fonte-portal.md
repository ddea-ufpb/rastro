# Contrato da fonte externa — Portal da Transparência (CGU)

Formato observado no arquivo real em 22/11/2026, na coleta do Trabalho 2 (`modulos/ingestao/coleta-favorecidos/FONTE.md`). A importação valida o zip contra este contrato e falha com `formato_alterado` se ele não bater (REQ-07).

## Acesso

| Item | Valor |
| :-- | :-- |
| URL | `https://portaldatransparencia.gov.br/download-de-dados/emendas-parlamentares/UNICO`, que redireciona para `https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/emendas-parlamentares/EmendasParlamentares.zip` |
| Autenticação | nenhuma |
| Tamanho | ~47 MB |
| Atualização | diária (`Last-Modified` de 19/11/2026 22:36 GMT na coleta) |
| Pedido condicional | `If-None-Match: <ETag>` → `304` sem corpo (REQ-02, REQ-03) |
| Licença | Dados abertos (Lei 12.527/2011), com citação da fonte |

## Arquivos usados

O zip tem 6 CSVs. O MVP usa dois; os outros quatro são ignorados, e a ausência deles não é erro.

| Arquivo | Uso | Codificação |
| :-- | :-- | :-- |
| `EmendasParlamentares.csv` | `Emenda`, `Autor` | Windows-1252, separador `;`, aspas `"` |
| `EmendasParlamentares_PorFavorecido.csv` | `Pagamento`, `Favorecido`, `Descarte` | Windows-1252, separador `;`, aspas `"`, 13 colunas |

## Colunas exigidas

`EmendasParlamentares.csv`: `Código da Emenda`, `Ano da Emenda`, `Tipo de Emenda`, `Código do Autor da Emenda`, `Nome do Autor da Emenda`, `Localidade de aplicação do recurso`, `Código Município IBGE`, `Código UF IBGE`, `Código Função`, `Nome Função`, `Valor Empenhado`, `Valor Liquidado`, `Valor Pago`, `Valor Restos A Pagar Inscritos`, `Valor Restos A Pagar Cancelados`, `Valor Restos A Pagar Pagos`.

`EmendasParlamentares_PorFavorecido.csv`: `Código da Emenda`, `Código do Autor da Emenda`, `Nome do Autor da Emenda`, `Número da emenda`, `Tipo de Emenda`, `Ano/Mês`, `Código do Favorecido`, `Favorecido`, `Natureza Jurídica`, `Tipo Favorecido`, `UF Favorecido`, `Município Favorecido`, `Valor Recebido`.

## Formatos e o que a importação faz

| Campo | Formato observado | Regra |
| :-- | :-- | :-- |
| Valores | `^-?\d+,\d{2}$`, sem separador de milhar | centavos inteiros (REQ-24); negativo é estorno (REQ-23) |
| `Ano/Mês` | `AAAAMM` | mantido (T2 R-ANOMES) |
| `Código do Favorecido` | 14 dígitos (PJ), CPF mascarado (PF), 6 dígitos (UG), `-8`/`-3`/`9000…` (sem informação) | ver `Tipo Favorecido` |
| `Tipo Favorecido` | `Pessoa Jurídica`, `Pessoa Fisica`, `Unidade Gestora`, `Sem informação`, `Inválido`, `Inscrição Genéric` | só `Pessoa Jurídica` entra (REQ-16–20) |
| `Natureza Jurídica` | texto; `Empresário (Individual)` é pessoa | descarte (REQ-17) |
| `Sem informação`, `S/I` | em código da emenda, natureza e município | nulo (REQ-25) |
| `UF Favorecido` | sigla; `-1` em 65 linhas | nulo (REQ-25) |
| `Código da Emenda` | 12 dígitos ou `Sem informação` | outro formato → `codigo_emenda_invalido` |
| `Município Favorecido` | nome em caixa alta, sem código IBGE | `Favorecido.municipio_ibge` = código do `Municipio` com o mesmo nome sem acento e `UF Favorecido = PB`; sem par → nulo |

## Recorte

Linha entra se a emenda tem `Código UF IBGE = 2500000` em `EmendasParlamentares.csv` **ou** se o favorecido tem `UF Favorecido = PB` (REQ-04). Na coleta: 836 298 linhas no arquivo de favorecidos, 31 840 no recorte, 19 647 pagamentos a pessoa jurídica, 2 353 CNPJs.

## Descartes medidos no T2 (linhas de pagamento)

| Motivo | Linhas |
| :-- | --: |
| `favorecido_pessoa_fisica` | 11 497 |
| `favorecido_empresario_individual` | 504 |
| `favorecido_nao_identificado` | 180 |
| `unidade_gestora_sem_cnpj` | 11 |
| `favorecido_tipo_desconhecido` | 1 |
| `cnpj_invalido`, `valor_fora_do_formato`, `numero_de_colunas_inesperado` | 0 |

Esses números são o caso de teste de referência de QA-01 e o baseline do limite do REQ-08.
