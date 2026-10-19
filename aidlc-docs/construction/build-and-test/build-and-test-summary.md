# Resumen de build y pruebas — U0 Fundación

Fecha: 2026-10-19.

## Ejecutado en el entorno de desarrollo

| Verificación | Resultado |
|---|---|
| `uv sync` + `uv build` | ✓ paquete `documentador-0.1.0` construido |
| `ruff check` / `ruff format --check` | ✓ sin observaciones |
| `mypy src` (estricto en `core/`) | ✓ sin errores |
| `pytest` (unitarias + plantilla CDK) | ✓ 144 pasan, 0 fallan |
| Cobertura | ✓ 96 % total; `core/` 95–98 % (meta ≥ 90 %) |
| Síntesis CDK `DocumentadorBase` | ✓ solo recursos previstos (18 parámetros, presupuesto, bucket + política, tabla, política IAM) |
| `doc publicar --ejemplo` (Pandoc 3.1 + LibreOffice 24.2) | ✓ Word y PDF; marca BORRADOR verificada visualmente |

## Pendiente en tu cuenta (puerta de salida de U0)

| Verificación | Estado |
|---|---|
| Despliegue `DocumentadorBase` con alertas de presupuesto | ⏳ pendiente |
| Token de GitHub en `/documentador/github/token` | ⏳ pendiente |
| `doc estado verificar` con 5 ✓ | ⏳ pendiente |
| `pytest -m integration` (7 pruebas) | ⏳ pendiente |
| Word/PDF con la plantilla corporativa aceptados | ⏳ pendiente |
| Perfil del marco revisado y aprobado como `marco@1.0.0` (sin `POR DEFINIR` obligatorios: contexto y principios) | ⏳ pendiente |

U0 se cierra cuando todas las filas de esta tabla estén en ✓.
