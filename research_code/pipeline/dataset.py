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


def align_dataset_frames(
    metadata: pd.DataFrame,
    proteome: pd.DataFrame,
    *,
    sample_id_column: str,
    scope: DataScope,
) -> DatasetBundle:
    """Align two frames by unique sample identity instead of row position."""

    if sample_id_column not in metadata.columns or sample_id_column not in proteome.columns:
        raise ValueError(f"both frames must contain {sample_id_column}")
    metadata_ids = metadata[sample_id_column]
    proteome_ids = proteome[sample_id_column]
    if metadata_ids.isna().any() or proteome_ids.isna().any():
        raise ValueError(f"{sample_id_column} values must be non-missing")
    if not metadata_ids.is_unique or not proteome_ids.is_unique:
        raise ValueError(f"{sample_id_column} values must be unique")
    if set(metadata_ids.tolist()) != set(proteome_ids.tolist()):
        raise ValueError(
            f"metadata and proteome must contain the same {sample_id_column} identities"
        )

    protein_ids = tuple(
        column for column in proteome.columns if column != sample_id_column
    )
    if not protein_ids:
        raise ValueError("proteome frame must contain at least one protein column")
    aligned = proteome.set_index(sample_id_column).loc[
        metadata_ids.tolist(), list(protein_ids)
    ]
    return DatasetBundle(
        metadata=metadata.copy(),
        endpoint=aligned.to_numpy(dtype=np.float64),
        protein_ids=protein_ids,
        scope=scope,
    )


def require_training_bundle(
    bundle: DatasetBundle,
    *,
    split_column: str = "split_final",
    train_label: str = "train",
) -> DatasetBundle:
    """Reject labeled validation/test rows before any fit-time operation."""

    if split_column not in bundle.metadata.columns:
        raise ValueError(f"training bundle must contain {split_column}")
    roles = bundle.metadata[split_column]
    if roles.isna().any() or not bool((roles == train_label).all()):
        raise ValueError(
            f"fit-time targets may contain only {split_column}={train_label}"
        )
    return bundle
