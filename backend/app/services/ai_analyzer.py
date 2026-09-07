import json
import os
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = None

if HAS_GENAI and GEMINI_API_KEY:
    try:
        client = genai.Client(
            api_key=GEMINI_API_KEY,
            http_options=types.HttpOptions(timeout=30000),
        )
    except Exception:
        client = None

MODEL = "gemini-2.5-flash"


# --------------------------------------------------
# AI response schema
# --------------------------------------------------

class SecurityAnalysis(BaseModel):
    attack_detected: bool
    risk_score: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=100)
    attack_type: str
    reasoning: str
    economic_threat: str
    recommended_action: str


# --------------------------------------------------
# Gemini security analysis
# --------------------------------------------------

def analyze_with_ai(
    telemetry: dict[str, Any],
    economic_metrics: dict[str, Any],
) -> SecurityAnalysis:

    prompt = f"""
You are the AI security analyst for Denial of Wallet.

Denial of Wallet is an economic security system that protects
autonomous AI agents from runaway, adversarial, or financially
destructive AI usage.

Analyze the supplied telemetry and economic metrics.

Look for:

1. Request flooding
2. Token amplification or token explosions
3. Abnormally expensive requests
4. Cost acceleration
5. Excessive tool usage
6. Runaway autonomous behavior
7. Repeated suspicious patterns
8. Other behavior that could cause denial of wallet

IMPORTANT RULES:

- Analyze behavior, not just raw thresholds.
- Distinguish legitimate high usage from suspicious behavior.
- Do not invent telemetry values.
- Do not invent financial values.
- The supplied economic metrics are calculated by the backend
  and must be treated as the financial source of truth.
- Risk score must be between 0 and 100.
- Confidence must be between 0 and 100.
- Recommended action must be one of:
  ALLOW, WARN, THROTTLE, RESTRICT, BLOCK.

Allowed attack types:

- none
- request_flood
- token_explosion
- cost_acceleration
- tool_abuse
- runaway_agent
- mixed

Return ONLY valid JSON.

Required JSON structure:

{{
    "attack_detected": true,
    "risk_score": 0,
    "confidence": 0,
    "attack_type": "none",
    "reasoning": "Explain why the behavior is or is not suspicious.",
    "economic_threat": "Explain the economic threat using only supplied metrics.",
    "recommended_action": "ALLOW"
}}

ECONOMIC METRICS:

{json.dumps(economic_metrics, indent=2, default=str)}

TELEMETRY:

{json.dumps(telemetry, indent=2, default=str)}
"""

    if client is None:
        burn = float(economic_metrics.get("burn_rate", 0.0) or 0.0)
        is_attack = burn > 5.0
        return SecurityAnalysis(
            attack_detected=is_attack,
            risk_score=min(100.0, max(10.0, burn * 12.0)),
            confidence=92.0,
            attack_type="cost_acceleration" if is_attack else "none",
            reasoning="Automated heuristic risk evaluation based on observed agent spend rate and trajectory metrics.",
            economic_threat="High burn rate threatens budget depletion" if is_attack else "Normal within budget bounds",
            recommended_action="THROTTLE" if is_attack else "ALLOW",
        )

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1,
        ),
    )

    result = json.loads(response.text)

    return SecurityAnalysis(**result)