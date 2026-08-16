# Experiments

Except for the required package `__init__.py`, every Python file in this folder
represents one executable study. Shared orchestration lives in
`../experiment_core/`; no experiment implements its own metric functions.

Every aggregate-only study now exposes an explicit public class in its own
module. For example, `CHXCenteredTransferExperiment` is defined in
`chx_centered_transfer.py`. The registry instantiates these classes directly;
the module-level `build_experiment()` function remains as a backward-compatible
Adapter. All such classes reuse `AggregateEvidenceExperiment`, which delegates
hash-first verification and aggregate report writing to the common core. The
registry imports experiment implementations lazily, so an experiment class can
also be imported and reused without a registry-bootstrap cycle.

There are four types:

1. **Live fixture experiments**: `synthetic_mean_baseline.py` and
   `synthetic_metadata_ridge.py` exercise the full model → central evaluation →
   aggregate report path, including a learnable non-collapsed response.
2. **Public-only live experiment**: `public_rna_lincs_mini.py` runs the frozen
   six-signature RNA/causal-axis smoke.
3. **Historical evidence Adapter**: files ending in a study name replay the
   frozen aggregate source hash and expected result. They do not pretend to
   retrain when historical per-sample predictions were intentionally not saved.
4. **Pending protocol Adapter**: a registered study with no audited outcome is
   non-golden and returns `BLOCKED`; it never invents a scalar or decision.

## Recent named experiment classes

| File | Public class | Registry name | Evidence boundary |
|---|---|---|---|
| `chemcpa_centered_direct.py` | `ChemCPACenteredDirectExperiment` | `chemcpa_centered_direct_evidence` | 23-entity whole-entity-held-out representation comparison; no arm promoted |
| `chx_centered_transfer.py` | `CHXCenteredTransferExperiment` | `chx_centered_transfer_evidence` | query-disjoint shared-center fixed-template transfer; not supported |
| `txgemma_top5_prompt.py` | `TxGemmaTop5PromptExperiment` | `txgemma_top5_prompt_evidence` | 28/28 strict abstentions after option-order audit |
| `chx_downstream_state.py` | `CHXDownstreamStateExperiment` | `chx_downstream_state_evidence` | post-hoc primary 0/2; abundance modules exploratory only |
| `blind_llm_causal_pilot.py` | `BlindLLMCausalPilotExperiment` | `blind_llm_causal_pilot_evidence` | one opaque blind pilot: partial module signal, no exact top-five or unique causal identification |
| `txgemma_generic_off_axis.py` | `TxGemmaGenericOffAxisExperiment` | `txgemma_generic_off_axis_pending` | protocol registered as `PENDING`; no golden outcome |

`loss_ablation.py` is one such aggregate-only Adapter. It verifies the release-safe
MSE/Huber/response-weighted-loss summary under `../evidence/loss-ablation-v1/`;
the clean package does not claim to retrain that private 384-coordinate pilot.
`structure_generalization.py` applies the same boundary to the independently
validated Tanimoto, CPA-style additive and structure-context bilinear pilot under
`../evidence/structure-generalization-v1/`. It verifies only release-safe
all-ITT/coverage aggregates and never loads chemical identities or private
predictions.
`chemcpa_nonlinear.py` replays one combined release-safe record for the nonlinear
composition v1/v2 pilots under `../evidence/chemcpa-nonlinear-v1-v2/`. V1 is a
measured-control conditional diagnostic; v2 is a no-control development
follow-up. The molecular branch is rejected, C0 remains research-only, and the
Adapter does not claim an exact CPA/chemCPA reproduction or private retraining.
`pubchem_structure_confirmatory.py` replays the later PubChem-first confirmation
under `../evidence/pubchem-structure-confirmatory-v1/`. It verifies only
anonymous all-37 means, coverage/count contracts and the frozen rejection of all
three structure candidates; it does not expose the private training runner.
`public_causal_residual.py` replays the frozen public causal-residual pilot under
`../evidence/public-causal-residual-v1/`. It verifies 39 anonymous aggregate
counts, fold-macro metrics and stability witnesses; it distributes no public-to-
competition join, prompt, causal chain, response vector or fitted parameter.
`public_similarity_prototype.py` independently replays the hard-cluster,
soft-neighbour and partial-pooling rejection under
`../evidence/public-similarity-prototype-v1/`. Its 43 frozen scalars cover the
all-ITT population, coverage/fallback counts and all nine primary comparison
rows without exposing entity mappings, public feature vectors, neighbours,
predictions or weights.

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

The same contract replays a recent study, for example:

```bash
python3 research_cli.py run blind_llm_causal_pilot_evidence \
  --scope aggregate-only \
  --data-root .. \
  --output reports/blind-llm-causal-pilot-replay
```

`chemical-router-v3` and `unified-router-final-v3-scoped` have no executable
source in the persistent or workspace trees. They remain
`BLOCKED_SOURCE_MISSING` in the evidence registry and are not exposed as
executable experiments.
