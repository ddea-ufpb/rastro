# ADR-0009 · Expor os descartes por município junto do resultado

- **Status:** aceita
- **Contexto:** Um município com dado sujo pode aparecer como "sem emendas" ou "nada recebido" porque o sistema descartou o que não conseguiu ler, e some do radar de quem fiscaliza (FI-01 §3.2, §8.4). Na coleta do Trabalho 2, 12 193 linhas de pagamento do recorte foram descartadas, a maior parte (11 497) por pessoa física.
- **Opções consideradas:**
  1. Contar descartes só no relatório da importação.
  2. Contar descartes por município e mostrá-los junto do resultado do município, da emenda e da importação.
- **Decisão:** Opção 2. Cada `Descarte` guarda `municipio_ibge` quando a linha o tem (REQ-26). P02 mostra "N linhas da fonte ligadas a esta cidade não entraram", com os motivos; P05 mostra os descartes da emenda; P09 mostra por motivo e por município (REQ-40, REQ-47, REQ-55).
- **Consequências:**
  - \+ "Zero" na tela nunca esconde uma linha descartada.
  - \+ O operador vê se um município concentra descartes, sinal de regra errada.
  - − Descarte sem município (UF `-1`, 65 linhas no T2) só aparece em P09.
  - Opção 1 descartada: o morador não abre relatório de importação.
