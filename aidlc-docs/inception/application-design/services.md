# Servicios y orquestación de los flujos

Cada flujo es una secuencia fija (grafo Strands sin decisiones del modelo sobre el orden). Antes y después de cada paso: registro en el estado (C8) y cobro al presupuesto (C9). Si se supera el tope, la ejecución queda "detenida" con lo hecho hasta ahí.

## Flujo 1 — Mapa (HU-1.3 a 1.8)

```
doc mapa generar --dominio INF
  1. C1 carga perfil, insumos y mapa actual (grafo)
  2. Investigador → temas + fuentes                 (lee base de conocimiento)
  3. Taxonomista → fichas propuestas                 (consulta grafo e índice de reglas)
  4. C1 asigna IDs y comprueba coherencia del mapa hipotético  → observaciones deterministas
  5. Validador → observaciones de criterio
  6. Contraste → informe (solo después de validar; no modifica la propuesta)
  7. C4 abre PR: archivos de ficha (sin cuerpo) + informe de observaciones y contraste en la descripción
  ── revisión humana en GitHub ──
  8a. doc revisar <PR>  → vuelve al paso 3 con las observaciones
  8b. doc aprobar <PR> --revisor  → C1 revalida; sin bloqueantes: fusiona, etiqueta mapa@x.y.z,
      guarda como casos de prueba las fichas que el revisor corrigió en el PR
```

La evaluación de dominios (HU-1.3) es un flujo corto: Investigador opcional → Taxonomista (evaluate_domains) → PR que modifica `marco/dominios.yaml`.

## Flujo 2 — Documento (HU-2.1 a 2.7)

```
doc redactar EST-INF-AWS-001
  0. C1 comprueba padre y dependencias; si están abiertos y no se aceptó, se detiene con advertencia
  1. Investigador → fuentes para el documento
  2. C7 → reglas parecidas ya aprobadas (para referenciar en vez de repetir)
  3. Redactor → borrador con reglas con ID; registra versión del perfil y plantilla
  4. C1 check_document → observaciones deterministas
  5. Validador → contradicciones, redundancia (con C7), cinco miradas
  6. Contraste (opcional, si hay existentes del tema)
  7. C4 abre PR con el borrador y las observaciones
  ── revisión humana en GitHub: comentarios por línea sobre las reglas ──
  8a. doc revisar <PR> → las reglas con comentario "RECHAZAR: …" vuelven al redactor (revise_rules);
      el resto queda igual → nuevo commit en el mismo PR
  8b. doc aprobar <PR> --revisor → C1 revalida; C1 calcula versión; fusiona; etiqueta <ID>@x.y.z;
      C7 indexa las reglas; C8 marca dependientes "por revalidar"; C10 genera Word y PDF
```

**Revalidación (HU-2.7):** cuando un documento se aprueba, sus dependientes quedan marcados. `run_revalidation` ejecuta C1 + validador sobre ellos y registra observaciones; los que estaban "con dependencias abiertas" pierden la marca si ya no hay conflictos.

## Flujo 3 — Nueva necesidad (HU-3.1 a 3.4)

```
doc necesidad "Necesitamos un estándar para cifrado en Azure"
  1. Admisión → estructurada, o preguntas (la ejecución queda "esperando aclaración")
     doc necesidad responder <id>
  2. Taxonomista (classify_need) → cubierta / ampliación / nueva
     cubierta: se informa el documento y termina
  3. Analista de impacto → paquete: documentos afectados, cambio, tipo de versión
  4. C1 construye el grafo con el paquete aplicado y comprueba coherencia; validador
  5. C4 abre un PR por paquete (rama propia)
  ── revisión humana ──
  6. doc aprobar <PR> --revisor → se ejecuta el flujo de documento para cada afectado dentro de la misma rama;
     el PR del paquete solo se fusiona cuando todos los documentos pasan; si alguno falla, nada se fusiona
```

**Cambio del perfil (HU-3.7):** igual que una necesidad, con el analista de impacto listando los documentos redactados con la versión anterior.

## Publicación (HU-3.5, 3.6)

Determinista, sin IA: al aprobar, C1 propone la versión con `diff_rules` + `bump`; C4 etiqueta; C10 genera Word (Pandoc + plantilla corporativa) y PDF (LibreOffice) y los guarda en `publicaciones/<ID>/<versión>/`. En las fases 1 a 3 la generación corre localmente (Pandoc y LibreOffice instalados) o en la Lambda contenedor cuando exista (U3).

## Dónde corre cada cosa

| Fase | Flujos | Revisión | Estado | Publicación |
|---|---|---|---|---|
| U1–U3 | En el equipo del Admin (CLI) llamando a Bedrock | Pull requests de GitHub + CLI | DynamoDB | Local o Lambda contenedor |
| U4 | AgentCore Runtime (mismo código de C3) | Web (la API usa C4; el PR sigue existiendo por detrás) | DynamoDB | Lambda contenedor |
