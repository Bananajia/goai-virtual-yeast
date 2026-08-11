# Structure-generalization v1 — release-safe aggregate evidence

## Decision

**VALIDATED_REJECTED / NO-PROMOTION.** The train-only grouped-OOD pilot is
methodologically reproducible, but none of the three structure candidates beats
the stronger fold-specific M0/C0 comparator on the required all-ITT endpoint,
Raw-FC, and condition-individuality outcomes jointly.

This file contains aggregate scalars only. It contains no sample, chemical,
strain or protein identity; no prediction, embedding, model weight or protein
vector; and no machine-specific path. The clean Adapter verifies this file but
does not claim to retrain the private pilot.

## Frozen scope

- Official train rows: **5,920**.
- Source output coordinates: **5,243**.
- Current-release train-only missing fraction strictly below 80% retains
  **4,422** coordinates; coordinates exactly on the 80% boundary: **0**.
- Response-blind pilot panel: **384** coordinates.
- Treated drug identities in the primary all-ITT analysis: **37**.
- Strict structure coverage: **22 covered**, **15 explicit missing/fallback**.
- Structure representation: ChEBI release 253 **largest-fragment
  canonical-isomeric parent**. This is not a full RDKit MolStandardize workflow.
- OOD scenarios: whole chemical and whole Kbio, five grouped folds each.
- Fixed validation numeric rows read: **0**; test numeric rows read: **0**.

## Candidates and comparators

- **M0:** direct masked metadata Ridge on the standardized endpoint matrix.
- **C0:** context-only rank-32 latent Ridge.
- **M1:** top-5 Morgan/Tanimoto response transfer with same-drug donors excluded.
- **M2:** CPA-style rank-32 additive Ridge. It tests compositional additivity; it
  is not an exact reproduction of CPA or chemCPA.
- **M3:** low-rank structure-by-context bilinear Ridge.

All candidate deltas below are relative to the stronger per-fold M0/C0
comparator. They are oriented so **positive is better**, including RMSE
improvement. Parentheses give improving folds out of five.

| OOD scenario | Candidate | Endpoint PCC | Endpoint RMSE | Raw-FC PCC | Context-residual PCC | Individuality PCC |
|---|---|---:|---:|---:|---:|---:|
| Whole chemical | M1 Tanimoto transfer | -0.00160 (0/5) | -0.02176 (0/5) | -0.00657 (1/5) | -0.00385 (1/5) | -0.00964 (0/5) |
| Whole chemical | M2 CPA-style additive | -0.00101 (3/5) | -0.01118 (3/5) | -0.01095 (0/5) | +0.00517 (3/5) | -0.00382 (2/5) |
| Whole chemical | M3 structure-context bilinear | -0.00101 (3/5) | -0.01096 (3/5) | -0.00998 (0/5) | +0.00832 (4/5) | -0.00277 (2/5) |
| Whole Kbio | M1 Tanimoto transfer | -0.00995 (0/5) | -0.13462 (0/5) | -0.08876 (0/5) | -0.20180 (0/5) | -0.10634 (0/5) |
| Whole Kbio | M2 CPA-style additive | -0.00721 (0/5) | -0.10054 (0/5) | -0.07173 (0/5) | -0.13006 (0/5) | -0.07650 (0/5) |
| Whole Kbio | M3 structure-context bilinear | -0.00820 (0/5) | -0.11430 (0/5) | -0.07292 (0/5) | -0.12045 (0/5) | -0.07566 (0/5) |

The whole-chemical context-residual gains of M2 and M3 are secondary diagnostic
signals. They do not override the all-ITT losses in endpoint, Raw-FC and
individuality.

## Structure-attribution control

On the structure-covered whole-chemical cohort, real structure mappings had
mixed but nonzero advantages over identity-breaking controls:

| Real mapping vs matched broken mapping | Endpoint RMSE improvement | Improving folds | Individuality RMSE improvement | Improving folds |
|---|---:|---:|---:|---:|
| M1 vs permuted Tanimoto | +0.00650 | 3/5 | +0.00561 | 3/5 |
| M2 vs permuted additive | +0.01279 | 3/5 | +0.01805 | 4/5 |
| M3 vs permuted bilinear | +0.01417 | 3/5 | +0.01949 | 4/5 |

PCC evidence was not uniformly positive, and the covered-only cohort cannot
replace the frozen all-ITT promotion analysis. The defensible conclusion is
therefore **weak, mixed structure-specific evidence without model promotion**.

## Reproducibility boundary

The independent aggregate replay rebuilt **60** summaries and **576** paired
comparisons from **300** fold/model/tier rows. Maximum discrepancies were
6.66e-16 for summaries and 4.44e-16 for paired deltas. All mandatory all-ITT
gate metrics were finite and every candidate remained NO-PROMOTION.
