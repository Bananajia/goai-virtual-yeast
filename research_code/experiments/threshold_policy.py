"""Experiment: replay only the valid threshold/output-contract evidence."""

from experiment_core.legacy_evidence import LegacyEvidenceReplay


def build_experiment() -> LegacyEvidenceReplay:
    return LegacyEvidenceReplay(
        experiment_ids=("threshold-control-calibration-v1",),
        run_name="threshold_policy_evidence",
    )
