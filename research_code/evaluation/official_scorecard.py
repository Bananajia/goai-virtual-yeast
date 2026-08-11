"""Official-facing scorecard contract for the four declared OOD routes.

This module exposes module weights, split routing, and module-scoped metrics.
It deliberately does not combine metrics or synthesize an "official total":
the organizer material does not publish the within-module aggregation needed
to do that faithfully.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping, Optional, Tuple

import numpy as np

from .metrics import EvaluationInput, EvaluationSuite
from .residuals import ResidualReferenceMode


class SplitKind(str, Enum):
    TEST_CHEM_ONLY = "test_chem_only"
    TEST_STRAIN_ONLY = "test_strain_only"
    TEST_BOTH = "test_both"
    TEST_TIME = "test_time"


class OfficialModule(str, Enum):
    ABSOLUTE_FIDELITY = "absolute_fidelity"
    MATCHED_CONTROL_RAW_FC = "matched_control_raw_fc"
    CONTEXT_MEAN_RESIDUAL = "context_mean_residual"
    DRUG_MEAN_RESIDUAL = "drug_mean_residual"
    DOUBLE_UNKNOWN_OR_TIME = "double_unknown_or_time"
    HIGH_RESPONSE_DEP = "high_response_dep"


class MetricFamily(str, Enum):
    ABSOLUTE_FIDELITY = "absolute_fidelity"
    MATCHED_CONTROL_RAW_FC = "matched_control_raw_fc"
    CONTEXT_MEAN_RESIDUAL = "context_mean_residual"
    DRUG_MEAN_RESIDUAL = "drug_mean_residual"
    DOUBLE_UNKNOWN_OR_TIME = "double_unknown_or_time"
    HIGH_RESPONSE_DEP = "high_response_dep"


OFFICIAL_MODULE_WEIGHTS_PERCENT: Mapping[OfficialModule, int] = MappingProxyType(
    {
        OfficialModule.ABSOLUTE_FIDELITY: 20,
        OfficialModule.MATCHED_CONTROL_RAW_FC: 25,
        OfficialModule.CONTEXT_MEAN_RESIDUAL: 20,
        OfficialModule.DRUG_MEAN_RESIDUAL: 20,
        OfficialModule.DOUBLE_UNKNOWN_OR_TIME: 10,
        OfficialModule.HIGH_RESPONSE_DEP: 5,
    }
)


@dataclass(frozen=True)
class SeparateReviewDimension:
    name: str
    weight_percent: Optional[int]
    is_separate_gate: bool = False
    is_separate_dimension: bool = False
    included_in_synthesized_total: bool = False


COMPLIANCE_GATE = SeparateReviewDimension(
    name="reproducibility_and_compliance",
    weight_percent=None,
    is_separate_gate=True,
)

OPEN_SOURCE_CONTRIBUTION = SeparateReviewDimension(
    name="open_source_contribution",
    weight_percent=5,
    is_separate_dimension=True,
)


@dataclass(frozen=True)
class SplitRoute:
    split: SplitKind
    required_metric_families: Tuple[MetricFamily, ...]


_COMMON = (
    MetricFamily.ABSOLUTE_FIDELITY,
    MetricFamily.MATCHED_CONTROL_RAW_FC,
)
_ROUTES: Mapping[SplitKind, SplitRoute] = MappingProxyType(
    {
        SplitKind.TEST_CHEM_ONLY: SplitRoute(
            split=SplitKind.TEST_CHEM_ONLY,
            required_metric_families=(
                *_COMMON,
                MetricFamily.CONTEXT_MEAN_RESIDUAL,
                MetricFamily.HIGH_RESPONSE_DEP,
            ),
        ),
        SplitKind.TEST_STRAIN_ONLY: SplitRoute(
            split=SplitKind.TEST_STRAIN_ONLY,
            required_metric_families=(
                *_COMMON,
                MetricFamily.DRUG_MEAN_RESIDUAL,
                MetricFamily.HIGH_RESPONSE_DEP,
            ),
        ),
        SplitKind.TEST_BOTH: SplitRoute(
            split=SplitKind.TEST_BOTH,
            required_metric_families=(
                *_COMMON,
                MetricFamily.DOUBLE_UNKNOWN_OR_TIME,
                MetricFamily.HIGH_RESPONSE_DEP,
            ),
        ),
        SplitKind.TEST_TIME: SplitRoute(
            split=SplitKind.TEST_TIME,
            required_metric_families=(
                *_COMMON,
                MetricFamily.DOUBLE_UNKNOWN_OR_TIME,
                MetricFamily.HIGH_RESPONSE_DEP,
            ),
        ),
    }
)


def route_for_split(split: SplitKind) -> SplitRoute:
    try:
        selected = SplitKind(split)
    except (TypeError, ValueError) as error:
        raise ValueError("unknown official OOD split") from error
    return _ROUTES[selected]


_DEP_METRICS = (
    "signed_precision_at_k",
    "signed_recall_at_k",
    "signed_f1_at_k",
    "macro_auprc",
    "high_response_pcc",
    "topk_direction_consistency",
)
_ABSOLUTE_FIDELITY_METRICS = (
    "endpoint_pcc",
    "endpoint_macro_sample_r2",
    "endpoint_macro_protein_pcc",
    "endpoint_mean_protein_r2",
)
_RAW_FC_METRICS = ("raw_fc_pcc",)
_CONTEXT_RESIDUAL_METRICS = ("context_residual_pcc",)
_DRUG_RESIDUAL_METRICS = ("drug_residual_pcc",)


@dataclass(frozen=True)
class OfficialScorecardResult:
    split: SplitKind
    module_metrics: Mapping[MetricFamily, Mapping[str, float]]
    coverage_denominators: Mapping[str, int]
    evaluation_contract: Mapping[str, bool]


def _named_metrics(
    metrics: Mapping[str, float], names: Tuple[str, ...]
) -> Mapping[str, float]:
    return MappingProxyType({name: metrics[name] for name in names})


def _defined_pcc_axis_count(truth: np.ndarray, valid: np.ndarray, axis: int) -> int:
    oriented_truth = truth if axis == 1 else truth.T
    oriented_valid = valid if axis == 1 else valid.T
    defined = 0
    for values, mask in zip(oriented_truth, oriented_valid):
        observed = values[mask]
        if len(observed) < 2:
            continue
        centered = observed - float(np.mean(observed))
        if float(np.sum(centered * centered)) > 1e-12:
            defined += 1
    return defined


class OfficialScorecard:
    """Route canonical metrics without inferring an unpublished total score."""

    schema_version = "1.0"

    def evaluate(
        self, *, split: SplitKind, inputs: EvaluationInput
    ) -> OfficialScorecardResult:
        route = route_for_split(split)
        if inputs.dep_policy is None:
            raise ValueError("official scorecard requires a DEP policy on every split")
        if (
            float(inputs.dep_policy.threshold) != 1.0
            or not inputs.dep_policy.strict_greater
        ):
            raise ValueError("official DEP policy must use abs(raw FC) > 1")
        if route.split in (
            SplitKind.TEST_CHEM_ONLY,
            SplitKind.TEST_STRAIN_ONLY,
        ):
            try:
                residual_mode = ResidualReferenceMode(inputs.residual_reference_mode)
            except (TypeError, ValueError) as error:
                raise ValueError("official residual route requires fit-frozen references") from error
            if residual_mode != ResidualReferenceMode.FIT_FROZEN:
                raise ValueError("official residual route requires fit-frozen references")
            if inputs.frozen_residual_references is None:
                raise ValueError("official residual route requires fit-frozen references")
        else:
            try:
                residual_mode = ResidualReferenceMode(inputs.residual_reference_mode)
            except (TypeError, ValueError) as error:
                raise ValueError(
                    "test_both/test_time require residual mode not_applicable"
                ) from error
            if residual_mode != ResidualReferenceMode.NOT_APPLICABLE:
                raise ValueError("test_both/test_time require residual mode not_applicable")
            if inputs.frozen_residual_references is not None:
                raise ValueError("test_both/test_time cannot carry residual references")

        evaluated = EvaluationSuite().evaluate(inputs)
        absolute = _named_metrics(evaluated.metrics, _ABSOLUTE_FIDELITY_METRICS)
        raw_fc = _named_metrics(evaluated.metrics, _RAW_FC_METRICS)
        metric_blocks = {
            MetricFamily.ABSOLUTE_FIDELITY: absolute,
            MetricFamily.MATCHED_CONTROL_RAW_FC: raw_fc,
            MetricFamily.DOUBLE_UNKNOWN_OR_TIME: MappingProxyType(
                {**dict(absolute), **dict(raw_fc)}
            ),
            MetricFamily.HIGH_RESPONSE_DEP: MappingProxyType(
                {
                    name: evaluated.metrics[name]
                    for name in _DEP_METRICS
                }
            ),
        }
        if MetricFamily.CONTEXT_MEAN_RESIDUAL in route.required_metric_families:
            metric_blocks[MetricFamily.CONTEXT_MEAN_RESIDUAL] = _named_metrics(
                evaluated.metrics, _CONTEXT_RESIDUAL_METRICS
            )
        if MetricFamily.DRUG_MEAN_RESIDUAL in route.required_metric_families:
            metric_blocks[MetricFamily.DRUG_MEAN_RESIDUAL] = _named_metrics(
                evaluated.metrics, _DRUG_RESIDUAL_METRICS
            )
        routed = MappingProxyType(
            {
                family: metric_blocks[family]
                for family in route.required_metric_families
            }
        )

        truth = np.asarray(inputs.truth_endpoint, dtype=np.float64)
        prediction = np.asarray(inputs.prediction_endpoint, dtype=np.float64)
        paired_valid = np.asarray(inputs.paired_response.valid_mask, dtype=bool)
        truth_fc = np.asarray(inputs.paired_response.values, dtype=np.float64)
        truth_valid = np.isfinite(truth)
        endpoint_common = truth_valid & np.isfinite(prediction)
        dep_truth_positive = (
            paired_valid
            & np.isfinite(truth_fc)
            & (np.abs(truth_fc) > float(inputs.dep_policy.threshold))
        )
        paired_truth_valid = truth_valid & paired_valid
        if route.split == SplitKind.TEST_CHEM_ONLY:
            residual_reference = inputs.frozen_residual_references.context
        elif route.split == SplitKind.TEST_STRAIN_ONLY:
            residual_reference = inputs.frozen_residual_references.drug
        else:
            residual_reference = None
        coverage_values = {
            "endpoint_total_cells": int(truth.size),
            "endpoint_conditions_total": int(truth.shape[0]),
            "endpoint_proteins_total": int(truth.shape[1]),
            "endpoint_truth_valid_cells": int(np.sum(truth_valid)),
            "prediction_finite_on_truth_cells": int(np.sum(endpoint_common)),
            "endpoint_conditions_with_defined_pcc": _defined_pcc_axis_count(
                truth, endpoint_common, axis=1
            ),
            "endpoint_proteins_with_defined_pcc": _defined_pcc_axis_count(
                truth, endpoint_common, axis=0
            ),
            "direct_control_paired_cells": int(np.sum(paired_truth_valid)),
            "residual_reference_required_cells": (
                int(np.sum(paired_truth_valid)) if residual_reference is not None else 0
            ),
            "residual_reference_available_cells": (
                int(np.sum(paired_truth_valid & np.isfinite(residual_reference)))
                if residual_reference is not None
                else 0
            ),
            "dep_truth_positive_cells": int(np.sum(dep_truth_positive)),
            "samples_with_truth_dep": int(np.sum(np.any(dep_truth_positive, axis=1))),
        }
        coverage = MappingProxyType(coverage_values)
        return OfficialScorecardResult(
            split=route.split,
            module_metrics=routed,
            coverage_denominators=coverage,
            evaluation_contract=evaluated.contract,
        )
