"""Experiment: replay all-entity external-knowledge Transformer evidence."""

from experiment_core.legacy_evidence import LegacyEvidenceReplay


def build_experiment() -> LegacyEvidenceReplay:
    return LegacyEvidenceReplay(
        experiment_ids=("external-knowledge-transformer-v1",),
        run_name="external_knowledge_transformer_evidence",
    )
