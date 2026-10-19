import boto3
from moto import mock_aws
from typer.testing import CliRunner

from documentador.cli import main as cli
from documentador.cli.main import app

from ..conftest import MARCO
from .test_cost import HAIKU, SONNET

runner = CliRunner()


def test_validate_real_profile():
    result = runner.invoke(app, ["perfil", "validar", "--perfil", str(MARCO)])
    assert result.exit_code == 0, result.output
    assert "✓ Perfil válido." in result.output and "advertencia" in result.output


def test_validate_for_approval_fails_on_pending():
    result = runner.invoke(app, ["perfil", "validar", "--perfil", str(MARCO), "--para-aprobar"])
    assert result.exit_code == 1 and "valor por definir" in result.output


def test_validate_reports_errors(profile_dir):
    (profile_dir.path / "niveles.yaml").unlink()
    result = runner.invoke(app, ["perfil", "validar", "--perfil", str(profile_dir.path)])
    assert result.exit_code == 1 and "niveles.yaml — falta el archivo" in result.output


def test_publish_requires_exactly_one_source():
    assert runner.invoke(app, ["publicar"]).exit_code == 2


def test_publish_example(tmp_path):
    result = runner.invoke(app, ["publicar", "--ejemplo", "--perfil", str(MARCO), "--salida", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "EST-INF-AWS-001.docx").exists() and (tmp_path / "EST-INF-AWS-001.pdf").exists()
    assert "Borrador" in result.output


def test_publish_rejects_bad_document(tmp_path):
    bad = tmp_path / "x.md"
    bad.write_text(cli.EXAMPLE.read_text().replace("dominio: INF", "dominio: XYZ"))
    result = runner.invoke(
        app, ["publicar", str(bad), "--perfil", str(MARCO), "--salida", str(tmp_path), "--sin-pdf"]
    )
    assert result.exit_code == 1 and "dominio desconocido" in result.output


@mock_aws
def test_verify(monkeypatch, tmp_path):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    ssm = boto3.client("ssm", region_name="us-east-1")
    for agent in cli.AGENTS:
        model = SONNET if agent in ("taxonomista", "redactor", "validador", "impacto") else HAIKU
        ssm.put_parameter(
            Name=f"/documentador/modelos/{agent}",
            Value=f'{{"modelo": "{model}", "esfuerzo": "low"}}',
            Type="String",
        )
    for model in (SONNET, HAIKU):
        ssm.put_parameter(
            Name=f"/documentador/precios/{model}", Value='{"entrada": 1, "salida": 2}', Type="String"
        )
    for flow in cli.FLOWS:
        ssm.put_parameter(Name=f"/documentador/topes/{flow}", Value="1.0", Type="String")
    ssm.put_parameter(Name="/documentador/tabla", Value="documentador-estado", Type="String")
    ssm.put_parameter(Name="/documentador/bucket", Value="documentador-archivos", Type="String")
    ssm.put_parameter(Name="/documentador/github/repo", Value="org/repo", Type="String")
    ssm.put_parameter(Name="/documentador/github/token", Value="ghp_x", Type="SecureString")
    boto3.client("s3", region_name="us-east-1").create_bucket(Bucket="documentador-archivos")
    boto3.client("dynamodb", region_name="us-east-1").create_table(
        TableName="documentador-estado",
        KeySchema=[{"AttributeName": "PK", "KeyType": "HASH"}, {"AttributeName": "SK", "KeyType": "RANGE"}],
        AttributeDefinitions=[
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "SK", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    monkeypatch.setattr(cli.GitHubRepository, "list_files", lambda self, prefix="", ref=None: ["marco/tipos.yaml"])
    monkeypatch.chdir(tmp_path)  # no config/local.yaml here
    result = runner.invoke(app, ["estado", "verificar", "--perfil", str(MARCO)])
    assert result.exit_code == 0, result.output
    assert result.output.count("✓") == 5


@mock_aws
def test_verify_reports_failures(monkeypatch, tmp_path):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["estado", "verificar", "--perfil", str(MARCO)])
    assert result.exit_code == 1
    assert "✓ Perfil del marco" in result.output and "✗ Tabla DynamoDB" in result.output
