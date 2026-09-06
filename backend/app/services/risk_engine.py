from app.services.anomaly_detector import analyze_agent
from app.services.cost_engine import calculate_cost_metrics


def calculate_risk_score(agent_id: str) -> dict:
    """
    Calculate overall economic security risk.
    """

    anomalies = analyze_agent(agent_id)
    cost = calculate_cost_metrics(agent_id)

    detectors = anomalies["detectors"]

    request_anomaly = detectors["request_flood"]["score"]
    token_anomaly = detectors["token_explosion"]["score"]
    cost_acceleration = detectors["cost_acceleration"]["score"]

    # --------------------------------
    # Budget Risk
    # --------------------------------

    exhaustion_minutes = cost["time_to_exhaustion_minutes"]

    if exhaustion_minutes is None:
        budget_risk = 0

    elif exhaustion_minutes <= 15:
        budget_risk = 100

    elif exhaustion_minutes <= 30:
        budget_risk = 90

    elif exhaustion_minutes <= 60:
        budget_risk = 75

    elif exhaustion_minutes <= 120:
        budget_risk = 50

    elif exhaustion_minutes <= 360:
        budget_risk = 25

    else:
        budget_risk = 0

    # --------------------------------
    # Maximum attack signal
    # --------------------------------

    attack_signal = max(
        request_anomaly,
        token_anomaly,
        cost_acceleration,
    )

    # --------------------------------
    # Combined risk
    # --------------------------------

    risk_score = (
        attack_signal * 0.60
        + request_anomaly * 0.10
        + token_anomaly * 0.10
        + cost_acceleration * 0.05
        + budget_risk * 0.15
    )

    risk_score = round(
        min(100, max(0, risk_score)),
        2,
    )

    # --------------------------------
    # Risk Level
    # --------------------------------

    if risk_score < 30:
        risk_level = "LOW"

    elif risk_score < 60:
        risk_level = "MEDIUM"

    elif risk_score < 80:
        risk_level = "HIGH"

    else:
        risk_level = "CRITICAL"

    return {
        "agent_id": agent_id,
        "risk_score": risk_score,
        "risk_level": risk_level,

        "risk_factors": {
            "request_anomaly": request_anomaly,
            "token_anomaly": token_anomaly,
            "cost_acceleration": cost_acceleration,
            "budget_risk": budget_risk,
        },

        "economic_metrics": {
            "burn_rate_per_minute": cost[
                "burn_rate_per_minute"
            ],
            "projected_cost_1h": cost[
                "projected_cost_1h"
            ],
            "projected_cost_24h": cost[
                "projected_cost_24h"
            ],
            "time_to_exhaustion_minutes": exhaustion_minutes,
            "remaining_budget": cost[
                "remaining_budget"
            ],
        },
    }