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
from .official_scorecard import (
    COMPLIANCE_GATE,
    OFFICIAL_MODULE_WEIGHTS_PERCENT,
    OPEN_SOURCE_CONTRIBUTION,
    MetricFamily,
    OfficialModule,
    OfficialScorecard,
    OfficialScorecardResult,
    SplitKind,
    SplitRoute,
    route_for_split,
)
from .residuals import (
    FrozenResidualReferences,
    ResidualReferenceMode,
    TrainOnlyProvenance,
    fit_frozen_residual_references,
    verify_train_only_provenance,
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
    "TrainOnlyProvenance",
    "fit_frozen_residual_references",
    "verify_train_only_provenance",
    "COMPLIANCE_GATE",
    "OFFICIAL_MODULE_WEIGHTS_PERCENT",
    "OPEN_SOURCE_CONTRIBUTION",
    "MetricFamily",
    "OfficialModule",
    "OfficialScorecard",
    "OfficialScorecardResult",
    "SplitKind",
    "SplitRoute",
    "route_for_split",
]
