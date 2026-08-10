import unittest

import numpy as np

from pipeline.controls import (
    AnalysisRole,
    ControlEstimand,
    DuplicateMeasurementKeyError,
    EstimandMismatchError,
    MeasurementMatrix,
    MeasurementRole,
    MeasurementRoleError,
    MeasurementShapeError,
    MeasuredControlPairer,
    MisorderedMeasurementError,
    NoCommonMeasurementsError,
    UnmatchedMeasurementError,
    UnknownControlEstimandError,
)


class MeasuredControlPairerTest(unittest.TestCase):
    def test_paired_estimand_subtracts_only_the_same_replicate_and_protein(self) -> None:
        endpoint = MeasurementMatrix(
            values=np.asarray([[10.0, 20.0], [12.0, 25.0]]),
            replicate_ids=("r1", "r2"),
            protein_ids=("p1", "p2"),
            role=MeasurementRole.ENDPOINT,
        )
        control = MeasurementMatrix(
            values=np.asarray([[7.0, 18.0], [8.0, 20.0]]),
            replicate_ids=("r1", "r2"),
            protein_ids=("p1", "p2"),
            role=MeasurementRole.MEASURED_CONTROL,
        )

        response = MeasuredControlPairer().estimate(
            endpoint, control, estimand=ControlEstimand.PAIRED
        )

        np.testing.assert_allclose(response.values, [[3.0, 2.0], [4.0, 5.0]])
        self.assertEqual(response.estimand, ControlEstimand.PAIRED)
        self.assertEqual(response.analysis_role, AnalysisRole.PRIMARY)

    def test_separate_missingness_cannot_manufacture_a_paired_response(self) -> None:
        endpoint_values = np.asarray([[10.0, 5.0], [np.nan, 6.0]])
        control_values = np.asarray([[np.nan, 4.0], [2.0, 5.0]])
        endpoint = MeasurementMatrix(
            values=endpoint_values,
            replicate_ids=("r1", "r2"),
            protein_ids=("p_missing", "p_observed"),
            role=MeasurementRole.ENDPOINT,
        )
        control = MeasurementMatrix(
            values=control_values,
            replicate_ids=("r1", "r2"),
            protein_ids=("p_missing", "p_observed"),
            role=MeasurementRole.MEASURED_CONTROL,
        )

        old_separate_aggregation = np.nanmean(endpoint_values, axis=0) - np.nanmean(
            control_values, axis=0
        )
        response = MeasuredControlPairer().estimate(
            endpoint, control, estimand=ControlEstimand.PAIRED
        )

        self.assertEqual(old_separate_aggregation[0], 8.0)
        self.assertTrue(np.isnan(response.values[:, 0]).all())
        np.testing.assert_allclose(response.values[:, 1], [1.0, 1.0])
        np.testing.assert_array_equal(
            response.valid_mask, [[False, True], [False, True]]
        )

    def test_duplicate_replicate_or_protein_keys_are_rejected(self) -> None:
        endpoint = MeasurementMatrix(
            values=np.asarray([[10.0], [11.0]]),
            replicate_ids=("r1", "r1"),
            protein_ids=("p1",),
            role=MeasurementRole.ENDPOINT,
        )
        control = MeasurementMatrix(
            values=np.asarray([[8.0], [9.0]]),
            replicate_ids=("r1", "r2"),
            protein_ids=("p1",),
            role=MeasurementRole.MEASURED_CONTROL,
        )

        with self.assertRaisesRegex(DuplicateMeasurementKeyError, "replicate"):
            MeasuredControlPairer().estimate(
                endpoint, control, estimand=ControlEstimand.PAIRED
            )

    def test_matrix_shape_must_match_its_replicate_and_protein_keys(self) -> None:
        malformed_endpoint = MeasurementMatrix(
            values=np.asarray([[10.0, 11.0]]),
            replicate_ids=("r1",),
            protein_ids=("p1",),
            role=MeasurementRole.ENDPOINT,
        )
        control = MeasurementMatrix(
            values=np.asarray([[8.0]]),
            replicate_ids=("r1",),
            protein_ids=("p1",),
            role=MeasurementRole.MEASURED_CONTROL,
        )

        with self.assertRaisesRegex(MeasurementShapeError, "protein"):
            MeasuredControlPairer().estimate(
                malformed_endpoint, control, estimand=ControlEstimand.PAIRED
            )

    def test_paired_estimand_rejects_same_replicates_in_a_different_order(self) -> None:
        endpoint = MeasurementMatrix(
            values=np.asarray([[10.0], [11.0]]),
            replicate_ids=("r1", "r2"),
            protein_ids=("p1",),
            role=MeasurementRole.ENDPOINT,
        )
        control = MeasurementMatrix(
            values=np.asarray([[9.0], [8.0]]),
            replicate_ids=("r2", "r1"),
            protein_ids=("p1",),
            role=MeasurementRole.MEASURED_CONTROL,
        )

        with self.assertRaisesRegex(MisorderedMeasurementError, "replicate"):
            MeasuredControlPairer().estimate(
                endpoint, control, estimand=ControlEstimand.PAIRED
            )

    def test_paired_estimand_rejects_same_proteins_in_a_different_order(self) -> None:
        endpoint = MeasurementMatrix(
            values=np.asarray([[10.0, 20.0]]),
            replicate_ids=("r1",),
            protein_ids=("p1", "p2"),
            role=MeasurementRole.ENDPOINT,
        )
        control = MeasurementMatrix(
            values=np.asarray([[18.0, 8.0]]),
            replicate_ids=("r1",),
            protein_ids=("p2", "p1"),
            role=MeasurementRole.MEASURED_CONTROL,
        )

        with self.assertRaisesRegex(MisorderedMeasurementError, "protein"):
            MeasuredControlPairer().estimate(
                endpoint, control, estimand=ControlEstimand.PAIRED
            )

    def test_paired_estimand_rejects_an_unmatched_replicate(self) -> None:
        endpoint = MeasurementMatrix(
            values=np.asarray([[10.0], [11.0]]),
            replicate_ids=("r1", "r2"),
            protein_ids=("p1",),
            role=MeasurementRole.ENDPOINT,
        )
        control = MeasurementMatrix(
            values=np.asarray([[8.0], [9.0]]),
            replicate_ids=("r1", "r3"),
            protein_ids=("p1",),
            role=MeasurementRole.MEASURED_CONTROL,
        )

        with self.assertRaisesRegex(UnmatchedMeasurementError, "replicate"):
            MeasuredControlPairer().estimate(
                endpoint, control, estimand=ControlEstimand.PAIRED
            )

    def test_no_jointly_observed_measurement_is_reported_as_no_match(self) -> None:
        endpoint = MeasurementMatrix(
            values=np.asarray([[10.0], [np.nan]]),
            replicate_ids=("r1", "r2"),
            protein_ids=("p1",),
            role=MeasurementRole.ENDPOINT,
        )
        control = MeasurementMatrix(
            values=np.asarray([[np.nan], [8.0]]),
            replicate_ids=("r1", "r2"),
            protein_ids=("p1",),
            role=MeasurementRole.MEASURED_CONTROL,
        )

        with self.assertRaises(NoCommonMeasurementsError):
            MeasuredControlPairer().estimate(
                endpoint, control, estimand=ControlEstimand.PAIRED
            )

    def test_fold_change_cannot_be_passed_as_a_reconstructed_control(self) -> None:
        endpoint = MeasurementMatrix(
            values=np.asarray([[10.0]]),
            replicate_ids=("r1",),
            protein_ids=("p1",),
            role=MeasurementRole.ENDPOINT,
        )
        fold_change_mislabeled_as_endpoint = MeasurementMatrix(
            values=np.asarray([[2.0]]),
            replicate_ids=("r1",),
            protein_ids=("p1",),
            role=MeasurementRole.ENDPOINT,
        )

        with self.assertRaisesRegex(MeasurementRoleError, "measured control"):
            MeasuredControlPairer().estimate(
                endpoint,
                fold_change_mislabeled_as_endpoint,
                estimand=ControlEstimand.PAIRED,
            )

    def test_independent_all_control_mean_is_explicitly_a_sensitivity_analysis(self) -> None:
        endpoint = MeasurementMatrix(
            values=np.asarray([[10.0, np.nan], [12.0, 24.0]]),
            replicate_ids=("treated-1", "treated-2"),
            protein_ids=("p1", "p2"),
            role=MeasurementRole.ENDPOINT,
        )
        controls = MeasurementMatrix(
            values=np.asarray([[6.0, 18.0], [8.0, np.nan], [10.0, 22.0]]),
            replicate_ids=("control-1", "control-2", "control-3"),
            protein_ids=("p1", "p2"),
            role=MeasurementRole.MEASURED_CONTROL,
        )

        response = MeasuredControlPairer().estimate(
            endpoint,
            controls,
            estimand=ControlEstimand.INDEPENDENT_ALL_CONTROL_SENSITIVITY,
        )

        np.testing.assert_allclose(
            response.values, [[2.0, np.nan], [4.0, 4.0]], equal_nan=True
        )
        self.assertEqual(
            response.estimand, ControlEstimand.INDEPENDENT_ALL_CONTROL_SENSITIVITY
        )
        self.assertEqual(response.analysis_role, AnalysisRole.SENSITIVITY)
        with self.assertRaises(EstimandMismatchError):
            response.require_estimand(ControlEstimand.PAIRED)

    def test_unknown_estimand_cannot_silently_be_labeled_as_sensitivity(self) -> None:
        endpoint = MeasurementMatrix(
            values=np.asarray([[10.0]]),
            replicate_ids=("r1",),
            protein_ids=("p1",),
            role=MeasurementRole.ENDPOINT,
        )
        control = MeasurementMatrix(
            values=np.asarray([[8.0]]),
            replicate_ids=("r1",),
            protein_ids=("p1",),
            role=MeasurementRole.MEASURED_CONTROL,
        )

        with self.assertRaises(UnknownControlEstimandError):
            MeasuredControlPairer().estimate(endpoint, control, estimand="paired")


if __name__ == "__main__":
    unittest.main()
