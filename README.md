# GOAI Virtual Yeast — Team MiJiao

This repository contains Team MiJiao's technical work and research code for the preliminary round of the GOAI AI for Research virtual-cell track. The project follows the evaluation contract clarified on August 11, 2026 and is organized around a single open leaderboard. Competition-only inputs and public-knowledge inputs are evaluated as internal ablations under the same contract rather than as separate leaderboards.

## Repository contents

- `research_code/pipeline/`: data contracts, preprocessing, paired measured controls, and out-of-distribution (OOD) splits.
- `research_code/models/`: the mean baseline and masked multi-output Ridge model.
- `research_code/experiments/`: unified experiment entry points and adapters for historical evidence.
- `research_code/evidence/`: release-safe aggregate evidence for loss functions, structure generalization, chemCPA-style nonlinear models, PubChem structure confirmation, public causal-axis residuals, and drug-strain similarity prototypes.
- `research_code/future_experiments/`: strictly public-only providers for the RNA mini experiment and causal-chain experiments.
- `research_code/evaluation/`: endpoint, raw fold-change, residual, differentially expressed protein, and four OOD evaluation modules. The code does not invent an unpublished official aggregate score.
- `research_code/tests/`: tests for missing values, leakage, metric boundaries, and privacy contracts.
- `research_code/mijiao_predict_v0/`: the MiJiaoPredict evidence-gated routing interface, expert-status manifest, per-query routing audit, and fail-safe fallback tests.
- `research_code/reports/meeting-audit-20260810/`: line-by-line checks, timestamps, and report-editing boundaries from the August 10 technical meeting.
- `OPEN_SOURCE_AND_DATA.md`: Apache-2.0 scope and the licensing boundaries for third-party dependencies, commercial APIs, models, and data.

The submission PDF and LaTeX source are intentionally kept outside this public code repository. Competition source data, private entity mappings, per-sample predictions, protein vectors, model credentials, and local machine paths are also excluded.

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

The production entry points for training and predicting with the LIVE metadata Ridge model are:

```bash
uv run --locked python research_cli.py train-metadata-ridge --help
uv run --locked python research_cli.py predict-metadata-ridge --help
```

These commands only accept locally supplied paths to authorized data. Training input must already be restricted to a clean `split_final=train` slice. Model artifacts and `prediction.csv` are not committed to the repository.

The current public tree discovers 118 unified tests: 115 pass and 3 are skipped as expected because they only replay historical trees that are not distributed with this repository. All 7 standalone MiJiaoPredict contract tests pass. Eleven release-safe adapters directly replay 11 aggregate records and 223 frozen scalar metrics. They verify evidence hashes and numeric values without pretending to retrain models on private data. The CLI currently lists 29 unified experiment entry points.

MiJiaoPredict v0 is not another trained black-box model. It is the public orchestration interface for the overall predictor. Metadata Ridge first produces a complete core prediction. The router permits an expert to apply a residual correction or replacement only when that expert has an executable source, has passed validation within a defined scope, and has all required inputs for the current query. If an expert is not promoted, required input is missing, or execution fails, the Ridge output is preserved and the event is recorded in the routing audit.

PubChem-first matching with RDKit MolStandardize increased strict structure coverage from 22/37 to 25/37 drugs. However, the Tanimoto, CPA-style additive, and bilinear candidates still did not pass the preregistered gates. This result shows that structure coverage improved, but it does not establish a net generalization benefit for the current structure branch.

The public drug-strain similarity prototype evaluated hard-cluster means, soft dual-kernel neighbor transfer, and partially pooled interactions. In the unseen-strain setting, the P1 mean gains were PCC `+0.063254` and RMSE `+0.002948`, but only 2 of 4 folds improved on each metric, so the strict majority gate was not met. The unseen-drug, double-unseen, matched-negative-control, P0, and P2 evaluations also failed their gates, so the method was not promoted. A separate 23-axis public causal-hypothesis representation matched only 6 of 37 drugs exactly and did not improve over either the strict PubChem structure baseline or the raw-CGM control. It was not promoted either. These are conservative negative results verified through independent aggregate replay; they are not general rejections of public knowledge or causal mechanisms.

## Data boundary

Every competition matrix must be supplied explicitly by a local caller through the Pipeline Adapter, and fitting is restricted to `split_final=train`. Formal raw fold-change evaluation requires an explicit chemical-to-DMSO/Water mapping and an exact metadata control match. Submission columns, column order, and log2 scale are validated against the official template contract. Public providers disable network writes by default. The GPT-compatible provider accepts only a fixed public-only schema and rejects free text, competition paths, sample identities, and protein vectors.

This repository does not grant redistribution rights for referenced external data or model weights. Users must separately comply with the original licenses for PubChem, RDKit, the 1,011-isolate/Peter resource, SGD, ChEBI, STRING, STITCH, L1000FWD, and all referenced models. See [`OPEN_SOURCE_AND_DATA.md`](OPEN_SOURCE_AND_DATA.md) for the complete disclosure.
