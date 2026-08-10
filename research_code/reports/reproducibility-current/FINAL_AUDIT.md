# Final independent audit

Date: 2026-08-10
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
- Aggregate reporting validates scalar metrics, non-negative counts, boolean
  contracts, portable provenance and safe notes before atomic output.
- Full research archive: 75/75 unified tests passed. Clean public checkout:
  72 passed and three optional historical-evidence replay tests skipped.
- 73 Python files compiled.
- `uv lock --check` resolved 27 packages.
- 17 experiments are discoverable through the common CLI.
- 19/19 persistent evidence records and 30/30 frozen metrics replayed; zero
  invalidated records were accepted as golden.
- Fixed-seed synthetic mean/Ridge results match the saved artifacts.
- The offline public RNA result is deterministic.
- The local Qwen six-case pilot correctly returned `BLOCKED` after invalid
  structured output and did not retain partial metrics.
- No competition matrix was read during this independent audit.

## External dependencies before an official full-data replay

- A machine-readable chemical-to-DMSO/Water mapping.
- The latest official submission feature template (protein names, count, order).
- Fresh train-only OOF predictions if historical residual/DEP results are to be
  rescored under the new fit-frozen and fixed-threshold definitions.
