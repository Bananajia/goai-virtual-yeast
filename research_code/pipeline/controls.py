"""Strict response construction from directly measured controls.

This Module deliberately accepts endpoint and measured-control matrices only.
Fold-change values are outputs, never inputs from which a control is rebuilt.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Hashable, Sequence, Tuple

import numpy as np


_PAIRING_SEAL = object()


class ControlPairingError(ValueError):
    """Base class for invalid measured-control pairing requests."""


class DuplicateMeasurementKeyError(ControlPairingError):
    """A replicate or protein key occurs more than once in a matrix."""


class MisorderedMeasurementError(ControlPairingError):
    """Two matrices contain the same keys but in a different order."""


class UnmatchedMeasurementError(ControlPairingError):
    """An endpoint key has no measured-control match (or conversely)."""


class MeasurementRoleError(ControlPairingError):
    """An input is not the direct measurement role required by the Interface."""


class EstimandMismatchError(ControlPairingError):
    """A sensitivity result was requested under a different estimand label."""


class NoCommonMeasurementsError(ControlPairingError):
    """No endpoint can be compared with an observed control reference."""


class MeasurementShapeError(ControlPairingError):
    """A matrix shape disagrees with its replicate or protein keys."""


class UnknownControlEstimandError(ControlPairingError):
    """The requested response is neither a supported estimand nor sensitivity."""


class MeasurementRole(str, Enum):
    ENDPOINT = "endpoint"
    MEASURED_CONTROL = "measured_control"


class ControlEstimand(str, Enum):
    """Two scientifically distinct response definitions.

    ``PAIRED`` is the primary estimand and requires exact replicate identity.
    ``INDEPENDENT_ALL_CONTROL_SENSITIVITY`` subtracts each protein's mean over
    every control replicate and is deliberately marked as sensitivity-only.
    """

    PAIRED = "paired_measured_control"
    INDEPENDENT_ALL_CONTROL_SENSITIVITY = "independent_all_control_sensitivity"


class AnalysisRole(str, Enum):
    PRIMARY = "primary_estimand"
    SENSITIVITY = "sensitivity_analysis"


@dataclass(frozen=True)
class MeasurementMatrix:
    """A keyed endpoint or direct-control matrix (replicate by protein)."""

    values: np.ndarray
    replicate_ids: Sequence[Hashable]
    protein_ids: Sequence[Hashable]
    role: MeasurementRole


@dataclass(frozen=True)
class ResponseEstimate:
    """A labeled response matrix that downstream evaluation can verify."""

    values: np.ndarray
    valid_mask: np.ndarray
    endpoint_reference: np.ndarray
    control_reference: np.ndarray
    estimand: ControlEstimand
    analysis_role: AnalysisRole
    replicate_ids: Tuple[Hashable, ...]
    protein_ids: Tuple[Hashable, ...]
    _verification_seal: object = field(default=None, repr=False, compare=False)

    def require_estimand(self, expected: ControlEstimand) -> "ResponseEstimate":
        if self.estimand != expected:
            raise EstimandMismatchError(
                "response uses %s, not requested %s"
                % (self.estimand.value, expected.value)
            )
        return self

    def require_verified_primary_pairing(self) -> "ResponseEstimate":
        if self._verification_seal is not _PAIRING_SEAL:
            raise MeasurementRoleError(
                "evaluation requires a verified paired measured-control result"
            )
        if self.estimand != ControlEstimand.PAIRED:
            raise EstimandMismatchError(
                "primary response evaluation requires paired measured control"
            )
        if self.analysis_role != AnalysisRole.PRIMARY:
            raise MeasurementRoleError(
                "sensitivity controls cannot be labeled as the primary estimand"
            )
        return self


class MeasuredControlPairer:
    """Construct a response under one explicitly selected control estimand."""

    def estimate(
        self,
        endpoint: MeasurementMatrix,
        measured_control: MeasurementMatrix,
        *,
        estimand: ControlEstimand,
    ) -> ResponseEstimate:
        """Return endpoint-minus-control without ever reconstructing control.

        Paired responses use a single finite common mask for every exact
        replicate-by-protein cell.  The independent sensitivity uses the
        finite all-control protein mean and retains the endpoint row layout.
        """
        try:
            selected_estimand = ControlEstimand(estimand)
        except (TypeError, ValueError) as error:
            raise UnknownControlEstimandError(
                "select paired_measured_control or "
                "independent_all_control_sensitivity explicitly"
            ) from error
        if endpoint.role != MeasurementRole.ENDPOINT:
            raise MeasurementRoleError("first matrix must contain endpoint measurements")
        if measured_control.role != MeasurementRole.MEASURED_CONTROL:
            raise MeasurementRoleError(
                "second matrix must contain a directly measured control; "
                "endpoint-minus-fold-change reconstruction is forbidden"
            )
        self._validate_shape(endpoint)
        self._validate_shape(measured_control)
        self._reject_duplicate_keys(endpoint)
        self._reject_duplicate_keys(measured_control)
        self._require_aligned_keys(
            endpoint.protein_ids, measured_control.protein_ids, "protein"
        )
        if selected_estimand == ControlEstimand.PAIRED:
            self._require_aligned_keys(
                endpoint.replicate_ids,
                measured_control.replicate_ids,
                "replicate",
            )
        endpoint_values = np.asarray(endpoint.values, dtype=np.float64)
        control_values = np.asarray(measured_control.values, dtype=np.float64)
        if selected_estimand == ControlEstimand.PAIRED:
            control_reference = control_values
            analysis_role = AnalysisRole.PRIMARY
        else:
            control_counts = np.sum(np.isfinite(control_values), axis=0)
            control_sums = np.nansum(control_values, axis=0)
            control_means = np.full(control_values.shape[1], np.nan, dtype=np.float64)
            observed = control_counts > 0
            control_means[observed] = control_sums[observed] / control_counts[observed]
            control_reference = np.broadcast_to(control_means, endpoint_values.shape)
            analysis_role = AnalysisRole.SENSITIVITY
        common = np.isfinite(endpoint_values) & np.isfinite(control_reference)
        if not np.any(common):
            raise NoCommonMeasurementsError(
                "no jointly observed endpoint and control measurements"
            )
        response = np.where(common, endpoint_values - control_reference, np.nan)
        endpoint_snapshot = self._readonly_copy(endpoint_values)
        control_snapshot = self._readonly_copy(control_reference)
        response_snapshot = self._readonly_copy(response)
        common_snapshot = self._readonly_copy(common)
        return ResponseEstimate(
            values=response_snapshot,
            valid_mask=common_snapshot,
            endpoint_reference=endpoint_snapshot,
            control_reference=control_snapshot,
            estimand=selected_estimand,
            analysis_role=analysis_role,
            replicate_ids=tuple(endpoint.replicate_ids),
            protein_ids=tuple(endpoint.protein_ids),
            _verification_seal=_PAIRING_SEAL,
        )

    @staticmethod
    def _readonly_copy(values: np.ndarray) -> np.ndarray:
        snapshot = np.array(values, copy=True)
        snapshot.setflags(write=False)
        return snapshot

    @staticmethod
    def _validate_shape(matrix: MeasurementMatrix) -> None:
        values = np.asarray(matrix.values)
        if values.ndim != 2:
            raise MeasurementShapeError("measurement values must be two-dimensional")
        if values.shape[0] != len(matrix.replicate_ids):
            raise MeasurementShapeError(
                "matrix rows must match the number of replicate keys"
            )
        if values.shape[1] != len(matrix.protein_ids):
            raise MeasurementShapeError(
                "matrix columns must match the number of protein keys"
            )

    @staticmethod
    def _reject_duplicate_keys(matrix: MeasurementMatrix) -> None:
        for key_name, keys in (
            ("replicate", tuple(matrix.replicate_ids)),
            ("protein", tuple(matrix.protein_ids)),
        ):
            if len(set(keys)) != len(keys):
                raise DuplicateMeasurementKeyError(
                    "%s keys must be unique for strict pairing" % key_name
                )

    @staticmethod
    def _require_aligned_keys(
        endpoint_keys: Sequence[Hashable],
        control_keys: Sequence[Hashable],
        key_name: str,
    ) -> None:
        endpoint_tuple = tuple(endpoint_keys)
        control_tuple = tuple(control_keys)
        if endpoint_tuple == control_tuple:
            return
        if set(endpoint_tuple) == set(control_tuple):
            raise MisorderedMeasurementError(
                "%s keys contain the same identities in a different order" % key_name
            )
        raise UnmatchedMeasurementError(
            "%s keys do not define one-to-one measured-control matches" % key_name
        )
