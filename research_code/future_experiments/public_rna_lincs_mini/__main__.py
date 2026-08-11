from __future__ import annotations

import argparse
from pathlib import Path

from future_experiments.public_causal_chain import OllamaCausalChainProvider

from .experiment import probe_ollama_runtime, run_local_ollama_pilot, run_offline_smoke


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the public-only L1000FWD mini-pilot")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--mode",
        choices=("offline-fixture", "local-ollama"),
        default="offline-fixture",
    )
    parser.add_argument("--model", default="qwen3:8b")
    parser.add_argument("--case-limit", type=int, choices=range(1, 7), default=1)
    args = parser.parse_args()
    if args.mode == "offline-fixture":
        run_offline_smoke(args.output)
    else:
        identity = probe_ollama_runtime(args.model)
        run_local_ollama_pilot(
            args.output,
            provider=OllamaCausalChainProvider(model=identity.model),
            runtime_identity=identity,
            case_limit=args.case_limit,
        )
    print(args.output / "REPORT.md")


if __name__ == "__main__":
    main()
