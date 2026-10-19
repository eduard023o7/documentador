"""Documents, rules and IDs: business rules BR-U0-16 to BR-U0-20."""

from pathlib import Path

import pytest

from documentador.core.document import (
    Document,
    DocumentError,
    Ficha,
    Rule,
    check_structure,
    document_path,
    extract_references,
    parse_document,
    render_document,
)
from documentador.core.ids import format_document_id, format_rule_id, parse_document_id, parse_rule_id
from documentador.core.profile import load_profile

from ..conftest import MARCO

EXAMPLE = Path(__file__).resolve().parents[2] / "src" / "documentador" / "publish" / "ejemplo.md"


@pytest.fixture(scope="module")
def profile():
    return load_profile(MARCO).profile


def make_standard(estado="en_validacion", **changes) -> Document:
    ficha = Ficha(
        id="EST-INF-AWS-001",
        titulo="Landing zone en AWS",
        tipo="estandar",
        dominio="INF",
        tecnologia="AWS",
        padre="LIN-INF-001",
        relaciones=[{"tipo": "depende_de", "destino": "LIN-SEG-002"}],
        alcance={"incluye": ["OUs", "SCPs"], "excluye": ["redes on-premise"]},
        justificacion="Nombra un producto y fija valores verificables.",
        fuentes=[{"titulo": "AWS Well-Architected", "ubicacion": "kb://aws-wa.pdf#p12"}],
        prioridad="alta",
        estado=estado,
    )
    sections = {
        "proposito": "Definir la estructura base de cuentas en AWS.",
        "alcance": "Aplica a todas las cuentas del grupo.",
        "relacionados": "- [[LIN-INF-001]]\n- [[LIN-SEG-002]]",
        "reglas": "Reglas de la landing zone.",
        "especificacion": "| OU | Uso |\n|---|---|\n| Prod | Producción |",
        "excepciones": "Se solicitan al arquitecto de infraestructura.",
        "cumplimiento": "Revisión trimestral de la estructura de OUs.",
        "referencias": "AWS Control Tower.",
        "control_cambios": "| Versión | Fecha | Motivo |\n|---|---|---|",
    }
    rules = [
        Rule(
            id="EST-INF-AWS-001.R01",
            nivel="DEBE",
            enunciado="Cada entorno tiene una cuenta separada.",
            justificacion="Aísla fallas y permisos; cumple [[LIN-INF-001.R02]].",
            verificacion="La OU de cada entorno contiene solo sus cuentas.",
            fuentes="[AWS Well-Architected, p. 12](kb://aws-wa.pdf#p12)",
        ),
        Rule(
            id="EST-INF-AWS-001.R02",
            nivel="DEBERÍA",
            enunciado="Las cuentas usan SCPs heredadas de su OU.",
            justificacion="Evita configuraciones manuales\ndiferentes por cuenta.",
            verificacion="No hay SCPs asignadas directamente a cuentas.",
            fuentes="Documentación de AWS Organizations.",
        ),
    ]
    doc = Document(ficha=ficha, sections=sections, rules=rules)
    if changes:
        doc = Document(
            ficha=Ficha.model_validate({**ficha.model_dump(), **changes.get("ficha", {})}),
            sections=changes.get("sections", sections),
            rules=changes.get("rules", rules),
        )
    return doc


# BR-U0-20: canonical round trip
def test_round_trip_is_stable(profile):
    text = render_document(make_standard(), profile)
    assert render_document(parse_document(text, profile), profile) == text


def test_example_round_trip(profile):
    text = EXAMPLE.read_text(encoding="utf-8")
    assert render_document(parse_document(text, profile), profile) == text
    assert text == render_document(make_standard(), profile)


def test_parse_reads_ficha_sections_and_rules(profile):
    doc = parse_document(render_document(make_standard(), profile), profile)
    assert doc.ficha.relaciones[0].destino == "LIN-SEG-002"
    assert list(doc.sections)[0] == "proposito"
    assert doc.sections["reglas"] == "Reglas de la landing zone."
    assert [r.nivel for r in doc.rules] == ["DEBE", "DEBERÍA"]
    assert doc.rules[1].justificacion == "Evita configuraciones manuales\ndiferentes por cuenta."


def test_proposed_document_has_only_ficha(profile):
    doc = Document(ficha=make_standard(estado="propuesto").ficha)
    text = render_document(doc, profile)
    assert text.startswith("---\n") and text.endswith("---\n")
    parsed = parse_document(text, profile)
    assert parsed.sections == {} and parsed.rules == []
    assert check_structure(parsed, profile) == []


def test_extract_references(profile):
    assert extract_references(make_standard()) == ["LIN-INF-001", "LIN-SEG-002", "LIN-INF-001.R02"]


# BR-U0-16
def test_document_path(profile):
    doc = make_standard()
    assert document_path(profile, doc.ficha) == "documentos/EST/EST-INF-AWS-001.md"
    assert check_structure(doc, profile, "documentos/EST/EST-INF-AWS-001.md") == []
    assert "ubicación incorrecta" in check_structure(doc, profile, "documentos/LIN/EST-INF-AWS-001.md")[0]


# BR-U0-17
@pytest.mark.parametrize(
    "update,fragment",
    [
        ({"id": "EST-INF-001"}, "ID con formato inválido"),
        ({"id": "EST-DAT-AWS-001"}, "no coincide"),
        ({"dominio": "XYZ", "id": "EST-XYZ-AWS-001"}, "dominio desconocido"),
        ({"tecnologia": None, "id": "EST-INF-AWS-001"}, "requiere tecnología"),
        ({"estado": "borrador"}, "estado desconocido"),
        ({"relaciones": [{"tipo": "deriva_de", "destino": "X"}]}, "relación no permitido"),
    ],
)
def test_ficha_checks(profile, update, fragment):
    doc = make_standard(ficha=update)
    assert any(fragment in p for p in check_structure(doc, profile)), check_structure(doc, profile)


def test_lineamiento_does_not_accept_technology(profile):
    doc = Document(
        ficha=Ficha(
            id="LIN-INF-001", titulo="x", tipo="lineamiento", dominio="INF", tecnologia="AWS", padre="INF"
        )
    )
    assert "el tipo no admite tecnología" in check_structure(doc, profile)


def test_invalid_ficha_raises(profile):
    with pytest.raises(DocumentError, match="Ficha inválida"):
        parse_document("---\nid: X\n---\n", profile)
    with pytest.raises(DocumentError, match="empezar con la ficha"):
        parse_document("# hola", profile)
    with pytest.raises(DocumentError, match="cierra la ficha"):
        parse_document("---\nid: X\n", profile)


# BR-U0-18
def test_required_section_missing_from_validation(profile):
    sections = dict(make_standard().sections)
    del sections["especificacion"]
    doc = make_standard(sections=sections)
    assert "falta la sección obligatoria: Especificación técnica" in check_structure(doc, profile)
    draft = make_standard(estado="en_redaccion", sections=sections)
    assert check_structure(draft, profile) == []


def test_sections_out_of_order(profile):
    sections = dict(make_standard().sections)
    reordered = {"alcance": sections.pop("alcance"), **sections}
    assert "las secciones no siguen el orden de la plantilla" in check_structure(
        make_standard(sections=reordered), profile
    )


def test_section_not_allowed_for_type(profile):
    sections = {"proposito": "x", "mapeo_iso27001": "y"}
    doc = make_standard(estado="en_redaccion", sections=sections)
    assert "sección no permitida para este tipo: mapeo_iso27001" in check_structure(doc, profile)
    seg = make_standard(
        estado="en_redaccion", sections=sections, ficha={"dominio": "SEG", "id": "EST-SEG-AWS-001"}
    )
    assert not any("no permitida" in p for p in check_structure(seg, profile))


def test_unknown_or_repeated_section_raises(profile):
    base = (
        "---\n" + render_document(Document(ficha=make_standard().ficha), profile).split("---\n")[1] + "---\n"
    )
    with pytest.raises(DocumentError, match="Sección desconocida"):
        parse_document(base + "\n## Anexos\n", profile)
    with pytest.raises(DocumentError, match="Sección repetida"):
        parse_document(base + "\n## Propósito\n\n## Propósito\n", profile)
    with pytest.raises(DocumentError, match="antes de la primera sección"):
        parse_document(base + "\ntexto suelto\n", profile)


# BR-U0-19
def test_rule_checks(profile):
    bad = [
        Rule("EST-INF-AWS-001.R1", "DEBE", "a", "b", "c", "d"),
        Rule("EST-INF-AWS-001.R02", "TALVEZ", "a", "b", "c", "d"),
        Rule("EST-INF-AWS-001.R02", "DEBE", "a", "", "c", "d"),
        Rule("LIN-INF-001.R03", "DEBE", "a", "b", "c", "d"),
    ]
    problems = check_structure(make_standard(rules=bad), profile)
    assert "ID de regla inválido: EST-INF-AWS-001.R1" in problems
    assert "EST-INF-AWS-001.R02: nivel desconocido TALVEZ" in problems
    assert "ID de regla repetido: EST-INF-AWS-001.R02" in problems
    assert "EST-INF-AWS-001.R02: falta el campo Justificación" in problems
    assert "ID de regla inválido: LIN-INF-001.R03" in problems


def test_malformed_rule_header_raises(profile):
    text = render_document(make_standard(), profile).replace(
        "### EST-INF-AWS-001.R01 · DEBE", "### Regla uno"
    )
    with pytest.raises(DocumentError, match="Encabezado de regla inválido"):
        parse_document(text, profile)


def test_text_outside_rule_fields_raises(profile):
    text = render_document(make_standard(), profile).replace(
        "### EST-INF-AWS-001.R01 · DEBE\n", "### EST-INF-AWS-001.R01 · DEBE\nsuelto\n"
    )
    with pytest.raises(DocumentError, match="fuera de los campos"):
        parse_document(text, profile)


# IDs
def test_ids(profile):
    assert format_document_id(profile, "estandar", "INF", 7, "AWS") == "EST-INF-AWS-007"
    assert format_document_id(profile, "fundacional", "AE", 12) == "FUN-AE-012"
    assert parse_document_id(profile, "EST-INF-AWS-007").tecnologia == "AWS"
    assert parse_document_id(profile, "LIN-SEG-002").tipo == "lineamiento"
    assert parse_document_id(profile, "GUI-INF-001") is None
    assert format_rule_id(profile, "LIN-SEG-002", 3) == "LIN-SEG-002.R03"
    assert parse_rule_id(profile, "LIN-SEG-002.R03") == ("LIN-SEG-002", 3)
    assert parse_rule_id(profile, "XYZ.R03") is None
    assert parse_rule_id(profile, "LIN-SEG-002") is None
