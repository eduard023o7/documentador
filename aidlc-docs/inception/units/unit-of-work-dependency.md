# Dependencias entre unidades

```
U0 Fundación ──▶ U1 Mapa ──▶ U2 Redacción ──▶ U3 Necesidades ──▶ U4 Web ──▶ Piloto
```

| Unidad | Necesita de las anteriores | Puede adelantarse en paralelo |
|---|---|---|
| U0 | — | — |
| U1 | Perfil aprobado, adaptador GitHub, infraestructura base (U0) | — |
| U2 | Mapa aprobado, coherencia, revisión con PR, estado y costo (U1) | — |
| U3 | Flujo de documento y versionado (U2) | Contenedor `docgen` (solo depende de la prueba de U0) |
| U4 | Operaciones de U1–U3 expuestas por la API | Pantallas de solo lectura (grafo, niveles) desde que exista el mapa de U1 |

Secuencia estricta por defecto (una sola persona construye). Las tareas paralelas indicadas solo se adelantan si sobra tiempo dentro de una unidad.
