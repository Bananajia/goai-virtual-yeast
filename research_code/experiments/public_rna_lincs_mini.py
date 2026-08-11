"""Experiment: public RNA mechanism-axis smoke with an offline causal provider."""

from __future__ import annotations

from experiment_core.base import ExperimentResult, ExperimentStatus, RunContext
from future_experiments.public_rna_lincs_mini import run_offline_smoke


class PublicRnaLincsMiniExperiment:
    name = "public_rna_lincs_mini"
    description = "Six public L1000FWD signatures and an offline causal-chain fixture."

    def run(self, context: RunContext) -> ExperimentResult:
        if context.data_scope != "public":
            raise ValueError("public_rna_lincs_mini requires data_scope=public")
        payload = run_offline_smoke(context.output_dir)
        return ExperimentResult(
            name=self.name,
            status=ExperimentStatus.PUBLIC_ONLY.value,
            metrics=payload["metrics"],
            counts=payload["counts"],
            contract=payload["contract"],
            provenance={"data_scope": context.data_scope, "seed": context.seed},
            notes=(payload["interpretation"],),
        )
