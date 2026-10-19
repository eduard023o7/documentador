# U0 · Arquitectura de despliegue

```
Tu equipo                                   AWS us-east-1 (cuenta piloto)
┌──────────────────────────┐               ┌───────────────────────────────────────┐
│ cdk deploy               │──CloudFormation▶ Stack DocumentadorBase                │
│                          │               │  ├─ Budget USD 10 ──▶ correo de avisos │
│ doc … (CLI, Python 3.12) │               │  ├─ S3 documentador-<cuenta>-archivos  │
│   credenciales AWS con   │──API AWS─────▶│  ├─ DynamoDB documentador-estado       │
│   política operador      │               │  ├─ SSM /documentador/*                │
│                          │               │  └─ IAM política documentador-operador │
│                          │               └───────────────────────────────────────┘
│                          │──API GitHub──▶ github.com/eduard023o7/documentador (contenido/)
└──────────────────────────┘
```

## Pasos de despliegue (los ejecutas tú; quedarán en `infra/README.md`)

1. Requisitos en tu equipo: Python 3.12, `uv`, Node.js (para el CLI de CDK), AWS CLI con credenciales de la cuenta piloto, Pandoc y LibreOffice (para la prueba de Word/PDF).
2. Una sola vez por cuenta y región: `cdk bootstrap aws://<cuenta>/us-east-1`.
3. `cd infra && cdk deploy DocumentadorBase -c correoAvisos=<tu correo>`.
4. Confirmar la suscripción en el correo que envía AWS Budgets, si aplica.
5. Crear el token de GitHub y guardarlo con `aws ssm put-parameter …` (ver diseño de infraestructura).
6. Asociar la política `documentador-operador` a tu usuario o rol (el comando exacto sale en las salidas del stack).
7. Verificar: `doc perfil validar` y `doc estado verificar` (comprueba acceso a la tabla, el bucket, los parámetros y GitHub).

Para eliminar todo: `cdk destroy DocumentadorBase` y borrar el parámetro del token.
