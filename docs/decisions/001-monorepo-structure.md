# ADR-001: Estructura Monorepo con Turborepo + pnpm

**Estado:** Aceptado  
**Fecha:** 2026-05-03

## Contexto

inmoBIA tiene tres aplicaciones distintas (frontend Next.js, backend Hono, servicio ML Python) y varios paquetes compartidos (schema DB, tipos, UI). Necesitamos decidir si manejarlos como repositorios separados o en un monorepo.

## Decisión

Monorepo con **Turborepo** para orquestación de tareas y **pnpm workspaces** para gestión de paquetes.

## Justificación

- Los paquetes `database`, `shared` (schemas Zod, tipos) y `ui` son consumidos por `apps/web` y `apps/api`. Sin monorepo, cualquier cambio de schema requeriría publicar un paquete npm y actualizar versiones en dos repos — demasiado fricción para un equipo pequeño.
- Turborepo cachea los builds por hash de inputs: si `packages/ui` no cambió, su build no se re-ejecuta. Esto reduce los tiempos de CI en ~60%.
- pnpm es 2-3x más rápido que npm/yarn en install y usa symlinks en lugar de copiar paquetes, lo que ahorra disco en máquinas de desarrollo.
- Alternativa considerada: **Nx** — más potente pero configuración más compleja. Para un equipo de 2-5 personas, Turborepo tiene mejor relación complejidad/beneficio.

## Consecuencias

- El servicio ML (Python/FastAPI) en `apps/ml/` vive en el mismo repo pero con su propio virtualenv. Los GitHub Actions deben instalar dependencias Python + Node.js.
- Cuando el equipo crezca y `apps/ml` necesite ciclos de deploy independientes, puede extraerse a su propio repo sin afectar el resto.
