# ADR-0007 · Usar asyncio com escritor único na importação e fila no envio de alertas

- **Status:** aceita (prototipar isolado antes de ligar ao banco, FI-01 §6.2)
- **Contexto:** O trabalho concorrente do Rastro é I/O (FI-01 §7.1): (a) baixar e ler vários arquivos da mesma importação; (b) consultar enquanto uma importação é gravada; (c) enviar muitos e-mails depois de uma importação. Recursos compartilhados: a linha do favorecido (o mesmo CNPJ chega por mais de um arquivo), o ponteiro da importação vigente e o registro de alerta enviado.
- **Opções consideradas:**
  1. Threads gravando direto no banco, cada uma com sua conexão.
  2. Broker externo (Redis, RabbitMQ) com workers.
  3. `asyncio` + `httpx`: workers leem e normalizam em paralelo e entregam lotes de linhas a um único escritor por uma `asyncio.Queue`; o escritor faz `INSERT … ON CONFLICT (cnpj) DO UPDATE` dentro da transação de publicação. No envio, workers `asyncio` consomem uma fila de alertas e marcam cada um com `UPDATE … WHERE status = 'pendente'`.
- **Decisão:** Opção 3 (REQ-14, REQ-67).
  - Segurança: dois favorecidos com o mesmo CNPJ são impossíveis pelo `UNIQUE` (REQ-21); a consulta nunca vê meia importação pelo ADR-0002; o mesmo alerta não sai duas vezes pelo `UNIQUE` da tripla e pela troca de estado condicional (REQ-65, REQ-69).
  - Vivacidade: toda importação termina `publicada` ou `falhou` dentro do tempo-limite (REQ-11, REQ-12); todo alerta termina `enviado` ou `falhou` após 3 tentativas (REQ-68).
  - O número de workers de leitura é parâmetro (`--workers 1|2|4`) para a medição do FI-01 §7.2 (REQ-86).
- **Consequências:**
  - \+ Nenhum processo extra no MVP; tudo cabe no Docker Compose.
  - \+ O escritor único elimina o upsert concorrente pelo mesmo CNPJ dentro da importação; o `ON CONFLICT` cobre o caso entre importações.
  - − asyncio é o ponto de menor domínio do autor (FI-01 §6.2). Mitigação: protótipo isolado com testes de propriedade antes da fatia que liga ao banco.
  - Opção 1 descartada: upsert concorrente pelo mesmo CNPJ exige tratar deadlock. Opção 2 descartada: um broker para um volume que cabe na memória.
