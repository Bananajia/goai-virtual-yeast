import unittest

import numpy as np
import pandas as pd

from pipeline import OfficialVehicleMap, Vehicle, match_official_controls


class VehicleMappingTest(unittest.TestCase):
    def test_every_treated_entity_resolves_to_one_explicit_vehicle(self) -> None:
        mapping = OfficialVehicleMap.from_mapping(
            {"drug-a": "DMSO", "drug-b": "Water"}
        )

        self.assertEqual(mapping.resolve("drug-a"), Vehicle.DMSO)
        self.assertEqual(mapping.resolve("drug-b"), Vehicle.WATER)

    def test_missing_or_pooled_vehicle_mapping_fails_closed(self) -> None:
        mapping = OfficialVehicleMap.from_mapping({"drug-a": "DMSO"})
        with self.assertRaisesRegex(KeyError, "no official vehicle"):
            mapping.resolve("drug-x")
        with self.assertRaisesRegex(ValueError, "DMSO or Water"):
            OfficialVehicleMap.from_mapping({"drug-a": "pooled"})

    def test_metadata_matcher_uses_official_vehicle_and_exact_context(self) -> None:
        metadata = pd.DataFrame(
            {
                "sample_ID": ["t1", "t2", "c1", "c2", "wrong-plate"],
                "chemical": ["drug-a", "drug-b", "DMSO", "Water", "DMSO"],
                "source": ["S"] * 5,
                "strain": ["Y"] * 5,
                "medium": ["M"] * 5,
                "temperature": [30] * 5,
                "time": [60] * 5,
                "instrument": ["I"] * 5,
                "plate": ["P", "P", "P", "P", "Q"],
            }
        )
        values = np.asarray(
            [[11.0, 22.0], [13.0, 24.0], [10.0, 20.0], [9.0, 21.0], [99.0, 99.0]]
        )
        endpoint, control = match_official_controls(
            metadata,
            values,
            protein_ids=("p1", "p2"),
            treated_sample_ids=("t1", "t2"),
            vehicle_map=OfficialVehicleMap.from_mapping(
                {"drug-a": "DMSO", "drug-b": "Water"}
            ),
            sample_id_column="sample_ID",
            chemical_column="chemical",
            match_columns=(
                "source",
                "strain",
                "medium",
                "temperature",
                "time",
                "instrument",
                "plate",
            ),
        )
        np.testing.assert_allclose(endpoint.values, [[11.0, 22.0], [13.0, 24.0]])
        np.testing.assert_allclose(control.values, [[10.0, 20.0], [9.0, 21.0]])
        self.assertEqual(tuple(endpoint.replicate_ids), ("t1", "t2"))
        self.assertEqual(tuple(control.replicate_ids), ("t1", "t2"))

    def test_metadata_matcher_rejects_missing_mapping_or_control(self) -> None:
        metadata = pd.DataFrame(
            {
                "sample_ID": ["t1", "c1"],
                "chemical": ["drug-a", "Water"],
                "source": ["S", "S"],
            }
        )
        values = np.asarray([[11.0], [10.0]])
        with self.assertRaisesRegex(ValueError, "no exact DMSO control"):
            match_official_controls(
                metadata,
                values,
                protein_ids=("p1",),
                treated_sample_ids=("t1",),
                vehicle_map=OfficialVehicleMap.from_mapping({"drug-a": "DMSO"}),
                sample_id_column="sample_ID",
                chemical_column="chemical",
                match_columns=("source",),
            )


if __name__ == "__main__":
    unittest.main()
