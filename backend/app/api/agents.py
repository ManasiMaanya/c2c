from fastapi import APIRouter, HTTPException

from app.db.supabase import supabase
from app.schemas.agent import AgentCreate, AgentUpdate

router = APIRouter(
    prefix="/agents",
    tags=["Agents"],
)


@router.post("/")
def create_agent(agent: AgentCreate):
    response = (
        supabase
        .table("agents")
        .insert({
            "name": agent.name,
            "model": agent.model,
            "budget": agent.budget,
        })
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=500,
            detail="Failed to create agent",
        )

    return response.data[0]


@router.get("/")
def get_agents():
    response = (
        supabase
        .table("agents")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    return response.data


@router.get("/{agent_id}")
def get_agent(agent_id: str):
    response = (
        supabase
        .table("agents")
        .select("*")
        .eq("id", agent_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=404,
            detail="Agent not found",
        )

    return response.data[0]
    
    response = (
        supabase
        .table("agents")
        .select("*")
        .eq("id", agent_id)
        .single()
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=404,
            detail="Agent not found",
        )

    return response.data


@router.patch("/{agent_id}")
def update_agent(
    agent_id: str,
    agent: AgentUpdate,
):
    update_data = agent.model_dump(
        exclude_none=True
    )

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update",
        )

    response = (
        supabase
        .table("agents")
        .update(update_data)
        .eq("id", agent_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=404,
            detail="Agent not found",
        )

    return response.data[0]

@router.delete("/{agent_id}")
def delete_agent(agent_id: str):
    response = (
        supabase
        .table("agents")
        .delete()
        .eq("id", agent_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=404,
            detail="Agent not found",
        )

    return {
        "message": "Agent deleted successfully",
        "agent_id": agent_id,
    }