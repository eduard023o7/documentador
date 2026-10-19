"""GitHub implementation of the content repository, over the REST API without cloning."""

from __future__ import annotations

import base64
from typing import Any

import httpx

from documentador.adapters.repository import (
    CONTENT_ROOT,
    MAIN_BRANCH,
    PLATFORM_AUTHOR,
    Author,
    LineComment,
    PullRequestRef,
    check_tag_name,
    content_path,
    require_reviewer,
)
from documentador.common.errors import RepositoryError
from documentador.common.retry import is_transient, with_retries

API_URL = "https://api.github.com"
API_VERSION = "2022-11-28"
PAGE_SIZE = 100


class GitHubRepository:
    def __init__(
        self,
        repo: str,
        token: str,
        main_branch: str = MAIN_BRANCH,
        client: httpx.Client | None = None,
    ) -> None:
        if repo.count("/") != 1:
            raise RepositoryError(f"Repositorio inválido: {repo!r}.", "Usa el formato dueño/repositorio.")
        self.repo = repo
        self.main = main_branch
        self._http = client or httpx.Client(base_url=API_URL, timeout=30)
        self._http.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": API_VERSION,
            }
        )

    # Reading
    def read(self, path: str, ref: str | None = None) -> str:
        ref = ref or self.main
        data = self._call("GET", f"contents/{self._full(path)}", params={"ref": ref})
        return base64.b64decode(data["content"]).decode("utf-8")

    def exists(self, path: str, ref: str | None = None) -> bool:
        try:
            self.read(path, ref)
        except RepositoryError as exc:
            if getattr(exc, "status", None) == 404:
                return False
            raise
        return True

    def list_files(self, prefix: str = "", ref: str | None = None) -> list[str]:
        data = self._call("GET", f"git/trees/{ref or self.main}", params={"recursive": "1"})
        root = CONTENT_ROOT + "/"
        paths = [
            item["path"].removeprefix(root)
            for item in data.get("tree", [])
            if item["type"] == "blob" and item["path"].startswith(root)
        ]
        return sorted(p for p in paths if p.startswith(prefix))

    # Writing
    def create_branch(self, name: str, base: str | None = None) -> None:
        sha = self._branch_sha(base or self.main)
        try:
            self._call("POST", "git/refs", json={"ref": f"refs/heads/{name}", "sha": sha})
        except RepositoryError as exc:
            if getattr(exc, "status", None) == 422:
                raise RepositoryError(f"La rama {name} ya existe.") from exc
            raise

    def commit(
        self, branch: str, files: dict[str, str | None], message: str, author: Author = PLATFORM_AUTHOR
    ) -> str:
        if branch == self.main:
            raise RepositoryError("No se escribe directo en main: los cambios entran por propuesta.")
        head = self._branch_sha(branch)
        base_tree = self._call("GET", f"git/commits/{head}")["tree"]["sha"]
        tree = []
        for path, content in files.items():
            entry: dict[str, Any] = {"path": self._full(path), "mode": "100644", "type": "blob"}
            if content is None:
                entry["sha"] = None
            else:
                entry["content"] = content
            tree.append(entry)
        new_tree = self._call("POST", "git/trees", json={"base_tree": base_tree, "tree": tree})["sha"]
        new_commit = self._call(
            "POST",
            "git/commits",
            json={
                "message": message,
                "tree": new_tree,
                "parents": [head],
                "author": {"name": author.name, "email": author.email},
            },
        )["sha"]
        self._call("PATCH", f"git/refs/heads/{branch}", json={"sha": new_commit})
        return str(new_commit)

    def open_pull_request(self, branch: str, title: str, body: str) -> PullRequestRef:
        data = self._call(
            "POST", "pulls", json={"title": title, "head": branch, "base": self.main, "body": body}
        )
        return PullRequestRef(number=int(data["number"]), branch=branch, url=str(data["html_url"]))

    def review_comments(self, pr: PullRequestRef) -> list[LineComment]:
        comments: list[LineComment] = []
        page = 1
        while True:
            batch = self._call(
                "GET", f"pulls/{pr.number}/comments", params={"per_page": PAGE_SIZE, "page": page}
            )
            for item in batch:
                comments.append(
                    LineComment(
                        path=str(item["path"]).removeprefix(CONTENT_ROOT + "/"),
                        line=item.get("line"),
                        body=str(item["body"]),
                    )
                )
            if len(batch) < PAGE_SIZE:
                return comments
            page += 1

    def merge(self, pr: PullRequestRef, message: str) -> str:
        require_reviewer(message)
        current = self._call("GET", f"pulls/{pr.number}")
        if current.get("merged"):
            return str(current["merge_commit_sha"])
        title, _, rest = message.partition("\n")
        data = self._call(
            "PUT",
            f"pulls/{pr.number}/merge",
            json={"merge_method": "squash", "commit_title": title, "commit_message": rest.strip()},
        )
        return str(data["sha"])

    def tag(self, name: str, commit: str) -> None:
        check_tag_name(name)
        try:
            existing = self._call("GET", f"git/ref/tags/{name}")
        except RepositoryError as exc:
            if getattr(exc, "status", None) != 404:
                raise
            self._call("POST", "git/refs", json={"ref": f"refs/tags/{name}", "sha": commit})
            return
        if existing["object"]["sha"] != commit:
            raise RepositoryError(f"La etiqueta {name} ya existe en otro commit; las etiquetas no se mueven.")

    # Internals
    def _full(self, path: str) -> str:
        return f"{CONTENT_ROOT}/{content_path(path)}"

    def _branch_sha(self, branch: str) -> str:
        return str(self._call("GET", f"git/ref/heads/{branch}")["object"]["sha"])

    @with_retries()
    def _call(self, method: str, path: str, **kwargs: Any) -> Any:
        response = self._http.request(method, f"/repos/{self.repo}/{path}", **kwargs)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if is_transient(exc):
                raise
            raise _repository_error(exc.response) from exc
        return response.json() if response.content else None


def _repository_error(response: httpx.Response) -> RepositoryError:
    code = response.status_code
    try:
        detail = response.json().get("message", "")
    except ValueError:
        detail = response.text[:200]
    if code in (401, 403):
        error = RepositoryError(
            f"GitHub rechazó el acceso ({code}): {detail}",
            "Revisa que el token en /documentador/github/token tenga permisos de Contents y Pull requests.",
        )
    elif code == 404:
        error = RepositoryError(f"No se encontró en GitHub: {detail or response.request.url.path}")
    elif code in (409, 422):
        error = RepositoryError(f"Conflicto en GitHub ({code}): {detail}")
    else:
        error = RepositoryError(f"Error de GitHub ({code}): {detail}")
    error.status = code  # type: ignore[attr-defined]
    return error
