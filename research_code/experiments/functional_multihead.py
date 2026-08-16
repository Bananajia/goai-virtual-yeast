"""Experiment: replay public functional-group multi-head evidence."""

from experiment_core.legacy_evidence import AggregateEvidenceExperiment


class FunctionalMultiheadExperiment(AggregateEvidenceExperiment):
    name = "functional_multihead_evidence"
    description = "Replay public functional-group multi-head aggregates."
    evidence_ids = ("public-functional-group-multihead-v1",)


def build_experiment() -> FunctionalMultiheadExperiment:
    return FunctionalMultiheadExperiment()
