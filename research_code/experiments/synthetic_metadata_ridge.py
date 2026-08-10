"""Experiment: end-to-end condition-aware Ridge on a deterministic fixture."""

from __future__ import annotations

import numpy as np

from evaluation import EvaluationInput
from experiment_core.base import ExperimentResult, ExperimentStatus, RunContext
from experiment_core.runner import ExperimentRunner
from models import MaskedMultiOutputRidge
from pipeline.controls import (
    ControlEstimand,
    MeasurementMatrix,
    MeasurementRole,
    MeasuredControlPairer,
)


class SyntheticMetadataRidge:
    name = "synthetic_metadata_ridge"
    description = "Recover a known condition-to-proteome map with masked Ridge."

    def run(self, context: RunContext) -> ExperimentResult:
        if context.data_scope != "synthetic":
            raise ValueError("synthetic_metadata_ridge requires data_scope=synthetic")
        generator = np.random.default_rng(context.seed)
        features = generator.normal(size=(36, 3))
        weights = np.asarray(
            [
                [1.2, -0.8, 0.4, 1.5, -1.0, 0.7, 0.3, -0.5],
                [-0.5, 1.1, 0.8, -0.2, 0.9, -1.3, 0.6, 0.4],
                [0.3, 0.2, -1.0, 0.7, 0.5, 0.8, -0.9, 1.2],
            ]
        )
        control = np.tile(np.linspace(8.0, 15.0, 8), (36, 1))
        endpoint = control + features @ weights + generator.normal(0.0, 0.003, size=(36, 8))
        fit = np.arange(24)
        evaluate = np.arange(24, 36)
        model = MaskedMultiOutputRidge(alpha=1e-6).fit(features[fit], endpoint[fit])
        prediction = model.predict(features[evaluate])
        evaluation_endpoint = endpoint[evaluate]
        evaluation_control = control[evaluate]
        paired_response = MeasuredControlPairer().estimate(
            MeasurementMatrix(
                evaluation_endpoint,
                tuple(range(len(evaluate))),
                tuple(range(endpoint.shape[1])),
                MeasurementRole.ENDPOINT,
            ),
            MeasurementMatrix(
                evaluation_control,
                tuple(range(len(evaluate))),
                tuple(range(endpoint.shape[1])),
                MeasurementRole.MEASURED_CONTROL,
            ),
            estimand=ControlEstimand.PAIRED,
        )
        return ExperimentRunner().complete_response_experiment(
            name=self.name,
            context=context,
            evaluation_input=EvaluationInput(
                truth_endpoint=evaluation_endpoint,
                prediction_endpoint=prediction,
                paired_response=paired_response,
                context_groups=tuple(f"context-{index // 2}" for index in range(12)),
                drug_groups=tuple(f"drug-{index % 3}" for index in range(12)),
            ),
            status=ExperimentStatus.COMPLETED.value,
            notes=("Deterministic synthetic signal-recovery fixture.",),
        )
