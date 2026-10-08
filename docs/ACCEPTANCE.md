# Acceptance Criteria

## Fixture foundation
- [x] Load typed case from JSON.
- [x] Check external-state assertions, required/forbidden trajectory events and event ordering.
- [x] Check required and forbidden Skill selections.
- [x] Safety-violation hard gate.
- [x] JSON report and CLI exit code.
- [x] GitHub Actions pytest job.

## Real integration (not complete)
- [ ] Real DeerFlow adapter tested against pinned version.
- [ ] Langfuse traces and scores linked to case_id/experiment_id.
- [ ] DeepEval and Ragas live metric adapters tested on representative cases.
- [ ] Skills loading, instruction adherence and execution outcome harness.
- [ ] External side-effect isolation and reset proved.
- [ ] Multi-turn simulator and state-machine guardrails.
- [ ] Judge consistency baseline, run repetitions and confidence intervals.
- [ ] Release gate quality thresholds approved by business/security owners.
- [ ] Secrets/redaction, RBAC, audit logs, retention and performance load tests.

No claim of production readiness until all integration items are verified.
