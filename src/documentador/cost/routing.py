"""Which model each agent uses, and the budget of each flow (pattern P2)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from documentador.common.errors import ConfigError
from documentador.config import Settings
from documentador.cost.budget import Budget, Price

Effort = Literal["low", "medium", "high", "xhigh", "max"]
EFFORTS: tuple[str, ...] = ("low", "medium", "high", "xhigh", "max")
AGENTS = (
    "taxonomista",
    "redactor",
    "validador",
    "impacto",
    "investigador",
    "contraste",
    "admision",
    "evaluador",
)
FLOWS = ("mapa", "documento", "necesidad", "evaluacion")


@dataclass(frozen=True)
class ModelConfig:
    model_id: str
    effort: str
    max_tokens: int


def model_for(agent: str, settings: Settings) -> ModelConfig:
    if agent not in AGENTS:
        raise ConfigError(f"Agente desconocido: {agent}.")
    data = settings.get_json(f"modelos/{agent}")
    try:
        config = ModelConfig(str(data["modelo"]), str(data["esfuerzo"]), int(data.get("max_tokens", 16000)))
    except (KeyError, TypeError, ValueError) as exc:
        raise ConfigError(
            f"/documentador/modelos/{agent} debe tener 'modelo', 'esfuerzo' y opcionalmente 'max_tokens'."
        ) from exc
    if config.effort not in EFFORTS:
        raise ConfigError(
            f"Esfuerzo no válido para {agent}: {config.effort}.", f"Usa uno de: {', '.join(EFFORTS)}."
        )
    return config


def budget_for(flow: str, settings: Settings) -> Budget:
    """A fresh budget for one run of `flow`, with prices for every configured agent model."""
    if flow not in FLOWS:
        raise ConfigError(f"Flujo desconocido: {flow}.")
    try:
        limit = float(settings.get(f"topes/{flow}"))
    except ValueError as exc:
        raise ConfigError(f"/documentador/topes/{flow} debe ser un número en USD.") from exc
    models = {model_for(agent, settings).model_id for agent in AGENTS}
    prices = {model: Price.from_dict(settings.get_json(f"precios/{model}")) for model in models}
    return Budget(limit_usd=limit, prices=prices)
