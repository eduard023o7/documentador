"""Document and rule IDs built from the patterns in `codificacion.yaml`."""

from __future__ import annotations

import re
import string
from dataclasses import dataclass

from documentador.core.profile_models import Profile

DOMAIN_REGEX = r"[A-Z0-9]{2,6}"


@dataclass(frozen=True)
class DocumentId:
    tipo: str
    dominio: str
    tecnologia: str | None
    n: int


def format_document_id(
    profile: Profile, tipo: str, dominio: str, n: int, tecnologia: str | None = None
) -> str:
    pattern = profile.codificacion.documento[tipo]
    return pattern.format(dominio=dominio, tecnologia=tecnologia or "", n=n)


def parse_document_id(profile: Profile, doc_id: str) -> DocumentId | None:
    """Return the parts of a document ID, or None if it matches no type pattern."""
    for tipo, pattern in profile.codificacion.documento.items():
        match = _pattern_regex(pattern, _technology_regex(profile)).fullmatch(doc_id)
        if match:
            parts = match.groupdict()
            return DocumentId(tipo, parts["dominio"], parts.get("tecnologia"), int(parts["n"]))
    return None


def format_rule_id(profile: Profile, doc_id: str, n: int) -> str:
    return profile.codificacion.regla.format(documento=doc_id, n=n)


def parse_rule_id(profile: Profile, rule_id: str) -> tuple[str, int] | None:
    """Return (document ID, rule number) for a rule ID, or None if malformed."""
    match = _pattern_regex(profile.codificacion.regla, _technology_regex(profile)).fullmatch(rule_id)
    if not match:
        return None
    doc_id = match.group("documento")
    if parse_document_id(profile, doc_id) is None:
        return None
    return doc_id, int(match.group("n"))


def _technology_regex(profile: Profile) -> str:
    return profile.codificacion.tecnologia.patron.removeprefix("^").removesuffix("$")


def _pattern_regex(pattern: str, technology: str) -> re.Pattern[str]:
    groups = {
        "dominio": DOMAIN_REGEX,
        "tecnologia": technology,
        "documento": r"[A-Z0-9-]+",
    }
    regex = ""
    for literal, field, spec, _ in string.Formatter().parse(pattern):
        regex += re.escape(literal)
        if field is None:
            continue
        if field == "n":
            width = int(spec[:-1]) if spec and spec.endswith("d") and spec[:-1].isdigit() else 1
            regex += rf"(?P<n>\d{{{width},}})"
        else:
            regex += f"(?P<{field}>{groups[field]})"
    return re.compile(regex)
