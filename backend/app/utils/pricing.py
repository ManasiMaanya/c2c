# app/utils/pricing.py

MODEL_PRICING = {
    "demo-model": {
        "input_per_1m": 0.50,
        "output_per_1m": 1.50,
    },

    # We can add real models later.
    "default": {
        "input_per_1m": 1.00,
        "output_per_1m": 2.00,
    },
}


def get_model_pricing(model: str) -> dict:
    """
    Return pricing configuration for a model.
    Falls back to default pricing if the model is unknown.
    """
    return MODEL_PRICING.get(model, MODEL_PRICING["default"])


def calculate_token_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float:
    """
    Calculate LLM cost from input/output token usage.
    """

    pricing = get_model_pricing(model)

    input_cost = (
        input_tokens / 1_000_000
    ) * pricing["input_per_1m"]

    output_cost = (
        output_tokens / 1_000_000
    ) * pricing["output_per_1m"]

    return round(input_cost + output_cost, 6)