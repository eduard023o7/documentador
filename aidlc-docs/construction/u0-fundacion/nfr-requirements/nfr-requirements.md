# Requisitos no funcionales del MVP (medibles)

Se definen en U0 y aplican a U0–U4. Cada uno amplía un RNF aprobado y dice cómo se comprueba. Decisión N1 = B.

## Costo (RNF-04, RNF-13)

| ID | Requisito | Cómo se comprueba |
|---|---|---|
| NFR-C1 | Presupuesto AWS de USD 10 para las pruebas iniciales, con alertas al 50 %, 80 % y 100 % al correo del Admin | AWS Budgets creado por CDK (prueba de infraestructura) |
| NFR-C2 | Ningún recurso de costo fijo mensual: sin NAT Gateway, OpenSearch Serverless, llaves KMS propias, instancias ni Secrets Manager | Prueba de la plantilla CDK que falla si aparece alguno |
| NFR-C3 | Cada ejecución tiene un tope en USD (por defecto: mapa USD 1,00; documento USD 0,60; necesidad USD 0,40; evaluación USD 0,20), configurable en Parameter Store | Prueba unitaria de `Budget`; la ejecución se detiene y queda "detenida" al superarlo |
| NFR-C4 | Cada paso registra modelo, tokens de entrada, salida y caché, y costo estimado | Registro del paso en DynamoDB; `doc ejecuciones <id>` lo muestra |
| NFR-C5 | Las instrucciones fijas de cada agente (sistema + perfil + plantilla) se marcan para caché de prompts | Tokens leídos de caché > 0 a partir de la segunda llamada de un mismo agente (prueba de integración) |
| NFR-C6 | Las pruebas unitarias y la mayor parte de las de flujo usan respuestas grabadas; solo `tests/integration` y `doc evaluar` llaman a Bedrock | Ejecutar `pytest tests/unit` sin credenciales de AWS pasa |

## Modelos (N1 = B)

| ID | Requisito |
|---|---|
| NFR-M1 | **Claude Sonnet 5.5** para taxonomista, redactor, validador y analista de impacto |
| NFR-M2 | **Claude Haiku 5.5** para investigador, contraste, admisión, evaluación de casos y tareas de clasificación simples |
| NFR-M3 | El modelo y el nivel de esfuerzo de cada agente se leen de Parameter Store; cambiarlos no requiere tocar código ni redesplegar |
| NFR-M4 | Respuesta de rechazo del modelo (`refusal`) o salida inválida: se reintenta una vez; si persiste, el paso falla con mensaje claro y la ejecución queda detenida sin escribir nada |
| NFR-M5 | Las salidas de los agentes son estructuradas (esquemas Pydantic) y se validan antes de usarse |

## Rendimiento y escala

| ID | Requisito |
|---|---|
| NFR-P1 | Flujo de mapa de un dominio < 15 min; redacción de un documento < 10 min; aprobación < 2 min; pantallas de la web < 2 s (p95) |
| NFR-P2 | Diseñado para 1 cuenta, ≤ 10 personas, ≤ 300 documentos y ≤ 5 ejecuciones simultáneas |
| NFR-P3 | Cargar el perfil y construir el grafo de 300 documentos toma < 2 s en local |

## Confiabilidad

| ID | Requisito |
|---|---|
| NFR-R1 | Sin acuerdo de disponibilidad; reintentos con espera exponencial ante errores transitorios de Bedrock, GitHub y AWS (máximo 3) |
| NFR-R2 | Una aprobación es todo o nada: si falla un paso (fusión, etiqueta, índice, publicación), se informa y se puede reintentar sin duplicar nada (operaciones idempotentes) |
| NFR-R3 | Una ejecución detenida conserva lo hecho y puede retomarse o descartarse |
| NFR-R4 | GitHub es la fuente de verdad; el estado de DynamoDB es reconstruible y no requiere respaldo |

## Seguridad mínima (RNF-05, RNF-06, RNF-14)

| ID | Requisito |
|---|---|
| NFR-S1 | Permisos IAM mínimos por función, generados por CDK; ningún permiso `*` sobre recursos salvo los que AWS exige |
| NFR-S2 | Cifrado en reposo y en tránsito con las opciones administradas por AWS; S3 con bloqueo de acceso público |
| NFR-S3 | Token de GitHub en Parameter Store SecureString; nunca en código, registros ni salidas de agentes; con permisos solo sobre este repositorio |
| NFR-S4 | Texto de fuentes externas entregado a los agentes entre delimitadores y declarado como material, nunca como instrucciones; agentes que leen fuentes sin herramientas de escritura |
| NFR-S5 | La API (U4) exige sesión de Cognito y valida tamaño y tipo de toda entrada |
| NFR-S6 | Toda aprobación y rechazo queda registrado con nombre del revisor, fecha y commit |

## Mantenibilidad y calidad (RNF-11)

| ID | Requisito |
|---|---|
| NFR-Q1 | Núcleo (C1) con ≥ 90 % de cobertura de líneas |
| NFR-Q2 | Cada criterio de aceptación de una historia tiene al menos una prueba |
| NFR-Q3 | Formato y estilo de código con `ruff`; tipos con `mypy` en modo estricto para `core/` |
| NFR-Q4 | Evaluación de clasificación ≥ 90 % de coincidencia desde 30 casos (RF-37) |

## Operación y registros (RNF-03)

| ID | Requisito |
|---|---|
| NFR-O1 | Registros en CloudWatch con 14 días de retención; en local, registro en consola y en el estado de la ejecución |
| NFR-O2 | Mensajes de error y de estado en español claro, con la acción sugerida |

## Portabilidad (RNF-10)

| ID | Requisito |
|---|---|
| NFR-X1 | `contenido/` se puede mover a otro repositorio cambiando solo la configuración del adaptador |
| NFR-X2 | Toda la infraestructura se crea y se destruye con CDK (`cdk deploy` / `cdk destroy`) |
