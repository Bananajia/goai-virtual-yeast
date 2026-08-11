# Release audit

Audit date: 2026-08-11

## Published scope

- One 52-page A4 technical report authored by 小米蕉队.
- The `research_code/` unified execution layer, public fixtures, aggregate reports and tests.
- The submission-level open-source/data disclosure and external-resource manifest.
- No historical private experiment tree and no competition dataset.

## Verification

- Python test discovery: 106 tests were discovered; 103 passed and 3 optional historical-evidence tests were skipped because that tree is intentionally not distributed.
- Python compilation: all 81 published Python source files compiled successfully; the unified CLI listed 21 experiments.
- Release-safe evidence replay: loss ablation, structure generalization, nonlinear composition and PubChem structure confirmation replayed 4/4 records and 65/65 frozen aggregate scalars from files included in this repository. They do not retrain the private studies.
- Full project evidence audit: the private local research tree replayed 23/23 golden records and 95/95 metrics before release packaging; the clean repository intentionally omits older private-source evidence required for that full replay.
- Dependency lock: `uv lock --check` passed with 27 resolved packages.
- Archive/file review: no cache directory, Python bytecode, environment file, credential file, model weight, database, archive or structured competition-data file is present.
- Path review: no personal absolute path or local-file URI is present.
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

## Expected protective strings

The source intentionally contains strings such as `private-data`, `/Users/` and `.codex/private` inside validators and adversarial tests. They are rejection patterns, not paths to published data. The fake value `fixture-key` is injected only into a mocked transport and never leaves the test process.

## Data boundary

Competition matrices, sample identities, private entity mappings, protein vectors, per-sample predictions, prompts/responses and external-service credentials are not included. Public fixtures retain source identifiers and hashes so their provenance can be audited independently.
