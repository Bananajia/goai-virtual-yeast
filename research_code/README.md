# Unified virtual-yeast research code

This directory is the clean execution layer for the GOAI virtual-yeast project. The historical `../code/experiments/` and `../experiments/` trees remain untouched as evidence.

## Layout

| Folder | Responsibility |
|---|---|
| `pipeline/` | schema validation, `log2`, fit-only missingness, direct controls, OOD splits, full-output restoration |
| `models/` | one `fit/predict` Interface; mean, masked Ridge, and later low-rank/neural Adapters |
| `experiments/` | one file per experiment; no shared runner or metric code |
| `experiment_core/` | common registry, runner, status and legacy-evidence Adapter |
| `future_experiments/` | strictly public-only RNA transfer and causal-chain providers |
| `evaluation/` | the canonical metric implementation used by all experiments |
| `reporting/` | aggregate-only result writers |
| `evidence/` | validity and golden-result registry for historical runs |
| `tests/` | public-interface and leakage-regression tests |

## Quick start

```bash
cd research_code
uv sync --extra dev
uv run --locked python -m unittest discover -s tests -v
uv run --locked python research_cli.py list
uv run --locked python research_cli.py run synthetic_mean_baseline --scope synthetic --output reports/synthetic_mean_baseline
uv run --locked python research_cli.py run loss_ablation_evidence --scope aggregate-only --data-root .. --output reports/loss-ablation-replay
uv run --locked python research_cli.py run structure_generalization_evidence --scope aggregate-only --data-root .. --output reports/structure-generalization-replay
uv run --locked python research_cli.py run chemcpa_nonlinear_evidence --scope aggregate-only --data-root .. --output reports/chemcpa-nonlinear-replay
```

The standalone submission package runs the executable core and public-only tests;
tests that replay the optional historical experiment tree are skipped when that
tree is not present. The loss-ablation, structure-generalization and
nonlinear-composition Adapters are
release-safe exceptions: their compact, identity-free aggregate evidence ships
under `evidence/loss-ablation-v1/` and
`evidence/structure-generalization-v1/`, and
`evidence/chemcpa-nonlinear-v1-v2/`. Each Adapter verifies the source hash
and frozen scalars. This makes the negative model-selection decisions auditable;
it does not retrain the private pilots.

## Non-negotiable contracts

- Metadata and proteome rows are joined by unique `sample_ID`, never by current CSV row order.
- Fit-time labeled bundles must contain only `split_final=train`; validation/test truth fails closed.
- The interpretation policy models proteins with missingness `<80%`. On the current release this gives 4,422 proteins, exactly the same panel as `<=80%`, because no protein lies exactly on the 80% boundary. The interpretation PDF's 4,232 count is not reproduced by its stated formula and is therefore not hard-coded.
- Submission row identities, protein names/order, finite values, and declared `log2` scale must pass `SubmissionContract`; the latest official feature template is authoritative.
- Raw-FC always uses a directly measured matched control sealed by `MeasuredControlPairer`; `match_official_controls()` requires an explicit chemical-to-DMSO/Water map and exact metadata keys. Bare control arrays and `control = endpoint - FC` are forbidden at the evaluator Interface.
- Official context/drug residuals use outer-fit frozen references. Evaluation-centered residuals remain a separately labeled historical sensitivity estimand.
- Official high-effect proteins use `abs(log2 FC) > 1`; the fit-quantile threshold remains an auxiliary sensitivity policy.
- Evaluation-centered residuals and individuality require at least two common finite observations per `group × protein`.
- Every compared model uses the same evaluation cohort and protein panel.
- Reports validate scalar aggregates and portable provenance before atomically writing. No identities, vectors, paths, prompts, or predictions are persisted.
- External GPT-compatible providers are disabled by default and accept only pinned public fixtures.

See [CONTEXT.md](CONTEXT.md) for domain terms and [ADR 0001](docs/adr/0001-unified-research-layer.md) for the migration decision.

Current verification outcome: [reproducibility report](reports/reproducibility-current/REPORT.md), [test record](reports/reproducibility-current/TEST_RECORD.md), and [independent final audit](reports/reproducibility-current/FINAL_AUDIT.md).
