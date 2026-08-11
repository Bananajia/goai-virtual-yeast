"""Experiment: replay conditional latent uncertainty evidence."""

from experiment_core.legacy_evidence import LegacyEvidenceReplay


def build_experiment() -> LegacyEvidenceReplay:
    return LegacyEvidenceReplay(
        experiment_ids=("conditional-latent-uncertainty-v1",),
        run_name="conditional_uncertainty_evidence",
    )
