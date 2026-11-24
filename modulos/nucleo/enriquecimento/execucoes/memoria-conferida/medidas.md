# Medidas das execuções

Gerado por `medir.py`. Gabarito: 40 itens rotulados à mão (commit 93cf3d9).

| Medida | exec1-pobre-traduzida | exec2-boa-traduzida | exec1-pobre-original | frases humanas |
| :-- | --: | --: | --: | --: |
| Formato válido | 100.0% | 95.0% | 100.0% | 100.0% |
| Acurácia (passa nos 4 critérios) | 92.5% | 87.5% | 80.0% | 100.0% |
| Acurácia auditada (pós-hoc: etapa citada mudou) | 92.5% | 37.5% | 70.0% | 100.0% |
| Tempo total | 192 s | 158 s | 155 s | 0 s |
| Passos por item | 3.02 | 3.38 | 2.95 | 0.00 |
| Não resolvidos | 0 | 2 | 0 | 0 |
| Critério: formato | 100.0% | 95.0% | 100.0% | 100.0% |
| Critério: sentido | 97.5% | 95.0% | 100.0% | 100.0% |
| Critério: valor | 95.0% | 87.5% | 87.5% | 100.0% |
| Critério: sem_jargao | 100.0% | 95.0% | 92.5% | 100.0% |

## Matriz de confusão: exec1-pobre-traduzida

Linha: sentido do gabarito. Coluna: sentido que a frase comunica.

| gabarito \ frase | avanco | recuo | nova |
| :-- | --: | --: | --: |
| avanco | 37 | 0 | 0 |
| recuo | 1 | 1 | 0 |
| nova | 0 | 0 | 1 |

Erros (3):

- `rastro-mud-20261119-202671080007` falhou em valor: A emenda aumentou o valor reservado e pago em relação à anterior.
- `rastro-mud-20261119-202539940016` falhou em sentido: O valor da emenda foi recuado em R$ 8.872,58 entre os anos seguintes.
- `rastro-mud-20261119-202641300018` falhou em valor: Nova emenda com valor reservado e pago em valores zero, indicando que o valor foi deixado para pagamento em anos subsequentes.

## Matriz de confusão: exec2-boa-traduzida

Linha: sentido do gabarito. Coluna: sentido que a frase comunica.

| gabarito \ frase | avanco | recuo | nova | nao_resolvido |
| :-- | --: | --: | --: | --: |
| avanco | 35 | 0 | 0 | 2 |
| recuo | 0 | 2 | 0 | 0 |
| nova | 0 | 0 | 1 | 0 |

Erros (5):

- `rastro-mud-20261119-202643200021` falhou em valor: A emenda foi realizada com avanco, aumentando o valor reservado e pago.
- `rastro-mud-20261119-202644130007` falhou em valor: A emenda foi ajustada para aumentar o valor reservado e pago no período especificado.
- `rastro-mud-20261119-202641550011` falhou em valor: A emenda foi ajustada para aumentar o valor reservado e o valor pago.
- `rastro-mud-20261119-202644090002` falhou em formato, sentido, valor, sem_jargao: (teto de passos)
- `rastro-mud-20261119-202644210004` falhou em formato, sentido, valor, sem_jargao: (teto de passos)

## Matriz de confusão: exec1-pobre-original

Linha: sentido do gabarito. Coluna: sentido que a frase comunica.

| gabarito \ frase | avanco | recuo | nova |
| :-- | --: | --: | --: |
| avanco | 37 | 0 | 0 |
| recuo | 0 | 2 | 0 |
| nova | 0 | 0 | 1 |

Erros (8):

- `rastro-mud-20261119-202643200021` falhou em valor: Valor empregado e pago foram aumentados em R$ X e R$ X, respectivamente.
- `rastro-mud-20261119-202622100014` falhou em sem_jargao: Valor liquidado foi aumentado em R$ 355.230,00.
- `rastro-mud-20261119-202642720012` falhou em valor: Valor empregado e pago foram aumentados em R$ X e R$ X, respectivamente.
- `rastro-mud-20261119-202571260005` falhou em valor: Valor empregado e pago foram aumentados em R$ X e R$ X, respectivamente.
- `rastro-mud-20261119-202539940016` falhou em sem_jargao: Valor dos restos a pagar foi reduzido em R$ 8.872,58.
- `rastro-mud-20261119-202541800017` falhou em sem_jargao: O valor dos restos a pagar foi reduzido em R$ 1.312,00 e o valor dos restos cancelados foi aumentado em R$ 1.312,00.
- `rastro-mud-20261119-202540770017` falhou em valor: Valor empregado e pago foram aumentados em R$ X e R$ X, respectivamente.
- `rastro-mud-20261119-202641300018` falhou em valor: A emenda foi registrada com confiança alta, pois é uma mudança de nova introdução no lote de 2026.

## Erros nas duas execuções (0)

