"""Provider Interface and three public-only Implementations."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Callable, Mapping, Optional, Protocol, Tuple

from future_experiments import PublicEvidencePacket

from .schema import CausalChain, MECHANISM_AXES, PublicCausalCase


class CausalChainProvider(Protocol):
    """One narrow provider Interface: public packet in, bounded chain out."""

    def infer(self, packet: PublicEvidencePacket) -> CausalChain:
        ...


class FixtureCausalChainProvider:
    """Deterministic offline Implementation for tests and frozen public pilots."""

    def __init__(self, chains: Mapping[str, CausalChain]) -> None:
        self._chains = dict(chains)

    def infer(self, packet: PublicEvidencePacket) -> CausalChain:
        case = PublicCausalCase.from_packet(packet)
        if case.entity not in self._chains:
            raise KeyError("no frozen public chain for entity %r" % case.entity)
        chain = self._chains[case.entity]
        chain.validate(case.citations)
        return chain


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        raise RuntimeError("provider request refused an HTTP redirect")


def _post_json(url: str, payload: Mapping[str, object], timeout: int) -> Mapping[str, object]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, sort_keys=True).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), _NoRedirect)
    with opener.open(request, timeout=timeout) as response:
        parsed = json.load(response)
    if not isinstance(parsed, dict):
        raise ValueError("provider response must be an object")
    return parsed


def _chain_schema() -> Mapping[str, object]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["edges"],
        "properties": {
            "edges": {
                "type": "array",
                "minItems": 3,
                "maxItems": 8,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "axis",
                        "citation",
                        "confidence",
                        "direction",
                        "relation",
                        "source",
                    ],
                    "properties": {
                        "axis": {"type": "string", "enum": list(MECHANISM_AXES)},
                        "citation": {"type": "string"},
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                        "direction": {"type": "integer", "enum": [-1, 0, 1]},
                        "relation": {"type": "string"},
                        "source": {"type": "string"},
                    },
                },
            }
        },
    }


def _provider_prompt(case: PublicCausalCase) -> str:
    task = {
        "contract": (
            "Infer 3-8 evidence-linked mechanism edges. Each edge must end on one "
            "allowed axis. Do not emit prose, genes, proteins, embeddings or response vectors."
        ),
        "case": case.provider_payload(),
    }
    return json.dumps(task, sort_keys=True, separators=(",", ":"))


def _responses_api_output_text(response: Mapping[str, object]) -> str:
    """Extract text from either an SDK-like fixture or raw Responses REST JSON."""

    convenience = response.get("output_text")
    if isinstance(convenience, str):
        return convenience
    parts = []
    output = response.get("output")
    if isinstance(output, list):
        for item in output:
            if not isinstance(item, dict):
                continue
            content = item.get("content")
            if not isinstance(content, list):
                continue
            for block in content:
                if (
                    isinstance(block, dict)
                    and block.get("type") == "output_text"
                    and isinstance(block.get("text"), str)
                ):
                    parts.append(block["text"])
    if parts:
        return "".join(parts)
    raise ValueError("OpenAI response is missing raw output_text content")


class OllamaCausalChainProvider:
    """Loopback-only Ollama Adapter; it cannot address a remote host."""

    def __init__(
        self,
        model: str = "qwen3:8b",
        endpoint: str = "http://127.0.0.1:11434/api/generate",
        timeout: int = 240,
        transport: Callable[[str, Mapping[str, object], int], Mapping[str, object]] = _post_json,
    ) -> None:
        parsed = urllib.parse.urlparse(endpoint)
        if (
            parsed.scheme != "http"
            or parsed.hostname not in ("127.0.0.1", "localhost")
            or parsed.port not in (None, 11434)
            or parsed.username
            or parsed.password
            or parsed.path != "/api/generate"
        ):
            raise ValueError("Ollama provider must use the loopback /api/generate endpoint")
        self._model = model
        self._endpoint = endpoint
        self._timeout = timeout
        self._transport = transport

    def infer(self, packet: PublicEvidencePacket) -> CausalChain:
        case = PublicCausalCase.from_packet(packet)
        payload = {
            "format": _chain_schema(),
            "model": self._model,
            "options": {"seed": 20260810, "temperature": 0},
            "prompt": _provider_prompt(case),
            "stream": False,
            "think": False,
        }
        response = self._transport(self._endpoint, payload, self._timeout)
        raw = response.get("response")
        if not isinstance(raw, str):
            raise ValueError("Ollama response is missing structured response text")
        return CausalChain.from_json(raw, case.citations)


class OpenAIPublicOnlyProvider:
    """Optional public-only OpenAI Adapter, deliberately disabled by default.

    This class is never used by the offline pilot. Enabling it is an explicit
    future action and still exposes only the already validated public case.
    """

    _ENDPOINT = "https://api.openai.com/v1/responses"

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-5-mini",
        enabled: bool = False,
        timeout: int = 120,
        transport: Optional[Callable[[str, Mapping[str, object], Mapping[str, str], int], Mapping[str, object]]] = None,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._enabled = enabled
        self._timeout = timeout
        self._transport = transport or self._default_transport

    @staticmethod
    def _default_transport(
        url: str,
        payload: Mapping[str, object],
        headers: Mapping[str, str],
        timeout: int,
    ) -> Mapping[str, object]:
        request = urllib.request.Request(
            url,
            data=json.dumps(payload, sort_keys=True).encode("utf-8"),
            headers=dict(headers),
            method="POST",
        )
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), _NoRedirect)
        with opener.open(request, timeout=timeout) as response:
            parsed = json.load(response)
        if not isinstance(parsed, dict):
            raise ValueError("OpenAI response must be an object")
        return parsed

    def infer(self, packet: PublicEvidencePacket) -> CausalChain:
        if not self._enabled:
            raise RuntimeError("OpenAI public-only Adapter is disabled; no network call was made")
        if not self._api_key:
            raise RuntimeError("an API key is required only after explicit enablement")
        case = PublicCausalCase.from_packet(packet)
        payload = {
            "model": self._model,
            "input": _provider_prompt(case),
            "store": False,
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "public_causal_chain",
                    "strict": True,
                    "schema": _chain_schema(),
                }
            },
        }
        response = self._transport(
            self._ENDPOINT,
            payload,
            {
                "Authorization": "Bearer " + self._api_key,
                "Content-Type": "application/json",
            },
            self._timeout,
        )
        raw = _responses_api_output_text(response)
        return CausalChain.from_json(raw, case.citations)
