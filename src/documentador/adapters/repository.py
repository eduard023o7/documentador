"""Content repository interface and an in-memory implementation (business rules BR-U0-21 to 26).

Paths are always relative to the content root (`contenido/`); nothing outside it can be written.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import Protocol

from documentador.common.errors import RepositoryError

CONTENT_ROOT = "contenido"
MAIN_BRANCH = "main"
PROPOSAL_FLOWS = ("mapa", "documento", "necesidad", "perfil")
REVIEWER_LINE = re.compile(r"^Revisado-por: (?P<name>\S.*)$", re.MULTILINE)
TAG_PATTERN = re.compile(r"^[A-Za-z0-9.-]+@\d+\.\d+\.\d+$")


@dataclass(frozen=True)
class Author:
    name: str
    email: str


PLATFORM_AUTHOR = Author("Admin documentador", "admin-documentador@users.noreply.github.com")


@dataclass(frozen=True)
class PullRequestRef:
    number: int
    branch: str
    url: str = ""


@dataclass(frozen=True)
class LineComment:
    path: str
    line: int | None
    body: str


class ContentRepository(Protocol):
    def read(self, path: str, ref: str = MAIN_BRANCH) -> str: ...
    def exists(self, path: str, ref: str = MAIN_BRANCH) -> bool: ...
    def list_files(self, prefix: str = "", ref: str = MAIN_BRANCH) -> list[str]: ...
    def create_branch(self, name: str, base: str = MAIN_BRANCH) -> None: ...
    def commit(
        self, branch: str, files: dict[str, str | None], message: str, author: Author = PLATFORM_AUTHOR
    ) -> str: ...
    def open_pull_request(self, branch: str, title: str, body: str) -> PullRequestRef: ...
    def review_comments(self, pr: PullRequestRef) -> list[LineComment]: ...
    def merge(self, pr: PullRequestRef, message: str) -> str: ...
    def tag(self, name: str, commit: str) -> None: ...


def content_path(path: str) -> str:
    """Validate a path relative to the content root and return it normalized (BR-U0-26)."""
    pure = PurePosixPath(path)
    if not path or pure.is_absolute() or ".." in pure.parts or "\\" in path:
        raise RepositoryError(f"Ruta no permitida: {path!r}.", "Solo se escribe dentro de contenido/.")
    return pure.as_posix()


def proposal_branch(flow: str, ident: str) -> str:
    """Branch name for a proposal: `propuesta/<flujo>-<id>` (BR-U0-21)."""
    if flow not in PROPOSAL_FLOWS:
        raise RepositoryError(f"Flujo de propuesta desconocido: {flow}.")
    slug = re.sub(r"[^A-Za-z0-9.-]+", "-", ident).strip("-")
    if not slug:
        raise RepositoryError("El identificador de la propuesta está vacío.")
    return f"propuesta/{flow}-{slug}"


def commit_message(summary: str, reason: str, reviewer: str | None = None) -> str:
    """Spanish commit message with summary, reason and, for approvals, the reviewer (BR-U0-22)."""
    lines = [summary.strip(), "", f"Motivo: {reason.strip()}"]
    if reviewer is not None:
        if not reviewer.strip():
            raise RepositoryError("Falta el nombre del revisor.", 'Usa --revisor "Nombre".')
        lines.append(f"Revisado-por: {reviewer.strip()}")
    return "\n".join(lines)


def require_reviewer(message: str) -> str:
    """A merge into main must name its reviewer (BR-U0-15, BR-U0-23)."""
    match = REVIEWER_LINE.search(message)
    if not match:
        raise RepositoryError(
            "Una aprobación sin nombre de revisor no se procesa.", 'Usa --revisor "Nombre".'
        )
    return match["name"].strip()


def check_tag_name(name: str) -> None:
    if not TAG_PATTERN.match(name):
        raise RepositoryError(
            f"Etiqueta con formato inválido: {name}.", "Usa <ID>@x.y.z, mapa@x.y.z o marco@x.y.z."
        )


@dataclass
class _Commit:
    sha: str
    files: dict[str, str]
    message: str
    author: Author


@dataclass
class InMemoryRepository:
    """Same contract as the GitHub implementation, for tests and local dry runs."""

    branches: dict[str, list[_Commit]] = field(default_factory=dict)
    pulls: dict[int, tuple[PullRequestRef, bool, str | None]] = field(default_factory=dict)
    tags: dict[str, str] = field(default_factory=dict)
    comments: dict[int, list[LineComment]] = field(default_factory=dict)
    _counter: int = 0

    def __post_init__(self) -> None:
        if MAIN_BRANCH not in self.branches:
            self.branches[MAIN_BRANCH] = [_Commit(self._sha(), {}, "inicio", PLATFORM_AUTHOR)]

    def seed(self, files: dict[str, str]) -> None:
        """Put files on main without a review (test setup only)."""
        head = self._head(MAIN_BRANCH)
        self.branches[MAIN_BRANCH].append(
            _Commit(self._sha(), {**head.files, **files}, "semilla", PLATFORM_AUTHOR)
        )

    def read(self, path: str, ref: str = MAIN_BRANCH) -> str:
        files = self._head(ref).files
        key = content_path(path)
        if key not in files:
            raise RepositoryError(f"No existe {CONTENT_ROOT}/{key} en {ref}.")
        return files[key]

    def exists(self, path: str, ref: str = MAIN_BRANCH) -> bool:
        return content_path(path) in self._head(ref).files

    def list_files(self, prefix: str = "", ref: str = MAIN_BRANCH) -> list[str]:
        return sorted(p for p in self._head(ref).files if p.startswith(prefix))

    def create_branch(self, name: str, base: str = MAIN_BRANCH) -> None:
        if name in self.branches:
            raise RepositoryError(f"La rama {name} ya existe.")
        self.branches[name] = [self._head(base)]

    def commit(
        self, branch: str, files: dict[str, str | None], message: str, author: Author = PLATFORM_AUTHOR
    ) -> str:
        if branch == MAIN_BRANCH:
            raise RepositoryError("No se escribe directo en main: los cambios entran por propuesta.")
        current = dict(self._head(branch).files)
        for path, content in files.items():
            key = content_path(path)
            if content is None:
                current.pop(key, None)
            else:
                current[key] = content
        commit = _Commit(self._sha(), current, message, author)
        self.branches[branch].append(commit)
        return commit.sha

    def open_pull_request(self, branch: str, title: str, body: str) -> PullRequestRef:
        self._head(branch)
        number = len(self.pulls) + 1
        ref = PullRequestRef(number=number, branch=branch, url=f"memoria://pull/{number}")
        self.pulls[number] = (ref, False, None)
        return ref

    def review_comments(self, pr: PullRequestRef) -> list[LineComment]:
        return list(self.comments.get(pr.number, []))

    def merge(self, pr: PullRequestRef, message: str) -> str:
        require_reviewer(message)
        ref, merged, sha = self.pulls[pr.number]
        if merged and sha:
            return sha
        head = self._head(ref.branch)
        commit = _Commit(self._sha(), dict(head.files), message, PLATFORM_AUTHOR)
        self.branches[MAIN_BRANCH].append(commit)
        self.pulls[pr.number] = (ref, True, commit.sha)
        return commit.sha

    def tag(self, name: str, commit: str) -> None:
        check_tag_name(name)
        existing = self.tags.get(name)
        if existing is not None and existing != commit:
            raise RepositoryError(f"La etiqueta {name} ya existe en otro commit; las etiquetas no se mueven.")
        self.tags[name] = commit

    def history(self, branch: str = MAIN_BRANCH) -> list[_Commit]:
        return list(self.branches[branch])

    def _head(self, ref: str) -> _Commit:
        if ref not in self.branches:
            raise RepositoryError(f"No existe la rama {ref}.")
        return self.branches[ref][-1]

    def _sha(self) -> str:
        self._counter += 1
        return f"{self._counter:040x}"
