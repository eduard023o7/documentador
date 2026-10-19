"""Structured logging with secret masking (patterns P7 and P8)."""

from __future__ import annotations

import json
import logging
import re
import sys
from typing import Any

_TOKEN_PATTERN = re.compile(r"(ghp_|gho_|ghs_|ghu_|github_pat_)[A-Za-z0-9_]+")
_CONTEXT_FIELDS = ("run_id", "paso", "agente", "modelo", "tokens", "costo", "duracion_ms")


def mask_secrets(text: str) -> str:
    return _TOKEN_PATTERN.sub(r"\1***", text)


class SecretMaskingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = mask_secrets(str(record.msg))
        if record.args:
            record.args = tuple(mask_secrets(a) if isinstance(a, str) else a for a in record.args)
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        data: dict[str, Any] = {
            "nivel": record.levelname,
            "logger": record.name,
            "mensaje": record.getMessage(),
        }
        for field in _CONTEXT_FIELDS:
            if hasattr(record, field):
                data[field] = getattr(record, field)
        if record.exc_info:
            data["error"] = mask_secrets(self.formatException(record.exc_info))
        return json.dumps(data, ensure_ascii=False)


def configure_logging(json_output: bool = False, level: int = logging.INFO) -> None:
    """Console-readable logs locally, JSON in AWS. Always masks GitHub tokens."""
    handler = logging.StreamHandler(sys.stderr)
    handler.addFilter(SecretMaskingFilter())
    handler.setFormatter(
        JsonFormatter() if json_output else logging.Formatter("%(levelname)s %(name)s: %(message)s")
    )
    root = logging.getLogger("documentador")
    root.handlers = [handler]
    root.setLevel(level)
    root.propagate = False
