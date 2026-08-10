"""Fit-only residual references for official OOD response evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Hashable, Sequence, Tuple

import numpy as np


_FIT_REFERENCE_SEAL = object()


class ResidualReferenceMode(str, Enum):
    EVALUATION_CENTERED = "evaluation_centered"
    FIT_FROZEN = "fit_frozen"


@dataclass(frozen=True)
class FrozenResidualReferences:
    """Context and drug means built only from an outer-fit response matrix."""

    context: np.ndarray
    drug: np.ndarray
    evaluation_replicate_ids: Tuple[Hashable, ...]
    protein_ids: Tuple[Hashable, ...]
    context_groups: Tuple[Hashable, ...]
    drug_groups: Tuple[Hashable, ...]
    _verification_seal: object = field(default=None, repr=False, compare=False)

    def require_fit_only(self) -> "FrozenResidualReferences":
        if self._verification_seal is not _FIT_REFERENCE_SEAL:
            raise ValueError("residual references must be produced from outer-fit data")
        return self


def _group_means(
    fit_fc: np.ndarray, groups: Sequence[Hashable]
) -> dict:
    positions = {}
    for position, group in enumerate(groups):
        positions.setdefault(group, []).append(position)
    means = {}
    for group, indices in positions.items():
        block = fit_fc[np.asarray(indices, dtype=np.int64)]
        counts = np.sum(np.isfinite(block), axis=0)
        sums = np.nansum(block, axis=0)
        means[group] = np.divide(
            sums,
            counts,
            out=np.full(fit_fc.shape[1], np.nan, dtype=np.float64),
            where=counts > 0,
        )
    return means


def fit_frozen_residual_references(
    fit_fc: np.ndarray,
    *,
    fit_context_groups: Sequence[Hashable],
    fit_drug_groups: Sequence[Hashable],
    evaluation_context_groups: Sequence[Hashable],
    evaluation_drug_groups: Sequence[Hashable],
    evaluation_replicate_ids: Sequence[Hashable],
    protein_ids: Sequence[Hashable],
) -> FrozenResidualReferences:
    """Freeze fit means and align them to held-out evaluation conditions."""

    fit_fc = np.asarray(fit_fc, dtype=np.float64)
    if fit_fc.ndim != 2 or len(fit_fc) == 0:
        raise ValueError("fit_fc must be a non-empty two-dimensional matrix")
    if len(fit_context_groups) != len(fit_fc) or len(fit_drug_groups) != len(fit_fc):
        raise ValueError("fit group labels must align with fit_fc rows")
    if len(evaluation_context_groups) != len(evaluation_drug_groups):
        raise ValueError("evaluation context and drug labels must align")
    if len(evaluation_replicate_ids) != len(evaluation_context_groups):
        raise ValueError("evaluation replicate IDs must align with evaluation groups")
    if len(set(evaluation_replicate_ids)) != len(evaluation_replicate_ids):
        raise ValueError("evaluation replicate IDs must be unique")
    if len(protein_ids) != fit_fc.shape[1] or len(set(protein_ids)) != len(protein_ids):
        raise ValueError("protein IDs must uniquely align with fit_fc columns")

    context_means = _group_means(fit_fc, fit_context_groups)
    drug_means = _group_means(fit_fc, fit_drug_groups)

    def align(groups: Sequence[Hashable], lookup: dict) -> np.ndarray:
        aligned = np.full((len(groups), fit_fc.shape[1]), np.nan, dtype=np.float64)
        for row, group in enumerate(groups):
            if group in lookup:
                aligned[row] = lookup[group]
        aligned.setflags(write=False)
        return aligned

    return FrozenResidualReferences(
        context=align(evaluation_context_groups, context_means),
        drug=align(evaluation_drug_groups, drug_means),
        evaluation_replicate_ids=tuple(evaluation_replicate_ids),
        protein_ids=tuple(protein_ids),
        context_groups=tuple(evaluation_context_groups),
        drug_groups=tuple(evaluation_drug_groups),
        _verification_seal=_FIT_REFERENCE_SEAL,
    )
