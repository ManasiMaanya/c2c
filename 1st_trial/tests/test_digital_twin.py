import unittest
from domain.models import (
    Task, EnterprisePolicy, PlanOption, CurrentExecutionState
)
from providers.pricing import ProviderPricingConfig
from providers.usage_event import UsageEvent
from engine.planner import PlanGenerator
from engine.policy_evaluator import PolicyEvaluator
from engine.plan_selector import PlanSelector
from engine.resimulator import ResimulationEngine
from engine.digital_twin import DigitalTwinFacade

class TestDigitalTwinSubsystem(unittest.TestCase):

    def setUp(self):
        self.sample_task = Task(
            task_id="task_test_101",
            description="Research 10 competitors and generate legal summary report",
            context_length=1500,
            complexity_level="medium"
        )
        self.sample_policy = EnterprisePolicy(
            max_cost=2.00,
            min_quality=80.0,
            max_risk=30.0,
            max_steps=20,
            max_tool_calls=10
        )

    # 1. Test 3 Baseline Plans Are Generated
    def test_three_baseline_plans_generated(self):
        plans = PlanGenerator.generate_baseline_plans(self.sample_task)
        self.assertEqual(len(plans), 3)

        plan_names = [p.plan_name for p in plans]
        self.assertIn("Cost Optimized Plan", plan_names)
        self.assertIn("Balanced Plan", plan_names)
        self.assertIn("Quality Optimized Plan", plan_names)

    # 2. Test Costs Are Calculated Correctly
    def test_costs_calculated_correctly(self):
        plans = PlanGenerator.generate_baseline_plans(self.sample_task)
        cost_plan = next(p for p in plans if p.plan_name == "Cost Optimized Plan")
        quality_plan = next(p for p in plans if p.plan_name == "Quality Optimized Plan")

        self.assertLess(cost_plan.estimated_cost, quality_plan.estimated_cost)
        self.assertGreater(cost_plan.estimated_cost, 0.0)

    # 3. Test Provider Pricing Calculations
    def test_provider_pricing_isolated_and_accurate(self):
        llm_cost = ProviderPricingConfig.calculate_llm_cost("gemini-2.5-flash", 1_000_000, 1_000_000)
        self.assertEqual(llm_cost, 0.375)

        serp_cost = ProviderPricingConfig.calculate_tool_cost("serpapi", "search", 5)
        self.assertEqual(serp_cost, 0.05)

        tts_cost = ProviderPricingConfig.calculate_tool_cost("elevenlabs", "tts", 2000)
        self.assertEqual(tts_cost, 0.06)

    # 4. Test Enterprise Constraints Reject Invalid Plans
    def test_enterprise_constraints_reject_invalid_plans(self):
        strict_policy = EnterprisePolicy(max_cost=1.00, min_quality=85.0, max_risk=25.0)
        plans = PlanGenerator.generate_baseline_plans(self.sample_task)
        evaluated = PolicyEvaluator.evaluate_plans(plans, strict_policy)

        cost_plan = next(p for p in evaluated if p.plan_name == "Cost Optimized Plan")
        quality_plan = next(p for p in evaluated if p.plan_name == "Quality Optimized Plan")

        self.assertFalse(cost_plan.is_policy_admissible)
        self.assertTrue(len(cost_plan.rejection_reasons) > 0)
        self.assertIn("Quality", cost_plan.rejection_reasons[0])

        self.assertFalse(quality_plan.is_policy_admissible)

    # 5. Test Valid Plan Can Be Selected
    def test_valid_plan_selected(self):
        sim_result = DigitalTwinFacade.simulate_task(self.sample_task, self.sample_policy)
        self.assertIsNotNone(sim_result.recommended_plan)
        self.assertTrue(sim_result.recommended_plan.is_policy_admissible)
        self.assertEqual(sim_result.recommended_plan.plan_name, "Balanced Plan")

    # 6. Test Plan Selection Is Deterministic
    def test_selection_is_deterministic(self):
        res1 = DigitalTwinFacade.simulate_task(self.sample_task, self.sample_policy)
        res2 = DigitalTwinFacade.simulate_task(self.sample_task, self.sample_policy)

        self.assertEqual(res1.recommended_plan.plan_id, res2.recommended_plan.plan_id)
        self.assertEqual(res1.recommended_plan.estimated_cost, res2.recommended_plan.estimated_cost)

    # 7. Test Resimulation Produces Multiple Candidate Future Paths
    def test_resimulation_produces_future_paths(self):
        plans = PlanGenerator.generate_baseline_plans(self.sample_task)
        balanced_plan = next(p for p in plans if p.plan_name == "Balanced Plan")

        state = CurrentExecutionState(
            execution_id="exec_9901",
            task_id=self.sample_task.task_id,
            current_step=4,
            actual_cost_so_far=0.45,
            actual_tokens_so_far=45000,
            actual_tool_calls_so_far=5,
            actual_retries_so_far=2,
            current_model="gemini-2.5-flash",
            budget=0.50,
            expected_plan=balanced_plan
        )

        resim = ResimulationEngine.resimulate(state, self.sample_policy)
        self.assertGreater(resim.trajectory_deviation_percent, 30.0)
        self.assertEqual(len(resim.future_paths), 4)

        strategy_names = [f.strategy_name for f in resim.future_paths]
        self.assertIn("Continue Current Route", strategy_names)
        self.assertIn("Switch Model to Flash Lite", strategy_names)
        self.assertIn("Reduce Tools Scope", strategy_names)
        self.assertIn("Stop Execution", strategy_names)

        self.assertIsNotNone(resim.recommended_future_path)

    # 8. Test UsageEvent Normalization
    def test_usage_event_normalization(self):
        llm_evt = UsageEvent.create_llm_event("exec_01", "gemini-2.5-flash", 10000, 2000)
        self.assertEqual(llm_evt.provider, "gemini")
        self.assertEqual(llm_evt.estimated_cost, 0.00135)

        tool_evt = UsageEvent.create_tool_event("exec_01", "serpapi", "search", 2)
        self.assertEqual(tool_evt.provider, "serpapi")
        self.assertEqual(tool_evt.estimated_cost, 0.02)

if __name__ == "__main__":
    unittest.main()
