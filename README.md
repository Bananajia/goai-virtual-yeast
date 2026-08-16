# GOAI Virtual Yeast — 小米蕉队

小米蕉队参加 GOAI AI for Research 赛道三虚拟细胞方向初赛的技术方案与研究代码。项目按照 2026-08-11 细化规则面向统一开放榜组织；仅比赛数据与公开知识配置是同一评价合同下的内部消融，不是两个独立榜单。

## Repository contents

- `GOAI 虚拟酵母赛道 小米蕉队.pdf`：精简提交版报告《虚拟酵母扰动蛋白质组预测：已知方法迁移的适用边界与机制因果链初探》。
- `research_code/pipeline/`：数据合同、预处理、成对实测对照与 OOD 划分。
- `research_code/models/`：均值基线与 masked multi-output Ridge。
- `research_code/experiments/`：统一实验入口及历史证据 Adapter。
- `research_code/evidence/`：发布安全的损失函数、结构泛化、chemCPA 风格非线性、PubChem 结构确认、公共因果轴残差与药物--菌株相似度原型聚合证据。
- `research_code/future_experiments/`：严格 public-only 的 RNA mini 与因果链 Provider。
- `research_code/evaluation/`：Endpoint、Raw-FC、残差、DEP 及四类 OOD 的官方面对型模块路由；不臆造未公布的官方总分。
- `research_code/tests/`：缺失值、泄漏、指标边界和隐私合同测试。
- `research_code/mijiao_predict_v0/`：MiJiaoPredict 手工证据门控接口、专家状态清单、逐条路由审计和异常回退测试。
- `research_code/reports/meeting-audit-20260810/`：8 月 10 日技术交流会的逐段核对、时间戳和报告修改边界。
- `OPEN_SOURCE_AND_DATA.md`：Apache-2.0 范围、第三方依赖、商业 API、模型和数据授权边界。

比赛原始数据、私有实体映射、逐样本预测、蛋白向量、模型凭据及本机路径均不包含在仓库中。

## Quick start

```bash
cd research_code
uv sync --locked --extra dev
uv run --locked python -m unittest discover -s tests -v
uv run --locked python -m unittest mijiao_predict_v0.test_mijiao_predict -v
uv run --locked python research_cli.py list
uv run --locked python research_cli.py run synthetic_mean_baseline \
  --scope synthetic \
  --output reports/synthetic_mean_baseline
```

LIVE metadata Ridge 的训练与预测入口为：

```bash
uv run --locked python research_cli.py train-metadata-ridge --help
uv run --locked python research_cli.py predict-metadata-ridge --help
```

它们只接受调用者在本机提供的获授权数据路径，训练输入必须已经是纯 `split_final=train` 切片；模型 artifact 与 `prediction.csv` 不进入仓库。

当前公开树会发现 118 项统一测试，其中 115 项通过，3 项只回放未随仓库分发的历史树，因此按预期跳过。MiJiaoPredict 的 7 项独立合同测试全部通过。11 个发布安全 Adapter 可直接回放 11 条聚合记录与 223 个冻结标量；它们核验证据哈希与数值，不冒充私有数据上的模型重训。当前 CLI 列出 29 个统一实验入口。

MiJiaoPredict v0 不是另一个已经训练好的黑箱模型，而是总预测器的公开编排接口。Metadata Ridge 先生成完整基础预测，只有在某个专家具有可执行来源、已在限定范围通过验证，并且当前查询具备所需输入时，路由器才允许该专家进行残差修正或替换。未晋级、输入缺失或执行异常时保持 Ridge 结果，并写入路由审计记录。

PubChem-first + RDKit MolStandardize 将严格结构覆盖从 22/37 提高到 25/37，但 Tanimoto、CPA-style additive 和双线性候选仍未通过预设门槛。该结果说明结构覆盖得到改善，但没有证明现有结构分支具有净泛化收益。

新增的公共药物--菌株相似度原型同时检验了硬聚类均值、软双核近邻迁移与部分池化交互。未见菌株场景的 P1 均值改善为 PCC `+0.063254`、RMSE `+0.002948`，但两项都只有 2/4 折为正，未通过严格多数门槛；未见药物、双重未知、匹配负对照及 P0/P2 也未通过，因此不晋级。另一项 23 轴公共因果假设表示只精确覆盖 6/37 个药物，相对严格 PubChem 结构基线和 raw-CGM 对照均无增量，同样不晋级。这些是经过独立聚合回放的保守负结果，不是对公共知识或因果机制的一般否定。

## Data boundary

任何比赛矩阵都必须由本机调用方通过 Pipeline Adapter 显式提供，拟合角色只允许 `split_final=train`。正式 Raw-FC 要求显式 chemical→DMSO/Water 映射和精确 metadata control match；提交列、顺序与 log2 尺度由官方模板合同验证。公共 Provider 默认关闭网络写入能力；GPT-compatible Provider 只接受固定的 public-only schema，不接受自由文本、比赛路径、样本身份或蛋白向量。

本仓库不授予所引用外部数据或模型权重的再分发许可。使用者须分别遵守 PubChem、RDKit、1011/Peter、SGD、ChEBI、STRING、STITCH、L1000FWD 及相关模型的原始许可。完整披露见 [`OPEN_SOURCE_AND_DATA.md`](OPEN_SOURCE_AND_DATA.md)。
