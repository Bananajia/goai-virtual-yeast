"""Experiment: replay prefix-state attribution evidence."""

from experiment_core.legacy_evidence import LegacyEvidenceReplay


def build_experiment() -> LegacyEvidenceReplay:
    return LegacyEvidenceReplay(
        experiment_ids=("static-prefix-v3-confirmatory",),
        run_name="static_prefix_evidence",
    )
