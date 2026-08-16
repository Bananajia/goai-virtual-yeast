"""Experiment: replay Ridge versus direct/low-rank/residual MLP evidence."""

from experiment_core.legacy_evidence import AggregateEvidenceExperiment


class FairArchitectureExperiment(AggregateEvidenceExperiment):
    name = "fair_architecture_evidence"
    description = "Replay the fair architecture benchmark aggregates."
    evidence_ids = ("fair-architecture-benchmark-v1",)


def build_experiment() -> FairArchitectureExperiment:
    return FairArchitectureExperiment()
