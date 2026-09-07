from typing import Dict, List, Tuple, Any, Optional
from decimal import Decimal, ROUND_HALF_UP
import math
import threading
from providers.usage_event import UsageEvent

def to_decimal(val: float) -> Decimal:
    if math.isnan(val) or math.isinf(val):
        raise ValueError(f"Cannot convert non-finite float {val} to Decimal")
    return Decimal(str(round(val, 6))).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)

class EconomicLedger:
    """
    Authoritative Real-Time Economic Ledger.
    Maintains immutable, append-only, idempotent actual usage events per execution.
    Uses Decimal arithmetic for security-critical monetary calculations.
    """
    _instance = None
    _lock = threading.RLock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EconomicLedger, cls).__new__(cls)
                cls._instance._events = {} # execution_id -> Dict[event_id, UsageEvent]
                cls._instance._reservations = {} # execution_id -> Dict[reservation_id, Decimal]
                cls._instance._session_locks = {} # execution_id -> threading.RLock
            return cls._instance

    def _get_session_lock(self, execution_id: str) -> threading.RLock:
        with self._lock:
            if execution_id not in self._session_locks:
                self._session_locks[execution_id] = threading.RLock()
            return self._session_locks[execution_id]

    def record_event(self, event: UsageEvent) -> Tuple[bool, str, float]:
        """
        Appends an actual usage event to the ledger.
        Enforces idempotency (duplicate event_id is not double-counted) and rejects negative/NaN/Inf values.
        """
        if not event.execution_id or not event.execution_id.strip():
            return False, "Missing execution_id in usage event", 0.0
        if not event.event_id or not event.event_id.strip():
            return False, "Missing event_id in usage event", 0.0

        if math.isnan(event.actual_cost) or math.isinf(event.actual_cost) or event.actual_cost < 0:
            return False, f"Invalid event actual_cost ({event.actual_cost})", 0.0
        if event.input_tokens < 0 or event.output_tokens < 0 or event.units_consumed < 0:
            return False, "Invalid negative tokens or units in usage event", 0.0

        session_lock = self._get_session_lock(event.execution_id)
        with session_lock:
            if event.execution_id not in self._events:
                self._events[event.execution_id] = {}

            # Idempotency check: duplicate event_id
            if event.event_id in self._events[event.execution_id]:
                current_total = self._calculate_actual_cost_decimal(event.execution_id)
                return True, f"Duplicate event '{event.event_id}' ignored idempotently", float(current_total)

            # Record event
            self._events[event.execution_id][event.event_id] = event
            current_total = self._calculate_actual_cost_decimal(event.execution_id)
            return True, "Usage event recorded successfully", float(current_total)

    def _calculate_actual_cost_decimal(self, execution_id: str) -> Decimal:
        events = self._events.get(execution_id, {})
        total = Decimal('0.000000')
        for evt in events.values():
            total += to_decimal(evt.actual_cost)
        return total.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)

    def reserve_cost(self, execution_id: str, reservation_id: str, amount: float) -> bool:
        if amount < 0 or math.isnan(amount) or math.isinf(amount):
            return False
        session_lock = self._get_session_lock(execution_id)
        with session_lock:
            if execution_id not in self._reservations:
                self._reservations[execution_id] = {}
            self._reservations[execution_id][reservation_id] = to_decimal(amount)
            return True

    def release_reservation(self, execution_id: str, reservation_id: str):
        session_lock = self._get_session_lock(execution_id)
        with session_lock:
            if execution_id in self._reservations:
                self._reservations[execution_id].pop(reservation_id, None)

    def get_actual_cost_decimal(self, execution_id: str) -> Decimal:
        session_lock = self._get_session_lock(execution_id)
        with session_lock:
            return self._calculate_actual_cost_decimal(execution_id)

    def get_actual_cost(self, execution_id: str) -> float:
        return float(self.get_actual_cost_decimal(execution_id))

    def get_reserved_cost_decimal(self, execution_id: str) -> Decimal:
        session_lock = self._get_session_lock(execution_id)
        with session_lock:
            reservations = self._reservations.get(execution_id, {})
            total = Decimal('0.000000')
            for amt in reservations.values():
                total += amt
            return total.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)

    def get_reserved_cost(self, execution_id: str) -> float:
        return float(self.get_reserved_cost_decimal(execution_id))

    def get_events(self, execution_id: str) -> List[UsageEvent]:
        session_lock = self._get_session_lock(execution_id)
        with session_lock:
            return list(self._events.get(execution_id, {}).values())

    def get_summary(self, execution_id: str, max_budget: float = 0.0) -> Dict[str, Any]:
        session_lock = self._get_session_lock(execution_id)
        with session_lock:
            events = list(self._events.get(execution_id, {}).values())
            actual_cost_dec = self._calculate_actual_cost_decimal(execution_id)
            reserved_cost_dec = Decimal('0.000000')
            for amt in self._reservations.get(execution_id, {}).values():
                reserved_cost_dec += amt
            reserved_cost_dec = reserved_cost_dec.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)

            budget_dec = to_decimal(max_budget).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP) if max_budget > 0 else Decimal('0.0000')
            remaining_dec = max(Decimal('0.0000'), budget_dec - actual_cost_dec - reserved_cost_dec).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)

            llm_calls = sum(1 for e in events if (e.operation == "generate_content" or e.provider == "gemini") and e.operation != "retry")
            tool_calls = sum(1 for e in events if e.operation in ["search", "text_to_speech", "execute"] or (e.provider != "gemini" and e.operation != "retry"))
            retries = sum(1 for e in events if e.operation == "retry")
            tokens = sum(e.input_tokens + e.output_tokens for e in events)
            steps = len(events)

            return {
                "execution_id": execution_id,
                "actual_cost": float(actual_cost_dec),
                "reserved_cost": float(reserved_cost_dec),
                "total_committed_cost": float(actual_cost_dec + reserved_cost_dec),
                "max_budget": float(budget_dec),
                "remaining_budget": float(remaining_dec),
                "llm_calls": llm_calls,
                "tool_calls": tool_calls,
                "retries": retries,
                "total_tokens": tokens,
                "total_steps": steps,
                "event_count": len(events)
            }

    def clear(self):
        with self._lock:
            self._events.clear()
            self._reservations.clear()
            self._session_locks.clear()
