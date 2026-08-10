import unittest

import numpy as np
import pandas as pd

from pipeline import MetadataEncoder, MetadataField


class MetadataEncoderTest(unittest.TestCase):
    def test_one_hot_numeric_and_unknown_contract(self) -> None:
        fit = pd.DataFrame(
            {
                "strain": ["A", "B"],
                "time": [0.0, 9.0],
                "temperature": [20.0, 30.0],
            }
        )
        query = pd.DataFrame(
            {"strain": ["C"], "time": [3.0], "temperature": [25.0]}
        )
        encoder = MetadataEncoder(
            fields=(
                MetadataField("strain", "categorical"),
                MetadataField("time", "log1p"),
                MetadataField("temperature", "standardize"),
            )
        ).fit(fit)
        transformed = encoder.transform(query)

        self.assertEqual(transformed.shape[0], 1)
        unknown_index = encoder.feature_names.index("strain=<UNKNOWN>")
        self.assertAlmostEqual(transformed[0, unknown_index], 1.0)
        time_index = encoder.feature_names.index("time=log1p")
        self.assertAlmostEqual(transformed[0, time_index], np.log1p(3.0))
        temp_index = encoder.feature_names.index("temperature=zscore")
        self.assertAlmostEqual(transformed[0, temp_index], 0.0)


if __name__ == "__main__":
    unittest.main()
