from __future__ import annotations

import unittest

import numpy as np

from mijiao_predict_v0.mijiao_predict import (
    Availability,
    ExpertKind,
    ExpertSpec,
    MiJiaoPredict,
    OutputMode,
    PromotionStatus,
    QueryEvidence,
)


class ConstantPredictor:
    def __init__(self, value: float) -> None:
        self.value = float(value)
        self.calls = 0

    def predict(self, features: np.ndarray) -> np.ndarray:
        self.calls += 1
        return np.full((len(features), 2), self.value, dtype=np.float64)


class NonfinitePredictor:
    def predict(self, features: np.ndarray) -> np.ndarray:
        return np.full((len(features), 2), np.nan, dtype=np.float64)


class MiJiaoPredictTest(unittest.TestCase):
    def test_rejected_structure_expert_falls_back_to_core_exactly(self) -> None:
        core = ConstantPredictor(10.0)
        structure = ConstantPredictor(3.0)
        model = MiJiaoPredict(
            core=core,
            experts=(
                ExpertSpec(
                    name="morgan_structure",
                    kind=ExpertKind.STRUCTURE,
                    predictor=structure,
                    availability=Availability.EXECUTABLE,
                    promotion=PromotionStatus.REJECTED,
                    feature_view="structure",
                    output_mode=OutputMode.RESIDUAL,
                ),
            ),
        )
        evidence = (
            QueryEvidence(
                chemical_seen=False,
                strain_seen=True,
                is_time_extrapolation=False,
                base_condition_seen=False,
                has_structure=True,
                has_chemical_features=True,
                has_strain_support=False,
                has_time_support=False,
            ),
        )

        result = model.predict_with_audit(
            feature_views={
                "metadata": np.zeros((1, 1)),
                "structure": np.ones((1, 4)),
            },
            evidence=evidence,
        )

        np.testing.assert_array_equal(result.prediction, [[10.0, 10.0]])
        self.assertEqual(result.routes[0].selected_model, "metadata_ridge")
        self.assertEqual(result.routes[0].reason, "no_eligible_unseen_chemical_expert")
        self.assertEqual(structure.calls, 0)

    def test_promoted_strain_residual_overlays_only_supported_unknown_strain_rows(self) -> None:
        core = ConstantPredictor(10.0)
        strain = ConstantPredictor(2.0)
        model = MiJiaoPredict(
            core=core,
            experts=(
                ExpertSpec(
                    name="cross_strain_residual_memory",
                    kind=ExpertKind.STRAIN,
                    predictor=strain,
                    availability=Availability.EXECUTABLE,
                    promotion=PromotionStatus.PROMOTED_SCOPED,
                    feature_view="strain",
                    output_mode=OutputMode.RESIDUAL,
                ),
            ),
        )
        evidence = (
            QueryEvidence(False, False, False, False, False, False, True, False),
            QueryEvidence(True, False, False, False, False, False, True, False),
            QueryEvidence(True, True, False, True, False, False, False, False),
        )

        result = model.predict_with_audit(
            feature_views={
                "metadata": np.zeros((3, 1)),
                "strain": np.ones((3, 3)),
            },
            evidence=evidence,
        )

        np.testing.assert_array_equal(
            result.prediction,
            [[10.0, 10.0], [12.0, 12.0], [10.0, 10.0]],
        )
        self.assertEqual(result.routes[0].reason, "double_unknown_fallback")
        self.assertEqual(result.routes[1].selected_model, "cross_strain_residual_memory")
        self.assertEqual(result.routes[2].reason, "core_default")
        self.assertEqual(strain.calls, 1)

    def test_time_expert_requires_seen_base_condition_and_time_support(self) -> None:
        core = ConstantPredictor(10.0)
        time = ConstantPredictor(7.0)
        model = MiJiaoPredict(
            core=core,
            experts=(
                ExpertSpec(
                    name="rank32_time_trajectory",
                    kind=ExpertKind.TIME,
                    predictor=time,
                    availability=Availability.EXECUTABLE,
                    promotion=PromotionStatus.PROMOTED_SCOPED,
                    feature_view="time",
                    output_mode=OutputMode.REPLACEMENT,
                ),
            ),
        )
        evidence = (
            QueryEvidence(True, True, True, True, False, False, False, True),
            QueryEvidence(True, True, True, False, False, False, False, True),
        )

        result = model.predict_with_audit(
            feature_views={
                "metadata": np.zeros((2, 1)),
                "time": np.ones((2, 2)),
            },
            evidence=evidence,
        )

        np.testing.assert_array_equal(result.prediction, [[7.0, 7.0], [10.0, 10.0]])
        self.assertEqual(result.routes[0].reason, "promoted_time_expert")
        self.assertEqual(result.routes[1].reason, "time_support_missing")

    def test_unseen_chemical_prefers_promoted_structure_then_chemical_fallback(self) -> None:
        model = MiJiaoPredict(
            core=ConstantPredictor(10.0),
            experts=(
                ExpertSpec(
                    name="morgan_structure",
                    kind=ExpertKind.STRUCTURE,
                    predictor=ConstantPredictor(3.0),
                    availability=Availability.EXECUTABLE,
                    promotion=PromotionStatus.PROMOTED_SCOPED,
                    feature_view="structure",
                    output_mode=OutputMode.RESIDUAL,
                ),
                ExpertSpec(
                    name="chemical_calibration",
                    kind=ExpertKind.CHEMICAL,
                    predictor=ConstantPredictor(5.0),
                    availability=Availability.EXECUTABLE,
                    promotion=PromotionStatus.PROMOTED_SCOPED,
                    feature_view="chemical",
                    output_mode=OutputMode.RESIDUAL,
                ),
            ),
        )
        evidence = (
            QueryEvidence(False, True, False, False, True, True, False, False),
            QueryEvidence(False, True, False, False, False, True, False, False),
            QueryEvidence(False, True, False, False, False, False, False, False),
        )

        result = model.predict_with_audit(
            feature_views={
                "metadata": np.zeros((3, 1)),
                "structure": np.ones((3, 4)),
                "chemical": np.ones((3, 2)),
            },
            evidence=evidence,
        )

        np.testing.assert_array_equal(
            result.prediction,
            [[13.0, 13.0], [15.0, 15.0], [10.0, 10.0]],
        )
        self.assertEqual(result.routes[0].reason, "promoted_structure_expert")
        self.assertEqual(result.routes[1].reason, "promoted_chemical_expert")
        self.assertEqual(result.routes[2].reason, "chemical_evidence_missing")

    def test_declared_evidence_without_feature_view_falls_back_to_core(self) -> None:
        structure = ConstantPredictor(3.0)
        model = MiJiaoPredict(
            core=ConstantPredictor(10.0),
            experts=(
                ExpertSpec(
                    name="morgan_structure",
                    kind=ExpertKind.STRUCTURE,
                    predictor=structure,
                    availability=Availability.EXECUTABLE,
                    promotion=PromotionStatus.PROMOTED_SCOPED,
                    feature_view="structure",
                ),
            ),
        )

        result = model.predict_with_audit(
            feature_views={"metadata": np.zeros((1, 1))},
            evidence=(
                QueryEvidence(False, True, False, False, True, True, False, False),
            ),
        )

        np.testing.assert_array_equal(result.prediction, [[10.0, 10.0]])
        self.assertEqual(result.routes[0].reason, "expert_feature_view_missing")
        self.assertEqual(structure.calls, 0)

    def test_predict_and_model_manifest_are_small_public_interfaces(self) -> None:
        model = MiJiaoPredict(core=ConstantPredictor(4.0))
        evidence = (
            QueryEvidence(True, True, False, True, False, False, False, False),
        )

        prediction = model.predict(
            feature_views={"metadata": np.zeros((1, 2))},
            evidence=evidence,
        )
        manifest = model.model_manifest()

        np.testing.assert_array_equal(prediction, [[4.0, 4.0]])
        self.assertEqual(manifest[0]["name"], "metadata_ridge")
        self.assertEqual(manifest[0]["role"], "complete_core")

    def test_invalid_expert_output_is_audited_and_falls_back_to_finite_core(self) -> None:
        model = MiJiaoPredict(
            core=ConstantPredictor(4.0),
            experts=(
                ExpertSpec(
                    name="unstable_structure",
                    kind=ExpertKind.STRUCTURE,
                    predictor=NonfinitePredictor(),
                    availability=Availability.EXECUTABLE,
                    promotion=PromotionStatus.PROMOTED_SCOPED,
                    feature_view="structure",
                ),
            ),
        )

        result = model.predict_with_audit(
            feature_views={
                "metadata": np.zeros((1, 1)),
                "structure": np.ones((1, 3)),
            },
            evidence=(
                QueryEvidence(False, True, False, False, True, True, False, False),
            ),
        )

        np.testing.assert_array_equal(result.prediction, [[4.0, 4.0]])
        self.assertEqual(result.routes[0].reason, "expert_execution_failed")


if __name__ == "__main__":
    unittest.main()
