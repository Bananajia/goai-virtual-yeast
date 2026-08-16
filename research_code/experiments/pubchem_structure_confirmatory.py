"""Experiment: replay the PubChem structure confirmatory aggregate evidence."""

from experiment_core.legacy_evidence import AggregateEvidenceExperiment


class PubChemStructureConfirmatoryExperiment(AggregateEvidenceExperiment):
    name = "pubchem_structure_confirmatory_evidence"
    description = "Replay PubChem structure confirmatory aggregates."
    evidence_ids = ("pubchem-structure-confirmatory-v1",)


def build_experiment() -> PubChemStructureConfirmatoryExperiment:
    """Return the release-safe Adapter; private model fitting is out of scope."""

    return PubChemStructureConfirmatoryExperiment()
