"""Experiment: replay validated structure-generalization v1 evidence."""

from experiment_core.legacy_evidence import LegacyEvidenceReplay


def build_experiment() -> LegacyEvidenceReplay:
    """Return an aggregate-only Adapter; this does not retrain the private pilot."""

    return LegacyEvidenceReplay(
        experiment_ids=("structure-generalization-v1",),
        run_name="structure_generalization_evidence",
    )
