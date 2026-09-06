from typing import Optional, List, Dict, Any, Tuple, Callable
from domain.models import (
    Task, PlanOption, EnterprisePolicy, SimulationResult,
    CurrentExecutionState, ResimulationResult, ProposedAction, FirewallDecision, ExecutionSession
)
from providers.usage_event import UsageEvent
from engine.planner import PlanGenerator
from engine.policy_evaluator import PolicyEvaluator
from engine.plan_selector import PlanSelector
from engine.resimulator import ResimulationEngine
from engine.ledger import EconomicLedger
from engine.firewall import RuntimeEconomicFirewall

class DigitalTwinFacade:
    """
    Main Facade for the Digital Twin Subsystem (Brain 1) & Runtime Economic Protection.
    Provides unified simulation, plan selection, resimulation, runtime firewall enforcement, and economic ledger tracking.
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

    # -------------------------------------------------------------------------
    # RUNTIME FIREWALL & ECONOMIC LEDGER CAPABILITIES
    # -------------------------------------------------------------------------
    @staticmethod
    def start_execution_session(
        task: Task,
        chosen_plan_name: str = "Balanced Plan",
        policy: Optional[EnterprisePolicy] = None
    ) -> ExecutionSession:
        policy = policy or EnterprisePolicy()
        selection = DigitalTwinFacade.select_plan(task, chosen_plan_name, policy)
        
        if not selection["selected_plan"] or not selection["is_admissible"]:
            raise ValueError(f"Cannot start execution session: No admissible plan found. ({selection['rejection_reasons'][0]})")

        plan = PlanOption(**selection["selected_plan"])
        session = ExecutionSession(task=task, selected_plan=plan, policy=policy)
        RuntimeEconomicFirewall().register_session(session)
        return session

    @staticmethod
    def authorize_action(execution_id: str, action: ProposedAction) -> FirewallDecision:
        decision, _ = RuntimeEconomicFirewall().evaluate_action(execution_id, action)
        return decision

    @staticmethod
    def execute_action_via_gateway(
        execution_id: str,
        action: ProposedAction,
        provider_func: Optional[Callable[[], Any]] = None,
        actual_cost_override: Optional[float] = None
    ) -> Tuple[FirewallDecision, Any]:
        return RuntimeEconomicFirewall().authorize_and_execute(
            execution_id, action, provider_func=provider_func, actual_cost_override=actual_cost_override
        )

    @staticmethod
    def record_usage_event(event: UsageEvent) -> Tuple[bool, str, float]:
        return EconomicLedger().record_event(event)

    @staticmethod
    def get_ledger_state(execution_id: str) -> Dict[str, Any]:
        firewall = RuntimeEconomicFirewall()
        session = firewall.get_session(execution_id)
        max_budget = session.selected_plan.estimated_cost if session else 0.0
        return firewall.ledger.get_summary(execution_id, max_budget=max_budget)
