# Complete Platform Acceptance

This is one complete delivery scope, not an MVP or a set of optional milestones. All unchecked requirements are required for acceptance. Existing fixture code is recorded separately and does not establish platform readiness. [Technical design](TECHNICAL_DESIGN.md) defines architecture; [integration contract](INTEGRATION.md) defines interface obligations. Agent/RAG use Langfuse + DeepEval; [Skills](SKILLS_EVALUATION.md) uses a dedicated harness. All three domains are mandatory.

## Existing repository baseline

- [x] JSON loader and fixture replay exist.
- [x] Rules for supplied state, required/forbidden events, simple ordering, Skill selections and safety-violation events exist.
- [x] CLI, JSON export, six test functions and pytest CI configuration exist.

These checks describe files in the repository, not a validated deployment or completed platform feature.

## Contracts, versions and compatibility

- [ ] API/domain/job/evidence schema baseline published, with generated TypeScript client and compatibility tests.
- [ ] Nested validation, safe IDs, contradictory/empty assertion rejection and required metric inputs enforced before effects.
- [ ] Published datasets, target/environment/Skill/knowledge snapshots, criteria, judges and policies immutable; drafts support concurrent-edit conflict checks.
- [ ] Manifest fingerprints agent/model/prompt/dataset/policy/tool/evaluator configuration; unavailable provider revisions explicit.
- [ ] Domain/mode and case sample, stochastic repetition, recovery attempt and re-evaluation have separate identities and do not overwrite results; component evaluations link to existing execution evidence.
- [ ] Legacy fixtures remain usable for offline rule regression; fixture-labelled imports cannot masquerade as live evidence.
- [ ] Expand/migrate/contract upgrades, old/new worker compatibility and rollback/recovery tests preserve versions and queued jobs.

## Web console, API and CI

- [ ] OIDC login, project membership and roles enforced on every API/resource/artifact/live-update path.
- [ ] Console has Agent/RAG/Skills entries with validated domain-specific cases, dataset import/export/version publication and target/environment configuration.
- [ ] Console supports experiment plans, baselines, repetitions, launch/progress/cancel and failure diagnosis.
- [ ] Console supports evidence views, task/risk comparisons, annotation/calibration, policy publication, release decisions and integration/operational status.
- [ ] Published versions and existing decisions cannot be modified through UI or API.
- [ ] API idempotency keys detect conflicting payload reuse; pagination and resumable progress survive reconnects.
- [ ] CLI and CI use the same API/authorization/gates; pending, incomplete or blocked experiments never return release success.
- [ ] End-to-end browser tests cover authoring, publication, run, comparison and CI result; keyboard access, labels and status/error states verified.

## Persistence and durable orchestration

- [ ] PostgreSQL is the authority for versions/runs/evaluations/decisions; Git and Langfuse are explicit import/export/projection channels.
- [ ] Object checksums, completed evidence manifests and database references agree; incomplete uploads block scoring and orphan cleanup is safe.
- [ ] Job/outbox creation is atomic with domain transitions; duplicate requests/delivery cannot duplicate committed runs/scores.
- [ ] Transactional claims, lease renewal, fencing and persisted checkpoints withstand concurrent workers and process loss.
- [ ] Agent/evaluator/cleanup/synchronization pools honor shared project/provider concurrency, budgets, rate limits and backpressure.
- [ ] Recovery reconciles existing remote work before replay; uncertain writes and stale workers cannot silently execute duplicate mutations.
- [ ] Cancellation/deadline handling stops or quarantines remote work; periodic reconciliation handles stuck jobs and expired environments.
- [ ] Failed safe retries are diagnosable and replayable with audit; user replay cannot bypass policy.
- [ ] Database/object backup restore and retention deletion tests preserve reference/audit consistency.

## Execution and independent business evidence

- [ ] Pinned DeerFlow/Agent invocation, RAG query/retrieval/generation APIs and Skill runtime evidence verified by contract tests; domain-specific terminal/cancel semantics enforced.
- [ ] Mutation-capable targets have independent before/after state and complete attempted/denied/successful mutation audit; read-only RAG/static modes have appropriate provenance and isolation checks.
- [ ] Fresh thread/memory/workspace/service namespace and scoped credentials per case/repetition.
- [ ] Agent cannot read assertions, judge references, control-plane secrets or another project's state.
- [ ] Production/unapproved endpoints remain inaccessible, including subprocess and sandbox network paths.
- [ ] Successful diagnosis and exactly one correct ticket pass; wrong/duplicate ticket, false success, failed writes and forbidden/unauthorized attempts are detected.
- [ ] Event normalization preserves source/call/attempt/target/causal identity and deduplicates repeated delivery.
- [ ] Parallel/retry ordering is scoped correctly; missing/truncated/ambiguous required evidence blocks decisions.
- [ ] Cleanup and cancellation failures quarantine state and block release; uncertain writes are reconciled before safe retry.
- [ ] Concurrent cases cannot access or alter one another's memory, files or records.

## Agent evaluation — Langfuse + DeepEval

- [ ] End-to-end knowledge Q&A, troubleshooting, tool execution, hybrid, escalation and multi-turn cases use compatible DeepEval metrics and Langfuse trace/experiment/score capabilities.
- [ ] Task/efficiency trajectory metrics and tool/argument component metrics receive tested, correctly scoped input structures; unsupported evidence blocks required criteria.
- [ ] Response/rubric scoring calibrated with references; independent state/authorization/safety assertions can fail a case regardless of high judge scores.
- [ ] Imported traces declare evidence completeness and cannot claim independent outcomes that were not captured.
- [ ] No duplicate generic Agent metric engine or trace explorer implemented; API/console use the selected frameworks.

## RAG evaluation — Langfuse + DeepEval

- [ ] Standalone retrieval, fixed-context generation and end-to-end RAG modes supported, plus component scoring within an Agent execution.
- [ ] DeepEval contextual precision/recall/relevance, faithfulness, answer relevancy and correctness/rubric criteria mapped to pinned input contracts.
- [ ] Ranked chunks, corpus/index/retriever/reranker versions, retrieved context, actual synthesis context and response preserved.
- [ ] Reference-dependent metrics reject missing references; retrieval-only cases never fabricate generation output to satisfy incompatible APIs.
- [ ] Labelled IR and citation assertions use version-matched ground truth; model-judged context metrics are not presented as labelled IR metrics.
- [ ] Empty/irrelevant retrieval, no-answer questions, stale/conflicting sources and fabricated citations detected by declared criteria.
- [ ] Retrieval/generation observations and criterion scores link correctly to Langfuse; no second RAG evaluation framework required.

## Skills evaluation — Dedicated Harness

- [ ] Dedicated static/forced/routing/integration modes reuse shared scheduling, storage, evidence, access control and reporting.
- [ ] S0 packaging, S1 discovery/routing, S2 loading, S3 adherence, S4 execution and S5 outcome validated with verified runtime instrumentation.
- [ ] Mode/stage applicability resolved before execution; forced selection is not scored as routing success, and static validation cannot establish runtime readiness.
- [ ] Alternative/forbidden/no-Skill routes validated; all stage assertions bind to one valid route and the same package versions.
- [ ] Catalog scanning distinguished from context loading; explicit links attribute tool/subagent work and preserve failed attempts.
- [ ] Missing resources/wrong versions, step violations, permission conflicts, incorrect calls and invalid/missing artifacts detected despite plausible final answers.
- [ ] Independent artifact/business-state validation, safe package paths and isolated execution verified.
- [ ] Prior/candidate/no-Skill comparisons hold other inputs fixed and preserve mode-specific results.
- [ ] Optional semantic Skill checks use the shared calibrated DeepEval rubric judge; deterministic assertions remain authoritative.
- [ ] Per-stage scores/failure codes/evidence references published through the shared Score contract and Langfuse outbox.

## Shared evaluation guarantees

- [ ] Each criterion has one domain owner and scope; linked Agent/RAG/Skills evaluations reuse evidence without rerunning or double-counting the task.
- [ ] Human-labelled judge calibration, repeat-run variation, untrusted-input handling and malformed/timeout behavior verified for all semantic criteria.
- [ ] Multi-turn state machines preserve turn/transition evidence and private assertions; simulator errors block cases.
- [ ] Re-scoring creates a new evaluation linked to captured evidence without overwriting original execution/scores/decisions.

## Regression, decisions and Langfuse

- [ ] Required criteria/applicability/evidence resolved before execution; empty criteria and required not-applicable/error cannot pass.
- [ ] Pass/fail/blocked decisions preserve all business failures, evaluation errors and cleanup status.
- [ ] Full planned coverage and hard gates checked; high-risk failures cannot be averaged away.
- [ ] Absolute/slice/regression thresholds, repetitions and uncertainty rules recorded before candidate runs; incompatible/missing baseline data blocks comparison.
- [ ] Policy approval and complete audit exist before a release decision is used; annotations cannot silently override objective violations.
- [ ] Finalized decisions reference immutable versions, evidence/evaluations and coverage manifests.
- [ ] Langfuse experiment/trace/observation/score mappings verified with project access isolation.
- [ ] Database outbox survives outages; domain/run/evaluation/criterion/scope synchronization is idempotent and publication requirements affect delivery without rewriting quality scores.
- [ ] Retention/redaction/deletion propagate to Langfuse and other projections; expired evidence cannot support new decisions.

## Security, deployment and operations

- [ ] Project roles, browser sessions/CSRF, service credential revocation and server-side secret references verified.
- [ ] Synthetic or approved de-identified data; redaction before local/object persistence, tracing and judge requests, including errors/raw records.
- [ ] Artifact path/size validation, authorized short-lived downloads and bounded runtime/token/cost budgets enforced.
- [ ] Complete container deployment, TLS/network isolation, dependency pins and documented upgrade/restore procedures provided.
- [ ] API/storage/worker/provider health and queue age, stuck leases, cost, evidence loss, cleanup and sync-lag alerts exercised.
- [ ] Declared capacity profile covers users, concurrency, dataset/artifact sizes, quotas, latency and recovery objectives.
- [ ] Load, worker restart, database/object/provider/Langfuse outage and recovery tests pass at the declared profile.

Acceptance requires every section, recorded business thresholds and a verified operating profile. Partial demonstrations are development checks, not acceptance of a reduced product. No fixed case count or average score alone proves readiness.
