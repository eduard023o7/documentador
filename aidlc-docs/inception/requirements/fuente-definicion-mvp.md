# Fuente: Definición del MVP — plataforma de lineamientos y estándares

> Copia de referencia del doc original (Claude Docs, rev 58, leído el 2026-10-19).
> Fuente viva: https://claude.ai/artifact/W8xhC2MeK41HYxgeX2uSMU — si difieren, manda el doc y se actualiza esta copia.
> Los diagramas embebidos se transcriben como tablas en su lugar.

2026-10-17 · @Eduardo
## Resumen y objetivo
La solución construye los documentos corporativos de arquitectura del grupo, de principio a fin: define el mapa de fundacionales, lineamientos y estándares, redacta cada documento con una plantilla común y entrega Markdown, Word y PDF. Desde la misma solución se ve el mapa como grafo, por niveles y con su cobertura, y se sigue el versionado de cada documento.
Lo construye el equipo de arquitectura con agentes de IA sobre AWS (us-east-1). La IA hace el grueso del trabajo y preaprueba; las personas validan, aportan insumos y aprueban.
Dos principios de diseño guían todo:
- Simple de entender: pocas pantallas, lenguaje claro y cada decisión de la IA viene con su justificación.
- Calidad alta y verificable: reglas de clasificación explícitas, validación automática y un set de casos de prueba que mide si los agentes clasifican como lo haría el equipo.
## Alcance
El MVP cubre el ciclo completo: mapa, redacción, validación, aprobación, versionado y entrega en Word y PDF. La publicación web para toda la empresa queda para después.
| Incluye | Queda fuera |
| Mapa documental generado por agentes y aprobado por el equipo | Guías, procedimientos y catálogos |
| Tres tipos de documento: fundacional, lineamiento y estándar | Publicación web para toda la empresa |
| Dominios propuestos por el equipo y evaluados por un agente | Inicio de sesión con Entra ID (fase posterior) |
| Redacción de cada documento con plantilla y reglas estandarizadas | Adendas locales de cada empresa (serán anexos, más adelante) |
| Validación del mapa y de cada documento |  |
| Contraste con los documentos existentes, solo como referencia |  |
| Ingreso de nuevas necesidades y análisis de impacto |  |
| Versionado de cada documento y del mapa |  |
| Vista de grafo, vista por niveles y tablero de cobertura |  |
| Exportación a Word con la plantilla corporativa y a PDF |  |
| Interfaz web sencilla con usuario y contraseña |  |
Los principios corporativos no son documentos del mapa: entran como instrucciones que guían a los agentes. El idioma de trabajo es el español.
## Modelo documental
Cada documento del mapa es de uno de tres tipos, y el tipo se decide con un test explícito, no caso por caso.
| Tipo | Qué dice | Depende de la tecnología | Cómo se verifica | Ejemplo |
| Fundacional | Clasificaciones y criterios que usan todos los dominios | No | Se usa como referencia en otros documentos | Clasificación de soluciones por criticidad (tiers) |
| Lineamiento | Qué se exige y por qué | No | Revisión de diseño | Toda nube debe separar cuentas por entorno |
| Estándar | Cómo se cumple con una tecnología concreta | Sí | Configuración o herramienta, con resultado sí/no | Estructura de OUs y SCPs en AWS Control Tower |
Test de clasificación (se aplica a cada tema, en este orden):
- ¿Lo usan como criterio común varios dominios y no exige nada por sí mismo? → Fundacional.
- ¿Seguiría siendo válido si mañana cambiamos de proveedor o tecnología? → Lineamiento.
- ¿Nombra un producto o fija valores comprobables con una herramienta? → Estándar.
- ¿Describe pasos de ejecución o cambia más de una vez al año? → Fuera del MVP (sería guía o catálogo); el agente lo registra como pendiente.
Un mismo tema puede repartirse entre tipos. Por ejemplo, "cifrar datos confidenciales en reposo" es lineamiento de seguridad, y "usar KMS con llaves del cliente" es estándar de AWS. Cada parte vive en un solo documento.
## Estructura del mapa y ficha de cada documento
El mapa es una matriz de dominios por niveles. Los dominios no están predefinidos: los propone el equipo y un agente los evalúa y sugiere ajustes.
- Nivel 0, principios: insumo de instrucciones, no forma parte del mapa.
- Nivel 1, fundacionales: transversales; se priorizan porque casi todo depende de ellos.
- Nivel 2, lineamientos: agrupados por dominio.
- Nivel 3, estándares: cada uno cuelga de un lineamiento y se agrupa por tecnología.
Cada documento del mapa tiene esta ficha:
| Campo | Contenido | Ejemplo |
| ID | Tipo, dominio, tecnología y correlativo | EST-INF-AWS-001 |
| Título | Nombre corto y descriptivo | Landing zone en AWS |
| Tipo | Fundacional, lineamiento o estándar | Estándar |
| Dominio | Uno de los dominios aprobados | Infraestructura |
| Padre | Un único documento superior | LIN-INF-001 Plataforma cloud |
| Relaciones | Referencias tipadas a otros documentos | depende_de LIN-SEG-002 |
| Frontera de alcance | Temas que cubre y temas que excluye explícitamente | Incluye OUs y SCPs; excluye redes on-premise |
| Justificación | Por qué es de ese tipo, según el test | Nombra un producto y fija valores verificables |
| Fuentes | Referencias que sustentan su existencia | AWS Well-Architected, TOGAF |
| Impacto | Número de documentos que dependen de él | Alto: 9 dependientes |
| Prioridad y estado | Para ordenar la redacción y seguir el avance | Alta · Propuesto |
Esquema de IDs propuesto: FUN-<DOM>-NNN, LIN-<DOM>-NNN y EST-<DOM>-<TEC>-NNN. Las reglas internas de cada documento usarán <ID>.RNN cuando se redacten.
## Reglas de relación y coherencia
El mapa no es un árbol sino una red: cada documento tiene un solo padre, y el resto de conexiones son referencias tipadas, nunca copias.
- Padre único. Todo lineamiento cuelga de un dominio y todo estándar de un lineamiento.
- Cada tema vive en un solo lugar. Las fronteras de alcance no se solapan; si dos documentos necesitan el mismo tema, uno lo define y el otro lo referencia.
- Relaciones tipadas: deriva_de (el padre), depende_de (usa algo definido en otro), complementa (cubre un tema vecino) y reemplaza (sustituye a uno anterior).
- Dueño por preocupación. El dominio dueño de un tema (por ejemplo, seguridad) es quien lo define; otro dominio puede endurecerlo, pero nunca relajarlo.
- Precedencia. Principio > fundacional > lineamiento > estándar. Un conflicto entre dominios lo resuelve el dueño del tema y, si no, el equipo de arquitectura.
- Sin dependencias circulares en depende_de.
- Las reglas del juego son configuración versionada. El test, el esquema de IDs, los tipos de relación y los criterios de validación los escribe el equipo; si cambian, el validador reevalúa todo el mapa.
## Configuración del marco documental
Todo lo que define cómo se ven y se construyen los documentos vive en un perfil del marco configurable, no en el código ni en los prompts. Ese perfil lo edita solo el administrador del marco desde la web, se versiona en GitHub y sus cambios se aprueban como cualquier documento.
| Elemento | Qué se puede ajustar | Ejemplo |
| Tipos de documento | Nombre, código, nivel, criterio del test de clasificación | Agregar el tipo "guía" más adelante |
| Plantillas por tipo | Secciones, orden, obligatoriedad e instrucciones de redacción por sección | El estándar exige "Especificación técnica"; el lineamiento no |
| Secciones por dominio | Secciones opcionales que un dominio activa desde un catálogo cerrado | Seguridad activa "Mapeo a controles ISO 27001" |
| Dominios y subdominios | Nombre, código para IDs, dueño y "mirada" del validador | INF, DAT, SEG, IA, AE, OT |
| Codificación | Formato de IDs de documento y de regla | EST-INF-AWS-001, .R01 |
| Niveles de obligatoriedad | Palabras y significado de cada nivel | DEBE / DEBERÍA / PUEDE |
| Relaciones | Tipos de relación permitidos y su significado | deriva_de, depende_de, complementa, reemplaza |
| Ciclo de vida y aprobación | Estados, quién aprueba por dominio y cuántas aprobaciones se necesitan | Estándares de seguridad: arquitecto de seguridad + arquitecto empresarial |
| Versionado y revisión | Qué cambio es mayor, menor o parche, y la periodicidad de revisión | Revisión anual |
| Estilo de redacción | Tono, persona gramatical, longitud máxima de una regla, formato de fechas | Impersonal, una regla en máximo dos oraciones |
| Glosario corporativo | Términos aprobados, sinónimos prohibidos y definiciones | "Landing zone", no "zona de aterrizaje" |
| Fuentes | Sitios aprobados y su jerarquía de autoridad | Documentación oficial > marco de referencia > artículo técnico |
| Validación | Criterios, severidades y qué bloquea la aprobación | Una cita inexistente bloquea; un estilo irregular solo avisa |
| Principios | Texto de los principios corporativos | API-first, seguridad desde el diseño |
| Formato de salida | Plantilla Word corporativa única, con portada, encabezado, pie y marca de agua | Marca "Borrador" en documentos no aprobados |
Lo que no se configura. Cuatro reglas quedan fijas porque sostienen la coherencia: padre único, IDs únicos, cada tema en un solo lugar y nada se publica sin aprobación humana.
Cambios al perfil. Cada documento registra la versión del perfil y de la plantilla con que se redactó. Si cambia una plantilla o una regla del marco, el analista de impacto lista los documentos afectados y el redactor propone su migración como paquete de cambios.
## Construcción de documentos
Todos los documentos se redactan con la misma plantilla y el mismo formato de reglas, de modo que se lean y referencien igual sin importar el dominio.
Plantilla estándar. Es la plantilla inicial del perfil del marco; se ajusta desde la configuración, sin salir del catálogo de secciones:
- Ficha (los campos del mapa)
- Propósito
- Alcance y aplicabilidad (incluye y excluye)
- Documentos relacionados
- Definiciones
- Reglas
- Especificación técnica (solo estándares)
- Excepciones
- Cumplimiento y verificación
- Referencias
- Control de cambios
Formato de cada regla. ID <documento>.RNN, nivel DEBE / DEBERÍA / PUEDE, enunciado, justificación, cómo se verifica y fuentes. Una regla que necesita algo de otro documento lo referencia por su ID, nunca lo copia.
Orden de redacción. El orquestador recorre el grafo: primero fundacionales, después lineamientos y al final estándares. Un documento solo se redacta cuando su padre está aprobado y sus dependencias están al menos en revisión.
Ciclo de vida: propuesto → en redacción → en validación → en revisión humana → aprobado → obsoleto. Cada documento aprobado se revisa una vez al año.
Versionado. Cada documento lleva versión mayor.menor.parche:
- Mayor: cambia o elimina una regla DEBE.
- Menor: agrega reglas o cambia reglas DEBERÍA o PUEDE.
- Parche: mejora la redacción sin cambiar el significado.
Cada versión registra autor, fecha, motivo y el paquete de cambios que la originó. El mapa completo también tiene versión.
Formatos. El Markdown en GitHub es la fuente de verdad. Word se genera desde el Markdown con la plantilla corporativa, y PDF desde Word. Los borradores salen con marca "Borrador".
## Agentes y flujos de trabajo
Ocho agentes trabajan en tres flujos: construir el mapa, redactar cada documento y procesar nuevas necesidades. Ninguno cambia el mapa ni un documento sin aprobación humana.
> **Diagrama: tres flujos y una sola puerta — nada cambia sin aprobación humana**
>
> | Mapa | Documento | Nueva necesidad |
> |---|---|---|
> | Investigador — qué debe cubrir cada dominio | Investigador — fuentes para cada regla | Admisión — recibe y aclara la necesidad |
> | Taxonomista — documentos, tipo y relaciones | Redactor — plantilla y reglas con ID | Taxonomista — ¿nuevo, ampliación o cubierto? |
> | Validador — coherencia del mapa | Validador — calidad, citas, cinco miradas | Analista de impacto — arma el paquete de cambios |
> | Contraste — contra documentos existentes | Contraste — contra documentos existentes | Validador — mapa con el paquete aplicado |
>
> Los tres flujos convergen en **Revisión humana** (aprueba, ajusta o rechaza) → **Publicador** (nueva versión, Word y PDF).
Si la revisión humana pide ajustes, el flujo vuelve al taxonomista o al redactor con las observaciones del equipo. Un paquete de cambios aprobado dispara la redacción de los documentos afectados por el flujo de documento, y se publica completo o no se publica.
| Agente | Responsabilidad | Entrega |
| Investigador | Averigua qué debe cubrir cada dominio y reúne fuentes para cada regla | Temas y fuentes citables |
| Taxonomista | Evalúa los dominios propuestos, define documentos, aplica el test de clasificación y asigna padre y relaciones | Mapa propuesto con justificaciones |
| Redactor | Escribe el documento con la plantilla estándar y reglas con ID, referenciando otros documentos en vez de copiarlos | Borrador en Markdown |
| Validador | Revisa el mapa o el documento: plantilla, coherencia con padre y dependencias, citas reales y las miradas de datos, IA, infraestructura, seguridad y arquitectura empresarial | Informe de observaciones por severidad |
| Contraste | Compara el mapa o el documento con los existentes, después de la validación | Coincidencias y diferencias |
| Admisión | Recibe una necesidad nueva y pide aclaraciones si está incompleta | Necesidad estructurada |
| Analista de impacto | Identifica qué documentos cambian y cómo | Paquete de cambios |
| Publicador | Asigna versión, registra el cambio en GitHub y genera Word y PDF | Versión aprobada y archivos |
## Visualización y seguimiento
La solución ofrece seis vistas, todas generadas desde el mismo mapa versionado, para saber qué documentos existen, cómo se relacionan y en qué estado están.
| Vista | Qué muestra | Para qué sirve |
| Grafo | Documentos como nodos (forma por tipo, color por estado) y relaciones como aristas (estilo por tipo de relación). Filtros por dominio, tipo y estado | Ver cómo conversan los documentos y qué depende de qué; al elegir un nodo se resaltan sus dependientes |
| Por niveles | Matriz de dominios por nivel (fundacional, lineamiento, estándar), con cada documento y su estado | Ver de un vistazo qué ya tenemos y qué falta |
| Cobertura | Documentos por estado y dominio, revisiones anuales vencidas y observaciones abiertas | Seguir el avance del programa |
| Ficha e historial | Ficha del documento, versiones con autor, fecha y motivo, diferencias entre versiones regla por regla, y descarga de Word y PDF de cada versión | Auditar qué cambió, cuándo y por qué |
| Bandeja y revisión por regla | Borradores y paquetes pendientes; dentro de cada uno, cada regla con sus fuentes y las observaciones del validador, para aceptarla, rechazarla o comentarla | Revisar rápido y con precisión; solo las reglas rechazadas vuelven al redactor |
| Calidad de los agentes | Borradores aprobados sin cambios, observaciones más frecuentes por tipo, coincidencia con los casos de prueba y costo por ejecución | Saber cuándo ajustar prompts o reglas del marco |
## Insumos, fuentes y salvaguardas
Los agentes trabajan con cuatro tipos de insumo, cada uno con un uso distinto:
| Insumo | Forma de ingreso | Uso |
| Principios corporativos | Formulario de texto | Instrucciones que guían todas las decisiones |
| Contexto de arquitectura empresarial | Formulario estructurado: dominios propuestos, tecnologías por dominio, empresas del grupo, entorno OT/IT; diagrama del framework adjunto | Base para proponer dominios y documentos |
| Fuentes de conocimiento | Lista de sitios web aprobados y PDFs subidos (TOGAF, documentación de proveedores, marcos públicos) | Sustentar qué debe cubrir el mapa |
| Documentos existentes | PDFs o Word subidos | Solo contraste, nunca como base |
Salvaguardas:
- Primero a ciegas, después el contraste. El mapa se genera y valida sin ver los documentos existentes. Luego un paso de contraste muestra coincidencias, temas que ya cubren y el mapa omitió, y temas nuevos. Ninguna diferencia se incorpora sola.
- Citas verificables. Toda fuente citada debe existir y estar disponible; el validador lo comprueba.
- Contenido externo solo como dato. Páginas web y PDFs pueden traer instrucciones ocultas para manipular a los agentes. Los agentes las tratan como texto a analizar, nunca como órdenes, y ningún agente que lee fuentes puede escribir en el mapa.
- Control de costos. Cada ejecución tiene un presupuesto de tokens; si lo supera, se detiene y avisa. Un presupuesto mensual alerta sobre el consumo total.
- Licencias. Antes de cargar contenido de Gartner, revisar el contrato: suele restringir su uso en herramientas de IA generativa.
- Trazabilidad. Cada propuesta de un agente guarda su justificación y las fuentes que usó.
## Arquitectura técnica en AWS
Propuesta inicial en us-east-1, elegida para que una sola persona la construya y opere con apoyo de IA: servicios gestionados, sin servidores que administrar y con flujos deterministas y fáciles de depurar.
| Componente | Servicio propuesto | Nota |
| Interfaz web | Sitio estático en Amplify Hosting | Pantallas: insumos, vistas del mapa, documentos, bandeja de trabajo |
| Vista de grafo | Librería de grafos en el navegador (por ejemplo, Cytoscape.js) | Se alimenta del mapa versionado; no requiere base de datos de grafos |
| Inicio de sesión | Cognito con usuario y contraseña | Dos roles: administrador del marco (uno) y arquitecto. Más adelante se federa con Entra ID sin cambiar la aplicación |
| API | API Gateway + Lambda | Punto único de entrada para la web |
| Orquestación de flujos | AgentCore Runtime con Strands Agents | Cada flujo es una secuencia fija de agentes; queda registro de cada paso |
| Agentes | Strands Agents (Python) con Claude en Amazon Bedrock | Un agente por rol, con sus propias instrucciones y herramientas |
| Fuentes PDF | S3 + Bedrock Knowledge Bases | Búsqueda semántica con cita a la página de origen |
| Búsqueda web | API de búsqueda externa limitada a sitios aprobados | Proveedor por definir |
| Mapa y documentos (fuente de verdad) | Markdown con metadatos en GitHub, un archivo por documento | Acceso mediante un adaptador; pasar de cuenta personal a corporativa es solo configuración |
| Generación de Word y PDF | Lambda en contenedor con Pandoc y la plantilla Word corporativa; PDF con LibreOffice | Archivos de cada versión guardados en S3 |
| Estado de trabajo | DynamoDB | Solicitudes, ejecuciones, observaciones y aprobaciones |
| Secretos y registros | Secrets Manager + CloudWatch | Token de GitHub y claves de API; trazas de cada ejecución. AWS Budgets alerta el consumo mensual |
La web oculta Git: cada aprobación del equipo se convierte por detrás en un commit con autor, fecha y motivo.
## Stack tecnológico
Python en todo el backend, agentes con Strands sobre AgentCore, y una web estática en React: todo serverless y desplegable con un comando. Código y contenido viven en GitHub; el despliegue automático con GitHub Actions llega al pasar a producción.
| Capa | Elección | Por qué |
| Lenguaje del backend | Python | Mejor soporte para Bedrock, Strands, Pandoc y librerías de documentos |
| Framework de agentes | Strands Agents | Elegido por el equipo; cada flujo se arma como un grafo de agentes con orden fijo |
| Ejecución de agentes | Amazon Bedrock AgentCore Runtime | Sesiones largas sin los límites de tiempo de Lambda; trazas con AgentCore Observability |
| Modelos | Claude en Amazon Bedrock | Un modelo más capaz para redactor y validador, uno más rápido para tareas simples; configurable |
| API | API Gateway + Lambda en Python | Operaciones rápidas de la web: leer el mapa, registrar aprobaciones, lanzar flujos |
| Interfaz web | React + Vite + TypeScript, publicada como sitio estático en Amplify Hosting | Serverless y sin servidor que mantener; Amplify UI resuelve la pantalla de inicio de sesión con Cognito. Amplify se conecta al repositorio de GitHub y publica cada cambio |
| Grafo y diferencias | Cytoscape.js y una librería de diferencias de texto | Grafo interactivo en el navegador y comparación de versiones regla por regla |
| Generación de documentos | Pandoc con la plantilla Word corporativa; LibreOffice para PDF; ambos en Lambda con contenedor | Word fiel a los estilos corporativos sin maquetar a mano |
| Fuentes PDF | Bedrock Knowledge Bases sobre S3, con S3 Vectors como almacén vectorial | Opción gestionada y de bajo costo para el volumen esperado |
| Datos de trabajo | DynamoDB y S3 | Estado de ejecuciones y aprobaciones; archivos de cada versión |
| Repositorio | GitHub mediante su API, detrás de un adaptador | Pasar de cuenta personal a corporativa es solo configuración |
| Infraestructura como código | AWS CDK en Python, desplegado desde tu equipo con un comando | Reproducible en la cuenta corporativa; CI/CD con GitHub Actions solo cuando pase a producción |
| Pruebas | pytest y los casos de prueba como evaluación automática | Medir la calidad de los agentes en cada cambio |
| Lectura en Obsidian (opcional) | Los Markdown del repositorio se pueden abrir como bóveda de Obsidian | Navegación local extra, sin ser parte de la solución |
## Estructura de los repositorios
Se usan dos repositorios Git: uno para el código de la solución y otro para el contenido del marco. Así el contenido nunca depende de la aplicación, y cada repositorio puede moverse de cuenta o de proveedor por separado.
Código de la solución:
```
plataforma-lineamientos/
  infra/        CDK en Python, un stack por capa
  agents/       un módulo Strands por agente
    flows/      grafos: mapa, documento, nueva necesidad
  api/          Lambdas de la API
  docgen/       contenedor con Pandoc y LibreOffice
  web/          React + Vite
  evals/        casos de prueba y evaluador
  tests/
```
Contenido del marco:
```
marco-arquitectura/
  marco/              perfil del marco (solo el administrador)
    tipos.yaml  dominios.yaml  codificacion.yaml
    relaciones.yaml  estilo.yaml  validacion.yaml
    fuentes.yaml  glosario.yaml  principios.md
    plantillas/       una plantilla por tipo
    plantilla-word/   corporativa.docx
  documentos/
    FUN/  LIN/  EST/  un archivo <ID>.md por documento
```
- La ficha vive en el propio documento, como metadatos al inicio del Markdown. Un documento "propuesto" es un archivo con ficha y sin cuerpo; el mapa se arma leyendo todas las fichas.
- Cada paquete de cambios es una rama; aprobarlo en la web la fusiona. La web oculta todo esto.
- Versiones con etiquetas de Git: EST-INF-AWS-001@1.2.0 por documento y mapa@1.4.0 para el mapa completo.
## Plan de trabajo por fases
El plan construye primero la calidad de los agentes y después la interfaz, porque el mayor riesgo es que el mapa salga mal clasificado, no que falte una pantalla.
> **Diagrama: plan del MVP — cada fase cierra con una puerta de calidad antes de la siguiente**
>
> | Fase | Contenido | Puerta de salida |
> |---|---|---|
> | 0 · Marco documental configurable | Perfil inicial: tipos, plantillas, IDs, relaciones, estilo y glosario. Casos de prueba clasificados por el equipo | Reglas, plantilla y casos aprobados por el equipo |
> | 1 · Agentes del mapa | Investigador, taxonomista, validador y contraste, todavía sin interfaz. Mapa piloto del dominio de infraestructura | Coincidencia con casos de prueba sobre el umbral |
> | 2 · Agentes de redacción | Redactor y validador de documentos con la plantilla estándar. Primeros documentos piloto de infraestructura | Borradores aprobados por el arquitecto del dominio |
> | 3 · Nuevas necesidades y versionado | Admisión, análisis de impacto, paquetes de cambios y versionado. Publicador: Word y PDF con la plantilla corporativa | Paquete aplicado sin romper reglas del mapa |
> | 4 · Interfaz web | Grafo, niveles, cobertura, historial, bandeja y editor del marco. Revisión por regla, panel de calidad y costos, Cognito y Azure Repos | Un arquitecto opera los flujos sin ayuda |
> | 5 · Piloto con el equipo | Infraestructura completa, con sus dependencias en otros dominios. Ajustes y extensión al resto de dominios | Piloto aprobado por el equipo |
Los casos de prueba de la fase 0 son la pieza clave de calidad: un conjunto de temas reales que el equipo clasifica a mano (tipo, dominio, padre). En cada cambio de prompts o reglas, los agentes vuelven a clasificarlos y se mide la coincidencia. Como el constructor es una sola persona con apoyo de IA, cada fase termina en algo que funciona y se puede mostrar al equipo.
Después del MVP, en orden de valor propuesto:
- Agente vigía: dispara la revisión anual y avisa cuando cambia una fuente.
- Consulta en lenguaje natural sobre los documentos aprobados, para los equipos de proyecto.
- Checklists de cumplimiento generados desde el campo "cómo se verifica" de cada regla.
- Registro de excepciones con fecha de vencimiento.
- Notificaciones por correo o Teams.
- Publicación web para toda la empresa e inicio de sesión con Entra ID.
## Backlog de la fase 0
La fase 0 termina cuando el equipo aprueba el perfil inicial del marco y los casos de prueba. Casi todo es trabajo de definición; la parte técnica se limita a preparar la cuenta y los repositorios.
Definiciones del marco (redacta el administrador, revisa el equipo):
- Tipos de documento y test de clasificación
- Plantilla por tipo: secciones, orden, obligatoriedad e instrucciones de redacción
- Dominios iniciales con su código y dueño, incluida la decisión sobre OT
- Codificación de IDs, niveles de obligatoriedad y tipos de relación
- Ciclo de vida, aprobadores por dominio y reglas de versionado
- Guía de estilo de redacción
- Glosario inicial
- Sitios web aprobados como fuente y su jerarquía de autoridad
- Criterios de validación y qué bloquea la aprobación
- Principios corporativos
Casos de prueba (todo el equipo):
- Entre 30 y 50 temas reales clasificados a mano con tipo, dominio y padre (cantidad propuesta)
- Umbral de coincidencia para aprobar la fase 1
Preparación técnica (administrador):
- Crear los dos repositorios con la estructura base
- Habilitar el acceso a modelos Claude en Bedrock (us-east-1) en la cuenta piloto
- Preparar CDK en la cuenta piloto y crear una alerta de presupuesto
- Probar a mano la conversión de un Markdown a Word con la plantilla corporativa y ajustar sus estilos
Gestión:
- Revisar el contrato de Gartner sobre uso en IA
- Aprobación del perfil y de los casos de prueba por el equipo (puerta de salida)
## Supuestos y decisiones pendientes
Supuestos:
- "Fundamentos" significa documentos fundacionales transversales, como la clasificación por criticidad o la clasificación de la información.
- Los usuarios del MVP son los cinco arquitectos; todos pueden proponer, revisar y aprobar en su dominio.
- Solo un administrador del marco puede cambiar el perfil del marco.
- Hay una sola plantilla Word corporativa para todo el grupo.
- Bedrock con modelos Claude está disponible en us-east-1 para la cuenta que se use.
- La plantilla Word corporativa tiene estilos definidos para títulos, tablas y listas, de modo que se pueda usar como plantilla de generación.
Decisiones pendientes:
- ¿Quién es dueño de los documentos fundacionales? Sugerencia: el arquitecto empresarial.
- ¿Quién da la aprobación final: el arquitecto del dominio o el equipo completo?
- Lista inicial de dominios propuestos por el equipo, incluido si OT es un dominio propio.
- Lista de sitios web aprobados como fuente.
- Revisión del contrato de Gartner sobre uso en IA.
- Umbral de calidad para aprobar el MVP (propuesta: 90 % de coincidencia con los casos de prueba).
- Proveedor de la API de búsqueda web.
- Revisión de la plantilla Word corporativa para usarla en la generación automática.
