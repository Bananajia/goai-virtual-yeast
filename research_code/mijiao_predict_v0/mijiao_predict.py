"""Manual, evidence-gated routing over a complete metadata core.

This module is intentionally independent from the historical router lineages.
It is a reconstruction of the routing *contract*, not a claim that the missing
``chemical-router-v3`` or ``unified-router-final-v3-scoped`` sources were found.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Mapping, Optional, Protocol, Sequence, Tuple

import numpy as np


class Predictor(Protocol):
    def predict(self, features: Any) -> np.ndarray:
        """Return a finite two-dimensional prediction matrix."""


class ExpertKind(str, Enum):
    STRAIN = "strain"
    TIME = "time"
    CHEMICAL = "chemical"
    STRUCTURE = "structure"


class Availability(str, Enum):
    EXECUTABLE = "executable"
    EXPERIMENT_ONLY = "experiment_only"
    SOURCE_MISSING = "source_missing"
    ADAPTER_MISSING = "adapter_missing"


class PromotionStatus(str, Enum):
    PROMOTED_SCOPED = "promoted_scoped"
    REJECTED = "rejected"
    PENDING = "pending"
    NOT_EVALUATED = "not_evaluated"


class OutputMode(str, Enum):
    RESIDUAL = "residual"
    REPLACEMENT = "replacement"


@dataclass(frozen=True)
class ExpertSpec:
    name: str
    kind: ExpertKind
    predictor: Optional[Predictor]
    availability: Availability
    promotion: PromotionStatus
    feature_view: str
    output_mode: OutputMode = OutputMode.RESIDUAL

    def __post_init__(self) -> None:
        if not self.name or not self.feature_view:
            raise ValueError("expert name and feature view must be non-empty")
        if self.availability is Availability.EXECUTABLE and self.predictor is None:
            raise ValueError("an executable expert requires a predictor")

    @property
    def eligible(self) -> bool:
        return (
            self.availability is Availability.EXECUTABLE
            and self.promotion is PromotionStatus.PROMOTED_SCOPED
            and self.predictor is not None
        )


@dataclass(frozen=True)
class QueryEvidence:
    chemical_seen: bool
    strain_seen: bool
    is_time_extrapolation: bool
    base_condition_seen: bool
    has_structure: bool
    has_chemical_features: bool
    has_strain_support: bool
    has_time_support: bool


@dataclass(frozen=True)
class RouteAudit:
    row_index: int
    selected_model: str
    selected_kind: Optional[ExpertKind]
    reason: str


@dataclass(frozen=True)
class PredictionResult:
    prediction: np.ndarray
    routes: Tuple[RouteAudit, ...]


class MiJiaoPredict:
    """Select only executable, promoted experts and otherwise preserve core."""

    def __init__(
        self,
        *,
        core: Predictor,
        experts: Sequence[ExpertSpec] = (),
        core_feature_view: str = "metadata",
        core_name: str = "metadata_ridge",
    ) -> None:
        if not core_feature_view or not core_name:
            raise ValueError("core name and feature view must be non-empty")
        expert_specs = tuple(experts)
        by_kind = {expert.kind: expert for expert in expert_specs}
        if len(by_kind) != len(expert_specs):
            raise ValueError("at most one expert may be registered per kind")
        self.core = core
        self.experts = by_kind
        self.core_feature_view = core_feature_view
        self.core_name = core_name

    def predict(
        self,
        *,
        feature_views: Mapping[str, Any],
        evidence: Sequence[QueryEvidence],
    ) -> np.ndarray:
        """Return routed predictions; use ``predict_with_audit`` for decisions."""

        return self.predict_with_audit(
            feature_views=feature_views,
            evidence=evidence,
        ).prediction

    def model_manifest(self) -> Tuple[Mapping[str, str], ...]:
        """Describe configured models without implying unavailable execution."""

        records = [
            {
                "name": self.core_name,
                "kind": "core",
                "role": "complete_core",
                "availability": Availability.EXECUTABLE.value,
                "promotion": "core",
                "output_mode": OutputMode.REPLACEMENT.value,
                "feature_view": self.core_feature_view,
            }
        ]
        for kind in ExpertKind:
            expert = self.experts.get(kind)
            if expert is None:
                continue
            records.append(
                {
                    "name": expert.name,
                    "kind": expert.kind.value,
                    "role": "conditional_expert",
                    "availability": expert.availability.value,
                    "promotion": expert.promotion.value,
                    "output_mode": expert.output_mode.value,
                    "feature_view": expert.feature_view,
                }
            )
        return tuple(records)

    def predict_with_audit(
        self,
        *,
        feature_views: Mapping[str, Any],
        evidence: Sequence[QueryEvidence],
    ) -> PredictionResult:
        if self.core_feature_view not in feature_views:
            raise ValueError("metadata core feature view is missing")
        core_prediction = self._validated_prediction(
            self.core.predict(feature_views[self.core_feature_view]),
            expected_rows=len(evidence),
            expected_width=None,
            label=self.core_name,
        )
        routes = [
            self._route_one(row_index=index, evidence=row)
            for index, row in enumerate(evidence)
        ]
        prediction = core_prediction.copy()
        selected: Dict[ExpertKind, list] = {}
        for route in routes:
            if route.selected_kind is not None:
                selected.setdefault(route.selected_kind, []).append(route.row_index)
        for kind, row_indices in selected.items():
            expert = self.experts[kind]
            if expert.feature_view not in feature_views:
                for row_index in row_indices:
                    routes[row_index] = self._fallback(
                        row_index, reason="expert_feature_view_missing"
                    )
                continue
            try:
                features = self._take_rows(
                    feature_views[expert.feature_view], row_indices
                )
                expert_prediction = self._validated_prediction(
                    expert.predictor.predict(features),  # type: ignore[union-attr]
                    expected_rows=len(row_indices),
                    expected_width=prediction.shape[1],
                    label=expert.name,
                )
            except Exception:
                # An optional expert cannot make the complete core unusable.
                # The exception text is intentionally not persisted in row audits.
                for row_index in row_indices:
                    routes[row_index] = self._fallback(
                        row_index, reason="expert_execution_failed"
                    )
                continue
            if expert.output_mode is OutputMode.RESIDUAL:
                prediction[row_indices] += expert_prediction
            else:
                prediction[row_indices] = expert_prediction
        return PredictionResult(prediction=prediction, routes=tuple(routes))

    def _route_one(self, *, row_index: int, evidence: QueryEvidence) -> RouteAudit:
        if not evidence.chemical_seen and not evidence.strain_seen:
            return self._fallback(row_index, reason="double_unknown_fallback")
        if evidence.is_time_extrapolation:
            if not (
                evidence.chemical_seen
                and evidence.strain_seen
                and evidence.base_condition_seen
                and evidence.has_time_support
            ):
                return self._fallback(row_index, reason="time_support_missing")
            expert = self.experts.get(ExpertKind.TIME)
            if expert is not None and expert.eligible:
                return RouteAudit(
                    row_index=row_index,
                    selected_model=expert.name,
                    selected_kind=expert.kind,
                    reason="promoted_time_expert",
                )
            return self._fallback(row_index, reason="no_eligible_time_expert")
        if evidence.chemical_seen and not evidence.strain_seen:
            expert = self.experts.get(ExpertKind.STRAIN)
            if evidence.has_strain_support and expert is not None and expert.eligible:
                return RouteAudit(
                    row_index=row_index,
                    selected_model=expert.name,
                    selected_kind=expert.kind,
                    reason="promoted_strain_expert",
                )
            return self._fallback(row_index, reason="no_eligible_unknown_strain_expert")
        if not evidence.chemical_seen and evidence.strain_seen:
            structure = self.experts.get(ExpertKind.STRUCTURE)
            if (
                evidence.has_structure
                and structure is not None
                and structure.eligible
            ):
                return RouteAudit(
                    row_index=row_index,
                    selected_model=structure.name,
                    selected_kind=structure.kind,
                    reason="promoted_structure_expert",
                )
            chemical = self.experts.get(ExpertKind.CHEMICAL)
            if (
                evidence.has_chemical_features
                and chemical is not None
                and chemical.eligible
            ):
                return RouteAudit(
                    row_index=row_index,
                    selected_model=chemical.name,
                    selected_kind=chemical.kind,
                    reason="promoted_chemical_expert",
                )
            if not evidence.has_structure and not evidence.has_chemical_features:
                return self._fallback(row_index, reason="chemical_evidence_missing")
            return self._fallback(
                row_index, reason="no_eligible_unseen_chemical_expert"
            )
        return self._fallback(row_index, reason="core_default")

    def _fallback(self, row_index: int, *, reason: str) -> RouteAudit:
        return RouteAudit(
            row_index=row_index,
            selected_model=self.core_name,
            selected_kind=None,
            reason=reason,
        )

    @staticmethod
    def _take_rows(features: Any, row_indices: Sequence[int]) -> Any:
        if hasattr(features, "iloc"):
            return features.iloc[list(row_indices)]
        values = np.asarray(features)
        if values.ndim < 1:
            raise ValueError("expert feature view must be row-aligned")
        return values[list(row_indices)]

    @staticmethod
    def _validated_prediction(
        prediction: Any,
        *,
        expected_rows: int,
        expected_width: Optional[int],
        label: str,
    ) -> np.ndarray:
        values = np.asarray(prediction, dtype=np.float64)
        if values.ndim != 2 or values.shape[0] != expected_rows:
            raise ValueError(f"{label} prediction must be a row-aligned 2D matrix")
        if expected_width is not None and values.shape[1] != expected_width:
            raise ValueError(f"{label} prediction width must match the core")
        if not np.isfinite(values).all():
            raise ValueError(f"{label} prediction must be finite")
        return values
