"""Experiment: replay the CHX downstream-state post-hoc abundance audit."""

from experiment_core.legacy_evidence import AggregateEvidenceExperiment


class CHXDownstreamStateExperiment(AggregateEvidenceExperiment):
    """Hash-lock the release-safe primary gate and module-level summaries."""

    name = "chx_downstream_state_evidence"
    description = (
        "Replay the post-hoc downstream-state primary gate and clearly scoped "
        "exploratory abundance-module summaries."
    )
    evidence_ids = ("downstream-state-posthoc-v1",)


def build_experiment() -> CHXDownstreamStateExperiment:
    """Backward-compatible builder used by older registry integrations."""

    return CHXDownstreamStateExperiment()
