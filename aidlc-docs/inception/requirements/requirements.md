# Requisitos — MVP plataforma de lineamientos y estándares

**Estado:** borrador v0, derivado de `fuente-definicion-mvp.md`. Pendiente de las respuestas en `requirement-verification-questions.md`; los puntos marcados **[PREGUNTA Qn]** dependen de ellas.

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
| Administrador del marco | Único que edita el perfil del marco. También construye y opera la solución |
| Arquitecto | Cinco arquitectos (datos, IA, infraestructura, seguridad, empresarial). Proponen, revisan y aprueban en su dominio |
| Agentes de IA | Investigador, Taxonomista, Redactor, Validador, Contraste, Admisión, Analista de impacto, Publicador |

## 4. Requisitos funcionales

### Modelo documental y mapa
- **RF-01** El mapa clasifica cada documento en uno de tres tipos (fundacional, lineamiento, estándar) aplicando el test de clasificación en orden; los temas que describen pasos de ejecución o cambian más de una vez al año quedan registrados como pendientes fuera del MVP.
- **RF-02** El mapa es una matriz de dominios × niveles (0 principios — no son documentos —, 1 fundacionales, 2 lineamientos, 3 estándares).
- **RF-03** Los dominios los propone el equipo; un agente los evalúa y sugiere ajustes; el equipo los aprueba. **[PREGUNTA Q6]**
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
- **RF-14** Orden de redacción por el grafo: fundacionales → lineamientos → estándares. Un documento se redacta solo si su padre está aprobado y sus dependencias están al menos en revisión.
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
- **RF-27** Búsqueda semántica sobre los PDFs con cita a la página de origen; búsqueda web limitada a sitios aprobados. **[PREGUNTA Q9]**

### Visualización y seguimiento
- **RF-28** Vista **Grafo**: nodos (forma por tipo, color por estado), aristas por tipo de relación, filtros por dominio/tipo/estado, resaltado de dependientes al elegir un nodo.
- **RF-29** Vista **Por niveles**: matriz dominio × nivel con cada documento y su estado.
- **RF-30** Vista **Cobertura**: documentos por estado y dominio, revisiones anuales vencidas, observaciones abiertas.
- **RF-31** Vista **Ficha e historial**: versiones con autor, fecha y motivo; diferencias regla por regla; descarga de Word y PDF por versión.
- **RF-32** Vista **Bandeja y revisión por regla**: borradores y paquetes pendientes; cada regla con fuentes y observaciones, para aceptar, rechazar o comentar.
- **RF-33** Vista **Calidad de los agentes**: borradores aprobados sin cambios, observaciones frecuentes por tipo, coincidencia con casos de prueba y costo por ejecución.

### Acceso y repositorio
- **RF-34** Inicio de sesión con usuario y contraseña; dos roles: administrador del marco y arquitecto. Debe poder federarse con Entra ID más adelante sin cambiar la aplicación.
- **RF-35** La web oculta Git: cada aprobación se convierte en un commit con autor, fecha y motivo; cada paquete de cambios es una rama que se fusiona al aprobarse; las versiones son etiquetas (`<ID>@x.y.z`, `mapa@x.y.z`). **[PREGUNTA Q2]**
- **RF-36** El acceso al repositorio de contenido pasa por un adaptador; cambiar de cuenta (personal → corporativa) o de proveedor es solo configuración.

### Calidad de los agentes
- **RF-37** Un conjunto de 30–50 temas reales clasificados a mano (tipo, dominio, padre) se usa como evaluación automática en cada cambio de prompts o reglas, midiendo la coincidencia contra un umbral. **[PREGUNTA Q7]**

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
- **RNF-10 Portabilidad:** el contenido nunca depende de la aplicación (repositorios separados); repositorio y proveedor de identidad intercambiables por configuración.
- **RNF-11 Calidad medible:** pytest + evaluación automática con los casos de prueba.

## 6. Stack de referencia (del insumo)

Python (backend y agentes) · Strands Agents sobre Amazon Bedrock AgentCore Runtime · Claude en Amazon Bedrock (un modelo más capaz para redactor y validador, uno más rápido para tareas simples; configurable) · API Gateway + Lambda · React + Vite + TypeScript en Amplify Hosting con Amplify UI · Cognito · Cytoscape.js + librería de diffs · Pandoc + LibreOffice en Lambda contenedor · Bedrock Knowledge Bases sobre S3 con S3 Vectors · DynamoDB y S3 · GitHub vía API detrás de un adaptador · AWS CDK en Python · pytest.

## 7. Fuera del alcance del MVP

Guías, procedimientos y catálogos · publicación web para toda la empresa · inicio de sesión con Entra ID · adendas locales por empresa · agente vigía, consulta en lenguaje natural, checklists de cumplimiento, registro de excepciones y notificaciones (backlog post-MVP).

## 8. Inconsistencias detectadas en el insumo

1. El plan de fases menciona **Azure Repos** en la fase 4, mientras el resto del documento usa **GitHub**. → Q2
2. El insumo define dos repositorios (`plataforma-lineamientos` y `marco-arquitectura`); este repositorio se llama `documentador`. → Q1
3. La fase 0 es mayormente definición del equipo (perfil del marco y casos de prueba), no código; conviene acordar qué parte construimos aquí. → Q3, Q4
