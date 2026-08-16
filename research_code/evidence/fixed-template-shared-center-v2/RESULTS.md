# Fixed-template transfer after query-disjoint shared centering

Date: 2026-08-14

## Frozen scope and estimand

- Shared biological contexts: **93**
- Protein coordinates: **5,243**
- Other treated entities in the shared center: **35**
- Fixed donor scale: **0.25**
- Both query entities excluded from every fitted center: **true**
- Target values used for fitting: **false**
- Official TRAIN numeric rows decoded: **5,920**
- Validation/test numeric rows decoded: **0**

The primary center is an equal-entity finite mean for each context-by-protein
cell. MSE is scored on the complete centered residual, with whole contexts as
the bootstrap unit. A positive gain would indicate improvement over the zero-
residual baseline.

## Frozen aggregate results

| Center | Contexts | Baseline MSE | Candidate MSE | MSE gain | 95% CI low | 95% CI high | Improved contexts |
|---|---:|---:|---:|---:|---:|---:|---:|
| shared-reference primary | 93 | 0.05313951966504137 | 0.058487852792623383 | -0.10064699796487796 | -0.1218971412242478 | -0.07997399859781272 | 11 |
| exact-batch sensitivity | 93 | 0.057299704695740694 | 0.060121574248163216 | -0.04924754093248027 | -0.05951888811702177 | -0.03907834031509197 | 12 |

## Decision and boundary

**VALIDATED_REJECTED / TRANSFER NOT SUPPORTED.** The fixed template worsened
primary MSE by 10.06%, with the whole-context interval entirely below zero and
only 11/93 contexts improving. The exact-batch sensitivity also worsened MSE.
A weak pattern cosine in a sensitivity branch is not sufficient evidence of
predictive transfer when the prespecified complete-residual loss deteriorates.

This source is aggregate-only and anonymous. It stores no query identity,
context label, sample value, protein value/vector, bootstrap draw, prediction,
or machine-local source path. It is a TRAIN-only diagnosis, not an independent
unknown-entity confirmation and not a claim that the two mechanisms are wholly
unrelated.
