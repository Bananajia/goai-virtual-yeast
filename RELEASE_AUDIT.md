# Release audit

Audit date: 2026-08-10

## Published scope

- One 48-page A4 technical report authored by 小米蕉队.
- The `research_code/` unified execution layer, public fixtures, aggregate reports and tests.
- No historical private experiment tree and no competition dataset.

## Verification

- Python test discovery: 81 tests were discovered; 78 passed and 3 optional historical-evidence tests were skipped because that tree is intentionally not distributed.
- Python compilation: all 76 published Python source files compiled successfully; the unified CLI listed 20 experiments.
- Release-safe evidence replay: loss ablation, structure generalization and nonlinear composition replayed 3/3 records and 45/45 frozen aggregate scalars from files included in this repository. They do not retrain the private studies.
- Full project evidence audit: the private local research tree replayed 22/22 golden records and 75/75 metrics before release packaging; the clean repository intentionally omits the older private-source evidence files required for that full replay.
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

## Expected protective strings

The source intentionally contains strings such as `private-data`, `/Users/` and `.codex/private` inside validators and adversarial tests. They are rejection patterns, not paths to published data. The fake value `fixture-key` is injected only into a mocked transport and never leaves the test process.

## Data boundary

Competition matrices, sample identities, private entity mappings, protein vectors, per-sample predictions, prompts/responses and external-service credentials are not included. Public fixtures retain source identifiers and hashes so their provenance can be audited independently.
