# ADR-0008 · Separar a interface React + Vite da API, com tipos gerados do OpenAPI

- **Status:** aceita
- **Contexto:** O morador usa o celular (FI-01 §3.1); o jornalista quer a API (FI-01 §7). A API precisa de contrato versionado (FI-01 §6). A interface é de consulta e não precisa de renderização no servidor (FI-01 §6).
- **Opções consideradas:**
  1. HTML renderizado pelo FastAPI (Jinja + HTMX).
  2. Next.js com renderização no servidor.
  3. SPA em TypeScript + React (Vite), estática, consumindo a API `/api/v1`, com tipos gerados de `contratos/openapi.yaml` (`openapi-typescript`).
- **Decisão:** Opção 3. A API é a única porta de dados; a interface não tem regra de fase nem texto de tradução (REQ-31). O CI falha se os tipos gerados divergirem do contrato (QA-02).
- **Consequências:**
  - \+ A mesma API serve a interface e o jornalista.
  - \+ A interface é servida como arquivos estáticos.
  - − Sem JavaScript, a interface não funciona. Aceito: o público usa navegador moderno; a API continua acessível.
  - Opção 1 descartada: o autor tem mais domínio em React e quer os tipos do contrato no front. Opção 2 descartada: servidor Node só para renderizar páginas de consulta.
