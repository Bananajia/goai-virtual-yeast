# GOAI Virtual Yeast — 小米蕉队

小米蕉队参加 GOAI AI for Research 虚拟细胞方向初赛的统一研究代码与技术方案。

## Repository contents

- `GOAI 虚拟酵母赛道 小米蕉队.pdf`：初赛技术方案。
- `research_code/pipeline/`：数据合同、预处理、成对实测对照与 OOD 划分。
- `research_code/models/`：均值基线与 masked multi-output Ridge。
- `research_code/experiments/`：统一实验入口及历史证据 Adapter。
- `research_code/future_experiments/`：严格 public-only 的 RNA mini 与因果链 Provider。
- `research_code/evaluation/`：Endpoint、Raw-FC、残差、RMSE、VR 与 DEP 指标。
- `research_code/tests/`：缺失值、泄漏、指标边界和隐私合同测试。

比赛原始数据、私有实体映射、逐样本预测、蛋白向量、模型凭据及本机路径均不包含在仓库中。

## Quick start

```bash
cd research_code
python3 -m unittest discover -s tests -v
python3 research_cli.py list
python3 research_cli.py run synthetic_mean_baseline \
  --scope synthetic \
  --output reports/synthetic_mean_baseline
```

可选依赖环境：

```bash
cd research_code
uv sync --extra dev
uv run python -m unittest discover -s tests -v
```

独立提交包会发现 60 项测试；其中 3 项仅用于回放未随仓库分发的历史实验树，因此在该树不存在时明确跳过。核心、评测、合成实验与 public-only 测试均可独立运行。

## Data boundary

任何比赛矩阵都必须由本机调用方通过 Pipeline Adapter 显式提供。公共 Provider 默认关闭网络写入能力；GPT-compatible Provider 只接受固定的 public-only schema，不接受自由文本、比赛路径、样本身份或蛋白向量。

本仓库不授予所引用外部数据或模型权重的再分发许可。使用者须分别遵守 ChEBI、STRING、STITCH、Peter 菌株资源、L1000FWD 及相关模型的原始许可。
