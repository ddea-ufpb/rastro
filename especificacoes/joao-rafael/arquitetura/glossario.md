# Glossário (arc42 §12)

Termos do domínio e do sistema, como usados na especificação. Termos de orçamento citam a fonte oficial que a tabela de tradução também cita (ADR-0005).

## Domínio (orçamento e fonte)

| Termo | Definição | Fonte |
| :-- | :-- | :-- |
| Emenda parlamentar | Indicação de um parlamentar, bancada ou comissão para destinar parte do orçamento federal. Identificada pelo código de 12 dígitos | Portal da Transparência, glossário |
| Autor | Quem indicou a emenda: parlamentar, bancada, comissão ou relator | Portal da Transparência |
| Empenho / empenhado | Reserva do dinheiro no orçamento para uma despesa. Não é pagamento | Manual Técnico de Orçamento (MTO) |
| Liquidação / liquidado | Conferência de que o bem ou serviço foi entregue, antes de pagar | MTO |
| Pagamento / pago | Saída do dinheiro para o favorecido. Na fonte, `Valor Pago` só conta o pago no ano do empenho | MTO; análise da Sarah (27/10/2026) |
| Restos a pagar (RP) | Despesa empenhada num ano e não paga até o fim dele. Pode ser paga (`rp_pago`) ou cancelada (`rp_cancelado`) depois | MTO |
| Favorecido | Quem recebeu um pagamento. No Rastro, só pessoa jurídica com CNPJ (ADR-0004) | Portal da Transparência |
| Natureza jurídica | Tipo da pessoa jurídica (município, autarquia, fundação, associação…), como publicado | Receita Federal / Portal |
| CNPJ raiz | Os 8 primeiros dígitos do CNPJ: a mesma pessoa jurídica, com filiais | Receita Federal |
| Localidade de aplicação | Texto da fonte sobre onde o recurso será aplicado; pode ser um município, o estado ou `MÚLTIPLO` | Portal da Transparência |

## Sistema

| Termo | Definição | Onde |
| :-- | :-- | :-- |
| Importação | Uma execução de `rastro importar` sobre um zip; termina `publicada` ou `falhou` | `contratos/cli.md`, ADR-0002 |
| Importação vigente | A importação publicada que as consultas leem, apontada por `ImportacaoVigente` | ADR-0002 |
| Recorte | Linhas com emenda da PB ou favorecido da PB | REQ-04 |
| Descarte | Linha do recorte que não entra, com motivo, arquivo, linha e município; sem dado pessoal | REQ-26, ADR-0004 |
| Proveniência | Fonte, arquivo, linha, data de extração e importação de um valor | ADR-0003 |
| Fase | Situação do dinheiro de uma emenda, derivada dos valores (`sem_empenho`, `cancelada`, `empenhada`, `liquidada`, `paga_em_parte`, `paga`) | ADR-0005 |
| Valor final | `empenhado − rp_cancelado` | ADR-0005 |
| Pago total | `pago + rp_pago` | ADR-0005 |
| Texto simples | A frase que traduz a fase para quem não é da área; vem da tabela, nunca do código | ADR-0005 |
| Termo oficial | O nome técnico da fase, mostrado ao lado do texto simples | ADR-0005 |
| Mudança de fase | Emenda cuja fase na nova importação é diferente da vigente anterior | REQ-34 |
| Sugestão de mesma entidade | Par de CNPJs de raízes diferentes com nome parecido no mesmo município; revisável, nunca somado | ADR-0001 |
| Destinado à cidade | Emendas cujo destino é o município | ADR-0010 |
| Recebido por entidades da cidade | Pagamentos a favorecidos sediados no município, de qualquer emenda | ADR-0010 |
| Assinatura | E-mail + filtro (município ou parlamentar); `pendente` até confirmar | ADR-0006 |
| Alerta | Aviso de mudança de fase para uma assinatura; um por (assinatura, emenda, importação) | REQ-65 |
| Token de gestão | Segredo do link "Gerenciar ou cancelar", no fragmento da URL | REQ-72 |
| Ação local | Ação da interface sem chamada à API (copiar, exportar o já carregado, link externo) | REQ-81 |
