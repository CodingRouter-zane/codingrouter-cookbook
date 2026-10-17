"""Offline CSV task-cost summary. No network calls or third-party packages."""

import argparse
import csv
import json
import re
import sys
from decimal import Decimal, ROUND_HALF_UP, localcontext
from pathlib import Path

FIELDS = {"task_id", "currency", "total_cost", "qualified"}
COST_PATTERN = re.compile(r"[0-9]{1,12}(?:\.[0-9]{1,6})?\Z")
CURRENCY_PATTERN = re.compile(r"[A-Z]{3}\Z")
SCALE = 1_000_000


class InputError(ValueError):
    """Invalid data; messages deliberately exclude user-supplied values."""


def money(micro_units):
    # Integer aggregation avoids cumulative decimal-context rounding.
    whole, fraction = divmod(micro_units, SCALE)
    return f"{whole}.{fraction:06d}"


def summarize(stream):
    reader = csv.DictReader(stream, strict=True)
    headers = reader.fieldnames
    if headers is None:
        raise InputError("CSV is empty; a header and at least one task are required.")
    if len(headers) != len(FIELDS) or set(headers) != FIELDS:
        raise InputError("Header must contain exactly task_id,currency,total_cost,qualified.")
    groups = {}
    seen = set()
    for row in reader:
        line = reader.line_num
        if None in row or any(value is None for value in row.values()):
            raise InputError(f"Line {line}: incorrect number of fields.")
        values = {key: value.strip() for key, value in row.items()}
        if any(not value for value in values.values()):
            raise InputError(f"Line {line}: required field is empty.")
        if values["task_id"] in seen:
            raise InputError(f"Line {line}: duplicate task_id.")
        if not CURRENCY_PATTERN.fullmatch(values["currency"]):
            raise InputError(f"Line {line}: currency must be three uppercase ASCII letters.")
        if not COST_PATTERN.fullmatch(values["total_cost"]):
            raise InputError(
                f"Line {line}: total_cost must be nonnegative fixed-point decimal "
                "with at most 12 integer and 6 fractional digits."
            )
        if values["qualified"] not in ("true", "false"):
            raise InputError(f"Line {line}: qualified must be true or false.")
        seen.add(values["task_id"])
        # Parsing and multiplication are exact for the bounded input precision.
        with localcontext() as context:
            context.prec = 28
            micro_units = int(Decimal(values["total_cost"]) * SCALE)
        group = groups.setdefault(values["currency"], [0, 0, 0])
        group[0] += 1
        group[1] += values["qualified"] == "true"
        group[2] += micro_units
    if not seen:
        raise InputError("CSV contains no tasks; at least one task is required.")
    result = []
    for currency, (count, qualified, total) in sorted(groups.items()):
        average = None
        if qualified:
            with localcontext() as context:
                context.prec = max(28, len(str(total)) + 16)
                average = format(
                    (Decimal(total) / SCALE / qualified).quantize(
                        Decimal("0.000001"), rounding=ROUND_HALF_UP
                    ),
                    ".6f",
                )
        result.append({
            "currency": currency,
            "task_count": count,
            "qualified_count": qualified,
            "total_cost": money(total),
            "cost_per_qualified_result": average,
        })
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", type=Path, help="UTF-8 CSV of completed tasks")
    args = parser.parse_args(argv)
    try:
        with args.csv_file.open(encoding="utf-8-sig", newline="") as stream:
            result = summarize(stream)
    except InputError as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2
    except UnicodeError:
        print("Input error: file must be valid UTF-8.", file=sys.stderr)
        return 2
    except csv.Error:
        print("Input error: malformed CSV or field too large.", file=sys.stderr)
        return 2
    except OSError:
        print("Input error: unable to read the CSV file.", file=sys.stderr)
        return 2
    # Print only after the complete input has passed validation; never partial totals.
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
