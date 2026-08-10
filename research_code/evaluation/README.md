# Evaluation

Every live experiment imports this folder. No experiment may define a local
Pearson, RMSE, residual-centering, variance-ratio, or DEP scorer.

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
- `*_mean_protein_r2`: R² down conditions for each protein, then mean across
  proteins with defined truth variance.
- `*_rmse`: micro RMSE across all jointly finite cells.

## Response families

`Raw-FC = endpoint - directly measured control`.

- Context residual: subtract the per-protein mean within the declared biological
  context group.
- Drug residual: subtract the per-protein mean within each chemical group.
- Individuality: subtract the per-protein mean across the evaluation cohort.

All centering uses exactly the truth–prediction common mask. A `group × protein`
cell is included only if it has at least two finite conditions.

## Condition variance ratio

The ratio is predicted individuality energy divided by truth individuality
energy. `0` means complete condition collapse; `1` means similar response
amplitude, not necessarily correct direction. It must be read together with PCC
and RMSE.

## High-response / DEP metrics

`DEPPolicy` is fit once on outer-fit Raw-FC and shared by baseline, candidate,
and negative controls:

- threshold: fit-only absolute FC quantile;
- `K`: fit-only median DEP count, clipped to a declared range;
- signed precision/recall@K;
- tie-aware macro AUPRC;
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
