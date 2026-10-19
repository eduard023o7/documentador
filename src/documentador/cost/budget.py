"""Per-run budget guard (pattern P1). Prices are configuration: USD per million tokens."""

from __future__ import annotations

from dataclasses import dataclass, field

from documentador.common.errors import DocumentadorError

MILLION = 1_000_000


@dataclass(frozen=True)
class Price:
    entrada: float
    salida: float
    cache_lectura: float = 0.0
    cache_escritura: float = 0.0

    @classmethod
    def from_dict(cls, data: dict[str, float]) -> Price:
        return cls(
            entrada=float(data["entrada"]),
            salida=float(data["salida"]),
            cache_lectura=float(data.get("cache_lectura", 0.0)),
            cache_escritura=float(data.get("cache_escritura", data["entrada"])),
        )


@dataclass(frozen=True)
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0

    def cost(self, price: Price) -> float:
        return (
            self.input_tokens * price.entrada
            + self.output_tokens * price.salida
            + self.cache_read_tokens * price.cache_lectura
            + self.cache_write_tokens * price.cache_escritura
        ) / MILLION


class BudgetExceeded(DocumentadorError):
    """The run would spend more than its limit. Nothing was called."""


@dataclass
class Budget:
    limit_usd: float
    prices: dict[str, Price]
    spent_usd: float = 0.0
    calls: list[tuple[str, Usage, float]] = field(default_factory=list)

    @property
    def remaining_usd(self) -> float:
        return max(self.limit_usd - self.spent_usd, 0.0)

    def ensure_affordable(self, model: str, input_tokens: int, max_output_tokens: int) -> None:
        """Raise before calling the model if the worst case of this call does not fit."""
        worst = Usage(input_tokens=input_tokens, output_tokens=max_output_tokens).cost(self._price(model))
        if worst > self.remaining_usd:
            raise BudgetExceeded(
                f"La llamada podría costar USD {worst:.4f} y quedan USD {self.remaining_usd:.4f} "
                f"de un tope de USD {self.limit_usd:.2f}.",
                "Sube el tope en /documentador/topes/<flujo> o reduce el alcance de la ejecución.",
            )

    def charge(self, model: str, usage: Usage) -> float:
        cost = usage.cost(self._price(model))
        self.spent_usd += cost
        self.calls.append((model, usage, cost))
        if self.spent_usd > self.limit_usd:
            raise BudgetExceeded(
                f"La ejecución gastó USD {self.spent_usd:.4f} y superó su tope de USD {self.limit_usd:.2f}.",
                "Revisa la ejecución con 'doc ejecuciones' antes de reintentar.",
            )
        return cost

    def _price(self, model: str) -> Price:
        try:
            return self.prices[model]
        except KeyError:
            raise BudgetExceeded(
                f"No hay precio configurado para el modelo {model}.",
                f"Define /documentador/precios/{model}.",
            ) from None
