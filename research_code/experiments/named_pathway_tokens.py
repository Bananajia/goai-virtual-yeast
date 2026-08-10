"""Experiment: replay named GO-slim output-side token evidence."""

from experiment_core.legacy_evidence import LegacyEvidenceReplay


def build_experiment() -> LegacyEvidenceReplay:
    return LegacyEvidenceReplay(
        experiment_ids=("named-pathway-tokens-v1",),
        run_name="named_pathway_tokens_evidence",
    )
