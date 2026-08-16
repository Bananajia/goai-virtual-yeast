# Test record

Date: 2026-08-16

## Unified research layer

```text
uv run --locked python -m unittest discover -s tests -q
Ran 118 tests
OK (skipped=3)
```

The release checkout passes 115 tests. Three tests that require the optional
historical experiment tree are skipped because that tree is intentionally not
published in this repository.

```text
uv run --locked python -m unittest mijiao_predict_v0.test_mijiao_predict -q
Ran 7 tests
OK
```

The separate MiJiaoPredict suite verifies scoped expert selection, exact Ridge
fallback, missing feature handling, invalid expert output and route auditing.

The suite covers preprocessing, fit-only state, unknown metadata levels, grouped
OOD zero overlap, strict measured-control pairing, common masks, residual
singletons, prediction-NaN opt-out rejection, constant predictions, DEP policy
isolation, provider payload privacy, deterministic public fixtures, evidence
tampering and code inventory.

```text
find . -type f -name '*.py' ... | python3 -m py_compile
93 Python files
PASS
```

```text
uv lock --check
Resolved 27 packages
PASS
```

The common CLI exposes **29** experiment entries.

## Historical contract suites

Representative frozen experiment suites were run without fixed validation/test
truth and produced 128 passing synthetic/contract checks in total:

| Historical experiment | Checks |
|---|---:|
| fair architecture benchmark | 8 |
| external-knowledge Transformer | 21 |
| pairwise control-affine v2 | 5 |
| conditional latent uncertainty | 8 |
| named pathway tokens | 8 |
| drug-target local network | 9 |
| strain genome/CNV | 8 |
| strain LoF shrinkage preflight | 7 |
| loss objective ablation | 19 |
| structure generalization | 15 |
| nonlinear measured-control diagnostic | 7 |
| nonlinear no-control follow-up | 13 |
| **Total** | **128** |

## Aggregate evidence replay

```text
registry records: 34
golden records: 30
release-safe records: 11
records requested: 30
records passed: 30
records failed: 0
frozen metrics verified: 253
invalidated used as golden: 0
PASS
```

Source SHA-256 is checked before metric extraction. The replay reads only
aggregate Markdown/JSON, never competition matrices, identities, vectors,
weights or predictions.

The eleven release-safe current-study aggregate Adapters replay 11/11 records
and 223/223 frozen scalars. The larger 30/253 replay requires the optional
historical aggregate tree and is therefore reported as a full-archive audit,
not as a clean-checkout retraining claim.

The PubChem confirmation Adapter verifies aggregate results only: 25/37 strict
structures, 12 exact missing-structure fallbacks and rejection of all three
tested structure candidates. It ships no SMILES, identity crosswalk,
fingerprints, predictions, weights or private matrices.

The two public-knowledge Adapters independently replay 39 and 43 frozen
scalars. Their shipped sources are byte-identical to the audited aggregate
results and contain no entity joins/mappings, per-condition or per-protein
rows, public feature/response vectors, neighbours, predictions or weights.
The external-resource manifest separately discloses the public AID 1159580
CGM, PubChem/Peter similarity assets and the non-bit-reproducible interactive
Codex authoring seam.

The causal and similarity `RESULTS.md` sources are byte-identical to the
independently audited originals, with SHA-256
`db9725213406606144ddfabb228ad77138ca6e67910b174dd1914cc4f5751f17`
and `d5f5fb39ddf69db910e19b03a62d8200039798d7772358fec9f669d17b7b06e0`.
A directed release scan found no machine-local path, identity/structure field,
or artifact larger than 50 KiB in either Adapter payload or replay receipt.

## Official-facing scorecard contract

`evaluation/official_scorecard.py` routes the six published modules with the
declared 20/25/20/20/10/5 weights to their applicable OOD splits. It does not
combine them into a weighted total because the published material does not
specify a reproducible within-module aggregation. Reproducibility/compliance
remains a gate, and the separately announced open-source contribution item is
reported independently.

## Determinism and end-to-end fixtures

- Public RNA mini: two independent offline runs produced byte-identical
  `RESULTS.json` and `REPORT.md`.
- Local `qwen3:8b` public-only smoke: one anonymous case reproduced byte-for-byte;
  the six-case run stopped fail-closed on an invalid schema at anonymous case 2,
  emitted no partial score, and passed the artifact leakage scan.
- Synthetic mean (seed 7): Endpoint PCC 0.995066 with condition variance ratio 0,
  confirming the average-value collapse is detected.
- Synthetic Metadata Ridge (seed 11): Raw-FC PCC 0.999994, condition variance ratio
  0.999841 and Endpoint RMSE 0.003759 on a known recoverable mechanism.
- The LIVE Metadata Ridge train/predict CLI is covered by deterministic tiny
  fixtures and failure-path tests only. It was not formally retrained on the
  private competition matrix for this release snapshot, so the synthetic
  metrics above are not presented as a competition-data result.
- Code inventory: 101 historical experiment directories, 448 Python files and
  121 test files; no absolute or private-data path is emitted.
- Nonlinear composition evidence: the two-stage aggregate Adapter verifies one
  record and 22 scalars; the no-control molecular branch remains rejected.

## Scope

This record proves the new code layer, metric contracts, public fixture and
frozen aggregate evidence are reproducible. It does not claim full source-level
retraining for experiments whose per-sample predictions were intentionally not
persisted, for the LIVE Metadata Ridge on private competition data, nor for the
two router lineages whose source is missing.
