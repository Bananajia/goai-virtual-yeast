"""Experiment: replay conditional latent uncertainty evidence."""

from experiment_core.legacy_evidence import AggregateEvidenceExperiment


class ConditionalUncertaintyExperiment(AggregateEvidenceExperiment):
    name = "conditional_uncertainty_evidence"
    description = "Replay conditional latent uncertainty aggregates."
    evidence_ids = ("conditional-latent-uncertainty-v1",)


def build_experiment() -> ConditionalUncertaintyExperiment:
    return ConditionalUncertaintyExperiment()
