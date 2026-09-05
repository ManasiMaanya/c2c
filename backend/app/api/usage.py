from fastapi import APIRouter


router = APIRouter(
    prefix="/agents",
    tags=["Usage"],
)


@router.get("/{agent_id}/usage")
def get_agent_usage(agent_id: str):
    return {
        "agent_id": agent_id,
        "message": "Usage analytics coming soon",
    }


@router.get("/{agent_id}/cost")
def get_agent_cost(agent_id: str):
    return {
        "agent_id": agent_id,
        "message": "Cost analytics coming soon",
    }