import json
import tempfile
import unittest
from pathlib import Path

from experiment_core.base import ExperimentResult
from reporting import AggregateReportWriter


class AggregateReportWriterTest(unittest.TestCase):
    @staticmethod
    def result(**overrides):
        values = {
            "name": "safe",
            "status": "COMPLETED",
            "metrics": {"pcc": 0.5},
            "counts": {"conditions": 2},
            "contract": {"aggregate_only": True},
            "provenance": {"data_scope": "synthetic", "seed": 7},
            "notes": ("Aggregate fixture only.",),
        }
        values.update(overrides)
        return ExperimentResult(**values)

    def test_vector_metric_fails_before_any_output_is_written(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "report"
            with self.assertRaisesRegex(TypeError, "metric.*scalar"):
                AggregateReportWriter().write(
                    self.result(metrics={"accidental_vector": [1, 2, 3]}), output
                )
            self.assertFalse(output.exists())

    def test_sensitive_absolute_path_fails_before_any_output_is_written(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "report"
            with self.assertRaisesRegex(ValueError, "path or private-data"):
                AggregateReportWriter().write(
                    self.result(notes=("Loaded /Users/example/private-data/x.csv",)),
                    output,
                )
            self.assertFalse(output.exists())

    def test_valid_undefined_metric_is_serialized_as_null(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "report"
            AggregateReportWriter().write(
                self.result(metrics={"undefined_metric": float("nan")}), output
            )
            payload = json.loads((output / "result.json").read_text())
        self.assertIsNone(payload["metrics"]["undefined_metric"])
        self.assertEqual(payload["provenance"]["seed"], 7)


if __name__ == "__main__":
    unittest.main()
