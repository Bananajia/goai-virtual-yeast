"""Experiment: replay public functional-group multi-head evidence."""

from experiment_core.legacy_evidence import LegacyEvidenceReplay


def build_experiment() -> LegacyEvidenceReplay:
    return LegacyEvidenceReplay(
        experiment_ids=("public-functional-group-multihead-v1",),
        run_name="functional_multihead_evidence",
    )
