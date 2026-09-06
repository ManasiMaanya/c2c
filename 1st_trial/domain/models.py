from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import math

def check_finite_non_negative(val: float, name: str) -> float:
    if math.isnan(val) or math.isinf(val):
        raise ValueError(f"{name} must be a finite number, got {val}")
    if val < 0:
        raise ValueError(f"{name} must be non-negative, got {val}")
    return val

def check_score_range(val: float, name: str) -> float:
    check_finite_non_negative(val, name)
    if val > 100.0:
        raise ValueError(f"{name} must be <= 100.0, got {val}")
    return val

class Task(BaseModel):
    task_id: str = Field(default_factory=lambda: f"task_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}")
    description: str
    context_length: Optional[int] = 1000
    complexity_level: Optional[str] = "medium" # "simple", "medium", "complex"

    @field_validator("context_length")
    @classmethod
    def validate_context_length(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError("context_length must be non-negative")
        return v

    @field_validator("complexity_level")
    @classmethod
    def validate_complexity_level(cls, v: Optional[str]) -> str:
        if not v:
            return "medium"
        v_clean = v.lower().strip()
        if v_clean not in ["simple", "medium", "complex"]:
            return "medium"
        return v_clean

class UsageEstimate(BaseModel):
    expected_llm_calls: int
    expected_input_tokens: int
    expected_output_tokens: int
    expected_tool_calls: int
    expected_retries: int
    expected_steps: int
    provider_breakdown: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("expected_llm_calls", "expected_input_tokens", "expected_output_tokens", "expected_tool_calls", "expected_retries", "expected_steps")
    @classmethod
    def validate_non_negative_int(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Usage metric must be non-negative")
        return v

class CostEstimate(BaseModel):
    llm_cost: float
    tool_cost: float
    total_estimated_cost: float

    @field_validator("llm_cost", "tool_cost", "total_estimated_cost")
    @classmethod
    def validate_cost(cls, v: float) -> float:
        return check_finite_non_negative(v, "Cost metric")

class QualityEstimate(BaseModel):
    score: float # 0.0 to 100.0 (e.g., 72.0, 89.0, 96.0)
    explanation: str

    @field_validator("score")
    @classmethod
    def validate_score(cls, v: float) -> float:
        return check_score_range(v, "Quality score")

class RiskEstimate(BaseModel):
    score: float # 0.0 to 100.0 (e.g., 15.0, 21.0, 45.0)
    contributing_factors: List[str] = Field(default_factory=list)

    @field_validator("score")
    @classmethod
    def validate_score(cls, v: float) -> float:
        return check_score_range(v, "Risk score")

class PlanOption(BaseModel):
    plan_id: str
    plan_name: str # "Cost Optimized", "Balanced", "Quality Optimized"
    selected_model: str
    expected_llm_calls: int
    expected_input_tokens: int
    expected_output_tokens: int
    expected_tool_calls: int
    expected_retries: int
    expected_steps: int
    estimated_cost: float
    cost_lower_bound: float = 0.0
    cost_upper_bound: float = 0.0
    prediction_confidence: float = 85.0 # 0.0 to 100.0%
    estimated_quality_score: float
    estimated_risk_score: float
    is_policy_admissible: bool = True
    rejection_reasons: List[str] = Field(default_factory=list)
    usage_breakdown: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("expected_llm_calls", "expected_input_tokens", "expected_output_tokens", "expected_tool_calls", "expected_retries", "expected_steps")
    @classmethod
    def validate_non_negative_counts(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Plan metrics counts must be non-negative")
        return v

    @field_validator("estimated_cost", "cost_lower_bound", "cost_upper_bound")
    @classmethod
    def validate_cost(cls, v: float) -> float:
        return check_finite_non_negative(v, "Plan cost metric")

    @field_validator("estimated_quality_score", "estimated_risk_score", "prediction_confidence")
    @classmethod
    def validate_scores(cls, v: float) -> float:
        return check_score_range(v, "Plan score/confidence")

    @model_validator(mode="after")
    def validate_cost_invariants(self) -> "PlanOption":
        if self.usage_breakdown:
            llm_c = float(self.usage_breakdown.get("llm_cost", 0.0))
            tool_c = float(self.usage_breakdown.get("tool_cost", 0.0))
            breakdown_sum = round(llm_c + tool_c, 4)
            if abs(self.estimated_cost - breakdown_sum) > 0.0001:
                raise ValueError(
                    f"Cost conservation invariant violated: estimated_cost ({self.estimated_cost}) "
                    f"does not match sum of usage_breakdown ({breakdown_sum})"
                )
        if self.cost_lower_bound > 0 or self.cost_upper_bound > 0:
            if not (self.cost_lower_bound - 0.0001 <= self.estimated_cost <= self.cost_upper_bound + 0.0001):
                raise ValueError(
                    f"Cost uncertainty range invariant violated: lower_bound ({self.cost_lower_bound}) "
                    f"<= estimated_cost ({self.estimated_cost}) <= upper_bound ({self.cost_upper_bound})"
                )
        return self

class EnterprisePolicy(BaseModel):
    policy_id: str = "default_enterprise_policy"
    max_cost: float = 2.00 # Max allowed budget ($)
    max_steps: int = 20
    max_tool_calls: int = 10
    max_retries: int = 3
    max_tokens: int = 80000
    allowed_models: List[str] = Field(default_factory=lambda: ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-3.1-pro"])
    min_quality: float = 80.0
    max_risk: float = 30.0

    @field_validator("max_cost")
    @classmethod
    def validate_max_cost(cls, v: float) -> float:
        return check_finite_non_negative(v, "max_cost")

    @field_validator("min_quality", "max_risk")
    @classmethod
    def validate_policy_scores(cls, v: float) -> float:
        return check_score_range(v, "Policy threshold")

    @field_validator("max_steps", "max_tool_calls", "max_retries", "max_tokens")
    @classmethod
    def validate_policy_counts(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Policy count constraints must be non-negative")
        return v

class SimulationResult(BaseModel):
    task: Task
    policy: EnterprisePolicy
    plans: List[PlanOption]
    recommended_plan: Optional[PlanOption] = None
    selection_explanation: str

class CurrentExecutionState(BaseModel):
    execution_id: str
    task_id: str
    current_step: int
    actual_cost_so_far: float
    actual_tokens_so_far: int
    actual_tool_calls_so_far: int
    actual_retries_so_far: int
    current_model: str
    budget: float = 5.00
    expected_plan: Optional[PlanOption] = None

    @field_validator("actual_cost_so_far", "budget")
    @classmethod
    def validate_costs(cls, v: float) -> float:
        return check_finite_non_negative(v, "Execution cost/budget")

    @field_validator("current_step", "actual_tokens_so_far", "actual_tool_calls_so_far", "actual_retries_so_far")
    @classmethod
    def validate_counts(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Execution metric counts must be non-negative")
        return v

class FuturePathOption(BaseModel):
    strategy_name: str # "Continue", "Switch Model (Flash Lite)", "Reduce Tools Scope", "Stop Execution"
    projected_final_cost: float
    expected_remaining_cost: float
    expected_quality_score: float
    expected_risk_score: float
    is_policy_admissible: bool = True
    rejection_reasons: List[str] = Field(default_factory=list)

    @field_validator("projected_final_cost", "expected_remaining_cost")
    @classmethod
    def validate_future_costs(cls, v: float) -> float:
        return check_finite_non_negative(v, "Future path cost")

    @field_validator("expected_quality_score", "expected_risk_score")
    @classmethod
    def validate_future_scores(cls, v: float) -> float:
        return check_score_range(v, "Future path score")

class ResimulationResult(BaseModel):
    execution_id: str
    current_state: CurrentExecutionState
    trajectory_deviation_percent: float
    expected_cost_at_current_step: float = 0.0
    predicted_cost_range_at_current_step: Dict[str, float] = Field(default_factory=dict) # {"lower": x, "upper": y}
    trajectory_status: str = "WITHIN_EXPECTED_RANGE" # "WITHIN_EXPECTED_RANGE" or "OUTSIDE_EXPECTED_RANGE"
    prediction_confidence: float = 85.0
    future_paths: List[FuturePathOption]
    recommended_future_path: Optional[FuturePathOption] = None
    resimulation_explanation: str


