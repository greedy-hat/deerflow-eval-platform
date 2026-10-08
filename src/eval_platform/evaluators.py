from typing import Protocol
from .models import Scenario, Execution, Score

class Evaluator(Protocol):
    def evaluate(self, case: Scenario, execution: Execution) -> list[Score]: ...

class OutcomeEvaluator:
    def evaluate(self, case: Scenario, execution: Execution) -> list[Score]:
        required = case.expected.get("required_state", {})
        if not required:
            return [Score("outcome", "not_applicable", None, reason="No state assertions")]
        failures = [k for k, v in required.items() if execution.state.get(k) != v]
        return [Score("outcome", "fail" if failures else "pass", 0.0 if failures else 1.0,
                      reason="State mismatch: " + ", ".join(failures) if failures else "State confirmed")]

class TrajectoryEvaluator:
    def evaluate(self, case: Scenario, execution: Execution) -> list[Score]:
        events = execution.events
        kinds = [e.type for e in events]
        required = case.expected.get("required_events", [])
        forbidden = case.expected.get("forbidden_events", [])
        missing = [x for x in required if x not in kinds]
        violations = [e for e in events if e.type in forbidden]
        ordering_errors = []
        for edge in case.expected.get("ordering", []):
            before, after = edge["before"], edge["after"]
            if before not in kinds or after not in kinds or kinds.index(before) >= kinds.index(after):
                ordering_errors.append(f"{before} must precede {after}")
        ok = not (missing or violations or ordering_errors)
        return [Score("trajectory", "pass" if ok else "fail", float(ok),
                      evidence_ids=[e.event_id for e in violations],
                      reason="; ".join([*(f"missing:{x}" for x in missing),
                                        *(f"forbidden:{x.type}" for x in violations), *ordering_errors]) or "Constraints passed")]

class SkillRoutingEvaluator:
    def evaluate(self, case: Scenario, execution: Execution) -> list[Score]:
        spec = case.expected.get("skills")
        if spec is None:
            return [Score("skill_routing", "not_applicable", None, reason="No routing assertions")]
        selected = {e.skill_id for e in execution.events if e.type == "skill_selected" and e.skill_id}
        required = set(spec.get("required", []))
        forbidden = set(spec.get("forbidden", []))
        acceptable = set(spec.get("acceptable", []))
        unknown = selected - (required | acceptable)
        fail = bool((required - selected) or (selected & forbidden) or (spec.get("no_skill_required", False) and selected))
        if spec.get("strict_allowlist", False) and unknown:
            fail = True
        reason = f"selected={sorted(selected)}, missing={sorted(required-selected)}, forbidden={sorted(selected & forbidden)}, unknown={sorted(unknown)}"
        return [Score("skill_routing", "fail" if fail else "pass", float(not fail),
                      evidence_ids=[e.event_id for e in execution.events if e.type == "skill_selected"], reason=reason)]

class SafetyEvaluator:
    def evaluate(self, case: Scenario, execution: Execution) -> list[Score]:
        violations = [e for e in execution.events if e.type == "safety_violation"]
        return [Score("safety", "fail" if violations else "pass", float(not violations),
                      evidence_ids=[e.event_id for e in violations],
                      reason=f"{len(violations)} safety violations")]

DEFAULT_EVALUATORS = [OutcomeEvaluator(), TrajectoryEvaluator(), SkillRoutingEvaluator(), SafetyEvaluator()]
