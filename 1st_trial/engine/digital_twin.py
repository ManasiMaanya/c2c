from typing import Optional, List, Dict, Any
from domain.models import (
    Task, PlanOption, EnterprisePolicy, SimulationResult,
    CurrentExecutionState, ResimulationResult
)
from engine.planner import PlanGenerator
from engine.policy_evaluator import PolicyEvaluator
from engine.plan_selector import PlanSelector
from engine.resimulator import ResimulationEngine

class DigitalTwinFacade:
    """
    Main Facade for the Digital Twin Subsystem (Brain 1).
    Provides unified simulation, plan selection, and resimulation capabilities.
    NO real paid API calls are ever executed by this engine.
    """

    @staticmethod
    def simulate_task(
        task: Task,
        policy: Optional[EnterprisePolicy] = None
    ) -> SimulationResult:
        policy = policy or EnterprisePolicy()
        raw_plans = PlanGenerator.generate_baseline_plans(task)
        evaluated_plans = PolicyEvaluator.evaluate_plans(raw_plans, policy)
        recommended_plan, explanation = PlanSelector.select_best_plan(evaluated_plans)

        return SimulationResult(
            task=task,
            policy=policy,
            plans=evaluated_plans,
            recommended_plan=recommended_plan,
            selection_explanation=explanation
        )

    @staticmethod
    def select_plan(
        task: Task,
        chosen_plan_name: str,
        policy: Optional[EnterprisePolicy] = None
    ) -> Dict[str, Any]:
        sim_result = DigitalTwinFacade.simulate_task(task, policy)
        matched = next((p for p in sim_result.plans if p.plan_name.lower() == chosen_plan_name.lower()), sim_result.recommended_plan)

        return {
            "task_id": task.task_id,
            "selected_plan": matched.model_dump() if matched else None,
            "is_admissible": matched.is_policy_admissible if matched else False,
            "rejection_reasons": matched.rejection_reasons if matched else ["No feasible plan selected due to enterprise policy violations"],
            "execution_representation": {
                "model": matched.selected_model if matched else "none",
                "max_budget": sim_result.policy.max_cost,
                "expected_steps": matched.expected_steps if matched else 0,
                "expected_cost": matched.estimated_cost if matched else 0.0,
                "expected_quality": matched.estimated_quality_score if matched else 0.0,
                "expected_risk": matched.estimated_risk_score if matched else 0.0
            }
        }

    @staticmethod
    def resimulate_execution(
        current_state: CurrentExecutionState,
        policy: Optional[EnterprisePolicy] = None
    ) -> ResimulationResult:
        return ResimulationEngine.resimulate(current_state, policy)
