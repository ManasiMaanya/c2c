from pydantic import BaseModel, Field


class AIAnalysis(BaseModel):
    anomaly_detected: bool

    attack_type: str

    confidence: float = Field(
        ge=0,
        le=1,
    )

    risk_score: float = Field(
        ge=0,
        le=100,
    )

    explanation: str

    evidence: list[str]

    recommended_action: str

    projected_loss_1h: float = Field(
        ge=0,
    )