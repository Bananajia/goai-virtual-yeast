"""Experiment: replay named GO-slim output-side token evidence."""

from experiment_core.legacy_evidence import AggregateEvidenceExperiment


class NamedPathwayTokensExperiment(AggregateEvidenceExperiment):
    name = "named_pathway_tokens_evidence"
    description = "Replay named GO-slim output-side token aggregates."
    evidence_ids = ("named-pathway-tokens-v1",)


def build_experiment() -> NamedPathwayTokensExperiment:
    return NamedPathwayTokensExperiment()
