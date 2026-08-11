"""Aggregate-only evaluation of public causal chains against withheld RNA axes."""

from __future__ import annotations

from typing import Dict, Mapping, Sequence, Tuple

from evaluation import evaluate_axis_predictions
from future_experiments.public_causal_chain import CausalChain, MECHANISM_AXES

from .axis_truth import axis_truth
from .fixture import FrozenL1000Fixture


def chain_vector(chain: CausalChain) -> Tuple[float, ...]:
    numerator = {axis: 0.0 for axis in MECHANISM_AXES}
    denominator = {axis: 0.0 for axis in MECHANISM_AXES}
    for edge in chain.edges:
        numerator[edge.axis] += edge.direction * edge.confidence
        denominator[edge.axis] += edge.confidence
    return tuple(
        0.0 if denominator[axis] == 0 else numerator[axis] / denominator[axis]
        for axis in MECHANISM_AXES
    )


def evaluate_chains(
    fixture: FrozenL1000Fixture,
    chains_by_signature: Mapping[str, CausalChain],
) -> Mapping[str, object]:
    if set(chains_by_signature) != set(fixture.truth_by_signature):
        raise ValueError("prediction and truth signature IDs must match exactly")
    truth_rows = []
    prediction_rows = []
    truth_support = []
    edge_count = 0
    for query in fixture.queries:
        truth, support = axis_truth(fixture.truth_by_signature[query.signature_id])
        prediction = chain_vector(chains_by_signature[query.signature_id])
        truth_rows.append(truth)
        prediction_rows.append(prediction)
        truth_support.extend(support)
        edge_count += len(chains_by_signature[query.signature_id].edges)

    return evaluate_axis_predictions(
        truth_rows,
        prediction_rows,
        causal_edges=edge_count,
        marker_hits=sum(truth_support),
    )
