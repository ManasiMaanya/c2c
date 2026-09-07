from fastapi import FastAPI

from app.api.agents import router as agents_router
from app.db.supabase import supabase
from app.api.events import router as events_router
from app.api.usage import router as usage_router
from app.api.attacks import router as attacks_router
from app.api.risk import router as risk_router
from app.api.digital_twin import router as digital_twin_router
from app.api.policy import router as policy_router
from app.api.simulation import router as simulation_router

app = FastAPI(
    title="Denial of Wallet",
    description="Economic Security Platform for Autonomous AI Agents",
    version="0.1.0",
)


app.include_router(agents_router)
app.include_router(events_router)
app.include_router(usage_router)
app.include_router(attacks_router)
app.include_router(risk_router)
app.include_router(digital_twin_router)
app.include_router(policy_router)
app.include_router(simulation_router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "denial-of-wallet",
    }


@app.get("/health/supabase")
def supabase_health_check():
    response = (
        supabase
        .table("agents")
        .select("id, name, model, budget, status")
        .limit(1)
        .execute()
    )

    return {
        "status": "ok",
        "supabase": True,
        "data": response.data,
    }