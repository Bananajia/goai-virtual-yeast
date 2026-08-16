# Downstream-state post-hoc abundance audit

Date: 2026-08-14

## Frozen scope

- Inference scope: **posthoc exploratory**
- Official numeric role: **TRAIN only**
- Shared query contexts: **93**
- Trajectory blocks: **16**
- Other treated entities in the reference center: **35**
- Protein coordinates: **5,243**
- Primary family size: **2**
- Primary hypotheses passed: **0**
- Validation/test numeric rows decoded: **0**

## Primary gate

| Primary | Scoreable contexts | Scoreable trajectories | Trajectory-equal effect | CI low | CI high | Fixed-family BH q | Direction agreement | Passed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| early single-marker state | 4 | 3 | — | — | — | 1.0 | — | 0 |
| late single-marker state | 30 | 16 | -0.025696768679119422 | -0.15279203931886046 | 0.12192749712851164 | 0.734375 | 0.5 | 0 |

The early marker failed the prespecified minimum of eight trajectories. The
late marker was scoreable but its effect was small, its interval crossed zero,
and its direction agreement and multiplicity-adjusted direction test failed.
The formal primary decision is therefore **NOT SUPPORTED (0/2)**.

## Exploratory abundance-module outline

| Module | Trajectory-equal shared-reference abundance effect |
|---|---:|
| cytosolic translation abundance | -0.16219030200135168 |
| efflux-pump abundance | -0.6201212180298895 |
| RNP-granule abundance | -0.04294799427191362 |
| mitochondrial-translation abundance | -0.08860985429566709 |

These four rows are exploratory descriptions of total protein abundance
relative to an other-entity context-by-protein center. They are not estimates
versus untreated cells and do not by themselves measure pathway activity,
translation rate, phosphorylation, target engagement, or causal mediation.

This evidence is aggregate-only. It contains no query identity, marker name,
module member list, trajectory label, sample value, protein vector, bootstrap
draw, prediction, or machine-local source path.
