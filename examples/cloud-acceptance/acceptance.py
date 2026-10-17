"""Summarize synthetic acceptance records without external services."""

import math
import statistics


def summarize(records):
    """Return counts, success rate, and mean duration for a list of records.

    Each record must be a dictionary with a bool ``ok`` and a nonnegative,
    finite int or float ``duration_ms`` (excluding bool). Invalid input raises
    ValueError. Input records are never modified.
    """
    if not isinstance(records, list):
        raise ValueError("records must be a list")

    succeeded = 0
    durations = []
    for index, record in enumerate(records):
        if not isinstance(record, dict) or not {"ok", "duration_ms"} <= record.keys():
            raise ValueError(f"record {index} must contain ok and duration_ms")
        if type(record["ok"]) is not bool:
            raise ValueError(f"record {index}: ok must be a bool")
        duration = record["duration_ms"]
        if (
            isinstance(duration, bool)
            or not isinstance(duration, (int, float))
            or duration < 0
            or (isinstance(duration, float) and not math.isfinite(duration))
        ):
            raise ValueError(f"record {index}: duration_ms must be finite and nonnegative")
        succeeded += record["ok"]
        durations.append(duration)

    total = len(records)
    return {
        "total": total,
        "succeeded": succeeded,
        "success_rate": succeeded / total if total else 0.0,
        "mean_duration_ms": statistics.mean(durations) if total else 0.0,
    }
