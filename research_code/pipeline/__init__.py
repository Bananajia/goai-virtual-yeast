"""Data loading, preprocessing, control pairing, and OOD split Modules."""

from .preprocessing import (
    Log2ProteomeTransformer,
    MissingnessFilter,
    ProteinOutputContract,
)
from .splitting import GroupedOODSplitter, OODSplit
from .metadata import MetadataEncoder, MetadataField
from .dataset import (
    DataScope,
    DatasetBundle,
    DatasetAdapter,
    InMemoryDatasetAdapter,
    align_dataset_frames,
    require_training_bundle,
)
from .controls import (
    AnalysisRole,
    ControlEstimand,
    MeasuredControlPairer,
    MeasurementMatrix,
    MeasurementRole,
    ResponseEstimate,
)
from .submission import SubmissionContract
from .vehicle import OfficialVehicleMap, Vehicle, match_official_controls

__all__ = [
    "GroupedOODSplitter",
    "DataScope",
    "DatasetAdapter",
    "DatasetBundle",
    "InMemoryDatasetAdapter",
    "align_dataset_frames",
    "require_training_bundle",
    "AnalysisRole",
    "ControlEstimand",
    "MeasuredControlPairer",
    "MeasurementMatrix",
    "MeasurementRole",
    "ResponseEstimate",
    "SubmissionContract",
    "OfficialVehicleMap",
    "Vehicle",
    "match_official_controls",
    "Log2ProteomeTransformer",
    "MissingnessFilter",
    "MetadataEncoder",
    "MetadataField",
    "OODSplit",
    "ProteinOutputContract",
]
