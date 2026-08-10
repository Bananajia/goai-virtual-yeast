import unittest

import numpy as np
import pandas as pd

from pipeline import DataScope, DatasetBundle


class DatasetContractTest(unittest.TestCase):
    def test_validated_bundle_keeps_schema_and_scope(self) -> None:
        bundle = DatasetBundle(
            metadata=pd.DataFrame({"strain": ["A", "B"]}),
            endpoint=np.asarray([[1.0, 2.0], [3.0, np.nan]]),
            protein_ids=("p1", "p2"),
            scope=DataScope.SYNTHETIC,
        )
        self.assertEqual(bundle.n_conditions, 2)
        self.assertEqual(bundle.n_proteins, 2)

    def test_misaligned_rows_or_duplicate_proteins_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            DatasetBundle(
                metadata=pd.DataFrame({"strain": ["A"]}),
                endpoint=np.ones((2, 2)),
                protein_ids=("p1", "p2"),
                scope=DataScope.PUBLIC,
            )
        with self.assertRaises(ValueError):
            DatasetBundle(
                metadata=pd.DataFrame({"strain": ["A"]}),
                endpoint=np.ones((1, 2)),
                protein_ids=("p1", "p1"),
                scope=DataScope.PUBLIC,
            )


if __name__ == "__main__":
    unittest.main()
