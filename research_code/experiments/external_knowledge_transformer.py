"""Experiment: replay all-entity external-knowledge Transformer evidence."""

from experiment_core.legacy_evidence import AggregateEvidenceExperiment


class ExternalKnowledgeTransformerExperiment(AggregateEvidenceExperiment):
    name = "external_knowledge_transformer_evidence"
    description = "Replay all-entity external-knowledge Transformer aggregates."
    evidence_ids = ("external-knowledge-transformer-v1",)


def build_experiment() -> ExternalKnowledgeTransformerExperiment:
    return ExternalKnowledgeTransformerExperiment()
