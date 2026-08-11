from __future__ import annotations

from typing import Dict, Iterable

from .base import Experiment, ExperimentResult, RunContext
from experiments.synthetic_mean_baseline import SyntheticMeanBaseline
from experiments.synthetic_metadata_ridge import SyntheticMetadataRidge
from experiments.legacy_evidence_replay import build_experiment as build_legacy_replay
from experiments.public_rna_lincs_mini import PublicRnaLincsMiniExperiment
from experiments.conditional_uncertainty import build_experiment as build_uncertainty
from experiments.chemcpa_nonlinear import build_experiment as build_chemcpa_nonlinear
from experiments.control_affine_pairwise import build_experiment as build_control_affine
from experiments.drug_target_localnet import build_experiment as build_drug_localnet
from experiments.external_knowledge_transformer import build_experiment as build_transformer
from experiments.fair_architecture import build_experiment as build_fair_architecture
from experiments.functional_multihead import build_experiment as build_multihead
from experiments.latent_dynamics import build_experiment as build_latent_dynamics
from experiments.local_llm_mechanism import build_experiment as build_local_llm
from experiments.loss_ablation import build_experiment as build_loss_ablation
from experiments.multiobjective_highresponse import build_experiment as build_multiobjective
from experiments.named_pathway_tokens import build_experiment as build_named_pathways
from experiments.pubchem_structure_confirmatory import (
    build_experiment as build_pubchem_structure_confirmatory,
)
from experiments.static_prefix import build_experiment as build_static_prefix
from experiments.strain_genome_cnv import build_experiment as build_strain_genome
from experiments.structure_generalization import (
    build_experiment as build_structure_generalization,
)
from experiments.threshold_policy import build_experiment as build_threshold_policy


class ExperimentRegistry:
    """Single discovery and execution Interface for experiment Implementations."""

    def __init__(self, experiments: Iterable[Experiment]) -> None:
        self._experiments: Dict[str, Experiment] = {}
        for experiment in experiments:
            if experiment.name in self._experiments:
                raise ValueError(f"duplicate experiment name: {experiment.name}")
            self._experiments[experiment.name] = experiment

    @classmethod
    def default(cls) -> "ExperimentRegistry":
        return cls(
            (
                SyntheticMeanBaseline(),
                SyntheticMetadataRidge(),
                PublicRnaLincsMiniExperiment(),
                build_legacy_replay(),
                build_fair_architecture(),
                build_control_affine(),
                build_transformer(),
                build_multihead(),
                build_latent_dynamics(),
                build_multiobjective(),
                build_loss_ablation(),
                build_uncertainty(),
                build_local_llm(),
                build_named_pathways(),
                build_drug_localnet(),
                build_strain_genome(),
                build_structure_generalization(),
                build_chemcpa_nonlinear(),
                build_pubchem_structure_confirmatory(),
                build_static_prefix(),
                build_threshold_policy(),
            )
        )

    def names(self) -> tuple:
        return tuple(sorted(self._experiments))

    def get(self, name: str) -> Experiment:
        try:
            return self._experiments[name]
        except KeyError as error:
            raise KeyError(f"unknown experiment: {name}") from error

    def run(self, name: str, context: RunContext) -> ExperimentResult:
        return self.get(name).run(context)
