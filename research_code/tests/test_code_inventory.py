import unittest
from pathlib import Path

from evidence.build_code_inventory import build_inventory


class CodeInventoryTest(unittest.TestCase):
    @unittest.skipUnless(
        (Path(__file__).resolve().parents[2] / "code" / "experiments").exists(),
        "requires the optional historical experiment tree",
    )
    def test_inventory_covers_legacy_and_frozen_trees_without_private_paths(self) -> None:
        research_root = Path(__file__).resolve().parents[1]
        payload = build_inventory(
            research_root.parent, research_root / "evidence" / "registry.json"
        )
        serialized = str(payload)

        self.assertGreater(payload["experiment_directories"], 50)
        self.assertGreater(payload["python_files"], 300)
        self.assertIn("code/experiments", payload["generated_from"])
        self.assertNotIn("private-data", serialized)
        self.assertNotIn("/Users/", serialized)
        self.assertNotIn("__pycache__", serialized)


if __name__ == "__main__":
    unittest.main()
