# Test record

Date: 2026-08-10

## Unified research layer

```text
PYTHONPATH=research_code python3 -m unittest discover -s research_code/tests -q
Ran 81 tests
OK
```

In the full private research archive all 81 tests pass. In the final clean
release checkout, all 81 tests were discovered: 78 passed and the 3 tests whose
optional historical source tree is intentionally not shipped skipped explicitly.

The suite covers preprocessing, fit-only state, unknown metadata levels, grouped
OOD zero overlap, strict measured-control pairing, common masks, residual
singletons, prediction-NaN opt-out rejection, constant predictions, DEP policy isolation, provider payload
privacy, deterministic public fixtures, evidence tampering and code inventory.

```text
find research_code -type f -name '*.py' ... | python3 -m py_compile
76 Python files
PASS
```

```text
uv lock --check
Resolved 27 packages
PASS
```

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
records requested: 22
records passed: 22
records failed: 0
frozen metrics verified: 75
invalidated used as golden: 0
PASS
```

Source SHA-256 is checked before metric extraction. The replay reads only
aggregate Markdown/JSON, never competition matrices, identities, vectors,
weights or predictions.

The clean release independently replays the three release-safe current-study
Adapters (loss, structure and nonlinear composition): 3/3 records and 45/45
frozen scalars pass. The larger 22/75 replay requires the optional historical
aggregate tree and is therefore reported as a full-archive audit, not as a
clean-checkout retraining claim.

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
- Code inventory: 99 historical experiment directories, 440 Python files and
  119 test files; no absolute or private-data path is emitted.
- Nonlinear composition evidence: the two-stage aggregate Adapter verifies one
  record and 22 scalars; the no-control molecular branch remains rejected.

## Scope

This record proves the new code layer, metric contracts, public fixture and
frozen aggregate evidence are reproducible. It does not claim full source-level
retraining for experiments whose per-sample predictions were intentionally not
persisted, nor for the two router lineages whose source is missing.
