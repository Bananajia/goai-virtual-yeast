"""Generate a non-mutating inventory of the historical experiment tree."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable


def infer_family(name: str) -> str:
    lowered = name.lower()
    rules = (
        (("strain", "genome", "cnv", "peter"), "strain_genome"),
        (("time", "latent", "dynamics", "trajectory"), "time_dynamics"),
        (("control", "threshold", "vehicle"), "control_calibration"),
        (("lincs", "rna"), "rna_transfer"),
        (("llm", "gpt", "qwen", "causal"), "llm_causal_chain"),
        (("active", "fewshot", "few-shot"), "active_calibration"),
        (("string", "target", "pathway", "reactome", "network", "goslim"), "knowledge_network"),
        (("jump", "pcba", "dutta", "cgm", "structure", "pubchem", "mosaic"), "public_chemistry"),
        (("ridge", "metadata", "baseline", "mean"), "statistical_baseline"),
        (("transformer", "mlp", "gru", "uncertainty", "multiobjective"), "learned_architecture"),
    )
    for tokens, family in rules:
        if any(token in lowered for token in tokens):
            return family
    return "other"


def experiment_directories(project_root: Path) -> Iterable[Path]:
    code_root = project_root / "code" / "experiments"
    for directory in sorted(code_root.iterdir()):
        if not directory.is_dir() or directory.name.startswith(".") or directory.name == "__pycache__":
            continue
        if directory.name == "official-dataset-local":
            for child in sorted(directory.iterdir()):
                if child.is_dir() and not child.name.startswith(".") and child.name != "__pycache__":
                    yield child
        else:
            yield directory
    for directory in sorted((project_root / "experiments").iterdir()):
        if directory.is_dir() and not directory.name.startswith(".") and directory.name != "__pycache__":
            yield directory


def build_inventory(project_root: Path, registry_path: Path) -> Dict[str, object]:
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    status_by_id = {
        record["experiment_id"]: record["status"] for record in registry["records"]
    }
    records = []
    for directory in experiment_directories(project_root):
        files = tuple(path for path in directory.rglob("*.py") if "__pycache__" not in path.parts)
        tests = tuple(path for path in files if path.name.startswith("test_") or "test" in path.parts)
        reports = tuple(
            path
            for path in directory.rglob("*")
            if path.is_file()
            and path.name in ("RESULTS.md", "VALIDATION.md", "VALIDATION_REPORT.md")
        )
        records.append(
            {
                "family": infer_family(directory.name),
                "path": directory.relative_to(project_root).as_posix(),
                "python_files": len(files),
                "report_files": len(reports),
                "status": status_by_id.get(directory.name, "UNREGISTERED_LEGACY"),
                "test_files": len(tests),
            }
        )
    families: Dict[str, int] = {}
    for record in records:
        families[record["family"]] = families.get(record["family"], 0) + 1
    return {
        "schema_version": "1.0",
        "generated_from": ["code/experiments", "experiments"],
        "experiment_directories": len(records),
        "python_files": sum(record["python_files"] for record in records),
        "test_files": sum(record["test_files"] for record in records),
        "families": dict(sorted(families.items())),
        "records": records,
    }


def main() -> int:
    research_root = Path(__file__).resolve().parents[1]
    project_root = research_root.parent
    payload = build_inventory(project_root, research_root / "evidence" / "registry.json")
    output = research_root / "evidence" / "code_inventory.json"
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
