"""Fail-closed prediction.csv contract independent of private truth labels."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable, Tuple

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class SubmissionContract:
    """Validate identity, feature, scale, and finite-value submission rules."""

    sample_ids: Tuple[Hashable, ...]
    protein_ids: Tuple[str, ...]
    sample_id_column: str = "sample_ID"
    output_scale: str = "log2"

    def __post_init__(self) -> None:
        if not self.sample_ids or len(set(self.sample_ids)) != len(self.sample_ids):
            raise ValueError("submission sample IDs must be non-empty and unique")
        if not self.protein_ids or len(set(self.protein_ids)) != len(self.protein_ids):
            raise ValueError("submission protein IDs must be non-empty and unique")
        if self.output_scale != "log2":
            raise ValueError("the supported submission output scale is log2")

    def validate(
        self, prediction: pd.DataFrame, *, declared_scale: str
    ) -> pd.DataFrame:
        if declared_scale != self.output_scale:
            raise ValueError(
                f"declared scale must be {self.output_scale}, not {declared_scale}"
            )
        expected_columns = (self.sample_id_column,) + tuple(self.protein_ids)
        if tuple(prediction.columns) != expected_columns:
            raise ValueError("prediction protein columns must match the contract exactly")
        if len(prediction) != len(self.sample_ids):
            raise ValueError("prediction row count must match test metadata")
        observed_ids = tuple(prediction[self.sample_id_column].tolist())
        if observed_ids != tuple(self.sample_ids):
            raise ValueError(f"prediction {self.sample_id_column} order must match test metadata")
        if len(set(observed_ids)) != len(observed_ids):
            raise ValueError(f"prediction {self.sample_id_column} values must be unique")
        try:
            values = prediction.loc[:, list(self.protein_ids)].to_numpy(dtype=np.float64)
        except (TypeError, ValueError) as error:
            raise ValueError("protein predictions must be numeric") from error
        if not np.isfinite(values).all():
            raise ValueError("all protein predictions must be finite")
        return prediction.copy()
