"""Fit-only residual references for official OOD response evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Hashable, Optional, Sequence, Tuple

import numpy as np


_FIT_REFERENCE_SEAL = object()
_TRAIN_PROVENANCE_SEAL = object()


class ResidualReferenceMode(str, Enum):
    EVALUATION_CENTERED = "evaluation_centered"
    FIT_FROZEN = "fit_frozen"
    NOT_APPLICABLE = "not_applicable"


@dataclass(frozen=True)
class TrainOnlyProvenance:
    """Verified identity and digest record for rows used to fit references."""

    replicate_ids: Tuple[Hashable, ...]
    source_sha256: str
    _verification_seal: object = field(default=None, repr=False, compare=False)

    def require_verified(self) -> "TrainOnlyProvenance":
        if self._verification_seal is not _TRAIN_PROVENANCE_SEAL:
            raise ValueError("residual provenance must be produced by train-only verifier")
        return self


def verify_train_only_provenance(
    *,
    replicate_ids: Sequence[Hashable],
    split_labels: Sequence[str],
    source_sha256: str,
) -> TrainOnlyProvenance:
    """Seal provenance only when every uniquely identified source row is train."""

    identities = tuple(replicate_ids)
    labels = tuple(split_labels)
    if not identities or len(identities) != len(labels):
        raise ValueError("verified train-only provenance requires aligned non-empty rows")
    if len(set(identities)) != len(identities):
        raise ValueError("verified train-only provenance requires unique replicate IDs")
    if any(label != "train" for label in labels):
        raise ValueError("verified train-only provenance cannot contain non-train rows")
    if (
        not isinstance(source_sha256, str)
        or len(source_sha256) != 64
        or any(character not in "0123456789abcdef" for character in source_sha256)
    ):
        raise ValueError("verified train-only provenance requires a lowercase SHA-256")
    return TrainOnlyProvenance(
        replicate_ids=identities,
        source_sha256=source_sha256,
        _verification_seal=_TRAIN_PROVENANCE_SEAL,
    )


@dataclass(frozen=True)
class FrozenResidualReferences:
    """Context and drug means built only from an outer-fit response matrix."""

    context: np.ndarray
    drug: np.ndarray
    evaluation_replicate_ids: Tuple[Hashable, ...]
    protein_ids: Tuple[Hashable, ...]
    context_groups: Tuple[Hashable, ...]
    drug_groups: Tuple[Hashable, ...]
    fit_provenance: Optional[TrainOnlyProvenance] = None
    _verification_seal: object = field(default=None, repr=False, compare=False)

    def require_fit_only(self) -> "FrozenResidualReferences":
        if self._verification_seal is not _FIT_REFERENCE_SEAL:
            raise ValueError("residual references must be produced from outer-fit data")
        if self.fit_provenance is None:
            raise ValueError("fit-frozen references require verified train-only provenance")
        self.fit_provenance.require_verified()
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
    fit_replicate_ids: Optional[Sequence[Hashable]] = None,
    fit_provenance: Optional[TrainOnlyProvenance] = None,
) -> FrozenResidualReferences:
    """Freeze fit means and align them to held-out evaluation conditions."""

    fit_fc = np.asarray(fit_fc, dtype=np.float64)
    if fit_fc.ndim != 2 or len(fit_fc) == 0:
        raise ValueError("fit_fc must be a non-empty two-dimensional matrix")
    if len(fit_context_groups) != len(fit_fc) or len(fit_drug_groups) != len(fit_fc):
        raise ValueError("fit group labels must align with fit_fc rows")
    if fit_provenance is None or fit_replicate_ids is None:
        raise ValueError("fit-frozen references require verified train-only provenance")
    verified_provenance = fit_provenance.require_verified()
    fit_identities = tuple(fit_replicate_ids)
    if len(fit_identities) != len(fit_fc):
        raise ValueError("fit replicate IDs must align with fit_fc rows")
    if fit_identities != verified_provenance.replicate_ids:
        raise ValueError("fit replicate IDs do not match verified train-only provenance")
    if len(evaluation_context_groups) != len(evaluation_drug_groups):
        raise ValueError("evaluation context and drug labels must align")
    if len(evaluation_replicate_ids) != len(evaluation_context_groups):
        raise ValueError("evaluation replicate IDs must align with evaluation groups")
    if len(set(evaluation_replicate_ids)) != len(evaluation_replicate_ids):
        raise ValueError("evaluation replicate IDs must be unique")
    if set(fit_identities).intersection(evaluation_replicate_ids):
        raise ValueError("fit and evaluation replicate IDs must be disjoint")
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
        fit_provenance=verified_provenance,
        _verification_seal=_FIT_REFERENCE_SEAL,
    )
