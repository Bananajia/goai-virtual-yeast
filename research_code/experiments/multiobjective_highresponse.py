"""Experiment: replay corrected multi-objective/high-response evidence."""

from experiment_core.legacy_evidence import AggregateEvidenceExperiment


class MultiobjectiveHighResponseExperiment(AggregateEvidenceExperiment):
    name = "multiobjective_highresponse_evidence"
    description = "Replay corrected multi-objective high-response aggregates."
    evidence_ids = ("multiobjective-highresponse-v1",)


def build_experiment() -> MultiobjectiveHighResponseExperiment:
    return MultiobjectiveHighResponseExperiment()
