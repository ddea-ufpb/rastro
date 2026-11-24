# Rastro — painel web

Next.js (App Router) + TypeScript strict + shadcn/ui. Gerenciador: pnpm (versão em `package.json#packageManager`); Node em `../.nvmrc`.

```bash
export NEXT_TELEMETRY_DISABLED=1   # o projeto não envia telemetria
pnpm install --frozen-lockfile
pnpm dev        # http://localhost:3000
pnpm lint && pnpm typecheck && pnpm build
```
