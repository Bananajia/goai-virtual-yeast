"""Experiment: replay the four-arm blind LLM causal-prediction pilot."""

from experiment_core.legacy_evidence import AggregateEvidenceExperiment


class BlindLLMCausalPilotExperiment(AggregateEvidenceExperiment):
    """Hash-lock the release-safe blind/freeze/unblind aggregate receipt."""

    name = "blind_llm_causal_pilot_evidence"
    description = (
        "Replay one opaque held-out-entity four-arm causal hypothesis pilot "
        "with predictions frozen before numeric outcomes were opened."
    )
    evidence_ids = ("blind-llm-causal-pilot-v1",)


def build_experiment() -> BlindLLMCausalPilotExperiment:
    """Backward-compatible builder used by older registry integrations."""

    return BlindLLMCausalPilotExperiment()
