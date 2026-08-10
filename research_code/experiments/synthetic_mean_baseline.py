"""Small deterministic end-to-end experiment used to verify the framework."""

from __future__ import annotations

import numpy as np

from evaluation import EvaluationInput
from pipeline.controls import (
    ControlEstimand,
    MeasurementMatrix,
    MeasurementRole,
    MeasuredControlPairer,
)

from experiment_core.base import ExperimentResult, ExperimentStatus, RunContext
from experiment_core.runner import ExperimentRunner


class SyntheticMeanBaseline:
    name = "synthetic_mean_baseline"
    description = "Predict every condition with the training protein mean."

    def run(self, context: RunContext) -> ExperimentResult:
        if context.data_scope != "synthetic":
            raise ValueError("synthetic_mean_baseline requires data_scope=synthetic")
        generator = np.random.default_rng(context.seed)
        protein_baseline = np.asarray([8.0, 12.0, 16.0, 20.0])
        control = np.tile(protein_baseline, (6, 1))
        response = generator.normal(0.0, 1.0, size=(6, 4))
        truth = control + response
        prediction = np.tile(np.nanmean(truth[:3], axis=0), (6, 1))
        paired_response = MeasuredControlPairer().estimate(
            MeasurementMatrix(
                truth, tuple(range(6)), tuple(range(4)), MeasurementRole.ENDPOINT
            ),
            MeasurementMatrix(
                control,
                tuple(range(6)),
                tuple(range(4)),
                MeasurementRole.MEASURED_CONTROL,
            ),
            estimand=ControlEstimand.PAIRED,
        )
        return ExperimentRunner().complete_response_experiment(
            name=self.name,
            context=context,
            evaluation_input=EvaluationInput(
                truth_endpoint=truth,
                prediction_endpoint=prediction,
                paired_response=paired_response,
                context_groups=("c1", "c1", "c2", "c2", "c3", "c3"),
                drug_groups=("d1", "d1", "d2", "d2", "d3", "d3"),
            ),
            notes=("Synthetic fixture only; no competition data were read.",),
            status=ExperimentStatus.COMPLETED.value,
        )
