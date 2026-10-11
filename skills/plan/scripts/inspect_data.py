#!/usr/bin/env python3
"""Inspect user-provided data and prepare the data-integrity review."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SECRET_NAMES = {".env", "credentials.json", "secrets.json"}
IGNORED_PARTS = {".git", "work", "figure-output", "__pycache__"}
TABLE_EXTENSIONS = {".csv", ".tsv"}
JSON_EXTENSIONS = {".json"}
JSONL_EXTENSIONS = {".jsonl", ".ndjson"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def validate_identifier(value: str, label: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", value):
        raise ValueError(f"{label} contains unsupported characters")
    return value


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative_path(path: Path, workspace: Path) -> str:
    return str(path.resolve().relative_to(workspace.resolve())).replace("\\", "/")


def is_secret(path: Path) -> bool:
    return path.name.lower() in SECRET_NAMES


def should_ignore(path: Path, workspace: Path) -> bool:
    try:
        relative = path.resolve().relative_to(workspace.resolve())
    except ValueError:
        return True
    return any(part in IGNORED_PARTS for part in relative.parts)


def detect_dialect(path: Path, sample: str) -> csv.Dialect:
    if path.suffix.lower() == ".tsv":
        return csv.excel_tab
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        return csv.excel


def inspect_table(path: Path) -> dict[str, Any]:
    with path.open(
        "r",
        encoding="utf-8-sig",
        errors="replace",
        newline="",
    ) as stream:
        sample = stream.read(8192)
        stream.seek(0)
        dialect = detect_dialect(path, sample)
        reader = csv.reader(stream, dialect)
        try:
            columns = next(reader)
        except StopIteration:
            return {
                "format": "table",
                "delimiter": getattr(dialect, "delimiter", ""),
                "row_count": 0,
                "column_count": 0,
                "columns": [],
                "duplicate_rows": 0,
                "empty_cells": 0,
                "parse_errors": ["file is empty"],
            }

        row_count = 0
        empty_cells = 0
        duplicate_rows = 0
        parse_errors: list[str] = []
        seen_rows: set[tuple[str, ...]] = set()
        for row_number, row in enumerate(reader, start=2):
            row_count += 1
            empty_cells += sum(1 for value in row if value.strip() == "")
            if len(row) != len(columns) and len(parse_errors) < 20:
                parse_errors.append(
                    f"row {row_number}: expected {len(columns)} columns, "
                    f"found {len(row)}"
                )
            row_key = tuple(row)
            if row_key in seen_rows:
                duplicate_rows += 1
            else:
                seen_rows.add(row_key)

    return {
        "format": "table",
        "delimiter": getattr(dialect, "delimiter", ""),
        "row_count": row_count,
        "column_count": len(columns),
        "columns": columns,
        "duplicate_rows": duplicate_rows,
        "empty_cells": empty_cells,
        "parse_errors": parse_errors,
    }


def inspect_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {
            "format": "json",
            "valid": False,
            "parse_errors": [str(exc)],
        }

    result: dict[str, Any] = {
        "format": "json",
        "valid": True,
        "top_level_type": type(payload).__name__,
        "parse_errors": [],
    }
    if isinstance(payload, dict):
        result["top_level_keys"] = list(payload.keys())
    elif isinstance(payload, list):
        result["record_count"] = len(payload)
    return result


def inspect_jsonl(path: Path) -> dict[str, Any]:
    line_count = 0
    parse_errors: list[str] = []
    with path.open("r", encoding="utf-8-sig", errors="replace") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            line_count += 1
            try:
                json.loads(line)
            except json.JSONDecodeError as exc:
                if len(parse_errors) < 20:
                    parse_errors.append(f"line {line_number}: {exc}")
    return {
        "format": "jsonl",
        "record_count": line_count,
        "parse_errors": parse_errors,
    }


def inspect_file(path: Path) -> tuple[str, dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix in TABLE_EXTENSIONS:
        return "inspected", inspect_table(path)
    if suffix in JSON_EXTENSIONS:
        return "inspected", inspect_json(path)
    if suffix in JSONL_EXTENSIONS:
        return "inspected", inspect_jsonl(path)
    if suffix in {".txt", ".md"}:
        try:
            with path.open(
                "r",
                encoding="utf-8-sig",
                errors="replace",
            ) as stream:
                line_count = sum(1 for _ in stream)
        except OSError as exc:
            return "failed", {"format": suffix.lstrip("."), "error": str(exc)}
        return "inspected", {
            "format": suffix.lstrip("."),
            "line_count": line_count,
            "parse_errors": [],
        }
    return "metadata_only", {
        "format": suffix.lstrip(".") or "unknown",
        "note": "structural inspection is not implemented for this format",
    }


def collect_paths(
    workspace: Path,
    explicit_paths: list[str],
) -> list[Path]:
    if explicit_paths:
        paths = []
        for raw_path in explicit_paths:
            path = Path(raw_path).expanduser()
            if not path.is_absolute():
                path = workspace / path
            paths.append(path.resolve())
        return paths

    scan_root = workspace / "inputs"
    if not scan_root.is_dir():
        scan_root = workspace
    return sorted(
        path.resolve()
        for path in scan_root.rglob("*")
        if path.is_file()
        and not should_ignore(path, workspace)
        and not is_secret(path)
    )


def new_item(path: Path, workspace: Path, item_id: str) -> dict[str, Any]:
    inspection_status, structural_check = inspect_file(path)
    stat = path.stat()
    return {
        "id": item_id,
        "path": relative_path(path, workspace),
        "sha256": sha256(path),
        "size_bytes": stat.st_size,
        "modified_at": datetime.fromtimestamp(
            stat.st_mtime, tz=timezone.utc
        ).replace(microsecond=0).isoformat(),
        "present": True,
        "inspection_status": inspection_status,
        "structural_check": structural_check,
        "origin": "unknown",
        "origin_evidence": "",
        "reliability": "unknown",
        "reliability_evidence": "",
        "definition_alignment": "unknown",
        "definition_basis": "unknown",
        "substitution_id": None,
        "replacement_definition": "",
        "alignment_notes": "",
        "quality_risks": [],
        "affected_master_ids": [],
        "affected_figures": [],
        "user_confirmed": False,
        "user_confirmed_at": None,
        "user_notes": "",
    }


def next_item_number(items: list[dict[str, Any]]) -> int:
    highest = 0
    for item in items:
        match = re.fullmatch(r"DATA-(\d+)", str(item.get("id", "")))
        if match:
            highest = max(highest, int(match.group(1)))
    return highest + 1


def render_markdown(report: dict[str, Any]) -> str:
    origin_confirmed = sum(
        1
        for item in report["items"]
        if str(item.get("origin", "unknown")).strip().lower()
        not in {"", "unknown"}
    )
    reliability_confirmed = sum(
        1
        for item in report["items"]
        if item.get("reliability") in {"high", "medium", "low"}
    )
    aligned = sum(
        1
        for item in report["items"]
        if item.get("definition_alignment") == "aligned"
    )
    substituted = sum(
        1
        for item in report["items"]
        if item.get("definition_basis") == "approved_substitution"
    )
    user_confirmed = sum(
        1
        for item in report["items"]
        if item.get("user_confirmed") is True
    )
    lines = [
        "# Data Integrity Report",
        "",
        "## Identity",
        "",
        f"- Paper ID: `{report['paper_id']}`",
        f"- Status: `{report['status']}`",
        f"- Last inspected: `{report['updated_at']}`",
        "",
        "## Summary",
        "",
        f"- Data items: {len(report['items'])}",
        f"- Origin confirmed: {origin_confirmed}",
        f"- Reliability confirmed: {reliability_confirmed}",
        f"- Definition aligned: {aligned}",
        f"- Approved definition substitutions: {substituted}",
        f"- User confirmed: {user_confirmed}",
        f"- Blocking issues: {len(report.get('blocking_issues', []))}",
        "",
        "## Items",
        "",
    ]
    if not report["items"]:
        lines.append("No data items have been inspected.")
    for item in report["items"]:
        checks = item.get("structural_check", {})
        quality_risks = ", ".join(item.get("quality_risks", []))
        affected_master_ids = ", ".join(item.get("affected_master_ids", []))
        affected_figures = ", ".join(item.get("affected_figures", []))
        lines.extend(
            [
                f"### {item['id']}: `{item['path']}`",
                "",
                f"- Present: `{str(item.get('present', True)).lower()}`",
                f"- Inspection: `{item.get('inspection_status', 'unknown')}`",
                f"- Format: `{checks.get('format', 'unknown')}`",
                f"- SHA-256: `{item.get('sha256', '')}`",
                f"- Origin: `{item.get('origin', 'unknown')}`",
                f"- Origin evidence: {item.get('origin_evidence', '')}",
                f"- Reliability: `{item.get('reliability', 'unknown')}`",
                f"- Reliability evidence: {item.get('reliability_evidence', '')}",
                f"- Definition alignment: `{item.get('definition_alignment', 'unknown')}`",
                f"- Definition basis: `{item.get('definition_basis', 'unknown')}`",
                f"- Substitution ID: `{item.get('substitution_id') or 'none'}`",
                f"- Replacement definition: {item.get('replacement_definition', '')}",
                f"- Alignment notes: {item.get('alignment_notes', '')}",
                f"- Quality risks: {quality_risks or 'none recorded'}",
                f"- Affected master IDs: {affected_master_ids or 'none recorded'}",
                f"- Affected figures: {affected_figures or 'none recorded'}",
                f"- User confirmed: `{str(item.get('user_confirmed', False)).lower()}`",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, help="Workspace root")
    parser.add_argument("--paper-id", required=True, help="Stable paper ID")
    parser.add_argument(
        "--path",
        action="append",
        default=[],
        help="Data file to inspect; repeat for multiple files",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        paper_id = validate_identifier(args.paper_id, "paper-id")
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    workspace = Path(args.workspace).expanduser().resolve()
    repro_dir = workspace / "work" / paper_id
    manifest_path = repro_dir / "reproduction_manifest.json"
    report_path = repro_dir / "data_integrity.json"
    if not manifest_path.is_file() or not report_path.is_file():
        print(
            f"error: missing initialized workspace or data_integrity.json: {repro_dir}",
            file=sys.stderr,
        )
        return 1

    report = load_json(report_path)
    previous_items = {
        str(item.get("path")): item for item in report.get("items", [])
    }
    paths = collect_paths(workspace, args.path)
    unknown_paths = [
        path for path in paths if not path.is_file() or should_ignore(path, workspace)
    ]
    if unknown_paths:
        print(
            "error: missing or ignored data paths: "
            + ", ".join(str(path) for path in unknown_paths),
            file=sys.stderr,
        )
        return 1

    secret_paths = [path for path in paths if is_secret(path)]
    if secret_paths:
        print(
            "error: secret-like files cannot be inspected: "
            + ", ".join(str(path) for path in secret_paths),
            file=sys.stderr,
        )
        return 1

    items: list[dict[str, Any]] = []
    changed = False
    inspected_paths: set[str] = set()
    next_number = next_item_number(list(previous_items.values()))
    for path in paths:
        relative = relative_path(path, workspace)
        inspected_paths.add(relative)
        current_hash = sha256(path)
        previous = previous_items.get(relative)
        if previous and previous.get("sha256") == current_hash:
            item = previous
            inspection_status, structural_check = inspect_file(path)
            item["inspection_status"] = inspection_status
            item["structural_check"] = structural_check
            item["present"] = True
        else:
            item = new_item(
                path,
                workspace,
                str(previous.get("id"))
                if previous
                else f"DATA-{next_number:03d}",
            )
            if not previous:
                next_number += 1
            changed = True
        item.setdefault("definition_basis", "unknown")
        item.setdefault("substitution_id", None)
        item.setdefault("replacement_definition", "")
        items.append(item)

    for relative, previous in previous_items.items():
        if relative not in inspected_paths:
            previous["present"] = False
            previous["inspection_status"] = "missing"
            items.append(previous)
            changed = True

    if changed:
        report["status"] = "in_progress"
    report["items"] = items
    report["updated_at"] = utc_now()
    report.setdefault("blocking_issues", [])
    write_json(report_path, report)
    (repro_dir / "data_integrity.md").write_text(
        render_markdown(report), encoding="utf-8", newline="\n"
    )

    print(
        json.dumps(
            {
                "status": report["status"],
                "report": str(report_path),
                "items": len(items),
                "changed": changed,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
