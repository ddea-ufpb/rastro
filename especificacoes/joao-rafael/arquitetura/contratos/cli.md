# Contrato da CLI do operador

Comando `rastro`, instalado pelo pacote Python. Toda saída tem a forma texto (padrão, 80 colunas, sem depender de cor) e a forma `--json`. `NO_COLOR` e `--sem-cor` desligam cor. Os ids `cli:<comando>` são os citados nas fichas O01 e O02.

## Códigos de saída

| Código | Significado |
| :-: | :-- |
| 0 | sucesso, inclusive "fonte sem alteração" e "arquivo já importado" |
| 2 | uso errado (argumento faltando ou inválido) |
| 3 | entrada recusada (formato alterado, descartes acima do limite, tradução incompleta) |
| 4 | fonte indisponível |
| 5 | outra importação em andamento |
| 6 | tempo esgotado |
| 1 | erro interno, com `request_id` |

## `cli:importar` — `rastro importar`

```
rastro importar (--arquivo <zip> | --baixar) [--workers 1|2|4] [--json]
```

| Etapa | O que faz | Requisitos |
| :-- | :-- | :-- |
| 0 | Marca como `falhou`/`interrompida` qualquer importação órfã; recusa com código 5 se há outra viva (trava `pg_advisory_lock`) | REQ-11 |
| 1 | `--baixar`: GET condicional; `304` → código 0 "fonte sem alteração desde dd/mm/aaaa"; falha → código 4 | REQ-02, REQ-03, REQ-15 |
| 2 | `sha256` igual a importação publicada → código 0 "arquivo já importado (importação #n)" | REQ-05 |
| 3 | Valida arquivos e colunas contra `fonte-portal.md` → senão código 3 `formato_alterado` | REQ-07 |
| 4 | N workers leem e normalizam; descartes com motivo; um escritor recebe as linhas | REQ-04, REQ-14, REQ-16–26, REQ-86 |
| 5 | Descartes de formato > ⟨2%⟩ → código 3 `descartes_acima_do_limite` | REQ-08 |
| 6 | Transação de publicação: grava, calcula `MudancaFase` e sugestões, troca a vigente | REQ-09, REQ-34, REQ-36 |
| 7 | Enfileira os alertas das mudanças e encerra; o despachante envia | REQ-65, REQ-67 |

Tempo-limite total ⟨30 min⟩ → código 6 (REQ-12). Cada etapa grava sua duração (REQ-85).

Saída de sucesso (texto):

```
Importação #12 publicada
  fonte: Portal da Transparência, atualizado em 19/11/2026 22:36
  arquivo: bruto/emendas-2026-11-22.zip (sha256 221c0a3e…)
  linhas lidas: 836 298   no recorte: 31 840   aceitas: 19 647   descartadas: 12 193
  descartes:  favorecido_pessoa_fisica 11 497 · favorecido_empresario_individual 504
              favorecido_nao_identificado 180 · unidade_gestora_sem_cnpj 11 · outros 1
  mudanças de fase: 37   sugestões novas: 4   alertas na fila: 9
  duração: download 8,1 s · leitura 21,4 s · normalização 3,2 s · publicação 6,7 s
OK
```

`--json` devolve o mesmo conteúdo no schema `Importacao` de `openapi.yaml`, mais `alertas_enfileirados`.

## `cli:importacoes` — `rastro importacoes`

`rastro importacoes [--limite N] [--json]`: lista as importações com status, datas, contagens e motivo de falha. Mesma informação de `listar_importacoes`.

## `cli:sugestoes` — `rastro sugestoes`

```
rastro sugestoes listar [--status pendente|relacionadas|distintas] [--municipio <ibge>] [--json]
rastro sugestoes revisar <id> --decisao relacionadas|distintas --revisor <nome>
```

`listar` mostra, por sugestão: os dois CNPJs, as razões sociais, o município, a `confianca`, a `origem` e o total recebido por cada CNPJ (separados). `revisar` grava decisão, revisor e data e não altera nenhum total (REQ-38). Revisar uma sugestão já revisada pede `--forcar`.

## `cli:traducao` — `rastro traducao`

`rastro traducao carregar <csv>`: CSV UTF-8 com `fase;texto_simples;termo_oficial;explicacao;fonte_definicao`. Cria versão nova e a torna vigente (REQ-32). Fase faltando ou fonte vazia → código 3 (REQ-33).
`rastro traducao listar`: versões e qual é a vigente.

## `cli:alertas` — `rastro alertas`

`rastro alertas despachar [--workers N]`: processo de longa duração que consome a fila (REQ-67–69). Ao iniciar, reenfileira `pendente` e `enviando` (REQ-69).
`rastro alertas status`: contagem por status da última importação.
