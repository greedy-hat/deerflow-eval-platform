# Integration Contract

1. Identify running DeerFlow version/commit and the actual HTTP/SDK entry point for a task. Do not infer method signatures from repository examples.
2. Enable DeerFlow's supported Langfuse tracing configuration and verify lead/subagent/tool observations actually appear.
3. Define correlation fields: experiment_id, case_id, trace_id, run_id, thread_id, skill_id, skill_version, tool_call_id. Preserve parent-child relations across async subagents.
4. Implement a real AgentAdapter mapping each execution into the repository's Execution schema. FixtureAgent is intentionally local-only and safe.
5. Inject deterministic mock ticket/log/config services and an isolated sandbox. Reset state before each run; assert actual system state afterwards.
6. Record explicit skill_selected, skill_loaded, skill_executed and skill_completed event semantics in code where observable; missing instrumentation must be reported.
7. Map DeepEval/Ragas metric inputs and outputs through versioned adapters. Attach resulting scores to Langfuse trace/observation with evidence identifiers.
8. Add secrets only as environment/secret-manager entries. Never log API keys or raw customer requests by default.
9. Test partial failures, duplicate messages, idempotency, multi-turn and multi-skill scenarios before production.
