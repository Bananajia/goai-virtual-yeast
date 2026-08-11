# 2026-08-10 虚拟细胞方向头脑风暴会：报告查漏补缺记录

来源：[腾讯会议回放](https://meeting.tencent.com/cw/NQBBbEoZd5)，会议名“GOAI虚拟细胞方向头脑风暴会”，时长约 1 小时 24 分。核对日期：2026-08-10。

## 证据边界

本记录逐段核对平台逐字稿与正式技术报告。逐字稿由平台自动生成，可能存在术语识别错误；会议属于技术交流，不能替代组委会书面规则、机器可读 submission template 或正式评分脚本。下面只记录可追溯的时间段、技术含义、当前覆盖情况和项目决定，不保存逐字稿全文。

## 增量核对

| 时间段 | 会议技术要点 | 项目已有证据 | 处理决定 |
|---|---|---|---|
| 01:23–02:17 | one-hot 无法表达新菌株或新药之间的相似性；新药需要 SMILES 等描述符 | whole-chemical MLP、结构 Transformer、靶点到 STRING 及结构泛化实验均已完成 | 保留结论：身份编码不足；外部表示必须通过 whole-drug 与错配负对照 |
| 04:54–05:14 | 口头提到开放/封闭知识可能合并，但同时要求等待官方通知 | 报告原有两套运行配置 | 改为“内部消融配置”，不声称官方存在两个榜单 |
| 08:12–08:47 | 任务是 zero-shot；需检查模型是否只回到平均值 | 均值 baseline 的条件方差为 0，逐蛋白 R² 为负 | 新增 MSE 条件均值的数学解释 |
| 17:20 左右 | 讨论 Huber 与高变化蛋白 | 已有多目标/高响应 pilot；后续同模型损失消融已完成 | 明确 Huber 是对大预测误差稳健化，不等于给大真实响应加权；Huber 退步，固定 $4\times$ 响应加权有信号但未过 RMSE/VR/排名联合门槛，全局保留 MSE |
| 23:22–26:56 | matched control 与同药物残差的聚合较复杂 | 已实现显式 measured-control、共同掩码和 fit-frozen residual | 将现实现称为“保守内部合同”，不冒充未公开的官方聚合公式 |
| 27:28–28:14 | 当前两种培养基主要按已给类别区分 | metadata encoder 把培养基作为类别变量 | 明确不声称能外推任意培养基配方 |
| 35:35–36:34 | NA 不是零；相减、PCC、R² 需共同有效掩码 | pipeline/evaluator 已保留 NA 并禁止填零 | 在正文补充 NA 的实验含义，并要求预测不得用 NaN 选择性跳过困难坐标 |
| 42:51–43:04 | 参赛者提交预测，matched control 由评测端准备 | submission contract 只接 Endpoint prediction | 在提交合同中明确不额外提交 matched-control 向量 |
| 43:13–47:25 | 建议 CPA/chemCPA；先做相似药物统计基线 | 已完成全 37 药物的 Tanimoto、CPA-style 加性、低秩双线性交互，以及两版非线性组合实验；22 个有严格结构，15 个显式 missing/fallback | 线性三分支均未通过 all-ITT 联合门槛；非线性 v1 仅作实测对照条件诊断，v2 的分子 C1 未通过联合门槛，C0 只保留为无实测对照输入的研究基线 |
| 51:53–54:31 | 每条件只有极少数群体蛋白组向量，不能直接照搬单细胞分布模型 | cVAE/异方差、GRU/静态前缀均已公平比较 | 明确 Self-Flow/cVAE/diffusion 当前不可识别，不优先扩张 |
| 55:54–58:09 | 高总体 R² 会隐藏强变化蛋白；GO/PPI 先验须经消融 | DEP、多目标、GO multi-head、命名 GO-slim、STRING 局部网络均已测试 | 保留固定 |Δ|>1 主口径；没有通过错配负对照的先验不进入模型 |
| 59:45–1:14:00 | 药物、菌株、环境之间存在交互；加性残差只是简化 | residual MLP 与 pair-ANOVA 未通过完整门槛 | 新增交互式表达式，并明确残差专家不是可识别因果分量 |
| 1:15:53–1:17:31 | 还有隐藏生物学评估和代码复现 | 报告已有隐藏集隔离、代码索引与 clean release | 保持现有边界 |
| 1:20:20–1:21:10 | 对过滤后还是全蛋白提交的口头说明不完全一致 | 当前 release 的 strict `<80%` 实算为 4,422，与 template 提交面板分开 | 不根据口头答疑或不可复现的 4,232 硬编码输出宽度，始终服从机器可读模板 |

## 本轮写入正式报告的内容

1. 两套知识配置是内部消融，而非官方双榜声明。
2. NA 的实验含义、共同有效掩码，以及禁止模型通过 NaN 逃避评分。
3. paired Endpoint 与 Raw-FC RMSE 在同一 measured control/mask 下的代数关系。
4. fit-frozen residual 是本项目为防泄漏采用的主评估，不冒充未公开评分脚本。
5. MSE 条件均值、Huber 与高响应加权的概念区分。
6. residual expert 的交互项与非因果边界。
7. 群体蛋白组不满足直接 control-to-treated 分布学习的可识别性条件。
8. prediction.csv 只提交 Endpoint 预测，matched control 由评测端处理。
9. 会议提到的是“SMILES 构造 embedding”和“相似药物/CPA”路线，**没有**规定 canonical SMILES、InChIKey、盐/母体、电荷或互变异构体标准化。当前使用 ChEBI r253 largest-fragment canonical-isomeric parent、并把歧义实体送入 missing 分支，是本项目为避免错误结构身份而新增的工程合同，不应表述成会议原话或官方要求。
10. 结构泛化实验已按全 $37$ 药物主队列完成；M2 仅是 CPA-style 加性 Ridge，不是 CPA/chemCPA 的完整复现。
11. 非线性组合实验分为两种不可混用的输入协议：v1 读取 exact-context 实测对照，只能作条件诊断；v2 不向预测器提供实测对照，是在 v1 结果已知后的开发性复测。C1 未通过联合门槛，C0 只保留研究，不属于默认提交路线；两版均不是原始 CPA/chemCPA 复现。

## 下一轮最小实验优先级

1. 用当前 release 实算的 strict 4,422 面板、fit-frozen residual、固定 |Δ|>1 DEP 口径重放 mean/Ridge/候选路由；不自行合成官方总分。
2. 已完成：在同一 384 蛋白、同一 OOD 折分下比较 MSE、Huber、$4\times$ response-weighted MSE/Huber；下一步只预注册更温和的 inner-fit 权重或幅度约束。
3. 已完成：whole-drug Tanimoto/kNN 风格响应迁移、CPA-style 加性 Ridge、低秩结构--条件双线性交互及两版非线性组合模型；当前分子分支均未晋级。下一轮先给无实测对照 C0 增加匹配 rank-32 目标与容量的线性对照，再只在覆盖更高、身份唯一、标准化策略冻结的结构上，用预注册正则、身份破坏负对照及许可兼容的预训练分子表示重测。
4. 在药物和菌株描述符同时更完整前，不扩大 Self-Flow、diffusion、Transformer 或大型 GNN；现有双线性交互的负结果保留为容量与身份置换对照基准。

## 对应实现

- 数据/NA/log2：`research_code/pipeline/preprocessing.py`
- matched control：`research_code/pipeline/controls.py`、`research_code/pipeline/vehicle.py`
- Endpoint/Raw-FC/残差：`research_code/evaluation/metrics.py`、`research_code/evaluation/residuals.py`
- 损失消融聚合回放：`research_code/experiments/loss_ablation.py`、`research_code/evidence/loss-ablation-v1/RESULTS.md`
- 结构泛化聚合回放：`research_code/experiments/structure_generalization.py`、`research_code/evidence/structure-generalization-v1/RESULTS.md`
- 非线性组合两版聚合回放：`research_code/experiments/chemcpa_nonlinear.py`、`research_code/evidence/chemcpa-nonlinear-v1-v2/RESULTS.md`
- DEP：`research_code/evaluation/dep.py`
- 提交合同：`research_code/pipeline/submission.py`
- 历史实验入口与证据级别：`research_code/evidence/registry.json`
