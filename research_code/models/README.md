# Models

Every model exposes only:

```python
model.fit(fit_features, fit_targets)
prediction = model.predict(query_features)
```

The current deep baseline Module contains:

- `ProteinMeanBaseline`: fit-only per-protein mean; exposes the average-proteome
  trap and should have condition variance ratio zero.
- `MaskedMultiOutputRidge`: one missing-aware Ridge fit per protein with a
  shared numeric feature matrix and unpenalized intercept.

Metadata encoding, missingness, OOD splits, measured controls, evaluation, and
reporting are injected from other Modules. A model never receives held truth or
implements its own metric.

Historical neural, low-rank, dynamics, uncertainty, pathway, Transformer, and
genome Implementations remain in their frozen evidence directories until a
parity-tested Adapter is added here. Their current conclusions are already
available through one-file evidence experiments.
