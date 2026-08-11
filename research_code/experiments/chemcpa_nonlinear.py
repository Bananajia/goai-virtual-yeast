"""Experiment: replay validated nonlinear-composition v1/v2 evidence."""

from experiment_core.legacy_evidence import LegacyEvidenceReplay


def build_experiment() -> LegacyEvidenceReplay:
    """Return an aggregate-only Adapter; this does not retrain the private pilots."""

    return LegacyEvidenceReplay(
        experiment_ids=("chemcpa-nonlinear-v1-v2",),
        run_name="chemcpa_nonlinear_evidence",
    )
