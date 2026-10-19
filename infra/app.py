#!/usr/bin/env python3
"""CDK app. Usage: cdk deploy DocumentadorBase -c correoAvisos=<correo>."""

import aws_cdk as cdk
from documentador_infra.base_stack import BaseStack

REGION = "us-east-1"

app = cdk.App()
email = app.node.try_get_context("correoAvisos")
if not email:
    raise SystemExit("Falta el correo para los avisos de presupuesto: usa -c correoAvisos=<correo>.")
BaseStack(
    app,
    "DocumentadorBase",
    alert_email=email,
    github_repo=app.node.try_get_context("repoGithub") or "eduard023o7/documentador",
    env=cdk.Environment(region=REGION),
    description="Documentador U0: presupuesto, archivos, estado, parámetros y política de operador.",
)
cdk.Tags.of(app).add("proyecto", "documentador")
app.synth()
