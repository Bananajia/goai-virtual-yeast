import json
import importlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from experiment_core import ExperimentRegistry, RunContext


class ExperimentInterfaceTest(unittest.TestCase):
    def test_named_experiment_classes_can_be_imported_without_registry_bootstrap(self) -> None:
        completed = subprocess.run(
            (
                sys.executable,
                "-c",
                (
                    "from experiments.fair_architecture import "
                    "FairArchitectureExperiment; "
                    "from experiments.chemcpa_centered_direct import "
                    "ChemCPACenteredDirectExperiment; "
                    "assert FairArchitectureExperiment().name == "
                    "'fair_architecture_evidence'; "
                    "assert ChemCPACenteredDirectExperiment().name == "
                    "'chemcpa_centered_direct_evidence'"
                ),
            ),
            cwd=Path(__file__).resolve().parents[1],
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_every_migrated_aggregate_adapter_exposes_a_named_class(self) -> None:
        cases = (
            ("legacy_evidence_replay", "AllLegacyEvidenceExperiment"),
            ("fair_architecture", "FairArchitectureExperiment"),
            ("control_affine_pairwise", "ControlAffinePairwiseExperiment"),
            (
                "external_knowledge_transformer",
                "ExternalKnowledgeTransformerExperiment",
            ),
            ("functional_multihead", "FunctionalMultiheadExperiment"),
            ("latent_dynamics", "LatentDynamicsExperiment"),
            ("multiobjective_highresponse", "MultiobjectiveHighResponseExperiment"),
            ("loss_ablation", "LossAblationExperiment"),
            ("conditional_uncertainty", "ConditionalUncertaintyExperiment"),
            ("local_llm_mechanism", "LocalLLMMechanismExperiment"),
            ("named_pathway_tokens", "NamedPathwayTokensExperiment"),
            ("drug_target_localnet", "DrugTargetLocalnetExperiment"),
            ("strain_genome_cnv", "StrainGenomeCNVExperiment"),
            ("structure_generalization", "StructureGeneralizationExperiment"),
            ("chemcpa_nonlinear", "ChemCPANonlinearExperiment"),
            (
                "pubchem_structure_confirmatory",
                "PubChemStructureConfirmatoryExperiment",
            ),
            ("public_causal_residual", "PublicCausalResidualExperiment"),
            ("public_similarity_prototype", "PublicSimilarityPrototypeExperiment"),
            ("static_prefix", "StaticPrefixExperiment"),
            ("threshold_policy", "ThresholdPolicyExperiment"),
        )
        registry = ExperimentRegistry.default()

        for module_name, class_name in cases:
            with self.subTest(module=module_name):
                module = importlib.import_module(f"experiments.{module_name}")
                experiment_class = getattr(module, class_name)
                built = module.build_experiment()
                self.assertIs(type(built), experiment_class)
                self.assertIs(type(registry.get(built.name)), experiment_class)

    def test_named_chemcpa_centered_direct_adapter_replays_through_registry(self) -> None:
        from experiments.chemcpa_centered_direct import (
            ChemCPACenteredDirectExperiment,
            build_experiment,
        )

        registry = ExperimentRegistry.default()
        self.assertIsInstance(build_experiment(), ChemCPACenteredDirectExperiment)
        self.assertIsInstance(
            registry.get("chemcpa_centered_direct_evidence"),
            ChemCPACenteredDirectExperiment,
        )
        with tempfile.TemporaryDirectory() as temporary:
            result = registry.run(
                "chemcpa_centered_direct_evidence",
                RunContext(
                    output_dir=Path(temporary),
                    data_scope="aggregate-only",
                    data_root=Path(__file__).resolve().parents[2],
                ),
            )

        self.assertEqual(result.status, "GOVERNANCE")
        self.assertGreaterEqual(result.metrics["metrics_verified"], 8)

    def test_named_chx_centered_transfer_adapter_replays_through_registry(self) -> None:
        from experiments.chx_centered_transfer import (
            CHXCenteredTransferExperiment,
            build_experiment,
        )

        registry = ExperimentRegistry.default()
        self.assertIsInstance(build_experiment(), CHXCenteredTransferExperiment)
        self.assertIsInstance(
            registry.get("chx_centered_transfer_evidence"),
            CHXCenteredTransferExperiment,
        )
        with tempfile.TemporaryDirectory() as temporary:
            result = registry.run(
                "chx_centered_transfer_evidence",
                RunContext(
                    output_dir=Path(temporary),
                    data_scope="aggregate-only",
                    data_root=Path(__file__).resolve().parents[2],
                ),
            )

        self.assertEqual(result.status, "GOVERNANCE")
        self.assertGreaterEqual(result.metrics["metrics_verified"], 10)

    def test_named_txgemma_top5_prompt_adapter_replays_through_registry(self) -> None:
        from experiments.txgemma_top5_prompt import (
            TxGemmaTop5PromptExperiment,
            build_experiment,
        )

        registry = ExperimentRegistry.default()
        self.assertIsInstance(build_experiment(), TxGemmaTop5PromptExperiment)
        self.assertIsInstance(
            registry.get("txgemma_top5_prompt_evidence"),
            TxGemmaTop5PromptExperiment,
        )
        with tempfile.TemporaryDirectory() as temporary:
            result = registry.run(
                "txgemma_top5_prompt_evidence",
                RunContext(
                    output_dir=Path(temporary),
                    data_scope="aggregate-only",
                    data_root=Path(__file__).resolve().parents[2],
                ),
            )

        self.assertEqual(result.status, "GOVERNANCE")
        self.assertGreaterEqual(result.metrics["metrics_verified"], 10)

    def test_named_chx_downstream_state_adapter_replays_through_registry(self) -> None:
        from experiments.chx_downstream_state import (
            CHXDownstreamStateExperiment,
            build_experiment,
        )

        registry = ExperimentRegistry.default()
        self.assertIsInstance(build_experiment(), CHXDownstreamStateExperiment)
        self.assertIsInstance(
            registry.get("chx_downstream_state_evidence"),
            CHXDownstreamStateExperiment,
        )
        with tempfile.TemporaryDirectory() as temporary:
            result = registry.run(
                "chx_downstream_state_evidence",
                RunContext(
                    output_dir=Path(temporary),
                    data_scope="aggregate-only",
                    data_root=Path(__file__).resolve().parents[2],
                ),
            )

        self.assertEqual(result.status, "GOVERNANCE")
        self.assertGreaterEqual(result.metrics["metrics_verified"], 12)

    def test_named_blind_llm_causal_pilot_replays_through_registry(self) -> None:
        from experiments.blind_llm_causal_pilot import (
            BlindLLMCausalPilotExperiment,
            build_experiment,
        )

        registry = ExperimentRegistry.default()
        self.assertIsInstance(build_experiment(), BlindLLMCausalPilotExperiment)
        self.assertIsInstance(
            registry.get("blind_llm_causal_pilot_evidence"),
            BlindLLMCausalPilotExperiment,
        )
        with tempfile.TemporaryDirectory() as temporary:
            result = registry.run(
                "blind_llm_causal_pilot_evidence",
                RunContext(
                    output_dir=Path(temporary),
                    data_scope="aggregate-only",
                    data_root=Path(__file__).resolve().parents[2],
                ),
            )

        self.assertEqual(result.status, "GOVERNANCE")
        self.assertGreaterEqual(result.metrics["metrics_verified"], 15)

    def test_pending_generic_off_axis_study_is_registered_without_golden_metrics(self) -> None:
        from experiments.txgemma_generic_off_axis import (
            TxGemmaGenericOffAxisExperiment,
            build_experiment,
        )

        registry = ExperimentRegistry.default()
        self.assertIsInstance(build_experiment(), TxGemmaGenericOffAxisExperiment)
        with tempfile.TemporaryDirectory() as temporary:
            result = registry.run(
                "txgemma_generic_off_axis_pending",
                RunContext(
                    output_dir=Path(temporary),
                    data_scope="aggregate-only",
                    data_root=Path(__file__).resolve().parents[2],
                ),
            )

        self.assertEqual(result.status, "BLOCKED")
        self.assertEqual(result.metrics["metrics_verified"], 0.0)
        self.assertEqual(result.counts["records_blocked"], 1)
        self.assertFalse(result.contract["source_hashes_verified"])

    def test_fixture_experiment_uses_one_interface_and_writes_aggregate_report(self) -> None:
        registry = ExperimentRegistry.default()
        with tempfile.TemporaryDirectory() as temporary:
            result = registry.run(
                "synthetic_mean_baseline",
                RunContext(
                    output_dir=Path(temporary),
                    data_scope="synthetic",
                    seed=7,
                ),
            )
            payload = json.loads((Path(temporary) / "result.json").read_text())

        self.assertEqual(result.name, "synthetic_mean_baseline")
        self.assertEqual(payload["schema_version"], "1.0")
        self.assertIn("endpoint_pcc", payload["metrics"])
        self.assertEqual(payload["provenance"]["seed"], 7)
        self.assertEqual(payload["provenance"]["data_scope"], "synthetic")
        self.assertNotIn("predictions", payload)
        self.assertNotIn("truth", payload)

    def test_unknown_experiment_fails_closed(self) -> None:
        with self.assertRaises(KeyError):
            ExperimentRegistry.default().get("does_not_exist")

    def test_each_migrated_study_has_a_named_experiment_file(self) -> None:
        names = set(ExperimentRegistry.default().names())
        self.assertIn("fair_architecture_evidence", names)
        self.assertIn("external_knowledge_transformer_evidence", names)
        self.assertIn("named_pathway_tokens_evidence", names)
        self.assertIn("drug_target_localnet_evidence", names)
        self.assertIn("strain_genome_cnv_evidence", names)
        self.assertIn("loss_ablation_evidence", names)
        self.assertIn("structure_generalization_evidence", names)
        self.assertIn("chemcpa_nonlinear_evidence", names)
        self.assertIn("pubchem_structure_confirmatory_evidence", names)

    def test_public_rna_pilot_uses_the_same_run_contract(self) -> None:
        registry = ExperimentRegistry.default()
        with tempfile.TemporaryDirectory() as temporary:
            result = registry.run(
                "public_rna_lincs_mini",
                RunContext(output_dir=Path(temporary), data_scope="public", seed=0),
            )
            self.assertTrue((Path(temporary) / "RESULTS.json").exists())
            self.assertTrue((Path(temporary) / "REPORT.md").exists())
        self.assertEqual(result.status, "PUBLIC_ONLY")
        self.assertEqual(result.counts["signatures"], 6)

    def test_public_causal_residual_evidence_replays_through_the_registry(self) -> None:
        registry = ExperimentRegistry.default()
        with tempfile.TemporaryDirectory() as temporary:
            result = registry.run(
                "public_causal_residual_evidence",
                RunContext(
                    output_dir=Path(temporary),
                    data_scope="aggregate-only",
                    data_root=Path(__file__).resolve().parents[2],
                ),
            )
            payload = json.loads((Path(temporary) / "result.json").read_text())

        self.assertEqual(result.status, "GOVERNANCE")
        self.assertEqual(result.counts["records_passed"], 1)
        self.assertGreaterEqual(result.metrics["metrics_verified"], 20)
        self.assertTrue(payload["contract"]["aggregate_only"])

    def test_public_similarity_prototype_evidence_replays_through_the_registry(self) -> None:
        registry = ExperimentRegistry.default()
        with tempfile.TemporaryDirectory() as temporary:
            result = registry.run(
                "public_similarity_prototype_evidence",
                RunContext(
                    output_dir=Path(temporary),
                    data_scope="aggregate-only",
                    data_root=Path(__file__).resolve().parents[2],
                ),
            )
            payload = json.loads((Path(temporary) / "result.json").read_text())

        self.assertEqual(result.status, "GOVERNANCE")
        self.assertEqual(result.counts["records_passed"], 1)
        self.assertGreaterEqual(result.metrics["metrics_verified"], 40)
        self.assertTrue(payload["contract"]["aggregate_only"])

    def test_synthetic_metadata_ridge_recovers_condition_signal(self) -> None:
        registry = ExperimentRegistry.default()
        with tempfile.TemporaryDirectory() as temporary:
            result = registry.run(
                "synthetic_metadata_ridge",
                RunContext(
                    output_dir=Path(temporary), data_scope="synthetic", seed=11
                ),
            )
        self.assertGreater(result.metrics["raw_fc_pcc"], 0.95)
        self.assertGreater(result.metrics["condition_variance_ratio"], 0.80)


if __name__ == "__main__":
    unittest.main()
