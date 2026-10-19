# Patrones de diseño NFR

Patrones transversales; U0 crea su base y U1–U4 los reutilizan.

## P1 · Guardia de presupuesto (NFR-C3, C4)
- Cada ejecución crea un `Budget(limit_usd)` con el tope del tipo de flujo leído de Parameter Store.
- Un **hook** de Strands, registrado en todos los agentes, recibe el uso de tokens de cada llamada al modelo (entrada, salida, caché leída y escrita), calcula el costo con la tabla de precios por modelo (Parameter Store) y llama a `Budget.charge`.
- Antes de cada llamada se comprueba que quede saldo para el peor caso de esa llamada (`max_tokens` × precio de salida); si no alcanza, se lanza `BudgetExceeded` sin llamar al modelo.
- `BudgetExceeded` detiene el flujo: se guarda lo hecho, la ejecución queda `detenida` con el motivo y no se abre PR.
- La tabla de precios es configuración, no código: al verificar los precios de Bedrock se actualiza sin redesplegar.

## P2 · Enrutador de modelos (NFR-M1 a M3)
- `model_for(agent) -> ModelConfig(model_id, effort, max_tokens)` lee `/documentador/modelos/<agente>` en Parameter Store con caché en memoria de 5 minutos.
- Valores iniciales: Sonnet 5.5 (esfuerzo `medium`) para taxonomista, redactor, validador e impacto; Haiku 5.5 (esfuerzo `low`) para investigador, contraste, admisión y evaluación.
- En local, un archivo `config/local.yaml` puede sobrescribir los valores (útil para pruebas con un modelo más barato).

## P3 · Salidas estructuradas y validadas (NFR-M4, M5)
- Cada agente declara su esquema de salida (Pydantic) y Strands lo solicita como salida estructurada.
- Validación al recibir: si falla o el modelo rechaza (`refusal`), un reintento con el error de validación como contexto; si vuelve a fallar, el paso termina en error con mensaje claro y nada se escribe.

## P4 · Reintentos con espera exponencial (NFR-R1)
- Decorador común `with_retries(max=3, base=1s, jitter)` para errores transitorios: limitación de velocidad (429), 5xx, cortes de red. Nunca reintenta errores 4xx de validación o permisos.
- Se aplica en los adaptadores (Bedrock, GitHub, AWS), no en la lógica de negocio.

## P5 · Aprobación idempotente en pasos (NFR-R2)
- La aprobación es una secuencia de pasos con estado guardado en DynamoDB (`APR#…`): revalidar → fusionar → etiquetar → indexar reglas → marcar dependientes → publicar.
- Cada paso comprueba si ya está hecho antes de actuar (PR ya fusionado, etiqueta ya existe con el mismo commit, vector ya indexado). Reintentar la aprobación continúa desde el paso fallido.
- Si falla la revalidación, no se toca nada. Si falla un paso posterior a la fusión, el contenido ya aprobado queda en `main` y el reintento completa el resto.

## P6 · Fuentes externas como datos (NFR-S4)
- El texto de fuentes se entrega al agente dentro de `<material fuente="…" origen="…">…</material>`, y las instrucciones del sistema dicen que todo lo que está dentro es material para analizar, nunca órdenes.
- Investigador y contraste solo tienen herramientas de búsqueda; ningún agente tiene herramientas de escritura. La escritura solo ocurre en C4 con aprobación humana.
- Se eliminan del material caracteres de control y etiquetas que imiten los delimitadores.

## P7 · Configuración y secretos (NFR-S3)
- Parámetros bajo `/documentador/…`: `github/token` (SecureString), `github/repo`, `modelos/<agente>`, `precios/<modelo>`, `topes/<flujo>`.
- Lectura con caché en memoria; en desarrollo local se admite la variable de entorno `DOCUMENTADOR_GITHUB_TOKEN`.
- Un filtro de registros enmascara cualquier cadena con forma de token de GitHub (`ghp_…`, `github_pat_…`).

## P8 · Registro estructurado (NFR-O1, O2)
- Registros JSON con `run_id`, `paso`, `agente`, `modelo`, `tokens`, `costo`, `duracion_ms`. En local, salida legible en consola.
- Mensajes al usuario en español, con la acción sugerida ("Falta el nombre del revisor: usa --revisor \"Nombre\"").

## P9 · Permisos mínimos (NFR-S1)
- Un rol IAM por pieza (desarrollador local, funciones Lambda en U3/U4, AgentCore en U4) con permisos sobre recursos concretos (la tabla, el bucket, los parámetros `/documentador/*`, los modelos usados).
- Prueba de la plantilla CDK que falla ante acciones `*` o recursos `*` no justificados.

## P10 · Pruebas sin costo (NFR-C6, Q1, Q2)
- Adaptadores con interfaz (`ContentRepository`, `StateStore`, `KnowledgeBase`, `RuleIndex`, `ModelClient`) e implementaciones en memoria para pruebas.
- Respuestas de modelos grabadas en `tests/fixtures/llm/` y reproducidas por un `ModelClient` falso.
- `moto` simula DynamoDB, S3 y Parameter Store en pruebas de adaptadores.
- `pytest -m integration` es lo único que usa AWS y GitHub reales.
