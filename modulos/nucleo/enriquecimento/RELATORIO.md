# Trabalho 2, Etapa 2: relatório (João Vitor, Rastro)

Recorte: dois lotes da CGU (26/10 e 19/11/2026); o modelo descreve em uma
frase, para o morador, o que mudou em cada emenda entre os lotes. O sentido
da mudança é classificado por regra (seção 1).

Tudo o que este relatório afirma está nos arquivos desta pasta e no histórico
do git da branch `trabalho2/etapa2-joao-vitor`.

## 0. Ambiente

| Item | Valor |
| :-- | :-- |
| Máquina | Apple M4 (CPU de 10 núcleos, GPU integrada de 10 núcleos, sem GPU dedicada), 16 GB de RAM, macOS 27.0.1 |
| Servidor de modelo | Ollama 0.33.3, local |
| Modelo | `qwen3:1.7b` (tag fixa; `cliente.py` recusa `:latest` e nome sem tag) |
| Parâmetros | `temperature: 0`, `seed: 42`, `think: false` (modo de raciocínio do qwen3 desligado), teto de 6 passos por item |
| Linguagem | Python 3.14, só biblioteca padrão; nenhum framework de agente |

Mesmo com `temperature: 0` e semente fixa, a saída pode variar entre rodadas
(ordem de operações de ponto flutuante no Metal, versão do Ollama). Por isso
cada execução está gravada linha a linha em `execucoes/`.

## 1. Onde o LLM entra e onde não entra (B1)

| Trabalho | Quem faz | Por quê |
| :-- | :-- | :-- |
| Ler o CSV, converter valor e data, parear os lotes, calcular as diferenças | parser (Etapa 1, `coleta/coletor.py`) | regra exata |
| Classificar o sentido da mudança (`avanco`, `recuo`, `nova`, `removida`) | **regra** (`sentido.py`) | ver abaixo |
| Escrever a frase para o morador | modelo local | não há regra que escreva linguagem de morador |
| Conferir a frase (formato, sentido, valor, jargão) | regra (`avaliar.py`) | o avaliador não pode ser outro modelo |

O tutorial pedia que o modelo também classificasse o tipo de mudança. Antes de
escrever o enriquecedor, testei uma regra de seis linhas contra o gabarito
rotulado à mão. Ela acerta **40 de 40** (`tests/test_sentido.py`):

- presença `nova` ou `removida` → a própria presença;
- `rap_cancelado` subiu → `recuo`;
- empenhado, liquidado, pago ou `rap_pago` subiu → `avanco`;
- algum valor caiu → `recuo`; senão → `correcao_cadastral`.

Como "se existe uma regra que acerta 100% das vezes, escreva a regra", o tipo
foi para a regra. O modelo recebe o sentido pronto e só escreve a frase.

Limite da regra: no corpus inteiro ela dá 2 920 `avanco`, 206 `nova`, 60
`recuo` e 5 `removida`. Há 47 itens `avanco` em que alguma etapa também caiu
(por exemplo, empenhado menor e liquidado maior). A regra chama de `avanco`,
mas o gabarito, com 37 `avanco` em 40, não tem nenhum caso assim: essa
fronteira não foi validada.

## 2. Contrato de ferramentas (B2)

Três ferramentas, todas com parâmetros tipados e `required` (`agente.py`):

| Ferramenta | Parâmetros | O que faz |
| :-- | :-- | :-- |
| `consultar_glossario` | `termo` (obrigatório) | Lê a referência de `referencia/<spec>.json`: definição do termo e, na spec boa, como dizê-lo ao morador e as regras de redação (`termo='regras'`) |
| `buscar_semelhante` | `sentido` (obrigatório, enum), `funcao` | Até duas frases já registradas nesta execução, do mesmo sentido e área, com os valores trocados por `R$ X` |
| `registrar` | `resumo` e `confianca` (obrigatórios; `confianca` em `alta`, `media`, `baixa`), `justificativa` | Entrega a frase e encerra o item |

A referência entra por ferramenta e é lida de arquivo, para poder ser
versionada e comparada. O prompt de sistema é o mesmo nas duas
especificações: muda só a referência e as `description`.

| | Spec pobre (`referencia/pobre.json`) | Spec boa (`referencia/boa.json`) |
| :-- | :-- | :-- |
| Glossário | definições técnicas | definição + "ao morador: …" |
| Regras | nenhuma | 8 regras de redação e desempate (pago antes de reservado; restos a pagar inscritos caindo e pagos subindo é um dinheiro só; arredondamento; termos proibidos; local múltiplo; tamanho; confiança) |
| `description` | o que a ferramenta faz | o que faz e QUANDO usar (antes de escrever, depois do glossário, uma vez por último) |

## 3. Laço, parada e robustez (B3)

`enriquecer_item` em `agente.py`, escrito à mão:

- teto de passos configurável (`--max-passos`, padrão 6; `max_passos < 1` é recusado);
- resposta sem `tool_calls` recebe um aviso ("chame registrar") e conta um passo;
- lista branca: só as três ferramentas; nome desconhecido devolve erro ao modelo, que continua;
- argumentos normalizados: aceitam dict ou string JSON, caixa e acento diferentes (`"Confiança": "Média"` → `confianca: media`) e a chave fundida `"resumo confianca"`, que o qwen3:1.7b mandou no primeiro teste. Lista ou objeto no lugar de texto é recusado. O erro devolvido diz as chaves recebidas e as aceitas;
- `registrar` com frase acima de 280 caracteres, `confianca` fora do enum ou campo obrigatório ausente devolve erro e não encerra o item;
- item que estoura o teto entra na saída com `status: nao_resolvido`, `resumo` vazio e `motivo: teto de passos`;
- nada do que o modelo manda vai para shell ou `eval`.

O servidor do modelo é tratado como serviço externo (`cliente.py`): até 3
tentativas com backoff exponencial e jitter, HTTP 4xx sem repetição, e
circuit breaker que abre após 5 falhas seguidas e espera 30 s. Falha do
servidor vira `nao_resolvido` com `motivo: modelo indisponível: …`, e a
retomada (`enriquecedor.py`) refaz só esses itens, descarta uma última linha
truncada e recusa misturar execuções de spec, modelo ou teto diferentes.

Testes: `python3 -m unittest discover -s tests -t .` (64 testes, com cliente
falso; nenhum chama o modelo real).

## 4. Gabarito e medição (B4)

### Gabarito

- 40 itens sorteados por `gabarito.py sortear` (semente 20261123, `random.Random(semente).sample` do corpus ordenado por id), commit `b778989`.
- Rotulados à mão por mim na folha `rotular.md` (tipo e frase) e importados com `gabarito.py importar`, commit `93cf3d9`, às 10:48 de 23/11/2026.
- O primeiro código do enriquecedor é do commit `64707e3` (11:02), e a primeira execução veio depois. O enriquecedor lê do gabarito só os ids (`enriquecedor.carregar_entrada`); o rótulo nunca chega ao modelo.
- `gabarito.py conferir` refaz o sorteio pela semente e confere o SHA-256 do corpus, então dá para provar que os itens foram sorteados e não escolhidos.

### Como a frase é medida

A frase é texto livre, então a acurácia é medida por quatro critérios
conferíveis sem outro modelo (`avaliar.py`). A frase está **correta** quando
passa nos quatro:

| Critério | Passa quando |
| :-- | :-- |
| formato | frase não vazia, uma frase só, até 280 caracteres, `confianca` válida |
| sentido | o sentido que a frase comunica (léxico: cancelou, reduziu → recuo; emenda nova → nova; …) é o do gabarito |
| valor | cita ao menos um valor, e todo valor citado fica a até 10% de uma diferença, de um valor antes ou de um valor depois do item |
| sem jargão | não usa empenho, liquidação nem restos a pagar |

O avaliador foi validado antes de medir o modelo: as 40 frases humanas passam
nos quatro critérios (coluna "frases humanas" das tabelas), e os testes
reprovam valor inventado, sentido trocado, jargão e formato inválido.

Depois da rodada 2 acrescentei uma **auditoria pós-hoc**: a frase não pode
atribuir mudança a uma etapa que não mudou (reservado, aprovado/liberado).
Ela não reprova nenhuma das 40 frases humanas e aparece como linha separada,
"acurácia auditada". A acurácia oficial continua sendo a dos quatro critérios
definidos antes das execuções.

### Duas rodadas

Cada rodada tem as duas execuções pedidas: especificação pobre e boa, os
mesmos 40 itens, o mesmo modelo.

- **Rodada 1** (código `64707e3`, resultados em `execucoes/rodada1/`, commit `2f32f5e`).
- **Rodada 2** (código `3ef584d`, resultados em `execucoes/rodada2/`, commit `abd5498`). Entre as duas, mudei duas coisas, pelos motivos abaixo, e declaro as duas:
  1. `buscar_semelhante` passou a trocar os valores por `R$ X`. Na rodada 1, o modelo copiava a frase do item anterior com os valores dele: 17 das 40 frases da pobre e 14 da boa eram repetição exata de uma frase anterior.
  2. Na `boa.json`, os exemplos de arredondamento ("R$ 405 mil", "R$ 1,2 milhão") eram valores dos itens 1 e 2 do gabarito, que eu tinha visto ao escrever a referência. Troquei por valores arbitrários ("R$ 73 mil", "R$ 4,9 milhões"). As regras de redação continuam sendo minhas e foram escritas depois de ver os textos de alguns itens do gabarito (não os rótulos): isso é um viés a favor da spec boa, e mesmo assim ela perdeu.

| Medida | R1 pobre | R1 boa | **R2 pobre** | **R2 boa** | frases humanas |
| :-- | --: | --: | --: | --: | --: |
| Formato válido | 100,0% | 95,0% | 100,0% | 95,0% | 100% |
| **Acurácia** (4 critérios) | 17,5% | 12,5% | **30,0%** | **5,0%** | 100% |
| Acurácia auditada (pós-hoc) | 12,5% | 12,5% | **20,0%** | **5,0%** | 100% |
| Tempo total | 222 s | 296 s | 312 s | 459 s | — |
| Passos por item | 3,08 | 3,15 | 3,10 | 2,88 | — |
| Não resolvidos | 0 | 2 | 0 | 2 | — |
| Critério sentido | 100% | 95,0% | 100% | 95,0% | 100% |
| Critério valor | 45,0% | 47,5% | 90,0% | 72,5% | 100% |
| Critério sem jargão | 40,0% | 17,5% | 37,5% | 5,0% | 100% |
| Frases repetidas de item anterior | 17 | 14 | 2 | 5 | 0 |

Detalhe completo, com a lista de erros de cada execução: `execucoes/rodada1/medidas.md`
e `execucoes/rodada2/medidas.md` (gerados por `medir.py`). As medidas das duas rodadas
foram recalculadas com o avaliador final, que ganhou sinônimos de sentido depois da
revisão adversária; as execuções em si não mudaram. Cada execução rodou uma vez: a
variação entre rodadas não foi medida.

### Matrizes de confusão (rodada 2)

Linha: sentido do gabarito. Coluna: sentido que a frase comunica.

| Pobre | avanco | recuo | nova |
| :-- | --: | --: | --: |
| avanco | 37 | 0 | 0 |
| recuo | 0 | 2 | 0 |
| nova | 0 | 0 | 1 |

| Boa | avanco | recuo | nova | não resolvido |
| :-- | --: | --: | --: | --: |
| avanco | 35 | 0 | 0 | 2 |
| recuo | 0 | 2 | 0 | 0 |
| nova | 0 | 0 | 1 | 0 |

A matriz diz pouco: o sentido vem pronto da regra e o gabarito tem 37 de 40
itens `avanco`. O erro do modelo não está no sentido, está no conteúdo da
frase (valor, etapa, jargão).

### Três erros comentados

1. **Cópia do molde da frase vizinha, com o marcador** (R2 pobre, `202643200021`). O item tem reservado +R$ 1.250.000,00, liberado +R$ 1.255.000,00 e pago +R$ 14.540,00. O modelo escreveu "Valor empregado e pago foram aumentados em **R$ X e R$ X**, respectivamente." Ele copiou de `buscar_semelhante` a frase do item anterior, já com os valores mascarados, e não trocou o marcador pelos valores do item. A máscara resolveu a cópia de números (17 → 2 repetições), mas não a cópia de molde: quase todas as frases da pobre seguem "Valor X e Y foram aumentados em …".
2. **A justificativa virou a frase** (R2 boa, `202641550011`). O item troca o local de "AMERICANA - SP" para "MÚLTIPLO" e reserva +R$ 250.480,75; nada foi pago. A spec boa produziu "A emenda foi registrada com confiança, pois a mudança foi de avanço no valor empenhado e pago." A frase não tem valor, usa jargão, afirma um pagamento que não houve e é a mesma em 5 itens. O modelo misturou o texto do glossário e da ferramenta `registrar` com a frase.
3. **Etapa errada, aprovada pelos quatro critérios** (R2 pobre, `202643020009`). Só o pago mudou (+R$ 9.800,00). O modelo escreveu "Valor empregado e pago foram aumentados em R$ 9.800,00 e R$ 9.800,00". O valor confere, o sentido confere, e "empregado" (o "empenhado" escrito errado pelo modelo) escapa da lista de jargão. Mas a frase diz que o reservado subiu, e não subiu. É o caso que motivou a auditoria pós-hoc: dos 12 acertos da pobre na rodada 2, 4 caem por isso.

### Um erro que persistiu nas duas execuções

`202529250005`: restos a pagar inscritos −R$ 8.000,00 e restos a pagar pagos +R$ 8.000,00, o mesmo dinheiro de anos anteriores sendo pago.

- Pobre: "Valor liquidado foi aumentado em R$ X." (etapa errada, marcador copiado).
- Boa: "A emenda alterou o valor dos restos a pagar, passando de R$ 8.000,00 para R$ 0,00, com um avanço de R$ 8.000,00." (jargão; trata a queda do inscrito como avanço).
- Humano: "Um pequeno valor pendente de R$ 8 mil do passado foi resolvido e pago para o Esporte e Lazer em SC."

A regra 3 da spec boa descreve exatamente esse caso e não bastou. Dos 9 itens
com restos a pagar, 7 falham nas duas specs; ao todo, 27 itens falham nas duas
execuções da rodada 2.

### O que os números dizem

- **O contrato de ferramentas funcionou; o conteúdo não.** Com a normalização de argumentos, 78 das 80 execuções da rodada 2 terminaram em `registrar` com formato válido, em cerca de 3 passos. A falha está no que o modelo escreve.
- **A spec boa piorou o resultado com este modelo.** Mais texto de referência (8 regras, cerca de 1 200 caracteres) levou o qwen3:1.7b a repetir os termos que deveria evitar (sem jargão: 37,5% → 5,0%) e a confundir justificativa com frase. Na aula, a description com "quando usar" levou o uso de ferramenta de 0% a 77%. Aqui o problema não é usar a ferramenta, é escrever, e mais instrução não ajudou um modelo de 1,7B.
- **Confiança declarada não serve de filtro.** O modelo declarou `alta` em 78 dos 80 itens das duas execuções da rodada 2, inclusive nos errados.
- **O melhor número honesto é 20% (8 de 40), na spec pobre auditada.** A tarefa de escrever para o morador, como foi especificada, não está ao alcance do `qwen3:1.7b` sem revisão humana.

### Limites da medição

- O avaliador confere o que dá para conferir por regra. O léxico de sentido e de jargão é limitado: "empregado" passou como não-jargão, e frases com sinônimos não previstos podem ser reprovadas. Ele foi validado nas 40 frases humanas e em exemplos da revisão adversária, não em um conjunto separado.
- O gabarito é desequilibrado (37 avanço, 2 recuo, 1 nova): a matriz de confusão e o critério de sentido quase não exercitam os outros sentidos.
- A auditoria de etapa foi criada depois de ver as saídas da rodada 2. Por isso fica em linha separada, e não substitui a acurácia definida antes.
- Não repeti a execução com um segundo modelo (opcional no tutorial).
- O laço foi escrito do zero em Python; não partiu do `agente.sh` da aula.

## 5. Entrega ao projeto (B5)

- `dados.jsonl`: o corpus inteiro (3 191 itens) enriquecido com a spec **pobre**, a de melhor acurácia medida. <!-- DADOS -->
- `ESQUEMA.md`: cada campo, tipo, obrigatoriedade e significado, com os nomes do modelo de dados do Trabalho 1. O grupo ainda não tem `CONTRATOS.md`.
- `carregar.py`: lê `dados.jsonl` e grava num SQLite, em `LoteImportacao`, `MudancaLote` (como no Trabalho 1) e na tabela nova `ResumoMudanca`. Cada frase passa pela mesma conferência do avaliador mais a etapa; `conferida = 1` quando passa, e `revisar = 1` quando não passa ou tem confiança baixa. Rodar de novo não duplica nada e atualiza o resumo (`tests/test_carregar.py`).

Falta: **um colega do grupo confirmar por escrito que o `carregar.py` funcionou**
(item do checklist do tutorial).

## 6. Aderência ao módulo (C)

- **C1.** O recorte (mudanças entre dois lotes da mesma fonte, com proveniência por registro) é o que o módulo `nucleo` produz no Trabalho 1: `MudancaLote`, calculada na publicação de cada lote (ADR-0009). Não se sobrepõe ao da Sarah (emendas da PB com fase de execução) nem ao do João Rafael (favorecidos).
- **C2.** Os campos usam os nomes do modelo de dados do Trabalho 1: `codigo_emenda`, `estado_antes`, `estado_depois`, `tipo`, `etapa`, `*_centavos`, `LoteImportacao`, `MudancaLote`. O campo novo de classificação se chama `sentido`, para não colidir com `MudancaLote.tipo`.
- **C4. A decisão que muda.** No modelo de dados do Trabalho 1, eu acrescentaria a entidade `ResumoMudanca` (`lote_novo_id`, `codigo_emenda`, `sentido`, `resumo`, `confianca`, `conferida`, `revisar`, `modelo`, `spec`) com esta regra: **o painel só mostra o `resumo` gerado quando `conferida = 1` e `revisar = 0`; nos outros casos mostra o `texto_simples` da `TabelaTraducao`**, que é fixo, versionado e escrito por pessoa (ADR-0008). O que medi sustenta isso:
  - o sentido da mudança é derivável por regra (40 de 40), então fica no núcleo como regra, ao lado de `MudancaLote.tipo`;
  - o texto livre de um modelo de 1,7B acerta 20% (auditado) e declara confiança alta mesmo quando erra, então não pode ir direto para a tela;
  - a tradução versionada do Trabalho 1 continua sendo a fonte confiável, e o modelo entra só como rascunho conferido.

## 7. Como reproduzir

```bash
cd modulos/nucleo/enriquecimento
python3 -m unittest discover -s tests -t .           # 68 testes, sem modelo
python3 gabarito.py conferir                          # sorteio e rótulos
ollama pull qwen3:1.7b && ollama serve
python3 enriquecedor.py --spec pobre --entrada gabarito --saida /tmp/exec1.jsonl
python3 enriquecedor.py --spec boa   --entrada gabarito --saida /tmp/exec2.jsonl
python3 medir.py /tmp/exec1.jsonl /tmp/exec2.jsonl
python3 carregar.py dados.jsonl --banco /tmp/rastro.db
```
