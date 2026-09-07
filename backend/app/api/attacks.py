from fastapi import APIRouter


router = APIRouter(
    prefix="/agents",
    tags=["Attacks"],
)


@router.get("/{agent_id}/attacks")
def get_agent_attacks(agent_id: str):
    return {
        "agent_id": agent_id,
        "attacks": [],
        "message": "Attack analysis coming soon",
    }