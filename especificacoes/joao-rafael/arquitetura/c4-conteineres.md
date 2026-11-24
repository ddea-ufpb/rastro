# C4 · Nível 2 — Contêineres (arc42 §5)

```mermaid
C4Container
    title Rastro — contêineres

    Person(usuario, "Morador, jornalista, gestor")
    Person(operador, "Operador de dados")

    System_Boundary(rastro, "Rastro") {
        Container(web, "Interface", "TypeScript, React, Vite", "SPA estática; tipos gerados do OpenAPI; sem regra de fase")
        Container(api, "API", "Python 3.12, FastAPI", "/api/v1, leitura em REPEATABLE READ, limite por IP")
        Container(cli, "CLI rastro", "Python 3.12, asyncio, httpx", "importar, sugestoes, traducao, importacoes")
        Container(desp, "Despachante de alertas", "Python 3.12, asyncio", "rastro alertas despachar; fila e workers")
        ContainerDb(db, "Banco", "PostgreSQL 16", "importações, emendas, pagamentos, favorecidos, tradução, assinaturas")
        ContainerDb(bruto, "Arquivos brutos", "disco local", "bruto/emendas-<data>.zip; fora do Git")
    }

    System_Ext(cgu, "Portal da Transparência")
    System_Ext(smtp, "SMTP")

    Rel(usuario, web, "Usa", "HTTPS")
    Rel(web, api, "Chama", "JSON")
    Rel(usuario, api, "Jornalista chama direto", "JSON")
    Rel(operador, cli, "Executa", "terminal")
    Rel(cli, cgu, "Baixa", "HTTPS")
    Rel(cli, bruto, "Guarda e lê", "arquivo")
    Rel(cli, db, "Escritor único da publicação", "SQL")
    Rel(api, db, "Lê; grava só assinaturas", "SQL")
    Rel(desp, db, "Lê alertas, marca status", "SQL")
    Rel(desp, smtp, "Envia", "SMTP/TLS")
    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

## Quem escreve onde

| Contêiner | Escreve | Só lê |
| :-- | :-- | :-- |
| CLI `rastro importar` | `Importacao`, `ImportacaoVigente`, `Emenda`, `Autor`, `Pagamento`, `Favorecido`, `NomeFavorecido`, `Descarte`, `MudancaFase`, `SugestaoMesmaEntidade`, `AlertaEnviado` (criação) | `Assinatura` |
| CLI `rastro sugestoes` / `traducao` | `SugestaoMesmaEntidade.status`, `VersaoTraducao`, `TraducaoFase` | — |
| API | `Assinatura` (criar, confirmar, apagar) | o resto |
| Despachante | `AlertaEnviado.status`, `tentativas`, `enviado_em` | `Assinatura`, `MudancaFase`, `Emenda` |
| Interface | nada | tudo pela API |

A API nunca escreve dado de fonte. Só a CLI de importação abre a transação de publicação, sob `pg_advisory_lock` (ADR-0002, ADR-0007).

## Implantação (arc42 §7, mínima)

Docker Compose com `db` (PostgreSQL 16), `api` (uvicorn), `web` (arquivos estáticos servidos por nginx), `despachante` e `mailpit` (só em desenvolvimento). A CLI roda com `docker compose run --rm cli rastro importar --baixar`, agendada uma vez por dia. CI no GitHub Actions com PostgreSQL de serviço. Hospedagem fora do Compose local: a definir com o grupo (FI-01 §6, "Supabase se precisar").
