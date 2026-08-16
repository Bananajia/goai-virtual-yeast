# Public similarity prototype v1 — release Adapter test record

## Frozen aggregate source

- Source: `RESULTS.md`.
- Source SHA-256:
  `d5f5fb39ddf69db910e19b03a62d8200039798d7772358fec9f669d17b7b06e0`.
- Expected aggregate scalars: **43**.
- Adapter run name: `public_similarity_prototype_evidence`.

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
- Source-hash and 43-scalar aggregate replay: **PASS**.
- Status and release-safe persistence contract: **PASS**.
- Scan for machine-local paths, identity fields and molecular strings: **PASS**.
- Full current research-code suite: **110/110 PASS; 0 skipped**.

These checks do not recreate entity mappings, molecular or genome features,
neighbour lists, response vectors, predictions, fitted parameters or private
training. The complete current-suite result is recorded in
`reports/reproducibility-current/TEST_RECORD.md`.
