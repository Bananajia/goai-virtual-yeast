"""Explicit whole-entity OOD split contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class OODSplit:
    fit_indices: np.ndarray
    evaluate_indices: np.ndarray
    identity_overlap: int
    held_out_entities: tuple


class GroupedOODSplitter:
    def hold_out(self, entities: Sequence[object], held_out: Sequence[object]) -> OODSplit:
        entity_array = np.asarray(entities, dtype=object)
        held_out_entities = tuple(held_out)
        if entity_array.ndim != 1 or len(entity_array) == 0:
            raise ValueError("entities must be a non-empty one-dimensional sequence")
        if not held_out_entities:
            raise ValueError("at least one held-out entity is required")
        evaluate = np.isin(entity_array, np.asarray(held_out_entities, dtype=object))
        if not np.any(evaluate) or np.all(evaluate):
            raise ValueError("split must contain both fit and evaluation rows")
        fit_indices = np.flatnonzero(~evaluate)
        evaluate_indices = np.flatnonzero(evaluate)
        fit_identity = set(entity_array[fit_indices].tolist())
        evaluate_identity = set(entity_array[evaluate_indices].tolist())
        overlap = len(fit_identity.intersection(evaluate_identity))
        if overlap:
            raise AssertionError("whole-entity OOD split contains identity leakage")
        return OODSplit(
            fit_indices=fit_indices,
            evaluate_indices=evaluate_indices,
            identity_overlap=overlap,
            held_out_entities=held_out_entities,
        )
