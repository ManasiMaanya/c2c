from app.services.anomaly_detector import get_recent_events
from app.services.cost_engine import calculate_cost_metrics
from app.services.ai_analyzer import analyze_with_ai


def analyze_agent_security(agent_id: str):

    events = get_recent_events(
        agent_id,
        limit=50,
    )

    cost_metrics = calculate_cost_metrics(
        agent_id
    )

    telemetry = {
        "recent_event_count": len(events),
        "events": events,
    }

    analysis = analyze_with_ai(
        telemetry=telemetry,
        economic_metrics=cost_metrics,
    )

    return {
        "agent_id": agent_id,
        "ai_analysis": analysis.model_dump(),
        "economic_metrics": cost_metrics,
    }