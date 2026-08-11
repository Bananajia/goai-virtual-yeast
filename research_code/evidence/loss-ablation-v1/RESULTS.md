# Loss ablation v1 — aggregate release evidence

Status: **validated aggregate evidence; global promotion rejected**

This release-safe record contains scalar grouped-OOF results only. It contains no
competition matrix, entity or protein identity, sample-level prediction, target or
control vector, embedding, model parameter, credential, API output, or local/private
filesystem path.

## Frozen comparison

- Input scope: 5,920 authorized train rows; fixed validation/test numeric values
  were not read.
- Current-release output contract: 5,243 coordinates; train-only missingness
  strictly below 80% retains 4,422 coordinates, with zero coordinates exactly on
  the 80% boundary. A response-blind hash fixes the 384-coordinate pilot.
- OOD: five whole-chemical folds and five whole-`Kbio` folds, with three matched
  seeds per loss.
- Model held fixed: metadata-only rank-16 decoder, one width-32 tanh layer, 80
  AdamW epochs, identical folds, initialization, parameters, optimizer and scorer.
- Experimental factor: MSE, Huber (delta 1), fourfold response-weighted MSE, or
  fourfold response-weighted Huber. Response weights use outer-fit cells satisfying
  `|endpoint - measured control| > 1 log2`.
- Primary control convention is an exploratory directly measured pooled
  DMSO/Water control because an authoritative chemical-to-vehicle map was not
  available.

## Candidate minus MSE

For RMSE, a negative change is an improvement.

| OOD scenario | Candidate | Raw-FC PCC change | Raw-FC positive folds | Endpoint / Raw-FC RMSE change | Fixed DEP F1 change | High-response RMSE change | Decision |
|---|---|---:|---:|---:|---:|---:|---|
| Whole chemical | Huber | -0.005865 | 0/5 | +0.004262 | -0.000952 | +0.009959 | Reject |
| Whole chemical | Response-weighted MSE | +0.022086 | 5/5 | -0.002792 | +0.001299 | -0.029698 | Reject: variance ratio 2.213904 to 2.252139 |
| Whole chemical | Response-weighted Huber | +0.012847 | 5/5 | -0.000776 | +0.000846 | -0.015001 | Reject: variance ratio 2.213904 to 2.233993 |
| Whole Kbio | Huber | -0.001112 | 1/5 | +0.000646 | -0.009141 | +0.013006 | Reject |
| Whole Kbio | Response-weighted MSE | +0.006036 | 5/5 | +0.005517 | +0.025599 | -0.024109 | Reject: RMSE/ranking/variance gates failed |
| Whole Kbio | Response-weighted Huber | +0.007437 | 5/5 | +0.003340 | +0.023354 | -0.017954 | Reject: RMSE/variance gates failed |

The real response-weighted MSE exceeds the within-protein deranged-weight control
in Raw-FC PCC in all five folds of both scenarios: +0.022310 for whole chemical
and +0.005287 for whole Kbio. Its high-response RMSE is also lower in all five
folds in both scenarios. Thus response-magnitude alignment carries signal, but the
fixed fourfold multiplier over-amplifies conditional variability and does not pass
the complete promotion gate.

## Decision and reproducibility boundary

Ordinary MSE remains the global objective for this metadata-only model. Huber is
not a drop-in improvement. Response-weighted MSE remains a research branch for a
future inner-fit comparison of milder multipliers or an explicit amplitude/variance
constraint; it is not a submitted global replacement and was not expanded to the
4,422-coordinate panel.

The clean repository exposes an aggregate-evidence adapter that verifies this
file's SHA-256 and frozen scalar values. It does **not** claim to retrain the private
384-coordinate study. The full historical runner, tests, freeze records and
independent aggregate replay remain in the optional persistent experiment tree.
