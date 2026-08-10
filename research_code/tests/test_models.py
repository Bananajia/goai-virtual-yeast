import unittest

import numpy as np

from models import MaskedMultiOutputRidge, ProteinMeanBaseline


class ModelInterfaceTest(unittest.TestCase):
    def test_protein_mean_baseline_preserves_missing_fit_semantics(self) -> None:
        targets = np.asarray([[1.0, np.nan], [3.0, 10.0]])
        model = ProteinMeanBaseline().fit(np.zeros((2, 1)), targets)
        prediction = model.predict(np.zeros((3, 1)))

        np.testing.assert_allclose(prediction, [[2.0, 10.0]] * 3)

    def test_masked_ridge_learns_each_protein_from_its_finite_rows(self) -> None:
        features = np.asarray([[1.0], [2.0], [3.0], [4.0]])
        targets = np.asarray(
            [[3.0, np.nan], [5.0, 3.0], [7.0, 4.0], [9.0, 5.0]]
        )
        model = MaskedMultiOutputRidge(alpha=1e-8).fit(features, targets)
        prediction = model.predict(np.asarray([[5.0]]))

        np.testing.assert_allclose(prediction, [[11.0, 6.0]], atol=1e-5)


if __name__ == "__main__":
    unittest.main()
