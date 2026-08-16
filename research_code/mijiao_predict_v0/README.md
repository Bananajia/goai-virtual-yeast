# MiJiaoPredict v0

`MiJiaoPredict` is a new, independent reconstruction of the project's intended
evidence-gated hard router. It is not the missing historical
`chemical-router-v3` or `unified-router-final-v3-scoped` implementation.

The public inference interface is deliberately small:

```python
prediction = model.predict(feature_views=views, evidence=query_evidence)
result = model.predict_with_audit(feature_views=views, evidence=query_evidence)
manifest = model.model_manifest()
```

The metadata core must always produce a complete finite protein matrix. An
expert may alter a row only when all three conditions hold:

1. the expert has an executable predictor registered in this router;
2. its promotion state is `promoted_scoped`;
3. the row has the evidence required by that expert's frozen scope.

Otherwise the returned row remains exactly equal to the metadata core. The
router never treats "an experiment ran" or "one diagnostic improved" as model
promotion.

## Fixed manual routing order

1. Drug and strain both unknown: metadata core.
2. Seen drug and unknown strain with support: promoted strain expert.
3. Seen base condition and extrapolated time with support: promoted time
   expert.
4. Unknown drug and seen strain: a promoted covered structure expert takes
   precedence, otherwise a promoted chemical expert may run.
5. Missing features, missing source/adapter, rejected or pending evidence:
   metadata core.

The structure-before-chemical order is an interface decision, not a statement
that the current Morgan/CPA candidates passed their gate.

## Current project boundary (2026-08-15 audit)

| Branch | Source/execution state | Scientific state | Default router state |
|---|---|---|---|
| Metadata Ridge | live train/artifact/predict/submission path | validated core | active core |
| Cross-strain residual memory | historical experiment source exists | scoped positive evidence | needs deployment adapter |
| Rank-32 time trajectory | historical source plus tested reconstruction exists | scoped positive evidence | needs deployment adapter |
| `chemical-router-v3` | executable source and frozen receipt missing | historical narrative only in current layer | inactive; reconstruction must be named as such |
| Morgan/Tanimoto, CPA-style and bilinear structure candidates | experiments ran; release-safe aggregate replay exists | all-ITT promotion gate failed | inactive |
| Family-2 learned soft MoE | experiment and replay ran | local point gain below the predeclared promotion margin | inactive |

In particular, covered-subset or context-residual structure improvements are
useful research signals, but they do not justify activating a molecular expert
for every unseen drug. A later molecular branch can be registered without
changing this router after it passes whole-drug, all-ITT, individuality and
identity/permutation controls.

## Test

From `research_code/`:

```bash
python3 -m unittest mijiao_predict_v0.test_mijiao_predict -v
```

The tests cover exact Ridge fallback, double-unknown fallback, scoped
strain/time routing, molecular/chemical precedence, rejected experts and
missing or invalid expert inputs. They use synthetic predictors and do not read
private competition data.
