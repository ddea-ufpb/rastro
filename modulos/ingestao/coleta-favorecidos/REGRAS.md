# Regras do normalizador

Coleta de 2026-11-22. "Item que motivou" aponta a linha do arquivo original (`EmendasParlamentares_PorFavorecido.csv:N`) quando a linha não entra no extrato, ou a linha do extrato (`bruto/favorecidos-pb-2026-11-22.csv:N`) quando entra. Linhas de pessoa não são citadas pelo conteúdo, só pela posição. As contagens contam linhas de pagamento.

| Regra | O que faz | Item que motivou | Linhas afetadas |
|---|---|---|---|
| R-RECORTE | Mantém só linhas com emenda da PB (`Código UF IBGE = 2500000` em `EmendasParlamentares.csv`) ou com `UF Favorecido = PB`; as outras não são descarte, estão fora do recorte | Contrato da Sarah, REQ-52: emendas `MÚLTIPLO` de fora pagam entidades da PB | 804 458 fora do recorte |
| R-PF | `Tipo Favorecido = Pessoa Fisica` → descarte `favorecido_pessoa_fisica`, já na obtenção (não entra no extrato) | `EmendasParlamentares_PorFavorecido.csv:114` (nome completo e CPF parcial de pessoa) | 11 497 |
| R-EI | Natureza `Empresário (Individual)` → descarte `favorecido_empresario_individual`, já na obtenção | `EmendasParlamentares_PorFavorecido.csv:68`; das 190 entidades com essa natureza, 17 tinham o CPF inteiro no nome | 504 |
| R-SEMFAV | `Tipo Favorecido` `Sem informação` ou `Inválido` (código `-8`, `-3`, `9000…`, nome `SEM INFORMACAO`) → descarte `favorecido_nao_identificado` | `EmendasParlamentares_PorFavorecido.csv:7005` | 180 |
| R-UG | `Tipo Favorecido = Unidade Gestora` (código de 6 dígitos, ex.: UFPB `153065`) → descarte `unidade_gestora_sem_cnpj` | `EmendasParlamentares_PorFavorecido.csv:74369` | 11 |
| R-TIPO | Qualquer outro tipo que não seja `Pessoa Jurídica` → descarte `favorecido_tipo_desconhecido` | `EmendasParlamentares_PorFavorecido.csv:104661` (`Inscrição Genéric`, nome de pessoa) | 1 |
| R-CNPJ | Código do favorecido precisa ter 14 dígitos e dígitos verificadores corretos → senão descarte `cnpj_invalido` | Na 1ª versão, sem R-SEMFAV, 181 linhas caíam aqui; eram favorecidos não identificados, não CNPJ com erro | 0 |
| R-SEMINFO | `Sem informação` / `S/I` → `null` (código da emenda, natureza, município) | `bruto/favorecidos-pb-2026-11-22.csv:2108` (código da emenda) · `:328` (município) | 1 226 código da emenda · 65 município · 0 natureza |
| R-UF | UF que não é sigla de 2 letras → `null` | `bruto/favorecidos-pb-2026-11-22.csv:328` (UF `-1`) | 65 |
| R-NEG | Valor negativo é mantido (estorno), não descartado | `bruto/favorecidos-pb-2026-11-22.csv:25` (`-34705,63`, Fundação FUNETEC) | 14 |
| R-VALOR | Valor no formato `^-?\d+,\d{2}$` (REQ-48) → vira string com ponto (`600000.00`), sem float; fora do formato → descarte `valor_fora_do_formato` | Formato observado em todas as linhas | 19 647 convertidas · 0 descartadas |
| R-ANOMES | `Ano/Mês` precisa ser `AAAAMM` com mês 01–12; mantido como `AAAAMM` (nome e formato do contrato `pagamento_favorecido.ano_mes`) | Formato observado em todas as linhas | 0 descartadas |
| R-TEXTO | Nome com espaços colapsados e sem quebra de linha | Guarda do esqueleto do tutorial | 0 |
| R-COLUNAS | Linha com número de colunas diferente de 13 → descarte `numero_de_colunas_inesperado` | Guarda (REQ-48) | 0 |
| R-CHAVE | Uma entidade por CNPJ: chave = sha256 do CNPJ; os pagamentos da entidade ficam em `campos.pagamentos` | Na coleta, cada CNPJ veio com um nome só; o coletor falha (assert) se aparecer um segundo nome | 19 647 pagamentos → 2 353 entidades |

## Observações que não viraram regra

- Mesmo nome com CNPJ diferente é comum e **não** é a mesma entidade: há 71 CNPJs chamados `FUNDO MUNICIPAL DE ASSISTENCIA SOCIAL`, um por município. O município separa esses casos sem modelo.
- 32 raízes de CNPJ (8 primeiros dígitos) têm mais de uma filial (ex.: `MUNICIPIO DE ALAGOA GRANDE`, duas). Raiz igual é a mesma pessoa jurídica: isso é regra, não decisão do modelo. Fica para a Etapa 2.
