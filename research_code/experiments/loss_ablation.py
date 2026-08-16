"""Experiment: replay validated MSE/Huber/response-weighted-loss evidence."""

from experiment_core.legacy_evidence import AggregateEvidenceExperiment


class LossAblationExperiment(AggregateEvidenceExperiment):
    name = "loss_ablation_evidence"
    description = "Replay the MSE, Huber and response-weighted loss comparison."
    evidence_ids = ("loss-ablation-v1",)


def build_experiment() -> LossAblationExperiment:
    """Return an aggregate-only adapter; this does not retrain the private pilot."""

    return LossAblationExperiment()
