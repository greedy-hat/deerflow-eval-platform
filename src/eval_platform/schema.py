import json
from pathlib import Path
from .models import Scenario

REQUIRED_TYPES = {"knowledge_qa", "troubleshooting", "tool_execution", "hybrid_workflow", "escalation"}

def load_scenario(path: str | Path) -> Scenario:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    for key in ("id", "task_type", "input", "expected"):
        if key not in payload:
            raise ValueError(f"Scenario missing field: {key}")
    if payload["task_type"] not in REQUIRED_TYPES:
        raise ValueError(f"Unrecognized task_type: {payload['task_type']}")
    expected = payload["expected"]
    for key in ("required_events", "forbidden_events", "ordering", "required_state"):
        if key in expected and not isinstance(expected[key], (list if key != "required_state" else dict)):
            raise ValueError(f"Invalid expected.{key}")
    return Scenario(**payload)
