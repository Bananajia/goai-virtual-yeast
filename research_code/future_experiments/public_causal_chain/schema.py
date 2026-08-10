"""Closed schemas for public-evidence mechanism chains.

The provider Seam deliberately accepts no prose prompt.  Every fact is a
canonical JSON record with a frozen relation vocabulary, and every output is a
3--8 edge chain ending on one of 23 interpretable yeast-relevant axes.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
import urllib.parse
from typing import Mapping, Tuple

from future_experiments import EvidenceScope, PublicEvidencePacket, PublicOnlyGuard


MECHANISM_AXES: Tuple[str, ...] = (
    "tor_nutrient_signaling",
    "translation_ribosome",
    "proteasome_protein_degradation",
    "chaperone_proteostasis",
    "ergosterol_membrane_sterol",
    "cell_wall_biosynthesis",
    "membrane_ion_homeostasis",
    "mitochondrial_respiration",
    "glycolysis_fermentation",
    "amino_acid_biosynthesis",
    "nucleotide_metabolism",
    "dna_replication_repair",
    "transcription_rna_processing",
    "chromatin_epigenetic",
    "cell_cycle",
    "microtubule_spindle",
    "actin_cytoskeleton",
    "oxidative_stress_redox",
    "osmotic_stress",
    "autophagy_vacuole",
    "kinase_phosphatase_signaling",
    "metal_homeostasis",
    "general_antimicrobial_toxicity",
)

FACT_RELATIONS = frozenset(
    ("activates", "associated_with", "binds", "inhibits", "perturbs", "targets")
)
CHAIN_RELATIONS = frozenset(
    ("activates", "associates_with", "disrupts", "increases", "induces", "inhibits", "reduces")
)
_SAFE_TOKEN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ._+()'\-]{0,79}$")
_PUBLIC_HOSTS = frozenset(
    (
        "doi.org",
        "maayanlab.cloud",
        "pubchem.ncbi.nlm.nih.gov",
        "pubmed.ncbi.nlm.nih.gov",
        "reactome.org",
        "string-db.org",
        "www.ncbi.nlm.nih.gov",
        "www.reactome.org",
        "www.yeastgenome.org",
        "yeastgenome.org",
    )
)


def _safe_token(value: object, field: str) -> str:
    if not isinstance(value, str) or not _SAFE_TOKEN.fullmatch(value):
        raise ValueError("%s must be a short controlled identifier" % field)
    return value


def _public_citation(value: object) -> str:
    if not isinstance(value, str) or len(value) > 300:
        raise ValueError("citation must be a public URL")
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme != "https" or parsed.hostname not in _PUBLIC_HOSTS:
        raise ValueError("citation host is not in the frozen public allowlist")
    if parsed.username or parsed.password or not parsed.path:
        raise ValueError("citation URL is malformed")
    return value


@dataclass(frozen=True)
class PublicFact:
    subject: str
    relation: str
    object: str
    citation_index: int

    @classmethod
    def from_canonical_json(cls, value: str, citation_count: int) -> "PublicFact":
        try:
            parsed = json.loads(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("facts must be canonical JSON records, not free text") from exc
        required = {"citation_index", "object", "relation", "subject"}
        if not isinstance(parsed, dict) or set(parsed) != required:
            raise ValueError("fact schema is closed; missing or additional fields are forbidden")
        canonical = json.dumps(parsed, sort_keys=True, separators=(",", ":"))
        if value != canonical:
            raise ValueError("facts must use canonical JSON serialization")
        subject = _safe_token(parsed["subject"], "fact.subject")
        object_value = _safe_token(parsed["object"], "fact.object")
        relation = parsed["relation"]
        if relation not in FACT_RELATIONS:
            raise ValueError("fact relation is outside the frozen vocabulary")
        citation_index = parsed["citation_index"]
        if isinstance(citation_index, bool) or not isinstance(citation_index, int):
            raise ValueError("citation_index must be an integer")
        if citation_index < 0 or citation_index >= citation_count:
            raise ValueError("citation_index is out of range")
        return cls(subject, relation, object_value, citation_index)

    def as_dict(self) -> Mapping[str, object]:
        return {
            "citation_index": self.citation_index,
            "object": self.object,
            "relation": self.relation,
            "subject": self.subject,
        }


@dataclass(frozen=True)
class PublicCausalCase:
    entity: str
    facts: Tuple[PublicFact, ...]
    citations: Tuple[str, ...]

    @classmethod
    def from_packet(cls, packet: PublicEvidencePacket) -> "PublicCausalCase":
        PublicOnlyGuard().validate(packet)
        if packet.scope is not EvidenceScope.PUBLIC:
            raise ValueError("causal-chain providers accept cited public evidence only")
        entity = _safe_token(packet.entity, "entity")
        if not packet.facts or len(packet.facts) > 16:
            raise ValueError("a public case requires 1--16 structured facts")
        if len(packet.citations) > 16:
            raise ValueError("a public case accepts at most 16 citations")
        citations = tuple(_public_citation(value) for value in packet.citations)
        facts = tuple(
            PublicFact.from_canonical_json(value, len(citations)) for value in packet.facts
        )
        return cls(entity=entity, facts=facts, citations=citations)

    def provider_payload(self) -> Mapping[str, object]:
        return {
            "entity": self.entity,
            "facts": [fact.as_dict() for fact in self.facts],
            "citations": list(self.citations),
            "allowed_axes": list(MECHANISM_AXES),
        }


@dataclass(frozen=True)
class CausalEdge:
    source: str
    relation: str
    axis: str
    direction: int
    confidence: float
    citation: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, object]) -> "CausalEdge":
        required = {"axis", "citation", "confidence", "direction", "relation", "source"}
        if not isinstance(value, dict) or set(value) != required:
            raise ValueError("causal edge schema is closed")
        direction = value["direction"]
        if isinstance(direction, bool) or direction not in (-1, 0, 1):
            raise ValueError("edge direction must be -1, 0 or 1")
        confidence = value["confidence"]
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
            raise ValueError("edge confidence must be numeric")
        return cls(
            source=_safe_token(value["source"], "edge.source"),
            relation=str(value["relation"]),
            axis=str(value["axis"]),
            direction=int(direction),
            confidence=float(confidence),
            citation=str(value["citation"]),
        )


@dataclass(frozen=True)
class CausalChain:
    edges: Tuple[CausalEdge, ...]

    @classmethod
    def from_json(cls, value: str, citations: Tuple[str, ...]) -> "CausalChain":
        try:
            parsed = json.loads(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("provider output must be JSON") from exc
        if not isinstance(parsed, dict) or set(parsed) != {"edges"}:
            raise ValueError("provider output schema is closed")
        raw_edges = parsed["edges"]
        if not isinstance(raw_edges, list):
            raise ValueError("provider output edges must be a list")
        chain = cls(tuple(CausalEdge.from_mapping(edge) for edge in raw_edges))
        chain.validate(citations)
        return chain

    def validate(self, citations: Tuple[str, ...]) -> None:
        if not 3 <= len(self.edges) <= 8:
            raise ValueError("a causal chain must contain 3--8 edges")
        citation_set = set(citations)
        for edge in self.edges:
            _safe_token(edge.source, "edge.source")
            if edge.relation not in CHAIN_RELATIONS:
                raise ValueError("edge relation is outside the frozen vocabulary")
            if edge.axis not in MECHANISM_AXES:
                raise ValueError("edge axis is outside the frozen 23-axis vocabulary")
            if edge.direction not in (-1, 0, 1):
                raise ValueError("edge direction must be -1, 0 or 1")
            if not 0.0 <= edge.confidence <= 1.0:
                raise ValueError("edge confidence must be in [0, 1]")
            if edge.citation not in citation_set:
                raise ValueError("every edge must cite evidence already present in the input packet")

    def as_dict(self) -> Mapping[str, object]:
        return {
            "edges": [
                {
                    "axis": edge.axis,
                    "citation": edge.citation,
                    "confidence": edge.confidence,
                    "direction": edge.direction,
                    "relation": edge.relation,
                    "source": edge.source,
                }
                for edge in self.edges
            ]
        }


def canonical_fact(subject: str, relation: str, object_value: str, citation_index: int) -> str:
    """Build the only fact representation accepted at the provider Seam."""

    value = {
        "citation_index": citation_index,
        "object": object_value,
        "relation": relation,
        "subject": subject,
    }
    serialized = json.dumps(value, sort_keys=True, separators=(",", ":"))
    PublicFact.from_canonical_json(serialized, max(1, citation_index + 1))
    return serialized
