import boto3
import pytest
from moto import mock_aws

from documentador.adapters.state import DynamoStateStore, InMemoryStateStore


def _table():
    resource = boto3.resource("dynamodb", region_name="us-east-1")
    resource.create_table(
        TableName="documentador-estado",
        KeySchema=[{"AttributeName": "PK", "KeyType": "HASH"}, {"AttributeName": "SK", "KeyType": "RANGE"}],
        AttributeDefinitions=[
            {"AttributeName": n, "AttributeType": "S"} for n in ("PK", "SK", "GSI1PK", "GSI1SK")
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "GSI1",
                "KeySchema": [
                    {"AttributeName": "GSI1PK", "KeyType": "HASH"},
                    {"AttributeName": "GSI1SK", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    return DynamoStateStore("documentador-estado", resource=resource)


@pytest.fixture(params=["memoria", "dynamodb"])
def store(request):
    if request.param == "memoria":
        yield InMemoryStateStore()
    else:
        with mock_aws():
            yield _table()


def test_store_contract(store):
    store.put(
        {"PK": "RUN#1", "SK": "META", "GSI1PK": "RUNS#en_curso", "GSI1SK": "2026-10-19", "flujo": "mapa"}
    )
    store.put({"PK": "RUN#1", "SK": "STEP#001", "agente": "investigador"})
    store.put({"PK": "RUN#1", "SK": "STEP#002", "agente": "taxonomista"})
    store.put({"PK": "RUN#2", "SK": "META", "GSI1PK": "RUNS#en_curso", "GSI1SK": "2026-10-20"})
    assert store.get("RUN#1", "META")["flujo"] == "mapa"
    assert store.get("RUN#9", "META") is None
    assert [i["agente"] for i in store.query("RUN#1", "STEP#")] == ["investigador", "taxonomista"]
    assert len(store.query("RUN#1")) == 3
    assert [i["PK"] for i in store.query_index("RUNS#en_curso")] == ["RUN#1", "RUN#2"]
    assert [i["PK"] for i in store.query_index("RUNS#en_curso", "2026-10-20")] == ["RUN#2"]
    store.delete("RUN#1", "STEP#001")
    assert len(store.query("RUN#1", "STEP#")) == 1
