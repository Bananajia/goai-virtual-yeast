"""Experiment: replay free-rollout and rolling-origin latent dynamics evidence."""

from experiment_core.legacy_evidence import LegacyEvidenceReplay


def build_experiment() -> LegacyEvidenceReplay:
    return LegacyEvidenceReplay(
        experiment_ids=("latent-dynamics-v1", "latent-dynamics-v2-rolling-origin"),
        run_name="latent_dynamics_evidence",
    )
