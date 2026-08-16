# Public causal residual pilot v1 — result

## Decision

**Integrity: PASS. Scientific gate: FAIL. Promotion: no.**

This experiment tested whether a frozen, public-data-only 23-axis signed
representation adds whole-drug OOD predictive value beyond a strict PubChem
structure baseline. It is a structured causal-hypothesis feature artifact, not
a native embedding and not evidence that a treatment effect was identified.

The public bundle contains 96 PubChem compounds and 288 fixed association
edges. The train-only protein experiment covers 37 treated identities: 25 have
the strict PubChem structure representation, 6 have an exact public-axis join,
and the other 31 rows of the causal candidate fall back bit-for-bit to the
structure baseline.

## Primary five-fold means

PCC is higher-is-better and RMSE is lower-is-better. Values below are the
outer-fit context-residual metrics.

| Tier | M0 context | M1 PubChem | raw-CGM | M2 signed axes |
|---|---:|---:|---:|---:|
| all 37 — PCC | 0.000000 | 0.023613 | 0.022771 | 0.022659 |
| all 37 — RMSE | 0.358180 | 0.361906 | 0.361867 | 0.361917 |
| covered 6 — PCC | 0.000000 | 0.098530 | 0.090653 | 0.090476 |
| covered 6 — RMSE | 0.379935 | 0.375828 | 0.375644 | 0.375995 |

For the delta table, both columns are oriented so that a positive value means
M2 is better. The parenthesized counts are positive folds out of five.

| Comparison | Delta PCC | Delta RMSE |
|---|---:|---:|
| all 37: M2 vs M1 | -0.000954 (1/5) | -0.0000117 (1/5) |
| covered 6: M2 vs M1 | -0.008054 (1/5) | -0.000168 (1/5) |
| covered 6: M2 vs raw-CGM | -0.000176 (2/5) | -0.000351 (2/5) |

M2 also failed to beat entity derangement, degree-preserving rewiring,
same-sparsity random axes, or unsigned axes. M2 and the sign-shuffle control
tied exactly in all 60 relevant aggregate cells, so this particular null is
not identifiable in the present six-identity linear-Ridge design. Removing
that null would not change the decision because G1--G5 fail independently.

## Interpretation boundary

The supported statement is narrow: in this coverage-informed exploratory
pilot, the fixed signed-confidence representation did not add predictive value
over strict PubChem structure or the raw public CGM axes. This does not show
that language-model reasoning is generally ineffective, does not falsify a
biological mechanism, and is not an official competition score. The pooled
DMSO/Water control policy is an explicitly exploratory sensitivity because a
verified chemical-to-vehicle map was unavailable.

The public RNA blind gate had already failed before this protein-residual
experiment, so this branch was non-promotable regardless of its downstream
score.

## Verification

- Frozen result SHA-256: `de6a0edd5658a5e4e774beea22062e059108ce69c802a84ce199522cc2280bb0`
- Independent replay receipt SHA-256: `92a4ffdd86cfae1c164b22e1b2cda576b4952dd6ea325180ecfb3d8d66ab0499`
- Replayed exactly: 90 fold rows, 108 summary rows, and 84 comparison rows
- G1--G6: all false; every gate comparison had five finite folds
- Validation and test numeric rows read: zero

See `VALIDATION_REPORT.md` for the audit trail and `MODEL_DISCLOSURE.md` for
the closed-model disclosure.
