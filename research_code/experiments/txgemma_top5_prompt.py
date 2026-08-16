"""Experiment: replay the TxGemma categorical top-five prompt audit."""

from experiment_core.legacy_evidence import AggregateEvidenceExperiment


class TxGemmaTop5PromptExperiment(AggregateEvidenceExperiment):
    """Hash-lock the release-safe option-order stability diagnosis."""

    name = "txgemma_top5_prompt_evidence"
    description = (
        "Replay the candidate-panel categorical prompt audit with cyclic "
        "answer-order perturbations and a strict abstention gate."
    )
    evidence_ids = ("txgemma-top5-prompt-v1",)


def build_experiment() -> TxGemmaTop5PromptExperiment:
    """Backward-compatible builder used by older registry integrations."""

    return TxGemmaTop5PromptExperiment()
