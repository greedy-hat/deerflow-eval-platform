# DeerFlow 2.0 评测平台：完整目标设计（设计一步到位）

> 设计状态：目标架构完整定义，实际代码按依赖增量交付。**实施顺序不代表某个组件在架构中被推迟设计。**

## 一、建设目标和原则

构建面向客户技术支持的完整评测平台，统一管理 Agent、SubAgent、RAG、Skills、Tools、多轮对话和发布回归。固定四项基础技术：**DeerFlow 2.0（被测系统）、Langfuse（可观测及实验投影）、DeepEval（语义与 RAG）、Agent Evaluation Framework / AEF（行为、回归、演化）**，另设独立 Skills Harness 和确定性业务规则。

- 完整设计一次冻结：模块边界、领域对象、数据契约、运行状态机、API、DB schema、事件流、CI gate、权限和非功能要求。
- 开发按纵向闭环切片：每批均落入终态架构，不搭建需要重写的“临时架构”。
- AEF 与 DeepEval 并列在统一 Evaluation Engine 内；AEF 与 DeepEval 同级且首批正式接入；当前个人非商业使用，遵守 PolyForm Noncommercial 条款，若未来转商用则重新确认授权。
- 不允许“评测通过”等于“可上线”：只有经审批的 Gold、完整 Trace、硬门禁和证据支持才可进入发布决策。

## 二、终态逻辑架构

```text
Web Console / REST API / CLI / CI-CD
                 |
       Evaluation Orchestrator
      (state machine + job queue)
                 |
     Run Registry / Policy / Dataset
                 |
          Execution Gateway
        /                  \
 DeerFlow 2.0 Adapter    Langfuse Adapter
 (Agent/SubAgent/Skills/ (Trace/Span/Dataset/
  RAG/Tools)              Experiment/Score)
        \                  /
           Normalized Evidence
                 |
     Evaluation Engine (parallel plugins)
       |           |            |
     DeepEval    AEF Port     Skills Harness
 (RAG/semantic) (behavior/    (routing/loading/
                 regression/   adherence/outcome)
                 evolution)
       \            |            /
       Business Assertions (independent hard checks)
                 |
          Result Aggregator
       /         |            \
   Case Report  Badcase     Version Comparison
       \         |            /
     Review, Policy & Release Gates
                 |
    PostgreSQL + Object Storage + Langfuse
```

## 三、九大模块设计清单（全部从开始纳入）

| 领域模块 | 长期职责 | 最小对外契约 |
|---|---|---|
| 1. Dataset & Gold | 数据集导入、不可变 revision、业务审核、场景分桶 | `DatasetService` |
| 2. Execution Gateway | deer-flow 调用、线程隔离、Mock/沙箱工具、超时与取消 | `AgentExecutionPort` |
| 3. Observability | Trace 查询/完整性/关联、Observation 结构归一化、Score 写回 | `TracePort`, `ScorePort` |
| 4. Evaluation Engine | 调度评测器、规范化执行证据和评测状态 | `EvaluatorPort` |
| 5. DeepEval Plugin | 答案/RAG/多轮 Judge、rationale、版本留痕 | `SemanticEvaluator` |
| 6. AEF Plugin | required/forbidden tools、回归、evolve、门禁证据 | `AEFPort` |
| 7. Skills Harness | 触发、加载、遵循、结果、对抗场景 | `SkillEvaluationPort` |
| 8. Results & Governance | 聚合、复核、Badcase、对比、发布审批 | `ReportPort`, `ReleaseGatePort` |
| 9. Platform Foundation | API/Web、持久队列、DB、RBAC、审计、存储、安全 | `RunRepository`, `AuditPort` |

每个模块都从第一天有独立协议、替身测试和明确 ownership；真实 adapter 可以依次接通。

## 四、统一领域对象和不可变标识

- `EvaluationCase`: case_id、revision、scenario、input、gold、assertions、evaluator plan、metadata、approval。
- `DatasetRevision`: dataset_id、revision、case hashes、approval、来源。
- `EvaluationRun`: run_id、suite、mode（fresh/replay）、status、环境、版本快照、policy_hash、时间。
- `CaseAttempt`: attempt_id、case_id、run_id、attempt_index、agent execution handle、trace mappings。
- `TraceReference`: correlation_id、deerflow_trace_id、langfuse_trace_id、span ids、completeness。
- `NormalizedEvidence`: final answer、events、retrieval context、tools、Skills、usage、error、source refs。
- `EvaluationScore`: evaluator_id/version、metric、value、threshold、confidence/reason/evidence、judge identity。
- `CaseVerdict`: PASS/FAIL/INCONCLUSIVE、violations、review_required。
- `ReviewDecision`: reviewer、decision、gold revision、reason、timestamp。
- `ReleaseDecision`: baseline/candidate、scenario gates、decision、approver、audit references。

追踪键：`run_id + case_id + revision + attempt_id`；与 Langfuse ID 显式映射，不能假定两种 trace_id 相同。

## 五、任务状态机

```text
CREATED -> VALIDATED -> QUEUED -> RUNNING -> COLLECTING_TRACE
          -> EVALUATING -> AGGREGATING -> REVIEW_PENDING? -> COMPLETED
                                                    |
                                        FAILED / INCONCLUSIVE / CANCELLED
```

失败与不确定性区分：业务规则已证实违反为 FAIL；不可得 Trace/Gold、模型 Judge 不可用、API 超时导致无法裁判为 INCONCLUSIVE；两者默认都不能放行发布。每次重试新 `attempt_id`，不得覆盖证据；评测器结果按 `run/case/attempt/evaluator/version` 幂等保存。

## 六、终态持久化和边界

建议 PostgreSQL 表：`datasets`, `dataset_revisions`, `cases`, `gold_reviews`, `runs`, `case_attempts`, `trace_references`, `evaluator_runs`, `scores`, `case_verdicts`, `review_decisions`, `candidate_comparisons`, `release_decisions`, `policies`, `audit_events`, `outbox_events`。大文本、检索片段和日志证据进 S3/MinIO（加密、TTL、hash）；Langfuse 是 Trace/Experiment/Score 可视化投影，不代替发布审计库。Dataset 的权威 revision 按 [ARCHITECTURE.md](ARCHITECTURE.md) 定义统一。

建议 API：`POST /datasets/import`、`POST /runs`、`GET /runs/{id}`、`GET /runs/{id}/cases`、`POST /runs/{id}/cancel`、`POST /reviews`、`POST /comparisons`、`POST /release-decisions`；定义 OpenAPI，鉴权使用 RBAC。Web UI 从同一 API 取数据，不直接写数据库。

## 七、评测策略与发布控制

评测策略是版本化配置：每个 scenario 决定执行哪套 DeepEval、AEF、Skills、确定性规则，权重只用于展示质量综合分，**高风险 hard violation 不允许被平均分抵消**。

- `smoke`：核心冒烟；`regression`：历史问题保护；`full`：全量代表性数据；`holdout`：候选未见过的数据。
- 同批运行 baseline/candidate，保留每个 case 的差异和证据，输出 accept/reject/rollback/manual-review 建议。
- 软语义分数在完成 Judge 与人工标定前只作为告警；硬门禁仅基于可靠确定性事实与批准规则。
- 自动化流程不得修改生产 Skill/Prompt/配置；发布审批为独立权限。

## 八、安全、可靠性与可运维性

专用评测租户、工具 deny-by-default、敏感工具替身、最小权限、脱敏、留存期、审计；任务队列重试与死信、Trace 延迟/丢失显式告警、结果写回 outbox、执行证据 hash、日志指标监控、环境/成本预算、SLO。需要验证具体 DeerFlow 2.0 和 Langfuse SDK 版本的真实采集细节，不能仅据概念设计假设接口已经存在。

## 九、完成定义：设计交付与工程交付分离

**设计完成**：以上九模块边界，schema/OpenAPI、状态机、策略接口、非功能约束、安全模型、部署图、验收用例均经过评审并版本冻结。

**工程完成**：代码、单元/契约/集成/安全测试、真实 Trace/DeepEval/AEF 端到端证据、部署脚本和 CI gate 全部通过。两者绝不混称。
