from fastapi import APIRouter


router = APIRouter(
    prefix="/agents",
    tags=["Policy"],
)


@router.post("/{agent_id}/policy/evaluate")
def evaluate_policy(agent_id: str):
    return {
        "agent_id": agent_id,
        "action": "ALLOW",
        "message": "Policy evaluation coming soon",
    }