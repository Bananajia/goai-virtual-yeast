# PubChem structure confirmatory v1 — release-safe aggregate evidence

Status: **validated negative result; no model promotion**

This compact record freezes only anonymous scalar results from an independently
replayed, train-only grouped-OOD confirmation. It is sufficient for the unified
evidence Adapter to verify the public conclusion, but it is not a private-study
training entrypoint.

## Frozen contract and population

- Strict train missing fraction below 80%: **4,422** eligible coordinates;
  exact-80% ties: **0**.
- Primary all-ITT population: **37** treated entities.
- Strict, unique and collision-free public structure coverage: **25 covered**;
  **12 explicit missing/fallback**.
- The missing/fallback rows use the frozen context-only fallback.
- Fixed validation numeric rows read: **0**; test numeric rows read: **0**.

## All-37 Raw-FC PCC

Each value is the unweighted mean over five outer folds. M0 is the direct
metadata Ridge comparator; C0 is the context-only comparator. M1, M2 and M3 are
the three preregistered structure candidates.

| Scenario | M0 metadata Ridge | C0 context-only Ridge | M1 Tanimoto transfer | M2 CPA-style additive | M3 structure-context bilinear |
|---|---:|---:|---:|---:|---:|
| Whole chemical | 0.255488 | 0.243875 | 0.251053 | 0.248201 | 0.247908 |
| Whole Kbio | 0.337380 | 0.246348 | 0.255678 | 0.277940 | 0.275726 |

The three candidates do not beat the stronger M0/C0 comparator on the frozen
all-37 gate.

## Frozen promotion decision

| Candidate | Promoted |
|---|---|
| M1 Tanimoto response transfer | **false** |
| M2 CPA-style latent additive Ridge | **false** |
| M3 low-rank structure-context bilinear Ridge | **false** |

Promoted candidates: **0** of **3**.

Coverage increased relative to the earlier strict audit, but coverage alone did
not produce a stable predictive gain. Therefore the existing primary route is
unchanged: **NO-PROMOTION** for all three structure candidates.

## Independent aggregate replay

- Fold/model/tier rows independently checked: **300**.
- Model summary rows independently checked: **60**.
- Candidate-versus-baseline paired checks: **576**.
- Real-versus-matched-permutation paired checks: **216**.
- Independent replay status: **PASS**.
- Maximum absolute replay discrepancy across summary values: **4.441e-16**.

## Release boundary

This file contains aggregate counts, scalar means and decisions only. It ships
no entity-level mappings, molecular strings, per-fold rows, predictions,
feature vectors, embeddings, neighbours, similarities, fitted parameters or
machine-local locations. The result is single-seed train-only OOF evidence, not
a fixed-validation, test or leaderboard estimate. The 384-coordinate diagnostic
panel used full-train missingness only and is therefore value-blind but not fully
prospective with respect to the outer folds.
