# Requisitos — EARS

Requisitos do Rastro (REQ-01 a REQ-88) nos cinco moldes EARS (Mavin et al., 2009). Cada id é estável e citado nas fichas de tela, nos contratos, nas ADRs e nos cenários de qualidade.

- **Molde:** U = ubíquo · E = evento (QUANDO) · S = estado (ENQUANTO) · I = indesejado (SE … ENTÃO) · O = opcional (ONDE). Todo requisito tem o sujeito "O SISTEMA" e uma única obrigação.
- **Origem:** FI-01 = Formulário de Ideação (19/11/2026), por seção. AC-n = critério de aceitação da primeira fatia (FI-01 §11.2). T2 = coleta real do Trabalho 2 (`modulos/ingestao/coleta-favorecidos/REGRAS.md`, 22/11/2026), por regra. Brief = `README.md` do repositório. ADR = decisão em `adr/`.
- **Verificação:** teste previsto (arquivo · caso). Caminhos relativos a `modulos/<módulo>/tests/`. `e2e/` são testes da interface (Playwright + axe).
- **Módulo:** `ingestao`, `nucleo`, `consulta`, `saida` (mapa no [README](README.md#mapa-para-os-quatro-módulos)); "todos" = transversal.
- **Telas:** fichas que citam o requisito, conferidas por `../verificar.py`. "—" = coberto por ADR, contrato ou cenário de qualidade.

Convenções: "importação vigente" é a apontada por `ImportacaoVigente`; valores monetários são inteiros em centavos (`*_centavos`); erros da API seguem `application/problem+json` (RFC 9457) com o campo `codigo`; ⟨ ⟩ marca meta provisória, revista depois do baseline (FI-01 §7.2).

## A · Importação e publicação

| ID | Molde | Requisito | Origem | Verificação | Módulo | Telas |
| :-- | :-: | :-- | :-- | :-- | :-- | :-- |
| REQ-01 | E | QUANDO o operador executar `rastro importar --arquivo <zip>`, O SISTEMA DEVE ler em fluxo `EmendasParlamentares.csv` e `EmendasParlamentares_PorFavorecido.csv` (Windows-1252, separador `;`) e registrar uma `Importacao` em `em_andamento` com `sha256`, `fonte_last_modified` e `iniciada_em`. | FI-01 §11.3 | `test_importar.py::test_importa_zip_amostra` | ingestao | O01 |
| REQ-02 | E | QUANDO o operador executar `rastro importar --baixar`, O SISTEMA DEVE pedir o zip com `If-None-Match` igual ao `fonte_etag` da última importação publicada e guardar o bruto como `bruto/emendas-<aaaa-mm-dd>.zip` antes de importar. | FI-01 §10.4; T2 (ETag) | `test_baixar.py::test_get_condicional` | ingestao | O01 |
| REQ-03 | E | QUANDO a fonte responder `304 Not Modified`, O SISTEMA DEVE encerrar com código 0 e a mensagem "fonte sem alteração desde dd/mm/aaaa", sem criar importação. | FI-01 §10.4 | `test_baixar.py::test_304_nao_cria_importacao` | ingestao | O01 |
| REQ-04 | U | O SISTEMA DEVE manter no recorte só as linhas cuja emenda tem `Código UF IBGE = 2500000` ou cujo favorecido tem `UF Favorecido = PB`, sem contar as demais como descarte. | FI-01 §5; T2 R-RECORTE | `test_recorte.py::test_emenda_multiplo_paga_entidade_pb` | ingestao | O01 |
| REQ-05 | E | QUANDO o operador importar um arquivo cujo `sha256` já pertence a uma importação `publicada`, O SISTEMA DEVE encerrar com código 0 e a mensagem "arquivo já importado (importação #n)", sem criar importação. | AC-1 | `test_importar.py::test_reimportar_mesmo_arquivo` | ingestao | O01 |
| REQ-06 | U | O SISTEMA DEVE identificar cada pagamento por `chave_pagamento` = sha256 de (`codigo_emenda`, `cnpj`, `ano_mes`, `valor_centavos`, ordinal da repetição), com `UNIQUE (importacao_id, chave_pagamento)`. | AC-1; ADR-0002 | `test_gravar.py::test_duas_importacoes_mesmas_contagens` | ingestao | — |
| REQ-07 | I | SE o zip não tiver os arquivos ou as colunas de `contratos/fonte-portal.md`, ENTÃO O SISTEMA DEVE marcar a importação como `falhou` com `motivo_falha = formato_alterado` e manter a vigente. | FI-01 §10.4 | `test_importar.py::test_coluna_renomeada` | ingestao | O01, P09 |
| REQ-08 | I | SE os descartes por formato (`valor_fora_do_formato`, `numero_de_colunas_inesperado`, `codigo_emenda_invalido`) passarem de ⟨2%⟩ das linhas do recorte, ENTÃO O SISTEMA DEVE marcar a importação como `falhou` com `motivo_falha = descartes_acima_do_limite`. | ADR-0002; T2 (0 descartes de formato em 31 840 linhas) | `test_importar.py::test_limite_de_descartes` | ingestao | O01, P09 |
| REQ-09 | E | QUANDO a importação passar nas validações, O SISTEMA DEVE, numa única transação, gravar os registros, marcar a importação como `publicada` com `publicada_em` e apontar `ImportacaoVigente` para ela. | FI-01 §10.2; ADR-0002 | `test_publicar.py::test_publicacao_atomica` | ingestao | O01 |
| REQ-10 | S | ENQUANTO uma importação estiver em andamento, O SISTEMA DEVE responder cada consulta com dados de uma única importação: a vigente no início da transação de leitura. | FI-01 §7.1; ADR-0002 | `test_publicar.py::test_leitura_durante_publicacao` | consulta | — |
| REQ-11 | I | SE o processo de importação for interrompido, ENTÃO O SISTEMA DEVE, na execução seguinte da CLI, marcar a importação órfã como `falhou` com `motivo_falha = interrompida`. | FI-01 §7.1 (vivacidade) | `test_importar.py::test_sigkill_vira_falhou` | ingestao | O01, P09 |
| REQ-12 | I | SE uma importação passar de ⟨30 min⟩ em `em_andamento`, ENTÃO O SISTEMA DEVE cancelá-la e marcá-la como `falhou` com `motivo_falha = tempo_esgotado`. | FI-01 §7.1 (vivacidade), §12 | `test_importar.py::test_tempo_esgotado` | ingestao | O01 |
| REQ-13 | U | O SISTEMA DEVE responder às consultas só com registros da importação vigente. | FI-01 §7.1 | `test_consulta.py::test_ignora_importacao_nao_publicada` | consulta | — |
| REQ-14 | E | QUANDO `rastro importar` rodar, O SISTEMA DEVE ler e normalizar os arquivos do zip concorrentemente (um worker `asyncio` por arquivo) e entregar as linhas a um único escritor, que grava a transação de publicação. | FI-01 §7.1 (a); ADR-0007 | `test_concorrencia.py::test_workers_um_escritor` | ingestao | O01 |
| REQ-15 | I | SE o download da fonte falhar ou exceder ⟨120 s⟩, ENTÃO O SISTEMA DEVE registrar a importação como `falhou` com `motivo_falha = fonte_indisponivel` e manter a vigente. | FI-01 §10.4 | `test_baixar.py::test_fonte_fora_do_ar` | ingestao | O01, P09 |

## B · Normalização, favorecidos e descartes

| ID | Molde | Requisito | Origem | Verificação | Módulo | Telas |
| :-- | :-: | :-- | :-- | :-- | :-- | :-- |
| REQ-16 | I | SE `Tipo Favorecido = Pessoa Fisica`, ENTÃO O SISTEMA DEVE descartar a linha antes de persistir, com motivo `favorecido_pessoa_fisica`, guardando só arquivo, linha e motivo. | AC-3; FI-01 §8.3; ADR-0004 | `test_normalizar.py::test_pessoa_fisica_nao_persiste` | ingestao | O01, P05 |
| REQ-17 | I | SE a natureza do favorecido for `Empresário (Individual)`, ENTÃO O SISTEMA DEVE descartar a linha com motivo `favorecido_empresario_individual`. | FI-01 §8.5; T2 R-EI (17 de 190 com CPF no nome); ADR-0004 | `test_normalizar.py::test_empresario_individual` | ingestao | O01, P05 |
| REQ-18 | I | SE `Tipo Favorecido` for `Sem informação` ou `Inválido`, ENTÃO O SISTEMA DEVE descartar a linha com motivo `favorecido_nao_identificado`. | T2 R-SEMFAV | `test_normalizar.py::test_sem_informacao` | ingestao | O01 |
| REQ-19 | I | SE `Tipo Favorecido = Unidade Gestora`, ENTÃO O SISTEMA DEVE descartar a linha com motivo `unidade_gestora_sem_cnpj`. | T2 R-UG | `test_normalizar.py::test_unidade_gestora` | ingestao | O01 |
| REQ-20 | I | SE o código do favorecido não tiver 14 dígitos com dígitos verificadores de CNPJ corretos, ENTÃO O SISTEMA DEVE descartar a linha com motivo `cnpj_invalido`. | FI-01 §8.3; T2 R-CNPJ | `test_normalizar.py::test_cnpj_digito_errado` | ingestao | O01 |
| REQ-21 | U | O SISTEMA DEVE identificar o favorecido só pelo CNPJ, com `Favorecido.cnpj` `UNIQUE NOT NULL`, e nunca unir favorecidos por nome. | AC-2; FI-01 §9.1; ADR-0001 | `test_gravar.py::test_unique_cnpj` | ingestao | P06 |
| REQ-22 | E | QUANDO o mesmo CNPJ chegar com razões sociais diferentes, O SISTEMA DEVE manter uma única entidade, com a razão social mais frequente na importação em `razao_social` e todas as grafias em `NomeFavorecido`. | AC-2 | `test_gravar.py::test_mesmo_cnpj_dois_nomes` | ingestao | P06 |
| REQ-23 | U | O SISTEMA DEVE gravar valores negativos (estornos) como publicados e somá-los com sinal. | T2 R-NEG (14 estornos) | `test_normalizar.py::test_estorno_negativo` | ingestao | P05 |
| REQ-24 | U | O SISTEMA DEVE converter valores no formato `^-?\d+,\d{2}$` para centavos inteiros, sem ponto flutuante, e descartar os demais com motivo `valor_fora_do_formato`. | T2 R-VALOR | `test_normalizar.py::test_valor_em_centavos` | ingestao | — |
| REQ-25 | U | O SISTEMA DEVE gravar `Sem informação`, `S/I` e UF fora do padrão de duas letras como nulo. | T2 R-SEMINFO, R-UF | `test_normalizar.py::test_sem_informacao_vira_nulo` | ingestao | — |
| REQ-26 | U | O SISTEMA DEVE gravar cada `Descarte` com `importacao_id`, `arquivo`, `linha`, `motivo` e `municipio_ibge` (quando a linha o tiver), sem nenhuma coluna de nome ou CPF. | FI-01 §8.3, §8.4; ADR-0004, ADR-0009 | `test_normalizar.py::test_descarte_sem_dado_pessoal` | ingestao | P02, P09 |
| REQ-27 | U | O SISTEMA DEVE agrupar CNPJs da mesma raiz (8 primeiros dígitos) como filiais só para exibição, mantendo os totais por CNPJ. | T2 (32 raízes com filiais) | `test_consulta.py::test_filiais_sem_somar` | consulta | P05, P06 |

## C · Proveniência, fase e mudanças

| ID | Molde | Requisito | Origem | Verificação | Módulo | Telas |
| :-- | :-: | :-- | :-- | :-- | :-- | :-- |
| REQ-28 | U | O SISTEMA DEVE gravar `fonte`, `arquivo`, `linha` e `extraido_em` como `NOT NULL` em todo registro de `Emenda`, `Pagamento` e `Favorecido`. | FI-01 §4.4, §10.1; ADR-0003 | `test_schema.py::test_insert_sem_proveniencia_falha` | ingestao | P09 |
| REQ-29 | U | O SISTEMA DEVE devolver, em toda resposta da API com valor monetário, a `Proveniencia` desse valor. | FI-01 §8.3; ADR-0003 | `test_contrato.py::test_todo_valor_tem_proveniencia` | consulta | P04, P05 |
| REQ-30 | U | O SISTEMA DEVE derivar `Emenda.fase` dos valores pela regra do ADR-0005 (`valor_final = empenhado − rp_cancelado`; `pago_total = pago + rp_pago`). | FI-01 §9; ADR-0005 | `test_fase.py::test_casos_reais_da_regra` | nucleo | P04, P10 |
| REQ-31 | U | O SISTEMA DEVE exibir cada fase com o `texto_simples` da versão vigente de `TraducaoFase`, o `termo_oficial` ao lado e a versão da tradução. | FI-01 §8.3, §8.4; ADR-0005 | `e2e/traducao.spec.ts` | nucleo | P02, P03, P04, P10, S03 |
| REQ-32 | E | QUANDO o operador executar `rastro traducao carregar <csv>`, O SISTEMA DEVE criar uma nova versão de `TraducaoFase` sem alterar as anteriores. | FI-01 §10.2 | `test_traducao.py::test_versao_nova_preserva_antigas` | nucleo | P10 |
| REQ-33 | I | SE a versão a carregar não traduzir todas as fases do ADR-0005 ou não citar a fonte da definição, ENTÃO O SISTEMA DEVE recusá-la com código 3. | FI-01 §12; ADR-0005 | `test_traducao.py::test_recusa_fase_sem_traducao` | nucleo | P10 |
| REQ-34 | E | QUANDO uma importação for publicada e existir vigente anterior, O SISTEMA DEVE calcular as `MudancaFase` (emenda, fase anterior, fase nova) na mesma transação da publicação. | FI-01 §4.2 (4); ADR-0006 | `test_mudancas.py::test_mudancas_na_publicacao` | nucleo | O01 |
| REQ-35 | E | QUANDO a primeira importação for publicada, O SISTEMA DEVE publicá-la sem gerar `MudancaFase`. | ADR-0006 | `test_mudancas.py::test_primeira_sem_mudancas` | nucleo | — |

## D · Sugestões de mesma entidade

| ID | Molde | Requisito | Origem | Verificação | Módulo | Telas |
| :-- | :-: | :-- | :-- | :-- | :-- | :-- |
| REQ-36 | E | QUANDO uma importação for publicada, O SISTEMA DEVE gerar `SugestaoMesmaEntidade` para pares de CNPJs de raízes diferentes, no mesmo município, cujo nome normalizado tenha similaridade ≥ ⟨0,9⟩, com `origem` e `confianca`. | FI-01 §8.3, §9; ADR-0001; T2 (71 "FUNDO MUNICIPAL DE ASSISTENCIA SOCIAL", um por município) | `test_sugestoes.py::test_mesmo_nome_outro_municipio_nao_sugere` | nucleo | O01, O02 |
| REQ-37 | U | O SISTEMA DEVE somar agregações por CNPJ, nunca por sugestão, revisada ou não. | FI-01 §8.3; ADR-0001 | `test_agregacoes.py::test_sugestao_nao_soma` | consulta | O02, P06, P07 |
| REQ-38 | E | QUANDO o operador executar `rastro sugestoes revisar <id> --decisao relacionadas|distintas`, O SISTEMA DEVE gravar a decisão, o revisor e a data, sem alterar nenhum total. | FI-01 §8.3 | `test_sugestoes.py::test_revisao_nao_muda_total` | nucleo | O02 |
| REQ-39 | U | O SISTEMA DEVE exibir sugestões pendentes com o rótulo "Sugestão automática, não revisada", as `relacionadas` com o rótulo "Revisada: entidades relacionadas" e nunca as `distintas`. | FI-01 §8.3 | `e2e/favorecido.spec.ts` | consulta | O02, P06 |

## E · Consulta

| ID | Molde | Requisito | Origem | Verificação | Módulo | Telas |
| :-- | :-: | :-- | :-- | :-- | :-- | :-- |
| REQ-40 | E | QUANDO o cliente pedir um município pelo código IBGE, O SISTEMA DEVE devolver as emendas destinadas a ele, a contagem por fase, o recebido por entidades sediadas nele e a contagem de descartes ligados a ele. | FI-01 §4.2 (1), §8.4; ADR-0009, ADR-0010 | `test_api_municipio.py::test_resumo` | consulta | P01, P02 |
| REQ-41 | I | SE o código IBGE não for de município da PB, ENTÃO O SISTEMA DEVE responder 404 com `codigo = municipio_nao_encontrado`. | FI-01 §5 | `test_api_municipio.py::test_fora_da_pb` | consulta | P01, P02 |
| REQ-42 | U | O SISTEMA DEVE mostrar, no município, "Destinado à cidade" e "Recebido por entidades da cidade" em blocos separados, sem somá-los. | ADR-0010 | `e2e/municipio.spec.ts` | consulta | P02 |
| REQ-43 | E | QUANDO o cliente listar emendas, O SISTEMA DEVE filtrar por `municipio_ibge`, `autor_codigo`, `funcao_codigo`, `ano` e `fase`, com paginação por cursor e `limite` ≤ 100. | FI-01 §4.1 | `test_api_emendas.py::test_filtros_combinados` | consulta | P03 |
| REQ-44 | I | SE um filtro tiver valor inválido, ENTÃO O SISTEMA DEVE responder 422 com o nome do parâmetro em `campo`. | Brief (contrato) | `test_api_emendas.py::test_filtro_invalido` | consulta | P03, P04 |
| REQ-45 | E | QUANDO o cliente pedir uma emenda pelo código, O SISTEMA DEVE devolver o valor de cada etapa com proveniência, a fase traduzida, o autor e o local de destino. | FI-01 §4.2 (1) | `test_api_emendas.py::test_detalhe` | consulta | P04 |
| REQ-46 | I | SE a emenda não existir na importação vigente, ENTÃO O SISTEMA DEVE responder 404 com `codigo = emenda_nao_encontrada`. | Brief (contrato) | `test_api_emendas.py::test_inexistente` | consulta | P04, P05 |
| REQ-47 | E | QUANDO o cliente pedir os pagamentos de uma emenda, O SISTEMA DEVE listá-los por favorecido (CNPJ, razão social, natureza, `ano_mes`, valor) com a soma e a contagem de linhas descartadas da emenda por motivo. | FI-01 §4.2 (2) | `test_api_pagamentos.py::test_lista_e_soma` | consulta | P05 |
| REQ-48 | E | QUANDO o cliente pedir um favorecido pelo CNPJ, O SISTEMA DEVE devolver os pagamentos recebidos por emenda, as grafias já vistas, as filiais da mesma raiz e as sugestões visíveis. | FI-01 §4.2 (2) | `test_api_favorecidos.py::test_detalhe` | consulta | P06 |
| REQ-49 | I | SE o CNPJ pedido não tiver 14 dígitos, ENTÃO O SISTEMA DEVE responder 422; SE não existir, 404 com `codigo = favorecido_nao_encontrado`. | Brief (contrato) | `test_api_favorecidos.py::test_cnpj_invalido_e_inexistente` | consulta | P06 |
| REQ-50 | E | QUANDO o cliente buscar favorecidos por texto, O SISTEMA DEVE devolver os que têm o texto na razão social, numa grafia ou no CNPJ, em ordem alfabética. | FI-01 §4.1 | `test_api_favorecidos.py::test_busca` | consulta | P01 |
| REQ-51 | E | QUANDO o cliente pedir agregações por `parlamentar`, `municipio` ou `funcao`, O SISTEMA DEVE devolver as somas de cada etapa por grupo, em ordem alfabética do nome do grupo. | FI-01 §4.2 (3) | `test_agregacoes.py::test_por_tres_eixos` | consulta | P07 |
| REQ-52 | U | O SISTEMA DEVE recusar com 422 qualquer pedido de ordenação de parlamentares por valor, nota ou posição. | FI-01 §5; Brief | `test_agregacoes.py::test_sem_ranking` | consulta | P01, P02, P03, P07, P08 |
| REQ-53 | E | QUANDO o cliente pedir um parlamentar pelo código, O SISTEMA DEVE devolver as emendas dele destinadas à PB e as somas por etapa. | FI-01 §4.2 (3) | `test_api_parlamentar.py::test_detalhe` | consulta | P08 |
| REQ-54 | E | QUANDO o cliente listar importações, O SISTEMA DEVE devolver cada uma com status, datas, contagens, `motivo_falha` e descartes por motivo. | FI-01 §7 (API) | `test_api_importacoes.py::test_lista` | consulta | P09 |
| REQ-55 | E | QUANDO o cliente pedir uma importação, O SISTEMA DEVE devolver os descartes por motivo e por município. | FI-01 §8.4 | `test_api_importacoes.py::test_descartes_por_municipio` | consulta | P09 |
| REQ-56 | S | ENQUANTO não houver importação publicada, O SISTEMA DEVE responder às consultas de dados com 503 e `codigo = sem_importacao_publicada`. | ADR-0002 | `test_consulta.py::test_sem_importacao` | consulta | P01, P02, P03, P04, P05, P06, P07, P08 |
| REQ-57 | U | O SISTEMA DEVE servir a API em `/api/v1` com um `/openapi.json` equivalente a `contratos/openapi.yaml`. | FI-01 §6 | `test_contrato.py::test_openapi_igual_ao_arquivo` | consulta | — |
| REQ-58 | I | SE um IP passar de ⟨60⟩ requisições por minuto, ENTÃO O SISTEMA DEVE responder 429 com `Retry-After`. | Brief (contrato) | `test_api_limite.py::test_429` | consulta | P01, P02, P03, P04, P05, P06, P07, P08, P09, P10, S01 |
| REQ-59 | U | O SISTEMA DEVE responder todo erro em `application/problem+json` com `codigo` e `request_id`. | RFC 9457 | `test_contrato.py::test_erros_problem_json` | consulta | — |
| REQ-60 | E | QUANDO o cliente pedir o status, O SISTEMA DEVE devolver a importação vigente (id, `publicada_em`, `fonte_last_modified`, `extraido_em`) e a versão vigente da tradução. | FI-01 §4.4 | `test_api_status.py::test_status` | consulta | P01, P09 |

## F · Assinaturas e alertas

| ID | Molde | Requisito | Origem | Verificação | Módulo | Telas |
| :-- | :-: | :-- | :-- | :-- | :-- | :-- |
| REQ-61 | E | QUANDO alguém criar uma assinatura com e-mail e filtro (município ou parlamentar), O SISTEMA DEVE gravá-la como `pendente` e enviar um e-mail de confirmação com token de uso único válido por 48 h. | FI-01 §4.2 (4); ADR-0006 | `test_assinaturas.py::test_cria_pendente` | saida | S01 |
| REQ-62 | U | O SISTEMA DEVE aceitar na assinatura só `email` e `filtro`, respondendo 422 a qualquer outro campo. | FI-01 §5, §8.3 | `test_assinaturas.py::test_campo_extra_422` | saida | S01 |
| REQ-63 | I | SE o token de confirmação ou de gestão estiver expirado, usado ou desconhecido, ENTÃO O SISTEMA DEVE responder 410 com `codigo = token_invalido`. | ADR-0006 | `test_assinaturas.py::test_token_expirado` | saida | S02 |
| REQ-64 | E | QUANDO o token de confirmação for válido, O SISTEMA DEVE marcar a assinatura como `ativa` e gerar o token de gestão. | ADR-0006 | `test_assinaturas.py::test_confirma` | saida | S02, S03 |
| REQ-65 | E | QUANDO uma `MudancaFase` casar com o filtro de uma assinatura `ativa`, O SISTEMA DEVE criar um `AlertaEnviado` por (assinatura, emenda, importação), com `UNIQUE` nessa tripla. | FI-01 §7.1, §9 | `test_alertas.py::test_unique_tripla` | saida | S03 |
| REQ-66 | U | O SISTEMA DEVE enviar no máximo um e-mail por assinatura e importação, listando todas as mudanças dela. | FI-01 §10.1 | `test_alertas.py::test_um_email_por_importacao` | saida | S03 |
| REQ-67 | E | QUANDO houver alertas `pendente`, O SISTEMA DEVE enviá-los por ⟨4⟩ workers `asyncio` que consomem uma `asyncio.Queue`. | FI-01 §6, §7.1 (c); ADR-0007 | `test_despachante.py::test_workers_concorrentes` | saida | S03 |
| REQ-68 | I | SE o envio de um e-mail falhar, ENTÃO O SISTEMA DEVE tentar de novo até 3 vezes com espera exponencial e marcar o alerta como `falhou`. | FI-01 §7.1 (vivacidade) | `test_despachante.py::test_tres_tentativas` | saida | S03 |
| REQ-69 | I | SE o despachante parar durante um envio, ENTÃO O SISTEMA DEVE, ao reiniciar, reenfileirar os alertas `pendente` e `enviando` sem reenviar os `enviado`. | FI-01 §7.1 (segurança) | `test_despachante.py::test_reinicio_sem_duplicar` | saida | — |
| REQ-70 | E | QUANDO o assinante cancelar, O SISTEMA DEVE apagar o e-mail, as assinaturas e os alertas ligados a ele. | FI-01 §8.3 | `test_assinaturas.py::test_cancelar_apaga_email` | saida | S02, S03 |
| REQ-71 | U | O SISTEMA DEVE incluir em todo e-mail de alerta o link de cancelamento, a fonte e a data da importação. | FI-01 §8.4 | `test_email.py::test_rodape_obrigatorio` | saida | S03 |
| REQ-72 | U | O SISTEMA DEVE transportar o token de gestão no fragmento da URL e no cabeçalho `X-Token-Assinatura`, nunca na query string. | ADR-0006 | `test_assinaturas.py::test_token_nao_aceito_na_query` | saida | S02, S03 |
| REQ-73 | I | SE já existir assinatura `ativa` para o mesmo e-mail e filtro, ENTÃO O SISTEMA DEVE responder 202 como para uma nova, sem criar outra. | ADR-0006 (não revelar quem assina) | `test_assinaturas.py::test_duplicada_mesma_resposta` | saida | S01 |
| REQ-74 | I | SE um e-mail receber mais de ⟨3⟩ pedidos de confirmação numa hora, ENTÃO O SISTEMA DEVE responder 202 sem enviar novo e-mail. | ADR-0006 | `test_assinaturas.py::test_limite_por_email` | saida | S01 |

## G · Interface (transversal)

| ID | Molde | Requisito | Origem | Verificação | Módulo | Telas |
| :-- | :-: | :-- | :-- | :-- | :-- | :-- |
| REQ-75 | U | O SISTEMA DEVE mostrar em toda tela com dados a faixa "Portal da Transparência · atualizado pela fonte em dd/mm/aaaa · importado em dd/mm/aaaa (importação #n)", com link para P09. | FI-01 §4.4, §8.4 | `e2e/proveniencia.spec.ts` | todos | P01, P02, P03, P04, P05, P06, P07, P08 |
| REQ-76 | S | ENQUANTO uma resposta estiver carregando, O SISTEMA DEVE mostrar um esqueleto com `aria-busy="true"`. | Diretrizes | `e2e/estados.spec.ts::carregando` | todos | P01, P02, P03, P04, P05, P06, P07, P08, P09, P10, S01, S02 |
| REQ-77 | E | QUANDO uma consulta não tiver resultado, O SISTEMA DEVE mostrar uma mensagem própria da tela, nunca R$ 0,00 ou tabela vazia sem texto. | FI-01 §8.4 | `e2e/estados.spec.ts::vazio` | todos | P01, P02, P03, P04, P05, P06, P07, P08, P09 |
| REQ-78 | I | SE a API responder 5xx, ENTÃO O SISTEMA DEVE mostrar a mensagem de erro com o `request_id` e o botão "Tentar de novo". | Diretrizes | `e2e/estados.spec.ts::erro` | todos | P01, P02, P03, P04, P05, P06, P07, P08, P09, P10, S01, S02 |
| REQ-79 | I | SE o navegador estiver sem conexão, ENTÃO O SISTEMA DEVE mostrar "Sem conexão" e nenhum valor guardado como se fosse atual. | Diretrizes | `e2e/estados.spec.ts::offline` | todos | P01, P02, P03, P04, P05, P06, P07, P08, P09, P10, S01, S02 |
| REQ-80 | U | O SISTEMA DEVE atender WCAG 2.2 AA em todas as telas web, com zero violações do axe. | Diretrizes | `e2e/a11y.spec.ts` | todos | — |
| REQ-81 | U | O SISTEMA DEVE executar copiar, exportar dados já carregados, voltar e abrir link externo sem chamada à API. | Diretrizes (convenção de ações) | `e2e/acoes-locais.spec.ts` | todos | P02, P03, P04, P05, P06, P07, P09, P10, S02, S03 |
| REQ-82 | U | O SISTEMA DEVE manter fora de toda tela e e-mail as palavras "desvio", "irregular", "suspeito", "atrasada", "parada" e "investido em". | FI-01 §5, §8.4 | `e2e/linguagem.spec.ts` | todos | P04, P07, P08, S03 |
| REQ-83 | U | O SISTEMA DEVE mostrar em toda tela e export o aviso "O Rastro mostra o caminho do dinheiro. Não avalia mérito nem comprova a aplicação final." | FI-01 §8.4 | `e2e/linguagem.spec.ts::aviso` | todos | P02, P03, P04, P05, P06, P07, P08, S03 |
| REQ-84 | E | QUANDO o usuário exportar uma lista em CSV, O SISTEMA DEVE incluir as colunas de proveniência e o aviso do REQ-83 na primeira linha. | FI-01 §8.4 | `e2e/export.spec.ts` | todos | P03, P05, P07 |

## H · Desempenho medido

| ID | Molde | Requisito | Origem | Verificação | Módulo | Telas |
| :-- | :-: | :-- | :-- | :-- | :-- | :-- |
| REQ-85 | U | O SISTEMA DEVE registrar a duração de cada etapa da importação (`download`, `leitura`, `normalizacao`, `publicacao`) em `Importacao.duracao_ms`. | FI-01 §7.2 | `test_importar.py::test_duracao_por_etapa` | ingestao | O01, P09 |
| REQ-86 | O | ONDE `--workers N` for informado, O SISTEMA DEVE usar N workers de leitura (1, 2 ou 4) e gravar N em `Importacao.workers`. | FI-01 §7.2 | `test_concorrencia.py::test_workers_parametro` | ingestao | O01 |
| REQ-87 | U | O SISTEMA DEVE responder `obter_agregacoes` e `obter_municipio` com p95 < ⟨300 ms⟩ sob ⟨20⟩ usuários virtuais do k6 por 60 s. | FI-01 §7.2, §10.1 | `perf/consulta.k6.js` (QA-04) | consulta | — |
| REQ-88 | U | O SISTEMA DEVE importar o zip completo da fonte em ≤ ⟨5 min⟩ com pico de memória ≤ ⟨512 MB⟩. | FI-01 §7.2, §10.3 (8 GB de RAM) | `perf/importacao.py` (QA-04) | ingestao | — |

## Critérios de aceitação do FI-01 × requisitos

| AC (FI-01 §11.2) | Requisitos |
| :-- | :-- |
| AC-1 Importação é idempotente | REQ-05, REQ-06 |
| AC-2 Mesmo CNPJ, nomes diferentes, uma entidade | REQ-21, REQ-22 |
| AC-3 Pessoa física não persiste | REQ-16, REQ-26 |
