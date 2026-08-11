# LIVE metadata Ridge source-stage addendum

Date: 2026-08-11

This addendum records the source-stage verification added after the organizer
merged the virtual-cell direction into one open leaderboard and strongly
recommended complete training/inference source. It supplements, but does not
rewrite, the independent 2026-08-10 audit snapshot.

## Added LIVE path

- `research_cli.py train-metadata-ridge` reads caller-supplied local metadata,
  raw proteome and config paths, and refuses any fit row whose
  `split_final` is not `train`.
- Raw finite intensities `<=0` fail closed. Missingness, log2 conversion,
  metadata vocabularies/statistics and Ridge fitting use the train-only slice.
- An all-train-missing filtered protein uses the config-frozen median of all
  finite train log2 cells. The computed value and policy are stored in the
  artifact manifest.
- Training atomically publishes `model.npz` and `manifest.json` only after the
  model hash, array shapes, encoder/model dimensions and output contract pass.
- `predict-metadata-ridge` accepts the latest official template as a unique
  ordered subset of artifact proteins, restores/reorders predictions, validates
  finite log2 output through `SubmissionContract`, and atomically writes the
  requested CSV.

The generated artifact contains fitted category vocabularies and official
protein names. It is a local private runtime product and is intentionally
excluded by `.gitignore`; only the training/inference source and tiny synthetic
fixtures are release candidates.

## Verification receipt

A fresh source-only copy, without the historical experiment tree or an existing
virtual environment, completed:

```text
uv sync --locked --extra dev
Resolved 27 packages

python -m unittest discover -s tests -v
Ran 106 tests
OK (skipped=3 optional historical-tree tests)

python -m compileall ...
81 published Python files
PASS

research_cli.py list
21 aggregate/synthetic/public experiment entries
```

Seven integration tests exercise the public CLI: train→artifact→prediction,
strict train-only roles, manifest seed/parameter/hash provenance, all-missing
fallback, official metadata headers, template protein subsets/unknown rejection,
and finite non-positive raw-intensity rejection. No competition data, external
API or model download was used in this verification.

The same release subsequently added the official-facing split/scorecard contract
and the release-safe PubChem structure-confirmation Adapter. These additions
account for the updated test, Python-file and CLI counts above.

## Disclosure receipt

- `OPEN_SOURCE_AND_DATA.md` states the Apache-2.0 scope, private exclusions,
  dependencies, commercial-API/closed-model status and 5% reusable contribution.
- `external_resources/manifest.json` indexes ten official/public data and local
  model resources, distinguishing LIVE use, aggregate-only pilots, public-only
  smoke tests and not-yet-frozen recommendations.
- GitHub and ZIP publication remain a separate audited release step: the clean
  checkout must repeat the tests, regenerate `SHA256SUMS`, and rebuild the
  archive from the final committed tree.
