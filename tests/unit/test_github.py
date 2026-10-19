"""GitHub adapter against a simulated REST API."""

import base64
import json

import httpx
import pytest
import respx

from documentador.adapters.github import GitHubRepository
from documentador.adapters.repository import PullRequestRef, commit_message
from documentador.common.errors import RepositoryError

API = "https://api.github.com/repos/org/repo"


@pytest.fixture
def gh():
    with respx.mock(base_url=API, assert_all_called=False) as mock:
        yield GitHubRepository("org/repo", "ghp_secreto"), mock


def test_read_decodes_content_and_sends_token(gh):
    repo, mock = gh
    route = mock.get("/contents/contenido/marco/tipos.yaml").respond(
        json={"content": base64.b64encode(b"tipos: []").decode()}
    )
    assert repo.read("marco/tipos.yaml") == "tipos: []"
    request = route.calls.last.request
    assert request.headers["Authorization"] == "Bearer ghp_secreto"
    assert request.url.params["ref"] == "main"


def test_exists_false_on_404(gh):
    repo, mock = gh
    mock.get("/contents/contenido/x.md").respond(404, json={"message": "Not Found"})
    assert repo.exists("x.md") is False


def test_list_only_content_blobs(gh):
    repo, mock = gh
    mock.get("/git/trees/main").respond(
        json={
            "tree": [
                {"path": "contenido/marco/tipos.yaml", "type": "blob"},
                {"path": "contenido/marco", "type": "tree"},
                {"path": "src/documentador/cli/main.py", "type": "blob"},
            ]
        }
    )
    assert repo.list_files() == ["marco/tipos.yaml"]


def test_commit_builds_tree_and_moves_branch(gh):
    repo, mock = gh
    mock.get("/git/ref/heads/propuesta/mapa-1").respond(json={"object": {"sha": "head"}})
    mock.get("/git/commits/head").respond(json={"tree": {"sha": "tree0"}})
    trees = mock.post("/git/trees").respond(json={"sha": "tree1"})
    commits = mock.post("/git/commits").respond(json={"sha": "c1"})
    move = mock.patch("/git/refs/heads/propuesta/mapa-1").respond(json={})
    sha = repo.commit("propuesta/mapa-1", {"documentos/LIN/LIN-INF-001.md": "x", "viejo.md": None}, "msg")
    assert sha == "c1"
    tree = json.loads(trees.calls.last.request.content)["tree"]
    assert tree[0] == {
        "path": "contenido/documentos/LIN/LIN-INF-001.md",
        "mode": "100644",
        "type": "blob",
        "content": "x",
    }
    assert tree[1]["sha"] is None
    body = json.loads(commits.calls.last.request.content)
    assert body["parents"] == ["head"] and body["author"]["name"] == "Admin documentador"
    assert json.loads(move.calls.last.request.content) == {"sha": "c1"}


def test_commit_rejects_paths_outside_content(gh):
    repo, mock = gh
    mock.get("/git/ref/heads/propuesta/mapa-1").respond(json={"object": {"sha": "head"}})
    mock.get("/git/commits/head").respond(json={"tree": {"sha": "tree0"}})
    with pytest.raises(RepositoryError, match="Ruta no permitida"):
        repo.commit("propuesta/mapa-1", {"../src/x.py": "x"}, "msg")


def test_create_branch_and_conflict(gh):
    repo, mock = gh
    mock.get("/git/ref/heads/main").respond(json={"object": {"sha": "m"}})
    refs = mock.post("/git/refs")
    refs.side_effect = [
        httpx.Response(201, json={}),
        httpx.Response(422, json={"message": "Reference already exists"}),
    ]
    repo.create_branch("propuesta/mapa-1")
    assert json.loads(refs.calls.last.request.content) == {"ref": "refs/heads/propuesta/mapa-1", "sha": "m"}
    with pytest.raises(RepositoryError, match="ya existe"):
        repo.create_branch("propuesta/mapa-1")


def test_open_pull_request(gh):
    repo, mock = gh
    mock.post("/pulls").respond(json={"number": 7, "html_url": "https://github.com/org/repo/pull/7"})
    pr = repo.open_pull_request("propuesta/mapa-1", "Mapa INF", "cuerpo")
    assert pr == PullRequestRef(7, "propuesta/mapa-1", "https://github.com/org/repo/pull/7")


def test_review_comments_paginates(gh):
    repo, mock = gh
    first = [{"path": "contenido/documentos/EST/X.md", "line": i, "body": "ok"} for i in range(100)]
    route = mock.get("/pulls/7/comments")
    route.side_effect = [
        httpx.Response(200, json=first),
        httpx.Response(200, json=[{"path": "contenido/a.md", "line": None, "body": "RECHAZAR: x"}]),
    ]
    comments = repo.review_comments(PullRequestRef(7, "b"))
    assert len(comments) == 101 and comments[0].path == "documentos/EST/X.md" and comments[-1].line is None


def test_merge_squash_with_reviewer(gh):
    repo, mock = gh
    mock.get("/pulls/7").respond(json={"merged": False})
    merge = mock.put("/pulls/7/merge").respond(json={"sha": "m1"})
    message = commit_message("Aprobado LIN-INF-001", "revisión", reviewer="Ana")
    assert repo.merge(PullRequestRef(7, "b"), message) == "m1"
    body = json.loads(merge.calls.last.request.content)
    assert body["merge_method"] == "squash" and "Revisado-por: Ana" in body["commit_message"]


def test_merge_is_idempotent_and_requires_reviewer(gh):
    repo, mock = gh
    mock.get("/pulls/7").respond(json={"merged": True, "merge_commit_sha": "m1"})
    assert repo.merge(PullRequestRef(7, "b"), commit_message("A", "b", reviewer="Ana")) == "m1"
    with pytest.raises(RepositoryError, match="sin nombre de revisor"):
        repo.merge(PullRequestRef(7, "b"), "sin revisor")


def test_tag_create_same_and_moved(gh):
    repo, mock = gh
    get = mock.get("/git/ref/tags/mapa@1.0.0")
    get.side_effect = [
        httpx.Response(404, json={"message": "Not Found"}),
        httpx.Response(200, json={"object": {"sha": "c1"}}),
        httpx.Response(200, json={"object": {"sha": "c1"}}),
    ]
    create = mock.post("/git/refs").respond(201, json={})
    repo.tag("mapa@1.0.0", "c1")
    assert json.loads(create.calls.last.request.content) == {"ref": "refs/tags/mapa@1.0.0", "sha": "c1"}
    repo.tag("mapa@1.0.0", "c1")
    with pytest.raises(RepositoryError, match="no se mueven"):
        repo.tag("mapa@1.0.0", "c2")


def test_permission_error_message(gh):
    repo, mock = gh
    mock.get("/contents/contenido/a.md").respond(403, json={"message": "Resource not accessible"})
    with pytest.raises(RepositoryError, match="rechazó el acceso") as info:
        repo.read("a.md")
    assert "Contents y Pull requests" in str(info.value)


def test_retries_server_errors(gh, monkeypatch):
    monkeypatch.setattr("documentador.common.retry.time.sleep", lambda _: None)
    repo, mock = gh
    route = mock.get("/contents/contenido/a.md")
    route.side_effect = [
        httpx.Response(502),
        httpx.Response(200, json={"content": base64.b64encode(b"ok").decode()}),
    ]
    assert repo.read("a.md") == "ok"


def test_invalid_repo_name():
    with pytest.raises(RepositoryError, match="dueño/repositorio"):
        GitHubRepository("repo", "t")
