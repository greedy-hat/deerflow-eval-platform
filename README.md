# DeerFlow Evaluation Platform

Scenario-driven evaluation platform foundation for mixed customer support agents using DeerFlow.

## Goals
- E2E outcome checks: external state, required and forbidden operations, event ordering.
- Skills evaluation: routing (required/acceptable/forbidden), execution harness extension.
- RAG and judge adapters: integration boundaries for Ragas, DeepEval, and Langfuse.
- Safe deterministic fixture tests, reusable CI and release gates.

## Local quickstart
```bash
python -m pip install -e '.[dev]'
pytest -q
deer-eval run examples/hybrid_ticket.json
```

**Current maturity:** Fixture-mode runnable foundation. Live DeerFlow, Langfuse, DeepEval, Ragas, full Skills harness and a web UI are NOT implemented or validated yet.

See [technical design](docs/TECHNICAL_DESIGN.md), [integration contract](docs/INTEGRATION.md) and [acceptance](docs/ACCEPTANCE.md). Do not run irreversible customer operations during evaluation.
