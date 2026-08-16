"""Experiment: replay the public causal-residual v1 aggregate evidence."""

from experiment_core.legacy_evidence import AggregateEvidenceExperiment


class PublicCausalResidualExperiment(AggregateEvidenceExperiment):
    name = "public_causal_residual_evidence"
    description = "Replay public signed causal-residual representation aggregates."
    evidence_ids = ("public-causal-residual-v1",)


def build_experiment() -> PublicCausalResidualExperiment:
    """Return the release-safe Adapter; private model fitting is out of scope."""

    return PublicCausalResidualExperiment()
