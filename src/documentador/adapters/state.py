"""Work-state store: one DynamoDB table with PK/SK and the GSI1 index (data-model.md §2).

U0 provides the generic item operations; U1 adds the run, observation and approval helpers on top.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any, Protocol

import boto3
from boto3.dynamodb.conditions import Key

from documentador.common.retry import with_retries

INDEX_NAME = "GSI1"

Item = dict[str, Any]


class StateStore(Protocol):
    def put(self, item: Item) -> None: ...
    def get(self, pk: str, sk: str) -> Item | None: ...
    def query(self, pk: str, sk_prefix: str = "") -> list[Item]: ...
    def query_index(self, gsi1pk: str, sk_prefix: str = "") -> list[Item]: ...
    def delete(self, pk: str, sk: str) -> None: ...


@dataclass
class InMemoryStateStore:
    items: dict[tuple[str, str], Item] = field(default_factory=dict)

    def put(self, item: Item) -> None:
        self.items[(item["PK"], item["SK"])] = dict(item)

    def get(self, pk: str, sk: str) -> Item | None:
        item = self.items.get((pk, sk))
        return dict(item) if item else None

    def query(self, pk: str, sk_prefix: str = "") -> list[Item]:
        return [dict(v) for (p, s), v in sorted(self.items.items()) if p == pk and s.startswith(sk_prefix)]

    def query_index(self, gsi1pk: str, sk_prefix: str = "") -> list[Item]:
        found = [
            dict(v)
            for v in self.items.values()
            if v.get("GSI1PK") == gsi1pk and str(v.get("GSI1SK", "")).startswith(sk_prefix)
        ]
        return sorted(found, key=lambda v: str(v.get("GSI1SK", "")))

    def delete(self, pk: str, sk: str) -> None:
        self.items.pop((pk, sk), None)


class DynamoStateStore:
    def __init__(self, table_name: str, resource: Any | None = None) -> None:
        self._table = (resource or boto3.resource("dynamodb")).Table(table_name)

    @with_retries()
    def put(self, item: Item) -> None:
        self._table.put_item(Item=item)

    @with_retries()
    def get(self, pk: str, sk: str) -> Item | None:
        item = self._table.get_item(Key={"PK": pk, "SK": sk}).get("Item")
        return dict(item) if item else None

    def query(self, pk: str, sk_prefix: str = "") -> list[Item]:
        condition = Key("PK").eq(pk)
        if sk_prefix:
            condition = condition & Key("SK").begins_with(sk_prefix)
        return list(self._paginate(KeyConditionExpression=condition))

    def query_index(self, gsi1pk: str, sk_prefix: str = "") -> list[Item]:
        condition = Key("GSI1PK").eq(gsi1pk)
        if sk_prefix:
            condition = condition & Key("GSI1SK").begins_with(sk_prefix)
        return list(self._paginate(IndexName=INDEX_NAME, KeyConditionExpression=condition))

    @with_retries()
    def delete(self, pk: str, sk: str) -> None:
        self._table.delete_item(Key={"PK": pk, "SK": sk})

    def _paginate(self, **kwargs: Any) -> Iterator[Item]:
        while True:
            response = self._query_page(**kwargs)
            yield from response.get("Items", [])
            if "LastEvaluatedKey" not in response:
                return
            kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]

    @with_retries()
    def _query_page(self, **kwargs: Any) -> dict[str, Any]:
        return dict(self._table.query(**kwargs))
