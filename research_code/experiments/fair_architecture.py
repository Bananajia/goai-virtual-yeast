"""Experiment: replay Ridge versus direct/low-rank/residual MLP evidence."""

from experiment_core.legacy_evidence import LegacyEvidenceReplay


def build_experiment() -> LegacyEvidenceReplay:
    return LegacyEvidenceReplay(
        experiment_ids=("fair-architecture-benchmark-v1",),
        run_name="fair_architecture_evidence",
    )
