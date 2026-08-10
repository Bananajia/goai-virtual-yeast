import math
import unittest

import numpy as np

from evaluation import EvaluationInput, EvaluationSuite, finite_pearson, group_center_common
from pipeline.controls import (
    AnalysisRole,
    ControlEstimand,
    MeasurementMatrix,
    MeasurementRole,
    MeasuredControlPairer,
    MeasurementRoleError,
    ResponseEstimate,
)


class EvaluationSuiteTest(unittest.TestCase):
    def setUp(self) -> None:
        self.truth = np.asarray(
            [
                [11.0, 22.0, 33.0, 44.0],
                [12.0, 20.0, 36.0, 40.0],
                [9.0, 24.0, 30.0, 48.0],
            ]
        )
        self.control = np.asarray(
            [
                [10.0, 20.0, 30.0, 40.0],
                [10.0, 20.0, 30.0, 40.0],
                [10.0, 20.0, 30.0, 40.0],
            ]
        )

    @staticmethod
    def paired_response(endpoint: np.ndarray, control: np.ndarray):
        rows, proteins = endpoint.shape
        return MeasuredControlPairer().estimate(
            MeasurementMatrix(
                values=endpoint,
                replicate_ids=tuple(f"r-{index}" for index in range(rows)),
                protein_ids=tuple(f"p-{index}" for index in range(proteins)),
                role=MeasurementRole.ENDPOINT,
            ),
            MeasurementMatrix(
                values=control,
                replicate_ids=tuple(f"r-{index}" for index in range(rows)),
                protein_ids=tuple(f"p-{index}" for index in range(proteins)),
                role=MeasurementRole.MEASURED_CONTROL,
            ),
            estimand=ControlEstimand.PAIRED,
        )

    def test_perfect_prediction_scores_one_and_uses_direct_control(self) -> None:
        result = EvaluationSuite().evaluate(
            EvaluationInput(
                truth_endpoint=self.truth,
                prediction_endpoint=self.truth.copy(),
                paired_response=self.paired_response(self.truth, self.control),
                context_groups=("c1", "c1", "c1"),
                drug_groups=("d1", "d1", "d2"),
            )
        )

        self.assertAlmostEqual(result.metrics["endpoint_pcc"], 1.0)
        self.assertAlmostEqual(result.metrics["endpoint_pooled_pcc"], 1.0)
        self.assertAlmostEqual(result.metrics["endpoint_pooled_r2"], 1.0)
        self.assertAlmostEqual(result.metrics["endpoint_mean_protein_r2"], 1.0)
        self.assertAlmostEqual(result.metrics["raw_fc_pcc"], 1.0)
        self.assertAlmostEqual(result.metrics["endpoint_rmse"], 0.0)
        self.assertAlmostEqual(result.metrics["raw_fc_rmse"], 0.0)
        self.assertAlmostEqual(result.metrics["endpoint_paired_rmse"], 0.0)
        self.assertTrue(result.contract["measured_control_passed_directly"])
        self.assertEqual(result.counts["raw_fc_cells"], 12)

    def test_response_metrics_use_truth_prediction_control_common_mask(self) -> None:
        prediction = self.truth.copy()
        control = self.control.copy()
        control[0, 0] = np.nan
        prediction[1, 1] = np.nan

        result = EvaluationSuite().evaluate(
            EvaluationInput(
                truth_endpoint=self.truth,
                prediction_endpoint=prediction,
                paired_response=self.paired_response(self.truth, control),
                context_groups=("c1", "c1", "c1"),
                drug_groups=("d1", "d1", "d2"),
            )
        )

        self.assertEqual(result.counts["endpoint_cells"], 11)
        self.assertEqual(result.counts["raw_fc_cells"], 10)
        self.assertEqual(result.counts["endpoint_paired_cells"], 10)
        self.assertAlmostEqual(result.metrics["raw_fc_rmse"], 0.0)
        self.assertAlmostEqual(
            result.metrics["endpoint_paired_rmse"], result.metrics["raw_fc_rmse"]
        )

    def test_group_center_excludes_group_protein_singletons(self) -> None:
        truth = np.asarray([[1.0, np.nan], [np.nan, 4.0], [3.0, 6.0]])
        prediction = truth.copy()

        centered_truth, centered_prediction = group_center_common(
            truth, prediction, ("a", "a", "b")
        )

        self.assertTrue(np.isnan(centered_truth).all())
        self.assertTrue(np.isnan(centered_prediction).all())

    def test_constant_across_conditions_prediction_has_zero_variance_ratio(self) -> None:
        prediction = np.asarray(
            [
                [11.0, 22.0, 33.0, 44.0],
                [11.0, 22.0, 33.0, 44.0],
                [11.0, 22.0, 33.0, 44.0],
            ]
        )
        result = EvaluationSuite().evaluate(
            EvaluationInput(
                truth_endpoint=self.truth,
                prediction_endpoint=prediction,
                paired_response=self.paired_response(self.truth, self.control),
                context_groups=("c1", "c1", "c1"),
                drug_groups=("d1", "d1", "d2"),
            )
        )

        self.assertAlmostEqual(result.metrics["condition_variance_ratio"], 0.0)
        self.assertTrue(math.isfinite(result.metrics["raw_fc_pcc"]))

    def test_constant_prediction_is_zero_correlation_not_silently_dropped(self) -> None:
        self.assertAlmostEqual(
            finite_pearson(np.asarray([1.0, 2.0, 3.0]), np.asarray([4.0, 4.0, 4.0])),
            0.0,
        )
        self.assertTrue(
            math.isnan(
                finite_pearson(
                    np.asarray([1.0, 1.0, 1.0]), np.asarray([1.0, 2.0, 3.0])
                )
            )
        )

    def test_doubled_response_has_pcc_one_and_variance_ratio_four(self) -> None:
        truth_fc = self.truth - self.control
        prediction = self.control + 2.0 * truth_fc
        result = EvaluationSuite().evaluate(
            EvaluationInput(
                truth_endpoint=self.truth,
                prediction_endpoint=prediction,
                paired_response=self.paired_response(self.truth, self.control),
                context_groups=("c1", "c1", "c1"),
                drug_groups=("d1", "d1", "d2"),
            )
        )

        self.assertAlmostEqual(result.metrics["raw_fc_pcc"], 1.0)
        self.assertAlmostEqual(result.metrics["condition_variance_ratio"], 4.0)
        self.assertGreater(result.metrics["amplitude_log_error"], 0.0)

    def test_bare_or_reconstructed_control_array_is_rejected(self) -> None:
        with self.assertRaisesRegex(TypeError, "verified paired measured-control"):
            EvaluationSuite().evaluate(
                EvaluationInput(
                    truth_endpoint=self.truth,
                    prediction_endpoint=self.truth.copy(),
                    paired_response=self.control,
                    context_groups=("c1", "c1", "c1"),
                    drug_groups=("d1", "d1", "d2"),
                )
            )

    def test_paired_response_must_reference_the_same_truth_endpoint(self) -> None:
        altered_truth = self.truth.copy()
        altered_truth[0, 0] += 1.0
        with self.assertRaisesRegex(ValueError, "paired endpoint reference"):
            EvaluationSuite().evaluate(
                EvaluationInput(
                    truth_endpoint=altered_truth,
                    prediction_endpoint=altered_truth.copy(),
                    paired_response=self.paired_response(self.truth, self.control),
                    context_groups=("c1", "c1", "c1"),
                    drug_groups=("d1", "d1", "d2"),
                )
            )

    def test_manually_forged_response_without_pairer_seal_is_rejected(self) -> None:
        forged = ResponseEstimate(
            values=self.truth - self.control,
            valid_mask=np.ones_like(self.truth, dtype=bool),
            endpoint_reference=self.truth,
            control_reference=self.control,
            estimand=ControlEstimand.PAIRED,
            analysis_role=AnalysisRole.PRIMARY,
            replicate_ids=("r1", "r2", "r3"),
            protein_ids=("p1", "p2", "p3", "p4"),
        )
        with self.assertRaisesRegex(
            MeasurementRoleError, "verified paired measured-control"
        ):
            EvaluationSuite().evaluate(
                EvaluationInput(
                    truth_endpoint=self.truth,
                    prediction_endpoint=self.truth.copy(),
                    paired_response=forged,
                    context_groups=("c1", "c1", "c1"),
                    drug_groups=("d1", "d1", "d2"),
                )
            )


if __name__ == "__main__":
    unittest.main()
