"""Fail-closed contract for experiments that may call a model provider."""

from dataclasses import dataclass
from enum import Enum
import re
from typing import Tuple


class EvidenceScope(str, Enum):
    PUBLIC = "public"
    SYNTHETIC = "synthetic"
    PRIVATE_COMPETITION = "private_competition"


@dataclass(frozen=True)
class PublicEvidencePacket:
    entity: str
    scope: EvidenceScope
    facts: Tuple[str, ...]
    citations: Tuple[str, ...]


class PublicOnlyGuard:
    """A narrow Seam that prevents private matrices from reaching providers."""

    _forbidden = re.compile(
        r"(?:protein|proteome|response|embedding|prediction)_?(?:vector|matrix)?\s*=",
        re.IGNORECASE,
    )

    def validate(self, packet: PublicEvidencePacket) -> None:
        if packet.scope not in (EvidenceScope.PUBLIC, EvidenceScope.SYNTHETIC):
            raise ValueError("future provider experiments accept public or synthetic evidence only")
        joined = "\n".join((packet.entity,) + packet.facts + packet.citations)
        if self._forbidden.search(joined):
            raise ValueError("vector or response payloads are forbidden at the provider Seam")
        if packet.scope is EvidenceScope.PUBLIC and not packet.citations:
            raise ValueError("public evidence must include at least one citation")
