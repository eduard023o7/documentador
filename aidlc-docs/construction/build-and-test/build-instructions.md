# Instrucciones de build (U0)

## En tu equipo

```bash
git clone https://github.com/eduard023o7/documentador.git && cd documentador
git checkout claude/peaceful-einstein-qc6q6f      # hasta que se fusione a main
uv sync                                           # Python ≥ 3.12, dependencias de desarrollo y CDK
uv run doc --help                                 # comprueba que el comando quedó instalado
```

Herramientas externas: Node.js ≥ 18 (CDK), AWS CLI v2, Pandoc y LibreOffice (Word y PDF).

## Calidad de código

```bash
uv run ruff check src tests infra
uv run ruff format --check src tests infra
uv run mypy src
```

## Paquete instalable (opcional)

```bash
uv build      # genera dist/documentador-0.1.0-py3-none-any.whl
```

## Despliegue

Sigue [`infra/README.md`](../../../infra/README.md): `cdk bootstrap`, `cdk deploy DocumentadorBase -c correoAvisos=<correo>`, token de GitHub en Parameter Store y, si tu usuario no es administrador, la política `documentador-operador`.
