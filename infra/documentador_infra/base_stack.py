"""Stack DocumentadorBase (U0): budget, files bucket, state table, parameters and operator policy."""

from __future__ import annotations

import json

from aws_cdk import CfnOutput, Duration, RemovalPolicy, Stack
from aws_cdk import aws_budgets as budgets
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_ssm as ssm
from constructs import Construct

from documentador_infra import valores

PARAMETER_PREFIX = "/documentador/"
TABLE_NAME = "documentador-estado"
POLICY_NAME = "documentador-operador"
TEMP_PREFIX = "tmp/"
TEMP_DAYS = 7


class BaseStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, *, alert_email: str, github_repo: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self._budget(alert_email)

        self.bucket = s3.Bucket(
            self,
            "Archivos",
            bucket_name=f"documentador-{self.account}-archivos",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            versioned=False,
            lifecycle_rules=[s3.LifecycleRule(prefix=TEMP_PREFIX, expiration=Duration.days(TEMP_DAYS))],
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.table = dynamodb.Table(
            self,
            "Estado",
            table_name=TABLE_NAME,
            partition_key=dynamodb.Attribute(name="PK", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="SK", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            point_in_time_recovery_specification=dynamodb.PointInTimeRecoverySpecification(
                point_in_time_recovery_enabled=False
            ),
            time_to_live_attribute="expira",
            removal_policy=RemovalPolicy.DESTROY,
        )
        self.table.add_global_secondary_index(
            index_name="GSI1",
            partition_key=dynamodb.Attribute(name="GSI1PK", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="GSI1SK", type=dynamodb.AttributeType.STRING),
        )

        self._parameters(github_repo)
        policy = self._operator_policy()

        CfnOutput(self, "Bucket", value=self.bucket.bucket_name)
        CfnOutput(self, "Tabla", value=self.table.table_name)
        CfnOutput(self, "PoliticaOperador", value=policy.managed_policy_arn)
        CfnOutput(
            self,
            "AsociarPolitica",
            value="aws iam attach-user-policy --user-name <tu-usuario> --policy-arn "
            + policy.managed_policy_arn,
        )

    def _budget(self, alert_email: str) -> None:
        subscribers = [budgets.CfnBudget.SubscriberProperty(subscription_type="EMAIL", address=alert_email)]

        def notification(kind: str, percent: int) -> budgets.CfnBudget.NotificationWithSubscribersProperty:
            return budgets.CfnBudget.NotificationWithSubscribersProperty(
                notification=budgets.CfnBudget.NotificationProperty(
                    notification_type=kind,
                    comparison_operator="GREATER_THAN",
                    threshold=percent,
                    threshold_type="PERCENTAGE",
                ),
                subscribers=subscribers,
            )

        budgets.CfnBudget(
            self,
            "Presupuesto",
            budget=budgets.CfnBudget.BudgetDataProperty(
                budget_name="documentador-pruebas",
                budget_type="COST",
                time_unit="MONTHLY",
                budget_limit=budgets.CfnBudget.SpendProperty(amount=valores.PRESUPUESTO_USD, unit="USD"),
            ),
            notifications_with_subscribers=[
                *(notification("ACTUAL", p) for p in valores.AVISOS_REALES),
                *(notification("FORECASTED", p) for p in valores.AVISOS_PRONOSTICO),
            ],
        )

    def _parameters(self, github_repo: str) -> None:
        values: dict[str, str] = {
            "github/repo": github_repo,
            "github/rama": "main",
            "tabla": self.table.table_name,
            "bucket": self.bucket.bucket_name,
        }
        values.update({f"modelos/{agent}": json.dumps(cfg) for agent, cfg in valores.MODELOS.items()})
        values.update({f"precios/{model}": json.dumps(price) for model, price in valores.PRECIOS.items()})
        values.update({f"topes/{flow}": f"{usd:.2f}" for flow, usd in valores.TOPES_USD.items()})
        for name, value in values.items():
            ssm.StringParameter(
                self,
                "Param-" + name.replace("/", "-").replace(".", "-"),
                parameter_name=PARAMETER_PREFIX + name,
                string_value=value,
                tier=ssm.ParameterTier.STANDARD,
            )

    def _operator_policy(self) -> iam.ManagedPolicy:
        parameters_arn = self.format_arn(service="ssm", resource="parameter", resource_name="documentador/*")
        return iam.ManagedPolicy(
            self,
            "Operador",
            managed_policy_name=POLICY_NAME,
            description="Permisos mínimos para usar la CLI doc del documentador.",
            statements=[
                iam.PolicyStatement(
                    sid="EstadoDeTrabajo",
                    actions=[
                        "dynamodb:GetItem",
                        "dynamodb:PutItem",
                        "dynamodb:UpdateItem",
                        "dynamodb:DeleteItem",
                        "dynamodb:Query",
                        "dynamodb:BatchWriteItem",
                        "dynamodb:DescribeTable",
                    ],
                    resources=[self.table.table_arn, f"{self.table.table_arn}/index/*"],
                ),
                iam.PolicyStatement(
                    sid="ArchivosLectura",
                    actions=["s3:ListBucket"],
                    resources=[self.bucket.bucket_arn],
                ),
                iam.PolicyStatement(
                    sid="ArchivosObjetos",
                    actions=["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
                    resources=[self.bucket.arn_for_objects("*")],
                ),
                iam.PolicyStatement(
                    sid="Parametros",
                    actions=["ssm:GetParameter", "ssm:GetParameters", "ssm:GetParametersByPath"],
                    resources=[parameters_arn],
                ),
            ],
        )
