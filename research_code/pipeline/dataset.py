"""Validated dataset contract and loading Seam."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol, Tuple

import numpy as np
import pandas as pd


class DataScope(str, Enum):
    SYNTHETIC = "synthetic"
    PUBLIC = "public"
    PRIVATE_LOCAL = "private_local"


@dataclass(frozen=True)
class DatasetBundle:
    metadata: pd.DataFrame
    endpoint: np.ndarray
    protein_ids: Tuple[str, ...]
    scope: DataScope

    def __post_init__(self) -> None:
        endpoint = np.asarray(self.endpoint, dtype=np.float64)
        if endpoint.ndim != 2:
            raise ValueError("endpoint must be a condition-by-protein matrix")
        if len(self.metadata) != endpoint.shape[0]:
            raise ValueError("metadata rows must align with endpoint conditions")
        if len(self.protein_ids) != endpoint.shape[1]:
            raise ValueError("protein IDs must align with endpoint columns")
        if len(set(self.protein_ids)) != len(self.protein_ids):
            raise ValueError("protein IDs must be unique")
        object.__setattr__(self, "endpoint", endpoint)
        object.__setattr__(self, "metadata", self.metadata.reset_index(drop=True).copy())

    @property
    def n_conditions(self) -> int:
        return int(self.endpoint.shape[0])

    @property
    def n_proteins(self) -> int:
        return int(self.endpoint.shape[1])


class DatasetAdapter(Protocol):
    def load(self) -> DatasetBundle:
        ...


class InMemoryDatasetAdapter:
    def __init__(self, bundle: DatasetBundle) -> None:
        self._bundle = bundle

    def load(self) -> DatasetBundle:
        return self._bundle
