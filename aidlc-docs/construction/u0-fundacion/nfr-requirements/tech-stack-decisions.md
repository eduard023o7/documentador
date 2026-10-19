# Decisiones de stack tecnológico

| Capa | Decisión | Motivo | Se verifica en |
|---|---|---|---|
| Lenguaje | Python 3.12 | Soporte de Strands, CDK, Pandoc y python-docx | — |
| Gestión de dependencias | `pyproject.toml` con versiones fijadas; `uv` para instalar | Rápido y reproducible | Generación de código U0 |
| Modelos de datos | Pydantic v2 | Validación del perfil, fichas y salidas de agentes | U0 |
| YAML / front matter | `ruamel.yaml` (conserva orden y comentarios) | Ida y vuelta estable de archivos (BR-U0-20) | U0 |
| CLI | Typer | Comandos `doc …` en español, con ayuda automática | U0 |
| Agentes | Strands Agents sobre Amazon Bedrock | Elegido en el doc; un agente por rol, flujos de orden fijo | Diseño de infraestructura U1 |
| Modelo capaz | Claude Sonnet 5.5 (`anthropic.claude-sonnet-5-5` en Bedrock) | N1 = B | ID exacto, perfil de inferencia y precio en us-east-1: diseño de infraestructura U1 |
| Modelo económico | Claude Haiku 5.5 (`anthropic.claude-haiku-5-5` en Bedrock) | N1 = B | Ídem |
| Configuración de modelos | Esfuerzo `medium` para Sonnet en redacción y validación, `low` en tareas simples; Haiku con esfuerzo `low`; pensamiento adaptativo (en estos modelos no se desactiva) | Equilibrio costo/calidad; se ajusta con la evaluación | Diseño NFR U0 / evaluación U1 |
| Caché de prompts | Puntos de caché tras las instrucciones del sistema, el perfil y la plantilla | Reduce el costo de entrada en llamadas repetidas | Prueba de integración U1 |
| Embeddings | Amazon Titan Text Embeddings V2 | Multilingüe y el más barato de Bedrock | Diseño de infraestructura U1 |
| Base de conocimiento | Bedrock Knowledge Bases con S3 Vectors | RNF-13, S6 | Diseño de infraestructura U1 (incluye rastreador web) |
| Índice de reglas | S3 Vectors (índice propio) | Costo casi nulo | U2 |
| Estado | DynamoDB bajo demanda, una tabla | D3 = A | U1 |
| Repositorio | GitHub REST API con `httpx` (sin clonar) | Simple, sin dependencias de Git en Lambda | U0 |
| Documentos | Pandoc 3 + LibreOffice (sin pantalla) + python-docx (marca de agua) | RF-17 | U0 (local), U3 (Lambda contenedor) |
| Infraestructura | AWS CDK v2 en Python | Un comando para crear y destruir | U0 |
| Pruebas | pytest, pytest-cov, moto (AWS simulado), respuestas grabadas de modelos | NFR-C6, NFR-Q1 | U0 |
| Calidad de código | ruff, mypy (estricto en `core/`) | NFR-Q3 | U0 |
| Web (U4) | React + Vite + TypeScript, Amplify Hosting, Amplify UI, Cytoscape.js, librería de diferencias | Del doc | U4 |
| Ejecución de agentes en U4 | AgentCore Runtime | D1 = A | U4 |

**Descartados:** OpenSearch Serverless (costo fijo), Secrets Manager (costo por secreto, se usa Parameter Store), buscador web externo en el MVP (S6), Opus 5.5 (N1 = B; se puede activar por agente en Parameter Store si la evaluación lo pide).
