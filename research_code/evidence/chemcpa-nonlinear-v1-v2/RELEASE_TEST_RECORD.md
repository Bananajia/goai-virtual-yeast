# Release integration test record

Date: 2026-08-10

## Frozen aggregate source

- SHA-256: `435f3127f8a338d5477944a326660d339cf82b248f51bb1ccf919d5b90c770b7`
- Registry status: `VALIDATED_REJECTED`
- Persistence: `PERSISTENT_RELEASE_SAFE`
- Expected aggregate scalars: 22

## TDD record

The initial adapter-registration, replay and aggregate-only safety tests failed as expected before
the adapter, registry record and compact evidence source existed. After implementation, all three
targeted tests passed.

## Final checks

- Unified research-code suite: **81 tests passed**.
- Evidence registry JSON parse: **PASS**.
- Source-hash and 22-scalar aggregate replay: **PASS**.
- Mobile report builder JavaScript syntax: **PASS**.
- LaTeX static scan: no duplicate labels, missing references, missing citations or checked
  environment-count mismatches.
- Release-safety scan: no machine-local location and no row/entity-level payload in
  the compact aggregate source.

No PDF compilation, mobile artifact generation or publication action was performed during this
integration check.
