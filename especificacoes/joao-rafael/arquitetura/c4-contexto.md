# C4 · Nível 1 — Contexto (arc42 §3)

```mermaid
C4Context
    title Rastro — contexto do sistema

    Person(morador, "Morador", "Município da PB; celular; consulta ocasional")
    Person(jornalista, "Jornalista / controle social", "Desktop; rastreia valores e cita a fonte; usa a API")
    Person(gestor, "Gestor municipal", "Desktop; acompanha o empenhado e não pago da cidade")
    Person(operador, "Operador de dados", "Terminal; importa, revisa sugestões e carrega a tradução")

    System(rastro, "Rastro", "Importa emendas e pagamentos da PB, traduz a fase, mostra quem recebeu e avisa quando a fase muda")

    System_Ext(cgu, "Portal da Transparência (CGU)", "Zip único de emendas, atualizado diariamente")
    System_Ext(ibge, "IBGE", "Lista dos 223 municípios da PB (semente)")
    System_Ext(smtp, "Serviço de e-mail (SMTP)", "Entrega a confirmação e os alertas")
    System_Ext(mto, "Glossário do Portal / MTO", "Definição oficial de cada fase")

    Rel(morador, rastro, "Busca a cidade, lê a fase", "HTTPS")
    Rel(jornalista, rastro, "Consulta, compara, exporta", "HTTPS, JSON")
    Rel(gestor, rastro, "Consulta e assina alerta", "HTTPS")
    Rel(operador, rastro, "rastro importar, sugestoes, traducao", "CLI")
    Rel(rastro, cgu, "GET condicional do zip", "HTTPS, If-None-Match")
    Rel(rastro, ibge, "Carrega municípios", "arquivo, uma vez")
    Rel(rastro, smtp, "Envia e-mails", "SMTP/TLS")
    Rel(smtp, gestor, "Entrega alerta", "e-mail")
    Rel(jornalista, cgu, "Confere na fonte", "link da proveniência")
    UpdateLayoutConfig($c4ShapeInRow="4", $c4BoundaryInRow="1")
```

## Atores e vizinhos

| Elemento | Tipo | Relação | Telas |
| :-- | :-- | :-- | :-- |
| Morador | pessoa | consulta sem conta; e-mail só para alerta | P01, P02, P04, P05, P10, S01–S03 |
| Jornalista / controle social | pessoa | consulta, compara, exporta, usa a API, assina | P01–P10, S01–S03 |
| Gestor municipal | pessoa | acompanha a cidade e assina | P02, P03, P04, S01–S03 |
| Operador de dados | pessoa | roda a CLI | O01, O02, P09, P10 |
| Portal da Transparência | sistema externo | única fonte de dados do MVP; se cair, a vigente anterior continua (REQ-15) | — |
| IBGE | sistema externo | semente de municípios | — |
| Serviço SMTP | sistema externo | entrega; falha vira nova tentativa (REQ-68) | S03 |
| Glossário / MTO | documento externo | citado em `TraducaoFase.fonte_definicao`, não copiado | P10 |

## Afetados que não são usuários (FI-01 §3.2)

| Quem | Requisitos e ADRs que o protegem |
| :-- | :-- |
| Parlamentar autor | REQ-30, REQ-31, REQ-52, REQ-82, ADR-0005 |
| Entidade favorecida | REQ-21, REQ-37, REQ-39, ADR-0001 |
| Pessoa física na fonte | REQ-16, REQ-17, REQ-26, ADR-0004 |
| Município com dado sujo | REQ-40, REQ-55, ADR-0009 |

## Limites

- **Dentro:** download e importação, normalização, descartes, proveniência, fase e tradução, mudanças entre importações, sugestões de mesma entidade, API de leitura, interface, assinaturas e e-mail.
- **Fora (FI-01 §5):** emendas estaduais e municipais; municípios fora da PB; mérito, nota ou ranking de parlamentar; execução física de obra; fusão de CNPJs diferentes; dado de pessoa física; cadastro além do e-mail; Siga Brasil.
