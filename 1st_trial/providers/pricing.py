from typing import Dict, Any
import math
from decimal import Decimal, ROUND_HALF_UP

class ProviderPricingConfig:
    """
    Configuration-driven pricing repository for external AI providers & tools.
    Zero real API calls are executed by this simulation engine.
    """

    # LLM Provider Pricing (USD per 1,000,000 tokens)
    LLM_PRICING: Dict[str, Dict[str, float]] = {
        "gemini-2.5-flash-lite": {
            "input_per_1m": 0.0375,
            "output_per_1m": 0.15
        },
        "gemini-2.5-flash": {
            "input_per_1m": 0.075,
            "output_per_1m": 0.30
        },
        "gemini-3.1-pro": {
            "input_per_1m": 1.25,
            "output_per_1m": 5.00
        }
    }

    # Search & Tool Provider Pricing (USD per call)
    TOOL_PRICING: Dict[str, Dict[str, float]] = {
        "serpapi": {
            "search_per_call": 0.01 # $0.01 per search
        },
        "elevenlabs": {
            "tts_per_1k_chars": 0.03 # $0.03 per 1,000 voice characters
        },
        "code_sandbox": {
            "execution_per_call": 0.005 # $0.005 per sandbox execution
        }
    }

    @classmethod
    def calculate_llm_cost(cls, model: str, input_tokens: int, output_tokens: int, strict: bool = False) -> float:
        if input_tokens < 0 or output_tokens < 0:
            raise ValueError(f"Token counts cannot be negative: input_tokens={input_tokens}, output_tokens={output_tokens}")
        
        model_clean = (model or "").strip()
        if strict and model_clean not in cls.LLM_PRICING:
            raise ValueError(f"Unknown LLM model '{model}' is not permitted by pricing configuration")

        if not model_clean:
            model_clean = "gemini-2.5-flash"
        
        pricing = cls.LLM_PRICING.get(model_clean, cls.LLM_PRICING["gemini-2.5-flash"])
        input_cost = (input_tokens / 1_000_000.0) * pricing["input_per_1m"]
        output_cost = (output_tokens / 1_000_000.0) * pricing["output_per_1m"]
        return round(input_cost + output_cost, 6)

    @classmethod
    def calculate_tool_cost(cls, provider: str, operation: str, units: int = 1, strict: bool = False) -> float:
        if units < 0:
            raise ValueError(f"Tool execution units cannot be negative: units={units}")
        provider_clean = (provider or "").lower().strip()
        
        if strict and provider_clean not in cls.TOOL_PRICING:
            raise ValueError(f"Unknown tool provider '{provider}' is not permitted by pricing configuration")

        if provider_clean == "serpapi":
            return round(units * cls.TOOL_PRICING["serpapi"]["search_per_call"], 6)
        elif provider_clean == "elevenlabs":
            return round((units / 1000.0) * cls.TOOL_PRICING["elevenlabs"]["tts_per_1k_chars"], 6)
        elif provider_clean == "code_sandbox":
            return round(units * cls.TOOL_PRICING["code_sandbox"]["execution_per_call"], 6)
        
        if strict:
            raise ValueError(f"Unknown provider '{provider}' cannot be priced in strict mode")
        return round(units * 0.001, 6)

    @classmethod
    def calculate_llm_cost_decimal(cls, model: str, input_tokens: int, output_tokens: int, strict: bool = False) -> Decimal:
        cost_float = cls.calculate_llm_cost(model, input_tokens, output_tokens, strict=strict)
        return Decimal(str(cost_float)).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)

    @classmethod
    def calculate_tool_cost_decimal(cls, provider: str, operation: str, units: int = 1, strict: bool = False) -> Decimal:
        cost_float = cls.calculate_tool_cost(provider, operation, units, strict=strict)
        return Decimal(str(cost_float)).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)


