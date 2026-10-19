"""Retries with exponential backoff for transient failures only (pattern P4)."""

from __future__ import annotations

import functools
import random
import time
from collections.abc import Callable
from typing import ParamSpec, TypeVar

import httpx
from botocore.exceptions import ClientError, ConnectionError, EndpointConnectionError

from documentador.common.errors import TransientError

P = ParamSpec("P")
T = TypeVar("T")

_TRANSIENT_AWS_CODES = {
    "ThrottlingException",
    "Throttling",
    "TooManyRequestsException",
    "ProvisionedThroughputExceededException",
    "RequestLimitExceeded",
    "ServiceUnavailable",
    "ServiceUnavailableException",
    "InternalServerError",
    "InternalFailure",
    "ModelNotReadyException",
}


def is_transient(exc: BaseException) -> bool:
    """True for throttling, 5xx and network errors; never for 4xx validation or permissions."""
    if isinstance(exc, TransientError):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        code = exc.response.status_code
        return code == 429 or code >= 500
    if isinstance(exc, httpx.TransportError):
        return True
    if isinstance(exc, ClientError):
        error = exc.response.get("Error", {})
        status = exc.response.get("ResponseMetadata", {}).get("HTTPStatusCode", 0)
        return error.get("Code") in _TRANSIENT_AWS_CODES or status >= 500
    return isinstance(exc, ConnectionError | EndpointConnectionError)


def with_retries(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    sleep: Callable[[float], None] = time.sleep,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Retry the wrapped call on transient errors, waiting base_delay * 2**n plus jitter."""

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    if attempt == max_attempts or not is_transient(exc):
                        raise
                    sleep(base_delay * 2 ** (attempt - 1) + random.uniform(0, base_delay / 2))
            raise AssertionError("unreachable")

        return wrapper

    return decorator
