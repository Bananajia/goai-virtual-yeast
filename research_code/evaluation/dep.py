"""Fit-only policy and metrics for high-response/DEP protein coordinates."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Dict

import numpy as np


@dataclass(frozen=True)
class DEPPolicy:
    threshold: float
    k: int
    panel_width: int


def fit_dep_policy(
    fit_fc: np.ndarray,
    *,
    quantile: float = 0.90,
    min_k: int = 10,
    max_fraction: float = 0.25,
) -> DEPPolicy:
    """Fit threshold and K once on outer-fit truth, never on held truth."""

    values = np.asarray(fit_fc, dtype=np.float64)
    if values.ndim != 2 or not 0.0 < quantile < 1.0:
        raise ValueError("fit_fc must be two-dimensional and quantile in (0, 1)")
    finite = np.abs(values[np.isfinite(values)])
    if len(finite) == 0:
        raise ValueError("cannot fit a DEP policy without finite fold changes")
    threshold = float(np.quantile(finite, quantile))
    counts = np.sum(np.isfinite(values) & (np.abs(values) >= threshold), axis=1)
    proposed = int(np.median(counts)) if len(counts) else min_k
    upper = max(min_k, int(math.floor(values.shape[1] * max_fraction)))
    k = int(np.clip(proposed, min_k, max(1, upper)))
    k = min(k, values.shape[1])
    return DEPPolicy(threshold=threshold, k=k, panel_width=int(values.shape[1]))


def _average_precision_tie_aware(labels: np.ndarray, scores: np.ndarray) -> float:
    labels = np.asarray(labels, dtype=bool)
    scores = np.asarray(scores, dtype=np.float64)
    positives = int(np.sum(labels))
    if positives == 0:
        return math.nan
    order = np.argsort(-scores, kind="stable")
    ordered_labels = labels[order]
    ordered_scores = scores[order]
    total = 0
    true_positive = 0
    average_precision = 0.0
    start = 0
    while start < len(order):
        end = start + 1
        while end < len(order) and ordered_scores[end] == ordered_scores[start]:
            end += 1
        group_positive = int(np.sum(ordered_labels[start:end]))
        total += end - start
        true_positive += group_positive
        if group_positive:
            average_precision += (true_positive / total) * (group_positive / positives)
        start = end
    return float(average_precision)


def _macro(values: list) -> float:
    finite = np.asarray(values, dtype=np.float64)
    finite = finite[np.isfinite(finite)]
    return float(np.mean(finite)) if len(finite) else math.nan


def high_response_metrics(
    truth_fc: np.ndarray, prediction_fc: np.ndarray, policy: DEPPolicy
) -> Dict[str, float]:
    truth_fc = np.asarray(truth_fc, dtype=np.float64)
    prediction_fc = np.asarray(prediction_fc, dtype=np.float64)
    if truth_fc.ndim != 2 or truth_fc.shape != prediction_fc.shape:
        raise ValueError("truth and prediction fold changes must align")
    if truth_fc.shape[1] != policy.panel_width:
        raise ValueError("DEP policy panel width does not match scoring data")

    precision = []
    recall = []
    auprc = []
    direction = []
    errors = []
    samples_with_dep = 0
    scored_cells = 0
    for truth_row, prediction_row in zip(truth_fc, prediction_fc):
        common = np.isfinite(truth_row) & np.isfinite(prediction_row)
        truth = truth_row[common]
        prediction = prediction_row[common]
        if len(truth) == 0:
            continue
        positives = np.abs(truth) >= policy.threshold
        positive_count = int(np.sum(positives))
        if positive_count == 0:
            continue
        samples_with_dep += 1
        k = min(policy.k, len(truth))
        predicted_top = np.argsort(-np.abs(prediction), kind="stable")[:k]
        true_top = np.argsort(-np.abs(truth), kind="stable")[:k]
        signed_hits = positives[predicted_top] & (
            np.sign(prediction[predicted_top]) == np.sign(truth[predicted_top])
        )
        precision.append(float(np.sum(signed_hits) / k))
        recall.append(float(np.sum(signed_hits) / positive_count))
        auprc.append(_average_precision_tie_aware(positives, np.abs(prediction)))
        overlap = np.intersect1d(predicted_top, true_top, assume_unique=False)
        if len(overlap):
            direction.append(
                float(np.mean(np.sign(prediction[overlap]) == np.sign(truth[overlap])))
            )
        errors.extend((prediction[positives] - truth[positives]).tolist())
        scored_cells += positive_count

    error_array = np.asarray(errors, dtype=np.float64)
    return {
        "dep_threshold_abs_log2_fc": float(policy.threshold),
        "dep_k": float(policy.k),
        "samples_with_dep": float(samples_with_dep),
        "signed_precision_at_k": _macro(precision),
        "signed_recall_at_k": _macro(recall),
        "macro_auprc": _macro(auprc),
        "topk_direction_consistency": _macro(direction),
        "high_response_mae": float(np.mean(np.abs(error_array))) if len(error_array) else math.nan,
        "high_response_rmse": float(np.sqrt(np.mean(np.square(error_array)))) if len(error_array) else math.nan,
        "high_response_cells": float(scored_cells),
    }
