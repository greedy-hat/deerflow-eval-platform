# DeerFlow Evaluation Platform

Scenario-driven evaluation platform for mixed customer-support agents using DeerFlow. The target design is a complete shared platform; the current code is a fixture-only foundation.

## Evaluation domains

- **Agent — Langfuse + DeepEval:** task/tool/response and multi-turn evaluation, with independent business-state and safety assertions.
- **RAG — Langfuse + DeepEval:** retrieval, fixed-context generation and end-to-end evaluation, with source/citation provenance.
- **Skills — dedicated Harness:** package, routing, loading, adherence, execution and independent outcome validation; shared reporting and optional semantic judging.
- Shared versioned datasets, durable execution, isolation, access control, regression/release gates and Langfuse trace/experiment/score views.

## Current fixture quickstart

```bash
python -m pip install -e '.[dev]'
pytest -q
deer-eval run examples/hybrid_ticket.json
```

**Current maturity:** Fixture-mode runnable foundation. Live DeerFlow/RAG targets, Langfuse, DeepEval, the dedicated Skills Harness and a web UI are NOT implemented or validated yet.

**Target architecture:** React/TypeScript console, FastAPI backend, PostgreSQL metadata and durable jobs, S3-compatible evidence storage, separate execution/evaluation workers, and verified Agent/RAG adapters using Langfuse + DeepEval, alongside a dedicated Skills Harness. Full Skills, RAG, multi-turn, regression gates, access control and operations are one delivery scope. PostgreSQL owns published versions and decisions; Git is import/export and Langfuse is a projection. The design documents describe target behavior, not implemented capabilities.

See [technical design](docs/TECHNICAL_DESIGN.md), [Skills evaluation design](docs/SKILLS_EVALUATION.md), [integration contract](docs/INTEGRATION.md) and [acceptance](docs/ACCEPTANCE.md). Do not run irreversible customer operations during evaluation.
