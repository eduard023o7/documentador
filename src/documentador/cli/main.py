"""`doc` command line. U0 commands: `perfil validar`, `publicar`, `estado verificar`."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Annotated

import boto3
import typer

from documentador.adapters.github import GitHubRepository
from documentador.adapters.state import DynamoStateStore
from documentador.common.errors import DocumentadorError
from documentador.config import Settings
from documentador.core.document import DocumentError, check_structure, parse_document
from documentador.core.profile import ProfileError, load_profile
from documentador.cost.routing import AGENTS, FLOWS, model_for
from documentador.publish.word import document_markdown, is_draft, render_docx, render_pdf

DEFAULT_PROFILE = Path("contenido/marco")
TEMPLATE_FILE = "plantilla-word/corporativa.docx"
EXAMPLE = Path(__file__).resolve().parents[1] / "publish" / "ejemplo.md"
CHECK_ITEM = {"PK": "VERIFICACION", "SK": "META"}

app = typer.Typer(help="Plataforma de lineamientos y estándares de arquitectura.", no_args_is_help=True)
perfil_app = typer.Typer(help="Perfil del marco documental.", no_args_is_help=True)
estado_app = typer.Typer(help="Conexión con AWS y GitHub.", no_args_is_help=True)
app.add_typer(perfil_app, name="perfil")
app.add_typer(estado_app, name="estado")

ProfileOption = Annotated[Path, typer.Option("--perfil", help="Carpeta del perfil del marco.")]


@perfil_app.command("validar")
def validate_profile(
    perfil: ProfileOption = DEFAULT_PROFILE,
    para_aprobar: Annotated[
        bool, typer.Option("--para-aprobar", help="Los valores 'POR DEFINIR' cuentan como error.")
    ] = False,
) -> None:
    """Valida el perfil del marco y muestra todos los errores y advertencias."""
    try:
        result = load_profile(perfil, for_approval=para_aprobar)
    except ProfileError as exc:
        typer.echo(f"✗ El perfil tiene {len(exc.issues)} error(es):", err=True)
        for issue in exc.issues:
            typer.echo(f"  - {issue}", err=True)
        raise typer.Exit(1) from exc
    typer.echo("✓ Perfil válido.")
    if result.warnings:
        typer.echo(f"{len(result.warnings)} advertencia(s):")
        for warning in result.warnings:
            typer.echo(f"  - {warning}")


@app.command("publicar")
def publish(
    archivo: Annotated[Path | None, typer.Argument(help="Documento Markdown a convertir.")] = None,
    ejemplo: Annotated[bool, typer.Option("--ejemplo", help="Usa el documento de ejemplo.")] = False,
    salida: Annotated[Path, typer.Option("--salida", help="Carpeta donde dejar Word y PDF.")] = Path(
        "salida"
    ),
    perfil: ProfileOption = DEFAULT_PROFILE,
    plantilla: Annotated[Path | None, typer.Option("--plantilla", help="Plantilla Word (.docx).")] = None,
    sin_pdf: Annotated[bool, typer.Option("--sin-pdf", help="Genera solo el Word.")] = False,
) -> None:
    """Convierte un documento a Word con la plantilla corporativa y luego a PDF."""
    if ejemplo == (archivo is not None):
        typer.echo("Indica un archivo o usa --ejemplo (solo uno de los dos).", err=True)
        raise typer.Exit(2)
    source = EXAMPLE if ejemplo else archivo
    assert source is not None
    try:
        profile = load_profile(perfil).profile
        doc = parse_document(source.read_text(encoding="utf-8"), profile)
        problems = check_structure(doc, profile)
        if problems:
            typer.echo("✗ El documento tiene problemas de estructura:", err=True)
            for problem in problems:
                typer.echo(f"  - {problem}", err=True)
            raise typer.Exit(1)
        template = plantilla or perfil / TEMPLATE_FILE
        docx = render_docx(document_markdown(doc, profile), template, draft=is_draft(doc))
        salida.mkdir(parents=True, exist_ok=True)
        word_path = salida / f"{doc.ficha.id}.docx"
        word_path.write_bytes(docx)
        typer.echo(f"✓ Word: {word_path}" + (" (con marca Borrador)" if is_draft(doc) else ""))
        if not sin_pdf:
            pdf_path = salida / f"{doc.ficha.id}.pdf"
            pdf_path.write_bytes(render_pdf(docx))
            typer.echo(f"✓ PDF: {pdf_path}")
    except (ProfileError, DocumentError, DocumentadorError, OSError) as exc:
        typer.echo(f"✗ {exc}", err=True)
        raise typer.Exit(1) from exc


@estado_app.command("verificar")
def verify(perfil: ProfileOption = DEFAULT_PROFILE) -> None:
    """Comprueba el acceso a los parámetros, la tabla, el bucket y GitHub."""
    settings = Settings()
    checks: list[tuple[str, Callable[[], str]]] = [
        ("Perfil del marco", lambda: _check_profile(perfil)),
        ("Parámetros de modelos y topes", lambda: _check_parameters(settings)),
        ("Tabla DynamoDB", lambda: _check_table(settings)),
        ("Bucket S3", lambda: _check_bucket(settings)),
        ("GitHub", lambda: _check_github(settings)),
    ]
    failures = 0
    for name, check in checks:
        try:
            typer.echo(f"✓ {name}: {check()}")
        except Exception as exc:  # report every check, whatever failed
            failures += 1
            typer.echo(f"✗ {name}: {exc}", err=True)
    if failures:
        raise typer.Exit(1)


def _check_profile(path: Path) -> str:
    result = load_profile(path)
    return f"válido ({len(result.warnings)} valores por definir)"


def _check_parameters(settings: Settings) -> str:
    models = {model_for(agent, settings).model_id for agent in AGENTS}
    for flow in FLOWS:
        float(settings.get(f"topes/{flow}"))
    for model in models:
        settings.get_json(f"precios/{model}")
    return f"{len(AGENTS)} agentes, {len(models)} modelos con precio, {len(FLOWS)} topes"


def _check_table(settings: Settings) -> str:
    name = settings.get("tabla")
    store = DynamoStateStore(name)
    store.put(dict(CHECK_ITEM))
    store.get(CHECK_ITEM["PK"], CHECK_ITEM["SK"])
    store.delete(CHECK_ITEM["PK"], CHECK_ITEM["SK"])
    return f"{name} (lectura y escritura)"


def _check_bucket(settings: Settings) -> str:
    name = settings.get("bucket")
    boto3.client("s3").head_bucket(Bucket=name)
    return name


def _check_github(settings: Settings) -> str:
    repo_name = settings.get("github/repo")
    repo = GitHubRepository(repo_name, settings.get("github/token"), settings.get("github/rama", "main"))
    files = repo.list_files("marco/")
    return f"{repo_name} ({len(files)} archivos del perfil en {repo.main})"


def main() -> None:
    app()


if __name__ == "__main__":
    main()
