"""Experiment: replay validated nonlinear-composition v1/v2 evidence."""

from experiment_core.legacy_evidence import AggregateEvidenceExperiment


class ChemCPANonlinearExperiment(AggregateEvidenceExperiment):
    name = "chemcpa_nonlinear_evidence"
    description = "Replay validated nonlinear-composition v1/v2 aggregates."
    evidence_ids = ("chemcpa-nonlinear-v1-v2",)


def build_experiment() -> ChemCPANonlinearExperiment:
    """Return an aggregate-only Adapter; this does not retrain the private pilots."""

    return ChemCPANonlinearExperiment()
