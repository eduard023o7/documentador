# Requisitos — MVP plataforma de lineamientos y estándares

**Estado:** borrador v1 (2026-10-19). Incorpora las respuestas de `requirement-verification-questions.md`; los puntos marcados **[SEGUIMIENTO Sn]** dependen de `requirement-followup-questions.md`.

## 0. Decisiones tomadas

| # | Decisión |
|---|---|
| Q1 | **Monorepo**: código y contenido del marco en este repositorio, en carpetas separadas |
| Q3 | El ciclo AI-DLC cubre **todo el MVP** (fases 0 a 5) |
| Q4 | La IA **redacta bajo demanda**; antes se hacen la planificación y las definiciones (dominios, principios, estructura). Sin redundancia entre documentos, referencias cruzadas y mapa de relaciones como grafo |
| Q5 | La aprobación final la da **el revisor** |
| Q6 | Los dominios son **insumo de la planificación**; OT puede ser dominio, aún por definir. No se fijan dominios en el código |
| Q7 | Umbral de calidad: **90 %** de coincidencia con los casos de prueba |
| Q8 | **Eduardo es dueño de todo el MVP**, incluidos los fundacionales |
| Q10 | Disponibles: **cuenta AWS** y **plantilla Word corporativa**. Pendientes: sitios aprobados, contrato de Gartner |

## 1. Análisis de la solicitud

| Aspecto | Evaluación |
|---|---|
| Tipo de solicitud | Proyecto nuevo (greenfield) |
| Alcance | Sistema completo: agentes, API, web, generación de documentos, infraestructura AWS y repositorio de contenido |
| Complejidad | Alta: 8 agentes, 3 flujos, contenido versionado en Git, 6 vistas, exportación Word/PDF |
| Profundidad del análisis | Completa. El insumo ya es detallado; las preguntas se limitan a vacíos e inconsistencias |
| Restricción principal | Lo construye y opera una sola persona con apoyo de IA → servicios gestionados, serverless, flujos deterministas |
| Riesgo principal | Que el mapa salga mal clasificado (no que falte una pantalla) → la calidad de los agentes se construye y mide primero |

## 2. Objetivo

Construir de principio a fin los documentos corporativos de arquitectura del grupo: definir el mapa (fundacionales, lineamientos, estándares), redactar cada documento con una plantilla común, validarlo, aprobarlo, versionarlo y entregarlo en Markdown, Word y PDF; con vistas para ver el mapa como grafo, por niveles y su cobertura. La IA hace el grueso y preaprueba; las personas validan, aportan insumos y aprueban.

**Principios de diseño:** (1) simple de entender: pocas pantallas, lenguaje claro, cada decisión de la IA con su justificación; (2) calidad alta y verificable: reglas explícitas, validación automática y casos de prueba que miden si los agentes clasifican como el equipo.

## 3. Actores

| Actor | Descripción |
|---|---|
| Administrador del marco | Único que edita el perfil del marco. También construye y opera la solución. En el MVP: Eduardo, dueño de todo |
| Revisor | Da la aprobación final de un documento, del mapa o de un paquete de cambios **[SEGUIMIENTO S4]** |
| Arquitecto | Propone necesidades, pide redacciones y revisa **[SEGUIMIENTO S5: si en el MVP hay más usuarios que Eduardo]** |
| Agentes de IA | Investigador, Taxonomista, Redactor, Validador, Contraste, Admisión, Analista de impacto, Publicador |

## 4. Requisitos funcionales

### Modelo documental y mapa
- **RF-01** El mapa clasifica cada documento en uno de tres tipos (fundacional, lineamiento, estándar) aplicando el test de clasificación en orden; los temas que describen pasos de ejecución o cambian más de una vez al año quedan registrados como pendientes fuera del MVP.
- **RF-02** El mapa es una matriz de dominios × niveles (0 principios — no son documentos —, 1 fundacionales, 2 lineamientos, 3 estándares).
- **RF-03** Los dominios (y si OT es uno de ellos) son insumo de la planificación: los ingresa el usuario, un agente los evalúa y sugiere ajustes, y el revisor los aprueba. El código no asume ningún dominio fijo.
- **RF-04** Cada documento tiene una ficha con: ID, título, tipo, dominio, padre, relaciones, frontera de alcance (incluye/excluye), justificación de tipo, fuentes, impacto (nº de dependientes), prioridad y estado.
- **RF-05** IDs: `FUN-<DOM>-NNN`, `LIN-<DOM>-NNN`, `EST-<DOM>-<TEC>-NNN`; reglas internas `<ID>.RNN`.
- **RF-06** El sistema valida automáticamente las reglas de coherencia: padre único (lineamiento→dominio, estándar→lineamiento), fronteras de alcance sin solapes, relaciones tipadas (`deriva_de`, `depende_de`, `complementa`, `reemplaza`), dueño por preocupación (otro dominio puede endurecer, nunca relajar), precedencia principio > fundacional > lineamiento > estándar, y sin ciclos en `depende_de`.
- **RF-07** Si cambian el test, el esquema de IDs, los tipos de relación o los criterios de validación, el validador reevalúa todo el mapa.

### Configuración del marco
- **RF-08** Todo lo que define cómo se ven y construyen los documentos vive en un **perfil del marco** versionado (tipos, plantillas por tipo, secciones opcionales por dominio desde catálogo cerrado, dominios y subdominios, codificación, niveles DEBE/DEBERÍA/PUEDE, relaciones, ciclo de vida y aprobadores, versionado y revisión, estilo, glosario, fuentes y su jerarquía, criterios de validación y severidades, principios, formato de salida Word).
- **RF-09** Solo el administrador edita el perfil desde la web; los cambios se versionan en Git y se aprueban como cualquier documento.
- **RF-10** Cuatro invariantes no son configurables: padre único, IDs únicos, cada tema en un solo lugar, nada se publica sin aprobación humana.
- **RF-11** Cada documento registra la versión del perfil y de la plantilla con que se redactó. Ante un cambio del marco, el analista de impacto lista los afectados y el redactor propone su migración como paquete de cambios.

### Construcción de documentos
- **RF-12** Plantilla inicial: ficha, propósito, alcance y aplicabilidad, documentos relacionados, definiciones, reglas, especificación técnica (solo estándares), excepciones, cumplimiento y verificación, referencias, control de cambios.
- **RF-13** Cada regla tiene: ID, nivel (DEBE/DEBERÍA/PUEDE), enunciado, justificación, cómo se verifica y fuentes. Lo que viene de otro documento se referencia por ID, nunca se copia.
- **RF-14** **Redacción bajo demanda:** el usuario elige un documento del mapa aprobado y pide su redacción; no hay redacción masiva del mapa. El orden recomendado sigue el grafo (fundacionales → lineamientos → estándares). Comportamiento si el padre o las dependencias no están aprobados: **[SEGUIMIENTO S3]**.
- **RF-15** Ciclo de vida: propuesto → en redacción → en validación → en revisión humana → aprobado → obsoleto. Revisión anual de cada aprobado.
- **RF-16** Versionado `mayor.menor.parche` (mayor: cambia/elimina una regla DEBE; menor: agrega reglas o cambia DEBERÍA/PUEDE; parche: redacción). Cada versión registra autor, fecha, motivo y paquete de cambios. El mapa completo también se versiona.
- **RF-17** El Markdown en Git es la fuente de verdad. Word se genera desde Markdown con la plantilla corporativa; PDF desde Word. Los no aprobados llevan marca de agua "Borrador".

### Agentes y flujos
- **RF-18** Flujo **Mapa**: Investigador → Taxonomista → Validador → Contraste → revisión humana → Publicador.
- **RF-19** Flujo **Documento**: Investigador → Redactor → Validador (plantilla, coherencia, citas reales, miradas de datos, IA, infraestructura, seguridad y arquitectura empresarial) → Contraste → revisión humana → Publicador.
- **RF-20** Flujo **Nueva necesidad**: Admisión (pide aclaraciones si está incompleta) → Taxonomista (¿nuevo, ampliación o cubierto?) → Analista de impacto (paquete de cambios) → Validador (mapa con el paquete aplicado) → revisión humana → Publicador.
- **RF-21** Si la revisión humana pide ajustes, el flujo vuelve al taxonomista o redactor con las observaciones. En la revisión por regla, solo las reglas rechazadas vuelven al redactor.
- **RF-22** Un paquete de cambios aprobado dispara la redacción de los documentos afectados y se publica completo o no se publica (atómico).
- **RF-23** Ningún agente cambia el mapa ni un documento sin aprobación humana. Cada propuesta guarda su justificación y las fuentes usadas.

### Insumos y fuentes
- **RF-24** Insumos: principios (formulario de texto), contexto de arquitectura empresarial (formulario estructurado + diagrama adjunto), fuentes de conocimiento (sitios aprobados y PDFs) y documentos existentes (PDF/Word, solo para contraste).
- **RF-25** El mapa se genera y valida sin ver los documentos existentes; luego el contraste muestra coincidencias, omisiones y temas nuevos. Ninguna diferencia se incorpora sola.
- **RF-26** Toda fuente citada debe existir y estar disponible; el validador lo comprueba.
- **RF-27** Búsqueda semántica sobre los PDFs con cita a la página de origen; búsqueda en los sitios aprobados. Mecanismo: **[SEGUIMIENTO S6]** (recomendado: rastreador de Bedrock Knowledge Bases limitado a los sitios aprobados).

### Visualización y seguimiento
- **RF-28** Vista **Grafo**: nodos (forma por tipo, color por estado), aristas por tipo de relación, filtros por dominio/tipo/estado, resaltado de dependientes al elegir un nodo.
- **RF-29** Vista **Por niveles**: matriz dominio × nivel con cada documento y su estado.
- **RF-30** Vista **Cobertura**: documentos por estado y dominio, revisiones anuales vencidas, observaciones abiertas.
- **RF-31** Vista **Ficha e historial**: versiones con autor, fecha y motivo; diferencias regla por regla; descarga de Word y PDF por versión.
- **RF-32** Vista **Bandeja y revisión por regla**: borradores y paquetes pendientes; cada regla con fuentes y observaciones, para aceptar, rechazar o comentar.
- **RF-33** Vista **Calidad de los agentes**: borradores aprobados sin cambios, observaciones frecuentes por tipo, coincidencia con casos de prueba y costo por ejecución.

### Acceso y repositorio
- **RF-34** Inicio de sesión con usuario y contraseña; dos roles: administrador del marco y arquitecto. Debe poder federarse con Entra ID más adelante sin cambiar la aplicación.
- **RF-35** La web oculta Git: cada aprobación se convierte en un commit con autor, fecha y motivo; cada paquete de cambios es una rama que se fusiona al aprobarse; las versiones son etiquetas (`<ID>@x.y.z`, `mapa@x.y.z`). Proveedor: **[SEGUIMIENTO S1]** (recomendado: GitHub en el MVP).
- **RF-36** El acceso al repositorio de contenido pasa por un adaptador; cambiar de cuenta (personal → corporativa) o de proveedor es solo configuración.

### Calidad de los agentes
- **RF-37** Un conjunto de 30–50 temas reales clasificados a mano (tipo, dominio, padre) se usa como evaluación automática en cada cambio de prompts o reglas; la fase 1 se aprueba con **≥ 90 %** de coincidencia. Quién arma los casos: **[SEGUIMIENTO S5]**.

### Sin redundancia y con referencias (refuerzo de Q4)
- **RF-38** **Detección de redundancia:** antes de proponer un documento o una regla, el taxonomista y el redactor consultan el mapa y las reglas existentes; el validador marca como observación toda regla que repita el significado de otra ya existente (comparación semántica) y propone reemplazarla por una referencia a su ID.
- **RF-39** **Referencias navegables:** toda referencia a otro documento o regla (`<ID>` o `<ID>.RNN`) se valida contra el mapa (debe existir y no estar obsoleta) y se muestra como enlace en la web, en Word y en PDF.
- **RF-40** **Mapa como grafo:** el mapa (documentos + relaciones tipadas) se construye leyendo las fichas y es la fuente única que usan los agentes para decidir dónde vive cada tema, y que muestran las vistas de grafo y por niveles.

## 5. Requisitos no funcionales

- **RNF-01 Región y nube:** AWS us-east-1.
- **RNF-02 Operabilidad:** servicios gestionados y serverless; desplegable con un comando (AWS CDK en Python); flujos deterministas y fáciles de depurar.
- **RNF-03 Trazabilidad:** registro de cada paso de cada ejecución (AgentCore Observability / CloudWatch).
- **RNF-04 Costo:** presupuesto de tokens por ejecución (se detiene y avisa al superarlo) y presupuesto mensual con alerta (AWS Budgets). **[PREGUNTA Q11]**
- **RNF-05 Seguridad ante inyección de prompts:** el contenido de páginas web y PDFs se trata como datos, nunca como órdenes; ningún agente que lee fuentes puede escribir en el mapa.
- **RNF-06 Secretos:** token del repositorio y claves de API en Secrets Manager.
- **RNF-07 Licencias:** no cargar contenido de Gartner hasta revisar el contrato.
- **RNF-08 Idioma:** español en contenido, interfaz y mensajes.
- **RNF-09 Usabilidad:** pocas pantallas, lenguaje claro, toda decisión de la IA con justificación visible.
- **RNF-10 Portabilidad:** monorepo con el contenido del marco en una carpeta propia que no importa nada del código, de modo que pueda extraerse a otro repositorio sin cambios; repositorio y proveedor de identidad intercambiables por configuración.
- **RNF-12 Commits de contenido:** las aprobaciones generan commits en el mismo repositorio que el código; el despliegue (Amplify, CDK) debe ignorar cambios solo de contenido para no reconstruir la aplicación en cada aprobación.
- **RNF-11 Calidad medible:** pytest + evaluación automática con los casos de prueba.

## 6. Stack de referencia (del insumo)

Python (backend y agentes) · Strands Agents sobre Amazon Bedrock AgentCore Runtime · Claude en Amazon Bedrock (un modelo más capaz para redactor y validador, uno más rápido para tareas simples; configurable) · API Gateway + Lambda · React + Vite + TypeScript en Amplify Hosting con Amplify UI · Cognito · Cytoscape.js + librería de diffs · Pandoc + LibreOffice en Lambda contenedor · Bedrock Knowledge Bases sobre S3 con S3 Vectors · DynamoDB y S3 · GitHub vía API detrás de un adaptador · AWS CDK en Python · pytest.

## 7. Fuera del alcance del MVP

Guías, procedimientos y catálogos · publicación web para toda la empresa · inicio de sesión con Entra ID · adendas locales por empresa · agente vigía, consulta en lenguaje natural, checklists de cumplimiento, registro de excepciones y notificaciones (backlog post-MVP).

## 8. Inconsistencias detectadas en el insumo

1. El plan de fases menciona **Azure Repos** en la fase 4, mientras el resto del documento usa **GitHub**. → S1 (pendiente)
2. El insumo define dos repositorios; se resolvió con un **monorepo** (Q1).
3. El insumo fija un orden de redacción por el grafo; la decisión de redactar **bajo demanda** cambia ese orden a recomendación. → S3 (pendiente)
4. El insumo habla de cinco arquitectos aprobando por dominio; la respuesta indica un dueño único y un revisor. → S4, S5 (pendiente)
