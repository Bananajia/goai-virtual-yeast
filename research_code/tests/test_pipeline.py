import unittest

import numpy as np

from pipeline import (
    GroupedOODSplitter,
    Log2ProteomeTransformer,
    MissingnessFilter,
    ProteinOutputContract,
)


class PipelineTest(unittest.TestCase):
    def test_log2_keeps_missing_and_rejects_nonpositive_observations(self) -> None:
        raw = np.asarray([[1.0, 2.0, np.nan], [4.0, 0.0, -1.0]])
        transformed = Log2ProteomeTransformer().transform(raw)

        np.testing.assert_allclose(transformed[0, :2], [0.0, 1.0])
        self.assertTrue(np.isnan(transformed[0, 2]))
        self.assertTrue(np.isnan(transformed[1, 1:]).all())

    def test_official_missingness_policy_excludes_exactly_eighty_percent(self) -> None:
        train = np.asarray(
            [
                [1.0, 1.0, np.nan],
                [1.0, np.nan, np.nan],
                [1.0, np.nan, np.nan],
                [1.0, np.nan, np.nan],
                [1.0, np.nan, np.nan],
            ]
        )
        holdout = np.ones((3, 3))
        filtering = MissingnessFilter(max_missing_fraction=0.80).fit(train)

        self.assertEqual(filtering.keep_mask.tolist(), [True, False, False])
        self.assertEqual(filtering.transform(holdout).shape, (3, 1))

    def test_inclusive_eighty_percent_remains_an_explicit_sensitivity_policy(self) -> None:
        train = np.asarray(
            [
                [1.0, 1.0],
                [1.0, np.nan],
                [1.0, np.nan],
                [1.0, np.nan],
                [1.0, np.nan],
            ]
        )
        filtering = MissingnessFilter(
            max_missing_fraction=0.80, include_boundary=True
        ).fit(train)

        self.assertEqual(filtering.keep_mask.tolist(), [True, True])

    def test_official_missingness_is_counted_on_raw_na_before_log2(self) -> None:
        raw = np.asarray([[0.0, np.nan], [2.0, 4.0]])
        filtering = MissingnessFilter(max_missing_fraction=0.80).fit_raw(raw)
        self.assertEqual(filtering.missing_fraction.tolist(), [0.0, 0.5])
        self.assertEqual(filtering.keep_mask.tolist(), [True, True])

    def test_output_contract_restores_full_width_with_train_only_fallback(self) -> None:
        train = np.asarray([[1.0, np.nan, 3.0], [3.0, 10.0, 5.0]])
        contract = ProteinOutputContract.from_training(
            train, modeled_mask=np.asarray([True, False, True])
        )
        restored = contract.restore(np.asarray([[2.0, 4.0], [4.0, 6.0]]))

        np.testing.assert_allclose(restored, [[2.0, 10.0, 4.0], [4.0, 10.0, 6.0]])

    def test_all_missing_filtered_protein_requires_explicit_fit_only_fallback(self) -> None:
        train = np.asarray([[1.0, np.nan], [3.0, np.nan]])
        mask = np.asarray([True, False])
        with self.assertRaisesRegex(ValueError, "explicit unobserved_fallback"):
            ProteinOutputContract.from_training(train, modeled_mask=mask)

        contract = ProteinOutputContract.from_training(
            train,
            modeled_mask=mask,
            unobserved_fallback=float(np.nanmedian(train)),
        )
        restored = contract.restore(np.asarray([[2.0]]))
        np.testing.assert_allclose(restored, [[2.0, 2.0]])

    def test_whole_entity_split_has_zero_identity_overlap(self) -> None:
        entities = np.asarray(["a", "a", "b", "b", "c", "c"])
        split = GroupedOODSplitter().hold_out(entities, held_out=("c",))

        self.assertEqual(split.fit_indices.tolist(), [0, 1, 2, 3])
        self.assertEqual(split.evaluate_indices.tolist(), [4, 5])
        self.assertEqual(split.identity_overlap, 0)


if __name__ == "__main__":
    unittest.main()
