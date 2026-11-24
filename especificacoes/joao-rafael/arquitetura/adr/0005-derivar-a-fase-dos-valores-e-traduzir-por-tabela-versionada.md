# ADR-0005 · Derivar a fase dos valores e traduzi-la por tabela versionada

- **Status:** aceita (texto simples em versão 1, aguardando revisão de alguém da área de orçamento, FI-01 §12)
- **Contexto:** O morador não entende "empenhado, liquidado, pago" (FI-01 §2.1). Uma tradução errada afirma que um parlamentar não executou o que executou (FI-01 §3.2), e uma tradução simples demais faz ler "desvio" onde há atraso normal (FI-01 §8.4). A análise do arquivo real feita pela Sarah (27/10/2026) mostrou que `Valor Pago` só registra o pago no ano do empenho e que o pago depois vem em `Valor Restos A Pagar Pagos`.
- **Opções consideradas:**
  1. Fase pela coluna de maior etapa preenchida, texto no código.
  2. Texto gerado por modelo de linguagem a cada emenda.
  3. Fase derivada por regra pura dos valores, com restos a pagar, e texto numa tabela `TraducaoFase` versionada, com o termo oficial e a fonte da definição.
- **Decisão:** Opção 3. Com `valor_final = empenhado − rp_cancelado` e `pago_total = pago + rp_pago` (REQ-30):

  | Fase | Condição |
  | :-- | :-- |
  | `sem_empenho` | `empenhado = 0` |
  | `cancelada` | `empenhado > 0` e `valor_final ≤ 0` |
  | `empenhada` | `valor_final > 0`, `liquidado = 0` e `pago_total = 0` |
  | `liquidada` | `liquidado > 0` e `pago_total = 0` |
  | `paga_em_parte` | `0 < pago_total < valor_final` |
  | `paga` | `pago_total ≥ valor_final > 0` |

  A tabela traz `texto_simples`, `termo_oficial`, `explicacao` e `fonte_definicao` por fase, numa versão imutável (REQ-32, REQ-33). A interface mostra os dois termos e a versão (REQ-31) e explica cada fase em P10.
- **Consequências:**
  - \+ Corrigir uma tradução é carregar uma versão nova, sem deploy.
  - \+ A regra é testável com linhas reais (`test_fase.py`).
  - − A fase descreve o dinheiro, não a obra. O aviso do REQ-83 diz isso em toda tela.
  - Opção 1 descartada: classifica como "reservado" o que já foi pago em restos a pagar. Opção 2 descartada: textos diferentes para a mesma fase e nenhuma fonte.
