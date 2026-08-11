"""Experiment: replay the PubChem structure confirmatory aggregate evidence."""

from experiment_core.legacy_evidence import LegacyEvidenceReplay


def build_experiment() -> LegacyEvidenceReplay:
    """Return the release-safe Adapter; private model fitting is out of scope."""

    return LegacyEvidenceReplay(
        experiment_ids=("pubchem-structure-confirmatory-v1",),
        run_name="pubchem_structure_confirmatory_evidence",
    )
