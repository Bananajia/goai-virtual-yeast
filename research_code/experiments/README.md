# Experiments

Except for the required package `__init__.py`, every Python file in this folder
represents one executable study. Shared orchestration lives in
`../experiment_core/`; no experiment implements its own metric functions.

There are three types:

1. **Live fixture experiments**: `synthetic_mean_baseline.py` and
   `synthetic_metadata_ridge.py` exercise the full model → central evaluation →
   aggregate report path, including a learnable non-collapsed response.
2. **Public-only live experiment**: `public_rna_lincs_mini.py` runs the frozen
   six-signature RNA/causal-axis smoke.
3. **Historical evidence Adapter**: files ending in a study name replay the
   frozen aggregate source hash and expected result. They do not pretend to
   retrain when historical per-sample predictions were intentionally not saved.

List all registered experiments:

```bash
python3 research_cli.py list
```

Replay one study:

```bash
python3 research_cli.py run fair_architecture_evidence \
  --scope aggregate-only \
  --data-root .. \
  --output reports/fair-architecture-replay
```

`chemical-router-v3` and `unified-router-final-v3-scoped` have no executable
source in the persistent or workspace trees. They remain
`BLOCKED_SOURCE_MISSING` in the evidence registry and are not exposed as
executable experiments.
