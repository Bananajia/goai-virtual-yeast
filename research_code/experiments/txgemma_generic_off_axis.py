"""Experiment: track the pending two-stage generic/off-axis TxGemma study."""

from experiment_core.legacy_evidence import AggregateEvidenceExperiment


class TxGemmaGenericOffAxisExperiment(AggregateEvidenceExperiment):
    """Expose the protocol in the registry without inventing an outcome."""

    name = "txgemma_generic_off_axis_pending"
    description = (
        "Pending two-stage generic-response-axis and drug-specific off-axis "
        "study; no golden outcome is available yet."
    )
    evidence_ids = ("txgemma-generic-off-axis-v1",)


def build_experiment() -> TxGemmaGenericOffAxisExperiment:
    """Backward-compatible builder for the pending registry entry."""

    return TxGemmaGenericOffAxisExperiment()
