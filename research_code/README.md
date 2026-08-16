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
| `evaluation/` | canonical metrics plus the official-facing split/scorecard contract (no invented total) |
| `reporting/` | aggregate-only result writers |
| `evidence/` | validity and golden-result registry for historical runs |
| `mijiao_predict_v0/` | evidence-gated MiJiaoPredict orchestration, expert contracts, route audit and exact core fallback |
| `tests/` | public-interface and leakage-regression tests |

## Quick start

```bash
cd research_code
uv sync --locked --extra dev
uv run --locked python -m unittest discover -s tests -v
uv run --locked python -m unittest mijiao_predict_v0.test_mijiao_predict -v
uv run --locked python research_cli.py list
uv run --locked python research_cli.py run synthetic_mean_baseline --scope synthetic --output reports/synthetic_mean_baseline
uv run --locked python research_cli.py run loss_ablation_evidence --scope aggregate-only --data-root .. --output reports/loss-ablation-replay
uv run --locked python research_cli.py run structure_generalization_evidence --scope aggregate-only --data-root .. --output reports/structure-generalization-replay
uv run --locked python research_cli.py run chemcpa_nonlinear_evidence --scope aggregate-only --data-root .. --output reports/chemcpa-nonlinear-replay
uv run --locked python research_cli.py run pubchem_structure_confirmatory_evidence --scope aggregate-only --data-root .. --output reports/pubchem-structure-confirmatory-replay
uv run --locked python research_cli.py run public_causal_residual_evidence --scope aggregate-only --data-root .. --output reports/public-causal-residual-replay
uv run --locked python research_cli.py run public_similarity_prototype_evidence --scope aggregate-only --data-root .. --output reports/public-similarity-prototype-replay
uv run --locked python research_cli.py run chx_centered_transfer_evidence --scope aggregate-only --data-root .. --output reports/chx-centered-transfer-replay
uv run --locked python research_cli.py run blind_llm_causal_pilot_evidence --scope aggregate-only --data-root .. --output reports/blind-llm-causal-pilot-replay
```

## LIVE competition metadata Ridge

The release-safe baseline accepts local CSV paths and never bundles competition
data. The train inputs must already be a **train-only local slice**: every
metadata row must have `split_final=train`. A mixed organizer train/validation
package is rejected rather than filtered silently.

```bash
uv run --locked python research_cli.py train-metadata-ridge \
  --metadata /authorized/local/train_metadata.csv \
  --proteome /authorized/local/train_proteome.csv \
  --config configs/metadata_ridge.json \
  --artifact-dir /authorized/local/artifacts/metadata-ridge \
  --seed 0

uv run --locked python research_cli.py predict-metadata-ridge \
  --artifact-dir /authorized/local/artifacts/metadata-ridge \
  --test-metadata /authorized/local/test_metadata.csv \
  --submission-template /authorized/local/submission_template.csv \
  --output /authorized/local/prediction.csv
```

Training fails closed on finite raw intensities `<=0`, fits missingness and all
metadata statistics on train only, and records seed, parameters, input hashes,
software versions and model hash in `manifest.json`. An all-train-missing
filtered protein receives the config-frozen median of all finite train log2
cells. Prediction follows the official template's sample order and its unique
ordered protein subset, validates finite log2 output through
`SubmissionContract`, and atomically writes `prediction.csv`. Generated model
artifacts contain fitted vocabularies and official feature names; keep them out
of the public repository.

## MiJiaoPredict v0

`mijiao_predict_v0.MiJiaoPredict` is the public orchestration interface for the
overall predictor. A complete Metadata Ridge prediction is supplied as the
core. A scoped residual or replacement expert can modify a row only when its
source is executable, its frozen status is `promoted_scoped`, the query matches
that scope, and the required feature view is present. Missing inputs, rejected
experts, invalid outputs and execution errors preserve the finite core exactly
and are recorded in a route audit. The repository does not relabel rejected
structure, knowledge or language-model pilots as enabled experts.

The standalone submission package runs the executable core and public-only tests;
tests that replay the optional historical experiment tree are skipped when that
tree is not present. Eleven release-safe aggregate Adapters ship compact,
identity-free evidence under `evidence/loss-ablation-v1/`,
`evidence/structure-generalization-v1/`,
`evidence/chemcpa-nonlinear-v1-v2/`,
`evidence/pubchem-structure-confirmatory-v1/`,
`evidence/public-causal-residual-v1/`, and
`evidence/public-similarity-prototype-v1/`,
`evidence/chemcpa-centered-direct-v1/`,
`evidence/fixed-template-shared-center-v2/`,
`evidence/txgemma-top5-prompt-v1/`,
`evidence/downstream-state-posthoc-v1/`, and
`evidence/blind-llm-causal-pilot-v1/`. Each Adapter verifies the source
hash before its frozen scalars. This makes the negative model-selection
decisions auditable; it does not retrain the private pilots or distribute
entity joins, per-condition/per-protein artifacts, vectors or fitted weights.

Every aggregate study has an explicit named experiment class in its own file,
all reusing `AggregateEvidenceExperiment`; legacy `build_experiment()` callers
remain supported. The still-running TxGemma generic-axis/off-axis protocol is a
non-golden `PENDING` registry entry and cannot emit a successful replay.

## Non-negotiable contracts

- Metadata and proteome rows are joined by unique `sample_ID`, never by current CSV row order.
- Fit-time labeled bundles must contain only `split_final=train`; validation/test truth fails closed.
- The LIVE CLI rejects finite raw intensities `<=0`; only original `NA` remains missing.
- The interpretation policy models proteins with missingness `<80%`. On the current release this gives 4,422 proteins, exactly the same panel as `<=80%`, because no protein lies exactly on the 80% boundary. The interpretation PDF's 4,232 count is not reproduced by its stated formula and is therefore not hard-coded.
- Submission row identities, protein names/order, finite values, and declared `log2` scale must pass `SubmissionContract`; the latest official feature template is authoritative.
- The template may select and reorder a unique subset of artifact proteins; a template protein absent from the artifact fails closed.
- Raw-FC always uses a directly measured matched control sealed by `MeasuredControlPairer`; `match_official_controls()` requires an explicit chemical-to-DMSO/Water map and exact metadata keys. Bare control arrays and `control = endpoint - FC` are forbidden at the evaluator Interface.
- Official control matching seals all source/strain/medium/temperature/time/instrument/plate roles; subset-key matching is available only through `match_exploratory_controls()` and cannot produce an official control contract.
- Official context/drug residuals use outer-fit frozen references with verified train-only provenance and disjoint fit/evaluation IDs. Evaluation-centered residuals remain a separately labeled historical sensitivity estimand.
- `OfficialScorecard` exposes the 20/25/20/20/10/5 module weights and the four split routes, but never synthesizes an official total. Reproducibility/compliance is a separate gate and the announced open-source 5% is disclosed separately.
- Official high-effect proteins use `abs(log2 FC) > 1`; the fit-quantile threshold remains an auxiliary sensitivity policy.
- Evaluation-centered residuals and individuality require at least two common finite observations per `group × protein`.
- Every compared model uses the same evaluation cohort and protein panel.
- Reports validate scalar aggregates and portable provenance before atomically writing. No identities, vectors, paths, prompts, or predictions are persisted.
- External GPT-compatible providers are disabled by default and accept only pinned public fixtures.

See [CONTEXT.md](CONTEXT.md) for domain terms and [ADR 0001](docs/adr/0001-unified-research-layer.md) for the migration decision.

Current verification outcome: [2026-08-11 LIVE baseline addendum](reports/reproducibility-current/LIVE_BASELINE_ADDENDUM_20260811.md), plus the preserved 2026-08-10 [reproducibility report](reports/reproducibility-current/REPORT.md), [test record](reports/reproducibility-current/TEST_RECORD.md), and [independent audit](reports/reproducibility-current/FINAL_AUDIT.md).
