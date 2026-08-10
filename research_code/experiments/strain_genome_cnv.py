"""Experiment: replay strain LoF/frameshift/CNV evidence and identifiability stop."""

from experiment_core.legacy_evidence import LegacyEvidenceReplay


def build_experiment() -> LegacyEvidenceReplay:
    return LegacyEvidenceReplay(
        experiment_ids=("strain-genome-cnv-v1", "strain-lof-shrinkage-v1"),
        run_name="strain_genome_cnv_evidence",
    )
