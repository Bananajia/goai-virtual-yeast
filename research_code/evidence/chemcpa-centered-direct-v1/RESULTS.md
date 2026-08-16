# chemCPA centered-direct whole-drug holdout

Date: 2026-08-14

## Frozen scope

- Canonical treated entities: **23**
- Biological contexts: **96**
- Protein coordinates: **5,243**
- Outer unit: one entire treated entity; inner tuning uses only the remaining entities.
- Numeric scope: official TRAIN only; validation/test numeric rows decoded: **0**.

## Response endpoint

| Arm | MacroMSE | MacroPCC | MSE gain vs baseline | PCC delta vs baseline | Entities with lower MSE |
|---|---:|---:|---:|---:|---:|
| response-only baseline | 0.21880349651077785 | 0.5118567088418347 | 0 | 0 | — |
| RDKit194 | 0.21844306674053757 | 0.5120770320277134 | 0.0016472760992762847 | 0.00022032318587872357 | 14 |
| chemCPA32 | 0.21874874769720326 | 0.5109498370877698 | 0.00025021909817557475 | -0.0009068717540648974 | 10 |
| external PCA32 | 0.2189787528212684 | 0.5112831371524881 | -0.0008009758220748342 | -0.0005735716893465748 | 15 |
| random MLP32 | 0.21899351530425565 | 0.5113044198794473 | -0.0008684449586409126 | -0.0005522889623873484 | 6 |

## Decision and boundary

**VALIDATED_REJECTED / NO-PROMOTION.** The chemCPA arm's small MSE trend did
not survive the predefined paired whole-entity uncertainty gate, and its PCC
delta was negative. RDKit also failed the stability gate. The 100 shuffled
label worlds qualified numeric equivalence and runtime only; they were not a
scientific permutation p-value.

This release source contains only anonymous aggregates. It contains no entity
crosswalk, molecular strings, protein vectors, predictions, model weights,
sample values, or machine-local source paths, and does not claim private
retraining.
