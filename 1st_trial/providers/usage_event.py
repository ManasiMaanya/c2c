from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from providers.pricing import ProviderPricingConfig

class UsageEvent(BaseModel):
    """
    Unified economic usage abstraction.
    Normalizes provider operations (Gemini LLM calls, SerpApi web searches, ElevenLabs TTS).
    """
    event_id: str = Field(default_factory=lambda: f"evt_{datetime.now(timezone.utc).strftime('%H%M%S%f')}")
    execution_id: str
    provider: str # "gemini", "serpapi", "elevenlabs", "code_sandbox"
    operation: str # "generate_content", "search", "text_to_speech", "execute"
    units_consumed: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    model: Optional[str] = None
    estimated_cost: float = 0.0
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @classmethod
    def create_llm_event(cls, execution_id: str, model: str, input_tokens: int, output_tokens: int) -> "UsageEvent":
        cost = ProviderPricingConfig.calculate_llm_cost(model, input_tokens, output_tokens)
        return cls(
            execution_id=execution_id,
            provider="gemini",
            operation="generate_content",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model,
            estimated_cost=cost
        )

    @classmethod
    def create_tool_event(cls, execution_id: str, provider: str, operation: str, units: int = 1) -> "UsageEvent":
        cost = ProviderPricingConfig.calculate_tool_cost(provider, operation, units)
        return cls(
            execution_id=execution_id,
            provider=provider,
            operation=operation,
            units_consumed=units,
            estimated_cost=cost
        )
