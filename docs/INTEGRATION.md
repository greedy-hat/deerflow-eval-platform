# Complete Platform Integration Contract

This contract applies to the Agent, RAG and Skills domains in [technical design](TECHNICAL_DESIGN.md). Agent/RAG use Langfuse + DeepEval; Skills uses the [dedicated Skills Harness](SKILLS_EVALUATION.md). The current `FixtureAgent` is an offline replay tool and does not satisfy live integration. Unsupported mandatory capabilities block complete acceptance; they are not silently dropped.

## 1. Verify interfaces before dependent implementation

- Record DeerFlow commit/version and actual task API. Contract-test request fields, streaming records, terminal status, remote run lookup, cancellation, idempotency and timeout behavior.
- Identify lead/subagent/tool/retrieval/Skill evidence producers and completeness. Publish a capability table distinguishing discovery, selection, context loading and attributable execution.
- Instrument missing required Skill/evidence stages or select an explicitly reviewed compatible target version. Do not infer events from final answers or tool names.
- Pin Langfuse SDK/deployment, DeepEval SDK/metric/evaluation mode and judge configuration. Agent and RAG input mappers share one DeepEval adapter. Native Langfuse tracing is conditional; independent platform evidence remains mandatory.

## 2. Connect all clients to platform authority

- UI, CLI and CI use versioned API resources and project authorization; TypeScript types/clients derive from OpenAPI.
- PostgreSQL owns immutable published versions, run plans/states, evaluations and release decisions. Git imports create drafts and exports preserve published snapshots; Langfuse is a mapped projection.
- Publish domain-specific dataset/target/environment/criterion/judge/policy versions before launch. Declare `evaluation_domain` and mode. Atomically freeze the experiment case/repetition plan and create initial jobs. Agent runs can link component RAG/Skills evaluations without duplicating execution or release criteria.
- Use request idempotency/body digests, draft revisions and structured errors. Never acknowledge remote cancellation as completed until verified.
- Offline fixture execution stays explicitly labelled and cannot bypass a live gate.

## 3. Preserve identity, privacy and environment isolation

- Allocate project, experiment, case-run, attempt, turn and evaluation IDs with distinct semantics. Propagate service/trace correlation or retain explicit mappings.
- Give the agent only user input and allowed context; keep assertions/references and platform credentials inaccessible.
- For mutation-capable Agent/Skills targets, capture initial/final state through an independent environment reader, including object identity, fields, count and forbidden changes. RAG captures immutable corpus/pipeline/query/context provenance; static Skills validation does not require agent execution.
- Scope credentials, memory, workspace and test services per run. Enforce allowed endpoints for subprocesses and log attempted/denied/successful mutations.
- Stop/reconcile work before final state; use bounded settlement deadlines. Unconfirmed termination or cleanup quarantines the environment and blocks release/reuse.

## 4. Enforce durable job semantics

- Create jobs/outbox with domain changes in one PostgreSQL transaction. Claims use short row-lock transactions; remote execution never holds database locks.
- Version job payloads and include lease owner/expiry/fencing token. Stale workers cannot commit results; environment credentials prevent stale mutations where supported.
- Treat delivery as at least once. Deduplicate requests/events/results without collapsing genuine retries or independent repetitions.
- Recover remote state before replaying an execution. Lease expiry does not prove remote termination; uncertain writes require independent reconciliation.
- Shared quotas, cancellation, retry eligibility and cleanup deadlines are persisted and enforced across workers. Record retries and exhausted jobs for diagnosis.

## 5. Domain mapping and score ownership

| Domain | Required adapter work | Evaluation boundary |
| --- | --- | --- |
| Agent | Task/turn/tool/subagent evidence to compatible DeepEval trace or test-case structures | Existing task/tool/response metrics; independent business and safety assertions remain hard gates |
| RAG | Standalone or observation-linked query/ranked-context/actual synthesis/response/reference samples | DeepEval contextual, faithfulness, relevancy and rubric metrics; labelled IR/citation assertions where declared |
| Skills | Versioned package/catalog, runtime lifecycle, attributable execution and independent artifacts/state | Custom S0–S5 validators and static/forced/routing/integration modes; optional shared semantic judge |

- Preserve causal/component scope. A Langfuse trace is not automatically a valid input for every DeepEval metric; require tested native integration or explicit conversion.
- Validate mode-specific metric fields and reference availability before scoring. Never fabricate missing RAG reference answers, generated answers or Skill lifecycle events.
- Use existing Langfuse trace, experiment comparison and score capabilities. Platform metadata has one authority; native runners do not independently reschedule/retry platform work.
- Each criterion has one owner and domain/scope. Link overlapping Agent/RAG/Skills observations instead of counting equivalent scores multiple times. Preserve module-specific scores in combined reports.
- Skills must meet its dedicated mode/stage applicability rules; forced loading is not routing success and static validation is not runtime acceptance.

## 6. Commit evidence and evaluate

- Normalize source identity, producer, turn/attempt/call/target, arguments/result and parent/causal relationships; retain redacted raw provenance.
- Collection order/timestamps do not prove cross-agent causality. Scope constraints explicitly and reject ambiguous evidence.
- Declare evidence completeness; no forbidden event is not a pass without complete relevant audit coverage.
- Upload checksum-verified immutable objects before committing a complete evidence manifest and evaluation job. Incomplete manifests block scoring; orphan collection respects active uploads and retention.
- Map each criterion to required evidence/framework inputs, scope and versions. Re-scoring creates a new evaluation; original executions/scores/decisions remain unchanged.
- Finish required evaluation and cleanup before final decision. Persist pass/fail/blocked with full failure/error reasons, fixed policy and coverage references.

## 7. Synchronize and retain projections

- Use a transactional outbox for Langfuse datasets/experiment items/traces/observations/scores, with explicit local-to-remote mappings.
- Deduplicate using integration/project/domain/run/evaluation/criterion-version/scope identities; retry does not overwrite prior evaluations.
- Outages leave durable pending/error state. Quality decisions stay authoritative in PostgreSQL; required publication separately blocks delivery.
- Apply matching project access, redaction and retention to remote views. Reconcile remote deletions/expired evidence visibly.

## 8. Full contract test matrix

Test API authorization, publication/edit conflicts, idempotency and legacy schemas; all task types; Skills S0–S5 and alternative routes; Agent/DeepEval trace and RAG/DeepEval sample mappings; multi-turn and parallel evidence; wrong/duplicate objects; false success; forbidden attempts; uncertain writes/timeouts; missing telemetry; duplicate job/event delivery; stale workers; namespace isolation; cleanup/cancel failures; re-evaluation; projection outage/retry; storage consistency/retention; upgrade/backup restore; domain linkage without double-counting; and full UI/API/CI workflows under the declared concurrency/capacity profile.
