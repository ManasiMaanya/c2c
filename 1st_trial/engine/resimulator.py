from typing import List, Tuple, Optional
from domain.models import CurrentExecutionState, FuturePathOption, ResimulationResult, EnterprisePolicy
from providers.pricing import ProviderPricingConfig

class ResimulationEngine:
    @staticmethod
    def resimulate(
        state: CurrentExecutionState,
        policy: Optional[EnterprisePolicy] = None
    ) -> ResimulationResult:
        policy = policy or EnterprisePolicy()
        budget = state.budget or policy.max_cost

        expected_total = state.expected_plan.estimated_cost if state.expected_plan else 0.35
        expected_steps = state.expected_plan.expected_steps if state.expected_plan else 10
        
        progress_ratio = max(0.1, min(1.0, state.current_step / (expected_steps or 1)))
        expected_cost_so_far = progress_ratio * expected_total

        if expected_cost_so_far > 0:
            deviation_pct = round(((state.actual_cost_so_far - expected_cost_so_far) / expected_cost_so_far) * 100, 1)
        else:
            deviation_pct = 0.0

        remaining_steps = max(1, expected_steps - state.current_step)

        # 1. Continue Current Route
        cont_remaining_cost = round(remaining_steps * 0.04 * (1.0 + max(0.0, deviation_pct / 100.0)), 4)
        cont_final_cost = round(state.actual_cost_so_far + cont_remaining_cost, 4)
        
        path_continue = FuturePathOption(
            strategy_name="Continue Current Route",
            projected_final_cost=cont_final_cost,
            expected_remaining_cost=cont_remaining_cost,
            expected_quality_score=state.expected_plan.estimated_quality_score if state.expected_plan else 89.0,
            expected_risk_score=min(100.0, 21.0 + (deviation_pct * 0.4))
        )
        if cont_final_cost > budget or cont_final_cost > policy.max_cost:
            path_continue.is_policy_admissible = False
            path_continue.rejection_reasons.append(f"Projected final cost (${cont_final_cost:.2f}) breaches budget (${budget:.2f})")

        # 2. Switch Model (Flash Lite)
        switch_remaining_cost = round(remaining_steps * 0.008, 4)
        switch_final_cost = round(state.actual_cost_so_far + switch_remaining_cost, 4)
        
        path_switch = FuturePathOption(
            strategy_name="Switch Model to Flash Lite",
            projected_final_cost=switch_final_cost,
            expected_remaining_cost=switch_remaining_cost,
            expected_quality_score=84.0,
            expected_risk_score=18.0
        )
        if switch_final_cost > budget:
            path_switch.is_policy_admissible = False
            path_switch.rejection_reasons.append(f"Cost (${switch_final_cost:.2f}) exceeds budget")

        # 3. Reduce Tools Scope
        reduce_remaining_cost = round(remaining_steps * 0.005, 4)
        reduce_final_cost = round(state.actual_cost_so_far + reduce_remaining_cost, 4)

        path_reduce = FuturePathOption(
            strategy_name="Reduce Tools Scope",
            projected_final_cost=reduce_final_cost,
            expected_remaining_cost=reduce_remaining_cost,
            expected_quality_score=75.0,
            expected_risk_score=25.0
        )

        # 4. Stop Execution
        path_stop = FuturePathOption(
            strategy_name="Stop Execution",
            projected_final_cost=state.actual_cost_so_far,
            expected_remaining_cost=0.0,
            expected_quality_score=0.0,
            expected_risk_score=0.0
        )

        future_paths = [path_continue, path_switch, path_reduce, path_stop]

        admissible_futures = [p for p in future_paths if p.is_policy_admissible and p.expected_quality_score >= policy.min_quality]
        if admissible_futures:
            admissible_futures.sort(key=lambda x: x.expected_quality_score, reverse=True)
            recommended = admissible_futures[0]
            explanation = (
                f"Resimulation completed. Trajectory deviation is {deviation_pct}% above expected. "
                f"Recommended reroute: '{recommended.strategy_name}' (Projected cost: ${recommended.projected_final_cost:.2f}, "
                f"Quality: Q{int(recommended.expected_quality_score)})."
            )
        else:
            recommended = path_switch if path_switch.is_policy_admissible else path_stop
            explanation = (
                f"Trajectory deviation (+{deviation_pct}%) breached budget threshold. "
                f"Rerouting to '{recommended.strategy_name}' to contain further economic loss."
            )

        return ResimulationResult(
            execution_id=state.execution_id,
            current_state=state,
            trajectory_deviation_percent=deviation_pct,
            future_paths=future_paths,
            recommended_future_path=recommended,
            resimulation_explanation=explanation
        )
