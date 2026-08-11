"""Hash-verified loader with a hard query/truth separation."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Dict, Mapping, Tuple


MAX_FIXTURE_BYTES = 55 * 1024


@dataclass(frozen=True)
class SignatureQuery:
    signature_id: str
    perturbagen: str
    perturbagen_id: str
    cell_line: str
    time_hours: float
    dose_micromolar: float


@dataclass(frozen=True)
class SignatureTruth:
    signature_id: str
    up_genes: Tuple[str, ...]
    down_genes: Tuple[str, ...]


@dataclass(frozen=True)
class FrozenL1000Fixture:
    queries: Tuple[SignatureQuery, ...]
    truth_by_signature: Mapping[str, SignatureTruth]
    fixture_sha256: str

    @classmethod
    def load(cls, fixture_dir: Path) -> "FrozenL1000Fixture":
        fixture_dir = Path(fixture_dir)
        manifest_path = fixture_dir / "manifest.json"
        if not manifest_path.is_file():
            raise ValueError("public fixture manifest is missing")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("source_scope") != "public":
            raise ValueError("RNA mini-pilot accepts a public fixture only")
        fixture_name = manifest.get("fixture")
        if fixture_name != "l1000fwd_six.json":
            raise ValueError("unexpected public fixture name")
        data_path = fixture_dir / fixture_name
        if not data_path.is_file() or data_path.stat().st_size >= MAX_FIXTURE_BYTES:
            raise ValueError("fixture is missing or exceeds the frozen 55 KB limit")
        raw = data_path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != manifest.get("sha256"):
            raise ValueError("public fixture SHA-256 mismatch")
        if manifest.get("fixture_bytes") not in (None, len(raw)):
            raise ValueError("public fixture byte count mismatch")

        payload = json.loads(raw.decode("utf-8"))
        required_root = {
            "ranked_gene_limit_per_direction",
            "schema_version",
            "signatures",
            "source",
            "source_api",
        }
        if not isinstance(payload, dict) or set(payload) != required_root:
            raise ValueError("public fixture root schema changed")
        if payload["schema_version"] != 1 or payload["source"] != "L1000FWD":
            raise ValueError("unsupported public fixture version or source")
        rows = payload["signatures"]
        if not isinstance(rows, list) or len(rows) != 6:
            raise ValueError("the mini-pilot freezes exactly six signatures")

        queries = []
        truths: Dict[str, SignatureTruth] = {}
        query_keys = {
            "cell_line",
            "dose_micromolar",
            "perturbagen",
            "perturbagen_id",
            "signature_id",
            "time_hours",
        }
        for row in rows:
            if not isinstance(row, dict) or set(row) != {"query", "truth"}:
                raise ValueError("signature row schema changed")
            query, truth = row["query"], row["truth"]
            if not isinstance(query, dict) or set(query) != query_keys:
                raise ValueError("query schema changed or contains withheld truth")
            if not isinstance(truth, dict) or set(truth) != {"down_genes", "up_genes"}:
                raise ValueError("truth schema changed")
            signature_id = _short_string(query["signature_id"], "signature_id", 160)
            if signature_id in truths:
                raise ValueError("signature IDs must be unique")
            query_record = SignatureQuery(
                signature_id=signature_id,
                perturbagen=_short_string(query["perturbagen"], "perturbagen", 80),
                perturbagen_id=_short_string(query["perturbagen_id"], "perturbagen_id", 40),
                cell_line=_short_string(query["cell_line"], "cell_line", 24),
                time_hours=_finite_nonnegative(query["time_hours"], "time_hours"),
                dose_micromolar=_finite_nonnegative(query["dose_micromolar"], "dose_micromolar"),
            )
            up = _gene_tuple(truth["up_genes"], "up_genes")
            down = _gene_tuple(truth["down_genes"], "down_genes")
            if set(up) & set(down):
                raise ValueError("a gene cannot be both up and down in the frozen truth")
            queries.append(query_record)
            truths[signature_id] = SignatureTruth(signature_id, up, down)
        return cls(tuple(queries), truths, digest)


def _short_string(value: object, field: str, maximum: int) -> str:
    if not isinstance(value, str) or not value or len(value) > maximum:
        raise ValueError("invalid %s" % field)
    if "\n" in value or "\r" in value or "\x00" in value:
        raise ValueError("invalid control character in %s" % field)
    return value


def _finite_nonnegative(value: object, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("%s must be numeric" % field)
    result = float(value)
    if result < 0.0 or result != result or result == float("inf"):
        raise ValueError("%s must be finite and nonnegative" % field)
    return result


def _gene_tuple(value: object, field: str) -> Tuple[str, ...]:
    if not isinstance(value, list) or not value or len(value) > 100:
        raise ValueError("%s must be a nonempty bounded list" % field)
    genes = tuple(_short_string(gene, field, 40).upper() for gene in value)
    if len(set(genes)) != len(genes):
        raise ValueError("%s contains duplicate genes" % field)
    return genes
