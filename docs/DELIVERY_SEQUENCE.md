# 分步实施（基于已定义的完整目标架构）

本文件只决定**执行顺序与验收工单**，不是阶段式架构设计。九大模块及模型、接口先由 [完整设计](MASTER_DESIGN.md) 一次性定义；任何新增需求优先在统一契约中登记变更再施工。

| 实施批次 | 交付的纵向能力 | 依赖 | 完成判据 |
|---|---|---|---|
| 0 架构冻结 | 九模块 ADR、Schema、OpenAPI、状态机、DB migration、策略及部署设计、授权决策 | 业务场景 / 实际版本 | 评审通过，无悬空跨模块字段 |
| 1 运行与证据 | CLI/API 创建 run → DeerFlow fresh run → Langfuse Trace → NormalizedEvidence → DB/报告 | 批次 0 | Trace 双 ID 关联；错误/不完整必为 INCONCLUSIVE |
| 2 评测器闭环 | DeepEval + AEF 实际行为评测插件 + 自有 Business Rules + Skills Harness 契约 → ResultAggregator → Langfuse Score | 批次 1 | 30–50 Gold；高风险工具失败；语义分数回写 |
| 3 专项评测 | RAG 检索/生成分测、多轮、Skills 路由/加载/执行 + 覆盖率 | 批次 2 | 各场景可独立跑并关联 Trace |
| 4 回归与发布 | Baseline/candidate、improvement/regression/holdout、场景级 gate、Badcase 审核 | 批次 2–3 | 故意退化候选阻断 |
| 5 AEF 高级能力完善 | 扩展首批已集成的 AEF：回归、evolve、并发测试与审计 | 批次 2–4 | 契约测试通过；可在开关关闭下独立运行 |
| 6 运营与扩展 | Web Console、RBAC、审计、CI/CD、队列治理、压测 | 批次 1–5 的稳定契约 | 全链路权限/恢复/安全与性能验收 |

### 重要区别

- **从开始就画出并定义 AEF 和 Skills 的接口**，而不是在第 5 批才决定它们如何加入。
- **批次可以并行**：Schema/API 与页面原型可并行；DeepEval、AEF 契约测试、Skills Harness 的实现可并行。
- **先写接口、再接真实系统**：不要求全部功能一次开发完成，但不能用临时字段、私有直连和不可迁移的 POC 结构。
- **使用范围**：当前个人非商业用途可以依许可证接入 AEF，未来转商用时再确认授权。
- 每批必须提供可审计的端到端证据，不以文档代替代码验收。

### 推荐首批执行工单

1. 冻结 DeerFlow/Langfuse/DeepEval/AEF 接口与版本矩阵，确认 AEF 许可证；
2. 完成 PostgreSQL schema、`EvaluationCase/EvaluationRun/NormalizedEvidence/EvaluationScore` Python model 与 OpenAPI；
3. 定义五类 port：`AgentExecutionPort`, `TracePort`, `EvaluatorPort`, `AEFPort`, `SkillEvaluationPort`；
4. 实现一条 HTTP → Trace → Score 真实执行闭环；
5. 固定自动化契约测试，确保后续模块直接按终态协议实现。

架构关联：[ARCHITECTURE](ARCHITECTURE.md) · [CONTRACTS](CONTRACTS.md) · [METRICS](METRICS_AND_GATES.md) · [ACCEPTANCE](ACCEPTANCE_AND_RISKS.md)。
