# 详细工程任务（历史 Phase 命名保留作任务分组）

> **规范入口已更新**：[完整目标设计](MASTER_DESIGN.md) + [分步实施](DELIVERY_SEQUENCE.md)。本文件出现的 Phase 仅表示施工任务分组，**不是分阶段设计架构**；AEF/DeepEval/Skills 等接口从设计开始就完整定义。


> 所有时间为**建议工程阶段**，不是实际已完成承诺。依赖目标 DeerFlow 2.0 部署版本、模型服务、Langfuse 版本、业务工具权限以及 AEF 商业授权。

## Phase 0 — 基线核对与依赖冻结

**工作**：记录 DeerFlow commit/tag 与 API；验证其 Langfuse tracing 集成范围；锁定 Langfuse Python SDK、DeepEval、Python 版本；确认评测用具（只读/Mock）与测试租户。

**交付**：版本矩阵、环境变量模板、最小一条真实 DeerFlow Trace、工具 span 清单、许可证审核记录。

**Exit**：能把一次请求的 `thread_id` / `deerflow_trace_id` 与 Langfuse `trace_id` 关联；可获取最终答案与工具 span。若没有则先修 instrumentation。

## Phase 1 — 最小闭环 POC（最高优先级）

1. 实现 `DeerFlowClient`：HTTP/SDK 调用、幂等 case token、超时取消、禁用写操作。
2. 实现 `LangfuseTraceReader`：有界轮询、错误分类、缺失 Trace 失败关闭（fail closed）。
3. 实现 `TraceNormalizer`：事件类型/步骤/工具/检索结果/最终输出/错误/耗时；留原 span id。
4. 实现 `DeepEvalRunner`：答案相关性、忠实性、context relevance 等选用评测；分离检索和生成；保留 judge rationale 与 evaluator model/version。
5. 实现 `BusinessRuleEvaluator`：必需/禁止工具、顺序、业务事实和未授权动作。
6. 实现 `ScoreWriter`：按 case/metric 关联 Langfuse Trace 和 Experiment；重复写入不产生无法分辨的分数。
7. 一个命令运行 30–50 条分层用例；输出 `results.json`、`summary.json`、`review_queue.jsonl`。

**Exit**：三种结果 PASS/FAIL/INCONCLUSIVE；Trace 缺失不能 PASS；至少一个必需工具失败与一个检索无依据案例可复现；Langfuse 对照到原 Trace。

## Phase 2 — 回归资产与可复现实验

1. 确认 JSONL schema，按场景管理 `smoke`/`regression`/`full`。
2. Case 内容不可变 revision + SHA256，人工 Gold 业务审批；禁止把产出答案自动当 Gold。
3. Run snapshot：agent/prompt/skill/tool policy、RAG index、LLM/judge、dataset revision、阈值、Git SHA。
4. 按多轮会话（turns）运行，确保会话内串行/不同 case 隔离。
5. 运行统计：按场景 hard pass、分数分布、成本、延迟、token、样本量、区间估计。
6. 引入 `baseline` vs `candidate` paired comparison（相同 case、近似环境）；保留稳定回归集与独立 holdout。
7. Badcase → 人工复核 → 分类 → 回归集提案；提交 Gold 必须审批。

**Exit**：重复执行同一 revision 可定位版本与证据；强制回归可阻断显著退化；人工待审核不被当作已确认失败或 Gold。

## AEF 高级能力扩展（基础行为评测在首批接入）

**使用范围**：当前个人非商业使用 AEF，保留 PolyForm Noncommercial 条款；未来转为商业用途需重新确认授权。

适配：`ProjectAdapter.call_agent(case, context)` 调用 DeerFlow；`read_trace(handle, case)` 从 Langfuse 转成 AEF 的 `NormalizedTrace`；`hard_gates` 负责可决定性的业务风险规则，`soft_quality` 负责告警。

- 适配 `metadata.behavior_evaluators`：required/forbidden tools、call order/count、tool errors。
- 发布流水线 `regression → smoke → full`（保护集失败即阻断）。
- `evolve`：improvement / regression / holdout；只输出 accept/reject/rollback 建议和审计，不部署候选。
- 将 AEF 报告统一归一化为平台 CaseResult，附原文件哈希；上传对应 Langfuse Score。
- 加契约测试：事件顺序、未知 spans、错误、trace 重试、超时和高风险操作。

**Exit**：一个故意违反禁用工具规则的候选被拒绝；历史能力退化导致发布阻断；关闭 AEF feature flag 时 Phase 1–2 正常运行。

## Phase 4 — 持久化/CI/治理

引入 DB/异步队列/outbox、审计、RBAC、发布审批、定时生产抽样（脱敏）、CI 状态回传。仅在真正需要时加独立 UI。CI 中必须区分业务规则 FAIL 与服务不可用 INCONCLUSIVE，默认两者都不能放行。

## 推荐代码目录（未来实现，不代表已存在）

```text
src/deerflow_eval/
  api/                 # FastAPI (P4)
  cli.py               # 单命令 eval run
  models.py            # 统一领域契约
  integrations/
    deerflow_client.py
    langfuse_trace.py
    langfuse_scores.py
    deepeval_runner.py
    aef_adapter.py      # 首批接入
  evaluators/
    business_rules.py
  orchestration/
    runner.py
    registry.py
    gates.py
  reporting/
    json_report.py
tests/
  fixtures/
  unit/
  contract/
  integration/
```

## 第一批工单拆分建议

1. 环境与 trace 字段核验（DeerFlow→Langfuse）。
2. 统一 `Case`/`Run`/`NormalizedEvent`/`Score` schema。
3. Trace reader + 超时与错误态。
4. DeepEval wrapper（独立 Judge 配置）。
5. Deterministic hard rules + 禁止工具校验。
6. Langfuse Score Writer。
7. 一键 CLI 和报告。
8. 脱敏、人工标注和 30–50 条 Gold 数据。
9. 基线/候选实验、regression gate。
10. AEF 适配与进阶版本回归功能。

详见 [接口契约](CONTRACTS.md)、[指标和门禁](METRICS_AND_GATES.md)、[验收与风险](ACCEPTANCE_AND_RISKS.md)。
