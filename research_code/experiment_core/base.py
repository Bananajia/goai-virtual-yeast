from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Protocol


class ExperimentStatus(str, Enum):
    PROMOTED = "PROMOTED"
    CONDITIONAL = "CONDITIONAL"
    PUBLIC_ONLY = "PUBLIC_ONLY"
    VALID_REJECT = "VALID_REJECT"
    INVALIDATED = "INVALIDATED"
    BLOCKED = "BLOCKED"
    PENDING = "PENDING"
    GOVERNANCE = "GOVERNANCE"
    COMPLETED = "COMPLETED"


@dataclass(frozen=True)
class RunContext:
    output_dir: Path
    data_scope: str
    seed: int = 0
    data_root: Path = None


@dataclass(frozen=True)
class ExperimentResult:
    name: str
    status: str
    metrics: Mapping[str, float]
    counts: Mapping[str, int]
    contract: Mapping[str, bool]
    provenance: Mapping[str, Any] = field(default_factory=dict)
    notes: tuple = field(default_factory=tuple)


class Experiment(Protocol):
    name: str
    description: str

    def run(self, context: RunContext) -> ExperimentResult:
        ...
