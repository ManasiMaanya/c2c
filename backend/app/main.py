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
from app.api.dashboard import router as dashboard_router

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
app.include_router(dashboard_router)

# Mount frontend files from 1st_trial
from pathlib import Path
from typing import Optional
from fastapi import HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

TRIAL_DIR = Path(__file__).resolve().parents[2] / "1st_trial"
STATIC_DIR = TRIAL_DIR / "static"

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def read_root():
    index_path = TRIAL_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {
        "status": "ok",
        "service": "denial-of-wallet",
    }


@app.get("/app")
@app.get("/app/{full_path:path}")
def read_app_control_plane(full_path: Optional[str] = None):
    app_path = TRIAL_DIR / "app.html"
    if app_path.exists():
        return FileResponse(str(app_path))
    raise HTTPException(status_code=404, detail="app.html control plane not found")


@app.get("/wallet.png")
def get_wallet_image():
    wallet_path = TRIAL_DIR / "wallet.png"
    if wallet_path.exists():
        return FileResponse(str(wallet_path), media_type="image/png")
    raise HTTPException(status_code=404, detail="wallet.png asset not found")


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