import logging

import boto3
import httpx
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws

from documentador.common.errors import ConfigError, DocumentadorError, TransientError
from documentador.common.logging import JsonFormatter, SecretMaskingFilter, mask_secrets
from documentador.common.retry import is_transient, with_retries
from documentador.config import Settings


def _client_error(code: str, status: int = 400) -> ClientError:
    return ClientError({"Error": {"Code": code}, "ResponseMetadata": {"HTTPStatusCode": status}}, "op")


def _http_error(status: int) -> httpx.HTTPStatusError:
    request = httpx.Request("GET", "https://api.github.com")
    return httpx.HTTPStatusError("x", request=request, response=httpx.Response(status, request=request))


class TestRetry:
    @pytest.mark.parametrize(
        "exc,expected",
        [
            (TransientError("x"), True),
            (_http_error(429), True),
            (_http_error(502), True),
            (_http_error(404), False),
            (_http_error(403), False),
            (_client_error("ThrottlingException"), True),
            (_client_error("ValidationException"), False),
            (_client_error("AccessDeniedException", 403), False),
            (_client_error("Unknown", 503), True),
            (ValueError("x"), False),
        ],
    )
    def test_is_transient(self, exc, expected):
        assert is_transient(exc) is expected

    def test_retries_transient_then_succeeds(self):
        calls, waits = [], []

        @with_retries(max_attempts=3, sleep=waits.append)
        def flaky():
            calls.append(1)
            if len(calls) < 3:
                raise TransientError("temporal")
            return "ok"

        assert flaky() == "ok"
        assert len(calls) == 3 and len(waits) == 2
        assert waits[1] > waits[0]

    def test_gives_up_after_max_attempts(self):
        @with_retries(max_attempts=2, sleep=lambda _: None)
        def always_fails():
            raise TransientError("temporal")

        with pytest.raises(TransientError):
            always_fails()

    def test_never_retries_permanent_errors(self):
        calls = []

        @with_retries(sleep=lambda _: None)
        def forbidden():
            calls.append(1)
            raise _http_error(403)

        with pytest.raises(httpx.HTTPStatusError):
            forbidden()
        assert len(calls) == 1


class TestLogging:
    def test_masks_github_tokens(self):
        assert mask_secrets("token ghp_abc123XYZ y github_pat_11AA_bb") == "token ghp_*** y github_pat_***"

    def test_filter_masks_message_and_args(self):
        record = logging.LogRecord("documentador", logging.INFO, "", 0, "uso %s", ("ghp_secreto",), None)
        SecretMaskingFilter().filter(record)
        assert "secreto" not in record.getMessage()

    def test_json_formatter_includes_context(self):
        record = logging.LogRecord("documentador", logging.INFO, "", 0, "paso listo", (), None)
        record.run_id = "R1"
        record.costo = 0.01
        out = JsonFormatter().format(record)
        assert '"run_id": "R1"' in out and '"mensaje": "paso listo"' in out


class TestErrors:
    def test_message_with_action(self):
        assert str(DocumentadorError("Falta algo.", "Hazlo así.")) == "Falta algo.\n→ Hazlo así."


@mock_aws
class TestSettings:
    def _ssm(self):
        client = boto3.client("ssm", region_name="us-east-1")
        client.put_parameter(Name="/documentador/github/repo", Value="org/repo", Type="String")
        client.put_parameter(Name="/documentador/github/token", Value="ghp_x", Type="SecureString")
        client.put_parameter(Name="/documentador/topes/mapa", Value='{"usd": 1.0}', Type="String")
        return client

    def test_reads_parameter_store(self, tmp_path):
        settings = Settings(local_file=None, ssm_client=self._ssm())
        assert settings.get("github/repo") == "org/repo"
        assert settings.get("github/token") == "ghp_x"
        assert settings.get_json("topes/mapa") == {"usd": 1.0}

    def test_local_file_overrides_parameter_store(self, tmp_path):
        local = tmp_path / "local.yaml"
        local.write_text("github/repo: otra/repo\nmodelos/redactor: {modelo: m, esfuerzo: low}\n")
        settings = Settings(local_file=local, ssm_client=self._ssm())
        assert settings.get("github/repo") == "otra/repo"
        assert settings.get_json("modelos/redactor") == {"modelo": "m", "esfuerzo": "low"}

    def test_env_overrides_everything(self, monkeypatch):
        monkeypatch.setenv("DOCUMENTADOR_GITHUB_TOKEN", "ghp_env")
        settings = Settings(local_file=None, ssm_client=self._ssm())
        assert settings.get("github/token") == "ghp_env"

    def test_env_overrides_branch(self, monkeypatch):
        monkeypatch.setenv("DOCUMENTADOR_GITHUB_RAMA", "claude/rama")
        assert Settings(local_file=None, ssm_client=self._ssm()).get("github/rama", "main") == "claude/rama"

    def test_missing_parameter(self):
        settings = Settings(local_file=None, ssm_client=self._ssm())
        assert settings.get("no/existe", default="d") == "d"
        with pytest.raises(ConfigError, match="/documentador/no/existe"):
            settings.get("no/existe")

    def test_caches_values(self):
        ssm = self._ssm()
        now = [0.0]
        settings = Settings(local_file=None, ssm_client=ssm, clock=lambda: now[0])
        settings.get("github/repo")
        ssm.put_parameter(Name="/documentador/github/repo", Value="nuevo/repo", Type="String", Overwrite=True)
        assert settings.get("github/repo") == "org/repo"
        now[0] = 301
        assert settings.get("github/repo") == "nuevo/repo"
