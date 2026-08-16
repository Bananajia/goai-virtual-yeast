"""Experiment: replay prefix-state attribution evidence."""

from experiment_core.legacy_evidence import AggregateEvidenceExperiment


class StaticPrefixExperiment(AggregateEvidenceExperiment):
    name = "static_prefix_evidence"
    description = "Replay static-prefix state attribution aggregates."
    evidence_ids = ("static-prefix-v3-confirmatory",)


def build_experiment() -> StaticPrefixExperiment:
    return StaticPrefixExperiment()
