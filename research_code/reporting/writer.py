from __future__ import annotations

from dataclasses import asdict
import json
import math
import numbers
import os
from pathlib import Path
import re
import tempfile
from typing import Any

from experiment_core.base import ExperimentResult


def _json_safe(value: Any) -> Any:
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_safe(item) for item in value]
    return value


class AggregateReportWriter:
    schema_version = "1.0"

    _sensitive_text = re.compile(
        r"(?:/Users/|/home/|/var/folders/|private-data|\.codex/private|[A-Za-z]:\\)",
        flags=re.IGNORECASE,
    )

    def write(self, result: ExperimentResult, output_dir: Path) -> None:
        self._validate(result)
        payload = _json_safe(asdict(result))
        payload["schema_version"] = self.schema_version
        json_text = json.dumps(
            payload, ensure_ascii=False, indent=2, sort_keys=True
        ) + "\n"
        lines = [
            f"# {result.name}",
            "",
            f"Status: `{result.status}`",
            "",
            "## Metrics",
            "",
            "| Metric | Value |",
            "|---|---:|",
        ]
        for name, value in sorted(result.metrics.items()):
            display = "undefined" if not math.isfinite(float(value)) else f"{float(value):.6f}"
            lines.append(f"| `{name}` | {display} |")
        if result.provenance:
            lines.extend(("", "## Provenance", "", "| Field | Value |", "|---|---|"))
            for name, value in sorted(result.provenance.items()):
                lines.append(f"| `{name}` | `{value}` |")
        lines.extend(("", "Only aggregate metrics are persisted; raw vectors are never written."))
        markdown_text = "\n".join(lines) + "\n"
        self._atomic_write_many(
            output_dir,
            {"result.json": json_text, "REPORT.md": markdown_text},
        )

    def _validate(self, result: ExperimentResult) -> None:
        for label, value in (("name", result.name), ("status", result.status)):
            if not isinstance(value, str) or not value or len(value) > 160:
                raise TypeError(f"{label} must be a short non-empty string")
            self._reject_sensitive_text(value)
        for name, value in result.metrics.items():
            self._validate_key(name, "metric")
            if isinstance(value, bool) or not isinstance(value, numbers.Real):
                raise TypeError(f"metric {name} must be a numeric scalar")
            if math.isinf(float(value)):
                raise ValueError(f"metric {name} cannot be infinite")
        for name, value in result.counts.items():
            self._validate_key(name, "count")
            if isinstance(value, bool) or not isinstance(value, numbers.Integral):
                raise TypeError(f"count {name} must be a non-negative integer")
            if int(value) < 0:
                raise ValueError(f"count {name} must be non-negative")
        for name, value in result.contract.items():
            self._validate_key(name, "contract")
            if not isinstance(value, bool):
                raise TypeError(f"contract {name} must be boolean")
        for name, value in result.provenance.items():
            self._validate_key(name, "provenance")
            if isinstance(value, str):
                if len(value) > 512:
                    raise ValueError(f"provenance {name} is too long")
                self._reject_sensitive_text(value)
            elif value is not None and not isinstance(
                value, (bool, numbers.Integral, numbers.Real)
            ):
                raise TypeError(f"provenance {name} must be a scalar")
        if not isinstance(result.notes, tuple):
            raise TypeError("notes must be an immutable tuple of strings")
        if len(result.notes) > 32:
            raise ValueError("too many report notes")
        for note in result.notes:
            if not isinstance(note, str):
                raise TypeError("report notes must be strings")
            if len(note) > 2000:
                raise ValueError("report note is too long")
            self._reject_sensitive_text(note)

    @staticmethod
    def _validate_key(name: Any, family: str) -> None:
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,160}", name):
            raise TypeError(f"{family} name must be a short portable string")

    def _reject_sensitive_text(self, value: str) -> None:
        if self._sensitive_text.search(value):
            raise ValueError("reports cannot contain an absolute path or private-data reference")

    @staticmethod
    def _atomic_write_many(output_dir: Path, outputs: dict) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        temporary_paths = []
        try:
            for name, content in outputs.items():
                descriptor, temporary = tempfile.mkstemp(
                    dir=output_dir, prefix=f".{name}.", text=True
                )
                temporary_path = Path(temporary)
                temporary_paths.append(temporary_path)
                with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                    stream.write(content)
                    stream.flush()
                    os.fsync(stream.fileno())
            for temporary_path, name in zip(temporary_paths, outputs):
                os.replace(temporary_path, output_dir / name)
            temporary_paths.clear()
        finally:
            for temporary_path in temporary_paths:
                temporary_path.unlink(missing_ok=True)
