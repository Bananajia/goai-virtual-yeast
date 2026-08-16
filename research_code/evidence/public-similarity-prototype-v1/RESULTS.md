# Public-similarity experiment results

## Technical summary

P0, P1, and P2 all failed their preregistered support decisions. P1 showed a
positive mean PCC change against C0 in each scenario, but the RMSE direction or
strict fold-majority requirement failed, and P1 passed none of the nine
scenario-relevant null comparisons. P2 did not improve consistently over P1
and could not receive secondary support after the primary P1 failure.

These conclusions apply to the frozen public feature views, all-ITT fallback
policy, outer-fit estimators, and OOD splits used here. They do not establish
that public similarity has no predictive value in other representations or
experimental designs.

## All-ITT comparisons did not clear the joint gate

`ΔPCC` is candidate minus comparator. `RMSE improvement` is comparator minus
candidate, so positive values favor the candidate. A comparison required both
mean improvements to be strictly positive and both metrics to improve in a
strict majority of folds: 3/5 for whole-drug and 3/4 for whole-strain or
both-unknown.

| Scenario | Comparison | Mean ΔPCC | Mean RMSE improvement | Positive PCC folds | Positive RMSE folds | Passed |
|---|---|---:|---:|---:|---:|:---:|
| Whole-drug | P0 vs C0 | -0.011899 | -0.001769 | 2/5 | 1/5 | No |
| Whole-drug | P1 vs C0 | +0.000543 | -0.000974 | 3/5 | 2/5 | No |
| Whole-drug | P2 vs P1 | -0.019762 | +0.000865 | 1/5 | 3/5 | No |
| Whole-strain | P0 vs C0 | +0.030833 | +0.001164 | 3/4 | 2/4 | No |
| Whole-strain | P1 vs C0 | +0.063254 | +0.002948 | 2/4 | 2/4 | No |
| Whole-strain | P2 vs P1 | -0.016143 | -0.001483 | 0/4 | 1/4 | No |
| Both-unknown | P0 vs C0 | -0.010444 | -0.001450 | 1/4 | 1/4 | No |
| Both-unknown | P1 vs C0 | +0.003563 | -0.001445 | 1/4 | 0/4 | No |
| Both-unknown | P2 vs P1 | -0.002449 | +0.001409 | 1/4 | 2/4 | No |

All folds in these comparisons were finite. The negative decision therefore
comes from direction and stability, not from silently dropping an invalid
fold.

## P1 did not separate from matched nulls

The unique primary decision was conjunctive: P1 had to beat C0 and every
scenario-relevant null in all three scenarios. None of the nine P1-versus-null
comparisons passed. Some individual mean changes were positive, but no null
comparison simultaneously cleared positive mean PCC, positive mean RMSE
improvement, and the strict majority requirement for both metrics.

This prevents attributing the observed P1 variation to the intended public
drug/strain similarity structure. The separate drug-only signal,
strain-only signal, and joint dual-view increment labels also remained false.

## Coverage and estimand

The evaluation used 4,544 acquisition-aware condition aggregates and a frozen
384-protein panel. The all-ITT population comprised 37 drugs, with strict
public structure coverage for 25 and mandatory C0 fallback for 12. Of four
train strains, three had public mappings and one used mandatory C0 fallback.
The bilateral covered subset contained 2,062 conditions; 2,482 conditions
entered the all-ITT fallback partition.

Covered-only results were retained as diagnostics, including explicit
unavailable rows when a covered fold had no denominator. They were never used
for promotion. This protects the decision from selecting a favorable covered
subset after seeing outcomes.

## Interpretation boundary

The reference policy pools matched DMSO and Water controls and is exploratory.
The reported metrics are train-only OOD validation results, not an official
competition score estimate. The result rules out promotion of these frozen
candidates; it does not rule out better public encoders, alternative
similarities, richer interaction models, or later confirmatory evaluation.

Aggregate evidence is hash-bound to production result
`d7bf7be873a18ff96ebeca4c18fa119309a78340c573f255ecb85b2799f413d2`
and independent replay
`f176e1f301c1b7e486e45364276651e3355a91524bea0bf26890b86881fecbe3`.
