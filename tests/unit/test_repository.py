"""Content repository contract and Git conventions: BR-U0-21 to BR-U0-26."""

import pytest

from documentador.adapters.repository import (
    InMemoryRepository,
    LineComment,
    commit_message,
    content_path,
    proposal_branch,
    require_reviewer,
)
from documentador.common.errors import RepositoryError


@pytest.fixture
def repo():
    r = InMemoryRepository()
    r.seed({"marco/tipos.yaml": "a", "documentos/LIN/LIN-INF-001.md": "b"})
    return r


def test_read_list_exists(repo):
    assert repo.read("marco/tipos.yaml") == "a"
    assert repo.list_files("documentos/") == ["documentos/LIN/LIN-INF-001.md"]
    assert repo.exists("marco/tipos.yaml") and not repo.exists("marco/otro.yaml")
    with pytest.raises(RepositoryError, match="No existe"):
        repo.read("marco/otro.yaml")


def test_proposal_flow_branch_commit_pr_merge_tag(repo):
    branch = proposal_branch("documento", "EST-INF-AWS-001")
    repo.create_branch(branch)
    sha = repo.commit(
        branch,
        {"documentos/EST/EST-INF-AWS-001.md": "c", "marco/tipos.yaml": None},
        commit_message("Propuesta", "nuevo estándar"),
    )
    assert repo.read("documentos/EST/EST-INF-AWS-001.md", ref=branch) == "c"
    assert not repo.exists("marco/tipos.yaml", ref=branch)
    assert repo.exists("marco/tipos.yaml")  # main untouched until merge
    pr = repo.open_pull_request(branch, "Propuesta", "cuerpo")
    merged = repo.merge(pr, commit_message("Aprobado EST-INF-AWS-001", "revisión", reviewer="Ana"))
    assert repo.read("documentos/EST/EST-INF-AWS-001.md") == "c"
    assert "Revisado-por: Ana" in repo.history()[-1].message
    assert repo.merge(pr, commit_message("Aprobado", "revisión", reviewer="Ana")) == merged  # idempotent
    repo.tag("EST-INF-AWS-001@1.0.0", merged)
    repo.tag("EST-INF-AWS-001@1.0.0", merged)  # same commit: no-op
    assert sha != merged


# BR-U0-21
def test_proposal_branch_names():
    assert proposal_branch("mapa", "INF 2026") == "propuesta/mapa-INF-2026"
    with pytest.raises(RepositoryError):
        proposal_branch("otro", "x")
    with pytest.raises(RepositoryError):
        proposal_branch("mapa", "///")


def test_branch_already_exists(repo):
    repo.create_branch("propuesta/mapa-1")
    with pytest.raises(RepositoryError, match="ya existe"):
        repo.create_branch("propuesta/mapa-1")


# BR-U0-22
def test_commit_message_format():
    assert (
        commit_message("Resumen", "porque sí", reviewer="Ana")
        == "Resumen\n\nMotivo: porque sí\nRevisado-por: Ana"
    )
    assert "Revisado-por" not in commit_message("Resumen", "porque sí")


# BR-U0-23
def test_approval_requires_reviewer(repo):
    repo.create_branch("propuesta/mapa-1")
    pr = repo.open_pull_request("propuesta/mapa-1", "t", "b")
    with pytest.raises(RepositoryError, match="sin nombre de revisor"):
        repo.merge(pr, commit_message("Aprobado", "x"))
    with pytest.raises(RepositoryError, match="Falta el nombre del revisor"):
        commit_message("Aprobado", "x", reviewer="  ")
    assert require_reviewer("A\n\nRevisado-por: Luis Pérez") == "Luis Pérez"


# BR-U0-24
def test_tags_never_move(repo):
    repo.tag("mapa@1.0.0", "a" * 40)
    with pytest.raises(RepositoryError, match="no se mueven"):
        repo.tag("mapa@1.0.0", "b" * 40)
    with pytest.raises(RepositoryError, match="formato inválido"):
        repo.tag("mapa-1", "a" * 40)


# BR-U0-26 and BR-U0-15
@pytest.mark.parametrize("bad", ["", "/etc/passwd", "../src/x.py", "marco/../../x", "a\\b"])
def test_paths_outside_content_rejected(bad):
    with pytest.raises(RepositoryError, match="Ruta no permitida"):
        content_path(bad)


def test_no_direct_commits_to_main(repo):
    with pytest.raises(RepositoryError, match="directo en main"):
        repo.commit("main", {"marco/x.yaml": "y"}, "m")


def test_review_comments(repo):
    repo.create_branch("propuesta/documento-1")
    pr = repo.open_pull_request("propuesta/documento-1", "t", "b")
    repo.comments[pr.number] = [LineComment("documentos/EST/X.md", 10, "RECHAZAR: falta fuente")]
    assert repo.review_comments(pr)[0].body.startswith("RECHAZAR")
