"""Reliable statistical baselines with missing-aware target fitting."""

from __future__ import annotations

import numpy as np


class ProteinMeanBaseline:
    def __init__(self) -> None:
        self.mean_ = None

    def fit(self, features: np.ndarray, targets: np.ndarray) -> "ProteinMeanBaseline":
        features = np.asarray(features)
        targets = np.asarray(targets, dtype=np.float64)
        if targets.ndim != 2 or len(features) != len(targets):
            raise ValueError("features and targets must align")
        counts = np.sum(np.isfinite(targets), axis=0)
        self.mean_ = np.divide(
            np.nansum(targets, axis=0),
            counts,
            out=np.full(targets.shape[1], np.nan),
            where=counts > 0,
        )
        if not np.isfinite(self.mean_).all():
            raise ValueError("every target protein needs a finite fit observation")
        return self

    def predict(self, features: np.ndarray) -> np.ndarray:
        if self.mean_ is None:
            raise RuntimeError("model must be fit before predict")
        return np.tile(self.mean_, (len(features), 1))


class MaskedMultiOutputRidge:
    """Independent masked Ridge fits sharing the same numeric feature matrix."""

    def __init__(self, alpha: float = 1.0) -> None:
        if alpha < 0:
            raise ValueError("alpha must be non-negative")
        self.alpha = float(alpha)
        self.coef_ = None

    @staticmethod
    def _augment(features: np.ndarray) -> np.ndarray:
        features = np.asarray(features, dtype=np.float64)
        if features.ndim != 2 or not np.isfinite(features).all():
            raise ValueError("features must be a finite two-dimensional matrix")
        return np.column_stack((np.ones(len(features)), features))

    def fit(self, features: np.ndarray, targets: np.ndarray) -> "MaskedMultiOutputRidge":
        design = self._augment(features)
        targets = np.asarray(targets, dtype=np.float64)
        if targets.ndim != 2 or len(targets) != len(design):
            raise ValueError("features and targets must align")
        coefficients = np.full((design.shape[1], targets.shape[1]), np.nan)
        penalty = np.eye(design.shape[1], dtype=np.float64) * self.alpha
        penalty[0, 0] = 0.0
        for protein in range(targets.shape[1]):
            finite = np.isfinite(targets[:, protein])
            if not np.any(finite):
                raise ValueError(f"target protein {protein} has no finite fit observations")
            local_design = design[finite]
            local_target = targets[finite, protein]
            coefficients[:, protein] = np.linalg.pinv(
                local_design.T @ local_design + penalty
            ) @ (local_design.T @ local_target)
        self.coef_ = coefficients
        return self

    def predict(self, features: np.ndarray) -> np.ndarray:
        if self.coef_ is None:
            raise RuntimeError("model must be fit before predict")
        return self._augment(features) @ self.coef_
