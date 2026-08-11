"""Experiment: replay validated MSE/Huber/response-weighted-loss evidence."""

from experiment_core.legacy_evidence import LegacyEvidenceReplay


def build_experiment() -> LegacyEvidenceReplay:
    """Return an aggregate-only adapter; this does not retrain the private pilot."""

    return LegacyEvidenceReplay(
        experiment_ids=("loss-ablation-v1",),
        run_name="loss_ablation_evidence",
    )
