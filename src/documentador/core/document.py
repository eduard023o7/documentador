"""Documents as Markdown with a YAML front matter (the ficha) and sections from the template.

Business rules BR-U0-16 to BR-U0-20. Rendering is canonical: parsing and rendering a
canonical document gives back exactly the same text.
"""

from __future__ import annotations

import io
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import PurePosixPath
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

from documentador.core.ids import parse_document_id, parse_rule_id
from documentador.core.profile_models import SEMVER_PATTERN, Profile

FRONT_MATTER = "---"
DOCUMENTS_DIR = "documentos"
RULE_HEADER = re.compile(r"^### (?P<id>\S+) · (?P<nivel>\S+)$")
REFERENCE = re.compile(r"\[\[(?P<ref>[A-Z0-9-]+(?:\.R\d+)?)\]\]")
RULE_FIELDS = {
    "enunciado": "Enunciado",
    "justificacion": "Justificación",
    "verificacion": "Cómo se verifica",
    "fuentes": "Fuentes",
}
_FIELD_LINE = re.compile(r"^\*\*(?P<label>[^*]+):\*\*\s?(?P<text>.*)$")
# State from which the body must follow the template (BR-U0-18).
STRICT_FROM_STATE = "en_validacion"


class DocumentError(Exception):
    """The document cannot be parsed."""


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Relation(_Model):
    tipo: str
    destino: str


class Scope(_Model):
    incluye: list[str] = []
    excluye: list[str] = []


class SourceRef(_Model):
    titulo: str
    ubicacion: str


class DraftedWith(_Model):
    perfil: str
    plantilla: str


class Ficha(_Model):
    id: str
    titulo: str
    tipo: str
    dominio: str
    tecnologia: str | None = None
    padre: str
    relaciones: list[Relation] = []
    alcance: Scope = Scope()
    justificacion: str = ""
    fuentes: list[SourceRef] = []
    prioridad: Literal["alta", "media", "baja"] = "media"
    estado: str = "propuesto"
    version: str = Field(default="0.0.0", pattern=SEMVER_PATTERN)
    redactado_con: DraftedWith | None = None
    dependencias_abiertas: bool = False
    proxima_revision: date | None = None


@dataclass(frozen=True)
class Rule:
    id: str
    nivel: str
    enunciado: str
    justificacion: str
    verificacion: str
    fuentes: str


@dataclass(frozen=True)
class Document:
    ficha: Ficha
    # Section key -> free text, in document order. For the rules section, the text before the first rule.
    sections: dict[str, str] = field(default_factory=dict)
    rules: list[Rule] = field(default_factory=list)


def parse_document(text: str, profile: Profile) -> Document:
    front, body = _split_front_matter(text)
    try:
        ficha = Ficha.model_validate(front)
    except ValidationError as exc:
        problems = "; ".join(f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in exc.errors())
        raise DocumentError(f"Ficha inválida: {problems}") from exc
    sections, rules = _parse_body(body, profile)
    return Document(ficha=ficha, sections=sections, rules=rules)


def render_document(doc: Document, profile: Profile) -> str:
    data = doc.ficha.model_dump(mode="json")
    for optional in ("tecnologia", "redactado_con"):
        if data[optional] is None:
            del data[optional]
    out = io.StringIO()
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.allow_unicode = True
    yaml.width = 4096
    yaml.dump(data, out)
    parts = [f"{FRONT_MATTER}\n{out.getvalue()}{FRONT_MATTER}\n"]
    for key, content in doc.sections.items():
        section = profile.section(key)
        chunk = f"## {section.titulo}\n"
        if content:
            chunk += f"\n{content}\n"
        if section.contiene_reglas:
            for rule in doc.rules:
                chunk += "\n" + _render_rule(rule)
        parts.append(chunk)
    return "\n".join(parts)


def extract_references(doc: Document) -> list[str]:
    """IDs of documents or rules referenced as [[ID]] anywhere in the body, without repeats."""
    texts = list(doc.sections.values())
    for rule in doc.rules:
        texts += [rule.enunciado, rule.justificacion, rule.verificacion, rule.fuentes]
    found: list[str] = []
    for text in texts:
        for match in REFERENCE.finditer(text):
            if match["ref"] not in found:
                found.append(match["ref"])
    return found


def document_path(profile: Profile, ficha: Ficha) -> str:
    """Repository path of a document, relative to `contenido/` (BR-U0-16)."""
    return f"{DOCUMENTS_DIR}/{profile.doc_type(ficha.tipo).codigo}/{ficha.id}.md"


def check_structure(doc: Document, profile: Profile, path: str | None = None) -> list[str]:
    """Problems with file location, ficha, sections and rule format (BR-U0-16 to BR-U0-19)."""
    problems: list[str] = []
    ficha = doc.ficha
    keys = {t.clave for t in profile.tipos.tipos}
    if ficha.tipo not in keys:
        return [f"tipo desconocido: {ficha.tipo}"]
    doc_type = profile.doc_type(ficha.tipo)

    if path is not None and PurePosixPath(path).as_posix() != document_path(profile, ficha):
        problems.append(f"ubicación incorrecta: debe ser {document_path(profile, ficha)}")
    parsed = parse_document_id(profile, ficha.id)
    if parsed is None or parsed.tipo != ficha.tipo:
        problems.append(f"ID con formato inválido para el tipo {ficha.tipo}: {ficha.id}")
    elif parsed.dominio != ficha.dominio or (parsed.tecnologia or None) != ficha.tecnologia:
        problems.append("el ID no coincide con el dominio o la tecnología de la ficha")
    if ficha.dominio not in profile.domain_codes():
        problems.append(f"dominio desconocido: {ficha.dominio}")
    if doc_type.requiere_tecnologia and not ficha.tecnologia:
        problems.append("el tipo requiere tecnología")
    if not doc_type.requiere_tecnologia and ficha.tecnologia:
        problems.append("el tipo no admite tecnología")
    if ficha.estado not in profile.ciclo_vida.estados:
        problems.append(f"estado desconocido: {ficha.estado}")
    relation_types = {r.clave for r in profile.relaciones.relaciones if not r.implicita}
    for relation in ficha.relaciones:
        if relation.tipo not in relation_types:
            problems.append(f"tipo de relación no permitido: {relation.tipo}")

    problems += _check_sections(doc, profile)
    problems += _check_rules(doc, profile)
    return problems


def _check_sections(doc: Document, profile: Profile) -> list[str]:
    states = profile.ciclo_vida.estados
    strict = (
        doc.ficha.estado in states
        and STRICT_FROM_STATE in states
        and states.index(doc.ficha.estado) >= states.index(STRICT_FROM_STATE)
        and doc.ficha.estado != "obsoleto"
    )
    if not doc.sections and not strict:
        return []
    template = profile.plantillas[doc.ficha.tipo]
    order = [s.clave for s in template.secciones]
    allowed = set(order) | set(_domain_optional_sections(doc, profile))
    problems = [f"sección no permitida para este tipo: {k}" for k in doc.sections if k not in allowed]
    present = [k for k in doc.sections if k in order]
    if present != [k for k in order if k in present]:
        problems.append("las secciones no siguen el orden de la plantilla")
    if strict:
        for section in template.secciones:
            if section.obligatoria and section.clave not in doc.sections:
                problems.append(f"falta la sección obligatoria: {profile.section(section.clave).titulo}")
    return problems


def _domain_optional_sections(doc: Document, profile: Profile) -> list[str]:
    for domain in profile.dominios.dominios:
        if domain.codigo == doc.ficha.dominio:
            return domain.secciones_opcionales
    return []


def _check_rules(doc: Document, profile: Profile) -> list[str]:
    problems: list[str] = []
    levels = profile.level_keys()
    seen: set[str] = set()
    for rule in doc.rules:
        parsed = parse_rule_id(profile, rule.id)
        if parsed is None or parsed[0] != doc.ficha.id:
            problems.append(f"ID de regla inválido: {rule.id}")
        if rule.id in seen:
            problems.append(f"ID de regla repetido: {rule.id}")
        seen.add(rule.id)
        if rule.nivel not in levels:
            problems.append(f"{rule.id}: nivel desconocido {rule.nivel}")
        for key, label in RULE_FIELDS.items():
            if not getattr(rule, key).strip():
                problems.append(f"{rule.id}: falta el campo {label}")
    return problems


def _split_front_matter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith(FRONT_MATTER + "\n"):
        raise DocumentError("El documento debe empezar con la ficha entre líneas '---'.")
    end = text.find(f"\n{FRONT_MATTER}\n", len(FRONT_MATTER))
    if end == -1:
        raise DocumentError("Falta la línea '---' que cierra la ficha.")
    try:
        front = YAML(typ="safe").load(text[len(FRONT_MATTER) + 1 : end + 1])
    except YAMLError as exc:
        raise DocumentError(f"La ficha no es YAML válido: {exc}") from exc
    if not isinstance(front, dict):
        raise DocumentError("La ficha debe ser un diccionario.")
    return front, text[end + len(FRONT_MATTER) + 2 :]


def _parse_body(body: str, profile: Profile) -> tuple[dict[str, str], list[Rule]]:
    titles = {s.titulo: s.clave for s in profile.catalogo.secciones}
    sections: dict[str, str] = {}
    rules: list[Rule] = []
    current: str | None = None
    lines: list[str] = []

    def close() -> None:
        if current is None:
            if "\n".join(lines).strip():
                raise DocumentError("Hay texto antes de la primera sección.")
            return
        if profile.section(current).contiene_reglas:
            intro, parsed = _parse_rules(lines)
            sections[current] = intro
            rules.extend(parsed)
        else:
            sections[current] = "\n".join(lines).strip()

    for line in body.split("\n"):
        if line.startswith("## "):
            close()
            title = line[3:].strip()
            if title not in titles:
                raise DocumentError(f"Sección desconocida: {title}")
            current = titles[title]
            if current in sections:
                raise DocumentError(f"Sección repetida: {title}")
            lines = []
        else:
            lines.append(line)
    close()
    return sections, rules


def _parse_rules(lines: list[str]) -> tuple[str, list[Rule]]:
    intro: list[str] = []
    blocks: list[tuple[re.Match[str], list[str]]] = []
    for line in lines:
        header = RULE_HEADER.match(line)
        if header:
            blocks.append((header, []))
        elif line.startswith("### "):
            raise DocumentError(f"Encabezado de regla inválido: {line}")
        elif blocks:
            blocks[-1][1].append(line)
        else:
            intro.append(line)
    return "\n".join(intro).strip(), [_parse_rule(h, b) for h, b in blocks]


def _parse_rule(header: re.Match[str], lines: list[str]) -> Rule:
    by_label = {label: key for key, label in RULE_FIELDS.items()}
    values: dict[str, list[str]] = {key: [] for key in RULE_FIELDS}
    current: str | None = None
    for line in lines:
        match = _FIELD_LINE.match(line)
        if match and match["label"] in by_label:
            current = by_label[match["label"]]
            values[current].append(match["text"])
        elif current is not None:
            values[current].append(line)
        elif line.strip():
            raise DocumentError(f"{header['id']}: texto fuera de los campos de la regla")
    return Rule(
        id=header["id"],
        nivel=header["nivel"],
        **{key: "\n".join(text).strip() for key, text in values.items()},
    )


def _render_rule(rule: Rule) -> str:
    lines = [f"### {rule.id} · {rule.nivel}"]
    for key, label in RULE_FIELDS.items():
        lines += ["", f"**{label}:** {getattr(rule, key)}".rstrip()]
    return "\n".join(lines) + "\n"
