# Blind LLM causal-prediction pilot

Date: 2026-08-14

## Frozen design

- Opaque held-out treated entities: **1**
- Prompt arms: **4**
- Predictions per arm: **5**
- Predictions frozen before numeric outcome access: **true**
- Matched condition-time aggregates: **89**
- Trajectory blocks: **16**
- Time points: **6**
- Protein coordinates: **5,243**
- Eligible protein coordinates: **4,033**
- Whole-trajectory bootstrap replicates: **10,000**
- Non-TRAIN numeric rows decoded: **0**

The four arms supplied the same model with: the correct mechanism, no specific
mechanism, a wrong mechanism, or the correct pathway with counterfactual
direction. Each arm had to freeze a structured causal graph, five cellular
states, exactly five protein changes, directions, magnitudes, time bins,
competing explanations, and falsifiers before the evaluator opened outcomes.

## Protein-level and state-level results

| Result | Value |
|---|---:|
| correct-arm exact top-five overlap | 0 |
| correct-arm signed nDCG@5 | 0.0 |
| correct-arm eligible predictions | 5 |
| correct-arm mean absolute observed effect | 0.1920632437519853 |
| correct-arm mean rank percentile | 0.97296626984127 |
| correct-arm supported-state directional mean | 0.37358972080147995 |
| correct-arm supported-state CI low | 0.2032321433204057 |
| correct-arm supported-state CI high | 0.579957318474878 |
| correct-arm supported-state sign agreement | 1.0 |
| counterfactual-arm supported-state directional mean | 0.4851382168614178 |
| counterfactual-arm supported-state CI low | 0.26989373914542886 |
| counterfactual-arm supported-state CI high | 0.743743870998913 |
| counterfactual-arm supported-state sign agreement | 1.0 |

## Decision and boundary

**VALIDATED_SCOPED / REPLICATE BEFORE TRAINING.** The mechanism-informed arm
selected five high-ranking responders on average and one coherent downstream
state was supported. It did not recover any member of the observed exact top
five. More importantly, the counterfactual-direction arm supported the same
broad adaptive state, so this one-drug result does not identify a unique causal
direction. It supports the narrow claim that a large LLM can generate useful
module-level hypotheses for prospective testing; it does not support exact
protein ranking, unique causal identification, or general LLM superiority.

This release evidence contains only opaque aggregates. It contains no treated-
entity identity, protein identity, prompt/response transcript, public-to-
competition mapping, context label, sample value, protein vector, prediction
vector, bootstrap draw, or machine-local path. One fixed entity is insufficient
for a LoRA decision; the protocol should be repeated across independently held-
out entities and mechanisms.
