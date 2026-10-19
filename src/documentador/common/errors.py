"""Errors carrying a user-facing message in Spanish and a suggested action."""

from __future__ import annotations


class DocumentadorError(Exception):
    """Base error. `message` and `action` are shown to the user as-is."""

    def __init__(self, message: str, action: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.action = action

    def __str__(self) -> str:
        if self.action:
            return f"{self.message}\n→ {self.action}"
        return self.message


class ConfigError(DocumentadorError):
    """Missing or invalid configuration."""


class TransientError(DocumentadorError):
    """A failure worth retrying (throttling, 5xx, network)."""


class RepositoryError(DocumentadorError):
    """Content repository operation failed."""
