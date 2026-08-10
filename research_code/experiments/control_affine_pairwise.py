"""Experiment: replay pairwise exact-control conditional calibration evidence."""

from experiment_core.legacy_evidence import LegacyEvidenceReplay


def build_experiment() -> LegacyEvidenceReplay:
    return LegacyEvidenceReplay(
        experiment_ids=("control-affine-fullpanel-v2-pairwise",),
        run_name="control_affine_pairwise_evidence",
    )
