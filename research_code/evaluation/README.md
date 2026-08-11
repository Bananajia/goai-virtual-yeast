# Evaluation

Every live experiment imports this folder. No experiment may define a local
Pearson, RMSE, residual-centering, variance-ratio, or DEP scorer.

## Official-facing scorecard contract

`official_scorecard.py` declares the four organizer routes
`test_chem_only`, `test_strain_only`, `test_both`, and `test_time`. It exposes
the six published module weights (20/25/20/20/10/5), routes only the metric
families applicable to each split, requires the strict `abs(Raw-FC) > 1` DEP
policy, and records endpoint, paired-control, and DEP coverage denominators.
It does **not** compute a weighted or "official" total because the material does
not specify a reproducible within-module aggregation.

The reproducibility/compliance item remains a separate gate. The separately
announced 5% open-source contribution dimension is disclosed independently and
is not added to the six-module table by this implementation.

## Scopes

- `endpoint_*`: every cell where truth and prediction are both finite.
- `endpoint_paired_*`: only cells that additionally have a direct measured
  control.
- `raw_fc_*`, residuals, individuality, amplitude, variance ratio, and DEP:
  always the paired scope.

`EvaluationInput` does not accept a bare control array. It requires the sealed
`ResponseEstimate` returned by `MeasuredControlPairer`, verifies that its
endpoint snapshot is identical to evaluation truth, and rejects sensitivity
estimands as primary results.

On the paired scope, Endpoint RMSE and Raw-FC RMSE must be equal because both
truth and prediction subtract the same control:

`(prediction - control) - (truth - control) = prediction - truth`.

## PCC and R²

- `*_pcc`: Pearson across proteins for each condition, then an equal-weight
  macro mean across valid conditions. If truth varies but prediction is
  constant, PCC is `0`; if truth itself is constant, it is undefined.
- `*_pooled_pcc`: flattened diagnostic. It is retained to expose the historical
  average-proteome trap, not used alone for promotion.
- `*_pooled_r2`: flattened explained variation.
- `*_macro_sample_r2`: R² across proteins per condition, then macro averaged.
- `*_macro_protein_pcc`: PCC down conditions per protein, then macro averaged.
- `*_median_protein_r2`: R² down conditions per protein, then median aggregated.
- `*_mean_protein_r2`: R² down conditions for each protein, then mean across
  proteins with defined truth variance.
- `*_rmse`: micro RMSE across all jointly finite cells.

## Response families

`Raw-FC = endpoint - directly measured control`.

- Official context residual: freeze the per-protein mean for each declared
  biological context using outer-fit true Raw-FC, then subtract that same frozen
  reference from held truth and prediction.
- Official drug residual: freeze the per-protein mean for each chemical using
  outer-fit true Raw-FC, then subtract that same reference from held truth and
  prediction.
- Individuality: subtract the per-protein mean across the evaluation cohort.

`ResidualReferenceMode.FIT_FROZEN` is the official-facing default. Its sealed
references bind evaluation replicate IDs, protein IDs, group labels, and their
orders; same-shaped but misordered references fail. Building the references
also requires provenance sealed by `verify_train_only_provenance()`, exact fit
replicate IDs, and a zero-overlap check against evaluation IDs. A caller cannot
obtain a `fit_only=true` contract by omitting or manually constructing this
provenance.
`EVALUATION_CENTERED` is retained only to replay historical internal diagnostics;
it centers on the held cohort and cannot be compared as if it were the official
residual. Evaluation centering uses exactly the truth-prediction common mask and
requires at least two finite conditions per `group × protein`.
`NOT_APPLICABLE` is restricted to `test_both`/`test_time`, whose published
module uses absolute fidelity plus original Raw-FC rather than a residual mean.

## Condition variance ratio

The ratio is predicted individuality energy divided by truth individuality
energy. `0` means complete condition collapse; `1` means similar response
amplitude, not necessarily correct direction. It must be read together with PCC
and RMSE.

## High-response / DEP metrics

The official-facing high-effect policy fixes `abs(log2 FC) > 1`; only `K` is fit
on outer-fit Raw-FC and shared by baseline, candidate, and negative controls.
The historical quantile threshold remains available as an auxiliary policy:

- threshold: official fixed strict value `1`, or a labeled fit-only sensitivity quantile;
- `K`: fit-only median DEP count, clipped to a declared range;
- signed precision/recall/F1@K;
- tie-aware macro AUPRC;
- PCC over the truth-positive high-response coordinates;
- top-K direction consistency;
- truth-positive MAE/RMSE.

Held truth is never used to choose the threshold, K, protein panel, or mask.

## Forbidden historical paths

- reconstructing a control as `truth_endpoint - truth_fc`;
- separately aggregating endpoint and FC with different missing denominators;
- centering a protein from only one finite observation;
- silently dropping constant predictions from macro PCC;
- comparing models on model-specific finite cells;
- treating pooled DMSO/Water as official vehicle-specific FC.
