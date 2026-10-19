"""Initial values of the /documentador/ parameters (infrastructure-design.md).

Prices are reference USD per million tokens and must be replaced by the Bedrock prices in
us-east-1 before U1. Model IDs are verified in the infrastructure design of U1.
"""

SONNET = "anthropic.claude-sonnet-5-5"
HAIKU = "anthropic.claude-haiku-5-5"

MODELOS = {
    "taxonomista": {"modelo": SONNET, "esfuerzo": "medium", "max_tokens": 16000},
    "redactor": {"modelo": SONNET, "esfuerzo": "medium", "max_tokens": 16000},
    "validador": {"modelo": SONNET, "esfuerzo": "medium", "max_tokens": 16000},
    "impacto": {"modelo": SONNET, "esfuerzo": "medium", "max_tokens": 16000},
    "investigador": {"modelo": HAIKU, "esfuerzo": "low", "max_tokens": 8000},
    "contraste": {"modelo": HAIKU, "esfuerzo": "low", "max_tokens": 8000},
    "admision": {"modelo": HAIKU, "esfuerzo": "low", "max_tokens": 8000},
    "evaluador": {"modelo": HAIKU, "esfuerzo": "low", "max_tokens": 8000},
}

PRECIOS = {
    SONNET: {"entrada": 2.0, "salida": 10.0, "cache_lectura": 0.2, "cache_escritura": 2.5},
    HAIKU: {"entrada": 0.1, "salida": 0.5, "cache_lectura": 0.01, "cache_escritura": 0.125},
}

TOPES_USD = {"mapa": 1.00, "documento": 0.60, "necesidad": 0.40, "evaluacion": 0.20}

PRESUPUESTO_USD = 10
AVISOS_REALES = (50, 80, 100)
AVISOS_PRONOSTICO = (100,)
