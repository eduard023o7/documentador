"""Runtime settings from Parameter Store, `config/local.yaml` and environment (patterns P2 and P7).

Precedence, highest first: environment variables, `config/local.yaml`, Parameter Store.
Parameters live under `/documentador/`; values are cached in memory for five minutes.
"""

from __future__ import annotations

import json
import os
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import boto3
from botocore.exceptions import ClientError
from ruamel.yaml import YAML

from documentador.common.errors import ConfigError
from documentador.common.retry import with_retries

PARAMETER_PREFIX = "/documentador/"
GITHUB_TOKEN_ENV = "DOCUMENTADOR_GITHUB_TOKEN"
CACHE_SECONDS = 300

# Environment variables that override a parameter (name relative to the prefix).
_ENV_OVERRIDES = {
    "github/token": GITHUB_TOKEN_ENV,
    "github/repo": "DOCUMENTADOR_GITHUB_REPO",
    "tabla": "DOCUMENTADOR_TABLA",
    "bucket": "DOCUMENTADOR_BUCKET",
}


class Settings:
    def __init__(
        self,
        local_file: Path | None = Path("config/local.yaml"),
        ssm_client: Any | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._local = _read_local(local_file)
        self._ssm = ssm_client
        self._clock = clock
        self._cache: dict[str, tuple[float, str]] = {}

    def get(self, name: str, default: str | None = None) -> str:
        """Return a parameter value by its name relative to `/documentador/`."""
        env_name = _ENV_OVERRIDES.get(name)
        if env_name and os.environ.get(env_name):
            return os.environ[env_name]
        if name in self._local:
            return str(self._local[name])
        cached = self._cache.get(name)
        if cached and self._clock() - cached[0] < CACHE_SECONDS:
            return cached[1]
        value = self._fetch(name)
        if value is None:
            if default is not None:
                return default
            raise ConfigError(
                f"Falta el parámetro {PARAMETER_PREFIX}{name}.",
                "Despliega el stack DocumentadorBase o defínelo en config/local.yaml.",
            )
        self._cache[name] = (self._clock(), value)
        return value

    def get_json(self, name: str) -> Any:
        raw = self.get(name)
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ConfigError(f"El parámetro {PARAMETER_PREFIX}{name} no es JSON válido.") from exc

    @with_retries()
    def _fetch(self, name: str) -> str | None:
        if self._ssm is None:
            self._ssm = boto3.client("ssm")
        try:
            response = self._ssm.get_parameter(Name=PARAMETER_PREFIX + name, WithDecryption=True)
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") == "ParameterNotFound":
                return None
            raise
        return str(response["Parameter"]["Value"])


def _read_local(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    data = YAML(typ="safe").load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ConfigError(f"{path} debe ser un diccionario de parámetros.")
    return {k: json.dumps(v) if isinstance(v, dict | list) else v for k, v in data.items()}
