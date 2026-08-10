"""Canonical, leakage-safe evaluation Interface for every experiment."""

from .metrics import (
    EvaluationInput,
    EvaluationResult,
    EvaluationSuite,
    finite_pearson,
    group_center_common,
)
from .dep import (
    DEPPolicy,
    fit_dep_policy,
    fit_fixed_threshold_dep_policy,
    high_response_metrics,
)
from .gates import GateDecision, MetricCriterion, PromotionGate
from .public_axes import evaluate_axis_predictions
from .residuals import (
    FrozenResidualReferences,
    ResidualReferenceMode,
    fit_frozen_residual_references,
)

__all__ = [
    "EvaluationInput",
    "EvaluationResult",
    "EvaluationSuite",
    "GateDecision",
    "MetricCriterion",
    "PromotionGate",
    "DEPPolicy",
    "finite_pearson",
    "fit_dep_policy",
    "fit_fixed_threshold_dep_policy",
    "evaluate_axis_predictions",
    "group_center_common",
    "high_response_metrics",
    "FrozenResidualReferences",
    "ResidualReferenceMode",
    "fit_frozen_residual_references",
]
