"""Offline tests with synthetic records; no API calls."""

import copy
import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "examples" / "cloud-acceptance" / "acceptance.py"
)
SPEC = importlib.util.spec_from_file_location("cloud_acceptance", MODULE_PATH)
acceptance = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(acceptance)
summarize = acceptance.summarize


class SummarizeTests(unittest.TestCase):
    def test_mixed_success_and_failure(self):
        result = summarize([
            {"ok": True, "duration_ms": 10},
            {"ok": False, "duration_ms": 20.5},
            {"ok": True, "duration_ms": 0},
        ])
        self.assertEqual(result["total"], 3)
        self.assertEqual(result["succeeded"], 2)
        self.assertAlmostEqual(result["success_rate"], 2 / 3)
        self.assertAlmostEqual(result["mean_duration_ms"], 30.5 / 3)

    def test_empty_list(self):
        self.assertEqual(summarize([]), {
            "total": 0, "succeeded": 0,
            "success_rate": 0.0, "mean_duration_ms": 0.0,
        })

    def test_all_failed(self):
        self.assertEqual(summarize([
            {"ok": False, "duration_ms": 2},
            {"ok": False, "duration_ms": 4},
        ]), {
            "total": 2, "succeeded": 0,
            "success_rate": 0.0, "mean_duration_ms": 3.0,
        })

    def test_missing_fields(self):
        for record in ({}, {"ok": True}, {"duration_ms": 1}):
            with self.subTest(record=record), self.assertRaises(ValueError):
                summarize([record])

    def test_ok_requires_bool(self):
        for value in (0, 1, "true", None, [], {}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                summarize([{"ok": value, "duration_ms": 1}])

    def test_negative_duration(self):
        for value in (-1, -0.5):
            with self.subTest(value=value), self.assertRaises(ValueError):
                summarize([{"ok": True, "duration_ms": value}])

    def test_nonfinite_duration(self):
        for value in (float("nan"), float("inf"), -float("inf")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                summarize([{"ok": True, "duration_ms": value}])

    def test_bool_duration(self):
        for value in (True, False):
            with self.subTest(value=value), self.assertRaises(ValueError):
                summarize([{"ok": True, "duration_ms": value}])

    def test_invalid_record_and_duration_types(self):
        for record in (None, [], "record", 1):
            with self.subTest(record=record), self.assertRaises(ValueError):
                summarize([record])
        for value in (None, "10", [], {}, complex(1, 0)):
            with self.subTest(value=value), self.assertRaises(ValueError):
                summarize([{"ok": True, "duration_ms": value}])

    def test_input_unchanged_on_success_and_failure(self):
        records = [{"ok": True, "duration_ms": 1, "extra": ["synthetic"]}]
        original = copy.deepcopy(records)
        summarize(records)
        self.assertEqual(records, original)
        records.append({"ok": False})
        original = copy.deepcopy(records)
        with self.assertRaises(ValueError):
            summarize(records)
        self.assertEqual(records, original)

    def test_large_finite_durations(self):
        self.assertEqual(summarize([
            {"ok": True, "duration_ms": 1e308},
            {"ok": True, "duration_ms": 1e308},
        ])["mean_duration_ms"], 1e308)


if __name__ == "__main__":
    unittest.main()
