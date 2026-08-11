"""Experiment: replay dual local-LLM mechanism-feature evidence."""

from experiment_core.legacy_evidence import LegacyEvidenceReplay


def build_experiment() -> LegacyEvidenceReplay:
    return LegacyEvidenceReplay(
        experiment_ids=("dual-local-llm-mechanism-v1",),
        run_name="local_llm_mechanism_evidence",
    )
