from app.services.risk_engine import calculate_risk_score


def evaluate_policy(agent_id: str) -> dict:
    risk = calculate_risk_score(agent_id)

    score = risk["risk_score"]
    level = risk["risk_level"]

    if score < 30:
        action = "ALLOW"
        reason = "Agent behavior is within normal operating parameters."

    elif score < 60:
        action = "WARN"
        reason = "Anomalous behavior detected. Continue monitoring."

    elif score < 80:
        action = "THROTTLE"
        reason = "High-risk behavior detected. Reduce request frequency."

    elif score < 95:
        action = "RESTRICT"
        reason = "Severe economic risk detected. Restrict agent capabilities."

    else:
        action = "BLOCK"
        reason = "Critical economic threat detected. Block agent activity."

    model_downgrade = 60 <= score < 95

    return {
        "agent_id": agent_id,
        "risk_score": score,
        "risk_level": level,
        "action": action,
        "model_downgrade": model_downgrade,
        "reason": reason,
    }