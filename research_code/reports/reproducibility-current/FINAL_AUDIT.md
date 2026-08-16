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
- Current source tree: 110/110 unified tests passed; 0 skipped.
- 84 Python files compiled.
- `uv lock --check` resolved 27 packages.
- 23 experiments are discoverable through the common CLI.
- The registry contains 28 records: 25 golden, one invalidated and two
  source-missing lineages.
- 25/25 golden evidence records and 177/177 frozen metrics replayed; zero
  invalidated records were accepted as golden.
- The six release-safe aggregate Adapters (loss, structure, nonlinear
  composition, PubChem/RDKit confirmation, public causal residual and public
  similarity prototype) replayed 6/6 records and 147/147 frozen scalars. The
  two new public-knowledge sources are byte-identical to their audited
  aggregate results and ship no joins/mappings, per-condition/per-protein
  rows, feature/response vectors, neighbours, predictions or weights.
- The resource manifest discloses AID 1159580, the PubChem/Peter similarity
  assets and the interactive Codex closed commercial authoring seam. No
  competition data was supplied to that seam and it is not called during
  training/inference; the frozen output is hash-bound, while the unavailable
  exact service snapshot is correctly marked non-reproducible.
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
