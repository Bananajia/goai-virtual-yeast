"""Experiment: replay public drug-target to STRING local-network evidence."""

from experiment_core.legacy_evidence import LegacyEvidenceReplay


def build_experiment() -> LegacyEvidenceReplay:
    return LegacyEvidenceReplay(
        experiment_ids=("drug-target-localnet-v1",),
        run_name="drug_target_localnet_evidence",
    )
