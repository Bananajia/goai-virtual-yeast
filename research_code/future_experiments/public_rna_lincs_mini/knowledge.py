"""Frozen public mechanism packets and deterministic smoke chains."""

from __future__ import annotations

from typing import Dict, Mapping

from future_experiments import EvidenceScope, PublicEvidencePacket
from future_experiments.public_causal_chain import (
    CausalChain,
    CausalEdge,
    canonical_fact,
)

from .fixture import SignatureQuery


_KNOWLEDGE = {
    "Rapamycin": ("rapamycin-FKBP12", "inhibits", "MTOR", "https://pubchem.ncbi.nlm.nih.gov/compound/Rapamycin"),
    "MG-132": ("MG-132", "inhibits", "proteasome", "https://pubchem.ncbi.nlm.nih.gov/compound/MG-132"),
    "THAPSIGARGIN": ("thapsigargin", "inhibits", "SERCA", "https://pubchem.ncbi.nlm.nih.gov/compound/Thapsigargin"),
    "oligomycin c": ("oligomycin-C", "inhibits", "ATP-synthase", "https://pubchem.ncbi.nlm.nih.gov/compound/Oligomycin-C"),
    "Etoposide": ("etoposide", "inhibits", "TOP2", "https://pubchem.ncbi.nlm.nih.gov/compound/Etoposide"),
    "NOCODAZOLE": ("nocodazole", "binds", "tubulin", "https://pubchem.ncbi.nlm.nih.gov/compound/Nocodazole"),
}


def packet_for_query(query: SignatureQuery) -> PublicEvidencePacket:
    try:
        subject, relation, object_value, citation = _KNOWLEDGE[query.perturbagen]
    except KeyError as exc:
        raise KeyError("no frozen public evidence for %s" % query.perturbagen) from exc
    return PublicEvidencePacket(
        entity=query.perturbagen,
        scope=EvidenceScope.PUBLIC,
        facts=(canonical_fact(subject, relation, object_value, 0),),
        citations=(citation,),
    )


def fixture_chains() -> Mapping[str, CausalChain]:
    def chain(name: str, rows):
        citation = _KNOWLEDGE[name][3]
        return CausalChain(
            tuple(
                CausalEdge(source, relation, axis, direction, confidence, citation)
                for source, relation, axis, direction, confidence in rows
            )
        )

    return {
        "Rapamycin": chain(
            "Rapamycin",
            (
                ("MTOR", "reduces", "tor_nutrient_signaling", -1, 0.95),
                ("MTOR", "reduces", "translation_ribosome", -1, 0.80),
                ("MTOR", "increases", "autophagy_vacuole", 1, 0.75),
            ),
        ),
        "MG-132": chain(
            "MG-132",
            (
                ("proteasome", "inhibits", "proteasome_protein_degradation", -1, 0.95),
                ("proteotoxic-stress", "induces", "chaperone_proteostasis", 1, 0.85),
                ("proteotoxic-stress", "increases", "oxidative_stress_redox", 1, 0.65),
            ),
        ),
        "THAPSIGARGIN": chain(
            "THAPSIGARGIN",
            (
                ("SERCA", "reduces", "membrane_ion_homeostasis", -1, 0.95),
                ("ER-stress", "induces", "chaperone_proteostasis", 1, 0.90),
                ("ER-stress", "increases", "general_antimicrobial_toxicity", 1, 0.65),
            ),
        ),
        "oligomycin c": chain(
            "oligomycin c",
            (
                ("ATP-synthase", "reduces", "mitochondrial_respiration", -1, 0.95),
                ("energy-deficit", "increases", "glycolysis_fermentation", 1, 0.75),
                ("energy-deficit", "increases", "general_antimicrobial_toxicity", 1, 0.55),
            ),
        ),
        "Etoposide": chain(
            "Etoposide",
            (
                ("TOP2", "induces", "dna_replication_repair", 1, 0.95),
                ("DNA-damage", "reduces", "cell_cycle", -1, 0.90),
                ("DNA-damage", "increases", "general_antimicrobial_toxicity", 1, 0.75),
            ),
        ),
        "NOCODAZOLE": chain(
            "NOCODAZOLE",
            (
                ("tubulin", "disrupts", "microtubule_spindle", -1, 0.95),
                ("spindle-checkpoint", "reduces", "cell_cycle", -1, 0.90),
                ("cytoskeletal-stress", "increases", "general_antimicrobial_toxicity", 1, 0.55),
            ),
        ),
    }
