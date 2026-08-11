from __future__ import annotations

import json
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLI = PROJECT_ROOT / "research_cli.py"


def write_config(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "model": "masked_multi_output_ridge",
                "alpha": 1.0,
                "categorical": ["strain", "chemical", "medium", "time_unit"],
                "numeric": {"temperature": "standardize", "time": "log1p"},
                "technical_covariates": ["data_source", "instrument"],
                "missingness_policy": {
                    "fit_only": True,
                    "max_missing_fraction": 0.8,
                    "remove_when": ">=0.8",
                    "unobserved_fallback_policy": "fit_global_median",
                },
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )


class CompetitionMetadataRidgeCliTest(unittest.TestCase):
    def test_train_then_predict_writes_template_aligned_finite_submission(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            metadata_path = root / "train_metadata.csv"
            proteome_path = root / "train_proteome.csv"
            config_path = root / "config.json"
            artifact_dir = root / "artifact"
            test_metadata_path = root / "test_metadata.csv"
            template_path = root / "submission_template.csv"
            output_path = root / "prediction.csv"

            pd.DataFrame(
                {
                    "sample_ID": ["tr1", "tr2", "tr3", "tr4", "tr5"],
                    "split_final": ["train"] * 5,
                    "strain": ["S1", "S1", "S2", "S2", "S1"],
                    "chemical": ["D1", "D2", "D1", "D2", "D1"],
                    "medium": ["M1"] * 5,
                    "time_unit": ["h"] * 5,
                    "temperature": [30.0] * 5,
                    "time": [1.0, 2.0, 1.0, 2.0, 3.0],
                    "data_source": ["source-a"] * 5,
                    "instrument": ["inst-a"] * 5,
                }
            ).to_csv(metadata_path, index=False)
            pd.DataFrame(
                {
                    "sample_ID": ["tr3", "tr1", "tr5", "tr2", "tr4"],
                    "P1": [16.0, 4.0, 32.0, 8.0, 16.0],
                    "P2": [8.0, 2.0, 16.0, 4.0, 8.0],
                    "P3": [np.nan, 8.0, np.nan, np.nan, np.nan],
                }
            ).to_csv(proteome_path, index=False)
            write_config(config_path)

            train = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "train-metadata-ridge",
                    "--metadata",
                    str(metadata_path),
                    "--proteome",
                    str(proteome_path),
                    "--config",
                    str(config_path),
                    "--artifact-dir",
                    str(artifact_dir),
                    "--seed",
                    "17",
                ],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(train.returncode, 0, train.stderr)
            self.assertTrue((artifact_dir / "manifest.json").is_file())
            self.assertTrue((artifact_dir / "model.npz").is_file())

            pd.DataFrame(
                {
                    "sample_ID": ["te1", "te2"],
                    "strain": ["S1", "S2"],
                    "chemical": ["UNSEEN", "D1"],
                    "medium": ["M1", "M1"],
                    "time_unit": ["h", "h"],
                    "temperature": [30.0, 30.0],
                    "time": [4.0, 5.0],
                    "data_source": ["source-a", "source-a"],
                    "instrument": ["inst-a", "inst-a"],
                }
            ).to_csv(test_metadata_path, index=False)
            pd.DataFrame(
                {
                    "sample_ID": ["te2", "te1"],
                    "P1": [0.0, 0.0],
                    "P2": [0.0, 0.0],
                    "P3": [0.0, 0.0],
                }
            ).to_csv(template_path, index=False)

            predict = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "predict-metadata-ridge",
                    "--artifact-dir",
                    str(artifact_dir),
                    "--test-metadata",
                    str(test_metadata_path),
                    "--submission-template",
                    str(template_path),
                    "--output",
                    str(output_path),
                ],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(predict.returncode, 0, predict.stderr)
            prediction = pd.read_csv(output_path)
            self.assertEqual(tuple(prediction.columns), ("sample_ID", "P1", "P2", "P3"))
            self.assertEqual(tuple(prediction["sample_ID"]), ("te2", "te1"))
            self.assertTrue(np.isfinite(prediction[["P1", "P2", "P3"]]).all().all())
            np.testing.assert_allclose(prediction["P3"], np.array([3.0, 3.0]))

    def test_training_rejects_any_non_train_label_without_publishing_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            metadata_path = root / "metadata.csv"
            proteome_path = root / "proteome.csv"
            config_path = root / "config.json"
            artifact_dir = root / "artifact"
            pd.DataFrame(
                {
                    "sample_ID": ["tr1", "va1"],
                    "split_final": ["train", "validation"],
                    "strain": ["S1", "S1"],
                    "chemical": ["D1", "D1"],
                    "medium": ["M1", "M1"],
                    "time_unit": ["h", "h"],
                    "temperature": [30.0, 30.0],
                    "time": [1.0, 2.0],
                    "data_source": ["source-a", "source-a"],
                    "instrument": ["inst-a", "inst-a"],
                }
            ).to_csv(metadata_path, index=False)
            pd.DataFrame(
                {"sample_ID": ["tr1", "va1"], "P1": [4.0, 8.0]}
            ).to_csv(proteome_path, index=False)
            write_config(config_path)

            result = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "train-metadata-ridge",
                    "--metadata",
                    str(metadata_path),
                    "--proteome",
                    str(proteome_path),
                    "--config",
                    str(config_path),
                    "--artifact-dir",
                    str(artifact_dir),
                ],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("split_final=train", result.stderr)
            self.assertFalse(artifact_dir.exists())

    def test_training_manifest_records_seed_parameters_provenance_and_verified_model_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            metadata_path = root / "metadata.csv"
            proteome_path = root / "proteome.csv"
            config_path = root / "config.json"
            artifact_dir = root / "artifact"
            pd.DataFrame(
                {
                    "sample_ID": ["tr1", "tr2"],
                    "split_final": ["train", "train"],
                    "strain": ["S1", "S2"],
                    "chemical": ["D1", "D2"],
                    "medium": ["M1", "M1"],
                    "time_unit": ["h", "h"],
                    "temperature": [30.0, 31.0],
                    "time": [1.0, 2.0],
                    "data_source": ["source-a", "source-a"],
                    "instrument": ["inst-a", "inst-a"],
                }
            ).to_csv(metadata_path, index=False)
            pd.DataFrame(
                {"sample_ID": ["tr2", "tr1"], "P1": [8.0, 4.0]}
            ).to_csv(proteome_path, index=False)
            write_config(config_path)

            result = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "train-metadata-ridge",
                    "--metadata",
                    str(metadata_path),
                    "--proteome",
                    str(proteome_path),
                    "--config",
                    str(config_path),
                    "--artifact-dir",
                    str(artifact_dir),
                    "--seed",
                    "23",
                ],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((artifact_dir / "manifest.json").read_text())
            self.assertEqual(manifest["seed"], 23)
            self.assertEqual(manifest["model"]["alpha"], 1.0)
            self.assertEqual(manifest["preprocessing"]["missingness_fit_scope"], "split_final=train")
            self.assertEqual(manifest["preprocessing"]["nonpositive_finite_policy"], "fail_closed")
            self.assertEqual(manifest["provenance"]["train_rows"], 2)
            self.assertEqual(
                manifest["provenance"]["source_sha256"]["metadata"],
                hashlib.sha256(metadata_path.read_bytes()).hexdigest(),
            )
            self.assertEqual(
                manifest["files"]["model_sha256"],
                hashlib.sha256((artifact_dir / "model.npz").read_bytes()).hexdigest(),
            )
            self.assertNotIn(str(root), json.dumps(manifest, sort_keys=True))

    def test_all_train_missing_filtered_protein_uses_frozen_fit_global_median(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            metadata_path = root / "metadata.csv"
            proteome_path = root / "proteome.csv"
            config_path = root / "config.json"
            artifact_dir = root / "artifact"
            test_metadata_path = root / "test_metadata.csv"
            template_path = root / "template.csv"
            output_path = root / "prediction.csv"
            pd.DataFrame(
                {
                    "sample_ID": ["tr1", "tr2"],
                    "split_final": ["train", "train"],
                    "strain": ["S1", "S2"],
                    "chemical": ["D1", "D2"],
                    "medium": ["M1", "M1"],
                    "time_unit": ["h", "h"],
                    "temperature": [30.0, 31.0],
                    "time": [1.0, 2.0],
                    "data_source": ["source-a", "source-a"],
                    "instrument": ["inst-a", "inst-a"],
                }
            ).to_csv(metadata_path, index=False)
            pd.DataFrame(
                {
                    "sample_ID": ["tr1", "tr2"],
                    "P1": [4.0, 8.0],
                    "P_ALL_MISSING": [np.nan, np.nan],
                }
            ).to_csv(proteome_path, index=False)
            write_config(config_path)
            train = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "train-metadata-ridge",
                    "--metadata",
                    str(metadata_path),
                    "--proteome",
                    str(proteome_path),
                    "--config",
                    str(config_path),
                    "--artifact-dir",
                    str(artifact_dir),
                ],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(train.returncode, 0, train.stderr)

            pd.DataFrame(
                {
                    "sample_ID": ["te1"],
                    "strain": ["S1"],
                    "chemical": ["D1"],
                    "medium": ["M1"],
                    "time_unit": ["h"],
                    "temperature": [30.0],
                    "time": [3.0],
                    "data_source": ["source-a"],
                    "instrument": ["inst-a"],
                }
            ).to_csv(test_metadata_path, index=False)
            pd.DataFrame(
                {"sample_ID": ["te1"], "P1": [0.0], "P_ALL_MISSING": [0.0]}
            ).to_csv(template_path, index=False)
            predict = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "predict-metadata-ridge",
                    "--artifact-dir",
                    str(artifact_dir),
                    "--test-metadata",
                    str(test_metadata_path),
                    "--submission-template",
                    str(template_path),
                    "--output",
                    str(output_path),
                ],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(predict.returncode, 0, predict.stderr)
            prediction = pd.read_csv(output_path)
            self.assertEqual(prediction.loc[0, "P_ALL_MISSING"], 2.5)
            manifest = json.loads((artifact_dir / "manifest.json").read_text())
            self.assertEqual(
                manifest["preprocessing"]["unobserved_fallback_policy"],
                "fit_global_median",
            )
            self.assertEqual(manifest["preprocessing"]["fit_global_median_log2"], 2.5)

    def test_prediction_accepts_template_protein_ordered_subset(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            metadata_path = root / "metadata.csv"
            proteome_path = root / "proteome.csv"
            config_path = root / "config.json"
            artifact_dir = root / "artifact"
            test_metadata_path = root / "test_metadata.csv"
            template_path = root / "template.csv"
            output_path = root / "prediction.csv"
            pd.DataFrame(
                {
                    "sample_ID": ["tr1", "tr2"],
                    "split_final": ["train", "train"],
                    "strain": ["S1", "S2"],
                    "chemical": ["D1", "D2"],
                    "medium": ["M1", "M1"],
                    "time_unit": ["h", "h"],
                    "temperature": [30.0, 31.0],
                    "time": [1.0, 2.0],
                    "data_source": ["source-a", "source-a"],
                    "instrument": ["inst-a", "inst-a"],
                }
            ).to_csv(metadata_path, index=False)
            pd.DataFrame(
                {
                    "sample_ID": ["tr1", "tr2"],
                    "P1": [4.0, 8.0],
                    "P2": [2.0, 4.0],
                    "P3": [np.nan, np.nan],
                }
            ).to_csv(proteome_path, index=False)
            write_config(config_path)
            train = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "train-metadata-ridge",
                    "--metadata",
                    str(metadata_path),
                    "--proteome",
                    str(proteome_path),
                    "--config",
                    str(config_path),
                    "--artifact-dir",
                    str(artifact_dir),
                ],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(train.returncode, 0, train.stderr)
            pd.DataFrame(
                {
                    "sample_ID": ["te1"],
                    "strain": ["S1"],
                    "chemical": ["D1"],
                    "medium": ["M1"],
                    "time_unit": ["h"],
                    "temperature": [30.0],
                    "time": [3.0],
                    "data_source": ["source-a"],
                    "instrument": ["inst-a"],
                }
            ).to_csv(test_metadata_path, index=False)
            pd.DataFrame(
                {"sample_ID": ["te1"], "P3": [0.0], "P1": [0.0]}
            ).to_csv(template_path, index=False)

            predict = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "predict-metadata-ridge",
                    "--artifact-dir",
                    str(artifact_dir),
                    "--test-metadata",
                    str(test_metadata_path),
                    "--submission-template",
                    str(template_path),
                    "--output",
                    str(output_path),
                ],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(predict.returncode, 0, predict.stderr)
            prediction = pd.read_csv(output_path)
            self.assertEqual(tuple(prediction.columns), ("sample_ID", "P3", "P1"))
            self.assertEqual(prediction.loc[0, "P3"], 2.0)

            bad_template = root / "bad_template.csv"
            bad_output = root / "bad_prediction.csv"
            pd.DataFrame(
                {"sample_ID": ["te1"], "P_NOT_IN_ARTIFACT": [0.0]}
            ).to_csv(bad_template, index=False)
            rejected = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "predict-metadata-ridge",
                    "--artifact-dir",
                    str(artifact_dir),
                    "--test-metadata",
                    str(test_metadata_path),
                    "--submission-template",
                    str(bad_template),
                    "--output",
                    str(bad_output),
                ],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("proteins absent from the artifact", rejected.stderr)
            self.assertFalse(bad_output.exists())

    def test_published_config_trains_with_official_metadata_headers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            metadata_path = root / "metadata.csv"
            proteome_path = root / "proteome.csv"
            artifact_dir = root / "artifact"
            pd.DataFrame(
                {
                    "sample_ID": ["tr1", "tr2"],
                    "split_final": ["train", "train"],
                    "Strains": ["S1", "S2"],
                    "perturbation_no_concentration": ["D1", "D2"],
                    "Medium": ["M1", "M1"],
                    "pert_time_unit": ["h", "h"],
                    "Temperature": [30.0, 31.0],
                    "pert_time": [1.0, 2.0],
                    "data_source": ["source-a", "source-a"],
                    "instrument": ["inst-a", "inst-a"],
                }
            ).to_csv(metadata_path, index=False)
            pd.DataFrame(
                {"sample_ID": ["tr2", "tr1"], "P1": [8.0, 4.0]}
            ).to_csv(proteome_path, index=False)

            result = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "train-metadata-ridge",
                    "--metadata",
                    str(metadata_path),
                    "--proteome",
                    str(proteome_path),
                    "--config",
                    str(PROJECT_ROOT / "configs" / "metadata_ridge.json"),
                    "--artifact-dir",
                    str(artifact_dir),
                ],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((artifact_dir / "manifest.json").read_text())
            field_names = [
                item["name"] for item in manifest["metadata_encoder"]["fields"]
            ]
            self.assertEqual(
                field_names,
                [
                    "Strains",
                    "perturbation_no_concentration",
                    "Medium",
                    "pert_time_unit",
                    "Temperature",
                    "pert_time",
                    "data_source",
                    "instrument",
                ],
            )

    def test_training_rejects_finite_nonpositive_raw_intensity_without_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            metadata_path = root / "metadata.csv"
            proteome_path = root / "proteome.csv"
            config_path = root / "config.json"
            artifact_dir = root / "artifact"
            pd.DataFrame(
                {
                    "sample_ID": ["tr1"],
                    "split_final": ["train"],
                    "strain": ["S1"],
                    "chemical": ["D1"],
                    "medium": ["M1"],
                    "time_unit": ["h"],
                    "temperature": [30.0],
                    "time": [1.0],
                    "data_source": ["source-a"],
                    "instrument": ["inst-a"],
                }
            ).to_csv(metadata_path, index=False)
            pd.DataFrame(
                {"sample_ID": ["tr1"], "P_ZERO": [0.0], "P_NEG": [-1.0]}
            ).to_csv(proteome_path, index=False)
            write_config(config_path)

            result = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "train-metadata-ridge",
                    "--metadata",
                    str(metadata_path),
                    "--proteome",
                    str(proteome_path),
                    "--config",
                    str(config_path),
                    "--artifact-dir",
                    str(artifact_dir),
                ],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("2 finite non-positive intensities", result.stderr)
            self.assertFalse(artifact_dir.exists())


if __name__ == "__main__":
    unittest.main()
