from typing import Dict, List, Tuple, Optional, Any, Callable
from decimal import Decimal, ROUND_HALF_UP
import math
import uuid
from domain.models import ProposedAction, FirewallDecision, ExecutionSession
from providers.usage_event import UsageEvent
from providers.pricing import ProviderPricingConfig
from engine.ledger import EconomicLedger, to_decimal

class RuntimeEconomicFirewall:
    """
    Runtime Economic Firewall & Controlled Provider Gateway.
    Enforces selected Digital Twin plan limits BEFORE any provider execution.
    Maintains concurrency safety and fail-closed security invariants.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RuntimeEconomicFirewall, cls).__new__(cls)
            cls._instance.ledger = EconomicLedger()
            cls._instance._sessions: Dict[str, ExecutionSession] = {}
        return cls._instance

    def register_session(self, session: ExecutionSession):
        with self.ledger._lock:
            self._sessions[session.execution_id] = session

    def get_session(self, execution_id: str) -> Optional[ExecutionSession]:
        with self.ledger._lock:
            return self._sessions.get(execution_id)

    def evaluate_action(self, execution_id: str, action: ProposedAction) -> Tuple[FirewallDecision, Optional[str]]:
        """
        Evaluates a proposed runtime action against the selected plan & ledger state.
        Returns FirewallDecision ("ALLOW", "BLOCK", or "ERROR") and an optional reservation_id.
        Fails closed on any error, unknown provider, missing plan, or accounting failure.
        """
        session = self.get_session(execution_id)
        if not session:
            return FirewallDecision(
                decision="ERROR",
                execution_id=execution_id,
                action_id=action.action_id,
                reasons=[f"Execution session '{execution_id}' not found or uninitialized"]
            ), None

        if session.status == "ACCOUNTING_ERROR":
            return FirewallDecision(
                decision="ERROR",
                execution_id=execution_id,
                action_id=action.action_id,
                reasons=["Execution session is in fail-safe state: ACCOUNTING_ERROR. No further actions permitted."]
            ), None

        if session.status in ["COMPLETED", "BLOCKED"]:
            return FirewallDecision(
                decision="BLOCK",
                execution_id=execution_id,
                action_id=action.action_id,
                reasons=[f"Execution session is {session.status}"]
            ), None

        session_lock = self.ledger._get_session_lock(execution_id)
        with session_lock:
            reasons = []
            plan = session.selected_plan
            policy = session.policy

            # 1. Strict Provider & Model Verification (Fail Closed on Unknown Resource)
            action_cost_dec = Decimal('0.000000')
            try:
                if action.action_type == "llm_call" or action.provider == "gemini":
                    model = action.model or plan.selected_model
                    action_cost_dec = ProviderPricingConfig.calculate_llm_cost_decimal(
                        model, action.input_tokens, action.output_tokens, strict=True
                    )
                else:
                    action_cost_dec = ProviderPricingConfig.calculate_tool_cost_decimal(
                        action.provider, action.operation or "execute", action.units, strict=True
                    )
            except ValueError as ve:
                reasons.append(f"Resource violation: {str(ve)}")

            # 2. Model Allowlist Verification
            if action.model and action.model.strip():
                req_model = action.model.strip()
                allowed_models = policy.allowed_models or [plan.selected_model]
                if req_model not in allowed_models and req_model != plan.selected_model:
                    reasons.append(f"Requested model '{req_model}' is not permitted by selected economic plan")

            # 3. Ledger Economic State & Budget Verification
            ledger_summary = self.ledger.get_summary(execution_id, max_budget=plan.estimated_cost)
            current_actual_dec = Decimal(str(ledger_summary["actual_cost"]))
            current_reserved_dec = Decimal(str(ledger_summary["reserved_cost"]))
            allowed_budget_dec = Decimal(str(plan.estimated_cost))

            projected_cost_dec = (current_actual_dec + current_reserved_dec + action_cost_dec).quantize(Decimal('0.0001'))

            if current_actual_dec > allowed_budget_dec:
                reasons.append(f"Current actual cost (${float(current_actual_dec):.4f}) already exceeds allowed budget (${float(allowed_budget_dec):.4f})")

            if projected_cost_dec > allowed_budget_dec:
                reasons.append(f"Projected execution cost (${float(projected_cost_dec):.4f}) exceeds selected plan budget (${float(allowed_budget_dec):.4f})")

            # 4. Resource Counters Verification
            curr_llm = ledger_summary["llm_calls"]
            curr_tools = ledger_summary["tool_calls"]
            curr_retries = ledger_summary["retries"]
            curr_tokens = ledger_summary["total_tokens"]
            curr_steps = ledger_summary["total_steps"]

            proj_llm = curr_llm + (1 if action.action_type == "llm_call" else 0)
            proj_tools = curr_tools + (1 if action.action_type == "tool_call" else 0)
            proj_retries = curr_retries + (1 if action.action_type == "retry" else 0)
            proj_tokens = curr_tokens + action.input_tokens + action.output_tokens
            proj_steps = curr_steps + (1 if action.action_type == "step" or action.action_type in ["llm_call", "tool_call"] else 0)

            max_llm = plan.expected_llm_calls
            max_tools = min(plan.expected_tool_calls, policy.max_tool_calls)
            max_retries = min(plan.expected_retries, policy.max_retries)
            max_tokens = min(plan.expected_input_tokens + plan.expected_output_tokens, policy.max_tokens)
            max_steps = min(plan.expected_steps, policy.max_steps)

            if action.action_type == "llm_call" and proj_llm > max_llm:
                reasons.append(f"Projected LLM calls ({proj_llm}) exceed plan limit ({max_llm})")

            if action.action_type == "tool_call" and proj_tools > max_tools:
                reasons.append(f"Projected tool calls ({proj_tools}) exceed plan limit ({max_tools})")

            if action.action_type == "retry" and proj_retries > max_retries:
                reasons.append(f"Projected retries ({proj_retries}) exceed plan limit ({max_retries})")

            if proj_tokens > max_tokens:
                reasons.append(f"Projected tokens ({proj_tokens}) exceed plan token ceiling ({max_tokens})")

            if proj_steps > max_steps:
                reasons.append(f"Projected steps ({proj_steps}) exceed plan step ceiling ({max_steps})")

            # Decision Formulation
            if reasons:
                decision = FirewallDecision(
                    decision="BLOCK",
                    execution_id=execution_id,
                    action_id=action.action_id,
                    reasons=reasons,
                    current_actual_cost=float(current_actual_dec),
                    estimated_action_cost=float(action_cost_dec),
                    projected_cost=float(projected_cost_dec),
                    allowed_budget=float(allowed_budget_dec),
                    current_llm_calls=curr_llm,
                    projected_llm_calls=proj_llm,
                    max_llm_calls=max_llm,
                    current_tool_calls=curr_tools,
                    projected_tool_calls=proj_tools,
                    max_tool_calls=max_tools,
                    current_retries=curr_retries,
                    projected_retries=proj_retries,
                    max_retries=max_retries,
                    current_tokens=curr_tokens,
                    projected_tokens=proj_tokens,
                    max_tokens=max_tokens,
                    current_steps=curr_steps,
                    projected_steps=proj_steps,
                    max_steps=max_steps
                )
                return decision, None
            else:
                reservation_id = f"res_{uuid.uuid4().hex[:8]}"
                self.ledger.reserve_cost(execution_id, reservation_id, float(action_cost_dec))
                decision = FirewallDecision(
                    decision="ALLOW",
                    execution_id=execution_id,
                    action_id=action.action_id,
                    reasons=[],
                    current_actual_cost=float(current_actual_dec),
                    estimated_action_cost=float(action_cost_dec),
                    projected_cost=float(projected_cost_dec),
                    allowed_budget=float(allowed_budget_dec),
                    current_llm_calls=curr_llm,
                    projected_llm_calls=proj_llm,
                    max_llm_calls=max_llm,
                    current_tool_calls=curr_tools,
                    projected_tool_calls=proj_tools,
                    max_tool_calls=max_tools,
                    current_retries=curr_retries,
                    projected_retries=proj_retries,
                    max_retries=max_retries,
                    current_tokens=curr_tokens,
                    projected_tokens=proj_tokens,
                    max_tokens=max_tokens,
                    current_steps=curr_steps,
                    projected_steps=proj_steps,
                    max_steps=max_steps
                )
                return decision, reservation_id

    def authorize_and_execute(
        self,
        execution_id: str,
        action: ProposedAction,
        provider_func: Optional[Callable[[], Any]] = None,
        actual_cost_override: Optional[float] = None,
        simulate_accounting_failure: bool = False
    ) -> Tuple[FirewallDecision, Any]:
        """
        Controlled Provider Gateway.
        Enforces NO-BYPASS invariant: Action MUST be authorized before provider call.
        If blocked, provider_func is NEVER called ($0 spend).
        If provider call succeeds, actual usage event is recorded in the Ledger.
        If accounting fails, session enters fail-safe ACCOUNTING_ERROR state.
        """
        decision, reservation_id = self.evaluate_action(execution_id, action)

        if decision.decision != "ALLOW":
            return decision, None

        if not provider_func:
            # Default simulation provider function
            provider_func = lambda: {"status": "success", "result": f"Executed {action.action_type} via {action.provider}"}

        result = None
        try:
            result = provider_func()
        except Exception as e:
            if reservation_id:
                self.ledger.release_reservation(execution_id, reservation_id)
            return FirewallDecision(
                decision="ERROR",
                execution_id=execution_id,
                action_id=action.action_id,
                reasons=[f"Provider execution failed: {str(e)}"]
            ), None

        # Build & record actual usage event
        try:
            if simulate_accounting_failure:
                raise RuntimeError("Simulated ledger storage failure")

            if action.action_type == "llm_call" or action.provider == "gemini":
                usage_event = UsageEvent.create_llm_event(
                    execution_id=execution_id,
                    model=action.model or "gemini-2.5-flash",
                    input_tokens=action.input_tokens,
                    output_tokens=action.output_tokens,
                    actual_cost=actual_cost_override
                )
            else:
                usage_event = UsageEvent.create_tool_event(
                    execution_id=execution_id,
                    provider=action.provider,
                    operation=action.operation or action.action_type,
                    units=action.units,
                    actual_cost=actual_cost_override
                )

            success, msg, act_cost = self.ledger.record_event(usage_event)
            if not success:
                session = self.get_session(execution_id)
                if session:
                    session.status = "ACCOUNTING_ERROR"
                return FirewallDecision(
                    decision="ERROR",
                    execution_id=execution_id,
                    action_id=action.action_id,
                    reasons=[f"Accounting failure: {msg}. Execution entering fail-safe state."]
                ), None

        except Exception as e:
            session = self.get_session(execution_id)
            if session:
                session.status = "ACCOUNTING_ERROR"
            return FirewallDecision(
                decision="ERROR",
                execution_id=execution_id,
                action_id=action.action_id,
                reasons=[f"Accounting failure: {str(e)}. Execution entering fail-safe state."]
            ), None
        finally:
            if reservation_id:
                self.ledger.release_reservation(execution_id, reservation_id)

        return decision, result
