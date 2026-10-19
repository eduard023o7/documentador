"""Load and validate the framework profile (business rules BR-U0-01 to BR-U0-15)."""

from __future__ import annotations

import re
import string
from collections import Counter, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

from documentador.core import profile_models as m

PENDING_MARK = "POR DEFINIR"
OPTIONAL_MARK = "(opcional)"
ROOT_PARENT = "dominio"
OUT_OF_SCOPE = "fuera_mvp"
TEMPLATES_DIR = "plantillas"
CATALOG_FILE = "plantillas/catalogo-secciones.yaml"
PRINCIPLES_FILE = "principios.md"

# Profile attribute -> file name, in reading order.
PROFILE_FILES: dict[str, tuple[str, type[BaseModel]]] = {
    "tipos": ("tipos.yaml", m.TypesFile),
    "dominios": ("dominios.yaml", m.DomainsFile),
    "codificacion": ("codificacion.yaml", m.CodingFile),
    "niveles": ("niveles.yaml", m.LevelsFile),
    "relaciones": ("relaciones.yaml", m.RelationsFile),
    "ciclo_vida": ("ciclo-vida.yaml", m.LifecycleFile),
    "versionado": ("versionado.yaml", m.VersioningFile),
    "estilo": ("estilo.yaml", m.StyleFile),
    "glosario": ("glosario.yaml", m.GlossaryFile),
    "fuentes": ("fuentes.yaml", m.SourcesFile),
    "validacion": ("validacion.yaml", m.ValidationFile),
    "contexto": ("contexto.yaml", m.ContextFile),
    "catalogo": (CATALOG_FILE, m.SectionCatalog),
}

# Keys that would try to configure a non-configurable invariant (BR-U0-12 to 15).
INVARIANT_KEYS = {
    "padres_multiples": "cada documento tiene exactamente un padre",
    "multiples_padres": "cada documento tiene exactamente un padre",
    "reutilizar_ids": "los IDs son únicos y nunca se reutilizan",
    "ids_repetidos": "los IDs son únicos y nunca se reutilizan",
    "temas_duplicados": "cada tema vive en un solo documento",
    "publicar_sin_aprobacion": "nada se publica sin aprobación humana",
    "aprobacion_humana": "nada se publica sin aprobación humana",
}

REQUIRED_STATES = ("propuesto", "aprobado")
DOCUMENT_ID_FIELDS = {"dominio", "tecnologia", "n"}
RULE_ID_FIELDS = {"documento", "n"}
SPECIFICATION_SECTION = "especificacion"


@dataclass(frozen=True)
class Issue:
    archivo: str
    campo: str
    motivo: str

    def __str__(self) -> str:
        where = f"{self.archivo}: {self.campo}" if self.campo else self.archivo
        return f"{where} — {self.motivo}"


class ProfileError(Exception):
    """The profile is invalid. Carries every issue found, not only the first."""

    def __init__(self, issues: list[Issue]) -> None:
        self.issues = issues
        super().__init__("\n".join(str(i) for i in issues))


@dataclass(frozen=True)
class LoadedProfile:
    profile: m.Profile
    warnings: list[Issue]


def load_profile(path: Path, for_approval: bool = False) -> LoadedProfile:
    """Read `contenido/marco/`, validate it and return the profile plus warnings.

    With `for_approval`, pending values (`POR DEFINIR` without `(opcional)`) are errors.
    """
    errors: list[Issue] = []
    warnings: list[Issue] = []
    raw: dict[str, Any] = {}

    files = {attr: name for attr, (name, _) in PROFILE_FILES.items()}
    for attr, name in files.items():
        raw[attr] = _read_yaml(path / name, name, errors)

    principles_path = path / PRINCIPLES_FILE
    principles = ""
    if principles_path.exists():
        principles = principles_path.read_text(encoding="utf-8")
    else:
        errors.append(Issue(PRINCIPLES_FILE, "", "falta el archivo"))

    templates_raw: dict[str, Any] = {}
    types_raw = raw.get("tipos") or {}
    for doc_type in types_raw.get("tipos", []) if isinstance(types_raw, dict) else []:
        key = doc_type.get("clave") if isinstance(doc_type, dict) else None
        if isinstance(key, str):
            name = f"{TEMPLATES_DIR}/{key}.yaml"
            templates_raw[key] = _read_yaml(path / name, name, errors)

    for attr, data in raw.items():
        _check_invariant_keys(data, files[attr], errors)
    for key, data in templates_raw.items():
        _check_invariant_keys(data, f"{TEMPLATES_DIR}/{key}.yaml", errors)

    parsed: dict[str, Any] = {}
    for attr, (name, model) in PROFILE_FILES.items():
        if raw.get(attr) is not None:
            parsed[attr] = _validate(model, raw[attr], name, errors)
    templates: dict[str, m.Template] = {}
    for key, data in templates_raw.items():
        if data is not None:
            template = _validate(m.Template, data, f"{TEMPLATES_DIR}/{key}.yaml", errors)
            if template is not None:
                templates[key] = template

    _collect_pending(path, for_approval, errors, warnings)

    if errors or any(v is None for v in parsed.values()) or len(parsed) < len(PROFILE_FILES):
        raise ProfileError(errors or [Issue("perfil", "", "no se pudo leer")])

    profile = m.Profile(**parsed, plantillas=templates, principios=principles)
    errors.extend(_cross_checks(profile))
    if errors:
        raise ProfileError(errors)
    return LoadedProfile(profile=profile, warnings=warnings)


def _read_yaml(file: Path, name: str, errors: list[Issue]) -> Any:
    if not file.exists():
        errors.append(Issue(name, "", "falta el archivo"))
        return None
    try:
        data = YAML(typ="safe").load(file.read_text(encoding="utf-8"))
    except YAMLError as exc:
        errors.append(Issue(name, "", f"YAML inválido: {exc}"))
        return None
    if not isinstance(data, dict):
        errors.append(Issue(name, "", "debe contener un diccionario"))
        return None
    return data


def _validate(model: type[Any], data: Any, name: str, errors: list[Issue]) -> Any:
    try:
        return model.model_validate(data)
    except ValidationError as exc:
        for error in exc.errors():
            field = ".".join(str(part) for part in error["loc"])
            reason = _translate(error)
            errors.append(Issue(name, field, reason))
        return None


def _translate(error: Any) -> str:
    kind = error["type"]
    if kind == "missing":
        return "campo obligatorio faltante"
    if kind == "extra_forbidden":
        return "campo no reconocido"
    if kind == "literal_error" and error["loc"] and error["loc"][0] == "version_esquema":
        return f"versión de esquema no soportada (se espera {m.SCHEMA_VERSION})"
    if kind == "literal_error":
        return f"valor no permitido: {error['input']!r}"
    if kind == "string_pattern_mismatch":
        return f"formato inválido: {error['input']!r}"
    return str(error["msg"])


def _check_invariant_keys(data: Any, name: str, errors: list[Issue]) -> None:
    def walk(node: Any, trail: str) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                here = f"{trail}.{key}" if trail else str(key)
                if key in INVARIANT_KEYS:
                    errors.append(Issue(name, here, f"invariante no configurable: {INVARIANT_KEYS[key]}"))
                walk(value, here)
        elif isinstance(node, list):
            for index, item in enumerate(node):
                walk(item, f"{trail}.{index}")

    walk(data, "")


def _collect_pending(path: Path, for_approval: bool, errors: list[Issue], warnings: list[Issue]) -> None:
    for file in sorted(path.rglob("*")):
        if file.suffix not in {".yaml", ".md"} or not file.is_file():
            continue
        name = file.relative_to(path).as_posix()
        for number, line in enumerate(file.read_text(encoding="utf-8").splitlines(), start=1):
            if PENDING_MARK not in line:
                continue
            issue = Issue(name, f"línea {number}", "valor por definir")
            optional = OPTIONAL_MARK in line
            (errors if for_approval and not optional else warnings).append(issue)


def _cross_checks(p: m.Profile) -> list[Issue]:
    issues: list[Issue] = []
    issues += _check_types(p)
    issues += _check_domains(p)
    issues += _check_coding(p)
    issues += _check_lifecycle(p)
    issues += _check_templates(p)
    issues += _check_unique_keys(p)
    return issues


def _duplicates(values: list[str]) -> set[str]:
    return {value for value, count in Counter(values).items() if count > 1}


def _check_types(p: m.Profile) -> list[Issue]:
    issues: list[Issue] = []
    name = "tipos.yaml"
    types = p.tipos.tipos
    keys = {t.clave for t in types}
    for dup in _duplicates([t.codigo for t in types]):
        issues.append(Issue(name, "tipos", f"código de tipo repetido: {dup}"))
    for dup in _duplicates([t.clave for t in types]):
        issues.append(Issue(name, "tipos", f"clave de tipo repetida: {dup}"))
    for t in types:
        if t.padre_permitido != ROOT_PARENT and (
            t.padre_permitido not in keys or t.padre_permitido == t.clave
        ):
            issues.append(
                Issue(name, f"tipos.{t.clave}.padre_permitido", f"padre inválido: {t.padre_permitido}")
            )
    parent_of = {t.clave: t.padre_permitido for t in types}
    for t in types:
        seen, current = set(), t.clave
        while current in parent_of and current not in seen:
            seen.add(current)
            current = parent_of[current]
        if current in seen:
            issues.append(Issue(name, f"tipos.{t.clave}.padre_permitido", "ciclo entre tipos de documento"))
            break
    for index, step in enumerate(p.tipos.test_clasificacion):
        if step.resultado not in keys and step.resultado != OUT_OF_SCOPE:
            issues.append(
                Issue(
                    name, f"test_clasificacion.{index}.resultado", f"resultado desconocido: {step.resultado}"
                )
            )
    return issues


def _check_domains(p: m.Profile) -> list[Issue]:
    issues: list[Issue] = []
    for dup in _duplicates([d.codigo for d in p.dominios.dominios]):
        issues.append(Issue("dominios.yaml", "dominios", f"código de dominio repetido: {dup}"))
    optional = {s.clave for s in p.catalogo.secciones if s.opcional}
    for d in p.dominios.dominios:
        for key in d.secciones_opcionales:
            if key not in optional:
                issues.append(
                    Issue(
                        "dominios.yaml",
                        f"dominios.{d.codigo}.secciones_opcionales",
                        f"la sección '{key}' no es una sección opcional del catálogo",
                    )
                )
    return issues


def _placeholders(pattern: str) -> set[str] | None:
    try:
        return {f for _, f, _, _ in string.Formatter().parse(pattern) if f is not None}
    except ValueError:
        return None


def _check_coding(p: m.Profile) -> list[Issue]:
    issues: list[Issue] = []
    name = "codificacion.yaml"
    keys = {t.clave for t in p.tipos.tipos}
    patterns = p.codificacion.documento
    if set(patterns) != keys:
        issues.append(Issue(name, "documento", "debe definir un patrón por cada tipo de documento"))
    try:
        re.compile(p.codificacion.tecnologia.patron)
    except re.error:
        issues.append(Issue(name, "tecnologia.patron", "expresión regular inválida"))
    samples: dict[str, str] = {}
    for key, pattern in patterns.items():
        fields = _placeholders(pattern)
        if fields is None or not fields <= DOCUMENT_ID_FIELDS or "n" not in fields:
            issues.append(
                Issue(name, f"documento.{key}", "solo admite {dominio}, {tecnologia} y {n}, y debe usar {n}")
            )
            continue
        if key in keys and p.doc_type(key).requiere_tecnologia and "tecnologia" not in fields:
            issues.append(
                Issue(
                    name, f"documento.{key}", "el tipo requiere tecnología: el patrón debe usar {tecnologia}"
                )
            )
        if key in keys and not pattern.startswith(p.doc_type(key).codigo):
            issues.append(
                Issue(
                    name,
                    f"documento.{key}",
                    f"el ID debe empezar con el código del tipo ({p.doc_type(key).codigo})",
                )
            )
        samples[key] = pattern.format(dominio="DOM", tecnologia="TEC", n=1)
    if len(set(samples.values())) != len(samples):
        issues.append(Issue(name, "documento", "dos tipos generan el mismo ID"))
    rule_fields = _placeholders(p.codificacion.regla)
    if rule_fields is None or rule_fields != RULE_ID_FIELDS:
        issues.append(Issue(name, "regla", "debe usar exactamente {documento} y {n}"))
    return issues


def _check_lifecycle(p: m.Profile) -> list[Issue]:
    issues: list[Issue] = []
    name = "ciclo-vida.yaml"
    states = set(p.ciclo_vida.estados)
    for required in REQUIRED_STATES:
        if required not in states:
            issues.append(Issue(name, "estados", f"falta el estado obligatorio '{required}'"))
    for origin, targets in p.ciclo_vida.transiciones.items():
        for state in [origin, *targets]:
            if state not in states:
                issues.append(Issue(name, f"transiciones.{origin}", f"estado no declarado: {state}"))
    if all(s in states for s in REQUIRED_STATES):
        reached, queue = {"propuesto"}, deque(["propuesto"])
        while queue:
            for nxt in p.ciclo_vida.transiciones.get(queue.popleft(), []):
                if nxt not in reached:
                    reached.add(nxt)
                    queue.append(nxt)
        if "aprobado" not in reached:
            issues.append(Issue(name, "transiciones", "'aprobado' no es alcanzable desde 'propuesto'"))
    return issues


def _check_templates(p: m.Profile) -> list[Issue]:
    issues: list[Issue] = []
    catalog = {s.clave for s in p.catalogo.secciones}
    for dup in _duplicates([s.clave for s in p.catalogo.secciones]):
        issues.append(Issue(CATALOG_FILE, "secciones", f"sección repetida: {dup}"))
    for doc_type in p.tipos.tipos:
        name = f"{TEMPLATES_DIR}/{doc_type.clave}.yaml"
        template = p.plantillas.get(doc_type.clave)
        if template is None:
            continue
        if template.tipo != doc_type.clave:
            issues.append(Issue(name, "tipo", f"debe ser '{doc_type.clave}'"))
        keys = [s.clave for s in template.secciones]
        for dup in _duplicates(keys):
            issues.append(Issue(name, "secciones", f"sección repetida: {dup}"))
        for key in keys:
            if key not in catalog:
                issues.append(Issue(name, "secciones", f"la sección '{key}' no está en el catálogo"))
        if doc_type.requiere_tecnologia and not any(
            s.clave == SPECIFICATION_SECTION and s.obligatoria for s in template.secciones
        ):
            issues.append(
                Issue(name, "secciones", "el tipo requiere tecnología: 'especificacion' debe ser obligatoria")
            )
        if not any(p.section(k).contiene_reglas for k in keys if k in catalog):
            issues.append(Issue(name, "secciones", "la plantilla debe incluir una sección de reglas"))
    return issues


def _check_unique_keys(p: m.Profile) -> list[Issue]:
    issues: list[Issue] = []
    checks = [
        ("niveles.yaml", "niveles", [n.clave for n in p.niveles.niveles]),
        ("relaciones.yaml", "relaciones", [r.clave for r in p.relaciones.relaciones]),
        ("validacion.yaml", "criterios", [c.clave for c in p.validacion.criterios]),
        ("ciclo-vida.yaml", "estados", list(p.ciclo_vida.estados)),
    ]
    for name, field, values in checks:
        for dup in _duplicates(values):
            issues.append(Issue(name, field, f"valor repetido: {dup}"))
    allowed = {"principio", *(t.clave for t in p.tipos.tipos)}
    for item in p.relaciones.precedencia:
        if item not in allowed:
            issues.append(Issue("relaciones.yaml", "precedencia", f"elemento desconocido: {item}"))
    return issues
