# 架构设计与职责边界

## 1. 场景与目标

面向 DeerFlow 2.0 构建的**客户技术支持 Agent**：产品知识问答、故障排查、多轮澄清、工具调用、工单建议、Skills 路由。目标是回答三个问题：

1. 这个版本是否给出了正确、安全、有依据的答案？
2. 它是否采用了正确的检索与工具路径，并且未执行禁止操作？
3. 相比基线版本是否改善，同时没有破坏历史核心能力？

## 2. 推荐服务模块（渐进式实现）

```text
                       Git/CI triggers       Manual / scheduled
                               \                 /
                                Eval API / CLI
                                      |
                             Evaluation Orchestrator
                         (queue/retry/timeout/idempotency)
                          /           |              \
                 Dataset catalog   Run registry    Policy registry
                   (Langfuse)      (Postgres)       (versioned Git)
                          \           |             /
                                   Execution worker
                                         |
                                 DeerFlow 2.0 API
                                         |
                  Langfuse <---- OTel/callback instrumentation
                      |
                Trace reader + normalizer
                      |
          +-----------+-----------+-------------------+
          |                       |                   |
  Business rules            DeepEval worker      AEF adapter*
 (pure deterministic)       (semantic + RAG)   (behavior + release)
          +-----------+-----------+-------------------+
                      |
             Result aggregator -> Case/report/audit store
                      |
          Langfuse score writer + CI release gate + reviewer
```

`*` AEF 仅在商业授权、隔离评估和兼容性验证后启用。禁用 AEF 时基础评测与规则引擎仍须可工作。

**不要一开始就建设大型 Web 控制台。** P0 用 Python CLI + JSON 报告 + Langfuse UI；P1 引入持久任务/业务审核；P2 视人员使用情况再做 Web UI。

## 3. 组件所有权（禁止双写）

| 对象 | 权威存储 | 其他投影 |
| --- | --- | --- |
| 数据集内容/版本 | Langfuse Dataset version / 平台冻结快照与内容 hash | Git 导入导出 |
| Gold 与业务审核记录 | 平台 DB（批准的 case revision） | Langfuse metadata |
| 在线 Trace/Observation | Langfuse | 报告保存 trace_id 与摘要 |
| Run 生命周期、attempt、错误 | 平台 DB | Langfuse Experiment metadata |
| 分数原始明细与 judge 证据 | 平台 DB / object store | Langfuse Scores |
| 门禁策略及版本 | Git | DB 的 policy hash |
| 人工结论和发布决策 | 平台 DB | Langfuse tags/metadata（可选） |

**一致性**：`case_id`、`case_revision`、`run_id`、`attempt_id`、`langfuse_trace_id`、`deerflow_trace_id`、`agent_version` 必须可追踪；写回失败通过 outbox 重试，不删除原始报告。

## 4. 在线执行 vs 离线重评分

- **Fresh run**：固定版本和输入，通过 HTTP/SDK 调用 DeerFlow 2.0；采集真实执行的新 Trace；用于 smoke/regression/full/候选比较。
- **Replay/rescore**：对已经存在的 Langfuse Trace 进行重新评估，不代表候选版本重新执行；用于线上 badcase 探索、Judge 标定。
- **Consistency**：同一冻结版本多次独立运行，展示变异率与置信区间；不把天然随机性直接视为错误。

## 5. DeerFlow 2.0 接入策略

优先使用所部署版本已有的 Langfuse/Tracing 能力和服务 API。版本适配层分别负责：

- `DeerFlowClient.run_case()`：传入用户请求、会话/租户/测试身份，收集最终输出及执行句柄，实施真实超时与取消。
- `TraceReader.wait_and_get()`：通过 trace_id / metadata 检索、等待 span 完整及 flush（有上限）；聚合 Trace。
- `TraceNormalizer.normalize()`：按 span 的类型/名称/metadata 映射 lead_agent/subagent/retriever/skill/tool/LLM，保留原始 span IDs。
- `ScoreWriter`：仅对可信 trace_id 写 Score；重试与幂等 `run_id + case_id + metric_name + evaluator_version`。

不能假定 DeerFlow 内部 ID 与 Langfuse trace ID 完全一样；需用独立的 `correlation_id` 双向映射。技能是否加载、是否执行、RAG 文档命中等数据如果 Trace 中没有，应补充**版本兼容的显式 instrumentation**，不能推断为已发生。

## 6. 安全与权限

- 专门的 Eval Tenant、只读/Mock 工具、独立测试检索索引和工单服务；高风险动作必须阻断。
- 生产 Trace 脱敏：客户身份、联系方式、密钥、合同数据等字段屏蔽或抽样后入库。
- RBAC：viewer、evaluator、gold_reviewer、release_approver、admin；业务 Gold 审批人与候选提交人分离。
- 明确 retention、访问审计、审计不可篡改存储与数据删除流程。
- 任何候选 Prompt/Skill 不自动写入生产；发布必须业务方/CI 审批。

## 7. 演进与部署

**P0**：本地 Python 进程 + Langfuse + 文件 JSON 报告。**P1**：FastAPI + PostgreSQL + Worker/queue + 对象存储 + outbox。**P2**：多团队租户隔离、权限和控制台、容量与 SLO。不要把未来组件写成第一周的前置依赖。
