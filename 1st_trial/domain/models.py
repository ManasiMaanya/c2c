from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

class Task(BaseModel):
    task_id: str = Field(default_factory=lambda: f"task_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}")
    description: str
    context_length: Optional[int] = 1000
    complexity_level: Optional[str] = "medium" # "simple", "medium", "complex"

class UsageEstimate(BaseModel):
    expected_llm_calls: int
    expected_input_tokens: int
    expected_output_tokens: int
    expected_tool_calls: int
    expected_retries: int
    expected_steps: int
    provider_breakdown: Dict[str, Any] = Field(default_factory=dict)

class CostEstimate(BaseModel):
    llm_cost: float
    tool_cost: float
    total_estimated_cost: float

class QualityEstimate(BaseModel):
    score: float # 0.0 to 100.0 (e.g., 72.0, 89.0, 96.0)
    explanation: str

class RiskEstimate(BaseModel):
    score: float # 0.0 to 100.0 (e.g., 15.0, 21.0, 45.0)
    contributing_factors: List[str] = Field(default_factory=list)

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
    estimated_quality_score: float
    estimated_risk_score: float
    is_policy_admissible: bool = True
    rejection_reasons: List[str] = Field(default_factory=list)
    usage_breakdown: Dict[str, Any] = Field(default_factory=dict)

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

class FuturePathOption(BaseModel):
    strategy_name: str # "Continue", "Switch Model (Flash Lite)", "Reduce Tools Scope", "Stop Execution"
    projected_final_cost: float
    expected_remaining_cost: float
    expected_quality_score: float
    expected_risk_score: float
    is_policy_admissible: bool = True
    rejection_reasons: List[str] = Field(default_factory=list)

class ResimulationResult(BaseModel):
    execution_id: str
    current_state: CurrentExecutionState
    trajectory_deviation_percent: float
    future_paths: List[FuturePathOption]
    recommended_future_path: Optional[FuturePathOption] = None
    resimulation_explanation: str
