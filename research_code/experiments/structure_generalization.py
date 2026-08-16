"""Experiment: replay validated structure-generalization v1 evidence."""

from experiment_core.legacy_evidence import AggregateEvidenceExperiment


class StructureGeneralizationExperiment(AggregateEvidenceExperiment):
    name = "structure_generalization_evidence"
    description = "Replay validated structure-generalization aggregates."
    evidence_ids = ("structure-generalization-v1",)


def build_experiment() -> StructureGeneralizationExperiment:
    """Return an aggregate-only Adapter; this does not retrain the private pilot."""

    return StructureGeneralizationExperiment()
