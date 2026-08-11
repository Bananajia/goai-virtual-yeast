# Domain context

This file fixes the language used by the unified research layer.

- **ObservationMatrix**: a condition-by-protein matrix. Raw intensities are positive; transformed values are `log2` intensities with missing cells represented by `NaN`, never zero.
- **ConditionMetadata**: strain, chemical perturbation, medium, temperature, time, unit, and explicitly approved technical covariates.
- **MeasuredControl**: a directly observed DMSO/Water control paired to a treated condition. It must never be reconstructed from held-out endpoint truth.
- **PairedResponse**: endpoint, measured control, and prediction aligned on the same replicate-by-protein finite cells.
- **ProteinOutputContract**: the immutable full output width. A fit-only modeled subset is restored with fit-only protein fallbacks.
- **OODScenario**: a whole-entity or whole-combination holdout such as whole chemical, whole strain, unseen `K_bio`, whole time, or their intersection.
- **EvaluationCohort**: the exact rows, proteins, and common finite mask shared by compared models.
- **ExperimentSpec**: the immutable name, scope, split, model, evaluation policy, and evidence status of one experiment file.
- **ExperimentResult**: aggregate metrics, counts, contract flags, decision, and provenance. It never contains sample identities or response vectors.
- **PrivateDataset**: authorized competition data. It may only be consumed by local pipeline Adapters.
- **PublicEvidencePacket**: public facts plus source identifiers passed through the public-only provider Seam. It cannot contain competition paths, identities, matrices, embeddings, or predictions.
- **AggregateEvidence**: non-identifying fold-level or summary metrics retained for validation and reporting.
- **PromotionGate**: a predeclared multi-metric decision. A positive PCC alone is not sufficient.

## Model question

Every model receives condition features and predicts a protein endpoint vector. Response metrics are derived only after subtracting the same directly measured control from truth and prediction:

`truth_fc = truth_endpoint - measured_control`

`prediction_fc = prediction_endpoint - measured_control`

The central scientific question is whether a model preserves condition-specific response under strict OOD holdout, not merely whether it reconstructs the stable average proteome.
