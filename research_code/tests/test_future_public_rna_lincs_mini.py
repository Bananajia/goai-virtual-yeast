from __future__ import annotations

import tempfile
import unittest
import json
from pathlib import Path

from future_experiments.public_causal_chain import CausalChain, CausalEdge, PublicCausalCase
from future_experiments.public_rna_lincs_mini import (
    FIXTURE_DIR,
    FrozenL1000Fixture,
    OllamaRuntimeIdentity,
    probe_ollama_runtime,
    run_local_ollama_pilot,
    run_offline_smoke,
)


class PublicRnaLincsMiniTest(unittest.TestCase):
    def test_fixture_is_small_hashed_public_and_query_truth_are_separate(self) -> None:
        fixture = FrozenL1000Fixture.load(FIXTURE_DIR)
        self.assertEqual(len(fixture.queries), 6)
        self.assertEqual(len(fixture.truth_by_signature), 6)
        self.assertLess((FIXTURE_DIR / "l1000fwd_six.json").stat().st_size, 55 * 1024)

        query = fixture.queries[0]
        self.assertFalse(hasattr(query, "up_genes"))
        self.assertFalse(hasattr(query, "down_genes"))
        truth = fixture.truth_by_signature[query.signature_id]
        self.assertGreater(len(truth.up_genes), 0)
        self.assertGreater(len(truth.down_genes), 0)

    def test_hash_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "l1000fwd_six.json").write_text("{}", encoding="utf-8")
            (root / "manifest.json").write_text(
                '{"fixture":"l1000fwd_six.json","sha256":"bad","source_scope":"public"}',
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                FrozenL1000Fixture.load(root)

    def test_offline_smoke_is_deterministic_and_writes_aggregate_report(self) -> None:
        with tempfile.TemporaryDirectory() as left, tempfile.TemporaryDirectory() as right:
            first = run_offline_smoke(Path(left))
            second = run_offline_smoke(Path(right))
            self.assertEqual(first, second)
            self.assertEqual(first["counts"]["signatures"], 6)
            self.assertEqual(first["contract"]["query_truth_separated"], True)
            self.assertEqual(first["contract"]["private_data_read"], False)
            self.assertIn("macro_axis_cosine", first["metrics"])
            self.assertTrue((Path(left) / "RESULTS.json").exists())
            report = (Path(left) / "REPORT.md").read_text(encoding="utf-8")
            self.assertIn("L1000FWD", report)
            self.assertNotIn("up_genes", report)

    def test_local_ollama_pilot_reports_only_anonymous_aggregates(self) -> None:
        class RecordingProvider:
            def __init__(self) -> None:
                self.packets = []

            def infer(self, packet):
                self.packets.append(packet)
                case = PublicCausalCase.from_packet(packet)
                citation = case.citations[0]
                return CausalChain(
                    (
                        CausalEdge("public-target", "reduces", "cell_cycle", -1, 0.8, citation),
                        CausalEdge("public-target", "increases", "oxidative_stress_redox", 1, 0.7, citation),
                        CausalEdge("public-target", "increases", "general_antimicrobial_toxicity", 1, 0.6, citation),
                    )
                )

        provider = RecordingProvider()
        identity = OllamaRuntimeIdentity(
            provider="ollama-loopback",
            model="test-open-weight:1b",
            model_digest="a" * 64,
            ollama_version="0.test",
        )
        with tempfile.TemporaryDirectory() as directory:
            result = run_local_ollama_pilot(
                Path(directory),
                provider=provider,
                runtime_identity=identity,
                case_limit=1,
            )
            persisted = (Path(directory) / "RESULTS.json").read_text(encoding="utf-8")

        self.assertEqual(result["status"], "SMOKE_ONLY")
        self.assertEqual(result["counts"], {"anonymous_cases_attempted": 1, "anonymous_cases_evaluated": 1})
        self.assertEqual(len(provider.packets), 1)
        self.assertNotIn("up_genes", repr(provider.packets[0]))
        self.assertNotIn("down_genes", repr(provider.packets[0]))
        for forbidden in (
            "Rapamycin",
            "MG-132",
            "THAPSIGARGIN",
            "oligomycin",
            "Etoposide",
            "NOCODAZOLE",
            "prompt",
            "response",
            "up_genes",
            "down_genes",
            "signature_id",
        ):
            self.assertNotIn(forbidden, persisted)
        parsed = json.loads(persisted)
        self.assertEqual(parsed["provenance"]["model_digest"], "a" * 64)
        self.assertIn("macro_axis_cosine", parsed["metrics"])

    def test_local_ollama_pilot_fails_closed_without_persisting_raw_error(self) -> None:
        class InvalidProvider:
            def infer(self, packet):
                raise ValueError("RAW MODEL RESPONSE mentions Rapamycin and should stay memory-only")

        identity = OllamaRuntimeIdentity(
            provider="ollama-loopback",
            model="test-open-weight:1b",
            model_digest="b" * 64,
            ollama_version="0.test",
        )
        with tempfile.TemporaryDirectory() as directory:
            result = run_local_ollama_pilot(
                Path(directory),
                provider=InvalidProvider(),
                runtime_identity=identity,
                case_limit=6,
            )
            persisted = (Path(directory) / "RESULTS.json").read_text(encoding="utf-8")

        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["metrics"], {})
        self.assertEqual(result["counts"]["anonymous_cases_attempted"], 1)
        self.assertEqual(result["counts"]["anonymous_cases_evaluated"], 0)
        self.assertEqual(result["failure"]["category"], "ValueError")
        self.assertEqual(result["failure"]["code"], "provider_output_schema_invalid")
        self.assertNotIn("RAW MODEL RESPONSE", persisted)
        self.assertNotIn("Rapamycin", persisted)

    def test_ollama_runtime_probe_uses_fixed_loopback_and_exact_model_digest(self) -> None:
        calls = []

        def fake_get(url, timeout):
            calls.append((url, timeout))
            if url.endswith("/api/version"):
                return {"version": "0.32.5"}
            return {
                "models": [
                    {"name": "other:latest", "digest": "1" * 64},
                    {"name": "qwen3:8b", "digest": "2" * 64},
                ]
            }

        identity = probe_ollama_runtime("qwen3:8b", transport=fake_get)
        self.assertEqual(identity.model_digest, "2" * 64)
        self.assertEqual(identity.ollama_version, "0.32.5")
        self.assertEqual(
            [url for url, _ in calls],
            [
                "http://127.0.0.1:11434/api/version",
                "http://127.0.0.1:11434/api/tags",
            ],
        )


if __name__ == "__main__":
    unittest.main()
