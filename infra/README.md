# Infraestructura del documentador (AWS CDK)

Stack `DocumentadorBase` en **us-east-1**: presupuesto de USD 10 con avisos, bucket S3 privado, tabla DynamoDB bajo demanda, parámetros `/documentador/*` y la política IAM `documentador-operador`. Costo mensual esperado: prácticamente cero.

## Requisitos en tu equipo

- Python 3.12 o superior y [`uv`](https://docs.astral.sh/uv/)
- Node.js 18 o superior (para el CLI de CDK vía `npx`)
- AWS CLI v2
- Pandoc y LibreOffice (solo para generar Word y PDF)

## Despliegue con usuario IAM y llaves de acceso

1. **Configura tus credenciales** en un perfil propio:
   ```bash
   aws configure --profile documentador      # llave, secreto, región us-east-1, salida json
   export AWS_PROFILE=documentador
   aws sts get-caller-identity               # anota el número de cuenta
   ```
   El usuario que despliega necesita permisos para crear stacks (CloudFormation, S3, DynamoDB, SSM, IAM y Budgets). Si es administrador de la cuenta piloto, alcanza.

2. **Instala las dependencias** (en la raíz del repositorio):
   ```bash
   uv sync --group infra
   ```

3. **Arranca CDK en la cuenta** (una sola vez por cuenta y región):
   ```bash
   cd infra
   npx aws-cdk@2 bootstrap aws://<cuenta>/us-east-1
   ```

4. **Despliega el stack** con el correo que recibirá los avisos de presupuesto:
   ```bash
   npx aws-cdk@2 deploy DocumentadorBase -c correoAvisos=<tu correo>
   ```
   Los avisos de AWS Budgets llegan por correo sin necesidad de confirmar suscripción.

5. **Crea el token de GitHub** en GitHub → Settings → Developer settings → Fine-grained tokens:
   - Repository access: *Only select repositories* → `eduard023o7/documentador`
   - Permissions: **Contents** lectura y escritura, **Pull requests** lectura y escritura (Metadata queda en lectura)

   Guárdalo cifrado en Parameter Store (CloudFormation no puede crear parámetros cifrados):
   ```bash
   read -s TOKEN && aws ssm put-parameter --name /documentador/github/token \
     --type SecureString --value "$TOKEN" && unset TOKEN
   ```

6. **Permisos de uso diario.** Si usas `doc` con un usuario que no es administrador, asócialo a la política del stack (el comando exacto aparece en la salida `AsociarPolitica`):
   ```bash
   aws iam attach-user-policy --user-name <tu-usuario> --policy-arn <arn de documentador-operador>
   ```

7. **Verifica** (en la raíz del repositorio):
   ```bash
   uv run doc estado verificar
   ```
   Debe mostrar ✓ en perfil, parámetros, tabla, bucket y GitHub. GitHub lee la rama indicada en `/documentador/github/rama` (por defecto `main`).

## Cambiar valores (modelos, precios, topes)

Los valores iniciales están en `documentador_infra/valores.py`. Cámbialos ahí y vuelve a desplegar. Un cambio hecho a mano en la consola sirve para probar, pero el siguiente `deploy` lo reemplaza.

**Antes de U1:** reemplaza los precios de referencia por los de Bedrock en us-east-1 y confirma los IDs de los modelos.

## Eliminar todo

```bash
aws s3 rm s3://documentador-<cuenta>-archivos --recursive
npx aws-cdk@2 destroy DocumentadorBase
aws ssm delete-parameter --name /documentador/github/token
```

## Pruebas de la plantilla

```bash
uv run --group infra pytest infra/tests
```
Fallan si aparece un recurso de costo fijo, un permiso con `*`, un bucket público o sin HTTPS, o si falta algún aviso del presupuesto.
