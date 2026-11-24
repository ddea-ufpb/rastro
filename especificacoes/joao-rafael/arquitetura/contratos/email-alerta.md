# Contrato dos e-mails

Dois e-mails, enviados por SMTP (Mailpit em desenvolvimento). Texto simples e HTML com o mesmo conteúdo; o HTML não depende de imagem. Remetente fixo `Rastro <alertas@…>` (domínio a definir com a hospedagem). Sem pixel de rastreio nem link encurtado.

## `email:confirmacao`

Enviado por `criar_assinatura` (REQ-61).

| Parte | Conteúdo |
| :-- | :-- |
| Assunto | "Confirme seu alerta do Rastro: <município ou parlamentar>" |
| Corpo | O que foi pedido (filtro), o que o alerta faz ("um e-mail quando a fase de uma emenda mudar entre importações"), o link `/alertas/confirmar#t=<token>` e "Se não foi você, ignore este e-mail. Nada será enviado sem a confirmação." |
| Validade | 48 h, uso único (REQ-63) |

## `email:alerta`

Enviado pelo despachante, no máximo um por assinatura e importação (REQ-66). É a tela S03.

| Parte | Conteúdo |
| :-- | :-- |
| Assunto | "Rastro: N emendas de <filtro> mudaram de fase" |
| Para cada mudança | código da emenda, autor, `texto_simples` anterior → novo com `termo_oficial` entre parênteses (REQ-31), link `/emendas/<codigo>` |
| Rodapé obrigatório | fonte e data da importação ("Portal da Transparência, atualizado em dd/mm/aaaa, importação #n"), aviso do REQ-83, link "Gerenciar ou cancelar" `/alertas/minha#t=<token_gestao>` (REQ-71, REQ-72), cabeçalho `List-Unsubscribe` |
| Proibido | palavras do REQ-82 |
