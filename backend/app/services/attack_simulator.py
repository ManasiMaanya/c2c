from datetime import datetime, timedelta, timezone

from app.db.supabase import supabase
from app.utils.pricing import calculate_token_cost


def generate_request_flood(
    agent_id: str,
    normal_requests: int = 5,
    attack_requests: int = 25,
) -> dict:

    now = datetime.now(timezone.utc)

    events = []

    # -------------------------
    # NORMAL TRAFFIC
    # -------------------------

    for i in range(normal_requests):

        timestamp = now - timedelta(minutes=10) + timedelta(
            seconds=i * 60
        )

        input_tokens = 800
        output_tokens = 400

        cost = calculate_token_cost(
            model="demo-model",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

        events.append({
            "agent_id": agent_id,
            "timestamp": timestamp.isoformat(),
            "model": "demo-model",
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "tool_calls": 1,
            "latency_ms": 800,
            "estimated_cost": cost,
            "metadata": {
                "simulation": True,
                "scenario": "normal",
            },
        })

    # -------------------------
    # REQUEST FLOOD
    # -------------------------

    for i in range(attack_requests):

        timestamp = now - timedelta(seconds=i * 5)

        input_tokens = 1000
        output_tokens = 500

        cost = calculate_token_cost(
            model="demo-model",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

        events.append({
            "agent_id": agent_id,
            "timestamp": timestamp.isoformat(),
            "model": "demo-model",
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "tool_calls": 2,
            "latency_ms": 700,
            "estimated_cost": cost,
            "metadata": {
                "simulation": True,
                "scenario": "request_flood",
            },
        })

    # Insert all events
    response = (
        supabase
        .table("usage_events")
        .insert(events)
        .execute()
    )

    return {
        "agent_id": agent_id,
        "scenario": "request_flood",
        "normal_events": normal_requests,
        "attack_events": attack_requests,
        "inserted_events": len(response.data or []),
    }