from typing import List, Tuple, Optional
from domain.models import PlanOption

class PlanSelector:
    @staticmethod
    def select_best_plan(plans: List[PlanOption]) -> Tuple[Optional[PlanOption], str]:
        admissible = [p for p in plans if p.is_policy_admissible]

        if not admissible:
            reasons_summary = "; ".join(f"'{p.plan_name}': {', '.join(p.rejection_reasons)}" for p in plans if p.rejection_reasons)
            explanation = (
                f"NO_FEASIBLE_PLAN: All generated execution plans violated enterprise policy constraints. "
                f"No plan will be executed. Policy Rejections: [{reasons_summary}]."
            )
            return None, explanation

        admissible.sort(key=lambda p: (p.estimated_quality_score, -p.estimated_cost), reverse=True)
        winner = admissible[0]

        rejections = [f"{p.plan_name} REJECTED ({p.rejection_reasons[0]})" for p in plans if not p.is_policy_admissible]
        rejection_str = f" Disqualified plans: {', '.join(rejections)}." if rejections else ""

        explanation = (
            f"Plan '{winner.plan_name}' SELECTED. "
            f"It satisfies all enterprise constraints (Cost: ${winner.estimated_cost:.2f}, "
            f"Quality: Q{int(round(winner.estimated_quality_score))}, Risk: R{int(round(winner.estimated_risk_score))}) "
            f"and provides the optimal trade-off.{rejection_str}"
        )

        return winner, explanation

