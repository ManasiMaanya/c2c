from fastapi import APIRouter


router = APIRouter(
    prefix="/agents",
    tags=["Risk"],
)


@router.get("/{agent_id}/risk")
def get_agent_risk(agent_id: str):
    return {
        "agent_id": agent_id,
        "message": "Risk analysis coming soon",
    }