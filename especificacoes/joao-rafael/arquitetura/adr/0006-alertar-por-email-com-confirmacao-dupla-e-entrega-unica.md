# ADR-0006 · Alertar por e-mail com confirmação dupla e entrega única por mudança

- **Status:** aceita
- **Contexto:** O alerta tira do usuário o trabalho de voltar e comparar à mão (FI-01 §4.3). O FI-01 escolheu o e-mail como único dado pessoal (§8.1) e exige zero alertas duplicados para o mesmo assinante e mudança (§10.1). Sem confirmação, qualquer pessoa assinaria alertas no e-mail de outra.
- **Opções consideradas:**
  1. Conta com senha.
  2. Chave anônima mostrada na tela, sem e-mail (alerta só no painel).
  3. E-mail com confirmação dupla; link de gestão com token; uma linha `AlertaEnviado` por (assinatura, emenda, importação).
- **Decisão:** Opção 3.
  - A assinatura nasce `pendente` e só vira `ativa` pelo link de confirmação, de uso único e válido por 48 h (REQ-61, REQ-63, REQ-64).
  - O link de gestão leva o token no fragmento (`/alertas/minha#t=…`), que o navegador não envia ao servidor; a interface o manda no cabeçalho `X-Token-Assinatura` (REQ-72). Assim o token não aparece em log de servidor nem em `Referer`.
  - A resposta a um pedido de assinatura é sempre 202, exista ou não assinatura para aquele e-mail (REQ-73), com limite de pedidos por e-mail (REQ-74).
  - As mudanças vêm das `MudancaFase` calculadas na publicação (REQ-34). Cada par (assinatura, emenda) gera um `AlertaEnviado` com `UNIQUE (assinatura_id, emenda_codigo, importacao_id)` (REQ-65), e um único e-mail por assinatura e importação junta todas as mudanças (REQ-66).
  - Cancelar apaga o e-mail, as assinaturas e os alertas (REQ-70).
- **Consequências:**
  - \+ A duplicata é barrada pelo banco, não pela lógica do despachante (QA-03).
  - \+ Nenhum dado pessoal além do e-mail; nenhuma senha para vazar.
  - − Depende de um serviço SMTP. Em desenvolvimento, Mailpit no Docker Compose.
  - Opção 1 descartada: mais dado guardado e mais atrito (FI-01 §5). Opção 2 descartada: o gestor quer o aviso sem abrir o painel.
