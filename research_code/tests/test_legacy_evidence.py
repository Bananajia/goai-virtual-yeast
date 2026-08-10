from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from experiment_core.base import RunContext
from experiment_core.legacy_evidence import EvidenceRegistry, LegacyEvidenceReplay


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = PROJECT_ROOT / "research_code" / "evidence" / "registry.json"


class LegacyEvidenceRegistryTest(unittest.TestCase):
    def test_registry_is_privacy_safe_and_preserves_invalidations(self) -> None:
        registry = EvidenceRegistry.load(REGISTRY_PATH)

        self.assertGreaterEqual(len(registry.records), 21)
        self.assertEqual(
            registry.get("control-affine-fullpanel-v1").status,
            "INVALIDATED",
        )
        self.assertFalse(registry.get("control-affine-fullpanel-v1").golden)
        self.assertEqual(
            registry.get("control-affine-fullpanel-v1").replacement,
            "control-affine-fullpanel-v2-pairwise",
        )
        self.assertEqual(
            registry.get("chemical-router-v3").status,
            "BLOCKED_SOURCE_MISSING",
        )
        self.assertEqual(
            registry.get("unified-router-final-v3-scoped").status,
            "BLOCKED_SOURCE_MISSING",
        )
        self.assertEqual(
            registry.get("loss-ablation-v1").status,
            "VALIDATED_REJECTED",
        )
        self.assertEqual(
            registry.get("structure-generalization-v1").status,
            "VALIDATED_REJECTED",
        )
        self.assertEqual(
            registry.get("chemcpa-nonlinear-v1-v2").status,
            "VALIDATED_REJECTED",
        )

        raw = REGISTRY_PATH.read_text(encoding="utf-8")
        self.assertNotIn("/Users/", raw)
        for record in registry.records:
            if record.source is not None:
                self.assertFalse(Path(record.source.path).is_absolute())
                self.assertNotIn("private-data", Path(record.source.path).parts)

    @unittest.skipUnless(
        (PROJECT_ROOT / "experiments" / "control-affine-fullpanel-v2-pairwise").exists(),
        "requires the optional historical aggregate-evidence tree",
    )
    def test_replay_verifies_persisted_golden_aggregate_metrics(self) -> None:
        replay = LegacyEvidenceReplay(registry_path=REGISTRY_PATH)
        receipt = replay.verify(
            documents_root=PROJECT_ROOT,
            experiment_ids=(
                "control-affine-fullpanel-v2-pairwise",
                "training-camp-completion-v1",
            ),
        )

        self.assertEqual(receipt.status, "PASS")
        self.assertEqual(receipt.records_passed, 2)
        self.assertGreaterEqual(receipt.metrics_verified, 4)
        self.assertEqual(receipt.records_failed, 0)
        self.assertEqual(receipt.invalidated_used_as_golden, 0)

    @unittest.skipUnless(
        (PROJECT_ROOT / "experiments" / "fair-architecture-benchmark-v1").exists(),
        "requires the optional historical aggregate-evidence tree",
    )
    def test_run_uses_shared_experiment_interface_and_writes_aggregate_only(self) -> None:
        replay = LegacyEvidenceReplay(
            registry_path=REGISTRY_PATH,
            experiment_ids=("fair-architecture-benchmark-v1",),
        )
        with tempfile.TemporaryDirectory() as temporary:
            output_dir = Path(temporary)
            result = replay.run(
                RunContext(
                    output_dir=output_dir,
                    data_scope="aggregate-only",
                    data_root=PROJECT_ROOT,
                )
            )
            payload = json.loads(
                (output_dir / "result.json").read_text(encoding="utf-8")
            )

        self.assertEqual(result.status, "GOVERNANCE")
        self.assertEqual(payload["contract"]["aggregate_only"], True)
        self.assertNotIn("predictions", payload)
        self.assertNotIn("identities", payload)
        self.assertNotIn("protein_vectors", payload)

    def test_hash_change_fails_closed_before_metric_replay(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "aggregate.md"
            source.write_text("metric = 0.25\n", encoding="utf-8")
            registry_path = root / "registry.json"
            registry_path.write_text(
                json.dumps(
                    {
                        "schema_version": "1.0",
                        "records": [
                            {
                                "experiment_id": "fixture",
                                "status": "VALIDATED_REJECTED",
                                "golden": True,
                                "source": {
                                    "root": "documents",
                                    "path": "aggregate.md",
                                    "kind": "aggregate_markdown",
                                },
                                "source_sha256": "0" * 64,
                                "replacement": None,
                                "validity": "fixture",
                                "expected_aggregate_metrics": [
                                    {
                                        "name": "metric",
                                        "value": 0.25,
                                        "tolerance": 1e-12,
                                        "locator": {
                                            "kind": "regex",
                                            "pattern": "metric = (?P<value>[0-9.]+)",
                                        },
                                    }
                                ],
                            }
                        ],
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            receipt = LegacyEvidenceReplay(registry_path=registry_path).verify(
                documents_root=root,
                experiment_ids=("fixture",),
            )

        self.assertEqual(receipt.status, "FAIL")
        self.assertEqual(receipt.records_failed, 1)
        self.assertEqual(receipt.metrics_verified, 0)

    def test_release_safe_loss_ablation_adapter_replays(self) -> None:
        replay = LegacyEvidenceReplay(
            registry_path=REGISTRY_PATH,
            experiment_ids=("loss-ablation-v1",),
        )
        receipt = replay.verify(documents_root=PROJECT_ROOT)

        self.assertEqual(receipt.status, "PASS")
        self.assertEqual(receipt.records_passed, 1)
        self.assertGreaterEqual(receipt.metrics_verified, 6)

    def test_release_safe_structure_generalization_adapter_replays(self) -> None:
        replay = LegacyEvidenceReplay(
            registry_path=REGISTRY_PATH,
            experiment_ids=("structure-generalization-v1",),
        )
        receipt = replay.verify(documents_root=PROJECT_ROOT)

        self.assertEqual(receipt.status, "PASS")
        self.assertEqual(receipt.records_passed, 1)
        self.assertGreaterEqual(receipt.metrics_verified, 10)

    def test_release_safe_structure_evidence_has_no_machine_local_path(self) -> None:
        evidence_path = (
            PROJECT_ROOT
            / "research_code"
            / "evidence"
            / "structure-generalization-v1"
            / "RESULTS.md"
        )
        raw = evidence_path.read_text(encoding="utf-8")

        self.assertNotIn("/Users/", raw)
        self.assertNotIn("private-data", raw)
        self.assertIn("**37**", raw)
        self.assertIn("**22 covered**", raw)
        self.assertIn("**15 explicit missing/fallback**", raw)
        self.assertIn("NO-PROMOTION", raw)

    def test_release_safe_chemcpa_inspired_nonlinear_adapter_replays(self) -> None:
        replay = LegacyEvidenceReplay(
            registry_path=REGISTRY_PATH,
            experiment_ids=("chemcpa-nonlinear-v1-v2",),
        )
        receipt = replay.verify(documents_root=PROJECT_ROOT)

        self.assertEqual(receipt.status, "PASS")
        self.assertEqual(receipt.records_passed, 1)
        self.assertGreaterEqual(receipt.metrics_verified, 14)

    def test_release_safe_chemcpa_inspired_evidence_is_aggregate_only(self) -> None:
        evidence_path = (
            PROJECT_ROOT
            / "research_code"
            / "evidence"
            / "chemcpa-nonlinear-v1-v2"
            / "RESULTS.md"
        )
        raw = evidence_path.read_text(encoding="utf-8")

        for forbidden in (
            "/Users/",
            "private-data",
            "sample_ID",
            "InChIKey",
            "SMILES",
            "per-condition prediction",
            "protein vector",
            "model weight",
        ):
            self.assertNotIn(forbidden, raw)
        self.assertIn("exact-context measured-control conditional diagnostic", raw)
        self.assertIn("no-control development follow-up", raw)
        self.assertIn("NO-PROMOTION", raw)


if __name__ == "__main__":
    unittest.main()
