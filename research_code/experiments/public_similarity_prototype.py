"""Experiment: replay the public-similarity prototype v1 aggregate evidence."""

from experiment_core.legacy_evidence import AggregateEvidenceExperiment


class PublicSimilarityPrototypeExperiment(AggregateEvidenceExperiment):
    name = "public_similarity_prototype_evidence"
    description = "Replay public hard/soft similarity prototype aggregates."
    evidence_ids = ("public-similarity-prototype-v1",)


def build_experiment() -> PublicSimilarityPrototypeExperiment:
    """Return the release-safe Adapter; private model fitting is out of scope."""

    return PublicSimilarityPrototypeExperiment()
