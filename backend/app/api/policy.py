from fastapi import APIRouter, HTTPException

from app.services.policy_engine import evaluate_policy


router = APIRouter(
    prefix="/agents",
    tags=["Policy"],
)


@router.post("/{agent_id}/policy/evaluate")
def evaluate_agent_policy(agent_id: str):
    try:
        return evaluate_policy(agent_id)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )