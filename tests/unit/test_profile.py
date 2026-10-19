"""Profile validation: one case per business rule BR-U0-01 to BR-U0-15."""

import pytest

from documentador.core.profile import ProfileError, load_profile

from ..conftest import MARCO


def errors_of(profile_dir, for_approval=False) -> list[str]:
    with pytest.raises(ProfileError) as info:
        load_profile(profile_dir.path, for_approval=for_approval)
    return [str(i) for i in info.value.issues]


def assert_error(profile_dir, fragment: str) -> None:
    messages = errors_of(profile_dir)
    assert any(fragment in m for m in messages), messages


def test_real_profile_loads_with_pending_warnings():
    result = load_profile(MARCO)
    assert result.profile.doc_type("estandar").codigo == "EST"
    assert {"INF", "DAT", "SEG", "IA", "AE", "OT"} == result.profile.domain_codes()
    assert result.warnings and all("por definir" in str(w) for w in result.warnings)


def test_profile_helpers():
    p = load_profile(MARCO).profile
    assert p.doc_type_by_code("LIN").clave == "lineamiento"
    assert p.level_keys() == ["DEBE", "DEBERÍA", "PUEDE"]
    assert p.section("reglas").contiene_reglas
    assert p.severity("cita_inexistente") == "bloqueante"
    with pytest.raises(KeyError):
        p.doc_type("guia")


# BR-U0-01
def test_missing_file(profile_dir):
    (profile_dir.path / "niveles.yaml").unlink()
    assert_error(profile_dir, "niveles.yaml — falta el archivo")


def test_unsupported_schema_version(profile_dir):
    profile_dir.edit("estilo.yaml", lambda d: d.update(version_esquema=2))
    assert_error(profile_dir, "versión de esquema no soportada")


def test_reports_all_errors_together(profile_dir):
    (profile_dir.path / "niveles.yaml").unlink()
    (profile_dir.path / "glosario.yaml").unlink()
    messages = errors_of(profile_dir)
    assert len([m for m in messages if "falta el archivo" in m]) == 2


# BR-U0-02
def test_missing_required_field(profile_dir):
    profile_dir.edit("estilo.yaml", lambda d: d.pop("tono"))
    assert_error(profile_dir, "estilo.yaml: tono — campo obligatorio faltante")


def test_unknown_field(profile_dir):
    profile_dir.edit("estilo.yaml", lambda d: d.update(colores="azul"))
    assert_error(profile_dir, "campo no reconocido")


def test_invalid_value(profile_dir):
    profile_dir.edit("validacion.yaml", lambda d: d["criterios"][0].update(severidad="grave"))
    assert_error(profile_dir, "valor no permitido")


def test_invalid_yaml(profile_dir):
    (profile_dir.path / "estilo.yaml").write_text("tono: [sin cerrar\n")
    assert_error(profile_dir, "YAML inválido")


# BR-U0-03
def test_duplicate_domain_code(profile_dir):
    profile_dir.edit("dominios.yaml", lambda d: d["dominios"][1].update(codigo="INF"))
    assert_error(profile_dir, "código de dominio repetido: INF")


def test_bad_code_format(profile_dir):
    profile_dir.edit("dominios.yaml", lambda d: d["dominios"][0].update(codigo="infra"))
    assert_error(profile_dir, "formato inválido")


def test_duplicate_type_code(profile_dir):
    profile_dir.edit("tipos.yaml", lambda d: d["tipos"][1].update(codigo="FUN"))
    assert_error(profile_dir, "código de tipo repetido: FUN")


# BR-U0-04
def test_invalid_parent_type(profile_dir):
    profile_dir.edit("tipos.yaml", lambda d: d["tipos"][2].update(padre_permitido="guia"))
    assert_error(profile_dir, "padre inválido: guia")


def test_cycle_between_types(profile_dir):
    profile_dir.edit("tipos.yaml", lambda d: d["tipos"][1].update(padre_permitido="estandar"))
    assert_error(profile_dir, "ciclo entre tipos")


# BR-U0-05
def test_unknown_classification_result(profile_dir):
    profile_dir.edit("tipos.yaml", lambda d: d["test_clasificacion"][0].update(resultado="guia"))
    assert_error(profile_dir, "resultado desconocido: guia")


# BR-U0-06
def test_pattern_with_unknown_variable(profile_dir):
    profile_dir.edit("codificacion.yaml", lambda d: d["documento"].update(lineamiento="LIN-{area}-{n:03d}"))
    assert_error(profile_dir, "solo admite {dominio}, {tecnologia} y {n}")


def test_pattern_must_use_technology_when_required(profile_dir):
    profile_dir.edit("codificacion.yaml", lambda d: d["documento"].update(estandar="EST-{dominio}-{n:03d}"))
    assert_error(profile_dir, "debe usar {tecnologia}")


def test_patterns_must_produce_distinct_ids(profile_dir):
    def change(d):
        d["documento"]["lineamiento"] = "FUN-{dominio}-{n:03d}"

    profile_dir.edit("codificacion.yaml", change)
    messages = errors_of(profile_dir)
    assert any("mismo ID" in m or "código del tipo" in m for m in messages)


def test_pattern_for_every_type(profile_dir):
    profile_dir.edit("codificacion.yaml", lambda d: d["documento"].pop("fundacional"))
    assert_error(profile_dir, "un patrón por cada tipo")


def test_rule_pattern(profile_dir):
    profile_dir.edit("codificacion.yaml", lambda d: d.update(regla="R{n:02d}"))
    assert_error(profile_dir, "{documento} y {n}")


# BR-U0-07
def test_transition_to_undeclared_state(profile_dir):
    profile_dir.edit("ciclo-vida.yaml", lambda d: d["transiciones"].update(propuesto=["archivado"]))
    assert_error(profile_dir, "estado no declarado: archivado")


def test_approved_must_be_reachable(profile_dir):
    profile_dir.edit("ciclo-vida.yaml", lambda d: d["transiciones"].update(en_revision=["en_redaccion"]))
    assert_error(profile_dir, "'aprobado' no es alcanzable")


# BR-U0-08
def test_template_section_must_exist(profile_dir):
    profile_dir.edit(
        "plantillas/lineamiento.yaml",
        lambda d: d["secciones"].append({"clave": "anexos", "obligatoria": False}),
    )
    assert_error(profile_dir, "la sección 'anexos' no está en el catálogo")


def test_domain_optional_section_from_catalog(profile_dir):
    profile_dir.edit("dominios.yaml", lambda d: d["dominios"][0].update(secciones_opcionales=["proposito"]))
    assert_error(profile_dir, "no es una sección opcional del catálogo")


def test_missing_template(profile_dir):
    (profile_dir.path / "plantillas" / "estandar.yaml").unlink()
    assert_error(profile_dir, "plantillas/estandar.yaml — falta el archivo")


# BR-U0-09
def test_standard_requires_specification(profile_dir):
    profile_dir.edit(
        "plantillas/estandar.yaml",
        lambda d: d.update(secciones=[s for s in d["secciones"] if s["clave"] != "especificacion"]),
    )
    assert_error(profile_dir, "'especificacion' debe ser obligatoria")


# BR-U0-10 (covered by test_invalid_value) and BR-U0-11
def test_pending_values_block_approval(profile_dir):
    messages = errors_of(profile_dir, for_approval=True)
    assert any("contexto.yaml" in m for m in messages)
    assert not any("glosario.yaml" in m for m in messages)  # marked (opcional)


def test_profile_without_pending_values_can_be_approved(profile_dir):
    for name in ("contexto.yaml", "dominios.yaml", "glosario.yaml"):
        path = profile_dir.path / name
        path.write_text(path.read_text().replace("POR DEFINIR", "definido"))
    (profile_dir.path / "principios.md").write_text("# Principios\n")
    assert load_profile(profile_dir.path, for_approval=True).warnings == []


# BR-U0-12 to BR-U0-15: invariants are not configurable
@pytest.mark.parametrize(
    "name,key,reason",
    [
        ("tipos.yaml", "padres_multiples", "un padre"),
        ("codificacion.yaml", "reutilizar_ids", "nunca se reutilizan"),
        ("relaciones.yaml", "temas_duplicados", "un solo documento"),
        ("ciclo-vida.yaml", "publicar_sin_aprobacion", "aprobación humana"),
    ],
)
def test_invariants_cannot_be_configured(profile_dir, name, key, reason):
    profile_dir.edit(name, lambda d: d.update({key: True}))
    assert_error(profile_dir, "invariante no configurable: ")
    assert any(reason in m for m in errors_of(profile_dir))


def test_missing_principles(profile_dir):
    (profile_dir.path / "principios.md").unlink()
    assert_error(profile_dir, "principios.md — falta el archivo")


def test_unknown_precedence_item(profile_dir):
    profile_dir.edit("relaciones.yaml", lambda d: d["precedencia"].append("guia"))
    assert_error(profile_dir, "elemento desconocido: guia")


def test_duplicate_level(profile_dir):
    profile_dir.edit("niveles.yaml", lambda d: d["niveles"].append(d["niveles"][0]))
    assert_error(profile_dir, "valor repetido: DEBE")
