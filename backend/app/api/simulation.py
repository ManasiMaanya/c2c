from fastapi import APIRouter, HTTPException

from app.services.attack_simulator import generate_request_flood

router = APIRouter(
    prefix="/agents",
    tags=["Simulation"],
)


@router.post("/{agent_id}/simulate")
def simulate_agent(agent_id: str):

    try:
        return generate_request_flood(agent_id)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )