# Medidas das execuções

Gerado por `medir.py`. Gabarito: 40 itens rotulados à mão (commit 93cf3d9).

| Medida | exec1-pobre | exec2-boa | frases humanas |
| :-- | --: | --: | --: |
| Formato válido | 100.0% | 95.0% | 100.0% |
| Acurácia (passa nos 4 critérios) | 30.0% | 5.0% | 100.0% |
| Tempo total | 312 s | 459 s | 0 s |
| Passos por item | 3.10 | 2.88 | 0.00 |
| Não resolvidos | 0 | 2 | 0 |
| Critério: formato | 100.0% | 95.0% | 100.0% |
| Critério: sentido | 100.0% | 95.0% | 100.0% |
| Critério: valor | 90.0% | 72.5% | 100.0% |
| Critério: sem_jargao | 37.5% | 5.0% | 100.0% |

## Matriz de confusão: exec1-pobre

Linha: sentido do gabarito. Coluna: sentido que a frase comunica.

| gabarito \ frase | avanco | recuo | nova |
| :-- | --: | --: | --: |
| avanco | 37 | 0 | 0 |
| recuo | 0 | 2 | 0 |
| nova | 0 | 0 | 1 |

Erros (28):

- `rastro-mud-20261119-202643200021` falhou em valor: Valor empregado e pago foram aumentados em R$ X e R$ X, respectivamente.
- `rastro-mud-20261119-202622100014` falhou em sem_jargao: Valor liquidado foi aumentado em R$ 355.230,00.
- `rastro-mud-20261119-202544490008` falhou em sem_jargao: Valor liquidado foi aumentado em R$ 95.636,35.
- `rastro-mud-20261119-202642720012` falhou em sem_jargao: Valor liquidado foi aumentado em R$ 149.700,00.
- `rastro-mud-20261119-202645510004` falhou em sem_jargao: Valor liquidado foi aumentado em R$ 270.998,00.
- `rastro-mud-20261119-202624460008` falhou em sem_jargao: Valor liquidado foi aumentado em R$ 600.000,00.
- `rastro-mud-20261119-202529250005` falhou em valor, sem_jargao: Valor liquidado foi aumentado em R$ X.
- `rastro-mud-20261119-202644130003` falhou em sem_jargao: Valor liquidado foi aumentado em R$ 2.093.894,19.
- `rastro-mud-20261119-202543220011` falhou em sem_jargao: Valor liquidado foi aumentado em R$ 65.949,61.
- `rastro-mud-20261119-202630670009` falhou em sem_jargao: A valor liquidado foi aumentado em R$ 597.000,00.
- `rastro-mud-20261119-202644980003` falhou em sem_jargao: Valor liquidado foi aumentado em R$ 1.999.984,00.
- `rastro-mud-20261119-202571260005` falhou em sem_jargao: Valor liquidado foi aumentado em R$ 13.843,20.
- `rastro-mud-20261119-202644340021` falhou em sem_jargao: Valor liquidado foi aumentado em R$ 4.500,00.
- `rastro-mud-20261119-202540890003` falhou em valor: Valor empregado e pago foram aumentados em R$ X e R$ X, respectivamente.
- `rastro-mud-20261119-202637770005` falhou em sem_jargao: Valor liquidado foi aumentado em R$ 292.548,00.
- `rastro-mud-20261119-202641190004` falhou em sem_jargao: Valor liquidado foi aumentado em R$ 1.119.888,00.
- `rastro-mud-20261119-202644210004` falhou em sem_jargao: Valor liquidado foi aumentado em R$ 245.000,00.
- `rastro-mud-20261119-202637280001` falhou em sem_jargao: A valor liquidado foi aumentado em R$ 1.460.856,41.
- `rastro-mud-20261119-202539940016` falhou em sem_jargao: Valor dos restos a pagar foi reduzido em R$ 8.872,58.
- `rastro-mud-20261119-202541800017` falhou em sem_jargao: Valor dos restos a pagar foi reduzido em R$ 1.312,00.
- `rastro-mud-20261119-202671150001` falhou em sem_jargao: Valor liquidado foi aumentado em R$ 499.999,00.
- `rastro-mud-20261119-202630680003` falhou em sem_jargao: Valor liquidado foi aumentado em R$ 199.991,00.
- `rastro-mud-20261119-202641300018` falhou em valor: A emenda foi registrada com confiança alta, pois é uma mudança de nova introdução no lote de 2026.
- `rastro-mud-20261119-202671120007` falhou em sem_jargao: Valor liquidado foi aumentado em R$ 450.000,00.
- `rastro-mud-20261119-202643060003` falhou em sem_jargao: A valor liquidado foi aumentado em R$ 1.947.808,54.
- `rastro-mud-20261119-202628330007` falhou em sem_jargao: A valor liquidado foi aumentado em R$ 2.751.279,57.
- `rastro-mud-20261119-202625280002` falhou em sem_jargao: Valor liquidado foi aumentado em R$ 184.157,00.
- `rastro-mud-20261119-202644940003` falhou em sem_jargao: O valor liquidado foi aumentado em R$ 6.038.206,49.

## Matriz de confusão: exec2-boa

Linha: sentido do gabarito. Coluna: sentido que a frase comunica.

| gabarito \ frase | avanco | recuo | nova | nao_resolvido |
| :-- | --: | --: | --: | --: |
| avanco | 35 | 0 | 0 | 2 |
| recuo | 0 | 2 | 0 | 0 |
| nova | 0 | 0 | 1 | 0 |

Erros (38):

- `rastro-mud-20261119-202671080007` falhou em sem_jargao: Valor empenhado e pago foram aumentados em R$ 405.881,85 e R$ 39.247,58, respectivamente.
- `rastro-mud-20261119-202643200021` falhou em sem_jargao: Valor empenhado e pago foram aumentados em R$ 1.250.000,00 e R$ 14.540,00, respectivamente.
- `rastro-mud-20261119-202644130007` falhou em sem_jargao: Valor empenhado e pago foram aumentados em R$ 5.922,95.
- `rastro-mud-20261119-202641550011` falhou em valor, sem_jargao: A emenda foi registrada com confiança, pois a mudança foi de avanço no valor empenhado e pago.
- `rastro-mud-20261119-202619860018` falhou em valor, sem_jargao: A emenda foi registrada com confiança, pois a mudança foi de avanço no valor empenhado e pago.
- `rastro-mud-20261119-202622100014` falhou em valor, sem_jargao: A emenda foi registrada com confiança, pois a mudança foi de avanço no valor empenhado e pago.
- `rastro-mud-20261119-202544490008` falhou em sem_jargao: A emenda alterou o valor dos restos a pagar, passando de R$ 2.412.034,51 para R$ 2.316.398,16, com um avanço de R$ 95.636,35.
- `rastro-mud-20261119-202642720012` falhou em valor, sem_jargao: A emenda foi registrada com confiança, pois a mudança foi de avanço no valor empenhado e pago.
- `rastro-mud-20261119-202639420007` falhou em sem_jargao: Valor empenhado e pago foram aumentados em R$ 62.820,70 e R$ 62.820,70, respectivamente.
- `rastro-mud-20261119-202639640009` falhou em formato, sentido, valor, sem_jargao: (teto de passos)
- `rastro-mud-20261119-202645510004` falhou em sem_jargao: A emenda alterou o valor dos restos a pagar, passando de R$ 1.351.375,00 para R$ 1.622.373,00, com um avanço de R$ 270.998,00.
- `rastro-mud-20261119-202624460008` falhou em sem_jargao: A emenda alterou o valor dos restos a pagar, passando de R$ 6.540.803,00 para R$ 7.140.803,00, com um avanço de R$ 600.000,00.
- `rastro-mud-20261119-202529250005` falhou em valor, sem_jargao: A emenda alterou o valor dos restos a pagar, passando de R$ 8.000,00 para R$ 0,00, com um avanço de R$ 8.000,00.
- `rastro-mud-20261119-202644130003` falhou em sem_jargao: A emenda alterou o valor dos restos a pagar, passando de R$ 4.174.605,81 para R$ 6.268.500,00, com um avanço de R$ 2.093.894,19.
- `rastro-mud-20261119-202543220011` falhou em sem_jargao: A emenda alterou o valor dos restos a pagar, passando de R$ 211.232,82 para R$ 145.283,21 com um avanço de R$ 65.949,61.
- `rastro-mud-20261119-202571070008` falhou em sem_jargao: Valor Restos A Pagar Inscritos passou de R$ 641.600,00 para R$ 581.903,50 (-R$ 59.696,50); Valor Restos A Pagar Pagos passou de R$ 6.502.418,32 para R$ 6.562.114,82 (+R$ 59.696,50)
- `rastro-mud-20261119-202640640002` falhou em sem_jargao: Valor empenhado foi aumentado em R$ 500.000,00.
- `rastro-mud-20261119-202644090002` falhou em sem_jargao: Valor empenhado foi aumentado em R$ 500.000,00.
- `rastro-mud-20261119-202630670009` falhou em valor, sem_jargao: A emenda alterou o valor dos restos a pagar, passando de R$ 0,00 para R$ 597.000,00, com um avanço de R$ 597.000,00.
- `rastro-mud-20261119-202644980003` falhou em formato, sentido, valor, sem_jargao: (teto de passos)
- `rastro-mud-20261119-202571260005` falhou em valor, sem_jargao: A emenda foi registrada com confiança, pois a mudança foi de avanço no valor empenhado e pago.
- `rastro-mud-20261119-202644340021` falhou em sem_jargao: A emenda alterou o valor dos restos a pagar, passando de R$ 699.850,00 para R$ 704.350,00, com um avanço de R$ 4.500,00.
- `rastro-mud-20261119-202540890003` falhou em valor, sem_jargao: Valor Restos A Pagar Inscritos e Valor Restos A Pagar Pagos foram ajustados em valores negativos e positivos respectivamente.
- `rastro-mud-20261119-202631600001` falhou em sem_jargao: A emenda alterou o valor dos restos a pagar, passando de R$ 400.000,00 para R$ 507.881,46, com um avanço de R$ 107.881,46.
- `rastro-mud-20261119-202637770005` falhou em sem_jargao: A emenda alterou o valor dos restos a pagar, passando de R$ 1.199.764,00 para R$ 1.492.312,00, com um avanço de R$ 292.548,00.
- `rastro-mud-20261119-202641190004` falhou em sem_jargao: A emenda alterou o valor dos restos a pagar, passando de R$ 2.897.192,00 para R$ 4.017.080,00, com um avanço de R$ 1.119.888,00.
- `rastro-mud-20261119-202644210004` falhou em sem_jargao: A emenda alterou o valor dos restos a pagar, passando de R$ 247.464,00 para R$ 492.464,00, com um avanço de R$ 245.000,00.
- `rastro-mud-20261119-202637280001` falhou em sem_jargao: A emenda alterou o valor dos restos a pagar, passando de R$ 8.489.143,59 para R$ 9.950.000,00, com um avanço de R$ 1.460.856,41.
- `rastro-mud-20261119-202539940016` falhou em sem_jargao: Valor Restos A Pagar foi reduzido de R$ 165.527,31 para R$ 156.654,73
- `rastro-mud-20261119-202541800017` falhou em sem_jargao: Valor Restos A Pagar foi reduzido de R$ 901.312,00 para R$ 900.000,00 (-R$ 1.312,00); Valor Restos A Pagar Cancelados foi aumentado de R$ 200.000,00 para R$ 201.312,00 (+R$ 1.312,00).
- `rastro-mud-20261119-202671150001` falhou em sem_jargao: A emenda alterou o valor dos restos a pagar, passando de R$ 81.978.427,00 para R$ 82.478.426,00, com um avanço de R$ 499.999,00.
- `rastro-mud-20261119-202630680003` falhou em valor, sem_jargao: A emenda alterou o valor dos restos a pagar, passando de R$ 0,00 para R$ 199.991,00, com um avanço de R$ 199.991,00.
- `rastro-mud-20261119-202540770017` falhou em sem_jargao: Valor Restos A Pagar Inscritos passou de R$ 100.032,03 para R$ 13.037,43; Valor Restos A Pagar Pagos passou de R$ 391.693,38 para R$ 478.687,98
- `rastro-mud-20261119-202671120007` falhou em sem_jargao: A emenda alterou o valor dos restos a pagar, passando de R$ 109.819.294,00 para R$ 110.269.294,00, com um avanço de R$ 450.000,00.
- `rastro-mud-20261119-202643060003` falhou em sem_jargao: A emenda alterou o valor dos restos a pagar, passando de R$ 9.992.191,46 para R$ 11.940.000,00, com um avanço de R$ 1.947.808,54.
- `rastro-mud-20261119-202628330007` falhou em sem_jargao: A emenda alterou o valor dos restos a pagar, passando de R$ 13.914.970,43 para R$ 16.666.250,00, com um avanço de R$ 2.751.279,57.
- `rastro-mud-20261119-202625280002` falhou em sem_jargao: A emenda alterou o valor dos restos a pagar, passando de R$ 13.067.850,00 para R$ 13.252.007,00 (+R$ 184.157,00).
- `rastro-mud-20261119-202644940003` falhou em sem_jargao: A emenda alterou o valor dos restos a pagar, passando de R$ 13.861.793,51 para R$ 19.900.000,00, com um avanço de R$ 6.038.206,49.

## Erros nas duas execuções (27)

- `rastro-mud-20261119-202529250005`
- `rastro-mud-20261119-202539940016`
- `rastro-mud-20261119-202540890003`
- `rastro-mud-20261119-202541800017`
- `rastro-mud-20261119-202543220011`
- `rastro-mud-20261119-202544490008`
- `rastro-mud-20261119-202571260005`
- `rastro-mud-20261119-202622100014`
- `rastro-mud-20261119-202624460008`
- `rastro-mud-20261119-202625280002`
- `rastro-mud-20261119-202628330007`
- `rastro-mud-20261119-202630670009`
- `rastro-mud-20261119-202630680003`
- `rastro-mud-20261119-202637280001`
- `rastro-mud-20261119-202637770005`
- `rastro-mud-20261119-202641190004`
- `rastro-mud-20261119-202642720012`
- `rastro-mud-20261119-202643060003`
- `rastro-mud-20261119-202643200021`
- `rastro-mud-20261119-202644130003`
- `rastro-mud-20261119-202644210004`
- `rastro-mud-20261119-202644340021`
- `rastro-mud-20261119-202644940003`
- `rastro-mud-20261119-202644980003`
- `rastro-mud-20261119-202645510004`
- `rastro-mud-20261119-202671120007`
- `rastro-mud-20261119-202671150001`
