from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import math
from providers.pricing import ProviderPricingConfig

import uuid

class UsageEvent(BaseModel):
    """
    Unified economic usage abstraction.
    Normalizes provider operations (Gemini LLM calls, SerpApi web searches, ElevenLabs TTS).
    Serves as the authoritative record for runtime usage in the Real-Time Economic Ledger.
    """
    event_id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:16]}")
    execution_id: str
    provider: str # "gemini", "serpapi", "elevenlabs", "code_sandbox"
    operation: str # "generate_content", "search", "text_to_speech", "execute"
    units_consumed: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    model: Optional[str] = None
    estimated_cost: float = 0.0
    actual_cost: float = 0.0
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @field_validator("event_id", "execution_id", "provider")
    @classmethod
    def validate_non_empty_str(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Event identifier fields (event_id, execution_id, provider) cannot be empty")
        return v.strip()

    @field_validator("units_consumed", "input_tokens", "output_tokens")
    @classmethod
    def validate_non_negative_counts(cls, v: int) -> int:
        if v < 0:
            raise ValueError("UsageEvent metric counts must be non-negative")
        return v

    @field_validator("estimated_cost", "actual_cost")
    @classmethod
    def validate_cost(cls, v: float) -> float:
        if math.isnan(v) or math.isinf(v):
            raise ValueError(f"Cost must be a finite number, got {v}")
        if v < 0:
            raise ValueError(f"Cost cannot be negative, got {v}")
        return v

    @classmethod
    def create_llm_event(cls, execution_id: str, model: str, input_tokens: int, output_tokens: int, actual_cost: Optional[float] = None, event_id: Optional[str] = None) -> "UsageEvent":
        est_cost = ProviderPricingConfig.calculate_llm_cost(model, input_tokens, output_tokens)
        act_cost = actual_cost if actual_cost is not None else est_cost
        kwargs = {
            "execution_id": execution_id,
            "provider": "gemini",
            "operation": "generate_content",
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "model": model,
            "estimated_cost": est_cost,
            "actual_cost": act_cost
        }
        if event_id:
            kwargs["event_id"] = event_id
        return cls(**kwargs)

    @classmethod
    def create_tool_event(cls, execution_id: str, provider: str, operation: str, units: int = 1, actual_cost: Optional[float] = None, event_id: Optional[str] = None) -> "UsageEvent":
        est_cost = ProviderPricingConfig.calculate_tool_cost(provider, operation, units)
        act_cost = actual_cost if actual_cost is not None else est_cost
        kwargs = {
            "execution_id": execution_id,
            "provider": provider,
            "operation": operation,
            "units_consumed": units,
            "estimated_cost": est_cost,
            "actual_cost": act_cost
        }
        if event_id:
            kwargs["event_id"] = event_id
        return cls(**kwargs)

