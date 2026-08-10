"""Aggregate metrics for public mechanism-axis pilots."""

from __future__ import annotations

import math
from typing import Mapping, Sequence


def evaluate_axis_predictions(
    truth_rows: Sequence[Sequence[float]],
    prediction_rows: Sequence[Sequence[float]],
    *,
    causal_edges: int,
    marker_hits: int,
) -> Mapping[str, object]:
    if len(truth_rows) != len(prediction_rows) or not truth_rows:
        raise ValueError("axis truth and prediction rows must be nonempty and aligned")
    axis_count = len(truth_rows[0])
    if axis_count == 0 or any(len(row) != axis_count for row in truth_rows):
        raise ValueError("axis truth rows must have one fixed nonzero width")
    if any(len(row) != axis_count for row in prediction_rows):
        raise ValueError("axis prediction rows must match the truth width")

    truth_flat = tuple(value for row in truth_rows for value in row)
    prediction_flat = tuple(value for row in prediction_rows for value in row)
    truth_signal = [index for index, value in enumerate(truth_flat) if value != 0.0]
    predicted_signal = [index for index, value in enumerate(prediction_flat) if value != 0.0]
    overlap = set(truth_signal) & set(predicted_signal)
    signed_hits = sum(
        _sign(truth_flat[index]) == _sign(prediction_flat[index]) for index in truth_signal
    )
    macro_cosines = [
        _cosine(truth, prediction) for truth, prediction in zip(truth_rows, prediction_rows)
    ]
    top_hits = 0
    for truth, prediction in zip(truth_rows, prediction_rows):
        predicted_top = max(range(len(prediction)), key=lambda index: abs(prediction[index]))
        truth_max = max(abs(value) for value in truth)
        true_tops = {
            index
            for index, value in enumerate(truth)
            if truth_max > 0 and abs(value) == truth_max
        }
        top_hits += predicted_top in true_tops
    return {
        "metrics": {
            "macro_axis_cosine": _mean(macro_cosines),
            "pooled_axis_pearson": _pearson(truth_flat, prediction_flat),
            "signed_axis_accuracy": signed_hits / float(len(truth_signal)) if truth_signal else 0.0,
            "truth_axis_recall": len(overlap) / float(len(truth_signal)) if truth_signal else 0.0,
            "predicted_axis_precision": len(overlap) / float(len(predicted_signal)) if predicted_signal else 0.0,
            "top_axis_hit_rate": top_hits / float(len(truth_rows)),
        },
        "counts": {
            "signatures": len(truth_rows),
            "mechanism_axes": axis_count,
            "causal_edges": int(causal_edges),
            "rna_truth_axis_signals": len(truth_signal),
            "rna_marker_hits": int(marker_hits),
        },
    }


def _sign(value: float) -> int:
    return 1 if value > 0 else -1 if value < 0 else 0


def _mean(values: Sequence[float]) -> float:
    return sum(values) / float(len(values)) if values else 0.0


def _cosine(left: Sequence[float], right: Sequence[float]) -> float:
    dot = sum(left_value * right_value for left_value, right_value in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    return 0.0 if left_norm == 0.0 or right_norm == 0.0 else dot / (left_norm * right_norm)


def _pearson(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right) or not left:
        raise ValueError("Pearson inputs must be nonempty and aligned")
    left_mean = _mean(left)
    right_mean = _mean(right)
    return _cosine(
        tuple(value - left_mean for value in left),
        tuple(value - right_mean for value in right),
    )
