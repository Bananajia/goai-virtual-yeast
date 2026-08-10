import unittest

import numpy as np
import pandas as pd

from pipeline import SubmissionContract


class SubmissionContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = SubmissionContract(
            sample_ids=("s2", "s1"),
            protein_ids=("p1", "p2"),
            sample_id_column="sample_ID",
            output_scale="log2",
        )

    def test_valid_prediction_requires_exact_ids_columns_order_and_finite_log2(self) -> None:
        prediction = pd.DataFrame(
            {
                "sample_ID": ["s2", "s1"],
                "p1": [10.0, 11.0],
                "p2": [20.0, 21.0],
            }
        )

        validated = self.contract.validate(prediction, declared_scale="log2")

        self.assertEqual(validated.shape, (2, 3))

    def test_wrong_row_order_columns_scale_or_nonfinite_values_fail_closed(self) -> None:
        valid = pd.DataFrame(
            {
                "sample_ID": ["s2", "s1"],
                "p1": [10.0, 11.0],
                "p2": [20.0, 21.0],
            }
        )
        with self.assertRaisesRegex(ValueError, "sample_ID order"):
            self.contract.validate(valid.iloc[::-1].reset_index(drop=True), declared_scale="log2")
        with self.assertRaisesRegex(ValueError, "protein columns"):
            self.contract.validate(valid[["sample_ID", "p2", "p1"]], declared_scale="log2")
        with self.assertRaisesRegex(ValueError, "declared scale"):
            self.contract.validate(valid, declared_scale="raw")
        broken = valid.copy()
        broken.loc[0, "p1"] = np.nan
        with self.assertRaisesRegex(ValueError, "finite"):
            self.contract.validate(broken, declared_scale="log2")


if __name__ == "__main__":
    unittest.main()
