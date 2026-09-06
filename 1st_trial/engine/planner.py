from typing import List, Dict, Any
from domain.models import Task, PlanOption
from providers.pricing import ProviderPricingConfig

class PlanGenerator:
    """
    Baseline Strategy Planner.
    Generates the 3 baseline execution plans for any given user task:
      1. Plan 1 — Cost Optimized (Cheap model, minimal search)
      2. Plan 2 — Balanced (Balanced model, moderate research)
      3. Plan 3 — Quality Optimized (Pro model, extensive research & tool calls)
    """

    @staticmethod
    def generate_baseline_plans(task: Task) -> List[PlanOption]:
        complexity = (task.complexity_level or "medium").lower().strip()
        mult = 1.0
        if complexity == "complex":
            mult = 1.8
        elif complexity == "simple":
            mult = 0.7

        # -------------------------------------------------------------
        # PLAN 1: COST OPTIMIZED PLAN
        # -------------------------------------------------------------
        cost_calls = max(3, int(6 * mult))
        cost_in_tokens = max(5000, int(15000 * mult))
        cost_out_tokens = max(1000, int(3000 * mult))
        cost_tools = max(1, int(2 * mult))
        cost_retries = 1
        cost_steps = cost_calls + cost_tools

        cost_llm = round(ProviderPricingConfig.calculate_llm_cost("gemini-2.5-flash-lite", cost_in_tokens, cost_out_tokens), 6)
        cost_tool = round(ProviderPricingConfig.calculate_tool_cost("serpapi", "search", cost_tools), 6)
        total_cost_1 = round(cost_llm + cost_tool, 4)

        plan_1 = PlanOption(
            plan_id=f"plan_cost_{task.task_id[:8]}",
            plan_name="Cost Optimized Plan",
            selected_model="gemini-2.5-flash-lite",
            expected_llm_calls=cost_calls,
            expected_input_tokens=cost_in_tokens,
            expected_output_tokens=cost_out_tokens,
            expected_tool_calls=cost_tools,
            expected_retries=cost_retries,
            expected_steps=cost_steps,
            estimated_cost=total_cost_1,
            estimated_quality_score=72.0,
            estimated_risk_score=15.0,
            usage_breakdown={"llm_cost": cost_llm, "tool_cost": cost_tool}
        )

        # -------------------------------------------------------------
        # PLAN 2: BALANCED PLAN
        # -------------------------------------------------------------
        bal_calls = max(6, int(12 * mult))
        bal_in_tokens = max(15000, int(40000 * mult))
        bal_out_tokens = max(3000, int(8000 * mult))
        bal_tools = max(3, int(6 * mult))
        bal_retries = 2
        bal_steps = bal_calls + bal_tools

        bal_llm = round(ProviderPricingConfig.calculate_llm_cost("gemini-2.5-flash", bal_in_tokens, bal_out_tokens), 6)
        bal_tool = round(ProviderPricingConfig.calculate_tool_cost("serpapi", "search", bal_tools), 6)
        total_cost_2 = round(bal_llm + bal_tool, 4)

        plan_2 = PlanOption(
            plan_id=f"plan_bal_{task.task_id[:8]}",
            plan_name="Balanced Plan",
            selected_model="gemini-2.5-flash",
            expected_llm_calls=bal_calls,
            expected_input_tokens=bal_in_tokens,
            expected_output_tokens=bal_out_tokens,
            expected_tool_calls=bal_tools,
            expected_retries=bal_retries,
            expected_steps=bal_steps,
            estimated_cost=total_cost_2,
            estimated_quality_score=89.0,
            estimated_risk_score=21.0,
            usage_breakdown={"llm_cost": bal_llm, "tool_cost": bal_tool}
        )

        # -------------------------------------------------------------
        # PLAN 3: QUALITY OPTIMIZED PLAN
        # -------------------------------------------------------------
        qual_calls = max(10, int(20 * mult))
        qual_in_tokens = max(40000, int(120000 * mult))
        qual_out_tokens = max(8000, int(25000 * mult))
        qual_tools = max(6, int(12 * mult))
        qual_retries = 3
        qual_steps = qual_calls + qual_tools

        qual_llm = round(ProviderPricingConfig.calculate_llm_cost("gemini-3.1-pro", qual_in_tokens, qual_out_tokens), 6)
        qual_tool = round(ProviderPricingConfig.calculate_tool_cost("serpapi", "search", qual_tools) + ProviderPricingConfig.calculate_tool_cost("elevenlabs", "tts", 1000), 6)
        total_cost_3 = round(qual_llm + qual_tool, 4)

        plan_3 = PlanOption(
            plan_id=f"plan_qual_{task.task_id[:8]}",
            plan_name="Quality Optimized Plan",
            selected_model="gemini-3.1-pro",
            expected_llm_calls=qual_calls,
            expected_input_tokens=qual_in_tokens,
            expected_output_tokens=qual_out_tokens,
            expected_tool_calls=qual_tools,
            expected_retries=qual_retries,
            expected_steps=qual_steps,
            estimated_cost=total_cost_3,
            estimated_quality_score=96.0,
            estimated_risk_score=45.0,
            usage_breakdown={"llm_cost": qual_llm, "tool_cost": qual_tool}
        )

        return [plan_1, plan_2, plan_3]

