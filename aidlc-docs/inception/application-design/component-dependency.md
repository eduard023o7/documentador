# Dependencias entre componentes

## Matriz (fila depende de columna)

| | C1 Núcleo | C2 Agentes | C3 Flujos | C4 Revisión | C5 Repo | C6 KB | C7 Índice | C8 Estado | C9 Costo | C10 Publicador |
|---|---|---|---|---|---|---|---|---|---|---|
| **C1 Núcleo** | — | | | | | | | | | |
| **C2 Agentes** | ✔ (lectura) | — | | | | ✔ | ✔ | | ✔ | |
| **C3 Flujos** | ✔ | ✔ | — | ✔ (abre PR) | ✔ (lectura) | | ✔ | ✔ | ✔ | |
| **C4 Revisión** | ✔ | | ✔ (rework) | — | ✔ | | ✔ | ✔ | | ✔ |
| **C10 Publicador** | ✔ | | | | ✔ (lectura) | | | | | — |
| **C11 Evaluador** | ✔ | ✔ | | | ✔ (lectura) | | | ✔ | ✔ | |
| **C12 CLI / C13 API** | ✔ | | ✔ | ✔ | | ✔ | | ✔ | | ✔ |
| **C14 Web** | | | | | | | | | | (solo vía C13) |

**Reglas:**
- C1 no depende de nada: se prueba aislado y es el árbitro común.
- Los adaptadores (C5–C8) se usan detrás de interfaces; las pruebas unitarias usan versiones en memoria.
- Solo C4 escribe en C5. C2 no tiene acceso de escritura a C5 ni a C8.

## Flujo de datos

```
Insumos (CLI/Web) ──▶ C5 contenido/marco/ ──▶ C1 Perfil
PDFs / sitios ──────▶ S3 ──▶ C6 Base de conocimiento ──▶ C2 Investigador / Contraste
                                                   ┌──────────────┐
C5 documentos/ ──▶ C1 Grafo ──▶ C2 Taxonomista ──▶ │ Propuesta    │──▶ C1 coherencia ──▶ C2 Validador
                                                   └──────┬───────┘
                                                          ▼
                                     C4 PR ──▶ revisión humana ──▶ C4 aprobar
                                                                     │
          ┌──────────────────┬──────────────────┬───────────────────┼──────────────────┐
          ▼                  ▼                  ▼                   ▼                  ▼
   C5 merge + tags     C7 indexa reglas   C8 aprobación,     C8 casos de prueba   C10 Word/PDF → S3
                                          marcas revalidar
```

## Orden de construcción que impone

U0: C1 (perfil, documento), C5, C10 (prueba), C15 base → U1: C1 (grafo, coherencia), C6, C8, C9, C2 (investigador, taxonomista, validador, contraste), C3 mapa, C4, C11, C12 → U2: C7, C2 (redactor), C3 documento, C1 (versiones) → U3: C2 (admisión, impacto), C3 necesidad, C10 completo → U4: C13, C14, C3 en AgentCore.
