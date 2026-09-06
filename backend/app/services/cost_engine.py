# app/services/cost_engine.py

from datetime import datetime, timedelta, timezone
from app.db.supabase import supabase


def get_usage_events(agent_id: str):
    response = (
        supabase
        .table("usage_events")
        .select("*")
        .eq("agent_id", agent_id)
        .order("timestamp", desc=False)
        .execute()
    )

    return response.data or []


def calculate_cost_metrics(agent_id: str) -> dict:
    events = get_usage_events(agent_id)

    if not events:
        return {
            "agent_id": agent_id,
            "total_spend": 0.0,
            "remaining_budget": 0.0,
            "burn_rate_per_minute": 0.0,
            "requests_per_minute": 0.0,
            "tokens_per_minute": 0.0,
            "cost_per_minute": 0.0,
            "projected_cost_1h": 0.0,
            "projected_cost_24h": 0.0,
            "time_to_exhaustion_minutes": None,
        }

    total_spend = sum(
        float(event.get("estimated_cost") or 0)
        for event in events
    )

    total_requests = len(events)

    total_tokens = sum(
        int(event.get("input_tokens") or 0)
        + int(event.get("output_tokens") or 0)
        for event in events
    )

    first_timestamp = datetime.fromisoformat(
        events[0]["timestamp"].replace("Z", "+00:00")
    )

    last_timestamp = datetime.fromisoformat(
        events[-1]["timestamp"].replace("Z", "+00:00")
    )

    duration_seconds = (
        last_timestamp - first_timestamp
    ).total_seconds()

    duration_minutes = max(duration_seconds / 60, 1)

    requests_per_minute = (
        total_requests / duration_minutes
    )

    tokens_per_minute = (
        total_tokens / duration_minutes
    )

    cost_per_minute = (
        total_spend / duration_minutes
    )

    projected_cost_1h = cost_per_minute * 60

    projected_cost_24h = cost_per_minute * 60 * 24

    # Fetch agent budget
    agent_response = (
        supabase
        .table("agents")
        .select("budget")
        .eq("id", agent_id)
        .single()
        .execute()
    )

    budget = float(agent_response.data["budget"])

    remaining_budget = max(
        budget - total_spend,
        0,
    )

    if cost_per_minute > 0:
        time_to_exhaustion = (
            remaining_budget / cost_per_minute
        )
    else:
        time_to_exhaustion = None

    return {
        "agent_id": agent_id,
        "total_spend": round(total_spend, 4),
        "remaining_budget": round(remaining_budget, 4),
        "burn_rate_per_minute": round(cost_per_minute, 4),
        "requests_per_minute": round(requests_per_minute, 2),
        "tokens_per_minute": round(tokens_per_minute, 2),
        "cost_per_minute": round(cost_per_minute, 4),
        "projected_cost_1h": round(projected_cost_1h, 4),
        "projected_cost_24h": round(projected_cost_24h, 4),
        "time_to_exhaustion_minutes": (
            round(time_to_exhaustion, 2)
            if time_to_exhaustion is not None
            else None
        ),
    }