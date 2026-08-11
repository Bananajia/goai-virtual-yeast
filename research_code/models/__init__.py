"""Small model Implementations behind one fit/predict Interface."""

from .baselines import MaskedMultiOutputRidge, ProteinMeanBaseline

__all__ = ["MaskedMultiOutputRidge", "ProteinMeanBaseline"]
