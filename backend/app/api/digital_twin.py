from fastapi import APIRouter


router = APIRouter(
    prefix="/agents",
    tags=["Digital Twin"],
)


@router.get("/{agent_id}/digital-twin")
def get_digital_twin(agent_id: str):
    return {
        "agent_id": agent_id,
        "message": "Digital Twin simulation coming soon",
    }