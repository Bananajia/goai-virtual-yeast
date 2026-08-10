"""Deterministic offline runner for the six-signature public mini-pilot."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Callable, Mapping, Optional
import urllib.request

from future_experiments.public_causal_chain import (
    CausalChainProvider,
    FixtureCausalChainProvider,
)

from .evaluate import evaluate_chains
from .fixture import FrozenL1000Fixture
from .knowledge import fixture_chains, packet_for_query


FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class OllamaRuntimeIdentity:
    """Non-sensitive provenance for a loopback open-weight provider."""

    provider: str
    model: str
    model_digest: str
    ollama_version: str

    def validate(self) -> None:
        if self.provider != "ollama-loopback":
            raise ValueError("the local pilot accepts the loopback Ollama provider only")
        if not self.model or len(self.model) > 160 or any(c in self.model for c in "\r\n\x00"):
            raise ValueError("invalid local model identifier")
        if not _SHA256.fullmatch(self.model_digest):
            raise ValueError("model_digest must be a lowercase SHA-256 digest")
        if not self.ollama_version or len(self.ollama_version) > 80:
            raise ValueError("invalid Ollama version")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        raise RuntimeError("Ollama runtime probe refused an HTTP redirect")


def _get_loopback_json(url: str, timeout: int) -> Mapping[str, object]:
    if url not in (
        "http://127.0.0.1:11434/api/version",
        "http://127.0.0.1:11434/api/tags",
    ):
        raise ValueError("runtime probe accepts two fixed loopback endpoints only")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), _NoRedirect)
    with opener.open(url, timeout=timeout) as response:
        parsed = json.load(response)
    if not isinstance(parsed, dict):
        raise ValueError("Ollama runtime response must be an object")
    return parsed


def probe_ollama_runtime(
    model: str,
    *,
    timeout: int = 5,
    transport: Callable[[str, int], Mapping[str, object]] = _get_loopback_json,
) -> OllamaRuntimeIdentity:
    """Resolve local server version and the exact installed-model digest."""

    version_doc = transport("http://127.0.0.1:11434/api/version", timeout)
    tags_doc = transport("http://127.0.0.1:11434/api/tags", timeout)
    version = version_doc.get("version")
    rows = tags_doc.get("models")
    if not isinstance(version, str) or not isinstance(rows, list):
        raise ValueError("Ollama version/tags schema is invalid")
    matches = [row for row in rows if isinstance(row, dict) and row.get("name") == model]
    if len(matches) != 1:
        raise ValueError("requested local model must match exactly one installed Ollama tag")
    digest = matches[0].get("digest")
    identity = OllamaRuntimeIdentity(
        provider="ollama-loopback",
        model=model,
        model_digest=str(digest),
        ollama_version=version,
    )
    identity.validate()
    return identity


def run_offline_smoke(output_dir: Path) -> Mapping[str, object]:
    """Run without network or private data and persist aggregates only."""

    fixture = FrozenL1000Fixture.load(FIXTURE_DIR)
    provider = FixtureCausalChainProvider(fixture_chains())
    predictions = {
        query.signature_id: provider.infer(packet_for_query(query)) for query in fixture.queries
    }
    evaluated = evaluate_chains(fixture, predictions)
    result = {
        "protocol": "public-l1000fwd-six-causal-axis-smoke-v1",
        "status": "SMOKE_ONLY",
        "metrics": evaluated["metrics"],
        "counts": evaluated["counts"],
        "contract": {
            "fixture_sha256_verified": True,
            "provider_network_called": False,
            "private_data_read": False,
            "protein_vector_generated": False,
            "query_truth_separated": True,
        },
        "interpretation": (
            "Interface smoke only: six human HA1E RNA signatures are too small to establish "
            "transfer to yeast proteomics. A real local/authorized model must beat this frozen "
            "fixture under a preregistered public holdout before promotion."
        ),
    }
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "RESULTS.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "REPORT.md").write_text(_report(result), encoding="utf-8")
    return result


def run_local_ollama_pilot(
    output_dir: Path,
    *,
    provider: CausalChainProvider,
    runtime_identity: OllamaRuntimeIdentity,
    case_limit: int = 1,
) -> Mapping[str, object]:
    """Run one smoke case or all six cases without persisting provider I/O.

    The provider sees only ``SignatureQuery -> PublicEvidencePacket``.  The
    withheld RNA truth is opened by the evaluator after each successful
    inference and never crosses the provider Interface.
    """

    runtime_identity.validate()
    if isinstance(case_limit, bool) or not isinstance(case_limit, int) or not 1 <= case_limit <= 6:
        raise ValueError("case_limit must be an integer in [1, 6]")

    fixture = FrozenL1000Fixture.load(FIXTURE_DIR)
    predictions = {}
    attempted = 0
    failure_category: Optional[str] = None
    failure_code: Optional[str] = None
    for query in fixture.queries[:case_limit]:
        attempted += 1
        try:
            predictions[query.signature_id] = provider.infer(packet_for_query(query))
        except Exception as exc:  # fail closed; never persist raw provider output/error text
            failure_category = type(exc).__name__
            failure_code = (
                "provider_output_schema_invalid"
                if isinstance(exc, ValueError)
                else "provider_runtime_failed_closed"
            )
            break

    provenance = {
        "fixture_sha256": fixture.fixture_sha256,
        "model": runtime_identity.model,
        "model_digest": runtime_identity.model_digest,
        "ollama_version": runtime_identity.ollama_version,
        "provider": runtime_identity.provider,
        "protocol_version": "public-l1000fwd-local-ollama-v1",
    }
    if failure_category is not None:
        result = {
            "status": "BLOCKED",
            "metrics": {},
            "counts": {
                "anonymous_cases_attempted": attempted,
                "anonymous_cases_evaluated": 0,
            },
            "provenance": provenance,
            "failure": {
                "category": failure_category,
                "code": failure_code,
            },
        }
    else:
        selected_queries = fixture.queries[:case_limit]
        selected_fixture = FrozenL1000Fixture(
            queries=selected_queries,
            truth_by_signature={
                query.signature_id: fixture.truth_by_signature[query.signature_id]
                for query in selected_queries
            },
            fixture_sha256=fixture.fixture_sha256,
        )
        evaluated = evaluate_chains(selected_fixture, predictions)
        result = {
            "status": "SMOKE_ONLY" if case_limit == 1 else "PUBLIC_ONLY",
            "metrics": evaluated["metrics"],
            "counts": {
                "anonymous_cases_attempted": attempted,
                "anonymous_cases_evaluated": len(predictions),
            },
            "provenance": provenance,
        }

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "RESULTS.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "REPORT.md").write_text(_local_report(result), encoding="utf-8")
    return result


def _local_report(result: Mapping[str, object]) -> str:
    provenance = result["provenance"]
    counts = result["counts"]
    lines = [
        "# Local open-weight causal-axis pilot",
        "",
        "Status: `%s`" % result["status"],
        "",
        "## Anonymous aggregate",
        "",
        "- Cases attempted: %d" % counts["anonymous_cases_attempted"],
        "- Cases evaluated: %d" % counts["anonymous_cases_evaluated"],
        "- Provider: `%s`" % provenance["provider"],
        "- Model: `%s`" % provenance["model"],
        "- Model digest: `%s`" % provenance["model_digest"],
        "- Ollama version: `%s`" % provenance["ollama_version"],
        "- Public fixture SHA-256: `%s`" % provenance["fixture_sha256"],
        "",
    ]
    if result["status"] == "BLOCKED":
        failure = result["failure"]
        lines.extend(
            (
                "## Fail-closed outcome",
                "",
                "- Code: `%s`" % failure["code"],
                "- Error category: `%s`" % failure["category"],
                "- No provider prompt, response, entity name, chain, or per-case vector was persisted.",
                "",
            )
        )
    else:
        lines.extend(("## Aggregate metrics", "", "| Metric | Value |", "|---|---:|"))
        for name in sorted(result["metrics"]):
            lines.append("| `%s` | %.6f |" % (name, result["metrics"][name]))
        lines.extend(
            (
                "",
                "The provider received cited public mechanism facts only. Withheld RNA truth was opened only by the evaluator after inference. No prompt, response, entity name, chain, or per-case vector was persisted.",
                "",
            )
        )
    return "\n".join(lines)


def _report(result: Mapping[str, object]) -> str:
    metrics = result["metrics"]
    counts = result["counts"]
    lines = [
        "# Public L1000FWD six-signature causal-axis smoke",
        "",
        "This is an offline, public-only Interface test. It does not read the competition data, call an external provider, or predict a protein vector.",
        "",
        "## Frozen cohort",
        "",
        "- Signatures: %d (HA1E; six distinct perturbagens)" % counts["signatures"],
        "- Frozen mechanism axes: %d" % counts["mechanism_axes"],
        "- Structured causal edges: %d" % counts["causal_edges"],
        "- RNA marker hits used only by the evaluator: %d" % counts["rna_marker_hits"],
        "",
        "## Aggregate metrics",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for name in sorted(metrics):
        lines.append("| `%s` | %.6f |" % (name, metrics[name]))
    lines.extend(
        (
            "",
            "## Interpretation boundary",
            "",
            result["interpretation"],
            "",
            "The fixture manifest records source URLs, retrieval date, byte count and SHA-256. Query metadata and withheld RNA truth are represented by different types, so the provider never receives the evaluator's ranked gene lists.",
            "",
        )
    )
    return "\n".join(lines)
