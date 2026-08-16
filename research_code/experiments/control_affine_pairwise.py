"""Experiment: replay pairwise exact-control conditional calibration evidence."""

from experiment_core.legacy_evidence import AggregateEvidenceExperiment


class ControlAffinePairwiseExperiment(AggregateEvidenceExperiment):
    name = "control_affine_pairwise_evidence"
    description = "Replay pairwise exact-control calibration aggregates."
    evidence_ids = ("control-affine-fullpanel-v2-pairwise",)


def build_experiment() -> ControlAffinePairwiseExperiment:
    return ControlAffinePairwiseExperiment()
