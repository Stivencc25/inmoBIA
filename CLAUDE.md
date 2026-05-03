# CLAUDE.md — inmoBIA

Contexto para Claude Code al trabajar en este repositorio.

## Proyecto

**inmoBIA** es una plataforma inmobiliaria con IA para el mercado latinoamericano.
Combina gestión tradicional de propiedades (listings, agentes, CRM) con IA generativa
(valuación automática, chatbot, búsqueda semántica, generación de contenido).

Rama principal de desarrollo: `predevelop`. Nunca hacer push directo a `main`.

## Stack técnico

- **Frontend**: Next.js 15 (App Router), TypeScript 5, Tailwind CSS 4, shadcn/ui, Zustand, TanStack Query v5
- **Backend**: Hono.js en Node.js 22, validación con Zod
- **DB**: PostgreSQL 16 via Supabase, ORM: Drizzle, extensiones: pgvector + PostGIS
- **Auth**: Better Auth (email/password + Google OAuth)
- **IA**: Anthropic SDK (claude-sonnet-4-6 / claude-opus-4), Vercel AI SDK para streaming
- **Embeddings**: Voyage-3
- **ML**: FastAPI (Python) + XGBoost para AVM (Automated Valuation Model)
- **Colas**: BullMQ + Redis (Upstash)
- **Storage**: Cloudflare R2 (S3-compatible)
- **Monorepo**: Turborepo + pnpm workspaces

## Estructura de apps

```
apps/web/     → Next.js. Rutas: (public), (auth), (dashboard), (portal)
apps/api/     → Hono.js. Módulos en src/modules/<nombre>/
apps/ml/      → FastAPI Python. AVM y servicios ML
```

## Comandos frecuentes

```bash
pnpm dev              # todos los servicios en paralelo
pnpm build            # build producción
pnpm lint             # ESLint en todo el repo
pnpm typecheck        # tsc --noEmit
pnpm test             # vitest
pnpm db:push          # aplica schema Drizzle a la DB
pnpm db:generate      # genera archivos de migración
pnpm db:studio        # Drizzle Studio en localhost
```

## Convenciones de código

- TypeScript estricto (`strict: true`). No usar `any`.
- Schemas Zod en `packages/shared/src/schemas/` — se reutilizan en frontend y backend.
- Módulos en Hono: cada módulo tiene `router.ts`, `service.ts`, `schema.ts` y `types.ts`.
- Componentes React en PascalCase. Hooks con prefijo `use`.
- Variables de entorno accedidas solo via el helper validado en `packages/shared/src/env.ts`.
- Commits en inglés usando Conventional Commits: `feat:`, `fix:`, `chore:`, `docs:`.

## Módulos de negocio

`listings` | `agents` | `clients` | `search` | `ai-valuation` | `ai-recommendations` | `ai-chat` | `market-analytics` | `visits` | `notifications` | `media` | `auth`

## Variables de entorno requeridas

Ver `.env.example` para la lista completa. Las más críticas:
- `DATABASE_URL` — PostgreSQL connection string (Supabase)
- `ANTHROPIC_API_KEY` — para Claude y generación de contenido
- `BETTER_AUTH_SECRET` — clave de sesiones (mínimo 32 chars)
- `CLOUDFLARE_R2_*` — para upload de fotos/videos

## Decisiones importantes

- **Drizzle sobre Prisma**: permite queries PostGIS y pgvector sin perder typesafety
- **Hono sobre Express**: 2-3x más rápido, tipado nativo, Edge-compatible
- **pgvector sobre Pinecone**: elimina dependencia externa en MVP; migrable después
- **Modelo AVM propio**: LLMs no son confiables para valuación numérica; XGBoost con datos reales es 10x más preciso
