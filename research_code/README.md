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
python3 -m unittest discover -s tests -v
python3 research_cli.py list
python3 research_cli.py run synthetic_mean_baseline --scope synthetic --output reports/synthetic_mean_baseline
```

The standalone submission package runs the executable core and public-only tests;
tests that replay the optional historical experiment tree are skipped when that
tree is not present.

The optional environment can be locked with:

```bash
uv sync --extra dev
uv run python -m unittest discover -s tests -v
```

## Non-negotiable contracts

- Missingness thresholds are fit on training rows only; `>80%` is removed and exactly `80%` remains when the 80% policy is selected.
- Raw-FC always uses a directly measured matched control sealed by `MeasuredControlPairer`; bare control arrays and `control = endpoint - FC` are forbidden at the evaluator Interface.
- Centered residuals require at least two common finite observations per `group × protein`.
- Every compared model uses the same evaluation cohort and protein panel.
- Reports validate scalar aggregates and portable provenance before atomically writing. No identities, vectors, paths, prompts, or predictions are persisted.
- External GPT-compatible providers are disabled by default and accept only pinned public fixtures.

See [CONTEXT.md](CONTEXT.md) for domain terms and [ADR 0001](docs/adr/0001-unified-research-layer.md) for the migration decision.

Current verification outcome: [reproducibility report](reports/reproducibility-current/REPORT.md), [test record](reports/reproducibility-current/TEST_RECORD.md), and [independent final audit](reports/reproducibility-current/FINAL_AUDIT.md).
