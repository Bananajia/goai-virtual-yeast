"""Replay historical conclusions from aggregate-only evidence.

This Module intentionally cannot load competition matrices.  Its Interface
accepts only a declarative evidence registry plus caller-supplied project roots,
then verifies source hashes before extracting frozen aggregate metrics.  That
ordering is the fail-closed Seam between historical evidence and executable
research code.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple

from reporting import AggregateReportWriter

from .base import ExperimentResult, ExperimentStatus, RunContext


INVALIDATED_STATUSES = frozenset(("INVALIDATED",))
SOURCE_MISSING_STATUSES = frozenset(("BLOCKED_SOURCE_MISSING",))


@dataclass(frozen=True)
class EvidenceSource:
    root: str
    path: str
    kind: str


@dataclass(frozen=True)
class MetricExpectation:
    name: str
    value: float
    tolerance: float
    locator: Mapping[str, Any]


@dataclass(frozen=True)
class EvidenceRecord:
    experiment_id: str
    status: str
    golden: bool
    source: Optional[EvidenceSource]
    source_sha256: Optional[str]
    replacement: Optional[str]
    validity: str
    expected_aggregate_metrics: Tuple[MetricExpectation, ...]
    persistence: str = "PERSISTENT"


@dataclass(frozen=True)
class RecordReplay:
    experiment_id: str
    status: str
    metrics_verified: int
    reason: str


@dataclass(frozen=True)
class EvidenceReplayReceipt:
    status: str
    records_requested: int
    records_passed: int
    records_failed: int
    records_blocked: int
    metrics_verified: int
    invalidated_used_as_golden: int
    records: Tuple[RecordReplay, ...]


class EvidenceRegistry:
    """Validated declarative registry with an experiment-id lookup Interface."""

    def __init__(self, records: Iterable[EvidenceRecord]) -> None:
        indexed: Dict[str, EvidenceRecord] = {}
        for record in records:
            if record.experiment_id in indexed:
                raise ValueError(f"duplicate evidence record: {record.experiment_id}")
            if record.status in INVALIDATED_STATUSES and record.golden:
                raise ValueError(
                    f"invalidated evidence cannot be golden: {record.experiment_id}"
                )
            if record.status in SOURCE_MISSING_STATUSES and record.source is not None:
                raise ValueError(
                    f"source-missing evidence must not name a source: {record.experiment_id}"
                )
            if record.source is not None:
                path = Path(record.source.path)
                if path.is_absolute() or "private-data" in path.parts:
                    raise ValueError(
                        f"evidence source must be relative and aggregate-only: {record.experiment_id}"
                    )
                if record.source.root not in ("documents", "workspace"):
                    raise ValueError(
                        f"unknown evidence root {record.source.root}: {record.experiment_id}"
                    )
                if record.source.kind not in ("aggregate_markdown", "aggregate_json"):
                    raise ValueError(
                        f"unsupported aggregate source kind: {record.source.kind}"
                    )
                if not record.source_sha256 or not re.fullmatch(
                    r"[0-9a-f]{64}", record.source_sha256
                ):
                    raise ValueError(
                        f"aggregate source requires a SHA-256: {record.experiment_id}"
                    )
            indexed[record.experiment_id] = record
        self._records = indexed

    @classmethod
    def load(cls, path: Path) -> "EvidenceRegistry":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("schema_version") != "1.0":
            raise ValueError("unsupported evidence registry schema")
        records = []
        for raw in payload.get("records", []):
            source_raw = raw.get("source")
            source = EvidenceSource(**source_raw) if source_raw is not None else None
            expectations = tuple(
                MetricExpectation(
                    name=item["name"],
                    value=float(item["value"]),
                    tolerance=float(item["tolerance"]),
                    locator=item["locator"],
                )
                for item in raw.get("expected_aggregate_metrics", [])
            )
            records.append(
                EvidenceRecord(
                    experiment_id=raw["experiment_id"],
                    status=raw["status"],
                    golden=bool(raw["golden"]),
                    source=source,
                    source_sha256=raw.get("source_sha256"),
                    replacement=raw.get("replacement"),
                    validity=raw["validity"],
                    expected_aggregate_metrics=expectations,
                    persistence=raw.get("persistence", "PERSISTENT"),
                )
            )
        return cls(records)

    @property
    def records(self) -> Tuple[EvidenceRecord, ...]:
        return tuple(self._records.values())

    def get(self, experiment_id: str) -> EvidenceRecord:
        try:
            return self._records[experiment_id]
        except KeyError as error:
            raise KeyError(f"unknown evidence record: {experiment_id}") from error


class LegacyEvidenceReplay:
    """Unified Experiment Implementation for aggregate-only legacy replay."""

    name = "legacy_evidence_replay"
    description = "Verify frozen aggregate evidence without reading private matrices."

    def __init__(
        self,
        registry_path: Optional[Path] = None,
        experiment_ids: Optional[Iterable[str]] = None,
        workspace_root: Optional[Path] = None,
        run_name: Optional[str] = None,
    ) -> None:
        self.name = run_name or type(self).name
        self.registry_path = registry_path or (
            Path(__file__).resolve().parents[1] / "evidence" / "registry.json"
        )
        self.experiment_ids = (
            tuple(experiment_ids) if experiment_ids is not None else None
        )
        self.workspace_root = workspace_root

    def verify(
        self,
        documents_root: Path,
        experiment_ids: Optional[Iterable[str]] = None,
        workspace_root: Optional[Path] = None,
    ) -> EvidenceReplayReceipt:
        registry = EvidenceRegistry.load(self.registry_path)
        selected = self._select_records(registry, experiment_ids)
        roots = {
            "documents": Path(documents_root),
            "workspace": Path(workspace_root) if workspace_root is not None else None,
        }
        replayed = tuple(self._verify_record(record, roots) for record in selected)
        passed = sum(item.status == "PASS" for item in replayed)
        failed = sum(item.status == "FAIL" for item in replayed)
        blocked = sum(item.status == "BLOCKED" for item in replayed)
        invalidated_as_golden = sum(
            record.status in INVALIDATED_STATUSES and record.golden
            for record in selected
        )
        status = "PASS" if failed == 0 and blocked == 0 else "FAIL"
        return EvidenceReplayReceipt(
            status=status,
            records_requested=len(selected),
            records_passed=passed,
            records_failed=failed,
            records_blocked=blocked,
            metrics_verified=sum(item.metrics_verified for item in replayed),
            invalidated_used_as_golden=invalidated_as_golden,
            records=replayed,
        )

    def run(self, context: RunContext) -> ExperimentResult:
        if context.data_scope != "aggregate-only":
            raise ValueError("legacy_evidence_replay requires data_scope=aggregate-only")
        if context.data_root is None:
            raise ValueError("legacy_evidence_replay requires the persistent project root")
        receipt = self.verify(
            documents_root=context.data_root,
            experiment_ids=self.experiment_ids,
            workspace_root=self.workspace_root,
        )
        result = ExperimentResult(
            name=self.name,
            status=(
                ExperimentStatus.GOVERNANCE.value
                if receipt.status == "PASS"
                else ExperimentStatus.BLOCKED.value
            ),
            metrics={
                "evidence_replay_pass_rate": (
                    receipt.records_passed / receipt.records_requested
                    if receipt.records_requested
                    else 0.0
                ),
                "metrics_verified": float(receipt.metrics_verified),
            },
            counts={
                "records_requested": receipt.records_requested,
                "records_passed": receipt.records_passed,
                "records_failed": receipt.records_failed,
                "records_blocked": receipt.records_blocked,
            },
            contract={
                "aggregate_only": True,
                "source_hashes_verified": receipt.records_failed == 0,
                "invalidated_excluded_from_golden": (
                    receipt.invalidated_used_as_golden == 0
                ),
                "private_vectors_persisted": False,
            },
            provenance={"data_scope": context.data_scope, "seed": context.seed},
            notes=(
                "Legacy evidence was replayed from aggregate documents only.",
                "No competition matrix, identity, prediction or protein vector was read.",
            ),
        )
        AggregateReportWriter().write(result, context.output_dir)
        return result

    def _select_records(
        self,
        registry: EvidenceRegistry,
        experiment_ids: Optional[Iterable[str]],
    ) -> Tuple[EvidenceRecord, ...]:
        requested = (
            tuple(experiment_ids)
            if experiment_ids is not None
            else self.experiment_ids
        )
        if requested is not None:
            return tuple(registry.get(experiment_id) for experiment_id in requested)
        return tuple(
            record
            for record in registry.records
            if record.golden
            and record.source is not None
            and record.source.root == "documents"
        )

    def _verify_record(
        self,
        record: EvidenceRecord,
        roots: Mapping[str, Optional[Path]],
    ) -> RecordReplay:
        if not record.golden:
            return RecordReplay(
                record.experiment_id,
                "BLOCKED",
                0,
                "record is not eligible for golden replay",
            )
        if record.status in INVALIDATED_STATUSES:
            return RecordReplay(
                record.experiment_id,
                "FAIL",
                0,
                "invalidated evidence cannot be replayed as golden",
            )
        if record.source is None:
            return RecordReplay(
                record.experiment_id,
                "BLOCKED",
                0,
                "aggregate source is missing",
            )
        root = roots.get(record.source.root)
        if root is None:
            return RecordReplay(
                record.experiment_id,
                "BLOCKED",
                0,
                f"caller did not supply the {record.source.root} evidence root",
            )
        source_path = root / record.source.path
        if not source_path.is_file():
            return RecordReplay(
                record.experiment_id,
                "FAIL",
                0,
                "aggregate source is absent",
            )
        source_bytes = source_path.read_bytes()
        actual_hash = hashlib.sha256(source_bytes).hexdigest()
        if actual_hash != record.source_sha256:
            return RecordReplay(
                record.experiment_id,
                "FAIL",
                0,
                "aggregate source hash changed",
            )
        try:
            payload: Any
            if record.source.kind == "aggregate_json":
                payload = json.loads(source_bytes.decode("utf-8"))
            else:
                payload = source_bytes.decode("utf-8")
            for expectation in record.expected_aggregate_metrics:
                actual = self._extract_metric(payload, expectation.locator)
                if abs(actual - expectation.value) > expectation.tolerance:
                    raise ValueError(
                        f"metric {expectation.name} changed from frozen value"
                    )
        except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError):
            return RecordReplay(
                record.experiment_id,
                "FAIL",
                0,
                "frozen aggregate metric could not be reproduced",
            )
        return RecordReplay(
            record.experiment_id,
            "PASS",
            len(record.expected_aggregate_metrics),
            "source hash and frozen aggregate metrics verified",
        )

    @staticmethod
    def _extract_metric(payload: Any, locator: Mapping[str, Any]) -> float:
        kind = locator.get("kind")
        if kind == "regex":
            if not isinstance(payload, str):
                raise TypeError("regex locator requires text")
            match = re.search(str(locator["pattern"]), payload)
            if match is None:
                raise ValueError("metric pattern not found")
            raw = match.group("value").replace(",", "")
            return float(raw)
        if kind == "json_pointer":
            current = payload
            pointer = str(locator["pointer"])
            if not pointer.startswith("/"):
                raise ValueError("JSON pointer must start with slash")
            for raw_token in pointer[1:].split("/"):
                token = raw_token.replace("~1", "/").replace("~0", "~")
                if isinstance(current, list):
                    current = current[int(token)]
                else:
                    current = current[token]
            return float(current)
        raise ValueError(f"unsupported metric locator: {kind}")
