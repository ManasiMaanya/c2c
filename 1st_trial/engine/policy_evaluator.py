from typing import List
from domain.models import PlanOption, EnterprisePolicy

class PolicyEvaluator:
    @staticmethod
    def evaluate_plans(plans: List[PlanOption], policy: EnterprisePolicy) -> List[PlanOption]:
        evaluated_plans = []

        for plan in plans:
            reasons = []

            if plan.estimated_cost > policy.max_cost:
                reasons.append(f"Estimated cost (${plan.estimated_cost:.2f}) exceeds policy maximum (${policy.max_cost:.2f})")

            if plan.estimated_quality_score < policy.min_quality:
                reasons.append(f"Quality score ({plan.estimated_quality_score:.1f}) is below minimum required ({policy.min_quality:.1f})")

            if plan.estimated_risk_score > policy.max_risk:
                reasons.append(f"Risk score ({plan.estimated_risk_score:.1f}) exceeds maximum risk ceiling ({policy.max_risk:.1f})")

            if plan.expected_steps > policy.max_steps:
                reasons.append(f"Expected steps ({plan.expected_steps}) exceeds step limit ({policy.max_steps})")

            if plan.expected_tool_calls > policy.max_tool_calls:
                reasons.append(f"Expected tool calls ({plan.expected_tool_calls}) exceeds tool call limit ({policy.max_tool_calls})")

            if plan.expected_retries > policy.max_retries:
                reasons.append(f"Expected retries ({plan.expected_retries}) exceeds retry threshold ({policy.max_retries})")

            total_tokens = plan.expected_input_tokens + plan.expected_output_tokens
            if total_tokens > policy.max_tokens:
                reasons.append(f"Total expected tokens ({total_tokens}) exceeds token ceiling ({policy.max_tokens})")

            if policy.allowed_models and len(policy.allowed_models) > 0 and plan.selected_model not in policy.allowed_models:
                reasons.append(f"Model '{plan.selected_model}' is not in enterprise allowed models list ({policy.allowed_models})")

            if reasons:
                plan.is_policy_admissible = False
                plan.rejection_reasons = reasons
            else:
                plan.is_policy_admissible = True
                plan.rejection_reasons = []

            evaluated_plans.append(plan)

        return evaluated_plans

