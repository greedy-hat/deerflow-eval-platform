# 验收、测试与风险

## 1. 各阶段验收

| 阶段 | 最小验收标准 |
|---|---|
| P0 | 单条 DeerFlow 2.0 请求关联到 Langfuse trace + tool spans + final output |
| P1 | 30–50 条真实/脱敏用例可执行；结果含 PASS/FAIL/INCONCLUSIVE；DeepEval 输出、规则结果及 Langfuse Scores 可关联 |
| P2 | 数据/版本/Prompt/Skill/Judge/索引可追溯；历史回归与 holdout 独立；badcase 审核流程存在 |
| P3 | AEF 从首批作为正式插件接入并可通过 feature flag 控制；候选触犯禁用工具或回归集时 release 阻断 |
| P4 | CI/审批/权限/审计、消息重试与恢复、脱敏与隔离验收通过 |

## 2. 必备自动测试

- Contract：DeerFlow 响应模型变化、不同 Langfuse observation 映射、同一次运行多个 subagent、缺 tool span、延迟最终 flush。
- Functional：必需工具未调用、禁用工具被调用、上下文引用不足、无 Gold、Judge 异常。
- Safety：真实写工具被 Mock、禁止外网/生产凭证、越权客户数据、敏感数据脱敏。
- Idempotency：同一个 Case 重试；Score 写回超时/重复；报告在重启后恢复。
- Release：基线/候选的 regression 退化、holdout 被污染、样本不足、INCONCLUSIVE 时门禁必须不放行。
- Quality：Judge 与人工小样本双盲一致性；抽样人工审查 false positive/negative。

## 3. 上线阻断风险清单

| 风险 | 后果 | 控制措施 |
|---|---|---|
| AEF PolyForm Noncommercial 许可证 | 商用不合规 | 个人非商业使用遵守许可证；未来商用另行确认授权 |
| DeerFlow 2.0 / Langfuse 版本差异 | Span 与 ID 对不上 | 锁定 Git SHA / SDK 版本，契约测试 + 显式 correlation mapping |
| Trace 异步写入、部分缺失 | 误判工具未调用 | 有界等待 + `INCONCLUSIVE` + replay/重试 |
| Judge 不稳定/偏见 | 误阻断、虚假提升 | 人工标定，多次评估，语义指标先 soft |
| 测试作用于生产写工具 | 数据/业务事故 | Eval tenant、Mock、只读凭证与禁止动作 policy |
| 生产数据/Prompt 泄露 | 合规风险 | 脱敏、最小权限、保留期与日志审计 |
| 版本漂移 | 结果无法复现 | 记录 Case/模型/Skill/RAG/Prompt/Policy 的 content hash |
| 多系统双写 | 指标矛盾 | 明确权威存储；outbox 幂等写回 |
| 样本代表性不足 | 假阳性上线 | 高风险分场景样本下限与 holdout |

## 4. 对外接口的验收证据

每次验收产生：执行命令及配置（去密）、固定版本清单、用例 hash、执行 Trace URL / ID、result JSON、Score 写回记录、Reviewer 签名/审计记录及 CI 门禁状态。无 Trace 或无业务 Gold 的测试不能被描述为“全面通过”。

## 5. 未开始实施的事项

本文仓库是**实施方案**而非可运行平台：没有部署环境、API token、真实 DeerFlow 2.0 endpoint、已批准 Gold、AEF package。开始开发时先补齐这些输入；严禁凭示意 Schema 宣称已打通真实 API。
