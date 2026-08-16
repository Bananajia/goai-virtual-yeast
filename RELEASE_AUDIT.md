# Release audit

Audit date: 2026-08-16

## Published scope

- One 23-page A4 concise submission report authored by 小米蕉队.
- The `research_code/` unified execution layer, public fixtures, aggregate reports and tests.
- The submission-level open-source/data disclosure and external-resource manifest.
- No historical private experiment tree and no competition dataset.

## Verification

- Python test discovery: 118 tests were discovered; 115 passed and 3 optional historical-evidence tests were skipped because that tree is intentionally not distributed. The separate MiJiaoPredict contract suite passed 7/7 tests.
- Python compilation: all 93 published Python source files compiled successfully; the unified CLI listed 29 experiments.
- Release-safe evidence replay: 11 aggregate Adapters replay 11/11 records and 223/223 frozen aggregate scalars from files included in this repository. They do not retrain the private studies.
- Full project evidence audit: the local research tree replayed all 30 golden records and 253/253 metrics before release packaging; the registry contains 34 records in total, with non-golden invalidated, pending or source-missing provenance retained explicitly. The clean repository intentionally omits older private-source evidence required for that full replay.
- Dependency lock: `uv lock --check` passed with 27 resolved packages.
- Archive/file review: no cache directory, Python bytecode, environment file, credential file, model weight, database, archive or structured competition-data file is present.
- Path review: no operational personal absolute path or local-file URI is present; literal path fragments used by fail-closed validators and adversarial tests are documented below.
- Credential-pattern review: no OpenAI, GitHub, AWS, Slack or private-key pattern is present.
- `detect-secrets 1.5.0`: all findings were reviewed as pinned SHA-256 hashes/model digests or the literal fake key used by a fail-closed provider test; none is a credential.

## Competition-contract caveats

- The preprocessing formula is missingness `<80%`. On the currently released competition package it yields 4,422 modeled proteins; `<=80%` yields the same set because there are zero exact-boundary ties. The 4,232 count printed in the interpretation material cannot be reproduced from its displayed formula and is not hard-coded as machine truth.
- Official Raw-FC remains blocked until a machine-readable chemical-to-DMSO/Water mapping is supplied.
- Submission protein names, count and order are taken from the latest official feature template; the 5,243-coordinate source matrix does not itself define the submission width.
- Historical residual/DEP aggregates were not relabeled as fit-frozen or fixed-threshold scores without fresh per-sample OOF predictions.
- The official-facing scorecard exposes the announced 20/25/20/20/10/5 module weights and split routes but does not synthesize a total whose internal aggregation formula has not been released.
- The LIVE metadata Ridge training/prediction path is verified on deterministic tiny fixtures; this release does not claim a fresh 5,920-by-5,243 private-data training run.
- PubChem/RDKit increased strict structure coverage to 25/37, but all three frozen structure candidates failed promotion and therefore are not part of the LIVE predictor.
- The public drug--strain similarity prototype keeps all 37 drugs in the primary analysis with exact baseline fallback for missing public views. Its hard-cluster, soft-neighbor and partial-pooling candidates failed the frozen all-scenario/null gates; the positive mean in the unseen-strain scenario was only positive in 2/4 folds and is not promoted.
- The 23-axis public causal-hypothesis representation covers only 6/37 drugs and failed against both the strict PubChem structure baseline and raw public chemical-genetic axes. It is an exploratory predictive residual test, not identified treatment causality.
- An interactive OpenAI Codex closed commercial service was used once to help author a frozen public-only static causal-hypothesis asset. No competition entity list, response matrix, residual, prediction or evaluation result entered that service, and no online model is called during numerical training, inference, scoring or replay. Exact model snapshot and full prompt were not retained, so reproducibility is hash-based rather than generation-bit-reproducible.

## Expected protective strings

The source intentionally contains strings such as `private-data`, `/Users/` and `.codex/private` inside validators and adversarial tests. They are rejection patterns, not paths to published data. The fake value `fixture-key` is injected only into a mocked transport and never leaves the test process.

## Data boundary

Competition matrices, sample identities, private entity mappings, protein vectors, per-sample predictions, prompts/responses and external-service credentials are not included. Public fixtures retain source identifiers and hashes so their provenance can be audited independently.
