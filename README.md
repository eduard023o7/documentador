# documentador

Plataforma que construye, con agentes de IA sobre AWS, los documentos corporativos de arquitectura del grupo: mapa de fundacionales, lineamientos y estándares; redacción con plantilla común; validación; aprobación humana; versionado; y entrega en Markdown, Word y PDF.

El proyecto se desarrolla con la metodología **AI-DLC**. Ver [`CLAUDE.md`](CLAUDE.md) para las reglas de trabajo y [`aidlc-docs/aidlc-state.md`](aidlc-docs/aidlc-state.md) para el estado actual.

## Estructura

| Carpeta | Contenido |
|---|---|
| `contenido/` | **Contenido del marco** (sin código): perfil en `marco/`, documentos en `documentos/{FUN,LIN,EST}/`, plantilla Word. Se puede mover a otro repositorio sin cambios |
| `src/documentador/` | Paquete Python: núcleo (`core/`), adaptadores, costo, publicación, CLI `doc` |
| `infra/` | AWS CDK en Python ([guía de despliegue](infra/README.md)) |
| `tests/` | Pruebas: `unit/` sin red ni costo; `integration/` usa AWS y GitHub reales |
| `aidlc-docs/` | Artefactos de AI-DLC (requisitos, historias, diseños) |
| `docgen/`, `web/` | Reservadas para U3 (contenedor Word/PDF) y U4 (web) |

## Uso rápido

```bash
uv sync                                   # dependencias
uv run doc perfil validar                 # valida el perfil del marco
uv run doc publicar --ejemplo             # Word y PDF de ejemplo en salida/
uv run doc estado verificar               # acceso a AWS y GitHub (tras desplegar)
uv run pytest                             # pruebas sin costo
```
