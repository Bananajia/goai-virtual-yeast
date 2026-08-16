# Public causal residual v1 — release Adapter test record

## Frozen aggregate source

- Source: `RESULTS.md`.
- Source SHA-256:
  `db9725213406606144ddfabb228ad77138ca6e67910b174dd1914cc4f5751f17`.
- Expected aggregate scalars: **39**.
- Adapter run name: `public_causal_residual_evidence`.

The shipped source is byte-identical to the independently audited aggregate
result. It is not a copy of the training directory or a retraining entrypoint.

## TDD integration

The registry-run test first failed because the named Adapter was absent. It
passed after the one-file Adapter, hash-locked evidence record and default
registry registration were added. A second release-boundary test then failed
because this receipt was absent; it passed after both public-knowledge receipts
were added.

## Directed checks

- Default experiment discovery and shared run contract: **PASS**.
- Source-hash and 39-scalar aggregate replay: **PASS**.
- Status and release-safe persistence contract: **PASS**.
- Scan for machine-local paths, identity fields and molecular strings: **PASS**.
- Full current research-code suite: **110/110 PASS; 0 skipped**.

These checks do not recreate entity joins, prompts, causal chains, mechanism
axes, protein responses, predictions, fitted parameters or private training.
The complete current-suite result is recorded in
`reports/reproducibility-current/TEST_RECORD.md`.
