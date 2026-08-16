from __future__ import annotations

import json
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "external_resources" / "manifest.json"


class ExternalResourcesManifestTest(unittest.TestCase):
    def test_public_knowledge_assets_and_closed_authoring_seam_are_disclosed(self) -> None:
        payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        resources = {item["id"]: item for item in payload["resources"]}

        public_cgm = resources["pubchem_aid_1159580_public_cgm"]
        self.assertEqual(
            public_cgm["source_sha256"]["public_csv"],
            "12c518897ca45a3b04f7829df2d6283c011a6c6b6a816a9c27f84749078b32c0",
        )
        self.assertEqual(public_cgm["competition_data_used"], False)

        authoring = resources["interactive_codex_public_causal_authoring"]
        self.assertEqual(authoring["competition_data_supplied"], False)
        self.assertEqual(authoring["called_during_train_or_inference"], False)
        self.assertEqual(authoring["snapshot_reproducible"], False)
        self.assertEqual(
            authoring["frozen_output_sha256"],
            "2e6b137c221abafde31584e03c3a29e4bbb4e26830bf4a346ec061b2dae81a61",
        )

        for resource_id in ("pubchem_compound_structure", "yeast_1011_genomes"):
            self.assertIn(
                "public-similarity-prototype-v1",
                resources[resource_id]["used_by"],
            )
        self.assertEqual(
            resources["pubchem_compound_structure"]["source_sha256"][
                "strict_pubchem_crosswalk"
            ],
            "65a586905b11dd102a83cb36af8efe7305901648987b2ed49e2132bdb55d42c0",
        )

        raw = MANIFEST_PATH.read_text(encoding="utf-8")
        for forbidden in ("/Users/", "/var/folders/", "private-data"):
            self.assertNotIn(forbidden, raw)


if __name__ == "__main__":
    unittest.main()
