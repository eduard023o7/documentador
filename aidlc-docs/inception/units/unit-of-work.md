# Unidades de trabajo

Cada unidad se construye con las etapas de Construction definidas en `plans/execution-plan.md` y termina en una puerta de salida que apruebas.

## U0 · Fundación

| Aspecto | Contenido |
|---|---|
| Objetivo | Dejar escritas las reglas del juego y la base técnica para que los agentes trabajen sobre algo estable |
| Componentes | Estructura del monorepo, C1 (perfil y documento), C5 adaptador GitHub, C10 prueba de conversión, C15 infraestructura base, C12 CLI mínima (`doc perfil validar`) |
| Entregables | `contenido/marco/` completo (borrador de la IA aprobado por ti), plantillas por tipo, `pyproject.toml` y paquete `documentador`, stack CDK base (presupuesto USD 10 con alertas, bucket S3, Parameter Store, tabla DynamoDB), Word y PDF de ejemplo con la plantilla corporativa |
| Fuera | Agentes, base de conocimiento, web |
| Insumos que necesito de ti | Plantilla Word corporativa (`.docx`), acceso a la cuenta AWS para desplegar (desde tu equipo), un token de GitHub para el adaptador |
| Puerta de salida | Perfil y plantillas aprobados (`marco@1.0.0`); `doc perfil validar` pasa; despliegue base con alertas activo; Word/PDF de ejemplo aceptado por ti **con la plantilla corporativa** (se desarrolla con una genérica, F4=B) |
| Costo esperado | ≈ USD 0 (sin llamadas a modelos salvo la redacción asistida del perfil, que hago yo en esta sesión) |

## U1 · Mapa

| Aspecto | Contenido |
|---|---|
| Objetivo | Definir con ayuda de la IA los dominios y el mapa (fundacionales, lineamientos, estándares) con coherencia garantizada |
| Componentes | C1 (grafo, coherencia, IDs), C2 (investigador, taxonomista, validador, contraste), C3 flujo de mapa, C4 revisión con PR, C6 base de conocimiento con S3 Vectors, C8 estado, C9 costo, C11 evaluador, C12 CLI |
| Entregables | `doc insumos`, `doc fuentes`, `doc dominios evaluar`, `doc mapa generar`, `doc revisar`, `doc aprobar`, `doc evaluar`, `doc ejecuciones`; stack CDK de conocimiento y estado |
| Verificaciones previas | Modelos Claude habilitados en Bedrock us-east-1; rastreador web de la KB con S3 Vectors (si no, descarga a S3); costo medido de un flujo de mapa pequeño |
| Puerta de salida | Mapa piloto de infraestructura aprobado; evaluación de casos funcionando (umbral 90 % activo desde 30 casos) |
| Costo esperado | El mayor de las pruebas iniciales; tope por ejecución definido tras la medición |

## U2 · Redacción

| Aspecto | Contenido |
|---|---|
| Objetivo | Redactar bajo demanda documentos uniformes, sin redundancia y en armonía con el mapa |
| Componentes | C2 redactor (y validador ampliado), C3 flujo de documento y revalidación, C1 (versiones y diferencias por regla, `check_document`), C7 índice de reglas, C4 (rechazo por regla, aprobación con versión) |
| Entregables | `doc redactar`, revisión por regla en PR, revalidación automática de dependientes |
| Puerta de salida | Primeros documentos de infraestructura aprobados |

## U3 · Necesidades, versionado y publicación

| Aspecto | Contenido |
|---|---|
| Objetivo | Procesar cambios como paquetes atómicos y publicar Word/PDF de cada versión |
| Componentes | C2 admisión y analista de impacto, C3 flujo de necesidad y cambio de perfil, C4 aprobación de paquetes, C10 completo (Lambda contenedor `docgen`), revisión anual y obsolescencia |
| Entregables | `doc necesidad`, `doc publicar`, stack CDK de publicación |
| Puerta de salida | Un paquete aplicado sin romper reglas del mapa; Word y PDF publicados con la plantilla corporativa |

## U4 · Web

| Aspecto | Contenido |
|---|---|
| Objetivo | Operar todo desde la web, sin comandos ni Git |
| Componentes | C13 API, C14 web, C3 en AgentCore Runtime, Cognito, Amplify |
| Entregables | Inicio de sesión, insumos, seguimiento de flujos, grafo, niveles, cobertura, ficha e historial, bandeja y revisión por regla, revisión del mapa, editor del perfil, calidad y costos |
| Puerta de salida | Un integrante del equipo opera los flujos sin ayuda |

## Piloto (no es unidad de construcción)

Uso real con el equipo sobre infraestructura completa, ajustes y extensión a otros dominios; guía breve de uso. Puerta: piloto aprobado por el equipo.
