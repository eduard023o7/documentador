# Componentes

**Decisiones de base:** D1=A (en las fases 1 a 3 los flujos corren en el equipo del Admin; pasan a AgentCore Runtime en U4), D2=A (antes de la web se revisa con pull requests de GitHub), D3=A (estado de trabajo en DynamoDB desde U1). Más las cuatro decisiones del plan: coherencia en código, núcleo compartido, redundancia con embeddings y agentes de lectura sin escritura.

## Vista general

```
                ┌──────────── Entradas ────────────┐
                │  CLI (U0–U3)        Web + API (U4)│
                └───────────────┬──────────────────┘
                                ▼
        ┌────────────── Servicios de aplicación ──────────────┐
        │  Orquestador de flujos      Servicio de revisión     │
        │  (mapa · documento · necesidad)  y aprobación         │
        │  Control de costo           Publicador   Evaluador    │
        └───────┬──────────────────────────┬───────────────────┘
                ▼                          ▼
   ┌────── Agentes (IA) ──────┐   ┌──────── Núcleo del marco ────────┐
   │ Investigador  Taxonomista│   │ Perfil · Modelo documental · Grafo │
   │ Redactor  Validador      │──▶│ Coherencia · IDs · Versionado      │
   │ Contraste  Admisión      │   │ (Python puro, sin IA, sin red)     │
   │ Analista de impacto      │   └────────────────────────────────────┘
   └───────────┬──────────────┘
               ▼
   ┌──────────────────────── Adaptadores ────────────────────────┐
   │ Repositorio (GitHub) · Base de conocimiento (Bedrock KB +    │
   │ S3 Vectors) · Índice de reglas (S3 Vectors) · Estado          │
   │ (DynamoDB) · Modelos (Bedrock) · Archivos (S3)                │
   └──────────────────────────────────────────────────────────────┘
```

## Catálogo

| # | Componente | Responsabilidad | Unidad | Historias |
|---|---|---|---|---|
| C1 | **Núcleo del marco** | Cargar y validar el perfil; leer y escribir documentos (ficha + cuerpo + reglas); construir el grafo del mapa; comprobar las reglas de coherencia deterministas; asignar IDs; calcular versiones y diferencias regla por regla. Sin IA ni red: todo es Python puro y probado con pytest | U0 (base), U1–U3 (amplía) | HU-0.3, 0.4, 0.5, 1.5, 1.6, 1.11, 2.3, 2.7, 3.5, 3.8 |
| C2 | **Agentes** | Ocho agentes Strands, uno por rol, con instrucciones en español y entradas/salidas tipadas. Proponen; nunca escriben en el repositorio | U1 (5), U2 (usa), U3 (2) | HU-1.3–1.7, 2.2–2.5, 3.1–3.3, 3.7 |
| C3 | **Orquestador de flujos** | Ejecutar los flujos de mapa, documento y nueva necesidad en orden fijo; pasar el resultado de cada agente al siguiente; registrar cada paso; detenerse en la revisión humana | U1–U3; en AgentCore en U4 | HU-1.4–1.8, 2.1–2.5, 3.1–3.4, 4.3 |
| C4 | **Servicio de revisión y aprobación** | Convertir una propuesta en pull request; recoger rechazos y comentarios; aprobar con nombre del revisor (fusiona, etiqueta, actualiza estados); capturar correcciones como casos de prueba; marcar dependientes para revalidar | U1 (mapa), U2 (documento), U3 (paquete) | HU-1.8, 1.9, 2.6, 2.7, 3.4, 3.5, 4.8, 4.9 |
| C5 | **Adaptador de repositorio** | Interfaz única de lectura/escritura del contenido (archivos, ramas, commits, pull requests, fusión, etiquetas). Implementación GitHub; otra implementación = otro proveedor | U0 | HU-0.7 |
| C6 | **Base de conocimiento** | Ingerir PDFs y sitios aprobados; buscar con cita (archivo y página o URL); confirmar que una cita existe | U1 | HU-1.2, 1.4, 2.2 |
| C7 | **Índice de reglas** | Guardar cada regla aprobada como vector y devolver las más parecidas a un texto dado | U2 | HU-2.3, 2.4, 3.2 |
| C8 | **Estado de trabajo** | Ejecuciones, pasos, observaciones, aprobaciones, necesidades, paquetes y casos de prueba en DynamoDB | U1 | HU-1.8–1.10, 2.6, 3.1–3.4, 4.3, 4.11 |
| C9 | **Control de costo** | Elegir el modelo según el agente; contar tokens; cortar la ejecución al superar el tope; estimar costo | U1 | HU-1.10, 4.11 |
| C10 | **Publicador** | Generar Word (Pandoc + plantilla corporativa, marca "Borrador", referencias como enlaces) y PDF (LibreOffice); guardar los archivos de cada versión | U0 (prueba), U3 | HU-0.6, 3.6, 4.7 |
| C11 | **Evaluador** | Reclasificar los casos de prueba con el taxonomista y medir la coincidencia por tipo, dominio y padre | U1 | HU-1.9, 5.2 |
| C12 | **CLI** | Comandos para cargar insumos, lanzar flujos, revisar y aprobar en las fases 1 a 3 | U0–U3 | HU-1.1, 1.2, 2.1, 3.1 |
| C13 | **API** | Mismas operaciones que la CLI, para la web, protegidas con Cognito | U4 | HU-4.1–4.11 |
| C14 | **Web** | Pantallas: insumos, grafo, niveles, cobertura, ficha e historial, bandeja, editor del marco, calidad | U4 | HU-4.1–4.11 |
| C15 | **Infraestructura** | Stacks CDK por capa, presupuesto y alertas, permisos mínimos | U0 (base), U1, U3, U4 | HU-0.2 |
| — | **Estructura del monorepo** | Carpetas, reglas de despliegue y ramas (ver `repo-structure.md`) | U0 | HU-0.1 |

## Los ocho agentes (C2)

| Agente | Recibe | Devuelve | Herramientas (solo lectura) | Modelo |
|---|---|---|---|---|
| Investigador | Dominio o documento + perfil + principios | Temas con fuentes citables | Base de conocimiento | Rápido |
| Taxonomista | Temas, mapa actual, perfil, dominios | Fichas propuestas con justificación según el test; pendientes fuera del MVP | Grafo del mapa (consulta), índice de reglas | Capaz |
| Redactor | Ficha, plantilla, padre y dependencias, fuentes, reglas parecidas | Borrador Markdown con reglas con ID | Grafo, índice de reglas, base de conocimiento | Capaz |
| Validador | Mapa o borrador + observaciones deterministas de C1 | Observaciones de criterio (contradicción, redundancia, cinco miradas) con severidad | Grafo, índice de reglas, verificación de citas | Capaz |
| Contraste | Mapa o borrador + documentos existentes | Coincidencias, omisiones, temas nuevos | Base de conocimiento (colección "existentes") | Rápido |
| Admisión | Texto de la necesidad | Necesidad estructurada o preguntas de aclaración | — | Rápido |
| Analista de impacto | Necesidad clasificada o cambio del perfil + grafo | Paquete de cambios (documentos, cambio, tipo de versión) | Grafo | Capaz |
| Publicador | — | — | No es un agente de IA: es el componente C10, determinista | — |

El publicador del doc original se implementa sin IA (C10 + C4): asignar versión y generar archivos no requiere criterio.

**Piloto (HU-5.1 a 5.3):** no agrega componentes; usa todos los anteriores. La guía de uso (HU-5.3) es documentación.

## Reglas de diseño transversales

1. **Escritura única:** solo C4 escribe en el repositorio, y solo tras una aprobación con nombre del revisor.
2. **Coherencia en dos capas:** C1 comprueba lo verificable con código (bloqueante y gratis); el validador solo agrega lo que requiere criterio.
3. **Contenido externo es dato:** los textos de fuentes llegan a los agentes delimitados y marcados como material; ningún agente que los lee tiene herramientas de escritura.
4. **Nada fijo en el código:** dominios, tipos, plantillas, IDs y criterios salen del perfil (C1).
5. **Mismo núcleo en todas partes:** CLI, API, agentes y web (vía API) usan C1, así que nunca discrepan.
