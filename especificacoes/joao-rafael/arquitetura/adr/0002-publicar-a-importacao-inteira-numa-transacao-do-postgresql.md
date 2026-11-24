# ADR-0002 · Publicar a importação inteira numa transação do PostgreSQL

- **Status:** aceita
- **Contexto:** Uma consulta nunca pode ver uma importação pela metade, com parte dos pagamentos novos e parte antigos (FI-01 §7.1). Importar o mesmo arquivo duas vezes não pode duplicar nada (AC-1). Uma importação com erro não pode tirar do ar a anterior.
- **Opções consideradas:**
  1. Apagar e regravar as tabelas no lugar.
  2. Tabelas de staging e `RENAME` no fim.
  3. Gravar cada importação com `importacao_id` e trocar o ponteiro `ImportacaoVigente` na mesma transação que grava os registros.
- **Decisão:** Opção 3. A importação lê e normaliza fora da transação; o escritor único abre uma transação, grava todos os registros com o `importacao_id`, calcula as mudanças (ADR-0006), marca a importação como `publicada`, atualiza `ImportacaoVigente` e só então faz `COMMIT` (REQ-09). As consultas leem em `REPEATABLE READ` e filtram pela vigente lida no início (REQ-10, REQ-13). Falha em qualquer validação (REQ-07, REQ-08) termina em `falhou` sem tocar na vigente. O `sha256` do arquivo impede reimportar o mesmo arquivo (REQ-05), e `chave_pagamento` impede duplicar dentro da importação (REQ-06).
- **Consequências:**
  - \+ Leitores nunca bloqueiam e nunca veem mistura: o MVCC do PostgreSQL entrega o snapshot.
  - \+ Voltar à importação anterior é trocar o ponteiro.
  - − O banco guarda várias importações. Com 31 840 linhas no recorte (T2), cada importação ocupa poucos MB; a retenção fica para quando a feature 5 entrar (FI-01 §12).
  - − A transação de publicação é longa (todas as linhas). Medida em QA-01 e QA-03.
  - Opção 1 descartada: o leitor vê tabela vazia. Opção 2 descartada: `RENAME` pede trava exclusiva e complica o cálculo de mudanças entre importações.
