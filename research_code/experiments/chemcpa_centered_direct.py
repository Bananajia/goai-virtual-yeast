"""Experiment: replay the strict whole-drug-held-out representation test."""

from experiment_core.legacy_evidence import AggregateEvidenceExperiment


class ChemCPACenteredDirectExperiment(AggregateEvidenceExperiment):
    """Hash-lock the release-safe chemCPA centered-direct aggregate result."""

    name = "chemcpa_centered_direct_evidence"
    description = (
        "Replay the centered direct protein-prediction comparison under strict "
        "whole-drug holdout."
    )
    evidence_ids = ("chemcpa-centered-direct-v1",)


def build_experiment() -> ChemCPACenteredDirectExperiment:
    """Backward-compatible builder used by older registry integrations."""

    return ChemCPACenteredDirectExperiment()
