"""Common experiment completion path: evaluate once, persist aggregates once."""

from __future__ import annotations

from typing import Sequence

from evaluation import EvaluationInput, EvaluationSuite
from reporting import AggregateReportWriter

from .base import ExperimentResult, RunContext


class ExperimentRunner:
    def __init__(
        self,
        evaluator: EvaluationSuite = None,
        report_writer: AggregateReportWriter = None,
    ) -> None:
        self.evaluator = evaluator or EvaluationSuite()
        self.report_writer = report_writer or AggregateReportWriter()

    def complete_response_experiment(
        self,
        *,
        name: str,
        context: RunContext,
        evaluation_input: EvaluationInput,
        status: str = "completed",
        notes: Sequence[str] = (),
    ) -> ExperimentResult:
        evaluation = self.evaluator.evaluate(evaluation_input)
        result = ExperimentResult(
            name=name,
            status=status,
            metrics=evaluation.metrics,
            counts=evaluation.counts,
            contract=evaluation.contract,
            provenance={"data_scope": context.data_scope, "seed": context.seed},
            notes=tuple(notes),
        )
        self.report_writer.write(result, context.output_dir)
        return result
