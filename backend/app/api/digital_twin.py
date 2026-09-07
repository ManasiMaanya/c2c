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

from domain.models import EnterprisePolicy, Task, CurrentExecutionState, ProposedAction
from providers.usage_event import UsageEvent
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


class SelectPlanRequest(BaseModel):
    task: Task
    chosen_plan_name: str = "Balanced Plan"
    policy: Optional[EnterprisePolicy] = None


@router.post("/select-plan")
def api_select_plan(req: SelectPlanRequest):
    try:
        return DigitalTwinFacade.select_plan(req.task, req.chosen_plan_name, req.policy)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plan selection error: {str(e)}")


class ResimulateRequest(BaseModel):
    current_state: CurrentExecutionState
    policy: Optional[EnterprisePolicy] = None


@router.post("/resimulate")
def api_resimulate_execution(req: ResimulateRequest):
    try:
        result = DigitalTwinFacade.resimulate_execution(req.current_state, req.policy)
        return result.model_dump()
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resimulation error: {str(e)}")


class StartSessionRequest(BaseModel):
    task: Task
    chosen_plan_name: str = "Balanced Plan"
    policy: Optional[EnterprisePolicy] = None


@router.post("/runtime/start")
def api_start_execution_session(req: StartSessionRequest):
    try:
        session = DigitalTwinFacade.start_execution_session(req.task, req.chosen_plan_name, req.policy)
        return session.model_dump()
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session initialization error: {str(e)}")


@router.post("/runtime/authorize-action")
def api_authorize_action(action: ProposedAction):
    try:
        decision = DigitalTwinFacade.authorize_action(action.execution_id, action)
        return decision.model_dump()
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Action authorization error: {str(e)}")


@router.post("/runtime/record-event")
def api_record_usage_event(event: UsageEvent):
    try:
        success, msg, act_cost = DigitalTwinFacade.record_usage_event(event)
        if not success:
            raise HTTPException(status_code=400, detail=msg)
        return {"success": success, "message": msg, "actual_cost": act_cost}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Usage recording error: {str(e)}")


@router.get("/runtime/ledger-state/{execution_id}")
def api_get_ledger_state(execution_id: str):
    try:
        summary = DigitalTwinFacade.get_ledger_state(execution_id)
        if summary["event_count"] == 0 and summary["max_budget"] == 0.0:
            _ = DigitalTwinFacade.start_execution_session
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ledger retrieval error: {str(e)}")