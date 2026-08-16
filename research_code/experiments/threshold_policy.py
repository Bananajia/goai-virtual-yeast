"""Experiment: replay only the valid threshold/output-contract evidence."""

from experiment_core.legacy_evidence import AggregateEvidenceExperiment


class ThresholdPolicyExperiment(AggregateEvidenceExperiment):
    name = "threshold_policy_evidence"
    description = "Replay the valid threshold and output-contract aggregates."
    evidence_ids = ("threshold-control-calibration-v1",)


def build_experiment() -> ThresholdPolicyExperiment:
    return ThresholdPolicyExperiment()
