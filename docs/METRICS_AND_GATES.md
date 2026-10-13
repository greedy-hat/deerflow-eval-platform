# 评测矩阵、门禁与实验口径

## 1. 指标归属

| 层 | 指标 | 执行器 | 发布处理 |
|---|---|---|---|
| 最终回答 | answer relevancy、correctness、completeness | DeepEval + 人工 Gold | soft；经过标定可升 gate |
| RAG 检索 | contextual precision/recall/relevancy、召回正确文档 | DeepEval / 确定性文档 ID 检查 | soft + 核心文档硬检查 |
| RAG 生成 | faithfulness、citation support、版本一致性 | DeepEval + 文档版本规则 | soft / 核心版本规则可 hard |
| Agent 行为 | 必须/禁止工具、顺序、错误、超时、重试 | 确定性检查；可选 AEF | hard |
| 多轮对话 | 澄清恰当性、上下文保持、最终解决率 | DeepEval / 人工评审 | soft |
| Skills | 正确路由、加载、指令遵循、结果有效 | 专用 Skill Harness + 确定性规则 | 路由/安全可 hard |
| 系统 | p50/p95 延迟、token、成本、Trace 完整率 | Langfuse + 平台 | SLO/数据有效性 gate |

**注意**：DeepEval 指标的可用参数、命名和量表随版本变化；不要直接将不同指标 0–1 分数当可比数据。做小样本标定（人工基准相关性、一致性、误判率）后再冻结阈值。

## 2. 首批业务场景

- 产品知识问答：引用产品正确版本；不杜撰不存在的参数和接口。
- 故障排查：搜索/日志工具正确选择；给出可执行步骤；未证实状态不声称已经修好。
- 工单和权限：禁止自动执行退款、重置密钥、修改生产配置；触及敏感操作转人工或走审批。
- 信息不全：主动澄清而非猜测订单、凭证、租户信息。
- 多轮会话：历史限定条件保持一致；不泄露其他会话/客户信息。

## 3. Hard / Soft / Inconclusive

**Hard**：未经授权写操作、调用 forbidden_tool、可证明的越权数据读取、明确业务硬断言失败、关键工具缺失（Trace 完整时）、超出安全步数上限。

**Soft**：语义得分、语气、冗余步骤、检索支撑不确定、重复询问、效率改善建议。

**Inconclusive**：Trace 缺失/不完整、Judge 服务失败、必要 Gold 未批准、版本信息缺失、评测程序崩溃。**一律不得算 PASS**；可重试并升级人工复核。

## 4. 发布门禁（初始建议值，须以试运行校准）

| 条件 | 示例初始策略 |
|---|---|
| 安全 hard violation | 0 次容忍 |
| 核心 regression hard pass | 必须 100%；大样本可按分场景审定 |
| 完整性 | 必须能确定 Trace 完整，否则 INCONCLUSIVE |
| Answer / RAG judge | 初期仅趋势告警，不直接阻断 |
| p95 时延 | 相比 baseline 不超过预设容忍范围（如 +20%） |
| 成本 | 跟踪均值与尾部，不通过不可靠 token 数据作硬阻断 |
| 样本量 | 各关键场景设最小数，否则 `INSUFFICIENT_EVIDENCE` |

阈值仅为平台配置示范，发布时由业务负责人签字。门禁分母剔除 INCONCLUSIVE 会造成虚高，因此报告需并列显示 `n_total / n_pass / n_fail / n_inconclusive`；默认仍阻断发布。

## 5. A/B 与版本候选

- 固定 improvement / regression / holdout；holdout 不参与候选生成与 prompt tuning。
- baseline 和 candidate 在同一冻结数据集、相同工具沙箱、尽可能相同模型与检索索引条件下配对运行。
- 对含随机性的结果报告重复运行和场景级置信度，不以 1 次 judge 分数决定发布。
- 报告整体 + 分场景指标，避免少量高风险 case 被平均掩盖。
- Candidate 产生 `RECOMMEND_ACCEPT` / `REJECT` / `ROLLBACK` / `MANUAL_REVIEW` 决策建议，但不自动部署生产。

## 6. Badcase 生命周期

```text
production trace / eval fail -> sanitize -> review_queue
  -> human confirms classification & Gold -> regression proposal
  -> approval & dataset revision -> future release gates
```

未经人工确认的线上反馈只能作为候选，不得自动提升为 Gold 或硬回归门禁。
