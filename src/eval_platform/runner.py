from dataclasses import asdict
from pathlib import Path
import json
from typing import Protocol
from .models import Event, Scenario, Execution, EvaluationReport
from .evaluators import DEFAULT_EVALUATORS, Evaluator

class AgentAdapter(Protocol):
    def execute(self, case: Scenario) -> Execution: ...

class FixtureAgent:
    """Deterministic local agent fixture. No remote I/O or real side effects."""
    def execute(self, case: Scenario) -> Execution:
        sim = case.environment.get("fixture_execution")
        if sim is None:
            raise ValueError("Missing environment.fixture_execution. Use a real adapter for integration runs.")
        return Execution(trace_id=f"fixture-{case.id}", final_answer=sim.get("final_answer", ""),
                         events=[Event(**x) for x in sim.get("events", [])],
                         state=sim.get("state", {}), artifacts=sim.get("artifacts", {}))

class EvaluationRunner:
    def __init__(self, agent: AgentAdapter, evaluators: list[Evaluator] | None = None):
        self.agent = agent
        self.evaluators = evaluators if evaluators is not None else DEFAULT_EVALUATORS

    def run(self, case: Scenario) -> EvaluationReport:
        execution = self.agent.execute(case)
        scores = [score for evaluator in self.evaluators for score in evaluator.evaluate(case, execution)]
        hard_gates = {"outcome", "trajectory", "skill_routing", "safety"}
        passed = all(s.status == "pass" for s in scores if s.metric in hard_gates and s.status != "not_applicable")
        return EvaluationReport(case.id, execution.trace_id, scores, passed,
                                [s.metric.upper() + "_FAILED" for s in scores if s.status in ("fail", "error")])

def save_report(report: EvaluationReport, directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / f"{report.case_id}.json"
    path.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8")
    return path
