# Final independent audit

Date: 2026-08-11
Verdict: **PASS WITH DECLARED EXTERNAL DEPENDENCIES**

## Verified

- Folder responsibilities are separated and experiments use
  `Experiment.run(RunContext)`.
- Historical results enter through read-only aggregate evidence Adapters.
- Public providers and the private-data pipeline are separated; OpenAI is
  disabled by default and Ollama is loopback-only.
- Evaluation accepts only a `MeasuredControlPairer`-verified paired response;
  bare arrays, endpoint mismatch, a forged unsealed response, and a sensitivity
  estimand fail closed.
- Official vehicle matching, train-only target roles, strict `<80%`
  missingness, fit-frozen residual identity/order, fixed `|FC|>1` DEP, and
  submission ID/feature/log2/finite contracts have dedicated negative tests.
- The official-facing scorecard routes the six published modules and their
  20/25/20/20/10/5 weights by split, but deliberately does not synthesize a
  total score because no reproducible within-module aggregation was published.
  Reproducibility/compliance remains a gate and open-source contribution is
  disclosed separately.
- Aggregate reporting validates scalar metrics, non-negative counts, boolean
  contracts, portable provenance and safe notes before atomic output.
- Current source tree: 106/106 unified tests passed.
- 81 Python files compiled.
- `uv lock --check` resolved 27 packages.
- 21 experiments are discoverable through the common CLI.
- 23/23 golden evidence records and 95/95 frozen metrics replayed; zero
  invalidated records were accepted as golden.
- The four release-safe aggregate Adapters (loss, structure, nonlinear
  composition and PubChem/RDKit confirmation) replayed 4/4 records and 65/65
  frozen scalars. The PubChem Adapter ships no molecular identities, structures,
  fingerprints, predictions or weights.
- Fixed-seed synthetic mean/Ridge results match the saved artifacts.
- The offline public RNA result is deterministic.
- The local Qwen six-case pilot correctly returned `BLOCKED` after invalid
  structured output and did not retain partial metrics.
- LIVE Metadata Ridge train/predict is validated only on deterministic tiny
  fixtures and failure paths in this snapshot. No formal private competition
  data retraining or scoring is claimed.
- No competition matrix was read during this independent audit.

## External dependencies before an official full-data replay

- A machine-readable chemical-to-DMSO/Water mapping.
- The latest official submission feature template (protein names, count, order).
- Fresh train-only OOF predictions if historical residual/DEP results are to be
  rescored under the new fit-frozen and fixed-threshold definitions.
