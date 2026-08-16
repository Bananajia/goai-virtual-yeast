# PubChem structure confirmatory v1 — release Adapter test record

## Frozen aggregate source

- Source: `RESULTS.md`.
- Source SHA-256:
  `4f1837c02604874f58ea1abe6d5659107ba2931fe4ebec7d2717afaa1c8172d4`.
- Expected aggregate scalars: **20**.
- Adapter run name: `pubchem_structure_confirmatory_evidence`.

## TDD integration

The experiment-discovery test first failed because the Adapter was absent, then
passed after the one-file Adapter and default registry registration were added.
The evidence-registry test next failed because the frozen record was absent,
then passed after the compact source and hash-locked registry entry were added.
The release-boundary test finally failed because this test receipt was absent,
then passed after the receipt was added.

## Directed checks

- Default experiment discovery: **PASS**.
- Evidence registry parse and status lookup: **PASS**.
- Source-hash and 20-scalar aggregate replay: **PASS**.
- Release-boundary scan for machine-local paths, identity fields, molecular
  strings, fold identifiers and fitted weights: **PASS**.
- Full current research-code suite: **110/110 PASS; 0 skipped**.

These checks validate the release-safe aggregate Adapter. They do not retrain
the private confirmatory study or reconstruct its entity mappings, fold rows,
predictions, feature vectors or fitted parameters.
