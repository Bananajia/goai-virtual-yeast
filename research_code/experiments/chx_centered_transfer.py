"""Experiment: replay the fixed CHX template transfer after shared centering."""

from experiment_core.legacy_evidence import AggregateEvidenceExperiment


class CHXCenteredTransferExperiment(AggregateEvidenceExperiment):
    """Hash-lock the release-safe shared-center transfer diagnosis."""

    name = "chx_centered_transfer_evidence"
    description = (
        "Replay fixed donor-to-target residual transfer after excluding both "
        "queries from the context-by-protein reference center."
    )
    evidence_ids = ("fixed-template-shared-center-v2",)


def build_experiment() -> CHXCenteredTransferExperiment:
    """Backward-compatible builder used by older registry integrations."""

    return CHXCenteredTransferExperiment()
