import unittest

import numpy as np
import pandas as pd

from pipeline import DataScope, DatasetBundle, align_dataset_frames, require_training_bundle


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

    def test_frames_are_aligned_by_sample_id_not_current_row_order(self) -> None:
        metadata = pd.DataFrame(
            {"sample_ID": ["s2", "s1"], "strain": ["B", "A"]}
        )
        proteome = pd.DataFrame(
            {
                "sample_ID": ["s1", "s2"],
                "p1": [1.0, 2.0],
                "p2": [10.0, 20.0],
            }
        )

        bundle = align_dataset_frames(
            metadata,
            proteome,
            sample_id_column="sample_ID",
            scope=DataScope.SYNTHETIC,
        )

        np.testing.assert_allclose(bundle.endpoint, [[2.0, 20.0], [1.0, 10.0]])
        self.assertEqual(bundle.protein_ids, ("p1", "p2"))

    def test_sample_id_alignment_rejects_duplicates_or_unmatched_ids(self) -> None:
        duplicate_metadata = pd.DataFrame({"sample_ID": ["s1", "s1"]})
        proteome = pd.DataFrame({"sample_ID": ["s1", "s2"], "p1": [1.0, 2.0]})
        with self.assertRaisesRegex(ValueError, "sample_ID values must be unique"):
            align_dataset_frames(
                duplicate_metadata,
                proteome,
                sample_id_column="sample_ID",
                scope=DataScope.SYNTHETIC,
            )

        unmatched_metadata = pd.DataFrame({"sample_ID": ["s1", "s3"]})
        with self.assertRaisesRegex(ValueError, "same sample_ID identities"):
            align_dataset_frames(
                unmatched_metadata,
                proteome,
                sample_id_column="sample_ID",
                scope=DataScope.SYNTHETIC,
            )
        with self.assertRaises(ValueError):
            DatasetBundle(
                metadata=pd.DataFrame({"strain": ["A"]}),
                endpoint=np.ones((1, 2)),
                protein_ids=("p1", "p1"),
                scope=DataScope.PUBLIC,
            )

    def test_fit_bundle_rejects_validation_or_test_truth(self) -> None:
        train = DatasetBundle(
            metadata=pd.DataFrame(
                {"sample_ID": ["s1", "s2"], "split_final": ["train", "train"]}
            ),
            endpoint=np.ones((2, 1)),
            protein_ids=("p1",),
            scope=DataScope.PRIVATE_LOCAL,
        )
        self.assertIs(require_training_bundle(train), train)

        leaked = DatasetBundle(
            metadata=pd.DataFrame(
                {"sample_ID": ["s1", "s2"], "split_final": ["train", "val_chem_only"]}
            ),
            endpoint=np.ones((2, 1)),
            protein_ids=("p1",),
            scope=DataScope.PRIVATE_LOCAL,
        )
        with self.assertRaisesRegex(ValueError, "only split_final=train"):
            require_training_bundle(leaked)


if __name__ == "__main__":
    unittest.main()
