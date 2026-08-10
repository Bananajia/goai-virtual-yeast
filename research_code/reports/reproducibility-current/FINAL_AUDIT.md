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
- Full research archive: 81/81 unified tests passed. The final clean public
  checkout discovered the same 81 tests: 78 passed and 3 optional
  missing-history tests skipped explicitly.
- 76 Python files compiled.
- `uv lock --check` resolved 27 packages.
- 20 experiments are discoverable through the common CLI.
- 22/22 golden evidence records and 75/75 frozen metrics replayed; zero
  invalidated records were accepted as golden.
- In the clean release, the three bundled aggregate Adapters replayed 3/3
  records and 45/45 frozen scalars.
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
