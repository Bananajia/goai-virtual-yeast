"""Fit-only metadata encoder shared by Ridge and neural models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Sequence, Tuple

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class MetadataField:
    name: str
    transform: str

    def __post_init__(self) -> None:
        if self.transform not in ("categorical", "identity", "log1p", "standardize"):
            raise ValueError(f"unsupported metadata transform: {self.transform}")


class MetadataEncoder:
    """One-hot and numeric transforms with explicit missing/unknown tokens."""

    def __init__(self, fields: Sequence[MetadataField]) -> None:
        self.fields = tuple(fields)
        self._categories: Dict[str, Tuple[str, ...]] = {}
        self._numeric_stats: Dict[str, Tuple[float, float]] = {}
        self.feature_names = ()

    def fit(self, frame: pd.DataFrame) -> "MetadataEncoder":
        names = []
        for field in self.fields:
            if field.name not in frame:
                raise ValueError(f"metadata field is missing: {field.name}")
            if field.transform == "categorical":
                values = frame[field.name].where(frame[field.name].notna(), "<MISSING>")
                categories = tuple(sorted({str(value) for value in values}))
                categories = tuple(
                    category for category in categories if category != "<UNKNOWN>"
                ) + ("<UNKNOWN>",)
                self._categories[field.name] = categories
                names.extend(f"{field.name}={category}" for category in categories)
                continue
            numeric = pd.to_numeric(frame[field.name], errors="coerce").to_numpy(dtype=float)
            if not np.isfinite(numeric).all():
                raise ValueError(f"numeric metadata must be finite: {field.name}")
            if field.transform == "log1p" and np.any(numeric < 0):
                raise ValueError(f"log1p metadata must be non-negative: {field.name}")
            if field.transform == "standardize":
                mean = float(np.mean(numeric))
                scale = float(np.std(numeric))
                self._numeric_stats[field.name] = (mean, scale if scale > 0 else 1.0)
                names.append(f"{field.name}=zscore")
            elif field.transform == "log1p":
                self._numeric_stats[field.name] = (0.0, 1.0)
                names.append(f"{field.name}=log1p")
            else:
                self._numeric_stats[field.name] = (0.0, 1.0)
                names.append(field.name)
        self.feature_names = tuple(names)
        return self

    def transform(self, frame: pd.DataFrame) -> np.ndarray:
        if not self.feature_names:
            raise RuntimeError("MetadataEncoder must be fit before transform")
        blocks = []
        for field in self.fields:
            if field.name not in frame:
                raise ValueError(f"metadata field is missing: {field.name}")
            if field.transform == "categorical":
                categories = self._categories[field.name]
                known = set(categories[:-1])
                values = frame[field.name].where(frame[field.name].notna(), "<MISSING>")
                normalized = [str(value) if str(value) in known else "<UNKNOWN>" for value in values]
                block = np.zeros((len(frame), len(categories)), dtype=np.float64)
                lookup = {category: index for index, category in enumerate(categories)}
                for row, value in enumerate(normalized):
                    block[row, lookup[value]] = 1.0
                blocks.append(block)
                continue
            numeric = pd.to_numeric(frame[field.name], errors="coerce").to_numpy(dtype=float)
            if not np.isfinite(numeric).all():
                raise ValueError(f"numeric metadata must be finite: {field.name}")
            if field.transform == "log1p":
                if np.any(numeric < 0):
                    raise ValueError(f"log1p metadata must be non-negative: {field.name}")
                numeric = np.log1p(numeric)
            elif field.transform == "standardize":
                mean, scale = self._numeric_stats[field.name]
                numeric = (numeric - mean) / scale
            blocks.append(numeric[:, None])
        return np.column_stack(blocks) if blocks else np.empty((len(frame), 0))

    def fit_transform(self, frame: pd.DataFrame) -> np.ndarray:
        return self.fit(frame).transform(frame)
