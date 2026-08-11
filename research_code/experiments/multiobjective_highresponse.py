"""Experiment: replay corrected multi-objective/high-response evidence."""

from experiment_core.legacy_evidence import LegacyEvidenceReplay


def build_experiment() -> LegacyEvidenceReplay:
    return LegacyEvidenceReplay(
        experiment_ids=("multiobjective-highresponse-v1",),
        run_name="multiobjective_highresponse_evidence",
    )
