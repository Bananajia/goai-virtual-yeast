# Release-safe aggregate evidence: nonlinear composition pilots v1 and v2

## Scope boundary

This record combines two independently validated aggregate-proteome pilots. The model family is
chemCPA-inspired, but it is not exact CPA or chemCPA: it has no pretrained molecular encoder, dose
module or adversarial disentanglement.

- V1 is an **exact-context measured-control conditional diagnostic**. C0, C1 and N1 receive a
  rank-32 representation of a measured control from the same acquisition context. It is not a
  default zero-shot submission route.
- V2 is a **no-control development follow-up**, performed after the v1 result was known. No
  predictor receives a measured-control feature; the retained 32-coordinate control block is zero
  throughout fitting and evaluation. It is not an independent confirmation.

This release record contains aggregate counts, metrics and decisions only. It contains no entity-
or row-level artifacts and cannot retrain either private pilot.

## Shared frozen population

- Official train rows: **5,920**; fixed validation and test numeric reads: **0**.
- Strict train missing fraction below 80%: **4,422** eligible coordinates; exact-80% ties: **0**.
- Response-independent evaluation panel: **384** proteins.
- Whole-chemical grouped OOF: **5** folds by **3** frozen seeds, or **15** paired runs.
- Primary population: **37** treated drugs; **22 covered** and **15 explicit missing/fallback**.
- C0, C1 and N1: **44,416** trainable parameters each.

## V1 measured-control conditional diagnostic

The clean molecular attribution is C1 versus capacity-matched C0. C1 minus C0 Raw-FC PCC was
**-0.003304**, positive in **3/15** paired runs. C1 minus C0 Raw-FC RMSE was **+0.002450** and C1
had lower RMSE in only **1/15** runs. The frozen joint gate therefore **FAILS**.

The larger C0/C1 improvement over M0 cannot be used as a nonlinearity or zero-shot claim because
M0 did not receive the exact-context measured-control feature.

## V2 no-control development follow-up

All values are all-ITT means across the 15 paired runs. Raw-FC remains exploratory because an
official chemical-to-vehicle mapping was unavailable.

| Model | Raw-FC PCC | Raw-FC RMSE | Endpoint PCC | Endpoint RMSE |
|---|---:|---:|---:|---:|
| M0 metadata Ridge | 0.255488 | 0.621807 | 0.973752 | 0.621807 |
| C0 no-control nonlinear context | 0.275814 | 0.586450 | 0.976691 | 0.586450 |
| C1 real-structure composer | 0.271387 | 0.582446 | 0.976650 | 0.582446 |
| N1 permuted-structure control | 0.266930 | 0.606727 | 0.975181 | 0.606727 |

C0 versus M0 improved Raw-FC PCC by **+0.020325** and oriented RMSE by **+0.035357**; both were
positive in **15/15** runs. This is a no-control context/low-rank research signal, not a controlled
attribution to nonlinearity alone, because the model family and target representation also change.

The frozen C1 gate produced:

| Contrast | Oriented improvement | Positive rows | Gate result |
|---|---:|---:|---|
| Raw-FC PCC versus per-run stronger M0/C0 | -0.004426 | 7/15 | FAIL |
| Raw-FC RMSE versus per-run stronger M0/C0 | +0.004005 | 9/15 | PASS |
| Covered-tier Raw-FC PCC versus N1 | +0.007129 | 11/15 | PASS |
| Covered-tier Raw-FC RMSE versus N1 | +0.036897 | 9/15 | PASS |

Correct structures outperform the permutation control in the covered tier, but C1 does not beat
the stronger no-structure comparator on PCC. The joint molecular-branch gate therefore **FAILS**.

## Independent replay qualification

Every gate-relevant value and decision replayed. Exactly **4** of 231 secondary paired rows changed only a
non-gate context-residual PCC positive-count field when values near 1e-18 became exact zero after a
CSV round trip. No Raw-FC or RMSE gate input, 7/15 or 9/15 count, Boolean check, status or scientific
decision changed.

## Decision

**NO-PROMOTION** for the current molecular structure branch. Keep v1 only as a measured-control
conditional diagnostic. Keep v2 C0 only as a no-control research baseline, and add a target- and
capacity-matched linear comparator before attributing its gain to nonlinearity.
