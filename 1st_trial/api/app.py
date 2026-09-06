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

@app.get("/")
def read_root():
    return {
        "status": "online",
        "subsystem": "Digital Twin Engine (1st_trial)",
        "scope": "Simulation Only - Zero Real Provider Calls",
        "version": "1.0.0"
    }

class SimulateRequest(BaseModel):
    task: Task
    policy: Optional[EnterprisePolicy] = None

@app.post("/digital-twin/simulate")
def api_simulate_task(req: SimulateRequest):
    result = DigitalTwinFacade.simulate_task(req.task, req.policy)
    return result.model_dump()

class SelectPlanRequest(BaseModel):
    task: Task
    chosen_plan_name: str = "Balanced Plan"
    policy: Optional[EnterprisePolicy] = None

@app.post("/digital-twin/select-plan")
def api_select_plan(req: SelectPlanRequest):
    return DigitalTwinFacade.select_plan(req.task, req.chosen_plan_name, req.policy)

class ResimulateRequest(BaseModel):
    current_state: CurrentExecutionState
    policy: Optional[EnterprisePolicy] = None

@app.post("/digital-twin/resimulate")
def api_resimulate_execution(req: ResimulateRequest):
    result = DigitalTwinFacade.resimulate_execution(req.current_state, req.policy)
    return result.model_dump()
