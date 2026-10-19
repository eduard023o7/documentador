# Requisitos no funcionales (para todo el MVP) — plan

Se definen una sola vez en U0; U1–U4 los heredan (plan de ejecución). Base: RNF-01 a RNF-14 de los requisitos aprobados.
**Entregables** (en `construction/u0-fundacion/nfr-requirements/`): `nfr-requirements.md` (requisitos medibles) y `tech-stack-decisions.md` (versiones y servicios).

## Decisiones que tomo sin preguntar

| Tema | Decisión |
|---|---|
| Disponibilidad | Sin acuerdo de servicio: herramienta interna de un equipo. Reintentos automáticos ante errores transitorios; ninguna redundancia multi-región |
| Rendimiento | Flujo de mapa de un dominio < 15 min; redacción de un documento < 10 min; aprobación (fusión, etiquetas, Word/PDF) < 2 min; pantallas de la web < 2 s |
| Escala | 1 cuenta, ≤ 10 personas, ≤ 300 documentos, ≤ 5 ejecuciones simultáneas |
| Python | 3.12; dependencias fijadas en `pyproject.toml` |
| Embeddings | Amazon Titan Text Embeddings V2 (multilingüe, el más barato en Bedrock); se verifica en el diseño de infraestructura |
| Registros | CloudWatch con retención de 14 días; sin servicios de observabilidad extra |
| Pruebas | Núcleo (C1) con ≥ 90 % de cobertura; el resto, pruebas de los criterios de aceptación de cada historia; pruebas unitarias sin red ni costo |
| Respaldo | GitHub es la fuente de verdad del contenido; DynamoDB con recuperación a un punto en el tiempo desactivada (costo) — el estado es reconstruible |

## Pregunta

### N1. ¿Qué modelos usan los agentes?

Precios de referencia por millón de tokens (tarifa directa de Anthropic; **en Bedrock el precio lo fija AWS y lo verifico antes de U1**):

| Modelo | Entrada | Salida | Para qué sirve |
|---|---|---|---|
| Claude Opus 5.5 | USD 4 | USD 20 | El más capaz de uso general: criterio fino, redacción larga, revisión |
| Claude Sonnet 5.5 | USD 2 | USD 10 | Muy capaz, a la mitad de precio que Opus |
| Claude Haiku 5.5 | USD 0,10 | USD 0,50 | Rápido y muy barato: clasificar, extraer, resumir |

Costo estimado por operación (orden de magnitud, con caché de instrucciones activa):

| Opción | Mapa de un dominio | Redacción + validación de un documento | Con USD 10 alcanza para aprox. |
|---|---|---|---|
| A) Opus 5.5 para taxonomista, redactor, validador y analista de impacto; Haiku 5.5 para investigador, contraste, admisión y evaluador | ≈ USD 0,80 | ≈ USD 0,50 | 3 mapas + 12 documentos |
| B) Sonnet 5.5 en lugar de Opus 5.5; Haiku 5.5 igual | ≈ USD 0,40 | ≈ USD 0,25 | 6 mapas + 25 documentos |
| C) Haiku 5.5 para todo durante las pruebas iniciales, y pasar a A o B para el piloto | ≈ USD 0,05 | ≈ USD 0,03 | prácticamente ilimitado para pruebas, con calidad menor |

A) Recomendado por calidad: el riesgo principal es la clasificación del mapa y la armonía entre documentos, donde más pesa el criterio del modelo
B) Recomendado si priorizas el presupuesto; la evaluación con los casos de prueba dirá si la calidad alcanza
C) Útil para desarrollar sin gastar; la calidad del mapa se mide recién con A o B
X) Otro (explica)

Cualquiera sea la opción, el modelo por agente queda en Parameter Store y se cambia sin tocar código.

[Answer]: B — "B, procede"

## Pasos

- [x] Recibir respuesta a N1
- [x] Escribir `nfr-requirements.md`
- [x] Escribir `tech-stack-decisions.md`
- [x] Presentar para aprobación (aprobado el 2026-10-19)
