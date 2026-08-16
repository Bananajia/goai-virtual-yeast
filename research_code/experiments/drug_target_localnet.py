"""Experiment: replay public drug-target to STRING local-network evidence."""

from experiment_core.legacy_evidence import AggregateEvidenceExperiment


class DrugTargetLocalnetExperiment(AggregateEvidenceExperiment):
    name = "drug_target_localnet_evidence"
    description = "Replay public target-to-local-network aggregates."
    evidence_ids = ("drug-target-localnet-v1",)


def build_experiment() -> DrugTargetLocalnetExperiment:
    return DrugTargetLocalnetExperiment()
