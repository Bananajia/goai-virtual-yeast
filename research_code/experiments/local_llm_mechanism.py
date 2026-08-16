"""Experiment: replay dual local-LLM mechanism-feature evidence."""

from experiment_core.legacy_evidence import AggregateEvidenceExperiment


class LocalLLMMechanismExperiment(AggregateEvidenceExperiment):
    name = "local_llm_mechanism_evidence"
    description = "Replay the dual local-LLM mechanism-feature aggregates."
    evidence_ids = ("dual-local-llm-mechanism-v1",)


def build_experiment() -> LocalLLMMechanismExperiment:
    return LocalLLMMechanismExperiment()
