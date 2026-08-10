# 2026-08-10 虚拟细胞方向头脑风暴会：报告查漏补缺记录

来源：[腾讯会议回放](https://meeting.tencent.com/cw/NQBBbEoZd5)，会议名“GOAI虚拟细胞方向头脑风暴会”，时长约 1 小时 24 分。核对日期：2026-08-10。

## 证据边界

本记录逐段核对平台逐字稿与正式技术报告。逐字稿由平台自动生成，可能存在术语识别错误；会议属于技术交流，不能替代组委会书面规则、机器可读 submission template 或正式评分脚本。下面只记录可追溯的时间段、技术含义、当前覆盖情况和项目决定，不保存逐字稿全文。

## 增量核对

| 时间段 | 会议技术要点 | 项目已有证据 | 处理决定 |
|---|---|---|---|
| 01:23–02:17 | one-hot 无法表达新菌株或新药之间的相似性；新药需要 SMILES 等描述符 | whole-chemical MLP、结构 Transformer、靶点到 STRING 实验均已完成 | 保留结论：身份编码不足；外部表示必须通过 whole-drug 与错配负对照 |
| 04:54–05:14 | 口头提到开放/封闭知识可能合并，但同时要求等待官方通知 | 报告原有两套运行配置 | 改为“内部消融配置”，不声称官方存在两个榜单 |
| 08:12–08:47 | 任务是 zero-shot；需检查模型是否只回到平均值 | 均值 baseline 的条件方差为 0，逐蛋白 R² 为负 | 新增 MSE 条件均值的数学解释 |
| 17:20 左右 | 讨论 Huber 与高变化蛋白 | 已有多目标/高响应 pilot | 明确 Huber 是对大预测误差稳健化，不等于给大真实响应加权；后续公平比较 MSE、Huber、response-weighted MSE |
| 23:22–26:56 | matched control 与同药物残差的聚合较复杂 | 已实现显式 measured-control、共同掩码和 fit-frozen residual | 将现实现称为“保守内部合同”，不冒充未公开的官方聚合公式 |
| 27:28–28:14 | 当前两种培养基主要按已给类别区分 | metadata encoder 把培养基作为类别变量 | 明确不声称能外推任意培养基配方 |
| 35:35–36:34 | NA 不是零；相减、PCC、R² 需共同有效掩码 | pipeline/evaluator 已保留 NA 并禁止填零 | 在正文补充 NA 的实验含义，并要求预测不得用 NaN 选择性跳过困难坐标 |
| 42:51–43:04 | 参赛者提交预测，matched control 由评测端准备 | submission contract 只接 Endpoint prediction | 在提交合同中明确不额外提交 matched-control 向量 |
| 43:13–47:25 | 建议 CPA/chemCPA；先做相似药物统计基线 | 报告已有 CPA/chemCPA 路线；结构覆盖仍有限 | 取得规范化结构后，优先做 whole-drug Tanimoto/kNN，再决定是否上 CPA |
| 51:53–54:31 | 每条件只有极少数群体蛋白组向量，不能直接照搬单细胞分布模型 | cVAE/异方差、GRU/静态前缀均已公平比较 | 明确 Self-Flow/cVAE/diffusion 当前不可识别，不优先扩张 |
| 55:54–58:09 | 高总体 R² 会隐藏强变化蛋白；GO/PPI 先验须经消融 | DEP、多目标、GO multi-head、命名 GO-slim、STRING 局部网络均已测试 | 保留固定 |Δ|>1 主口径；没有通过错配负对照的先验不进入模型 |
| 59:45–1:14:00 | 药物、菌株、环境之间存在交互；加性残差只是简化 | residual MLP 与 pair-ANOVA 未通过完整门槛 | 新增交互式表达式，并明确残差专家不是可识别因果分量 |
| 1:15:53–1:17:31 | 还有隐藏生物学评估和代码复现 | 报告已有隐藏集隔离、代码索引与 clean release | 保持现有边界 |
| 1:20:20–1:21:10 | 对过滤后还是全蛋白提交的口头说明不完全一致 | 报告区分 strict 4,232 拟合面板与 template 提交面板 | 不根据口头答疑硬编码输出宽度，始终服从机器可读模板 |

## 本轮写入正式报告的内容

1. 两套知识配置是内部消融，而非官方双榜声明。
2. NA 的实验含义、共同有效掩码，以及禁止模型通过 NaN 逃避评分。
3. paired Endpoint 与 Raw-FC RMSE 在同一 measured control/mask 下的代数关系。
4. fit-frozen residual 是本项目为防泄漏采用的主评估，不冒充未公开评分脚本。
5. MSE 条件均值、Huber 与高响应加权的概念区分。
6. residual expert 的交互项与非因果边界。
7. 群体蛋白组不满足直接 control-to-treated 分布学习的可识别性条件。
8. prediction.csv 只提交 Endpoint 预测，matched control 由评测端处理。

## 下一轮最小实验优先级

1. 用 strict 4,232 面板、fit-frozen residual、固定 |Δ|>1 DEP 口径重放 mean/Ridge/候选路由；不自行合成官方总分。
2. 在同一 384 蛋白、同一 OOD 折分下比较 MSE、Huber、response-weighted MSE。
3. 取得唯一映射的规范化 SMILES/InChIKey 后，先做 whole-drug Tanimoto/kNN 强统计基线，再比较 CPA/chemCPA。
4. 只有在药物和菌株均有可泛化描述符后，才验证低秩双线性交互；在此之前不扩大 Self-Flow、diffusion、Transformer 或大型 GNN。

## 对应实现

- 数据/NA/log2：`research_code/pipeline/preprocessing.py`
- matched control：`research_code/pipeline/controls.py`、`research_code/pipeline/vehicle.py`
- Endpoint/Raw-FC/残差：`research_code/evaluation/metrics.py`、`research_code/evaluation/residuals.py`
- DEP：`research_code/evaluation/dep.py`
- 提交合同：`research_code/pipeline/submission.py`
- 历史实验入口与证据级别：`research_code/evidence/registry.json`
