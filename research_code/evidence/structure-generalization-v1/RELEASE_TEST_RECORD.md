# Structure-generalization v1 — clean Adapter test record

Validation date: 2026-08-10

## Release checks

- Unified research-code suite: **79/79 PASS**.
- Named experiment discovery includes
  `structure_generalization_evidence`.
- Source SHA-256 and **15** frozen aggregate scalars replay: **PASS**.
- Evidence registry JSON parse: **PASS**.
- Mobile digest builder JavaScript syntax: **PASS**.
- New Adapter/evidence/report-source privacy scan: **PASS**; no machine-specific
  absolute path, private-data path, credential, identity, prediction, embedding,
  weight or protein vector is present.

## Boundary

These checks validate the aggregate-only evidence Adapter. They do not claim
that the private 384-coordinate training run can be repeated without the
competition data and its historical shared dependencies.
