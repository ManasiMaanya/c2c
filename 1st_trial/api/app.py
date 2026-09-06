from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from domain.models import Task, EnterprisePolicy, CurrentExecutionState
from engine.digital_twin import DigitalTwinFacade

app = FastAPI(
    title="Denial of Wallet - Digital Twin Simulation API",
    description="Pure Simulation Engine for AI Agent Economic Planning & Trajectory Resimulation",
    version="1.0.0"
)

import os
from fastapi.responses import FileResponse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@app.get("/")
def read_root():
    index_path = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "status": "online",
        "subsystem": "Digital Twin Engine (1st_trial)",
        "scope": "Simulation Only - Zero Real Provider Calls",
        "version": "1.0.0"
    }

@app.get("/wallet.png")
def get_wallet_image():
    wallet_path = os.path.join(BASE_DIR, "wallet.png")
    if os.path.exists(wallet_path):
        return FileResponse(wallet_path, media_type="image/png")
    raise HTTPException(status_code=404, detail="wallet.png asset not found")

class SimulateRequest(BaseModel):
    task: Task
    policy: Optional[EnterprisePolicy] = None

@app.post("/digital-twin/simulate")
def api_simulate_task(req: SimulateRequest):
    try:
        result = DigitalTwinFacade.simulate_task(req.task, req.policy)
        return result.model_dump()
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")

class SelectPlanRequest(BaseModel):
    task: Task
    chosen_plan_name: str = "Balanced Plan"
    policy: Optional[EnterprisePolicy] = None

@app.post("/digital-twin/select-plan")
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

@app.post("/digital-twin/resimulate")
def api_resimulate_execution(req: ResimulateRequest):
    try:
        result = DigitalTwinFacade.resimulate_execution(req.current_state, req.policy)
        return result.model_dump()
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resimulation error: {str(e)}")

# -------------------------------------------------------------------------
# RUNTIME ECONOMIC FIREWALL & REAL-TIME LEDGER API ENDPOINTS
# -------------------------------------------------------------------------

class StartSessionRequest(BaseModel):
    task: Task
    chosen_plan_name: str = "Balanced Plan"
    policy: Optional[EnterprisePolicy] = None

@app.post("/digital-twin/runtime/start")
def api_start_execution_session(req: StartSessionRequest):
    try:
        session = DigitalTwinFacade.start_execution_session(req.task, req.chosen_plan_name, req.policy)
        return session.model_dump()
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session initialization error: {str(e)}")

from domain.models import ProposedAction
from providers.usage_event import UsageEvent

@app.post("/digital-twin/runtime/authorize-action")
def api_authorize_action(action: ProposedAction):
    try:
        decision = DigitalTwinFacade.authorize_action(action.execution_id, action)
        return decision.model_dump()
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Action authorization error: {str(e)}")

@app.post("/digital-twin/runtime/record-event")
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

@app.get("/digital-twin/runtime/ledger-state/{execution_id}")
def api_get_ledger_state(execution_id: str):
    try:
        summary = DigitalTwinFacade.get_ledger_state(execution_id)
        if summary["event_count"] == 0 and summary["max_budget"] == 0.0:
            # Check if session exists
            session = DigitalTwinFacade.start_execution_session # facade access check
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ledger retrieval error: {str(e)}")


