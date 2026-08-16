"""Experiment: verify all persistent historical aggregate evidence."""

from experiment_core.legacy_evidence import LegacyEvidenceReplay


class AllLegacyEvidenceExperiment(LegacyEvidenceReplay):
    """Replay every persistent golden aggregate record through one interface."""


def build_experiment() -> AllLegacyEvidenceExperiment:
    return AllLegacyEvidenceExperiment()
