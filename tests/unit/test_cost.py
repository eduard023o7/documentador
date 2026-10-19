import pytest

from documentador.common.errors import ConfigError
from documentador.config import Settings
from documentador.cost.budget import Budget, BudgetExceeded, Price, Usage
from documentador.cost.routing import budget_for, model_for

SONNET = "anthropic.claude-sonnet-5-5"
HAIKU = "anthropic.claude-haiku-5-5"
PRICES = {
    SONNET: Price(entrada=2.0, salida=10.0, cache_lectura=0.2, cache_escritura=2.5),
    HAIKU: Price(entrada=0.1, salida=0.5),
}


def test_usage_cost_includes_cache():
    usage = Usage(
        input_tokens=1_000_000, output_tokens=100_000, cache_read_tokens=500_000, cache_write_tokens=0
    )
    assert usage.cost(PRICES[SONNET]) == pytest.approx(2.0 + 1.0 + 0.1)


def test_price_defaults_cache_write_to_input():
    assert Price.from_dict({"entrada": 2, "salida": 10}).cache_escritura == 2


def test_charge_accumulates():
    budget = Budget(limit_usd=1.0, prices=PRICES)
    budget.charge(SONNET, Usage(input_tokens=10_000, output_tokens=2_000))
    budget.charge(HAIKU, Usage(input_tokens=10_000, output_tokens=2_000))
    assert budget.spent_usd == pytest.approx(0.04 + 0.002)
    assert len(budget.calls) == 2 and budget.remaining_usd == pytest.approx(0.958)


def test_charge_over_limit_raises():
    budget = Budget(limit_usd=0.01, prices=PRICES)
    with pytest.raises(BudgetExceeded, match="superó su tope"):
        budget.charge(SONNET, Usage(output_tokens=2_000))


def test_ensure_affordable_checks_worst_case_before_calling():
    budget = Budget(limit_usd=0.10, prices=PRICES)
    budget.ensure_affordable(SONNET, input_tokens=10_000, max_output_tokens=5_000)  # 0.07
    with pytest.raises(BudgetExceeded, match="podría costar"):
        budget.ensure_affordable(SONNET, input_tokens=10_000, max_output_tokens=16_000)  # 0.18


def test_unknown_model_price():
    with pytest.raises(BudgetExceeded, match="No hay precio"):
        Budget(limit_usd=1, prices={}).charge("otro", Usage())


def _settings(tmp_path, replace=None):
    local = tmp_path / "local.yaml"
    lines = [
        f"modelos/{a}: {{modelo: {SONNET}, esfuerzo: medium}}"
        for a in ("taxonomista", "redactor", "validador", "impacto")
    ]
    lines += [
        f"modelos/{a}: {{modelo: {HAIKU}, esfuerzo: low, max_tokens: 4000}}"
        for a in ("investigador", "contraste", "admision", "evaluador")
    ]
    lines += [
        f"precios/{SONNET}: {{entrada: 2, salida: 10}}",
        f"precios/{HAIKU}: {{entrada: 0.1, salida: 0.5}}",
        "topes/mapa: 1.0",
    ]
    if replace:
        lines = [replace if line.startswith(replace.split(":")[0] + ":") else line for line in lines]
    local.write_text("\n".join(lines) + "\n")
    return Settings(local_file=local, ssm_client=object())


def test_model_for(tmp_path):
    settings = _settings(tmp_path)
    assert model_for("redactor", settings).model_id == SONNET
    haiku = model_for("investigador", settings)
    assert (haiku.effort, haiku.max_tokens) == ("low", 4000)
    with pytest.raises(ConfigError, match="Agente desconocido"):
        model_for("poeta", settings)


def test_model_for_invalid_effort(tmp_path):
    settings = _settings(tmp_path, "modelos/redactor: {modelo: x, esfuerzo: extremo}")
    with pytest.raises(ConfigError, match="Esfuerzo no válido"):
        model_for("redactor", settings)


def test_budget_for(tmp_path):
    budget = budget_for("mapa", _settings(tmp_path))
    assert budget.limit_usd == 1.0 and set(budget.prices) == {SONNET, HAIKU}
    with pytest.raises(ConfigError, match="Flujo desconocido"):
        budget_for("otro", _settings(tmp_path))
