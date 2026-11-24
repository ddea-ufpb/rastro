# ADR-0003 · Exigir proveniência em todo registro e devolvê-la na API

- **Status:** aceita
- **Contexto:** A aposta central do FI-01 (§4.4) é que toda afirmação exibida pode ser rastreada até a linha do arquivo oficial. Proveniência opcional acaba vazia.
- **Opções consideradas:**
  1. Proveniência só no nível da importação (um arquivo, uma data).
  2. Proveniência por registro, guardada mas não exposta.
  3. Proveniência por registro, `NOT NULL` no schema, devolvida junto de cada valor.
- **Decisão:** Opção 3. `Emenda`, `Pagamento` e `Favorecido` têm `fonte`, `arquivo`, `linha` e `extraido_em` `NOT NULL` (REQ-28). Todo valor monetário da API vem num objeto `ValorComProveniencia` (REQ-29). A interface mostra a faixa de proveniência em toda tela (REQ-75) e a origem de cada valor a um toque.
- **Consequências:**
  - \+ Um insert sem fonte falha no banco, sem depender de revisão de código (FI-01 §11.3, tarefa "Schema inicial").
  - \+ O jornalista cita "arquivo X, linha N, extraído em dd/mm".
  - − As respostas ficam maiores. Aceito: o volume da PB é pequeno.
  - Opção 1 descartada: não diz de qual linha veio um pagamento. Opção 2 descartada: o usuário não confere o que não vê.
