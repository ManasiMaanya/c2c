import unittest
import threading
from domain.models import (
    Task, EnterprisePolicy, PlanOption, CurrentExecutionState, ProposedAction, FirewallDecision, ExecutionSession
)
from providers.pricing import ProviderPricingConfig
from providers.usage_event import UsageEvent
from engine.planner import PlanGenerator
from engine.policy_evaluator import PolicyEvaluator
from engine.plan_selector import PlanSelector
from engine.resimulator import ResimulationEngine
from engine.ledger import EconomicLedger
from engine.firewall import RuntimeEconomicFirewall
from engine.digital_twin import DigitalTwinFacade

class TestDigitalTwinSubsystem(unittest.TestCase):

    def setUp(self):
        EconomicLedger().clear()
        RuntimeEconomicFirewall()._sessions.clear()
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

    # 9. Adversarial Test: Negative Token Counts / Units Raise ValueError
    def test_adversarial_negative_token_counts_raises_error(self):
        with self.assertRaises(ValueError):
            ProviderPricingConfig.calculate_llm_cost("gemini-2.5-flash", -500, 1000)
        with self.assertRaises(ValueError):
            ProviderPricingConfig.calculate_tool_cost("serpapi", "search", -1)

    # 10. Adversarial Test: NaN and Inf Cost/Score Inputs Raise ValueError
    def test_adversarial_nan_and_inf_inputs_rejected(self):
        with self.assertRaises(ValueError):
            EnterprisePolicy(max_cost=float("nan"))
        with self.assertRaises(ValueError):
            EnterprisePolicy(max_cost=float("inf"))

    # 11. Invariant Test: Cost Conservation Invariant Strictly Enforced
    def test_cost_conservation_invariant_strictly_enforced(self):
        plans = PlanGenerator.generate_baseline_plans(self.sample_task)
        for p in plans:
            breakdown_sum = round(p.usage_breakdown["llm_cost"] + p.usage_breakdown["tool_cost"], 4)
            self.assertAlmostEqual(p.estimated_cost, breakdown_sum, places=4)

        # Mutating breakdown to mismatch cost must raise ValueError
        with self.assertRaises(ValueError):
            PlanOption(
                plan_id="tampered_plan",
                plan_name="Tampered Plan",
                selected_model="gemini-2.5-flash",
                expected_llm_calls=5,
                expected_input_tokens=1000,
                expected_output_tokens=500,
                expected_tool_calls=2,
                expected_retries=1,
                expected_steps=7,
                estimated_cost=10.00, # Cost mismatch!
                estimated_quality_score=80.0,
                estimated_risk_score=20.0,
                usage_breakdown={"llm_cost": 1.00, "tool_cost": 1.00}
            )

    # 12. Invariant Test: Ultra Strict Policy Rejects ALL Plans and Returns None Recommended
    def test_ultra_strict_policy_rejects_all_plans(self):
        ultra_strict_policy = EnterprisePolicy(max_cost=0.0001, min_quality=99.0)
        sim_result = DigitalTwinFacade.simulate_task(self.sample_task, ultra_strict_policy)

        self.assertIsNone(sim_result.recommended_plan)
        self.assertTrue(sim_result.selection_explanation.startswith("NO_FEASIBLE_PLAN"))
        for p in sim_result.plans:
            self.assertFalse(p.is_policy_admissible)
            self.assertGreater(len(p.rejection_reasons), 0)

    # 13. Boundary Test: Policy Boundary Equality Is Admissible
    def test_policy_boundary_equality_is_admissible(self):
        exact_policy = EnterprisePolicy(max_cost=0.50, min_quality=80.0)
        test_plan = PlanOption(
            plan_id="p_exact",
            plan_name="Exact Plan",
            selected_model="gemini-2.5-flash",
            expected_llm_calls=5,
            expected_input_tokens=1000,
            expected_output_tokens=500,
            expected_tool_calls=2,
            expected_retries=1,
            expected_steps=7,
            estimated_cost=0.50, # Exactly equals max_cost
            estimated_quality_score=80.0, # Exactly equals min_quality
            estimated_risk_score=20.0,
            usage_breakdown={"llm_cost": 0.40, "tool_cost": 0.10}
        )
        evaluated = PolicyEvaluator.evaluate_plans([test_plan], exact_policy)
        self.assertTrue(evaluated[0].is_policy_admissible)

    # 14. Edge Case Test: Resimulation Zero Remaining Steps & Overshoot
    def test_resimulation_zero_remaining_steps_and_overshoot(self):
        plans = PlanGenerator.generate_baseline_plans(self.sample_task)
        balanced_plan = next(p for p in plans if p.plan_name == "Balanced Plan")

        # Current step exceeds expected steps (overshoot)
        state_overshoot = CurrentExecutionState(
            execution_id="exec_overshoot",
            task_id=self.sample_task.task_id,
            current_step=balanced_plan.expected_steps + 5,
            actual_cost_so_far=0.50,
            actual_tokens_so_far=50000,
            actual_tool_calls_so_far=6,
            actual_retries_so_far=2,
            current_model="gemini-2.5-flash",
            budget=2.00,
            expected_plan=balanced_plan
        )
        resim = ResimulationEngine.resimulate(state_overshoot, self.sample_policy)
        cont_path = next(p for p in resim.future_paths if p.strategy_name == "Continue Current Route")
        self.assertEqual(cont_path.expected_remaining_cost, 0.0)
        self.assertEqual(cont_path.projected_final_cost, 0.50)

    # 15. Fallback Test: Unknown Provider and Model Handling
    def test_unknown_provider_and_model_fallback(self):
        llm_cost = ProviderPricingConfig.calculate_llm_cost("unknown-future-model-x", 100000, 50000)
        self.assertGreater(llm_cost, 0.0) # Uses default flash fallback pricing

        tool_cost = ProviderPricingConfig.calculate_tool_cost("custom_tool", "query", 10)
        self.assertEqual(tool_cost, 0.01)

    # -------------------------------------------------------------------------
    # RUNTIME ECONOMIC FIREWALL & LEDGER SECURITY TESTS (Scenarios 1 - 20)
    # -------------------------------------------------------------------------
    def _create_test_session(self, max_cost=1.00, plan_model="gemini-2.5-flash", max_tools=5, max_retries=2, max_tokens=50000, max_steps=10):
        t = Task(description="Firewall test task", complexity_level="medium")
        init_policy = EnterprisePolicy(max_cost=max(max_cost, 10.0), max_steps=100, max_tool_calls=100, max_tokens=500000, min_quality=50.0)
        session = DigitalTwinFacade.start_execution_session(t, "Balanced Plan", init_policy)
        
        # Apply exact test limits to session policy and plan
        session.policy.max_cost = max_cost
        session.policy.max_tool_calls = max_tools
        session.policy.max_retries = max_retries
        session.policy.max_tokens = max_tokens
        session.policy.max_steps = max_steps
        session.policy.allowed_models = [plan_model]

        session.selected_plan.estimated_cost = max_cost
        session.selected_plan.expected_tool_calls = max_tools
        session.selected_plan.expected_retries = max_retries
        session.selected_plan.expected_steps = max_steps
        session.selected_plan.expected_input_tokens = max_tokens // 2
        session.selected_plan.expected_output_tokens = max_tokens // 2
        session.selected_plan.selected_model = plan_model
        return session

    # Test 1: Basic Allow
    def test_firewall_basic_allow(self):
        session = self._create_test_session(max_cost=1.00)
        # Record $0.20 prior spend
        EconomicLedger().record_event(UsageEvent.create_tool_event(session.execution_id, "serpapi", "search", 20, actual_cost=0.20))
        
        act = ProposedAction(execution_id=session.execution_id, action_type="tool_call", provider="serpapi", units=10) # $0.10
        dec = DigitalTwinFacade.authorize_action(session.execution_id, act)
        self.assertEqual(dec.decision, "ALLOW")

    # Test 2: Budget Boundary Allow
    def test_firewall_budget_boundary_allow(self):
        session = self._create_test_session(max_cost=1.00)
        # Record $0.90 prior spend
        EconomicLedger().record_event(UsageEvent.create_tool_event(session.execution_id, "serpapi", "search", 90, actual_cost=0.90))
        
        act = ProposedAction(execution_id=session.execution_id, action_type="tool_call", provider="serpapi", units=10) # $0.10 -> total exactly $1.00
        dec = DigitalTwinFacade.authorize_action(session.execution_id, act)
        self.assertEqual(dec.decision, "ALLOW")

    # Test 3: Budget Exceeded Block
    def test_firewall_budget_exceeded_block(self):
        session = self._create_test_session(max_cost=1.00)
        EconomicLedger().record_event(UsageEvent.create_tool_event(session.execution_id, "serpapi", "search", 91, actual_cost=0.91))
        
        act = ProposedAction(execution_id=session.execution_id, action_type="tool_call", provider="serpapi", units=10) # $0.10 -> total $1.01 > $1.00
        dec = DigitalTwinFacade.authorize_action(session.execution_id, act)
        self.assertEqual(dec.decision, "BLOCK")
        self.assertIn("exceeds selected plan budget", dec.reasons[0])

    # Test 4: Token Limit Exceeded Block
    def test_firewall_token_limit_exceeded_block(self):
        session = self._create_test_session(max_tokens=50000)
        # Prior tokens = 48,000
        EconomicLedger().record_event(UsageEvent.create_llm_event(session.execution_id, "gemini-2.5-flash", 40000, 8000, actual_cost=0.01))
        
        act = ProposedAction(execution_id=session.execution_id, action_type="llm_call", provider="gemini", model="gemini-2.5-flash", input_tokens=3000, output_tokens=1000) # 4,000 tokens -> 52,000 > 50,000
        dec = DigitalTwinFacade.authorize_action(session.execution_id, act)
        self.assertEqual(dec.decision, "BLOCK")
        self.assertIn("exceed plan token ceiling", dec.reasons[0])

    # Test 5: Tool Limit Exceeded Block
    def test_firewall_tool_limit_exceeded_block(self):
        session = self._create_test_session(max_tools=5)
        for i in range(5):
            EconomicLedger().record_event(UsageEvent.create_tool_event(session.execution_id, "serpapi", "search", 1, actual_cost=0.01))
        
        act = ProposedAction(execution_id=session.execution_id, action_type="tool_call", provider="serpapi", units=1) # 6th tool call
        dec = DigitalTwinFacade.authorize_action(session.execution_id, act)
        self.assertEqual(dec.decision, "BLOCK")
        self.assertIn("exceed plan limit", dec.reasons[0])

    # Test 6: Retry Limit Exceeded Block
    def test_firewall_retry_limit_exceeded_block(self):
        session = self._create_test_session(max_retries=2)
        evt1 = UsageEvent(execution_id=session.execution_id, provider="gemini", operation="retry", actual_cost=0.01)
        evt2 = UsageEvent(execution_id=session.execution_id, provider="gemini", operation="retry", actual_cost=0.01)
        EconomicLedger().record_event(evt1)
        EconomicLedger().record_event(evt2)
        
        act = ProposedAction(execution_id=session.execution_id, action_type="retry", provider="gemini", units=1)
        dec = DigitalTwinFacade.authorize_action(session.execution_id, act)
        self.assertEqual(dec.decision, "BLOCK")
        self.assertIn("exceed plan limit", dec.reasons[0])

    # Test 7: Step Limit Exceeded Block
    def test_firewall_step_limit_exceeded_block(self):
        session = self._create_test_session(max_steps=5)
        for i in range(5):
            EconomicLedger().record_event(UsageEvent.create_tool_event(session.execution_id, "serpapi", "search", 1, actual_cost=0.01))
        
        act = ProposedAction(execution_id=session.execution_id, action_type="step", provider="gemini", units=1)
        dec = DigitalTwinFacade.authorize_action(session.execution_id, act)
        self.assertEqual(dec.decision, "BLOCK")
        self.assertIn("exceed plan step ceiling", dec.reasons[0])

    # Test 8: Unauthorized Model Block
    def test_firewall_unauthorized_model_block(self):
        session = self._create_test_session(plan_model="gemini-2.5-flash")
        session.policy.allowed_models = ["gemini-2.5-flash"] # Only Flash allowed
        
        act = ProposedAction(execution_id=session.execution_id, action_type="llm_call", provider="gemini", model="gemini-3.1-pro", input_tokens=1000, output_tokens=500)
        dec, result = DigitalTwinFacade.execute_action_via_gateway(session.execution_id, act)
        
        self.assertEqual(dec.decision, "BLOCK")
        self.assertIsNone(result) # Provider function NEVER executed!
        self.assertIn("not permitted by selected economic plan", dec.reasons[0])

    # Test 9: Unknown Provider or Model Block (Fail Closed)
    def test_firewall_unknown_provider_or_model_block(self):
        session = self._create_test_session()
        act_unknown = ProposedAction(execution_id=session.execution_id, action_type="tool_call", provider="unrecognized_hacked_provider", units=1)
        dec = DigitalTwinFacade.authorize_action(session.execution_id, act_unknown)
        self.assertEqual(dec.decision, "BLOCK")
        self.assertIn("Unknown tool provider", dec.reasons[0])

    # Test 10: Ledger Cost Accumulation
    def test_ledger_cost_accumulation(self):
        exec_id = "exec_acc_100"
        ledger = EconomicLedger()
        ledger.record_event(UsageEvent.create_tool_event(exec_id, "serpapi", "search", 1, actual_cost=0.08))
        ledger.record_event(UsageEvent.create_tool_event(exec_id, "serpapi", "search", 1, actual_cost=0.02))
        ledger.record_event(UsageEvent.create_tool_event(exec_id, "serpapi", "search", 1, actual_cost=0.06))
        ledger.record_event(UsageEvent.create_tool_event(exec_id, "serpapi", "search", 1, actual_cost=0.11))
        
        self.assertEqual(ledger.get_actual_cost(exec_id), 0.27)

    # Test 11: Duplicate Event Idempotency
    def test_ledger_duplicate_event_idempotency(self):
        exec_id = "exec_idemp_101"
        ledger = EconomicLedger()
        evt = UsageEvent.create_tool_event(exec_id, "serpapi", "search", 1, actual_cost=0.15, event_id="evt_fixed_001")
        
        success1, msg1, cost1 = ledger.record_event(evt)
        success2, msg2, cost2 = ledger.record_event(evt) # Duplicate ingestion!
        
        self.assertTrue(success1)
        self.assertTrue(success2)
        self.assertIn("Duplicate", msg2)
        self.assertEqual(cost1, 0.15)
        self.assertEqual(cost2, 0.15) # Cost counted ONCE!

    # Test 12: Negative Cost Rejection
    def test_ledger_negative_cost_rejection(self):
        with self.assertRaises(ValueError):
            UsageEvent(execution_id="exec_neg", provider="serpapi", operation="search", actual_cost=-0.05)

    # Test 13: NaN and Infinity Rejection
    def test_ledger_nan_inf_rejection(self):
        with self.assertRaises(ValueError):
            UsageEvent(execution_id="exec_nan", provider="serpapi", operation="search", actual_cost=float("nan"))

    # Test 14: Blocked Action Does Not Create Spend
    def test_blocked_action_does_not_create_spend(self):
        session = self._create_test_session(max_cost=0.50)
        # $0.45 spent
        EconomicLedger().record_event(UsageEvent.create_tool_event(session.execution_id, "serpapi", "search", 45, actual_cost=0.45))
        
        provider_called = []
        def dummy_provider():
            provider_called.append(True)
            return "executed"

        act = ProposedAction(execution_id=session.execution_id, action_type="tool_call", provider="serpapi", units=20) # $0.20 -> $0.65 > $0.50
        dec, res = DigitalTwinFacade.execute_action_via_gateway(session.execution_id, act, provider_func=dummy_provider)
        
        self.assertEqual(dec.decision, "BLOCK")
        self.assertEqual(len(provider_called), 0) # Provider NEVER called!
        self.assertEqual(EconomicLedger().get_actual_cost(session.execution_id), 0.45) # Spend unchanged!

    # Test 15: Actual Cost Authoritative Over Estimate
    def test_actual_cost_authoritative_over_estimate(self):
        session = self._create_test_session(max_cost=1.00)
        # Estimated was $0.30, but actual events sum to $0.34
        EconomicLedger().record_event(UsageEvent.create_tool_event(session.execution_id, "serpapi", "search", 1, actual_cost=0.34))
        
        summary = DigitalTwinFacade.get_ledger_state(session.execution_id)
        self.assertEqual(summary["actual_cost"], 0.34)
        self.assertNotEqual(summary["actual_cost"], session.selected_plan.estimated_cost)

    # Test 16: Concurrent Authorization Safety
    def test_concurrent_authorization_safety(self):
        session = self._create_test_session(max_cost=0.50)
        # $0.40 spent. Remaining = $0.10.
        EconomicLedger().record_event(UsageEvent.create_tool_event(session.execution_id, "serpapi", "search", 40, actual_cost=0.40))

        results = []
        def attempt_action():
            act = ProposedAction(execution_id=session.execution_id, action_type="tool_call", provider="serpapi", units=8) # $0.08
            dec = DigitalTwinFacade.authorize_action(session.execution_id, act)
            results.append(dec.decision)

        threads = [threading.Thread(target=attempt_action), threading.Thread(target=attempt_action)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # One thread MUST be ALLOWED, the second thread MUST be BLOCKED (since combined $0.16 > $0.10)
        self.assertEqual(results.count("ALLOW"), 1)
        self.assertEqual(results.count("BLOCK"), 1)

    # Test 17: Failed Provider Call No Spend Recorded
    def test_failed_provider_call_no_spend_recorded(self):
        session = self._create_test_session(max_cost=1.00)
        def failing_provider():
            raise RuntimeError("API Connection Error")

        act = ProposedAction(execution_id=session.execution_id, action_type="tool_call", provider="serpapi", units=1)
        dec, res = DigitalTwinFacade.execute_action_via_gateway(session.execution_id, act, provider_func=failing_provider)
        
        self.assertEqual(dec.decision, "ERROR")
        self.assertIn("Provider execution failed", dec.reasons[0])
        self.assertEqual(EconomicLedger().get_actual_cost(session.execution_id), 0.0) # Cost reservation released!

    # Test 18: Accounting Failure Enters Fail-Safe State
    def test_accounting_failure_enters_failsafe_state(self):
        session = self._create_test_session(max_cost=1.00)
        act = ProposedAction(execution_id=session.execution_id, action_type="tool_call", provider="serpapi", units=1)
        
        # Simulate accounting storage failure after provider call
        dec, res = RuntimeEconomicFirewall().authorize_and_execute(
            session.execution_id, act, simulate_accounting_failure=True
        )
        self.assertEqual(dec.decision, "ERROR")
        self.assertIn("Accounting failure", dec.reasons[0])
        self.assertEqual(session.status, "ACCOUNTING_ERROR")
        
# Record $0.90 prior spend
        EconomicLedger().record_event(UsageEvent.create_tool_event(session.execution_id, "serpapi", "search", 90, actual_cost=0.90))
        
        act = ProposedAction(execution_id=session.execution_id, action_type="tool_call", provider="serpapi", units=10) # $0.10 -> total exactly $1.00
        dec = DigitalTwinFacade.authorize_action(session.execution_id, act)
        self.assertEqual(dec.decision, "ALLOW")

    # Test 3: Budget Exceeded Block
    def test_firewall_budget_exceeded_block(self):
        session = self._create_test_session(max_cost=1.00)
        EconomicLedger().record_event(UsageEvent.create_tool_event(session.execution_id, "serpapi", "search", 91, actual_cost=0.91))
        
        act = ProposedAction(execution_id=session.execution_id, action_type="tool_call", provider="serpapi", units=10) # $0.10 -> total $1.01 > $1.00
        dec = DigitalTwinFacade.authorize_action(session.execution_id, act)
        self.assertEqual(dec.decision, "BLOCK")
        self.assertIn("exceeds selected plan budget", dec.reasons[0])

    # Test 4: Token Limit Exceeded Block
    def test_firewall_token_limit_exceeded_block(self):
        session = self._create_test_session(max_tokens=50000)
        # Prior tokens = 48,000
        EconomicLedger().record_event(UsageEvent.create_llm_event(session.execution_id, "gemini-2.5-flash", 40000, 8000, actual_cost=0.01))
        
        act = ProposedAction(execution_id=session.execution_id, action_type="llm_call", provider="gemini", model="gemini-2.5-flash", input_tokens=3000, output_tokens=1000) # 4,000 tokens -> 52,000 > 50,000
        dec = DigitalTwinFacade.authorize_action(session.execution_id, act)
        self.assertEqual(dec.decision, "BLOCK")
        self.assertIn("exceed plan token ceiling", dec.reasons[0])

    # Test 5: Tool Limit Exceeded Block
    def test_firewall_tool_limit_exceeded_block(self):
        session = self._create_test_session(max_tools=5)
        for i in range(5):
            EconomicLedger().record_event(UsageEvent.create_tool_event(session.execution_id, "serpapi", "search", 1, actual_cost=0.01))
        
        act = ProposedAction(execution_id=session.execution_id, action_type="tool_call", provider="serpapi", units=1) # 6th tool call
        dec = DigitalTwinFacade.authorize_action(session.execution_id, act)
        self.assertEqual(dec.decision, "BLOCK")
        self.assertIn("exceed plan limit", dec.reasons[0])

    # Test 6: Retry Limit Exceeded Block
    def test_firewall_retry_limit_exceeded_block(self):
        session = self._create_test_session(max_retries=2)
        evt1 = UsageEvent(execution_id=session.execution_id, provider="gemini", operation="retry", actual_cost=0.01)
        evt2 = UsageEvent(execution_id=session.execution_id, provider="gemini", operation="retry", actual_cost=0.01)
        EconomicLedger().record_event(evt1)
        EconomicLedger().record_event(evt2)
        
        act = ProposedAction(execution_id=session.execution_id, action_type="retry", provider="gemini", units=1)
        dec = DigitalTwinFacade.authorize_action(session.execution_id, act)
        self.assertEqual(dec.decision, "BLOCK")
        self.assertIn("exceed plan limit", dec.reasons[0])

    # Test 7: Step Limit Exceeded Block
    def test_firewall_step_limit_exceeded_block(self):
        session = self._create_test_session(max_steps=5)
        for i in range(5):
            EconomicLedger().record_event(UsageEvent.create_tool_event(session.execution_id, "serpapi", "search", 1, actual_cost=0.01))
        
        act = ProposedAction(execution_id=session.execution_id, action_type="step", provider="gemini", units=1)
        dec = DigitalTwinFacade.authorize_action(session.execution_id, act)
        self.assertEqual(dec.decision, "BLOCK")
        self.assertIn("exceed plan step ceiling", dec.reasons[0])

    # Test 8: Unauthorized Model Block
    def test_firewall_unauthorized_model_block(self):
        session = self._create_test_session(plan_model="gemini-2.5-flash")
        session.policy.allowed_models = ["gemini-2.5-flash"] # Only Flash allowed
        
        act = ProposedAction(execution_id=session.execution_id, action_type="llm_call", provider="gemini", model="gemini-3.1-pro", input_tokens=1000, output_tokens=500)
        dec, result = DigitalTwinFacade.execute_action_via_gateway(session.execution_id, act)
        
        self.assertEqual(dec.decision, "BLOCK")
        self.assertIsNone(result) # Provider function NEVER executed!
        self.assertIn("not permitted by selected economic plan", dec.reasons[0])

    # Test 9: Unknown Provider or Model Block (Fail Closed)
    def test_firewall_unknown_provider_or_model_block(self):
        session = self._create_test_session()
        act_unknown = ProposedAction(execution_id=session.execution_id, action_type="tool_call", provider="unrecognized_hacked_provider", units=1)
        dec = DigitalTwinFacade.authorize_action(session.execution_id, act_unknown)
        self.assertEqual(dec.decision, "BLOCK")
        self.assertIn("Unknown tool provider", dec.reasons[0])

    # Test 10: Ledger Cost Accumulation
    def test_ledger_cost_accumulation(self):
        exec_id = "exec_acc_100"
        ledger = EconomicLedger()
        ledger.record_event(UsageEvent.create_tool_event(exec_id, "serpapi", "search", 1, actual_cost=0.08))
        ledger.record_event(UsageEvent.create_tool_event(exec_id, "serpapi", "search", 1, actual_cost=0.02))
        ledger.record_event(UsageEvent.create_tool_event(exec_id, "serpapi", "search", 1, actual_cost=0.06))
        ledger.record_event(UsageEvent.create_tool_event(exec_id, "serpapi", "search", 1, actual_cost=0.11))
        
        self.assertEqual(ledger.get_actual_cost(exec_id), 0.27)

    # Test 11: Duplicate Event Idempotency
    def test_ledger_duplicate_event_idempotency(self):
        exec_id = "exec_idemp_101"
        ledger = EconomicLedger()
        evt = UsageEvent.create_tool_event(exec_id, "serpapi", "search", 1, actual_cost=0.15, event_id="evt_fixed_001")
        
        success1, msg1, cost1 = ledger.record_event(evt)
        success2, msg2, cost2 = ledger.record_event(evt) # Duplicate ingestion!
        
        self.assertTrue(success1)
        self.assertTrue(success2)
        self.assertIn("Duplicate", msg2)
        self.assertEqual(cost1, 0.15)
        self.assertEqual(cost2, 0.15) # Cost counted ONCE!

    # Test 12: Negative Cost Rejection
    def test_ledger_negative_cost_rejection(self):
        with self.assertRaises(ValueError):
            UsageEvent(execution_id="exec_neg", provider="serpapi", operation="search", actual_cost=-0.05)

    # Test 13: NaN and Infinity Rejection
    def test_ledger_nan_inf_rejection(self):
        with self.assertRaises(ValueError):
            UsageEvent(execution_id="exec_nan", provider="serpapi", operation="search", actual_cost=float("nan"))

    # Test 14: Blocked Action Does Not Create Spend
    def test_blocked_action_does_not_create_spend(self):
        session = self._create_test_session(max_cost=0.50)
        # $0.45 spent
        EconomicLedger().record_event(UsageEvent.create_tool_event(session.execution_id, "serpapi", "search", 45, actual_cost=0.45))
        
        provider_called = []
        def dummy_provider():
            provider_called.append(True)
            return "executed"

        act = ProposedAction(execution_id=session.execution_id, action_type="tool_call", provider="serpapi", units=20) # $0.20 -> $0.65 > $0.50
        dec, res = DigitalTwinFacade.execute_action_via_gateway(session.execution_id, act, provider_func=dummy_provider)
        
        self.assertEqual(dec.decision, "BLOCK")
        self.assertEqual(len(provider_called), 0) # Provider NEVER called!
        self.assertEqual(EconomicLedger().get_actual_cost(session.execution_id), 0.45) # Spend unchanged!

    # Test 15: Actual Cost Authoritative Over Estimate
    def test_actual_cost_authoritative_over_estimate(self):
        session = self._create_test_session(max_cost=1.00)
        # Estimated was $0.30, but actual events sum to $0.34
        EconomicLedger().record_event(UsageEvent.create_tool_event(session.execution_id, "serpapi", "search", 1, actual_cost=0.34))
        
        summary = DigitalTwinFacade.get_ledger_state(session.execution_id)
        self.assertEqual(summary["actual_cost"], 0.34)
        self.assertNotEqual(summary["actual_cost"], session.selected_plan.estimated_cost)

    # Test 16: Concurrent Authorization Safety
    def test_concurrent_authorization_safety(self):
        session = self._create_test_session(max_cost=0.50)
        # $0.40 spent. Remaining = $0.10.
        EconomicLedger().record_event(UsageEvent.create_tool_event(session.execution_id, "serpapi", "search", 40, actual_cost=0.40))

        results = []
        def attempt_action():
            act = ProposedAction(execution_id=session.execution_id, action_type="tool_call", provider="serpapi", units=8) # $0.08
            dec = DigitalTwinFacade.authorize_action(session.execution_id, act)
            results.append(dec.decision)

        threads = [threading.Thread(target=attempt_action), threading.Thread(target=attempt_action)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # One thread MUST be ALLOWED, the second thread MUST be BLOCKED (since combined $0.16 > $0.10)
        self.assertEqual(results.count("ALLOW"), 1)
        self.assertEqual(results.count("BLOCK"), 1)

    # Test 17: Failed Provider Call No Spend Recorded
    def test_failed_provider_call_no_spend_recorded(self):
        session = self._create_test_session(max_cost=1.00)
        def failing_provider():
            raise RuntimeError("API Connection Error")

        act = ProposedAction(execution_id=session.execution_id, action_type="tool_call", provider="serpapi", units=1)
        dec, res = DigitalTwinFacade.execute_action_via_gateway(session.execution_id, act, provider_func=failing_provider)
        
        self.assertEqual(dec.decision, "ERROR")
        self.assertIn("Provider execution failed", dec.reasons[0])
        self.assertEqual(EconomicLedger().get_actual_cost(session.execution_id), 0.0) # Cost reservation released!

    # Test 18: Accounting Failure Enters Fail-Safe State
    def test_accounting_failure_enters_failsafe_state(self):
        session = self._create_test_session(max_cost=1.00)
        act = ProposedAction(execution_id=session.execution_id, action_type="tool_call", provider="serpapi", units=1)
        
        # Simulate accounting storage failure after provider call
        dec, res = RuntimeEconomicFirewall().authorize_and_execute(
            session.execution_id, act, simulate_accounting_failure=True
        )
        self.assertEqual(dec.decision, "ERROR")
        self.assertIn("Accounting failure", dec.reasons[0])
        self.assertEqual(session.status, "ACCOUNTING_ERROR")
        
        # Subsequent actions MUST fail closed!
        dec2 = DigitalTwinFacade.authorize_action(session.execution_id, act)
        self.assertEqual(dec2.decision, "ERROR")
        self.assertIn("ACCOUNTING_ERROR", dec2.reasons[0])

    # Test 19: Zero Cost Internal Event Allowed
    def test_zero_cost_internal_event_allowed(self):
        session = self._create_test_session(max_cost=1.00)
        evt_zero = UsageEvent.create_tool_event(session.execution_id, "code_sandbox", "execute", 0, actual_cost=0.0)
        success, msg, act_cost = DigitalTwinFacade.record_usage_event(evt_zero)
        
        self.assertTrue(success)
        self.assertEqual(act_cost, 0.0)
        self.assertEqual(EconomicLedger().get_actual_cost(session.execution_id), 0.0)

    # Test 20: Multiple Violations Explained
    def test_multiple_violations_explained(self):
        session = self._create_test_session(max_cost=0.50, max_tools=2, max_steps=3)
        # $0.48 spent, 2 tool calls completed (at max_tools=2)
        EconomicLedger().record_event(UsageEvent.create_tool_event(session.execution_id, "serpapi", "search", 24, actual_cost=0.24))
        EconomicLedger().record_event(UsageEvent.create_tool_event(session.execution_id, "serpapi", "search", 24, actual_cost=0.24))
        
        act = ProposedAction(execution_id=session.execution_id, action_type="tool_call", provider="serpapi", units=10) # $0.10 -> total $0.58 > $0.50 AND 3 tools > 2
        dec = DigitalTwinFacade.authorize_action(session.execution_id, act)
        
        self.assertEqual(dec.decision, "BLOCK")
        self.assertGreater(len(dec.reasons), 1) # Multiple violations recorded!
        reasons_text = " ".join(dec.reasons)
        self.assertIn("exceeds selected plan budget", reasons_text)
        self.assertIn("exceed plan limit", reasons_text)

if __name__ == "__main__":
    unittest.main()
