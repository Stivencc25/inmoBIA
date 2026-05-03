# inmoBIA

Plataforma inmobiliaria potenciada por Inteligencia Artificial. Gestión de propiedades, agentes y clientes con valuación automática, búsqueda semántica y asistente conversacional.

[![CI](https://github.com/Stivencc25/inmoBIA/actions/workflows/ci.yml/badge.svg)](https://github.com/Stivencc25/inmoBIA/actions/workflows/ci.yml)

## Stack

| Capa | Tecnología |
|------|-----------|
| Frontend | Next.js 15 + TypeScript + Tailwind CSS 4 + shadcn/ui |
| Backend API | Hono.js + Node.js 22 |
| Base de datos | PostgreSQL 16 (Supabase) + pgvector + PostGIS |
| ORM | Drizzle ORM |
| Auth | Better Auth |
| IA/LLM | Anthropic Claude (claude-sonnet-4-6) + Vercel AI SDK |
| Embeddings | Voyage-3 |
| ML/AVM | FastAPI (Python) + XGBoost |
| Cache/Colas | Redis (Upstash) + BullMQ |
| Storage | Cloudflare R2 |
| Monorepo | Turborepo + pnpm workspaces |

## Estructura

```
inmoBIA/
├── apps/
│   ├── web/          # Next.js 15 — app principal
│   ├── api/          # Hono.js — API REST
│   └── ml/           # FastAPI — servicio AVM
├── packages/
│   ├── database/     # Drizzle schema + migraciones
│   ├── shared/       # tipos, schemas Zod compartidos
│   ├── ui/           # Design System
│   └── config/       # eslint, tsconfig, tailwind compartidos
├── docs/
│   └── decisions/    # ADRs
└── infra/            # Pulumi IaC
```

## Setup local

### Requisitos
- Node.js 22+
- pnpm 9+
- Docker (para PostgreSQL y Redis locales)

### Instalación

```bash
# Clonar el repositorio
git clone https://github.com/Stivencc25/inmoBIA.git
cd inmoBIA

# Instalar dependencias
pnpm install

# Configurar variables de entorno
cp .env.example .env
# Edita .env con tus credenciales

# Iniciar base de datos local
docker compose up -d

# Aplicar migraciones
pnpm db:push

# Iniciar todos los servicios en desarrollo
pnpm dev
```

### Comandos útiles

```bash
pnpm dev           # Inicia todos los apps en paralelo
pnpm build         # Build de producción
pnpm lint          # Linting en todo el monorepo
pnpm typecheck     # Type checking
pnpm test          # Tests
pnpm db:generate   # Genera migraciones Drizzle
pnpm db:push       # Aplica migraciones
pnpm db:studio     # Abre Drizzle Studio (UI de DB)
```

## Roadmap

- **Fase 0** — Fundamentos: monorepo, CI/CD, DB schema, auth básico
- **Fase 1** — MVP funcional: CRUD propiedades, CRM, visitas, multi-tenancy
- **Fase 2** — IA primera ola: generación de contenido, chatbot, búsqueda semántica
- **Fase 3** — IA segunda ola: AVM, recomendaciones, analytics de mercado
- **Fase 4** — Beta pública: seguridad, integraciones, app móvil, facturación
- **Fase 5** — Producción y escala

## Documentación

- [Decisiones de arquitectura](docs/decisions/)
- [Variables de entorno](.env.example)
