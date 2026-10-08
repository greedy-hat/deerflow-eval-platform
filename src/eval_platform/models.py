from dataclasses import dataclass, field
from typing import Any, Literal

Status = Literal["pass", "fail", "not_applicable", "error"]

@dataclass(frozen=True)
class Event:
    event_id: str
    type: str
    parent_id: str | None = None
    skill_id: str | None = None
    tool_name: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class Scenario:
    id: str
    task_type: str
    input: dict[str, Any]
    expected: dict[str, Any]
    environment: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class Execution:
    trace_id: str
    final_answer: str
    events: list[Event]
    state: dict[str, Any]
    artifacts: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class Score:
    metric: str
    status: Status
    score: float | None
    evidence_ids: list[str] = field(default_factory=list)
    reason: str = ""
    evaluator_version: str = "rules-v1"

@dataclass(frozen=True)
class EvaluationReport:
    case_id: str
    trace_id: str
    scores: list[Score]
    release_pass: bool
    failure_codes: list[str]
