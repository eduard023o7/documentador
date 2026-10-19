# U0 · Diseño de infraestructura

Región us-east-1, una cuenta, AWS CDK v2 en Python (`infra/`). Etiqueta común en todo: `proyecto=documentador`.

## Stack `DocumentadorBase` (U0)

| Recurso | Configuración | Requisitos |
|---|---|---|
| **Presupuesto** `documentador-pruebas` | Costo mensual USD 10; avisos por correo al 50 % y 80 % (real) y al 100 % (real y pronosticado) | NFR-C1 |
| **Bucket S3** `documentador-<cuenta>-archivos` | Bloqueo de acceso público total; cifrado SSE-S3; solo HTTPS; sin versionado (costo); regla de vida que borra `tmp/` a los 7 días; se elimina con el stack (todo su contenido se regenera desde Git) | NFR-S2, NFR-C2, NFR-X2 |
| **Tabla DynamoDB** `documentador-estado` | Bajo demanda; claves `PK`/`SK` (texto); índice `GSI1` (`GSI1PK`/`GSI1SK`); cifrado con llave de AWS; sin recuperación a un punto en el tiempo; atributo TTL `expira` | D3, NFR-R4, NFR-C2 |
| **Parámetros SSM** `/documentador/…` | `github/repo`, `github/rama`, `tabla`, `bucket`, `modelos/<agente>` (JSON: modelo, esfuerzo, máx. tokens), `precios/<modelo>` (JSON por millón de tokens), `topes/<flujo>` (USD) — todos tipo `String`, nivel estándar (gratis) | P2, P7, NFR-M3, NFR-C3 |
| **Política IAM** `documentador-operador` | Para la identidad con la que corres `doc` en tu equipo. Lectura/escritura en la tabla y su índice; lectura/escritura en el bucket; lectura de `/documentador/*` y descifrado con la llave `aws/ssm` solo vía SSM. En U1 se agrega invocar los modelos Sonnet 5.5, Haiku 5.5 y Titan Embeddings | P9, NFR-S1 |

**Token de GitHub (SecureString):** CloudFormation no puede crear parámetros SecureString, así que se crea una vez a mano con un comando (queda en la guía de despliegue):
```
aws ssm put-parameter --name /documentador/github/token --type SecureString --value <token>
```
Token "fine-grained" con permisos solo sobre este repositorio: *Contents* y *Pull requests* de lectura y escritura.

**Valores iniciales de parámetros:**

| Parámetro | Valor |
|---|---|
| `modelos/taxonomista`, `redactor`, `validador`, `impacto` | Sonnet 5.5, esfuerzo `medium` |
| `modelos/investigador`, `contraste`, `admision`, `evaluador` | Haiku 5.5, esfuerzo `low` |
| `precios/*` | Tarifa de referencia; se reemplaza por la de Bedrock al verificarla (antes de U1) |
| `topes/mapa`, `documento`, `necesidad`, `evaluacion` | 1,00 · 0,60 · 0,40 · 0,20 USD |

Los IDs exactos de los modelos en Bedrock se fijan en el diseño de infraestructura de U1; en U0 los parámetros llevan el ID de referencia.

## Lo que no se crea en U0

Lambdas, API Gateway, Cognito, Amplify, Knowledge Base, S3 Vectors, AgentCore y grupos de logs llegan en sus unidades (U1, U3, U4). Así U0 cuesta prácticamente cero.

## Pruebas de la plantilla (P9, NFR-C2)

`infra/tests/test_base_stack.py` sintetiza el stack y falla si:
- aparece un recurso de costo fijo (NAT Gateway, OpenSearch, KMS Key, instancias EC2/RDS, Secrets Manager);
- una política IAM usa `"Action": "*"` o `"Resource": "*"` fuera de las excepciones documentadas;
- el bucket no bloquea el acceso público o no exige HTTPS;
- falta el presupuesto con sus tres avisos.

## Costo esperado de U0

| Recurso | Costo mensual |
|---|---|
| Presupuesto (los dos primeros son gratis) | USD 0 |
| S3 (pocos MB) | < USD 0,01 |
| DynamoDB bajo demanda (casi sin uso) | < USD 0,01 |
| Parámetros SSM estándar | USD 0 |
| Arranque de CDK (bucket y repositorio de imágenes vacíos) | < USD 0,01 |
