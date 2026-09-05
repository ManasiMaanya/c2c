from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class UsageEventCreate(BaseModel):
    agent_id: str
    timestamp: datetime | None = None

    model: str = Field(min_length=1, max_length=100)

    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)

    tool_calls: int = Field(ge=0)
    latency_ms: int = Field(ge=0)

    estimated_cost: float = Field(ge=0)

    metadata: dict[str, Any] | None = None