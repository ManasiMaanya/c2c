import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("supabase")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_PUBLISHABLE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY")


class MockTable:
    def __init__(self, name: str, data_store: dict):
        self.name = name
        self.data_store = data_store
        if name not in self.data_store:
            if name == "agents":
                self.data_store[name] = [
                    {"id": "ag_8801_cs", "name": "Customer Support Agent", "model": "gemini-2.5-flash", "budget": 100.00, "status": "active"},
                    {"id": "ag_8802_code", "name": "Code Assistant Agent", "model": "gemini-3.1-pro", "budget": 150.00, "status": "active"},
                    {"id": "ag_8803_fin", "name": "Finance Analytics Bot", "model": "gemini-2.5-flash-lite", "budget": 50.00, "status": "paused"}
                ]
            elif name == "usage_events":
                self.data_store[name] = [
                    { "id": "evt_9901", "agent_id": "ag_8801_cs", "agent_name": "Customer Support Agent", "timestamp": "2026-09-06T18:30:12Z", "model": "gemini-2.5-flash", "input_tokens": 14200, "output_tokens": 3800, "tool_calls": 2, "latency_ms": 640, "estimated_cost": 0.0022, "actual_cost": 0.0022, "operation": "generate_content", "provider": "gemini" },
                    { "id": "evt_9902", "agent_id": "ag_8801_cs", "agent_name": "Customer Support Agent", "timestamp": "2026-09-06T18:32:45Z", "model": "serpapi", "input_tokens": 0, "output_tokens": 0, "tool_calls": 1, "latency_ms": 310, "estimated_cost": 0.0100, "actual_cost": 0.0100, "operation": "search", "provider": "serpapi" },
                    { "id": "evt_9903", "agent_id": "ag_8802_code", "agent_name": "Code Assistant Agent", "timestamp": "2026-09-06T18:35:00Z", "model": "gemini-3.1-pro", "input_tokens": 42000, "output_tokens": 12500, "tool_calls": 5, "latency_ms": 1820, "estimated_cost": 0.1150, "actual_cost": 0.1150, "operation": "generate_content", "provider": "gemini" },
                    { "id": "evt_9904", "agent_id": "ag_8802_code", "agent_name": "Code Assistant Agent", "timestamp": "2026-09-06T18:38:22Z", "model": "code_sandbox", "input_tokens": 0, "output_tokens": 0, "tool_calls": 2, "latency_ms": 450, "estimated_cost": 0.0100, "actual_cost": 0.0100, "operation": "execute", "provider": "code_sandbox" },
                    { "id": "evt_9905", "agent_id": "ag_8803_fin", "agent_name": "Finance Analytics Bot", "timestamp": "2026-09-06T18:40:11Z", "model": "elevenlabs", "input_tokens": 0, "output_tokens": 0, "tool_calls": 1, "latency_ms": 920, "estimated_cost": 0.0300, "actual_cost": 0.0300, "operation": "text_to_speech", "provider": "elevenlabs" }
                ]
            elif name == "attack_events":
                self.data_store[name] = [
                    { "id": "atk_101", "agent_id": "ag_8802_code", "agent_name": "Code Assistant Agent", "timestamp": "2026-09-06T18:10:00Z", "attack_type": "DoW Rate Spike", "severity": 82, "confidence": 94.5, "details": { "description": "Rapid burst of 45 high-token requests in 10s", "blocked_cost": 0.3800 } },
                    { "id": "atk_102", "agent_id": "ag_8801_cs", "agent_name": "Customer Support Agent", "timestamp": "2026-09-06T17:45:00Z", "attack_type": "Recursive Loop Attack", "severity": 78, "confidence": 89.0, "details": { "description": "Hallucinated tool calling loop detected", "blocked_cost": 0.2200 } },
                    { "id": "atk_103", "agent_id": "ag_8802_code", "agent_name": "Code Assistant Agent", "timestamp": "2026-09-06T16:20:00Z", "attack_type": "Model Escalation Exploit", "severity": 65, "confidence": 91.2, "details": { "description": "Attempted unpermitted switch to Pro model", "blocked_cost": 0.5000 } }
                ]
            elif name == "policy_actions":
                self.data_store[name] = [
                    { "id": "pa_501", "agent_id": "ag_8802_code", "timestamp": "2026-09-06T18:38:22Z", "action": "block", "reason": "Projected cost $1.0700 exceeds selected budget cap $1.0000", "risk_score": 82, "metadata": { "projected_cost": 1.07, "max_budget": 1.00 } },
                    { "id": "pa_502", "agent_id": "ag_8802_code", "timestamp": "2026-09-06T18:35:00Z", "action": "model_downgrade", "reason": "High token burn rate detected. Model downgraded from Gemini Pro to Flash", "risk_score": 65, "metadata": { "previous_model": "gemini-3.1-pro", "new_model": "gemini-2.5-flash" } },
                    { "id": "pa_503", "agent_id": "ag_8801_cs", "timestamp": "2026-09-06T18:32:45Z", "action": "throttle", "reason": "SerpApi search tool frequency exceeded 2 calls/min threshold", "risk_score": 45, "metadata": { "tool": "serpapi", "delay_ms": 2000 } },
                    { "id": "pa_504", "agent_id": "ag_8801_cs", "timestamp": "2026-09-06T18:30:12Z", "action": "allow", "reason": "Action authorized cleanly within budget bounds", "risk_score": 15, "metadata": { "cost": 0.0022 } },
                    { "id": "pa_505", "agent_id": "ag_8803_fin", "timestamp": "2026-09-06T18:25:00Z", "action": "warn", "reason": "Budget utilization reached 75% boundary", "risk_score": 55, "metadata": { "utilization_pct": 75 } }
                ]
            else:
                self.data_store[name] = []
        self._filter_id = None

    def select(self, *args, **kwargs):
        self._filter_id = None
        return self

    def insert(self, data, *args, **kwargs):
        if isinstance(data, list):
            self.data_store[self.name].extend(data)
        elif isinstance(data, dict):
            self.data_store[self.name].append(data)
        return self

    def update(self, *args, **kwargs):
        return self

    def delete(self, *args, **kwargs):
        return self

    def eq(self, field, value, *args, **kwargs):
        if field == "id":
            self._filter_id = value
        return self

    def order(self, *args, **kwargs):
        return self

    def limit(self, count: int, *args, **kwargs):
        return self

    def execute(self):
        class Response:
            def __init__(self, data):
                self.data = data
                self.count = len(data) if isinstance(data, list) else 1

        res_data = self.data_store.get(self.name, [])
        if self._filter_id:
            res_data = [item for item in res_data if item.get("id") == self._filter_id]
        return Response(res_data)


class MockClient:
    def __init__(self):
        self._stores = {}

    def table(self, name: str):
        return MockTable(name, self._stores)


supabase = None

if SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY:
    try:
        from supabase import Client, create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY)
    except Exception as exc:
        logger.warning("Failed to initialize Supabase client (%s). Using in-memory fallback.", exc)
        supabase = MockClient()
else:
    supabase = MockClient()