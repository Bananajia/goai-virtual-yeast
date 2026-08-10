"""Fit-only preprocessing and the full-protein output contract."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


class Log2ProteomeTransformer:
    """Take log2 only for positive values; never impute a missing value with zero."""

    def transform(self, values: np.ndarray) -> np.ndarray:
        values = np.asarray(values, dtype=np.float64)
        output = np.full_like(values, np.nan)
        valid = np.isfinite(values) & (values > 0)
        output[valid] = np.log2(values[valid])
        return output


class MissingnessFilter:
    """Select protein coordinates from fit rows only."""

    def __init__(self, max_missing_fraction: float = 0.80) -> None:
        if not 0.0 <= max_missing_fraction <= 1.0:
            raise ValueError("max_missing_fraction must be in [0, 1]")
        self.max_missing_fraction = float(max_missing_fraction)
        self.keep_mask = None
        self.missing_fraction = None

    def fit(self, fit_targets: np.ndarray) -> "MissingnessFilter":
        values = np.asarray(fit_targets, dtype=np.float64)
        if values.ndim != 2 or len(values) == 0:
            raise ValueError("fit_targets must be a non-empty two-dimensional matrix")
        self.missing_fraction = np.mean(~np.isfinite(values), axis=0)
        self.keep_mask = self.missing_fraction <= self.max_missing_fraction
        return self

    def transform(self, values: np.ndarray) -> np.ndarray:
        if self.keep_mask is None:
            raise RuntimeError("MissingnessFilter must be fit before transform")
        values = np.asarray(values, dtype=np.float64)
        if values.ndim != 2 or values.shape[1] != len(self.keep_mask):
            raise ValueError("input width does not match the fit protein coordinates")
        return values[:, self.keep_mask]

    def fit_transform(self, fit_targets: np.ndarray) -> np.ndarray:
        return self.fit(fit_targets).transform(fit_targets)


@dataclass(frozen=True)
class ProteinOutputContract:
    """Restore a modeled subset to the immutable full output width."""

    modeled_mask: np.ndarray
    fallback: np.ndarray

    @classmethod
    def from_training(
        cls, fit_targets: np.ndarray, modeled_mask: np.ndarray
    ) -> "ProteinOutputContract":
        fit_targets = np.asarray(fit_targets, dtype=np.float64)
        modeled_mask = np.asarray(modeled_mask, dtype=bool)
        if fit_targets.ndim != 2 or modeled_mask.shape != (fit_targets.shape[1],):
            raise ValueError("modeled_mask must match the full fit target width")
        counts = np.sum(np.isfinite(fit_targets), axis=0)
        sums = np.nansum(fit_targets, axis=0)
        fallback = np.divide(
            sums,
            counts,
            out=np.full(fit_targets.shape[1], np.nan, dtype=np.float64),
            where=counts > 0,
        )
        if np.any(~np.isfinite(fallback[~modeled_mask])):
            raise ValueError("every fallback protein needs at least one finite fit observation")
        return cls(modeled_mask=modeled_mask.copy(), fallback=fallback)

    @property
    def full_width(self) -> int:
        return int(len(self.modeled_mask))

    @property
    def modeled_width(self) -> int:
        return int(np.sum(self.modeled_mask))

    def restore(self, modeled_prediction: np.ndarray) -> np.ndarray:
        modeled_prediction = np.asarray(modeled_prediction, dtype=np.float64)
        if modeled_prediction.ndim != 2 or modeled_prediction.shape[1] != self.modeled_width:
            raise ValueError("modeled prediction width violates the output contract")
        restored = np.tile(self.fallback, (len(modeled_prediction), 1))
        restored[:, self.modeled_mask] = modeled_prediction
        if restored.shape[1] != self.full_width or not np.isfinite(restored).all():
            raise ValueError("full output contract produced a non-finite or wrong-width result")
        return restored
