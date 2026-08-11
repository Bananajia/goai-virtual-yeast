"""Frozen human-gene marker bridge for deriving 23-axis RNA truth."""

from __future__ import annotations

from typing import Dict, FrozenSet, Mapping, Tuple

from future_experiments.public_causal_chain import MECHANISM_AXES

from .fixture import SignatureTruth


AXIS_MARKERS: Mapping[str, FrozenSet[str]] = {
    "tor_nutrient_signaling": frozenset(("MTOR", "RPTOR", "RICTOR", "EIF4EBP1", "RPS6KB1", "DDIT4", "AKT1", "TSC1", "TSC2", "RRAGA", "RRAGB", "DEPTOR")),
    "translation_ribosome": frozenset(("EIF1AX", "EIF3F", "EIF4B", "EIF4A3", "EEF1A1", "RPL27A", "RPL37A", "RPS6", "NPM1", "IARS", "EPRS")),
    "proteasome_protein_degradation": frozenset(("PSMA1", "PSMB5", "PSMC1", "PSMD1", "UBB", "UBC", "VCP", "SQSTM1", "BAG2", "STUB1")),
    "chaperone_proteostasis": frozenset(("HSPA2", "HSPA5", "HSPA6", "HSPA8", "HSPA9", "HSP90AA1", "HSP90AB1", "CANX", "CALR", "HYOU1", "EDEM1", "DDIT3", "MANF")),
    "ergosterol_membrane_sterol": frozenset(("HMGCR", "SQLE", "SREBF2", "LDLR", "ACAT1", "IDI1", "TM7SF2", "ABCA1", "OSBPL3", "OSBPL10")),
    "cell_wall_biosynthesis": frozenset(("COL1A1", "COL11A1", "FN1", "DCN", "MMP2", "MMP9", "ITGA4", "ITGA6", "SDC1", "SDC4")),
    "membrane_ion_homeostasis": frozenset(("ATP2B4", "CALM1", "CALM3", "SLC12A2", "SLC25A14", "SLC25A24", "KCNMA1", "KCNAB1", "ATP9A", "MAGT1")),
    "mitochondrial_respiration": frozenset(("NDUFB7", "ATP5G1", "ATP5L", "ATPIF1", "SCO2", "IDH2", "GOT2", "POLG2", "TFAM", "OXA1L", "SLC25A6")),
    "glycolysis_fermentation": frozenset(("HK2", "TPI1", "PCK1", "PCK2", "FBP1", "PGAM1", "GAPDH", "LDHA", "ENO1", "G6PD", "ALDOC")),
    "amino_acid_biosynthesis": frozenset(("PHGDH", "SHMT2", "ASNS", "PSAT1", "GLUL", "GOT2", "IARS", "EPRS", "CNDP2", "SLC38A1")),
    "nucleotide_metabolism": frozenset(("DUT", "IMPDH2", "CTPS", "TYMS", "RPIA", "MTHFD2", "NME1", "GMPS", "CAD", "PRPS1")),
    "dna_replication_repair": frozenset(("GADD45A", "GADD45B", "RAD9A", "RAD23B", "RPA1", "BRCA1", "PARP1", "TP53BP2", "H2AFX", "CDC25A")),
    "transcription_rna_processing": frozenset(("POLR2I", "POLR2K", "EXOSC4", "RBM15B", "RBM25", "SRSF7", "SRSF10", "SRSF11", "DDX21", "DDX24")),
    "chromatin_epigenetic": frozenset(("HIST1H4C", "HIST1H4J", "HAT1", "HDAC9", "KDM4B", "KDM5A", "KDM5B", "SMARCC1", "SMARCD3", "BRD2")),
    "cell_cycle": frozenset(("PLK1", "PLK3", "ESPL1", "CENPA", "CENPE", "CENPF", "KIF2C", "TPX2", "CDC20", "CDC25A", "CDC25B", "CDK2")),
    "microtubule_spindle": frozenset(("TUBB", "TUBB6", "KIF2C", "TPX2", "CENPE", "CENPF", "DLGAP5", "CLIP3", "NUSAP1", "PLK1")),
    "actin_cytoskeleton": frozenset(("ACTR3", "ACTG2", "ACTC1", "RHOA", "RHOB", "ZYX", "WDR1", "CALD1", "CDC42SE1", "MICAL2")),
    "oxidative_stress_redox": frozenset(("NQO1", "NFE2L2", "HMOX1", "TXN", "SOD2", "GLRX", "GLRX2", "GSTA4", "CYBRD1", "MAFF")),
    "osmotic_stress": frozenset(("NFAT5", "AQP1", "AQP3", "MAPK14", "SGK1", "SLC12A2", "SLC25A24", "KCTD12", "TXNIP", "GPD1L")),
    "autophagy_vacuole": frozenset(("WIPI1", "ATG5", "ATG7", "BECN1", "SQSTM1", "MAP1LC3B", "SH3GLB1", "CLN5", "VPS28", "LAMP3")),
    "kinase_phosphatase_signaling": frozenset(("STK10", "MAP3K5", "MAP2K3", "PIK3CD", "PTP4A1", "PTP4A2", "PTP4A3", "PPP2R2A", "DUSP22", "CSNK1E")),
    "metal_homeostasis": frozenset(("MT1M", "TFRC", "SLC39A14", "CYBRD1", "HMOX1", "ABCG2", "ATP7A", "SLC31A1", "FTH1", "FTL")),
    "general_antimicrobial_toxicity": frozenset(("PMAIP1", "CASP10", "PERP", "DDIT3", "GADD45A", "GADD45B", "PTGS2", "TNFSF10", "SERPINB2", "IL6ST")),
}

if tuple(AXIS_MARKERS) != MECHANISM_AXES:
    raise RuntimeError("RNA marker vocabulary must align exactly to the frozen mechanism axes")


def axis_truth(truth: SignatureTruth) -> Tuple[Tuple[float, ...], Tuple[int, ...]]:
    """Return signed marker balance and support without exposing gene lists."""

    up = set(truth.up_genes)
    down = set(truth.down_genes)
    scores = []
    support = []
    for axis in MECHANISM_AXES:
        markers = AXIS_MARKERS[axis]
        up_count = len(up & markers)
        down_count = len(down & markers)
        count = up_count + down_count
        scores.append(0.0 if count == 0 else (up_count - down_count) / float(count))
        support.append(count)
    return tuple(scores), tuple(support)
