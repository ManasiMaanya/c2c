from fastapi import APIRouter


router = APIRouter(
    prefix="/agents",
    tags=["Simulation"],
)


@router.post("/{agent_id}/simulate")
def simulate_agent(agent_id: str):
    return {
        "agent_id": agent_id,
        "message": "Attack simulation coming soon",
    }