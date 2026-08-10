from __future__ import annotations

import argparse
from pathlib import Path

from experiment_core import ExperimentRegistry, RunContext


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
    return parser


def main() -> int:
    arguments = build_parser().parse_args()
    registry = ExperimentRegistry.default()
    if arguments.command == "list":
        for name in registry.names():
            print(name)
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
