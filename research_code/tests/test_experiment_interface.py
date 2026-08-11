import json
import tempfile
import unittest
from pathlib import Path

from experiment_core import ExperimentRegistry, RunContext


class ExperimentInterfaceTest(unittest.TestCase):
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
