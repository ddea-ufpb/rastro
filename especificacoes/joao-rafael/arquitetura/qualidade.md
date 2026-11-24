# Cenários de qualidade (arc42 §10)

Formato de 6 partes (Bass, Clements e Kazman). Um cenário por item do envelope não funcional da disciplina (FI-01 §7). Valores entre ⟨ ⟩ são metas provisórias: o FI-01 (§7.2) proíbe fixar meta antes do baseline. O primeiro passo de QA-04 é medir e revisar ⟨ ⟩.

Entrada fixa de todos os cenários: o zip de 22/11/2026 (`sha256 221c0a3e…`) e uma amostra reduzida dele em `tests/dados/amostra.zip`, com pelo menos uma linha de cada motivo de descarte do `fonte-portal.md`.

## QA-01 · Persistência — falha da importação não corrompe nem esconde dados

| Parte | Conteúdo |
| :-- | :-- |
| Fonte | Operador ou agendador rodando `rastro importar` |
| Estímulo | (a) `SIGKILL` no meio da transação de publicação; (b) zip com uma coluna renomeada; (c) zip com 5% das linhas com valor fora do formato; (d) mesmo zip importado duas vezes |
| Ambiente | Importação vigente anterior existe |
| Artefato | `rastro importar`, tabelas `Importacao`, `ImportacaoVigente`, `Pagamento`, `Favorecido` |
| Resposta | (a) na execução seguinte, `falhou`/`interrompida` (REQ-11); (b) `falhou`/`formato_alterado` (REQ-07); (c) `falhou`/`descartes_acima_do_limite` (REQ-08); (d) "arquivo já importado" (REQ-05). Em todos, a vigente continua a anterior |
| Medida | Em 20 execuções por estímulo: 0 linhas da importação falha visíveis pela API; contagens de `Pagamento` e `Favorecido` iguais antes e depois; em (d), contagens iguais após a 1ª e a 2ª execução (AC-1) |

Requisitos: REQ-05, REQ-07, REQ-08, REQ-09, REQ-11, REQ-28. Teste: `modulos/ingestao/tests/test_falhas.py`.

## QA-02 · API com contrato — respostas sempre válidas contra o OpenAPI

| Parte | Conteúdo |
| :-- | :-- |
| Fonte | Cliente da API (interface, jornalista, teste gerado) |
| Estímulo | Requisições a todas as operações de `openapi.yaml`, com parâmetros válidos e inválidos gerados por Schemathesis |
| Ambiente | Banco com a amostra publicada |
| Artefato | `/api/v1/*`, `/openapi.json`, tipos TypeScript gerados |
| Resposta | Status e corpo conformes ao schema; erros em `problem+json` com `codigo` (REQ-59); todo valor monetário com proveniência (REQ-29) |
| Medida | 0 violações em ⟨200⟩ casos por operação; diff entre `/openapi.json` e `contratos/openapi.yaml` vazio no CI; `openapi-typescript` sem diff nos tipos versionados |

Requisitos: REQ-29, REQ-44, REQ-57, REQ-59. Teste: `modulos/consulta/tests/test_contrato.py`.

## QA-03 · Concorrência — segurança e vivacidade da importação e dos alertas

| Parte | Conteúdo |
| :-- | :-- |
| Fonte | Importação com 4 workers, 20 clientes consultando e o despachante de alertas com 4 workers |
| Estímulo | (a) consultas contínuas durante a publicação; (b) o mesmo CNPJ chegando por linhas processadas por workers diferentes; (c) 500 assinaturas × 300 mudanças, com o despachante morto e reiniciado no meio |
| Ambiente | Importação vigente anterior com contagens conhecidas |
| Artefato | escritor único, `ON CONFLICT (cnpj)`, `UNIQUE` de `AlertaEnviado`, fila `asyncio.Queue` |
| Resposta | (a) cada resposta tem só dados da vigente anterior ou só da nova (REQ-10); (b) um favorecido por CNPJ (REQ-21); (c) cada tripla (assinatura, emenda, importação) enviada uma vez; todo alerta termina `enviado` ou `falhou` (REQ-65, REQ-68, REQ-69) |
| Medida | Em 100 execuções: 0 respostas com mistura (conferido pelo `importacao_id` de cada valor); 0 CNPJs duplicados; 0 e-mails duplicados no Mailpit; 0 alertas em `pendente` ou `enviando` 60 s depois de a fila esvaziar |

Requisitos: REQ-10, REQ-14, REQ-21, REQ-65, REQ-66, REQ-67, REQ-68, REQ-69. Testes: `modulos/ingestao/tests/test_concorrencia.py`, `modulos/saida/tests/test_despachante.py`.

## QA-04 · Desempenho medido — importação e consulta agregada

| Parte | Conteúdo |
| :-- | :-- |
| Fonte | (a) operador; (b) k6 |
| Estímulo | (a) `rastro importar --arquivo` do zip completo com `--workers 1`, `2` e `4`, 5 vezes cada; (b) `obter_agregacoes` (os três eixos) e `obter_municipio` (10 municípios) com ⟨20⟩ VUs por 60 s |
| Ambiente | Docker Compose local, máquina de 8 GB de RAM (FI-01 §10.3), banco com a importação completa |
| Artefato | `rastro importar`, `/api/v1/agregacoes`, `/api/v1/municipios/{codigo_ibge}` |
| Resposta | Duração por etapa gravada (REQ-85); p50, p95 e p99 do k6 |
| Medida | Baseline primeiro. Metas provisórias: (a) ≤ ⟨5 min⟩ e pico de memória ≤ ⟨512 MB⟩ (REQ-88); (b) p95 < ⟨300 ms⟩ e 0% de erro (REQ-87). `EXPLAIN ANALYZE` anexado para as consultas acima de 100 ms |

Requisitos: REQ-85, REQ-86, REQ-87, REQ-88. Scripts: `perf/importacao.py`, `perf/consulta.k6.js`.

## QA-05 · Testes — cada regra com o registro real que a motivou

| Parte | Conteúdo |
| :-- | :-- |
| Fonte | Desenvolvedor ou agente abrindo um PR |
| Estímulo | Mudança em normalização, fase, tradução ou alertas |
| Ambiente | CI no GitHub Actions |
| Artefato | `pytest` (back-end), Vitest e Playwright + axe (interface) |
| Resposta | Cada regra de `fonte-portal.md` e do ADR-0005 tem um teste com a linha real que a motivou (FI-01 §6); os AC-1 a AC-3 rodam como testes de integração com PostgreSQL real |
| Medida | 100% das regras R-* e das 6 fases com teste nomeado; cobertura de linha ≥ ⟨80%⟩ em `ingestao` e `nucleo`; 0 violações do axe (REQ-80); o CI falha se qualquer um cair |

Requisitos: REQ-16–26, REQ-30, REQ-80, REQ-82.
