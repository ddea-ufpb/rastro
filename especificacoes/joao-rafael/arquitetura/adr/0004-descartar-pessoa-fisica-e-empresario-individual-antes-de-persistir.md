# ADR-0004 · Descartar pessoa física e empresário individual antes de persistir

- **Status:** aceita (revista em 22/11/2026 com a coleta do Trabalho 2)
- **Contexto:** Nada na finalidade do Rastro precisa de nome ou CPF de pessoa (FI-01 §8.1). O FI-01 deixou em aberto se MEI com nome de pessoa conta como pessoa física (§8.5, §12). A coleta do Trabalho 2 respondeu: das 190 entidades com natureza `Empresário (Individual)` no recorte, 17 tinham o CPF inteiro no nome. A fonte também traz `Unidade Gestora` (sem CNPJ) e `Inscrição Genéric` (nome de pessoa estrangeira).
- **Opções consideradas:**
  1. Guardar a pessoa física com o nome mascarado.
  2. Agregar pessoas físicas numa linha "pessoas físicas" por emenda.
  3. Descartar pessoa física, empresário individual e tipos sem CNPJ antes de persistir, guardando só arquivo, linha, motivo e município.
- **Decisão:** Opção 3, com um motivo por caso (REQ-16 a REQ-20). O `Descarte` não tem coluna de nome nem de CPF (REQ-26). O zip original fica fora do Git e fora do banco, só no disco do operador.
- **Consequências:**
  - \+ O schema não tem onde guardar dado pessoal: a minimização é estrutural.
  - \+ A contagem de descartes por emenda e por município continua visível (REQ-47, ADR-0009), então o valor pago a pessoas não some sem explicação.
  - − A soma recebida por favorecidos fica menor que o pago da emenda quando há pagamento a pessoas. A tela P05 mostra a diferença como "pagamentos a pessoas físicas ou sem CNPJ, não exibidos".
  - − Diverge do contrato da Sarah, que põe empresário individual em `entidade_privada`. Proposto ao grupo.
  - Opção 1 descartada: nome mascarado ainda identifica em município pequeno. Opção 2 descartada: guardaria a linha da pessoa para agregar.
