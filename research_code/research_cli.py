from __future__ import annotations

import argparse
from pathlib import Path

from experiment_core import ExperimentRegistry, RunContext
from pipeline.competition_baseline import (
    predict_metadata_ridge,
    train_metadata_ridge,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Unified virtual-yeast research runner")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="list registered executable experiments")
    run = commands.add_parser("run", help="run one registered experiment")
    run.add_argument("name")
    run.add_argument(
        "--scope",
        required=True,
        choices=("synthetic", "public", "private_local", "aggregate-only"),
    )
    run.add_argument("--output", required=True, type=Path)
    run.add_argument("--data-root", type=Path)
    run.add_argument("--seed", type=int, default=0)

    train = commands.add_parser(
        "train-metadata-ridge",
        help="fit a live competition metadata Ridge artifact",
    )
    train.add_argument("--metadata", required=True, type=Path)
    train.add_argument("--proteome", required=True, type=Path)
    train.add_argument("--config", required=True, type=Path)
    train.add_argument("--artifact-dir", required=True, type=Path)
    train.add_argument("--seed", type=int, default=0)
    train.add_argument("--sample-id-column", default="sample_ID")

    predict = commands.add_parser(
        "predict-metadata-ridge",
        help="write a prediction.csv from a live metadata Ridge artifact",
    )
    predict.add_argument("--artifact-dir", required=True, type=Path)
    predict.add_argument("--test-metadata", required=True, type=Path)
    predict.add_argument("--submission-template", required=True, type=Path)
    predict.add_argument("--output", required=True, type=Path)
    predict.add_argument("--sample-id-column", default="sample_ID")
    return parser


def main() -> int:
    arguments = build_parser().parse_args()
    registry = ExperimentRegistry.default()
    if arguments.command == "list":
        for name in registry.names():
            print(name)
        return 0
    if arguments.command == "train-metadata-ridge":
        train_metadata_ridge(
            metadata_path=arguments.metadata,
            proteome_path=arguments.proteome,
            config_path=arguments.config,
            artifact_dir=arguments.artifact_dir,
            seed=arguments.seed,
            sample_id_column=arguments.sample_id_column,
        )
        print(f"metadata Ridge artifact: {arguments.artifact_dir}")
        return 0
    if arguments.command == "predict-metadata-ridge":
        predict_metadata_ridge(
            artifact_dir=arguments.artifact_dir,
            test_metadata_path=arguments.test_metadata,
            submission_template_path=arguments.submission_template,
            output_path=arguments.output,
            sample_id_column=arguments.sample_id_column,
        )
        print(f"prediction: {arguments.output}")
        return 0
    result = registry.run(
        arguments.name,
        RunContext(
            output_dir=arguments.output,
            data_scope=arguments.scope,
            data_root=arguments.data_root,
            seed=arguments.seed,
        ),
    )
    print(f"{result.name}: {result.status}")
    print(arguments.output / "REPORT.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
