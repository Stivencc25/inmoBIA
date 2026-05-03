# ADR-002: Stack Tecnológico

**Estado:** Aceptado  
**Fecha:** 2026-05-03

## Frontend: Next.js 15 + TypeScript + Tailwind CSS 4

Next.js con App Router es obligatorio para SEO (listings deben ser indexables por Google). TypeScript estricto desde el día 1 evita deuda técnica en un dominio complejo. Tailwind 4 + shadcn/ui da velocidad de desarrollo sin sacrificar customización de marca.

## Backend API: Hono.js

Elegido sobre Express y Fastify. Hono es 2-3x más rápido en benchmarks, tiene tipado RPC nativo que elimina la necesidad de OpenAPI para comunicación interna web↔api, y es compatible con Edge runtimes (útil si en el futuro se migra a Cloudflare Workers).

## ORM: Drizzle

Drizzle sobre Prisma porque:
1. Permite SQL raw con typesafety — necesario para queries PostGIS (`ST_DWithin`, `ST_Distance`) y pgvector (`<=>`, `<#>`).
2. Migraciones explícitas (archivos SQL) — más predecibles en producción.
3. ~40% más rápido que Prisma en queries complejas según benchmarks independientes.

## Base de datos: PostgreSQL via Supabase

Una sola instancia PostgreSQL con extensiones pgvector y PostGIS reemplaza tres servicios (relacional + vectorial + geoespacial). Supabase agrega Row Level Security, realtime y auth de respaldo. En MVP, esto elimina Pinecone/Weaviate y un servidor de mapas dedicado.

## IA: Anthropic Claude + Vercel AI SDK

Claude claude-sonnet-4-6 para chatbot y generación de contenido. Vercel AI SDK para streaming y tool use en Next.js. El modelo AVM (valuación) es XGBoost propio — los LLMs generativos no son confiables para predicciones numéricas en dominios donde los datos históricos locales son críticos.

## Auth: Better Auth

Sobre NextAuth/Auth.js porque soporta multi-tenancy, 2FA y tiene mejor DX con TypeScript. La abstracción permite agregar SSO empresarial en Fase 4 sin reescribir el sistema de auth.
