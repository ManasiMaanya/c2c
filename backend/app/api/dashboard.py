from fastapi import APIRouter
from app.db.supabase import supabase

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)

@router.get("/overview")
def get_dashboard_overview():
    # 1. Fetch agents
    agents_resp = supabase.table("agents").select("*").execute()
    agents = agents_resp.data if agents_resp and agents_resp.data else []
    
    if not agents:
        default_agents = [
            {
                "id": "ag_8801_cs",
                "name": "Customer Support Agent",
                "model": "gemini-2.5-flash",
                "budget": 100.00,
                "status": "active",
                "created_at": "2026-09-06T10:00:00Z"
            },
            {
                "id": "ag_8802_code",
                "name": "Code Assistant Agent",
                "model": "gemini-3.1-pro",
                "budget": 150.00,
                "status": "active",
                "created_at": "2026-09-06T11:30:00Z"
            },
            {
                "id": "ag_8803_fin",
                "name": "Finance Analytics Bot",
                "model": "gemini-2.5-flash-lite",
                "budget": 50.00,
                "status": "paused",
                "created_at": "2026-09-06T12:15:00Z"
            }
        ]
        try:
            supabase.table("agents").insert(default_agents).execute()
            agents_resp = supabase.table("agents").select("*").execute()
            agents = agents_resp.data if agents_resp and agents_resp.data else default_agents
        except Exception:
            agents = default_agents

    enriched_agents = []
    default_metrics = {
        "ag_8801_cs": {"actual_spend": 14.2800, "risk_score": 28, "risk_level": "low", "burn_rate": 1.85, "projected_24h": 44.40, "time_to_exhaustion": 2780},
        "ag_8802_code": {"actual_spend": 28.4400, "risk_score": 65, "risk_level": "high", "burn_rate": 5.40, "projected_24h": 129.60, "time_to_exhaustion": 1350},
        "ag_8803_fin": {"actual_spend": 6.0000, "risk_score": 15, "risk_level": "low", "burn_rate": 0.40, "projected_24h": 9.60, "time_to_exhaustion": 6600}
    }

    for ag in agents:
        ag_id = ag.get("id")
        metrics = default_metrics.get(ag_id, {"actual_spend": 0.0, "risk_score": 10, "risk_level": "low", "burn_rate": 0.50, "projected_24h": 12.0, "time_to_exhaustion": 5000})
        enriched = {**ag}
        for k, v in metrics.items():
            if k not in enriched:
                enriched[k] = v
        enriched_agents.append(enriched)

    # 2. Fetch usage events
    usage_resp = supabase.table("usage_events").select("*").execute()
    raw_usage = usage_resp.data if usage_resp and usage_resp.data else []
    if not raw_usage or "actual_cost" not in raw_usage[0]:
        usage_events = [
            { "id": "evt_9901", "agent_id": "ag_8801_cs", "agent_name": "Customer Support Agent", "timestamp": "2026-09-06T18:30:12Z", "model": "gemini-2.5-flash", "input_tokens": 14200, "output_tokens": 3800, "tool_calls": 2, "latency_ms": 640, "estimated_cost": 0.0022, "actual_cost": 0.0022, "operation": "generate_content", "provider": "gemini" },
            { "id": "evt_9902", "agent_id": "ag_8801_cs", "agent_name": "Customer Support Agent", "timestamp": "2026-09-06T18:32:45Z", "model": "serpapi", "input_tokens": 0, "output_tokens": 0, "tool_calls": 1, "latency_ms": 310, "estimated_cost": 0.0100, "actual_cost": 0.0100, "operation": "search", "provider": "serpapi" },
            { "id": "evt_9903", "agent_id": "ag_8802_code", "agent_name": "Code Assistant Agent", "timestamp": "2026-09-06T18:35:00Z", "model": "gemini-3.1-pro", "input_tokens": 42000, "output_tokens": 12500, "tool_calls": 5, "latency_ms": 1820, "estimated_cost": 0.1150, "actual_cost": 0.1150, "operation": "generate_content", "provider": "gemini" },
            { "id": "evt_9904", "agent_id": "ag_8802_code", "agent_name": "Code Assistant Agent", "timestamp": "2026-09-06T18:38:22Z", "model": "code_sandbox", "input_tokens": 0, "output_tokens": 0, "tool_calls": 2, "latency_ms": 450, "estimated_cost": 0.0100, "actual_cost": 0.0100, "operation": "execute", "provider": "code_sandbox" },
            { "id": "evt_9905", "agent_id": "ag_8803_fin", "agent_name": "Finance Analytics Bot", "timestamp": "2026-09-06T18:40:11Z", "model": "elevenlabs", "input_tokens": 0, "output_tokens": 0, "tool_calls": 1, "latency_ms": 920, "estimated_cost": 0.0300, "actual_cost": 0.0300, "operation": "text_to_speech", "provider": "elevenlabs" }
        ]
    else:
        usage_events = raw_usage

    # 3. Fetch attack events
    attack_resp = supabase.table("attack_events").select("*").execute()
    raw_attacks = attack_resp.data if attack_resp and attack_resp.data else []
    if not raw_attacks or "attack_type" not in raw_attacks[0]:
        attack_events = [
            { "id": "atk_101", "agent_id": "ag_8802_code", "agent_name": "Code Assistant Agent", "timestamp": "2026-09-06T18:10:00Z", "attack_type": "DoW Rate Spike", "severity": 82, "confidence": 94.5, "details": { "description": "Rapid burst of 45 high-token requests in 10s", "blocked_cost": 0.3800 } },
            { "id": "atk_102", "agent_id": "ag_8801_cs", "agent_name": "Customer Support Agent", "timestamp": "2026-09-06T17:45:00Z", "attack_type": "Recursive Loop Attack", "severity": 78, "confidence": 89.0, "details": { "description": "Hallucinated tool calling loop detected", "blocked_cost": 0.2200 } },
            { "id": "atk_103", "agent_id": "ag_8802_code", "agent_name": "Code Assistant Agent", "timestamp": "2026-09-06T16:20:00Z", "attack_type": "Model Escalation Exploit", "severity": 65, "confidence": 91.2, "details": { "description": "Attempted unpermitted switch to Pro model", "blocked_cost": 0.5000 } }
        ]
    else:
        attack_events = raw_attacks

    # 4. Fetch policy actions
    policy_resp = supabase.table("policy_actions").select("*").execute()
    raw_policy = policy_resp.data if policy_resp and policy_resp.data else []
    if not raw_policy or "reason" not in raw_policy[0]:
        policy_actions = [
            { "id": "pa_501", "agent_id": "ag_8802_code", "timestamp": "2026-09-06T18:38:22Z", "action": "block", "reason": "Projected cost $1.0700 exceeds selected budget cap $1.0000", "risk_score": 82, "metadata": { "projected_cost": 1.07, "max_budget": 1.00 } },
            { "id": "pa_502", "agent_id": "ag_8802_code", "timestamp": "2026-09-06T18:35:00Z", "action": "model_downgrade", "reason": "High token burn rate detected. Model downgraded from Gemini Pro to Flash", "risk_score": 65, "metadata": { "previous_model": "gemini-3.1-pro", "new_model": "gemini-2.5-flash" } },
            { "id": "pa_503", "agent_id": "ag_8801_cs", "timestamp": "2026-09-06T18:32:45Z", "action": "throttle", "reason": "SerpApi search tool frequency exceeded 2 calls/min threshold", "risk_score": 45, "metadata": { "tool": "serpapi", "delay_ms": 2000 } },
            { "id": "pa_504", "agent_id": "ag_8801_cs", "timestamp": "2026-09-06T18:30:12Z", "action": "allow", "reason": "Action authorized cleanly within budget bounds", "risk_score": 15, "metadata": { "cost": 0.0022 } },
            { "id": "pa_505", "agent_id": "ag_8803_fin", "timestamp": "2026-09-06T18:25:00Z", "action": "warn", "reason": "Budget utilization reached 75% boundary", "risk_score": 55, "metadata": { "utilization_pct": 75 } }
        ]
    else:
        policy_actions = raw_policy

    total_spend = sum(a.get("actual_spend", 0.0) for a in enriched_agents)
    total_budget = sum(a.get("budget", 0.0) for a in enriched_agents)

    return {
        "agents": enriched_agents,
        "usage_events": usage_events,
        "attack_events": attack_events,
        "policy_actions": policy_actions,
        "summary": {
            "total_spend": round(total_spend, 4),
            "total_budget": round(total_budget, 2),
            "active_agents": sum(1 for a in enriched_agents if a.get("status") == "active"),
            "total_events": len(usage_events),
            "blocked_actions": sum(1 for pa in policy_actions if pa.get("action") == "block"),
            "allowed_actions": sum(1 for pa in policy_actions if pa.get("action") == "allow")
        }
    }
