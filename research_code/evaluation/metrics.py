"""One canonical implementation of endpoint and perturbation-response metrics.

The deepest invariant in this Module is that measured controls are direct inputs.
No metric is allowed to reconstruct a control from separately aggregated endpoint
and fold-change matrices.  Centered metrics also require at least two finite
conditions for every group-by-protein cell.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Dict, Mapping, Optional, Sequence, Tuple

import numpy as np

from pipeline.controls import ResponseEstimate
from .dep import DEPPolicy, high_response_metrics
from .residuals import FrozenResidualReferences, ResidualReferenceMode


EPSILON = 1e-12


@dataclass(frozen=True)
class EvaluationInput:
    truth_endpoint: np.ndarray
    prediction_endpoint: np.ndarray
    paired_response: ResponseEstimate
    context_groups: Sequence[object]
    drug_groups: Sequence[object]
    residual_reference_mode: ResidualReferenceMode = ResidualReferenceMode.FIT_FROZEN
    frozen_residual_references: Optional[FrozenResidualReferences] = None
    dep_policy: Optional[DEPPolicy] = None


@dataclass(frozen=True)
class EvaluationResult:
    metrics: Mapping[str, float]
    counts: Mapping[str, int]
    contract: Mapping[str, bool]


def finite_pearson(truth: np.ndarray, prediction: np.ndarray) -> float:
    truth = np.asarray(truth, dtype=np.float64)
    prediction = np.asarray(prediction, dtype=np.float64)
    valid = np.isfinite(truth) & np.isfinite(prediction)
    if int(valid.sum()) < 2:
        return math.nan
    left = truth[valid] - float(np.mean(truth[valid]))
    right = prediction[valid] - float(np.mean(prediction[valid]))
    left_energy = float(np.sum(left * left))
    right_energy = float(np.sum(right * right))
    if left_energy <= EPSILON:
        return math.nan
    if right_energy <= EPSILON:
        return 0.0
    denominator = float(np.sqrt(left_energy * right_energy))
    return float(np.sum(left * right) / denominator)


def _macro_row_pearson(truth: np.ndarray, prediction: np.ndarray) -> float:
    values = np.asarray(
        [finite_pearson(row_truth, row_prediction) for row_truth, row_prediction in zip(truth, prediction)],
        dtype=np.float64,
    )
    finite = values[np.isfinite(values)]
    return float(np.mean(finite)) if len(finite) else math.nan


def _rmse(truth: np.ndarray, prediction: np.ndarray) -> float:
    valid = np.isfinite(truth) & np.isfinite(prediction)
    if not np.any(valid):
        return math.nan
    return float(np.sqrt(np.mean(np.square(prediction[valid] - truth[valid]))))


def _pooled_r2(truth: np.ndarray, prediction: np.ndarray) -> float:
    valid = np.isfinite(truth) & np.isfinite(prediction)
    if int(valid.sum()) < 2:
        return math.nan
    observed = truth[valid]
    predicted = prediction[valid]
    total = float(np.sum(np.square(observed - np.mean(observed))))
    if total <= EPSILON:
        return math.nan
    residual = float(np.sum(np.square(observed - predicted)))
    return 1.0 - residual / total


def _mean_protein_r2(truth: np.ndarray, prediction: np.ndarray) -> float:
    scores = []
    for protein in range(truth.shape[1]):
        score = _pooled_r2(truth[:, protein], prediction[:, protein])
        if np.isfinite(score):
            scores.append(score)
    return float(np.mean(scores)) if scores else math.nan


def _macro_sample_r2(truth: np.ndarray, prediction: np.ndarray) -> float:
    scores = [
        _pooled_r2(row_truth, row_prediction)
        for row_truth, row_prediction in zip(truth, prediction)
    ]
    finite = np.asarray(scores, dtype=np.float64)
    finite = finite[np.isfinite(finite)]
    return float(np.mean(finite)) if len(finite) else math.nan


def _macro_protein_pearson(truth: np.ndarray, prediction: np.ndarray) -> float:
    scores = [
        finite_pearson(truth[:, protein], prediction[:, protein])
        for protein in range(truth.shape[1])
    ]
    finite = np.asarray(scores, dtype=np.float64)
    finite = finite[np.isfinite(finite)]
    return float(np.mean(finite)) if len(finite) else math.nan


def _median_protein_r2(truth: np.ndarray, prediction: np.ndarray) -> float:
    scores = [
        _pooled_r2(truth[:, protein], prediction[:, protein])
        for protein in range(truth.shape[1])
    ]
    finite = np.asarray(scores, dtype=np.float64)
    finite = finite[np.isfinite(finite)]
    return float(np.median(finite)) if len(finite) else math.nan


def group_center_common(
    truth: np.ndarray,
    prediction: np.ndarray,
    groups: Sequence[object],
) -> Tuple[np.ndarray, np.ndarray]:
    """Center aligned arrays using a common mask and count >= 2 per cell."""

    truth = np.asarray(truth, dtype=np.float64)
    prediction = np.asarray(prediction, dtype=np.float64)
    if truth.ndim != 2 or truth.shape != prediction.shape:
        raise ValueError("truth and prediction must be aligned two-dimensional arrays")
    if len(groups) != len(truth):
        raise ValueError("group labels must align with condition rows")

    common = np.isfinite(truth) & np.isfinite(prediction)
    common_truth = np.where(common, truth, np.nan)
    common_prediction = np.where(common, prediction, np.nan)
    centered_truth = np.full_like(common_truth, np.nan)
    centered_prediction = np.full_like(common_prediction, np.nan)

    positions_by_group: Dict[object, list] = {}
    for position, group in enumerate(groups):
        positions_by_group.setdefault(group, []).append(position)

    for positions in positions_by_group.values():
        index = np.asarray(positions, dtype=np.int64)
        truth_block = common_truth[index]
        prediction_block = common_prediction[index]
        counts = np.sum(np.isfinite(truth_block), axis=0)
        usable = counts >= 2
        if not np.any(usable):
            continue
        truth_means = np.nanmean(truth_block[:, usable], axis=0)
        prediction_means = np.nanmean(prediction_block[:, usable], axis=0)
        centered_truth[np.ix_(index, usable)] = truth_block[:, usable] - truth_means
        centered_prediction[np.ix_(index, usable)] = (
            prediction_block[:, usable] - prediction_means
        )
    return centered_truth, centered_prediction


def _family_metrics(
    prefix: str, truth: np.ndarray, prediction: np.ndarray
) -> Tuple[Dict[str, float], Dict[str, int]]:
    common = np.isfinite(truth) & np.isfinite(prediction)
    return (
        {
            f"{prefix}_pcc": _macro_row_pearson(truth, prediction),
            f"{prefix}_pooled_pcc": finite_pearson(truth.ravel(), prediction.ravel()),
            f"{prefix}_pooled_r2": _pooled_r2(truth, prediction),
            f"{prefix}_macro_sample_r2": _macro_sample_r2(truth, prediction),
            f"{prefix}_macro_protein_pcc": _macro_protein_pearson(truth, prediction),
            f"{prefix}_median_protein_r2": _median_protein_r2(truth, prediction),
            f"{prefix}_mean_protein_r2": _mean_protein_r2(truth, prediction),
            f"{prefix}_rmse": _rmse(truth, prediction),
        },
        {f"{prefix}_cells": int(common.sum())},
    )


class EvaluationSuite:
    """Deep evaluation Module shared by all experiment Implementations."""

    schema_version = "1.1"

    def evaluate(self, inputs: EvaluationInput) -> EvaluationResult:
        truth = np.asarray(inputs.truth_endpoint, dtype=np.float64)
        prediction = np.asarray(inputs.prediction_endpoint, dtype=np.float64)
        if not isinstance(inputs.paired_response, ResponseEstimate):
            raise TypeError(
                "evaluation requires a verified paired measured-control result, "
                "not a bare or reconstructed control array"
            )
        paired_response = inputs.paired_response.require_verified_primary_pairing()
        paired_endpoint = np.asarray(
            paired_response.endpoint_reference, dtype=np.float64
        )
        control = np.asarray(paired_response.control_reference, dtype=np.float64)
        paired_valid = np.asarray(paired_response.valid_mask, dtype=bool)
        if truth.ndim != 2 or truth.shape != prediction.shape or truth.shape != control.shape:
            raise ValueError("truth, prediction, and direct measured control must align")
        if paired_endpoint.shape != truth.shape or paired_valid.shape != truth.shape:
            raise ValueError("paired endpoint reference and mask must align with truth")
        same_finite = np.array_equal(np.isfinite(truth), np.isfinite(paired_endpoint))
        finite = np.isfinite(truth) & np.isfinite(paired_endpoint)
        same_values = np.allclose(truth[finite], paired_endpoint[finite])
        if not same_finite or not same_values:
            raise ValueError(
                "paired endpoint reference must be the same truth endpoint matrix"
            )
        expected_pair_mask = np.isfinite(paired_endpoint) & np.isfinite(control)
        if not np.array_equal(paired_valid, expected_pair_mask):
            raise ValueError("paired measured-control mask failed integrity validation")
        if len(inputs.context_groups) != len(truth) or len(inputs.drug_groups) != len(truth):
            raise ValueError("context and drug labels must align with condition rows")

        missing_prediction = np.isfinite(truth) & ~np.isfinite(prediction)
        if np.any(missing_prediction):
            raise ValueError(
                "prediction must be finite at every finite truth endpoint cell; "
                "a model may not use NaN to opt out of difficult coordinates"
            )

        metrics: Dict[str, float] = {}
        counts: Dict[str, int] = {
            "conditions": int(truth.shape[0]),
            "proteins": int(truth.shape[1]),
        }

        endpoint_common = np.isfinite(truth) & np.isfinite(prediction)
        endpoint_truth = np.where(endpoint_common, truth, np.nan)
        endpoint_prediction = np.where(endpoint_common, prediction, np.nan)
        family_metrics, family_counts = _family_metrics(
            "endpoint", endpoint_truth, endpoint_prediction
        )
        metrics.update(family_metrics)
        counts.update(family_counts)

        response_common = endpoint_common & paired_valid
        paired_truth = np.where(response_common, truth, np.nan)
        paired_prediction = np.where(response_common, prediction, np.nan)
        family_metrics, family_counts = _family_metrics(
            "endpoint_paired", paired_truth, paired_prediction
        )
        metrics.update(family_metrics)
        counts.update(family_counts)
        truth_fc = np.where(response_common, paired_response.values, np.nan)
        prediction_fc = np.where(response_common, prediction - control, np.nan)
        family_metrics, family_counts = _family_metrics(
            "raw_fc", truth_fc, prediction_fc
        )
        metrics.update(family_metrics)
        counts.update(family_counts)
        if inputs.dep_policy is not None:
            metrics.update(high_response_metrics(truth_fc, prediction_fc, inputs.dep_policy))
        truth_rms = np.sqrt(np.nanmean(np.square(truth_fc), axis=1))
        prediction_rms = np.sqrt(np.nanmean(np.square(prediction_fc), axis=1))
        amplitude = np.abs(np.log1p(prediction_rms) - np.log1p(truth_rms))
        metrics["amplitude_log_error"] = float(np.nanmedian(amplitude))

        try:
            residual_mode = ResidualReferenceMode(inputs.residual_reference_mode)
        except (TypeError, ValueError) as error:
            raise ValueError("unknown residual reference mode") from error
        if residual_mode == ResidualReferenceMode.FIT_FROZEN:
            if inputs.frozen_residual_references is None:
                raise ValueError("fit-frozen residual scoring requires outer-fit references")
            references = inputs.frozen_residual_references.require_fit_only()
            if references.context.shape != truth_fc.shape or references.drug.shape != truth_fc.shape:
                raise ValueError("fit-frozen residual references must align with evaluation responses")
            if references.evaluation_replicate_ids != tuple(paired_response.replicate_ids):
                raise ValueError("fit-frozen replicate identities or row order do not match evaluation")
            if references.protein_ids != tuple(paired_response.protein_ids):
                raise ValueError("fit-frozen protein identities or column order do not match evaluation")
            if references.context_groups != tuple(inputs.context_groups):
                raise ValueError("fit-frozen context groups do not match evaluation")
            if references.drug_groups != tuple(inputs.drug_groups):
                raise ValueError("fit-frozen drug groups do not match evaluation")
            residual_families = (
                ("context_residual", truth_fc - references.context, prediction_fc - references.context),
                ("drug_residual", truth_fc - references.drug, prediction_fc - references.drug),
            )
        elif residual_mode == ResidualReferenceMode.EVALUATION_CENTERED:
            context_truth, context_prediction = group_center_common(
                truth_fc, prediction_fc, inputs.context_groups
            )
            drug_truth, drug_prediction = group_center_common(
                truth_fc, prediction_fc, inputs.drug_groups
            )
            residual_families = (
                ("context_residual", context_truth, context_prediction),
                ("drug_residual", drug_truth, drug_prediction),
            )
        else:
            if inputs.frozen_residual_references is not None:
                raise ValueError(
                    "not-applicable residual mode cannot carry frozen references"
                )
            residual_families = ()

        for name, centered_truth, centered_prediction in residual_families:
            family_metrics, family_counts = _family_metrics(
                name, centered_truth, centered_prediction
            )
            metrics.update(family_metrics)
            counts.update(family_counts)

        individuality_truth, individuality_prediction = group_center_common(
            truth_fc, prediction_fc, ("all",) * len(truth_fc)
        )
        family_metrics, family_counts = _family_metrics(
            "individuality", individuality_truth, individuality_prediction
        )
        metrics.update(family_metrics)
        counts.update(family_counts)
        valid = np.isfinite(individuality_truth) & np.isfinite(individuality_prediction)
        truth_energy = float(np.sum(np.square(individuality_truth[valid])))
        prediction_energy = float(np.sum(np.square(individuality_prediction[valid])))
        metrics["condition_variance_ratio"] = (
            prediction_energy / truth_energy if truth_energy > EPSILON else math.nan
        )

        return EvaluationResult(
            metrics=metrics,
            counts=counts,
            contract={
                "measured_control_passed_directly": True,
                "measured_control_verified_by_pairer": True,
                "response_common_mask": True,
                "group_protein_minimum_two": True,
                "residual_references_fit_only": residual_mode == ResidualReferenceMode.FIT_FROZEN,
                "residual_references_evaluation_centered": residual_mode == ResidualReferenceMode.EVALUATION_CENTERED,
                "residual_references_not_applicable": residual_mode == ResidualReferenceMode.NOT_APPLICABLE,
                "endpoint_scope_is_all_common_cells": True,
                "prediction_finite_where_truth_finite": True,
                "response_scope_is_direct_control_paired": True,
                "dep_policy_supplied": inputs.dep_policy is not None,
            },
        )
