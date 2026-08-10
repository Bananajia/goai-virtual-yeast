import unittest

import numpy as np

from evaluation import DEPPolicy, fit_dep_policy, high_response_metrics


class DEPMetricTest(unittest.TestCase):
    def test_policy_is_fit_only(self) -> None:
        fit_fc = np.asarray([[0.0, 1.0, 2.0, 3.0], [0.0, 1.5, 2.5, 3.5]])
        policy_before = fit_dep_policy(fit_fc, quantile=0.75, min_k=1)
        _held_extreme = np.asarray([[1e9, -1e9, 0.0, 0.0]])
        policy_after = fit_dep_policy(fit_fc, quantile=0.75, min_k=1)

        self.assertEqual(policy_before, policy_after)

    def test_sign_reversal_can_rank_deps_but_has_zero_signed_hits(self) -> None:
        truth = np.asarray([[2.0, -3.0, 0.1, 0.2]])
        prediction = -truth
        result = high_response_metrics(
            truth, prediction, DEPPolicy(threshold=1.0, k=2, panel_width=4)
        )

        self.assertAlmostEqual(result["macro_auprc"], 1.0)
        self.assertAlmostEqual(result["signed_precision_at_k"], 0.0)
        self.assertAlmostEqual(result["signed_recall_at_k"], 0.0)
        self.assertAlmostEqual(result["topk_direction_consistency"], 0.0)


if __name__ == "__main__":
    unittest.main()
