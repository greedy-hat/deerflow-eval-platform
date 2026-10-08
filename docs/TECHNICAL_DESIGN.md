# DeerFlow Evaluation Platform — Technical Design

## 1. Objective and constraints
For a hybrid customer-support agent combining knowledge Q&A, troubleshooting, tool actions, multiple agents and DeerFlow Skills, ship an evaluation platform that measures **real task outcomes** rather than just LLM answer quality. Avoid assuming that a pleasing answer means a ticket or configuration change happened.

Design objectives: reproducible scenario fixtures; stable evaluator contracts; trace-correlated atomic scores; negative Skill routing tests; isolated tool state; no customer secrets; release gating by risk.

## 2. Architecture
- **SUT:** DeerFlow lead agent, subagents, RAG, Skills, tools, sandbox.
- **Control plane:** scenarios, datasets, experiments, versions, release policy.
- **Execution plane:** fixture or DeerFlow adapter, case runner, environment reset, artifact collection.
- **Evaluation plane:** deterministic outcome/trajectory/safety/Skill-routing rules, DeepEval for supported LLM/agent metrics, Ragas for RAG metrics, LLM judges when determinism is unavailable.
- **Observability:** Langfuse as shared experiment/trace/score view; don't build a second full tracing product.
- **Reports:** case-level decisions, score provenance, failure classification and paired version comparison.

## 3. Domain contracts
**Scenario:** id, task_type, input, expected, environment, metadata. Task types: knowledge_qa, troubleshooting, tool_execution, hybrid_workflow, escalation. The environment describes synthetic fixtures and safe external-system stubs.

**Execution:** trace_id, final_answer, ordered events, observed external state, artifacts. Each event has id, kind, parent, skill and tool references. For production use, extend with tenant-safe correlation IDs, timestamps, run/thread/subagent IDs, Skill version, model/prompt and knowledge snapshot identifiers.

**Score:** metric, pass/fail/not_applicable/error, optional numeric score, evidence event IDs, reason, evaluator version. A framework adapter must map its scores into this schema and preserve native raw output separately.

Version all schemas; do not use metric names alone to identify judge criteria. Treat missing required evidence as failure/error, not success.

## 4. E2E evaluation
Three orthogonal dimensions:
1. **Outcome:** external state assertions (ticket exists, diagnosis root cause, successful mutation with no unintended side effect), not only text.
2. **Trajectory:** required/forbidden events and partial-order constraints; allow multiple legitimate plans.
3. **Response:** correctness, support from sources, comprehensibility, handoff quality.

Operationally run: load case → isolate and reset fixture → start agent → collect trace/state → evaluate → persist atomic scores → decision. For multi-turn simulations, constrain the user simulator to a deterministic state machine with checkpoints; log simulator turns separately.

### Release gate
Hard-fail on unauthorized tool operations, material disclosure of sensitive information, forbidden state changes and missing mandatory high-risk outcomes. Use paired-case regression and repeated runs for stochastic metrics. Latency/cost are secondary constraints, not replacements for task success.

## 5. Skills evaluation
Do not equate a Skill with a single tool API. DeerFlow Skills are discoverable instructions/resources with downstream tool execution.

- S0 **Static:** frontmatter, policy, references, packaging.
- S1 **Discovery/selection:** required, acceptable, forbidden, and no-Skill cases; precision/recall/F1 with multi-label ground truth.
- S2 **Loading:** selected Skill actually loaded, version verified.
- S3 **Instruction adherence:** critical required steps followed, disallowed behavior avoided.
- S4 **Execution:** tool name/arguments, sandbox artifact, exit status, retries and permission boundaries.
- S5 **Outcome:** local task state and expected artifacts verified.

Three harness modes: forced-Skill unit test, unconstrained Skill-selection test, and full integration scenario. Always test with and without new Skill version at fixed model/prompt/RAG snapshots; record conflicting skill choices. Failure labels: not_selected, false_trigger, load_failed, instruction_violation, tool_error, invalid_output, conflict, security_violation.

## 6. RAG evaluation
Separate retrieval (recall@k, precision@k, MRR, context recall/precision) from synthesis (faithfulness, answer relevance, citation correctness). Include documentation freshness, API version matching and troubleshooting-step coverage. Use Ragas metrics where their input contracts fit; do not fabricate reference answers for unlabeled production queries.

## 7. Integrations
**DeerFlow:** start with native Langfuse tracing if supported by deployed version. Build a trace adapter from actual observed spans, not assumptions. For actions capture real mock service state. Do not enable side effects in production.

**Langfuse:** persist trace/observation scores with case_id, run_id, evaluator_version, baseline/candidate versions. Redact log contents, authentication tokens and PII. Make data retention configurable.

**DeepEval:** only pass supported test cases and traces to respective metrics; trace-based metrics require compatible trace data. Start with component metrics and GEval, then validate native agent metrics.

**Ragas:** build per-observation RAG samples. Use judge configuration pinned by model/version; preserve prompts and scoring outputs for audit.

## 8. Reliability and operations
Agent timeouts, tool failures, evaluator failures, budget exhausted, missing telemetry and fixture initialization failures must be explicit error statuses. Use retries only for safe idempotent calls; preserve attempt IDs. Separate worker pools for Agent runs and judge calls. Per-tenant access controls, encrypted credentials, least-privilege integration and audit trail are required before production.

## 9. Versioning, roll-out and acceptance
Contract baseline v1 includes Scenario/Execution/Score, fixture evaluator, stable CI. Before production: deploy real DeerFlow adapter, inspect trace coverage, implement Langfuse score write-back, DeepEval/Ragas adapters, Skill loader/execution events, isolated test tools and dataset management UI. Validate using 100+ curated cases across all task categories with negative security/Skills cases; compare against a fixed baseline and calibrate judges with human review.

**Current implementation status:** only deterministic fixture-mode evaluators and CI tests exist. Live integrations, orchestration workers, persistence back-end and UI are planned interfaces, not completed features.
