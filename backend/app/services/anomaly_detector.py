from app.db.supabase import supabase


def get_recent_events(agent_id: str, limit: int = 50):
    response = (
        supabase
        .table("usage_events")
        .select("*")
        .eq("agent_id", agent_id)
        .order("timestamp", desc=True)
        .limit(limit)
        .execute()
    )

    return response.data or []


def detect_request_flood(events: list) -> dict:
    if len(events) < 2:
        return {
            "detected": False,
            "score": 0,
            "message": "Not enough data",
        }

    recent_count = len(events)

    # Simple prototype threshold.
    # We will replace this with baseline comparison later.
    if recent_count >= 20:
        score = min(100, recent_count * 4)

        return {
            "detected": True,
            "score": score,
            "message": f"High request volume detected: {recent_count} recent requests",
        }

    return {
        "detected": False,
        "score": 0,
        "message": "Request volume appears normal",
    }


def detect_token_explosion(events: list) -> dict:
    if len(events) < 2:
        return {
            "detected": False,
            "score": 0,
            "message": "Not enough data",
        }

    token_values = [
        (event.get("input_tokens") or 0)
        + (event.get("output_tokens") or 0)
        for event in events
    ]

    average_tokens = sum(token_values) / len(token_values)
    latest_tokens = token_values[0]

    if average_tokens == 0:
        return {
            "detected": False,
            "score": 0,
            "message": "No token usage detected",
        }

    ratio = latest_tokens / average_tokens

    if ratio >= 5:
        score = min(100, int(ratio * 15))

        return {
            "detected": True,
            "score": score,
            "message": f"Token explosion detected: {ratio:.1f}x baseline",
        }

    return {
        "detected": False,
        "score": 0,
        "message": "Token usage appears normal",
    }


def detect_cost_acceleration(events: list) -> dict:
    if len(events) < 4:
        return {
            "detected": False,
            "score": 0,
            "message": "Not enough data",
        }

    costs = [
        float(event.get("estimated_cost") or 0)
        for event in events
    ]

    recent_cost = costs[0]
    older_costs = costs[1:]

    average_previous = sum(older_costs) / len(older_costs)

    if average_previous == 0:
        return {
            "detected": False,
            "score": 0,
            "message": "No previous cost baseline",
        }

    ratio = recent_cost / average_previous

    if ratio >= 5:
        score = min(100, int(ratio * 15))

        return {
            "detected": True,
            "score": score,
            "message": f"Cost acceleration detected: {ratio:.1f}x baseline",
        }

    return {
        "detected": False,
        "score": 0,
        "message": "Cost growth appears normal",
    }


def analyze_agent(agent_id: str) -> dict:
    events = get_recent_events(agent_id)

    request_flood = detect_request_flood(events)
    token_explosion = detect_token_explosion(events)
    cost_acceleration = detect_cost_acceleration(events)

    detected = (
        request_flood["detected"]
        or token_explosion["detected"]
        or cost_acceleration["detected"]
    )

    return {
        "agent_id": agent_id,
        "attack_detected": detected,
        "detectors": {
            "request_flood": request_flood,
            "token_explosion": token_explosion,
            "cost_acceleration": cost_acceleration,
        },
    }