import unittest

import numpy as np
import pandas as pd

from evaluation import (
    DEPPolicy,
    EvaluationInput,
    ResidualReferenceMode,
    fit_fixed_threshold_dep_policy,
)
from evaluation.official_scorecard import (
    COMPLIANCE_GATE,
    OFFICIAL_MODULE_WEIGHTS_PERCENT,
    OPEN_SOURCE_CONTRIBUTION,
    MetricFamily,
    OfficialScorecard,
    OfficialModule,
    SplitKind,
    route_for_split,
)
from evaluation.residuals import (
    TrainOnlyProvenance,
    fit_frozen_residual_references,
    verify_train_only_provenance,
)
from pipeline import (
    OfficialControlMatchColumns,
    OfficialVehicleMap,
    Vehicle,
    match_exploratory_controls,
    match_official_controls,
)
from pipeline.controls import (
    ControlEstimand,
    MeasurementMatrix,
    MeasurementRole,
    MeasuredControlPairer,
)


class OfficialScorecardContractTest(unittest.TestCase):
    @staticmethod
    def official_inputs(*, include_dep: bool = True) -> EvaluationInput:
        truth = np.asarray(
            [
                [12.0, 18.0, 10.5, 24.0],
                [13.0, 17.0, 9.0, 22.0],
                [11.5, 19.0, 13.0, 18.0],
            ]
        )
        control = np.asarray([[10.0, 20.0, 10.0, 20.0]] * 3)
        replicate_ids = ("held-0", "held-1", "held-2")
        protein_ids = ("p0", "p1", "p2", "p3")
        paired = MeasuredControlPairer().estimate(
            MeasurementMatrix(
                truth,
                replicate_ids,
                protein_ids,
                MeasurementRole.ENDPOINT,
            ),
            MeasurementMatrix(
                control,
                replicate_ids,
                protein_ids,
                MeasurementRole.MEASURED_CONTROL,
            ),
            estimand=ControlEstimand.PAIRED,
        )
        fit_fc = np.asarray(
            [
                [1.0, -1.5, 0.2, 3.0],
                [2.0, -2.0, -0.5, 1.0],
                [0.5, -1.2, 2.0, -3.0],
            ]
        )
        fit_ids = ("fit-0", "fit-1", "fit-2")
        provenance = verify_train_only_provenance(
            replicate_ids=fit_ids,
            split_labels=("train",) * 3,
            source_sha256="c" * 64,
        )
        references = fit_frozen_residual_references(
            fit_fc,
            fit_context_groups=("c1", "c1", "c2"),
            fit_drug_groups=("d1", "d2", "d1"),
            evaluation_context_groups=("c1", "c1", "c2"),
            evaluation_drug_groups=("d1", "d2", "d1"),
            evaluation_replicate_ids=replicate_ids,
            protein_ids=protein_ids,
            fit_replicate_ids=fit_ids,
            fit_provenance=provenance,
        )
        return EvaluationInput(
            truth_endpoint=truth,
            prediction_endpoint=truth.copy(),
            paired_response=paired,
            context_groups=("c1", "c1", "c2"),
            drug_groups=("d1", "d2", "d1"),
            residual_reference_mode=ResidualReferenceMode.FIT_FROZEN,
            frozen_residual_references=references,
            dep_policy=(
                fit_fixed_threshold_dep_policy(
                    fit_fc, threshold=1.0, min_k=1, max_fraction=1.0
                )
                if include_dep
                else None
            ),
        )

    def test_weights_and_split_routes_are_declared_without_an_invented_total(self) -> None:
        self.assertEqual(
            dict(OFFICIAL_MODULE_WEIGHTS_PERCENT),
            {
                OfficialModule.ABSOLUTE_FIDELITY: 20,
                OfficialModule.MATCHED_CONTROL_RAW_FC: 25,
                OfficialModule.CONTEXT_MEAN_RESIDUAL: 20,
                OfficialModule.DRUG_MEAN_RESIDUAL: 20,
                OfficialModule.DOUBLE_UNKNOWN_OR_TIME: 10,
                OfficialModule.HIGH_RESPONSE_DEP: 5,
            },
        )
        self.assertEqual(
            route_for_split(SplitKind.TEST_CHEM_ONLY).required_metric_families,
            (
                MetricFamily.ABSOLUTE_FIDELITY,
                MetricFamily.MATCHED_CONTROL_RAW_FC,
                MetricFamily.CONTEXT_MEAN_RESIDUAL,
                MetricFamily.HIGH_RESPONSE_DEP,
            ),
        )
        self.assertEqual(
            route_for_split(SplitKind.TEST_STRAIN_ONLY).required_metric_families,
            (
                MetricFamily.ABSOLUTE_FIDELITY,
                MetricFamily.MATCHED_CONTROL_RAW_FC,
                MetricFamily.DRUG_MEAN_RESIDUAL,
                MetricFamily.HIGH_RESPONSE_DEP,
            ),
        )
        for split in (SplitKind.TEST_BOTH, SplitKind.TEST_TIME):
            self.assertIn(
                MetricFamily.DOUBLE_UNKNOWN_OR_TIME,
                route_for_split(split).required_metric_families,
            )
        self.assertTrue(COMPLIANCE_GATE.is_separate_gate)
        self.assertIsNone(COMPLIANCE_GATE.weight_percent)
        self.assertTrue(OPEN_SOURCE_CONTRIBUTION.is_separate_dimension)
        self.assertEqual(OPEN_SOURCE_CONTRIBUTION.weight_percent, 5)
        self.assertFalse(hasattr(route_for_split(SplitKind.TEST_BOTH), "weighted_total"))

    def test_official_control_matcher_rejects_an_arbitrary_column_subset(self) -> None:
        metadata = pd.DataFrame(
            {
                "sample_ID": ["treated", "control"],
                "chemical": ["drug-a", "DMSO"],
                "source": ["S", "S"],
            }
        )
        with self.assertRaisesRegex(ValueError, "all seven official control-match roles"):
            match_official_controls(
                metadata,
                np.asarray([[11.0], [10.0]]),
                protein_ids=("p1",),
                treated_sample_ids=("treated",),
                vehicle_map=OfficialVehicleMap.from_mapping({"drug-a": "DMSO"}),
                sample_id_column="sample_ID",
                chemical_column="chemical",
                match_columns=("source",),
            )

    def test_manually_forged_vehicle_map_cannot_enter_official_pairing(self) -> None:
        forged = OfficialVehicleMap(assignments={"drug-a": Vehicle.DMSO})
        with self.assertRaisesRegex(ValueError, "verified chemical-to-vehicle map"):
            forged.resolve("drug-a")

    def test_exploratory_control_matcher_keeps_the_subset_api_clearly_labeled(self) -> None:
        metadata = pd.DataFrame(
            {
                "sample_ID": ["treated", "control"],
                "chemical": ["drug-a", "DMSO"],
                "source": ["S", "S"],
            }
        )
        endpoint, control = match_exploratory_controls(
            metadata,
            np.asarray([[11.0], [10.0]]),
            protein_ids=("p1",),
            treated_sample_ids=("treated",),
            vehicle_map=OfficialVehicleMap.from_mapping({"drug-a": "DMSO"}),
            sample_id_column="sample_ID",
            chemical_column="chemical",
            match_columns=("source",),
        )
        np.testing.assert_allclose(endpoint.values, [[11.0]])
        np.testing.assert_allclose(control.values, [[10.0]])

    def test_official_control_roles_can_bind_to_actual_source_column_names(self) -> None:
        physical = {
            "source": "data_source",
            "strain": "Strains",
            "medium": "Medium",
            "temperature": "Temperature",
            "time": "pert_time",
            "instrument": "instrument",
            "plate": "plate",
        }
        metadata = pd.DataFrame(
            {
                "sample_ID": ["treated", "control"],
                "chemical": ["drug-a", "DMSO"],
                **{column: [role, role] for role, column in physical.items()},
            }
        )
        endpoint, control = match_official_controls(
            metadata,
            np.asarray([[11.0], [10.0]]),
            protein_ids=("p1",),
            treated_sample_ids=("treated",),
            vehicle_map=OfficialVehicleMap.from_mapping({"drug-a": "DMSO"}),
            sample_id_column="sample_ID",
            chemical_column="chemical",
            match_columns=OfficialControlMatchColumns(**physical),
        )
        np.testing.assert_allclose(endpoint.values, [[11.0]])
        np.testing.assert_allclose(control.values, [[10.0]])

    def test_residual_reference_provenance_rejects_any_non_train_row(self) -> None:
        with self.assertRaisesRegex(ValueError, "verified train-only"):
            verify_train_only_provenance(
                replicate_ids=("fit-1", "held-1"),
                split_labels=("train", "validation"),
                source_sha256="a" * 64,
            )

    def test_fit_frozen_references_fail_without_verified_train_provenance(self) -> None:
        with self.assertRaisesRegex(ValueError, "verified train-only provenance"):
            fit_frozen_residual_references(
                np.asarray([[1.0, 2.0]]),
                fit_context_groups=("context",),
                fit_drug_groups=("drug",),
                evaluation_context_groups=("context",),
                evaluation_drug_groups=("new-drug",),
                evaluation_replicate_ids=("held-1",),
                protein_ids=("p1", "p2"),
            )

    def test_fit_frozen_references_reject_fit_evaluation_identity_overlap(self) -> None:
        provenance = verify_train_only_provenance(
            replicate_ids=("fit-1",),
            split_labels=("train",),
            source_sha256="b" * 64,
        )
        with self.assertRaisesRegex(ValueError, "must be disjoint"):
            fit_frozen_residual_references(
                np.asarray([[1.0, 2.0]]),
                fit_context_groups=("context",),
                fit_drug_groups=("drug",),
                evaluation_context_groups=("context",),
                evaluation_drug_groups=("new-drug",),
                evaluation_replicate_ids=("fit-1",),
                protein_ids=("p1", "p2"),
                fit_replicate_ids=("fit-1",),
                fit_provenance=provenance,
            )

    def test_manually_forged_train_provenance_cannot_seal_references(self) -> None:
        forged = TrainOnlyProvenance(
            replicate_ids=("fit-1",),
            source_sha256="f" * 64,
        )
        with self.assertRaisesRegex(ValueError, "train-only verifier"):
            fit_frozen_residual_references(
                np.asarray([[1.0, 2.0]]),
                fit_context_groups=("context",),
                fit_drug_groups=("drug",),
                evaluation_context_groups=("context",),
                evaluation_drug_groups=("new-drug",),
                evaluation_replicate_ids=("held-1",),
                protein_ids=("p1", "p2"),
                fit_replicate_ids=("fit-1",),
                fit_provenance=forged,
            )

    def test_production_chem_scorecard_routes_metrics_and_records_coverage(self) -> None:
        result = OfficialScorecard().evaluate(
            split=SplitKind.TEST_CHEM_ONLY,
            inputs=self.official_inputs(),
        )

        self.assertEqual(result.split, SplitKind.TEST_CHEM_ONLY)
        self.assertEqual(
            tuple(result.module_metrics),
            route_for_split(SplitKind.TEST_CHEM_ONLY).required_metric_families,
        )
        self.assertIn(
            "endpoint_macro_protein_pcc",
            result.module_metrics[MetricFamily.ABSOLUTE_FIDELITY],
        )
        self.assertNotIn(
            "endpoint_paired_pcc",
            result.module_metrics[MetricFamily.ABSOLUTE_FIDELITY],
        )
        self.assertNotIn(
            "endpoint_rmse",
            result.module_metrics[MetricFamily.ABSOLUTE_FIDELITY],
        )
        self.assertNotIn(
            "raw_fc_rmse",
            result.module_metrics[MetricFamily.MATCHED_CONTROL_RAW_FC],
        )
        self.assertIn(
            "context_residual_pcc",
            result.module_metrics[MetricFamily.CONTEXT_MEAN_RESIDUAL],
        )
        self.assertIn(
            "signed_f1_at_k",
            result.module_metrics[MetricFamily.HIGH_RESPONSE_DEP],
        )
        self.assertNotIn(
            "high_response_rmse",
            result.module_metrics[MetricFamily.HIGH_RESPONSE_DEP],
        )
        self.assertEqual(result.coverage_denominators["endpoint_total_cells"], 12)
        self.assertEqual(result.coverage_denominators["endpoint_conditions_total"], 3)
        self.assertEqual(result.coverage_denominators["endpoint_proteins_total"], 4)
        self.assertEqual(
            result.coverage_denominators["endpoint_conditions_with_defined_pcc"], 3
        )
        self.assertEqual(
            result.coverage_denominators["endpoint_proteins_with_defined_pcc"], 4
        )
        self.assertEqual(result.coverage_denominators["endpoint_truth_valid_cells"], 12)
        self.assertEqual(
            result.coverage_denominators["prediction_finite_on_truth_cells"], 12
        )
        self.assertEqual(result.coverage_denominators["direct_control_paired_cells"], 12)
        self.assertEqual(result.coverage_denominators["residual_reference_required_cells"], 12)
        self.assertEqual(result.coverage_denominators["residual_reference_available_cells"], 12)
        self.assertEqual(result.coverage_denominators["dep_truth_positive_cells"], 9)
        self.assertEqual(result.coverage_denominators["samples_with_truth_dep"], 3)
        self.assertFalse(hasattr(result, "official_total"))

    def test_production_scorecard_rejects_missing_dep_policy_on_every_route(self) -> None:
        for split in SplitKind:
            with self.subTest(split=split):
                with self.assertRaisesRegex(ValueError, "requires a DEP policy"):
                    OfficialScorecard().evaluate(
                        split=split,
                        inputs=self.official_inputs(include_dep=False),
                    )

    def test_production_scorecard_rejects_non_strict_dep_threshold_policy(self) -> None:
        inputs = self.official_inputs()
        bypass = EvaluationInput(
            truth_endpoint=inputs.truth_endpoint,
            prediction_endpoint=inputs.prediction_endpoint,
            paired_response=inputs.paired_response,
            context_groups=inputs.context_groups,
            drug_groups=inputs.drug_groups,
            residual_reference_mode=inputs.residual_reference_mode,
            frozen_residual_references=inputs.frozen_residual_references,
            dep_policy=DEPPolicy(
                threshold=1.0,
                k=inputs.dep_policy.k,
                panel_width=inputs.dep_policy.panel_width,
                strict_greater=False,
            ),
        )
        with self.assertRaisesRegex(ValueError, r"abs\(raw FC\) > 1"):
            OfficialScorecard().evaluate(
                split=SplitKind.TEST_CHEM_ONLY,
                inputs=bypass,
            )

    def test_production_scorecard_cannot_hide_a_truth_valid_cell_with_nan(self) -> None:
        inputs = self.official_inputs()
        prediction = np.array(inputs.prediction_endpoint, copy=True)
        prediction[0, 0] = np.nan
        bypass = EvaluationInput(
            truth_endpoint=inputs.truth_endpoint,
            prediction_endpoint=prediction,
            paired_response=inputs.paired_response,
            context_groups=inputs.context_groups,
            drug_groups=inputs.drug_groups,
            residual_reference_mode=inputs.residual_reference_mode,
            frozen_residual_references=inputs.frozen_residual_references,
            dep_policy=inputs.dep_policy,
        )
        with self.assertRaisesRegex(ValueError, "may not use NaN to opt out"):
            OfficialScorecard().evaluate(
                split=SplitKind.TEST_CHEM_ONLY,
                inputs=bypass,
            )

    def test_residual_routes_fail_when_the_frozen_reference_is_missing(self) -> None:
        inputs = self.official_inputs()
        bypass = EvaluationInput(
            truth_endpoint=inputs.truth_endpoint,
            prediction_endpoint=inputs.prediction_endpoint,
            paired_response=inputs.paired_response,
            context_groups=inputs.context_groups,
            drug_groups=inputs.drug_groups,
            residual_reference_mode=ResidualReferenceMode.FIT_FROZEN,
            frozen_residual_references=None,
            dep_policy=inputs.dep_policy,
        )
        for split in (SplitKind.TEST_CHEM_ONLY, SplitKind.TEST_STRAIN_ONLY):
            with self.subTest(split=split):
                with self.assertRaisesRegex(ValueError, "requires fit-frozen references"):
                    OfficialScorecard().evaluate(split=split, inputs=bypass)

    def test_strain_route_requires_and_reports_drug_mean_residual(self) -> None:
        result = OfficialScorecard().evaluate(
            split=SplitKind.TEST_STRAIN_ONLY,
            inputs=self.official_inputs(),
        )
        self.assertIn(MetricFamily.DRUG_MEAN_RESIDUAL, result.module_metrics)
        self.assertNotIn(MetricFamily.CONTEXT_MEAN_RESIDUAL, result.module_metrics)
        self.assertIn(
            "drug_residual_pcc",
            result.module_metrics[MetricFamily.DRUG_MEAN_RESIDUAL],
        )

    def test_both_and_time_routes_do_not_force_an_irrelevant_residual_reference(self) -> None:
        inputs = self.official_inputs()
        non_residual = EvaluationInput(
            truth_endpoint=inputs.truth_endpoint,
            prediction_endpoint=inputs.prediction_endpoint,
            paired_response=inputs.paired_response,
            context_groups=inputs.context_groups,
            drug_groups=inputs.drug_groups,
            residual_reference_mode=ResidualReferenceMode.NOT_APPLICABLE,
            frozen_residual_references=None,
            dep_policy=inputs.dep_policy,
        )
        for split in (SplitKind.TEST_BOTH, SplitKind.TEST_TIME):
            with self.subTest(split=split):
                result = OfficialScorecard().evaluate(split=split, inputs=non_residual)
                self.assertIn(
                    MetricFamily.DOUBLE_UNKNOWN_OR_TIME,
                    result.module_metrics,
                )
                self.assertNotIn(
                    MetricFamily.CONTEXT_MEAN_RESIDUAL,
                    result.module_metrics,
                )
                self.assertNotIn(
                    MetricFamily.DRUG_MEAN_RESIDUAL,
                    result.module_metrics,
                )


if __name__ == "__main__":
    unittest.main()
