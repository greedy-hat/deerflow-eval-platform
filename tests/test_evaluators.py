from pathlib import Path
from eval_platform.models import Event
from eval_platform.schema import load_scenario
from eval_platform.runner import EvaluationRunner, FixtureAgent
from eval_platform.evaluators import TrajectoryEvaluator, SkillRoutingEvaluator, OutcomeEvaluator, SafetyEvaluator

BASE = Path(__file__).resolve().parents[1] / "examples/hybrid_ticket.json"

def test_happy_path():
    report = EvaluationRunner(FixtureAgent()).run(load_scenario(BASE))
    assert report.release_pass
    assert all(s.status == "pass" for s in report.scores)

def test_forbidden_action_blocked():
    case = load_scenario(BASE)
    execution = FixtureAgent().execute(case)
    execution.events.append(Event("danger", "production_config_changed"))
    assert TrajectoryEvaluator().evaluate(case, execution)[0].status == "fail"

def test_wrong_order_blocked():
    case = load_scenario(BASE)
    execution = FixtureAgent().execute(case)
    execution.events.reverse()
    assert TrajectoryEvaluator().evaluate(case, execution)[0].status == "fail"

def test_skill_not_selected():
    case = load_scenario(BASE)
    execution = FixtureAgent().execute(case)
    execution.events[:] = [e for e in execution.events if e.skill_id != "ticket-creation"]
    assert SkillRoutingEvaluator().evaluate(case, execution)[0].status == "fail"

def test_real_state_is_required():
    case = load_scenario(BASE)
    execution = FixtureAgent().execute(case)
    execution.state["ticket_created"] = False
    assert OutcomeEvaluator().evaluate(case, execution)[0].status == "fail"

def test_safety_violation():
    case = load_scenario(BASE)
    execution = FixtureAgent().execute(case)
    execution.events.append(Event("v", "safety_violation"))
    assert SafetyEvaluator().evaluate(case, execution)[0].status == "fail"
