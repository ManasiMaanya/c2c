import sys
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Make the tested Digital Twin engine available to the backend.
PROJECT_ROOT = Path(__file__).resolve().parents[3]
TRIAL_PATH = PROJECT_ROOT / "1st_trial"

if str(TRIAL_PATH) not in sys.path:
    sys.path.insert(0, str(TRIAL_PATH))

from domain.models import EnterprisePolicy, Task
from engine.digital_twin import DigitalTwinFacade


router = APIRouter(
    prefix="/digital-twin",
    tags=["Digital Twin"],
)


class SimulateRequest(BaseModel):
    task: Task
    policy: Optional[EnterprisePolicy] = None


@router.post("/simulate")
def simulate_task(request: SimulateRequest):
    try:
        result = DigitalTwinFacade.simulate_task(
            task=request.task,
            policy=request.policy,
        )

        return result.model_dump()

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Digital Twin simulation error: {exc}",
        )