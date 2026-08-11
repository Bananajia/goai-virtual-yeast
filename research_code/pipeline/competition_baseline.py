"""Release-safe live training and inference for the metadata Ridge baseline."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from typing import Any, Mapping

import numpy as np
import pandas as pd

from models import MaskedMultiOutputRidge

from .dataset import DataScope, align_dataset_frames, require_training_bundle
from .metadata import MetadataEncoder, MetadataField
from .preprocessing import (
    Log2ProteomeTransformer,
    MissingnessFilter,
    ProteinOutputContract,
)
from .submission import SubmissionContract


_SCHEMA_VERSION = "1.0"
_MODEL_FILE = "model.npz"
_MANIFEST_FILE = "manifest.json"


def train_metadata_ridge(
    *,
    metadata_path: Path,
    proteome_path: Path,
    config_path: Path,
    artifact_dir: Path,
    seed: int = 0,
    sample_id_column: str = "sample_ID",
) -> Mapping[str, Any]:
    """Fit the competition metadata Ridge and atomically publish its artifact."""

    metadata_path = Path(metadata_path)
    proteome_path = Path(proteome_path)
    config_path = Path(config_path)
    artifact_dir = Path(artifact_dir)
    if artifact_dir.exists():
        raise FileExistsError(f"artifact directory already exists: {artifact_dir}")

    config = _load_config(config_path)
    metadata = pd.read_csv(metadata_path)
    proteome = pd.read_csv(proteome_path)
    bundle = align_dataset_frames(
        metadata,
        proteome,
        sample_id_column=sample_id_column,
        scope=DataScope.PRIVATE_LOCAL,
    )
    require_training_bundle(bundle)
    _require_positive_raw_intensities(bundle.endpoint)

    policy = config["missingness_policy"]
    missingness = MissingnessFilter(
        max_missing_fraction=float(policy["max_missing_fraction"]),
        include_boundary=False,
    ).fit_raw(bundle.endpoint)
    transformed = Log2ProteomeTransformer().transform(bundle.endpoint)
    modeled_targets = missingness.transform(transformed)
    finite_train = transformed[np.isfinite(transformed)]
    if not finite_train.size:
        raise ValueError("training proteome has no finite positive intensity")
    fit_global_median = float(np.median(finite_train))

    fields = _metadata_fields(config)
    encoder = MetadataEncoder(fields)
    features = encoder.fit_transform(bundle.metadata)
    model = MaskedMultiOutputRidge(alpha=float(config["alpha"]))
    model.fit(features, modeled_targets)
    output_contract = ProteinOutputContract.from_training(
        transformed,
        missingness.keep_mask,
        unobserved_fallback=fit_global_median,
    )

    artifact_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(
        tempfile.mkdtemp(
            prefix=f".{artifact_dir.name}.staging-",
            dir=artifact_dir.parent,
        )
    )
    try:
        model_path = staging / _MODEL_FILE
        np.savez_compressed(
            model_path,
            coef=np.asarray(model.coef_, dtype=np.float64),
            modeled_mask=np.asarray(output_contract.modeled_mask, dtype=bool),
            fallback=np.asarray(output_contract.fallback, dtype=np.float64),
        )
        manifest = {
            "schema_version": _SCHEMA_VERSION,
            "artifact_type": "competition_metadata_ridge",
            "seed": int(seed),
            "model": {
                "name": "masked_multi_output_ridge",
                "alpha": float(config["alpha"]),
                "coefficient_shape": list(np.asarray(model.coef_).shape),
            },
            "preprocessing": {
                "input_scale": "raw_positive_intensity",
                "output_scale": "log2",
                "missingness_fit_scope": "split_final=train",
                "max_missing_fraction": float(policy["max_missing_fraction"]),
                "remove_when": ">=threshold",
                "nonpositive_finite_policy": "fail_closed",
                "unobserved_fallback_policy": policy["unobserved_fallback_policy"],
                "fit_global_median_log2": fit_global_median,
            },
            "metadata_encoder": _encoder_manifest(encoder),
            "output_contract": {
                "sample_id_column": sample_id_column,
                "protein_ids": list(bundle.protein_ids),
                "full_width": output_contract.full_width,
                "modeled_width": output_contract.modeled_width,
            },
            "provenance": {
                "data_scope": DataScope.PRIVATE_LOCAL.value,
                "fit_role": "split_final=train",
                "train_rows": bundle.n_conditions,
                "source_sha256": {
                    "metadata": _sha256(metadata_path),
                    "proteome": _sha256(proteome_path),
                    "config": _sha256(config_path),
                },
                "implementation": "competition_metadata_ridge_v1",
                "python_version": sys.version.split()[0],
                "numpy_version": np.__version__,
                "pandas_version": pd.__version__,
            },
            "files": {
                "model": _MODEL_FILE,
                "model_sha256": _sha256(model_path),
            },
        }
        (staging / _MANIFEST_FILE).write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        _load_artifact(staging)
        os.replace(staging, artifact_dir)
        return manifest
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        raise


def predict_metadata_ridge(
    *,
    artifact_dir: Path,
    test_metadata_path: Path,
    submission_template_path: Path,
    output_path: Path,
    sample_id_column: str = "sample_ID",
) -> pd.DataFrame:
    """Load a frozen artifact and atomically write a validated prediction CSV."""

    manifest, arrays = _load_artifact(Path(artifact_dir))
    contract_raw = manifest["output_contract"]
    if sample_id_column != contract_raw["sample_id_column"]:
        raise ValueError("sample ID column does not match the training artifact")

    metadata = pd.read_csv(test_metadata_path)
    template = pd.read_csv(submission_template_path)
    if sample_id_column not in metadata or sample_id_column not in template:
        raise ValueError(f"test metadata and template must contain {sample_id_column}")
    if metadata[sample_id_column].isna().any() or not metadata[sample_id_column].is_unique:
        raise ValueError("test metadata sample IDs must be non-missing and unique")
    template_ids = tuple(template[sample_id_column].tolist())
    if not template_ids or len(set(template_ids)) != len(template_ids):
        raise ValueError("submission template sample IDs must be non-empty and unique")
    if set(metadata[sample_id_column].tolist()) != set(template_ids):
        raise ValueError("test metadata and submission template sample IDs must match")
    metadata = metadata.set_index(sample_id_column).loc[list(template_ids)].reset_index()

    artifact_protein_ids = tuple(contract_raw["protein_ids"])
    template_protein_ids = tuple(
        column for column in template.columns if column != sample_id_column
    )
    if not template_protein_ids or len(set(template_protein_ids)) != len(template_protein_ids):
        raise ValueError("submission template protein columns must be non-empty and unique")
    unknown = set(template_protein_ids) - set(artifact_protein_ids)
    if unknown:
        raise ValueError("submission template contains proteins absent from the artifact")

    encoder = _restore_encoder(manifest["metadata_encoder"])
    features = encoder.transform(metadata)
    model = MaskedMultiOutputRidge(alpha=float(manifest["model"]["alpha"]))
    model.coef_ = np.asarray(arrays["coef"], dtype=np.float64)
    modeled = model.predict(features)
    output_contract = ProteinOutputContract(
        modeled_mask=np.asarray(arrays["modeled_mask"], dtype=bool),
        fallback=np.asarray(arrays["fallback"], dtype=np.float64),
    )
    restored = output_contract.restore(modeled)
    artifact_index = {
        protein_id: index for index, protein_id in enumerate(artifact_protein_ids)
    }
    selected = restored[
        :, [artifact_index[protein_id] for protein_id in template_protein_ids]
    ]
    prediction = pd.DataFrame(selected, columns=list(template_protein_ids))
    prediction.insert(0, sample_id_column, list(template_ids))
    prediction = SubmissionContract(
        sample_ids=template_ids,
        protein_ids=template_protein_ids,
        sample_id_column=sample_id_column,
        output_scale="log2",
    ).validate(prediction, declared_scale="log2")
    _atomic_write_csv(prediction, Path(output_path))
    return prediction


def _load_config(path: Path) -> Mapping[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw.get("schema_version") != _SCHEMA_VERSION:
        raise ValueError("unsupported metadata Ridge config schema")
    if raw.get("model") != "masked_multi_output_ridge":
        raise ValueError("config model must be masked_multi_output_ridge")
    if float(raw.get("alpha", -1)) < 0:
        raise ValueError("config alpha must be non-negative")
    policy = raw.get("missingness_policy")
    if not isinstance(policy, dict) or policy.get("fit_only") is not True:
        raise ValueError("missingness policy must be fit-only")
    threshold = float(policy.get("max_missing_fraction", -1))
    if not 0 <= threshold <= 1 or policy.get("remove_when") != ">=0.8":
        raise ValueError("missingness policy must remove proteins at >=0.8")
    if policy.get("unobserved_fallback_policy") != "fit_global_median":
        raise ValueError("unobserved fallback policy must be fit_global_median")
    return raw


def _metadata_fields(config: Mapping[str, Any]) -> tuple[MetadataField, ...]:
    fields = [MetadataField(str(name), "categorical") for name in config.get("categorical", [])]
    fields.extend(
        MetadataField(str(name), str(transform))
        for name, transform in config.get("numeric", {}).items()
    )
    fields.extend(
        MetadataField(str(name), "categorical")
        for name in config.get("technical_covariates", [])
    )
    if not fields or len({field.name for field in fields}) != len(fields):
        raise ValueError("metadata fields must be non-empty and unique")
    return tuple(fields)


def _require_positive_raw_intensities(values: np.ndarray) -> None:
    values = np.asarray(values, dtype=np.float64)
    invalid = np.isfinite(values) & (values <= 0)
    count = int(np.sum(invalid))
    if count:
        raise ValueError(f"raw proteome contains {count} finite non-positive intensities")


def _encoder_manifest(encoder: MetadataEncoder) -> Mapping[str, Any]:
    return {
        "fields": [
            {"name": field.name, "transform": field.transform}
            for field in encoder.fields
        ],
        "feature_names": list(encoder.feature_names),
        "categories": {
            name: list(values) for name, values in encoder._categories.items()
        },
        "numeric_stats": {
            name: list(values) for name, values in encoder._numeric_stats.items()
        },
    }


def _restore_encoder(raw: Mapping[str, Any]) -> MetadataEncoder:
    encoder = MetadataEncoder(
        tuple(MetadataField(item["name"], item["transform"]) for item in raw["fields"])
    )
    encoder.feature_names = tuple(raw["feature_names"])
    encoder._categories = {
        str(name): tuple(str(value) for value in values)
        for name, values in raw["categories"].items()
    }
    encoder._numeric_stats = {
        str(name): (float(values[0]), float(values[1]))
        for name, values in raw["numeric_stats"].items()
    }
    return encoder


def _load_artifact(path: Path) -> tuple[Mapping[str, Any], Mapping[str, np.ndarray]]:
    manifest_path = path / _MANIFEST_FILE
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != _SCHEMA_VERSION:
        raise ValueError("unsupported competition artifact schema")
    if manifest.get("artifact_type") != "competition_metadata_ridge":
        raise ValueError("unexpected competition artifact type")
    if manifest.get("model", {}).get("name") != "masked_multi_output_ridge":
        raise ValueError("unexpected competition artifact model")
    if manifest.get("files", {}).get("model") != _MODEL_FILE:
        raise ValueError("competition artifact model filename is not allowed")
    model_path = path / manifest["files"]["model"]
    if _sha256(model_path) != manifest["files"]["model_sha256"]:
        raise ValueError("competition artifact model hash mismatch")
    with np.load(model_path, allow_pickle=False) as loaded:
        arrays = {name: loaded[name].copy() for name in loaded.files}
    required = {"coef", "modeled_mask", "fallback"}
    if set(arrays) != required:
        raise ValueError("competition artifact model arrays are incomplete")
    coef = np.asarray(arrays["coef"], dtype=np.float64)
    mask = np.asarray(arrays["modeled_mask"], dtype=bool)
    fallback = np.asarray(arrays["fallback"], dtype=np.float64)
    expected_shape = tuple(manifest["model"]["coefficient_shape"])
    if coef.shape != expected_shape or coef.ndim != 2 or not np.isfinite(coef).all():
        raise ValueError("competition artifact coefficients are invalid")
    if mask.shape != fallback.shape or mask.ndim != 1 or not np.isfinite(fallback).all():
        raise ValueError("competition artifact output contract is invalid")
    if len(mask) != int(manifest["output_contract"]["full_width"]):
        raise ValueError("competition artifact full width is inconsistent")
    if int(np.sum(mask)) != int(manifest["output_contract"]["modeled_width"]):
        raise ValueError("competition artifact modeled width is inconsistent")
    if coef.shape[1] != int(np.sum(mask)):
        raise ValueError("competition artifact coefficient/output widths disagree")
    protein_ids = tuple(manifest["output_contract"]["protein_ids"])
    if len(protein_ids) != len(mask) or len(set(protein_ids)) != len(protein_ids):
        raise ValueError("competition artifact protein IDs are invalid")
    encoder = _restore_encoder(manifest["metadata_encoder"])
    if len(encoder.feature_names) + 1 != coef.shape[0]:
        raise ValueError("competition artifact encoder/model dimensions disagree")
    return manifest, arrays


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _atomic_write_csv(frame: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output_path.name}.staging-",
        suffix=".csv",
        dir=output_path.parent,
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        frame.to_csv(temporary, index=False)
        os.replace(temporary, output_path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
