from __future__ import annotations

from typing import Dict, Iterable

from .base import Experiment, ExperimentResult, RunContext


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
        # Import lazily so every experiment class remains independently
        # importable and reusable without a registry-bootstrap cycle.
        from experiments.blind_llm_causal_pilot import BlindLLMCausalPilotExperiment
        from experiments.chemcpa_centered_direct import ChemCPACenteredDirectExperiment
        from experiments.chemcpa_nonlinear import ChemCPANonlinearExperiment
        from experiments.chx_centered_transfer import CHXCenteredTransferExperiment
        from experiments.chx_downstream_state import CHXDownstreamStateExperiment
        from experiments.conditional_uncertainty import ConditionalUncertaintyExperiment
        from experiments.control_affine_pairwise import ControlAffinePairwiseExperiment
        from experiments.drug_target_localnet import DrugTargetLocalnetExperiment
        from experiments.external_knowledge_transformer import (
            ExternalKnowledgeTransformerExperiment,
        )
        from experiments.fair_architecture import FairArchitectureExperiment
        from experiments.functional_multihead import FunctionalMultiheadExperiment
        from experiments.latent_dynamics import LatentDynamicsExperiment
        from experiments.legacy_evidence_replay import AllLegacyEvidenceExperiment
        from experiments.local_llm_mechanism import LocalLLMMechanismExperiment
        from experiments.loss_ablation import LossAblationExperiment
        from experiments.multiobjective_highresponse import (
            MultiobjectiveHighResponseExperiment,
        )
        from experiments.named_pathway_tokens import NamedPathwayTokensExperiment
        from experiments.pubchem_structure_confirmatory import (
            PubChemStructureConfirmatoryExperiment,
        )
        from experiments.public_causal_residual import PublicCausalResidualExperiment
        from experiments.public_rna_lincs_mini import PublicRnaLincsMiniExperiment
        from experiments.public_similarity_prototype import (
            PublicSimilarityPrototypeExperiment,
        )
        from experiments.static_prefix import StaticPrefixExperiment
        from experiments.strain_genome_cnv import StrainGenomeCNVExperiment
        from experiments.structure_generalization import StructureGeneralizationExperiment
        from experiments.synthetic_mean_baseline import SyntheticMeanBaseline
        from experiments.synthetic_metadata_ridge import SyntheticMetadataRidge
        from experiments.threshold_policy import ThresholdPolicyExperiment
        from experiments.txgemma_top5_prompt import TxGemmaTop5PromptExperiment
        from experiments.txgemma_generic_off_axis import (
            TxGemmaGenericOffAxisExperiment,
        )

        return cls(
            (
                SyntheticMeanBaseline(),
                SyntheticMetadataRidge(),
                PublicRnaLincsMiniExperiment(),
                AllLegacyEvidenceExperiment(),
                FairArchitectureExperiment(),
                ControlAffinePairwiseExperiment(),
                ExternalKnowledgeTransformerExperiment(),
                FunctionalMultiheadExperiment(),
                LatentDynamicsExperiment(),
                MultiobjectiveHighResponseExperiment(),
                LossAblationExperiment(),
                ConditionalUncertaintyExperiment(),
                LocalLLMMechanismExperiment(),
                NamedPathwayTokensExperiment(),
                DrugTargetLocalnetExperiment(),
                StrainGenomeCNVExperiment(),
                StructureGeneralizationExperiment(),
                ChemCPANonlinearExperiment(),
                ChemCPACenteredDirectExperiment(),
                CHXCenteredTransferExperiment(),
                TxGemmaTop5PromptExperiment(),
                CHXDownstreamStateExperiment(),
                BlindLLMCausalPilotExperiment(),
                TxGemmaGenericOffAxisExperiment(),
                PubChemStructureConfirmatoryExperiment(),
                PublicCausalResidualExperiment(),
                PublicSimilarityPrototypeExperiment(),
                StaticPrefixExperiment(),
                ThresholdPolicyExperiment(),
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
