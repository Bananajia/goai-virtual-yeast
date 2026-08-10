# Release audit

Audit date: 2026-08-10

## Published scope

- One 40-page A4 technical report authored by 小米蕉队.
- The `research_code/` unified execution layer, public fixtures, aggregate reports and tests.
- No historical private experiment tree and no competition dataset.

## Verification

- Python test discovery: 60 tests were discovered; 57 passed and 3 optional historical-evidence tests were skipped because that tree is intentionally not distributed.
- Dependency lock: `uv lock --check` passed with 27 resolved packages.
- Archive/file review: no cache directory, Python bytecode, environment file, credential file, model weight, database, archive or structured competition-data file is present.
- Path review: no personal absolute path or local-file URI is present.
- Credential-pattern review: no OpenAI, GitHub, AWS, Slack or private-key pattern is present.
- `detect-secrets 1.5.0`: all findings were reviewed as pinned SHA-256 hashes/model digests or the literal fake key used by a fail-closed provider test; none is a credential.

## Expected protective strings

The source intentionally contains strings such as `private-data`, `/Users/` and `.codex/private` inside validators and adversarial tests. They are rejection patterns, not paths to published data. The fake value `fixture-key` is injected only into a mocked transport and never leaves the test process.

## Data boundary

Competition matrices, sample identities, private entity mappings, protein vectors, per-sample predictions, prompts/responses and external-service credentials are not included. Public fixtures retain source identifiers and hashes so their provenance can be audited independently.
