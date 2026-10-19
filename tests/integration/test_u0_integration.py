"""U0 integration checks against the real AWS account and GitHub.

Run only after deploying DocumentadorBase and creating the token:
    uv run pytest -m integration tests/integration
Side effects: writes and deletes one item in the table and one object under tmp/ in the bucket.
Nothing is written to GitHub.
"""

import uuid

import boto3
import pytest

from documentador.adapters.github import GitHubRepository
from documentador.adapters.state import DynamoStateStore
from documentador.config import Settings
from documentador.cost.routing import AGENTS, FLOWS, budget_for, model_for

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def settings():
    return Settings()


def test_parameters_complete(settings):
    for agent in AGENTS:
        model_for(agent, settings)
    for flow in FLOWS:
        assert budget_for(flow, settings).limit_usd > 0


def test_token_is_secure_string():
    parameter = boto3.client("ssm").get_parameter(Name="/documentador/github/token")["Parameter"]
    assert parameter["Type"] == "SecureString"


def test_state_table_round_trip(settings):
    store = DynamoStateStore(settings.get("tabla"))
    key = f"PRUEBA#{uuid.uuid4()}"
    store.put({"PK": key, "SK": "META", "GSI1PK": "PRUEBAS", "GSI1SK": key})
    try:
        assert store.get(key, "META")["GSI1PK"] == "PRUEBAS"
        assert any(i["PK"] == key for i in store.query_index("PRUEBAS", key))
    finally:
        store.delete(key, "META")


def test_bucket_round_trip(settings):
    s3 = boto3.client("s3")
    bucket = settings.get("bucket")
    key = f"tmp/prueba-{uuid.uuid4()}.txt"
    s3.put_object(Bucket=bucket, Key=key, Body=b"ok")
    try:
        assert s3.get_object(Bucket=bucket, Key=key)["Body"].read() == b"ok"
    finally:
        s3.delete_object(Bucket=bucket, Key=key)


def test_bucket_is_private(settings):
    config = boto3.client("s3").get_public_access_block(Bucket=settings.get("bucket"))
    assert all(config["PublicAccessBlockConfiguration"].values())


def test_github_reads_profile(settings):
    repo = GitHubRepository(
        settings.get("github/repo"), settings.get("github/token"), settings.get("github/rama", "main")
    )
    files = repo.list_files("marco/")
    assert "marco/tipos.yaml" in files
    assert "version_esquema: 1" in repo.read("marco/tipos.yaml", repo.main)


def test_budget_exists():
    account = boto3.client("sts").get_caller_identity()["Account"]
    budget = boto3.client("budgets").describe_budget(AccountId=account, BudgetName="documentador-pruebas")[
        "Budget"
    ]
    assert float(budget["BudgetLimit"]["Amount"]) == 10
