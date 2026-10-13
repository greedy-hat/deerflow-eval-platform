# 统一数据契约（建议 v1）

本文定义**平台自有接口**，不是 DeerFlow/Langfuse/DeepEval/AEF 任一 SDK 的直接 Python 类型。具体 SDK 调用以锁定版本核验后为准。

## 1. Case JSONL（一行一条）

```json
{
  "case_id": "support-001",
  "revision": "1",
  "scenario": "technical-troubleshooting",
  "input": {"message": "API 返回 401，如何排查？", "turns": []},
  "gold": {
    "required_facts": ["检查凭证有效性", "核对鉴权头格式"],
    "forbidden_claims": ["已替客户重置密钥"]
  },
  "assertions": {
    "required_tools": ["search_product_docs"],
    "forbidden_tools": ["reset_api_key", "modify_production_config"],
    "max_tool_errors": 0
  },
  "evaluation": {"deepeval": ["answer_relevancy", "faithfulness"]},
  "metadata": {"risk": "medium", "approved_by": "gold-reviewer", "dataset_revision": "2026-10-v1"}
}
```

`gold.required_facts` 是经业务审核的断言，不等同于完整参考答案。工具名须通过该版本 DeerFlow 的 observation 实际验证。

## 2. RunIdentity

```json
{
  "run_id": "uuid",
  "case_id": "support-001",
  "case_revision": "1",
  "attempt_id": "uuid",
  "correlation_id": "uuid",
  "agent_version": "deerflow-commit-sha",
  "prompt_version": "hash",
  "skill_versions": {"diagnose": "hash"},
  "rag_index_version": "index-snapshot",
  "dataset_revision": "2026-10-v1",
  "judge_version": "model-and-prompt-hash",
  "policy_hash": "sha256",
  "deerflow_trace_id": null,
  "langfuse_trace_id": null
}
```

**原则**：单个 Case 可以重试，因此 `attempt_id` 不等于 `run_id`；历史 `thread_id` 不应跨不同 case 混用。保存 trace 映射的来源与获取时间。

## 3. NormalizedTrace v1

```json
{
  "schema_version": "1",
  "correlation_id": "uuid",
  "trace_id": "actual-langfuse-trace-id",
  "complete": true,
  "final_output": "HTTP 401 通常表示鉴权未通过……",
  "events": [
    {
      "span_id": "actual-span-id",
      "parent_span_id": "parent-id",
      "module": "retriever",
      "action": "search_product_docs",
      "status": "success",
      "start_time": "2026-10-13T09:00:00Z",
      "duration_ms": 450,
      "error": null,
      "attributes": {"document_ids": ["doc-1"], "retrieval_query": "API 401"}
    }
  ],
  "retrieval_context": ["产品文档片段（脱敏）"],
  "usage": {"input_tokens": null, "output_tokens": null, "cost_usd": null}
}
```

事件基于 **Langfuse observation/span**，不同 DeerFlow 版本的字段必须由 adapter 显式映射；缺失信息用 null + completeness reason，不能虚构 step/tool。

## 4. CaseResult（评测输出）

```json
{
  "run_id": "uuid",
  "case_id": "support-001",
  "attempt_id": "uuid",
  "trace_id": "actual-langfuse-trace-id",
  "status": "PASS",
  "hard_violations": [],
  "scores": [
    {"metric": "answer_relevancy", "value": 0.9, "threshold": 0.8,
     "evaluator": "deepeval", "evaluator_version": "locked-version",
     "judge_model": "locked-model", "reason": "judge evidence saved separately"}
  ],
  "evidence_refs": ["object-store://eval/run/case"],
  "errors": []
}
```

`status`：`PASS`、`FAIL`、`INCONCLUSIVE`。Judge 异常、Trace 不完整、检索上下文缺失等不可验证情形为 `INCONCLUSIVE`；可观测的风险规则违规为 `FAIL`。

## 5. 对接层伪代码

```python
def evaluate_case(case, snapshot):
    handle = deerflow_client.run_case(case.input, snapshot, safe_tools=True)
    trace = trace_reader.wait_and_get(handle.correlation_id, timeout_s=60)
    normalized = normalizer.normalize(trace) if trace else None

    if normalized is None or not normalized.complete:
        result = inconclusive("TRACE_MISSING_OR_INCOMPLETE")
    else:
        hard_checks = business_rules.check(case.assertions, normalized)
        semantic = deepeval_runner.evaluate(case, normalized)
        result = aggregator.combine(hard_checks, semantic)

    result_store.save(result)  # source of truth
    score_outbox.enqueue(result)  # async retry, writes to Langfuse
    return result
```

这是接口顺序说明，非可运行 SDK 示例。业务规则中的“违规”与“缺证据”必须区分。

## 6. Langfuse 写回约定

- 每个 score 附 `run_id, case_id, attempt_id, metric, evaluator_version`（按部署 SDK 支持的字段编码）。
- 尽可能写至同一 Trace / Observation；如出自历史 replay 则加 `mode=rescore`。
- 上传前检查 `trace_id` 对应 identity；不可关联则保存到 outbox 待处理，禁止随意选择另一个 Trace。
- `metric` 命名分层：`answer.relevancy`, `rag.faithfulness`, `behavior.required_tools`, `business.safety_gate`。
- 同一次 `run+case+attempt+metric+evaluator_version` 幂等；若 Langfuse API 不支持原生幂等，由平台自己的发送台账去重。
- 不把 LLM judge 的不确定结论映射为确定性的高风险硬门禁。

## 7. AEF 适配（有授权才启用）

AEF 的 `ProjectAdapter` 提供 `call_agent`、`read_trace`、`hard_gates` 和 `soft_quality`。Langfuse 的 NormalizedTrace v1 再映射到**已固定 AEF 版本**的 `agent_eval.NormalizedTrace`，不能假设两者字段/构造函数相同。单独做契约测试。

AEF 示例/文档入口：[README](https://github.com/Lin-chpin/agent-evaluation-framework)；需遵守 PolyForm Noncommercial 授权限制。
