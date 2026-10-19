# Componentes lógicos para los requisitos no funcionales

| Pieza | Módulo | Patrón | Se construye en |
|---|---|---|---|
| `Settings` (lectura de Parameter Store y `config/local.yaml`) | `documentador.config` | P2, P7 | U0 |
| `with_retries` | `documentador.common.retry` | P4 | U0 |
| Registro estructurado y filtro de secretos | `documentador.common.logging` | P7, P8 | U0 |
| Errores con mensaje para el usuario | `documentador.common.errors` | P8 | U0 |
| `Budget`, `BudgetExceeded`, tabla de precios | `documentador.cost` | P1 | U0 (clase), U1 (hook en agentes) |
| `model_for` / `ModelConfig` | `documentador.cost.routing` | P2 | U0 (lectura), U1 (uso) |
| Interfaces de adaptadores + versiones en memoria | `documentador.adapters.*` | P10 | U0 (`ContentRepository`, `StateStore`), U1–U2 (resto) |
| Envoltorio de material externo | `documentador.agents.material` | P6 | U1 |
| Validación de salidas y reintento | `documentador.agents.structured` | P3 | U1 |
| Orquestador de aprobación por pasos | `documentador.review.approval` | P5 | U1 |
| Pruebas de plantilla CDK (sin costo fijo, sin `*`) | `infra/tests` | P9, NFR-C2 | U0 |
