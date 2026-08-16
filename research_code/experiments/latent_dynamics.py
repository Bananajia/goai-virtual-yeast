"""Experiment: replay free-rollout and rolling-origin latent dynamics evidence."""

from experiment_core.legacy_evidence import AggregateEvidenceExperiment


class LatentDynamicsExperiment(AggregateEvidenceExperiment):
    name = "latent_dynamics_evidence"
    description = "Replay free-rollout and rolling-origin dynamics aggregates."
    evidence_ids = ("latent-dynamics-v1", "latent-dynamics-v2-rolling-origin")


def build_experiment() -> LatentDynamicsExperiment:
    return LatentDynamicsExperiment()
