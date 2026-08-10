"""Predeclared multi-metric promotion decisions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class MetricCriterion:
    metric: str
    minimum_gain: float
    higher_is_better: bool = True


@dataclass(frozen=True)
class GateDecision:
    passed: bool
    gains: Mapping[str, float]
    checks: Mapping[str, bool]


class PromotionGate:
    def __init__(self, criteria: Sequence[MetricCriterion]) -> None:
        self.criteria = tuple(criteria)
        if not self.criteria:
            raise ValueError("a promotion gate needs at least one criterion")

    def evaluate(
        self,
        *,
        candidate: Mapping[str, float],
        reference: Mapping[str, float],
    ) -> GateDecision:
        gains = {}
        checks = {}
        for criterion in self.criteria:
            if criterion.metric not in candidate or criterion.metric not in reference:
                raise KeyError(f"gate metric missing: {criterion.metric}")
            raw_difference = float(candidate[criterion.metric]) - float(
                reference[criterion.metric]
            )
            gain = raw_difference if criterion.higher_is_better else -raw_difference
            gains[criterion.metric] = gain
            checks[criterion.metric] = gain >= criterion.minimum_gain
        return GateDecision(
            passed=bool(all(checks.values())), gains=gains, checks=checks
        )
