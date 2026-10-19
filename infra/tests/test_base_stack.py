"""Template checks for DocumentadorBase: no fixed costs, no wildcards, private bucket, budget alerts."""

import json

import aws_cdk as cdk
import pytest
from aws_cdk.assertions import Match, Template
from documentador_infra import valores
from documentador_infra.base_stack import BaseStack

FIXED_COST_TYPES = {
    "AWS::EC2::NatGateway",
    "AWS::EC2::Instance",
    "AWS::RDS::DBInstance",
    "AWS::OpenSearchServerless::Collection",
    "AWS::OpenSearchService::Domain",
    "AWS::KMS::Key",
    "AWS::SecretsManager::Secret",
    "AWS::ElastiCache::CacheCluster",
}


@pytest.fixture(scope="module")
def template() -> Template:
    app = cdk.App()
    stack = BaseStack(
        app,
        "Prueba",
        alert_email="avisos@example.com",
        github_repo="org/repo",
        env=cdk.Environment(account="123456789012", region="us-east-1"),
    )
    return Template.from_stack(stack)


def test_no_fixed_cost_resources(template):
    types = {r["Type"] for r in template.to_json()["Resources"].values()}
    assert not types & FIXED_COST_TYPES


def test_no_wildcard_permissions(template):
    for resource in template.to_json()["Resources"].values():
        if resource["Type"] not in ("AWS::IAM::Policy", "AWS::IAM::ManagedPolicy", "AWS::IAM::Role"):
            continue
        for statement in resource["Properties"].get("PolicyDocument", {}).get("Statement", []):
            actions = statement["Action"] if isinstance(statement["Action"], list) else [statement["Action"]]
            resources = (
                statement["Resource"] if isinstance(statement["Resource"], list) else [statement["Resource"]]
            )
            assert "*" not in actions and not any(a.endswith(":*") for a in actions)
            assert "*" not in resources


def test_bucket_private_and_https_only(template):
    template.has_resource_properties(
        "AWS::S3::Bucket",
        {
            "PublicAccessBlockConfiguration": {
                "BlockPublicAcls": True,
                "BlockPublicPolicy": True,
                "IgnorePublicAcls": True,
                "RestrictPublicBuckets": True,
            },
            "BucketEncryption": Match.any_value(),
        },
    )
    template.has_resource_properties(
        "AWS::S3::BucketPolicy",
        {
            "PolicyDocument": {
                "Statement": Match.array_with(
                    [
                        Match.object_like(
                            {
                                "Effect": "Deny",
                                "Condition": {"Bool": {"aws:SecureTransport": "false"}},
                            }
                        )
                    ]
                )
            },
        },
    )
    assert "Versioning" not in json.dumps(template.find_resources("AWS::S3::Bucket"))


def test_budget_with_three_alerts(template):
    budgets = template.find_resources("AWS::Budgets::Budget")
    assert len(budgets) == 1
    props = next(iter(budgets.values()))["Properties"]
    assert props["Budget"]["BudgetLimit"] == {"Amount": 10, "Unit": "USD"}
    alerts = {
        (n["Notification"]["NotificationType"], n["Notification"]["Threshold"])
        for n in props["NotificationsWithSubscribers"]
    }
    assert alerts == {("ACTUAL", 50), ("ACTUAL", 80), ("ACTUAL", 100), ("FORECASTED", 100)}
    assert props["NotificationsWithSubscribers"][0]["Subscribers"][0]["Address"] == "avisos@example.com"


def test_state_table_on_demand_with_index(template):
    template.has_resource_properties(
        "AWS::DynamoDB::Table",
        {
            "TableName": "documentador-estado",
            "BillingMode": "PAY_PER_REQUEST",
            "GlobalSecondaryIndexes": [Match.object_like({"IndexName": "GSI1"})],
            "TimeToLiveSpecification": {"AttributeName": "expira", "Enabled": True},
        },
    )


def test_parameters(template):
    names = {p["Properties"]["Name"] for p in template.find_resources("AWS::SSM::Parameter").values()}
    for agent in valores.MODELOS:
        assert f"/documentador/modelos/{agent}" in names
    for flow in valores.TOPES_USD:
        assert f"/documentador/topes/{flow}" in names
    assert {"/documentador/github/repo", "/documentador/tabla", "/documentador/bucket"} <= names
    assert "/documentador/github/token" not in names  # SecureString is created by hand


def test_operator_policy_scope(template):
    template.has_resource_properties(
        "AWS::IAM::ManagedPolicy", {"ManagedPolicyName": "documentador-operador"}
    )
