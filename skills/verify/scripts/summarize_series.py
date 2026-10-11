#!/usr/bin/env python3
"""Compare two numeric CSV series and write error metrics."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path


def read_series(path: Path, key: str, value: str) -> dict[str, float]:
    series: dict[str, float] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None:
            raise ValueError(f"{path} has no header")
        missing = {key, value} - set(reader.fieldnames)
        if missing:
            raise ValueError(f"{path} missing columns: {sorted(missing)}")
        for row in reader:
            item_key = str(row[key])
            item_value = row[value]
            if item_value not in (None, ""):
                series[item_key] = float(item_value)
    return series


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected", required=True, help="Expected CSV path")
    parser.add_argument("--actual", required=True, help="Actual CSV path")
    parser.add_argument("--key", required=True, help="Shared key column")
    parser.add_argument("--value", required=True, help="Numeric value column")
    parser.add_argument("--abs-tolerance", type=float, default=1e-9)
    parser.add_argument("--rel-tolerance", type=float, default=1e-6)
    parser.add_argument("--output", help="Optional output JSON path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        expected = read_series(Path(args.expected), args.key, args.value)
        actual = read_series(Path(args.actual), args.key, args.value)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    common = sorted(set(expected) & set(actual))
    rows = []
    abs_errors: list[float] = []
    rel_errors: list[float] = []
    within = 0

    for key in common:
        expected_value = expected[key]
        actual_value = actual[key]
        abs_error = abs(actual_value - expected_value)
        rel_error = (
            abs_error / abs(expected_value) if expected_value != 0 else math.inf
        )
        passes = abs_error <= args.abs_tolerance or rel_error <= args.rel_tolerance
        within += int(passes)
        abs_errors.append(abs_error)
        if math.isfinite(rel_error):
            rel_errors.append(rel_error)
        rows.append(
            {
                "key": key,
                "expected": expected_value,
                "actual": actual_value,
                "absolute_error": abs_error,
                "relative_error": rel_error,
                "within_tolerance": passes,
            }
        )

    summary = {
        "matched_keys": len(common),
        "missing_expected": sorted(set(actual) - set(expected)),
        "missing_actual": sorted(set(expected) - set(actual)),
        "within_tolerance": within,
        "max_absolute_error": max(abs_errors, default=None),
        "mean_absolute_error": (
            sum(abs_errors) / len(abs_errors) if abs_errors else None
        ),
        "rmse": (
            math.sqrt(sum(value * value for value in abs_errors) / len(abs_errors))
            if abs_errors
            else None
        ),
        "max_relative_error": max(rel_errors, default=None),
        "mean_relative_error": (
            sum(rel_errors) / len(rel_errors) if rel_errors else None
        ),
        "rows": rows,
    }
    if args.output:
        Path(args.output).write_text(
            json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
