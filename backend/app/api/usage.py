from fastapi import APIRouter, HTTPException

from app.services.cost_engine import calculate_cost_metrics


router = APIRouter(
    prefix="/agents",
    tags=["Usage"],
)


@router.get("/{agent_id}/usage")
def get_agent_usage(agent_id: str):
    try:
        return calculate_cost_metrics(agent_id)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.get("/{agent_id}/cost")
def get_agent_cost(agent_id: str):
    try:
        return calculate_cost_metrics(agent_id)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )