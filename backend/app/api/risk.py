from fastapi import APIRouter, HTTPException

from app.services.risk_engine import calculate_risk_score
from app.services.security_analyzer import analyze_agent_security


router = APIRouter(
    prefix="/agents",
    tags=["Risk"],
)


@router.get("/{agent_id}/risk")
def get_agent_risk(agent_id: str):
    try:
        return calculate_risk_score(agent_id)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.get("/{agent_id}/ai-analysis")
def get_ai_analysis(agent_id: str):
    try:
        return analyze_agent_security(agent_id)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )