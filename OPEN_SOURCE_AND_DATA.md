# 小米蕉队：开源、依赖、模型与数据边界

更新日期：2026-08-16

本文件对应 GOAI 赛道三虚拟细胞方向 2026-08-11 修订规则及[选手参赛协议](https://www.goaihz.com/terms)关于开源范围、授权方式、第三方依赖、商业 API、模型服务和数据来源的披露要求。它描述提交代码的实际状态，不把计划中的资源写成已经用于最终模型。

## 开放范围与授权

- 提交包中的小米蕉队原创 `research_code/` Python 源码、测试、配置和原创说明文档，随发布包根目录的 `LICENSE` 按 Apache License 2.0 授权。
- `research_code/evaluation/`、`pipeline/`、`SubmissionContract`、MiJiaoPredict 证据门控接口、public-only Provider 合同、聚合证据 Adapter 和泄漏回归测试是本队拟形成的可复用开源贡献。
- 比赛原始数据、私有实体映射、本地训练 artifact、逐样本预测、蛋白向量、模型权重、prompt/response 与凭据不属于开放范围，也不会进入 Git 历史或 ZIP。
- 第三方数据、小型 fixture 和模型权重不因进入或被引用于本仓库而获得 Apache-2.0 再授权；其许可和再分发边界以原始提供方为准。
- 初赛期间 GitHub 仓库保持私有。初赛完成并通过 Git 历史、许可、凭据与数据泄漏复核后，计划公开上述原创代码层；若某项第三方资产不能再分发，只公开确定性下载/预处理代码、版本和哈希。

## 可运行提交基线

`research_code/research_cli.py` 提供 LIVE competition metadata Ridge 的训练与推理命令。训练入口只接受由参赛者在本机预先切出的 `split_final=train` metadata/proteome 文件；它会拒绝混入 validation/test 标签的文件。当前入口不声称可直接读取组委会的混合 train/validation 原始包。

训练 artifact 在本机保存模型系数、fit-only encoder 状态、蛋白输出合同和 provenance manifest。该 artifact 含训练类别词表与官方蛋白名称，属于本地运行产物，不应提交到公共仓库。推理按最新版官方 submission template 的样本顺序和蛋白有序子集生成 `prediction.csv`。

## 第三方依赖

| 依赖 | 角色 | 固定方式 |
|---|---|---|
| Python、NumPy、pandas | LIVE baseline 运行时 | `research_code/pyproject.toml` 与 `uv.lock` |
| pytest | 开发测试 | `dev` extra 与 `uv.lock` |
| h5py、RDKit | 外部公共数据/化学特征的可选依赖；当前 LIVE metadata Ridge 不调用 | `public` extra 与 `uv.lock` |
| Ollama | 本地模型试验的外部运行时；不属于提交基线依赖 | 运行报告记录版本 |
| `qwen3:8b`、`gemma4:12b` | 获授权 competition train-only whole-drug 机制诊断；未联网、未晋级 | 聚合 evidence 记录精确本地 tag；权重不再分发、原许可适用 |
| Qwen3 8B | 另一项独立的 public-only L1000FWD smoke；没有进入酵母预测模型 | 运行报告记录 tag 与 digest；权重不再分发、原许可适用 |

完整解析版本和 wheel 哈希以 `research_code/uv.lock` 为准。使用者仍须遵守各依赖自身许可证。

## 商业 API 与闭源模型

- LIVE metadata Ridge 以及本文各项比赛数据训练、推理、评分和聚合重放均**没有调用商业 API，也不依赖在线闭源模型**。
- `public-causal-residual-v1` 的一份 public-only 静态解释特征曾由交互式 OpenAI Codex 闭源商业服务（GPT-5 family，服务未暴露精确 snapshot）协助编写。服务只接收冻结的 PubChem/公共 chemical-genetic 字段与 23 轴 schema；没有接收比赛实体清单、成员关系、蛋白矩阵、残差、预测、验证或测试结果。该过程没有单独调用开发者 API，也没有使用项目 API key；训练、推理、评分与重放阶段不再调用模型服务。完整 prompt/transcript 与精确 snapshot 不可复现，因此复现边界是公开输入、冻结输出、校验值与 closed-schema validator，而不是重新生成。该候选未通过公共 RNA 前置门槛及蛋白残差增量门槛，未进入比赛预测器。
- 代码中另有一个默认关闭的 OpenAI-compatible public-only Provider 接口，仅作为未来实验 seam；它不同于上述一次性 Codex 静态资产编写，也不参与当前提交结果。仓库不含 API key，不要求评审调用或付费。
- competition train-only whole-drug 机制诊断在本机使用 `qwen3:8b` 与 `gemma4:12b` open-weight 模型，未联网、未调用外部 API，且候选未晋级；它不同于 public-only RNA smoke。
- public-only L1000FWD smoke 只通过回环地址调用本机 Ollama/Qwen3 8B，并在结构化输出失败时 fail-closed；该结果同样没有进入比赛预测器。

## 数据来源与授权边界

资源状态索引见 `research_code/external_resources/manifest.json`：

- 组委会数据仅在获授权的本机路径读取，不再分发；LIVE baseline 当前只使用这部分 train-only 切片。
- PubChem/RDKit 与 SGD S288C→DHY210 代理是 2026-08-11 规则推荐的开放知识路线。PubChem-first 身份与 MolStandardize 覆盖审计已冻结为 $25/37$（旧 ChEBI 严格覆盖为 $22/37$），并完成带匹配结构置乱的 train-only 聚合确认；Tanimoto、CPA-style 和双线性候选均未晋级。该资产没有进入 LIVE metadata Ridge，实体级结构也不随发布包分发；发布层只保留无身份的聚合证据与来源/版本边界。1011/Peter 菌株资源已用于 aggregate-only 私有 pilot，但没有进入 LIVE metadata Ridge；发布层只保留聚合结论与来源边界。S288C→DHY210 仍只是组委会允许的参考背景代理，不等于 DHY210 特异变异/CNV 已知。
- PubChem AID 1159580 的公开酵母 chemical-genetic 数据用于构建固定 23 轴公共候选表示。公开候选面板与静态解释资产可以按其来源许可和本仓库声明审阅；比赛内精确连接表、成员关系、逐实体分数、响应残差和模型权重均不分发。该表示只覆盖比赛主分析中的 $6/37$ 个药物，因果候选相对严格 PubChem 结构及 raw-CGM 对照均未产生增量价值；“因果”仅表示待检验的结构化假设，不表示已识别处理效应。
- 药物/菌株公共相似度实验使用同一 $25/37$ 严格 PubChem 结构视图和 $3/4$ 公共菌株映射，比较硬聚类均值、软双核距离迁移及部分池化交互。全 $37$ 药物主分析保留缺失实体的精确基线回退；三类候选及其匹配置乱对照均未通过冻结门槛。发布层只保留不含身份、核矩阵、medoid、向量、逐条件输出或权重的聚合证据。
- ChEBI、STRING/STITCH、公共菌株资源和 L1000FWD 的既有试验均按各自证据边界报告。只有 L1000FWD 小 fixture 随代码分发，并保留来源、检索日期、哈希和单独的许可说明。

## 5% 开源贡献说明

本项目可复用贡献包括：fit-only 数据合同、missing/unknown 处理、模板权威的全输出恢复、直接实测对照合同、OOD 划分、Endpoint/Raw-FC/残差/DEP 指标、统一实验接口、隐私安全聚合报告、public-only 模型 Provider 防护和故障注入测试。提交材料会明确区分 `LIVE`、聚合证据回放和未来实验，避免用“代码数量”替代真实可复现能力。
