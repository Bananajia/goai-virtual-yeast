import unittest

from evaluation import MetricCriterion, PromotionGate


class PromotionGateTest(unittest.TestCase):
    def test_higher_and_lower_is_better_are_normalized(self) -> None:
        decision = PromotionGate(
            criteria=(
                MetricCriterion("raw_fc_pcc", minimum_gain=0.01, higher_is_better=True),
                MetricCriterion("raw_fc_rmse", minimum_gain=0.02, higher_is_better=False),
            )
        ).evaluate(
            candidate={"raw_fc_pcc": 0.31, "raw_fc_rmse": 0.40},
            reference={"raw_fc_pcc": 0.29, "raw_fc_rmse": 0.43},
        )

        self.assertTrue(decision.passed)
        self.assertAlmostEqual(decision.gains["raw_fc_pcc"], 0.02)
        self.assertAlmostEqual(decision.gains["raw_fc_rmse"], 0.03)

    def test_one_failed_criterion_rejects_joint_gate(self) -> None:
        decision = PromotionGate(
            criteria=(MetricCriterion("raw_fc_pcc", minimum_gain=0.01),)
        ).evaluate(
            candidate={"raw_fc_pcc": 0.295}, reference={"raw_fc_pcc": 0.29}
        )
        self.assertFalse(decision.passed)


if __name__ == "__main__":
    unittest.main()
