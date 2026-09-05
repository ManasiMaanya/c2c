from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.db.supabase import supabase
from app.schemas.event import UsageEventCreate


router = APIRouter(
    prefix="/events",
    tags=["Telemetry"],
)


@router.post("/")
def create_usage_event(event: UsageEventCreate):
    timestamp = event.timestamp or datetime.now(timezone.utc)

    event_data = {
        "agent_id": event.agent_id,
        "timestamp": timestamp.isoformat(),
        "model": event.model,
        "input_tokens": event.input_tokens,
        "output_tokens": event.output_tokens,
        "tool_calls": event.tool_calls,
        "latency_ms": event.latency_ms,
        "estimated_cost": event.estimated_cost,
        "metadata": event.metadata or {},
    }

    response = (
        supabase
        .table("usage_events")
        .insert(event_data)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=500,
            detail="Failed to create usage event",
        )

    return response.data[0]