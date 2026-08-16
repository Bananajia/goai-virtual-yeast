"""Experiment: replay strain LoF/frameshift/CNV evidence and identifiability stop."""

from experiment_core.legacy_evidence import AggregateEvidenceExperiment


class StrainGenomeCNVExperiment(AggregateEvidenceExperiment):
    name = "strain_genome_cnv_evidence"
    description = "Replay strain LoF, frameshift and CNV aggregate evidence."
    evidence_ids = ("strain-genome-cnv-v1", "strain-lof-shrinkage-v1")


def build_experiment() -> StrainGenomeCNVExperiment:
    return StrainGenomeCNVExperiment()
