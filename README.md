# DeerFlow 2.0 Evaluation Platform（实施方案）

基于 **DeerFlow 2.0 + Langfuse + DeepEval + agent-evaluation-framework（受控引入）** 的客户技术支持 Agent 评测平台。

> **状态：设计方案 / 尚未实现生产级集成。** 本仓库当前保存实现蓝图、接口契约和验收计划，不宣称已完成 DeerFlow、Langfuse、DeepEval 的端到端集成。

## 定位

- **DeerFlow 2.0**：被测系统（Lead Agent、SubAgent、Skills、RAG、Tools）。
- **Langfuse**：Trace/Span 可观测、Dataset/Experiment 管理、质量分数可视化。
- **DeepEval**：最终回答质量、RAG 相关性/忠实性、语义评判与多轮能力评测。
- **agent-evaluation-framework（AEF）**：工具行为与确定性规则、历史回归、版本候选比较和发布门禁；只有许可证审核通过后才引入代码或运行于商业环境。
- **本平台**：最薄的编排层、身份映射、业务 Gold、结果归一化、人工复核和发布决策；避免重做四个项目已有的功能。

## 设计与实施的关系

**最终架构一次性完整设计，工程按照模块依赖分步施工。** [完整目标设计](docs/MASTER_DESIGN.md) 从一开始包含 AEF、DeepEval、Skills Harness、发布门禁与平台治理；[分步实施清单](docs/DELIVERY_SEQUENCE.md) 只是交付顺序，不能理解为后续阶段才考虑 AEF。商业使用 AEF 仍须先取得相应授权。

## 文档导航

1. [完整目标设计（九模块 / 状态机 / 数据模型）](docs/MASTER_DESIGN.md)
2. [分步实施任务（同一架构下逐批交付）](docs/DELIVERY_SEQUENCE.md)
3. [总体架构与边界](docs/ARCHITECTURE.md)
4. [原始详细实施任务参考](docs/IMPLEMENTATION_PLAN.md)
5. [数据契约、示例与适配器](docs/CONTRACTS.md)
6. [评测指标与发布门禁](docs/METRICS_AND_GATES.md)
7. [验收标准与风险](docs/ACCEPTANCE_AND_RISKS.md)
8. [示例用例](examples/support_cases.jsonl)

## 端到端目标

```text
Versioned Dataset / Gold
          |
          v
Eval Orchestrator -> DeerFlow 2.0 (isolated test tenant)
          |                  |
          |                  v
          |             Langfuse Trace + Spans
          |                  |
          +---- normalize <-+
          |         |
          +--> DeepEval (semantic/RAG)
          +--> deterministic business checks
          +--> AEF (behavior/regression/release, licensed + enabled)
          |
          +--> normalized results + review queue + evidence
          +--> Langfuse Scores / Experiment
          +--> CI gate (only verified hard assertions)
```

**双向关联**：执行产生 Langfuse Trace；评测通过 `trace_id`/关联 ID 读取并将 Scores 写回。离线历史 Trace 评分不等同于针对新版本的 fresh-run 回归。

## 设计原则

1. **可信发布**：未采集到必要 Trace、工具执行不完整、Evaluator 异常时标记 `INCONCLUSIVE`，不能按通过处理。
2. **数据主权**：Gold 由业务方审核；Dataset/Experiment 优先使用 Langfuse；评测平台持久化运行状态、版本快照、审计和门禁决策。
3. **隔离执行**：线上客服数据脱敏；写操作禁用或导向沙箱/模拟服务；禁止在评测环境触达真实退款、工单变更或生产配置修改。
4. **可复现**：固定 DeerFlow 版本、Prompt/Skill/索引/模型版本、Dataset revision、Judge 配置和阈值。
5. **受控引入 AEF**：在许可证审批之前，只实现自有适配器及确定性断言接口，不复制或安装其代码用于商业业务。

## 首个可交付 POC

`support-001`：用户询问技术产品接口报错原因。自动运行 DeerFlow；Langfuse 得到 Trace；DeepEval 评估最终回答与检索支撑；规则检查规定工具与禁用动作；将结果关联写回 Langfuse，并导出 Case 报告。如果没有 trace/评测不可用则结果为 `INCONCLUSIVE`。

详见 [实施计划](docs/IMPLEMENTATION_PLAN.md) 与 [验收标准](docs/ACCEPTANCE_AND_RISKS.md)。

## 来源 / 依赖

- [DeerFlow](https://github.com/bytedance/deer-flow)
- [Langfuse](https://langfuse.com/docs)
- [DeepEval](https://docs.confident-ai.com/)
- [Agent Evaluation Framework](https://github.com/Lin-chpin/agent-evaluation-framework) — **PolyForm Noncommercial，商业使用需另行授权**

本仓库**不包含**任何上游 AEF 代码或其衍生文件。依赖版本和 API 在正式编码前须按实际部署的 release 锁定与核验。
