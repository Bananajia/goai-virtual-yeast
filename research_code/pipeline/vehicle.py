"""Explicit chemical-to-solvent mapping required for primary Raw-FC."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Hashable, Mapping, Sequence, Tuple

import numpy as np
import pandas as pd

from .controls import MeasurementMatrix, MeasurementRole


class Vehicle(str, Enum):
    DMSO = "DMSO"
    WATER = "Water"


@dataclass(frozen=True)
class OfficialVehicleMap:
    assignments: Mapping[Hashable, Vehicle]

    @classmethod
    def from_mapping(
        cls, assignments: Mapping[Hashable, str]
    ) -> "OfficialVehicleMap":
        if not assignments:
            raise ValueError("official vehicle mapping cannot be empty")
        parsed = {}
        for entity, value in assignments.items():
            try:
                parsed[entity] = Vehicle(value)
            except (TypeError, ValueError) as error:
                raise ValueError("every official vehicle must be DMSO or Water") from error
        return cls(assignments=MappingProxyType(parsed))

    def resolve(self, treated_entity: Hashable) -> Vehicle:
        try:
            return self.assignments[treated_entity]
        except KeyError as error:
            raise KeyError(f"no official vehicle mapping for {treated_entity!r}") from error


def match_official_controls(
    metadata: pd.DataFrame,
    endpoint: np.ndarray,
    *,
    protein_ids: Sequence[Hashable],
    treated_sample_ids: Sequence[Hashable],
    vehicle_map: OfficialVehicleMap,
    sample_id_column: str,
    chemical_column: str,
    match_columns: Sequence[str],
) -> Tuple[MeasurementMatrix, MeasurementMatrix]:
    """Build treated/control matrices from an explicit official vehicle map.

    Controls are selected only when vehicle and every requested metadata key
    match.  Multiple valid control rows are averaged per protein using only
    their directly measured finite values.  The output control matrix adopts
    the treated sample identities so the strict pairer can verify alignment.
    """

    values = np.asarray(endpoint, dtype=np.float64)
    required = (sample_id_column, chemical_column, *tuple(match_columns))
    missing = [column for column in required if column not in metadata.columns]
    if missing:
        raise ValueError(f"metadata is missing control-match columns: {missing}")
    if values.ndim != 2 or values.shape != (len(metadata), len(protein_ids)):
        raise ValueError("endpoint matrix must align with metadata rows and protein IDs")
    sample_ids = metadata[sample_id_column]
    if sample_ids.isna().any() or not sample_ids.is_unique:
        raise ValueError(f"{sample_id_column} must be non-missing and unique")
    if len(set(protein_ids)) != len(protein_ids):
        raise ValueError("protein IDs must be unique")
    treated_ids = tuple(treated_sample_ids)
    if not treated_ids or len(set(treated_ids)) != len(treated_ids):
        raise ValueError("treated sample IDs must be non-empty and unique")
    by_id = {sample_id: row for row, sample_id in enumerate(sample_ids.tolist())}
    absent = [sample_id for sample_id in treated_ids if sample_id not in by_id]
    if absent:
        raise ValueError("treated sample IDs must exist in metadata")

    treated_values = np.empty((len(treated_ids), values.shape[1]), dtype=np.float64)
    control_values = np.full_like(treated_values, np.nan)
    for output_row, sample_id in enumerate(treated_ids):
        source_row = by_id[sample_id]
        treated_values[output_row] = values[source_row]
        treated_metadata = metadata.iloc[source_row]
        if any(pd.isna(treated_metadata[column]) for column in match_columns):
            raise ValueError("treated control-match keys must be non-missing")
        vehicle = vehicle_map.resolve(treated_metadata[chemical_column])
        candidate = metadata[chemical_column].eq(vehicle.value)
        for column in match_columns:
            candidate &= metadata[column].eq(treated_metadata[column])
        candidate_rows = np.flatnonzero(candidate.to_numpy(dtype=bool))
        if len(candidate_rows) == 0:
            raise ValueError(
                f"no exact {vehicle.value} control for treated sample {sample_id!r}"
            )
        block = values[candidate_rows]
        counts = np.sum(np.isfinite(block), axis=0)
        sums = np.nansum(block, axis=0)
        control_values[output_row] = np.divide(
            sums,
            counts,
            out=np.full(values.shape[1], np.nan, dtype=np.float64),
            where=counts > 0,
        )

    protein_tuple = tuple(protein_ids)
    return (
        MeasurementMatrix(
            values=treated_values,
            replicate_ids=treated_ids,
            protein_ids=protein_tuple,
            role=MeasurementRole.ENDPOINT,
        ),
        MeasurementMatrix(
            values=control_values,
            replicate_ids=treated_ids,
            protein_ids=protein_tuple,
            role=MeasurementRole.MEASURED_CONTROL,
        ),
    )
