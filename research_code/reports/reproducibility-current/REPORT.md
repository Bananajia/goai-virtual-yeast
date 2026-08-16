# 当前代码整理与复现报告

日期：2026-08-11

参赛队伍：**小米蕉队**

## 结论

项目已经形成一层独立、可执行的研究代码，历史实验目录保持原样作为证据。新代码将数据处理、模型、实验、未来公共数据实验、统一评测和聚合报告分开，并通过同一个实验 Interface 调用。

本轮复现分成三种证据，不能混为一谈：

1. **统一代码的可执行复现：** 当前源代码树 110 项单元/合同测试全部通过，84 个发布层 Python 文件编译通过。最终干净发布仓库应在组装完成后单独记录，不能沿用旧 checkout 的测试数。
2. **历史结论的证据回放：** registry 共 28 项，其中 25 份 golden 聚合证据的 SHA-256 与 177 个冻结指标全部复现，未读取私有矩阵或逐样本预测；六个 release-safe 聚合 Adapter 为 6/6 records、147/147 scalars。
3. **端到端合成验证：** 固定 seed 7 的平均值模型正确呈现条件方差塌缩；固定 seed 11 的 Metadata Ridge 在已知合成机制上恢复 Raw-FC PCC 0.999994、条件方差比 0.999841、Endpoint RMSE 0.003759。

这证明新 Interface、统一评测和证据链可以复现。它不等于重新训练了全部历史模型，也不等于已在私有比赛矩阵上正式重跑 LIVE Metadata Ridge；历史运行没有保存逐样本预测，且两个最终路由名称缺少可执行源码，因此这些边界不能伪装成源码级复现。

## 目录与职责

| 目录 | 唯一职责 | 主要 Interface |
|---|---|---|
| `pipeline/` | 数据合同、log2、fit-only 缺失过滤、metadata 编码、OOD 划分、实测对照配对 | `DatasetAdapter`、`MissingnessFilter`、`GroupedOODSplitter`、`MeasuredControlPairer` |
| `models/` | 可替换预测器 | `fit()` / `predict()`；均值与 masked multi-output Ridge |
| `experiments/` | 一个 Python 文件代表一个实验；只做组装，不复制评测实现 | `Experiment.run(RunContext)` |
| `experiment_core/` | 注册、执行、状态与历史证据 Adapter | `ExperimentResult`、`ExperimentRegistry`、`LegacyEvidenceReplay` |
| `future_experiments/` | 与比赛私有数据物理隔离的 public-only 研究 | `CausalChainProvider`、public RNA fixture |
| `evaluation/` | 唯一规范指标实现 | `EvaluationSuite`、`DEPPolicy`、`PromotionGate` |
| `reporting/` | 只写模型级聚合 JSON/Markdown | `AggregateReportWriter` |
| `evidence/` | 冻结来源、哈希、有效性、替代关系和代码盘点 | `registry.json`、`code_inventory.json` |
| `tests/` | 缺失、泄漏、分组、指标边界和隐私回归测试 | Python `unittest` |

历史树仍包含 101 个实验目录、448 个 Python 文件和 121 个测试文件。它们没有被批量改写；新层通过 Adapter 引用已验证证据，避免为了“整理”而破坏原始实验谱系。

## 统一评测的关键修正

- Raw-FC 必须由 `predicted endpoint - directly measured matched control` 得到；evaluator 只接受经过 `MeasuredControlPairer` 密封验证的 paired response，裸 control 数组、只传 FC 或用 `truth endpoint - truth FC` 反推对照都会失败。
- `match_official_controls()` 必须通过显式 chemical→DMSO/Water 映射，并同时匹配 source、菌株、培养基、温度、时间、instrument 与 plate；映射或对照缺失时停止。
- 拟合入口通过 `split_final=train` 角色检查，validation/test 标签进入拟合会立即失败。
- endpoint、control 与 prediction 使用相同 replicate×protein 共同有限值掩码。
- 真值有效的 Endpoint 坐标要求预测值有限；模型若输出 NaN 试图跳过困难坐标，评价器会立即停止。实测对照缺失只缩小响应指标的合法队列，不会删除 Endpoint 评价坐标。
- 官方 context/drug residual 默认使用 outer-fit truth 冻结参考；参考同时绑定样本 ID、蛋白 ID、分组及顺序。历史 evaluation-centered 残差单独标为内部敏感性。individuality 中心化前使用共同掩码；每个 `group × protein` 至少两个有限观测。
- 真值有方差而预测恒定时 PCC 记为 0，不再把 NaN 静默跳过，避免平均值模型分数虚高。
- Endpoint 同时报告 all-cell 与 paired-cell scope；Raw-FC、残差、VR 和 DEP 只用 paired scope。
- 官方 DEP 使用固定 `abs(log2 FC) > 1`；只有 K 由 outer-fit 数据拟合，并在 baseline、candidate 和负对照之间共享。历史分位数阈值仅为敏感性。
- paired scope 下 Endpoint RMSE 与 Raw-FC RMSE 必然相等，因为二者减去同一个实测 control；报告不再把它们描述成两条独立误差信号。
- `OfficialScorecard` 按 split 路由公开的六个评分模块及 20/25/20/20/10/5 权重，但不合成“官方总分”：现有材料没有给出可复现的模块内聚合公式。复现/合规仍是门槛，另行公布的开源贡献项独立披露。
- 聚合报告在创建目录或文件前验证 metrics 只能是标量、counts 只能是非负整数、contract 只能是布尔值，并拒绝绝对路径和 private-data 文本；JSON 与 Markdown 在内存中完成后再原子写出。

## 历史正式结果回放

证据回放结果：25/25 个 golden records 通过，177/177 个冻结指标一致，0 个已作废结果被当作 golden。六个 release-safe 聚合 Adapter（loss、structure、nonlinear composition、PubChem/RDKit confirmatory、public causal residual、public similarity prototype）独立核验 6/6 records、147/147 scalars。

本轮新增了正式 baseline 套件的冻结回放：

| 结果 | 冻结值 | 含义 |
|---|---:|---|
| 平均值 baseline Flattened PCC | 0.941091 | 基础蛋白丰度轮廓非常稳定 |
| 平均值 baseline Flattened R² | 0.885639 | 大部分 flattened 总变异来自跨蛋白基础差异 |
| 平均值 baseline 逐蛋白平均 R² | -0.041278 | 没有恢复同一蛋白跨条件变化 |
| 平均值 baseline 条件方差比 | 0 | 对所有条件输出同一张谱 |
| Metadata Ridge Endpoint PCC | 0.985145 | 完整蛋白谱轮廓高度相关，不是 98.5% 药物效应准确率 |
| pooled-control Raw-FC PCC | 0.326278 | 仅为缺少 chemical→vehicle 映射时的探索性内部口径 |
| 当前 release 的 strict 掩码 | 4,422 modeled + 821 fallback = 5,243 | train-only 缺失率 `<80%`；恰好 80% 的坐标为 0，因此与 `<=80%` 面板相同 |
| 解读材料报告数 | 4,232 modeled + 1,011 filtered | 不能由材料所列公式在当前 release 复现，不作机器常量；提交列仍由最新官方模板决定 |

`control-affine-fullpanel-v1` 及旧 response-threshold 结果的无效部分继续保留作审计，但不会进入 golden 结论。现有历史 context/drug residual 与高响应聚合结果没有逐样本预测可供新版 fit-frozen、固定阈值 evaluator 重算，因此仍按旧内部协议标注，不能据此估算官方总分。

### PubChem/RDKit 结构确认

正式聚合 Adapter 已纳入 37 个药物的确认性实验：25 个通过严格结构解析，12 个走逐项完全缺失回退；三种结构候选均未通过晋级门。Adapter 核验 20 个冻结标量，但不分发实体 crosswalk、SMILES、InChIKey、fingerprint、逐样本预测或权重。这个结果说明结构覆盖从旧版本改善，但没有证明结构特征带来稳定的药物特异增益，因此没有把候选强行晋级。

### 公共因果链与相似度原型

两个已完成的公共知识实验也已接入独立 release-safe Adapter。因果残差实验核验 39 个匿名聚合标量，相似度原型核验 43 个；两者分别与已审计 `RESULTS.md` 逐字节一致。它们只保存总体覆盖、fold-macro 指标、方向计数和结论，不分发实体 join/mapping、逐条件或逐蛋白行、分子/基因组/机制轴向量、邻居、预测或权重。二者都维持 `VALIDATED_REJECTED`，不能因为可复现而改写为候选晋级。

因果链的交互式 Codex 闭源商业创作 seam 已在 `external_resources/manifest.json` 披露：未提供比赛数据，训练/推理/评分/回放时无模型调用，冻结输入输出有 SHA-256；但精确服务快照和稳定 transcript 不可得，因此生成本身不声称 bit-reproducible。相似度实验的 PubChem 与 Peter-2018 公共资产及哈希边界也在同一 manifest 中登记。

### LIVE Metadata Ridge 边界

`train-metadata-ridge` / `predict-metadata-ridge` 的数据合同、train-only 拟合、未知类别、artifact 与 submission 模板路径已经由 tiny fixture 和失败路径测试覆盖。当前快照没有在私有正式矩阵上重新训练、推理并评分；上文 seed 11 指标仅为可恢复合成机制的端到端测试，不能写成正式比赛结果。

## Future public-only 小实验

### 公共因果链 Interface

Provider 只接受固定 schema 的公共事实与已锁来源，输出 3–8 条 `source → relation → 23 mechanism axes` 边。它不接受 DataFrame、文件路径、比赛实体、任意自由文本、蛋白向量或私有实验摘要。

已实现：

- 确定性 Fixture provider；
- 仅允许 `127.0.0.1/localhost` 的 Ollama provider；
- 默认禁用的 OpenAI-compatible public-only Adapter。

本轮没有调用外部 GPT。未来若显式启用，Adapter 也只能收到通过 allowlist 与哈希校验的公共 fixture。

### RNA/L1000FWD mini smoke

六条冻结的公开 HA1E RNA 扰动签名被映射到同一 23 机制轴，与 fixture 因果链比较：macro cosine 0.122479、pooled Pearson 0.120599、signed accuracy 0.150943。两次离线执行的 JSON 与 Markdown 逐字一致。

该结果只证明“公共查询 → 因果链 → RNA 机制轴 → 聚合评测”链路可运行；样本太少且是人类 RNA，不能据此声称已迁移到酵母蛋白质组。

### 本地开放权重模型实测

在同一 public-only Interface 上又运行了本机 `qwen3:8b`。匿名单例 smoke 成功并立即复跑得到逐字一致的聚合结果（macro cosine 0.094916）；预设六例运行在匿名第 2 例遇到不符合封闭 schema 的结构化输出，因此 fail-closed，丢弃全部部分分数并标记 `BLOCKED`。这说明本地推理链路可用，但当前模型的结构输出稳定性尚不足，不能声称 LLM 机制特征有效，更不能进入酵母预测模型。

该运行只访问回环 Ollama，未联网、未调用闭源 API，且未保存药物名、prompt、response、因果链、RNA truth 或逐例向量。

## 已知复现边界

- `chemical-router-v3` 与 `unified-router-final-v3-scoped` 只有叙述和私有聚合线索，在持久项目与工作区都没有找到对应源码，状态固定为 `BLOCKED_SOURCE_MISSING`。若重写，只能标记 reconstruction，不能冒充原实现。
- 大多数历史隐私协议没有保存逐样本预测，所以无法仅靠 aggregate CSV 用新版 evaluator 重算每个 cell；必须在未来新的 train-only OOF 运行中同时调用 legacy 与 canonical scorer 做 reconciliation。
- 本轮没有读取 fixed validation/test 真值，没有重新调参，也没有通过网络发送比赛数据。
- LIVE Metadata Ridge 当前只有 tiny fixture 级端到端验证；正式私有数据重跑仍待具备可合法使用的数据与最新版提交模板后执行。
- 正式重放仍依赖组委会提供机器可读 vehicle 映射和最新版 submission feature contract；代码对两者缺失均采用 fail-closed，不用 pooled control 或自定列宽冒充正式结果。
- public-only mini fixture 的许可和跨物种边界必须保留；它目前不进入比赛模型。

## 最短复现命令

```bash
cd research_code
uv sync --extra dev
uv run --locked python -m unittest discover -s tests -q
uv run --locked python research_cli.py list
uv run --locked python research_cli.py run \
  legacy_evidence_replay --scope aggregate-only \
  --data-root .. \
  --output reports/reproducibility-current/legacy-evidence
uv run --locked python research_cli.py run \
  pubchem_structure_confirmatory_evidence --scope aggregate-only \
  --data-root .. \
  --output reports/reproducibility-current/pubchem-structure-confirmatory-replay
uv run --locked python research_cli.py run \
  public_causal_residual_evidence --scope aggregate-only \
  --data-root .. \
  --output reports/reproducibility-current/public-causal-residual-replay
uv run --locked python research_cli.py run \
  public_similarity_prototype_evidence --scope aggregate-only \
  --data-root .. \
  --output reports/reproducibility-current/public-similarity-prototype-replay
uv run --locked python research_cli.py run \
  synthetic_mean_baseline --scope synthetic \
  --seed 7 \
  --output reports/reproducibility-current/synthetic-pipeline
uv run --locked python research_cli.py run \
  synthetic_metadata_ridge --scope synthetic \
  --seed 11 \
  --output reports/reproducibility-current/synthetic-metadata-ridge
uv run --locked python research_cli.py run \
  public_rna_lincs_mini --scope public \
  --output reports/reproducibility-current/public-rna-mini
```

详细命令与检查结果见 `TEST_RECORD.md`；每个子目录还有各自的 `REPORT.md`/`result.json`。
