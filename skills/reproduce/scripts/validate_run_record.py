#!/usr/bin/env python3
"""Validate locked runbook execution records for ReproduSpec figures."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_STEP_FIELDS = (
    "spec_step",
    "status",
    "command",
    "parameters",
    "inputs",
    "outputs",
    "validation",
    "failure_action",
    "handoff",
    "result",
)


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


def runbook_step_ids(spec_path: Path) -> list[str]:
    text = spec_path.read_text(encoding="utf-8")
    runbook_start = text.find("## Execution Runbook")
    if runbook_start < 0:
        return []
    tail = text[runbook_start + len("## Execution Runbook") :]
    next_section = re.search(r"^##[^#]", tail, re.MULTILINE)
    if next_section is not None:
        tail = tail[: next_section.start()]
    return re.findall(r"^###\s+(S\d{2,3})\b", tail, re.MULTILINE)


def has_content(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, help="Workspace root")
    parser.add_argument("--paper-id", required=True, help="Stable paper ID")
    parser.add_argument(
        "--figure-id",
        action="append",
        default=[],
        help="Figure ID to validate; repeat to validate multiple figures",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        paper_id = validate_identifier(args.paper_id, "paper-id")
        target_ids = [
            validate_identifier(value, "figure-id")
            for value in args.figure_id
        ]
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    workspace = Path(args.workspace).expanduser().resolve()
    repro_dir = workspace / "work" / paper_id
    manifest_path = repro_dir / "reproduction_manifest.json"
    if not manifest_path.is_file():
        print(f"error: missing manifest: {manifest_path}", file=sys.stderr)
        return 1

    manifest = load_json(manifest_path)
    spec_lock = manifest.get("spec_lock", {})
    if not isinstance(spec_lock, dict) or spec_lock.get("status") != "locked":
        print("error: spec_lock is missing or not locked", file=sys.stderr)
        return 1
    locked_specs = {
        str(item.get("figure_id")): item
        for item in spec_lock.get("figure_specs", [])
        if isinstance(item, dict) and str(item.get("figure_id", "")).strip()
    }
    figures = [
        figure
        for figure in manifest.get("figures", [])
        if isinstance(figure, dict) and str(figure.get("id", "")).strip()
    ]
    figure_by_id = {str(figure["id"]): figure for figure in figures}
    selected_ids = target_ids or sorted(figure_by_id)
    unknown = sorted(set(selected_ids) - set(figure_by_id))
    if unknown:
        print(f"error: unknown figure IDs: {', '.join(unknown)}", file=sys.stderr)
        return 1

    errors: list[str] = []
    needs_relock = False
    validations: list[dict[str, Any]] = []
    for figure_id in selected_ids:
        figure = figure_by_id[figure_id]
        locked = locked_specs.get(figure_id)
        if not isinstance(locked, dict):
            errors.append(f"{figure_id}: missing spec_lock figure record")
            continue

        figure_dir = repro_dir / str(figure.get("path", ""))
        spec_path = figure_dir / "spec.md"
        evidence_path = repro_dir / str(locked.get("evidence_path", ""))
        run_record_path = figure_dir / "logs" / "run_record.json"
        if not spec_path.is_file():
            errors.append(f"{figure_id}: missing spec.md")
            needs_relock = True
            continue
        if not evidence_path.is_file():
            errors.append(f"{figure_id}: missing frozen evidence pack")
            needs_relock = True
            continue
        if not run_record_path.is_file():
            errors.append(f"{figure_id}: missing logs/run_record.json")
            continue

        actual_spec_hash = sha256(spec_path)
        actual_evidence_hash = sha256(evidence_path)
        if actual_spec_hash != locked.get("spec_sha256"):
            errors.append(f"{figure_id}: specification changed after locking")
            needs_relock = True
            continue
        if actual_evidence_hash != locked.get("evidence_sha256"):
            errors.append(f"{figure_id}: evidence changed after locking")
            needs_relock = True
            continue

        try:
            run_record = load_json(run_record_path)
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(f"{figure_id}: invalid run record: {exc}")
            continue
        if not isinstance(run_record, dict):
            errors.append(f"{figure_id}: run record must be an object")
            continue
        if str(run_record.get("figure_id", "")) != figure_id:
            errors.append(f"{figure_id}: run record figure_id does not match")

        specification = run_record.get("specification", {})
        if not isinstance(specification, dict):
            errors.append(f"{figure_id}: run record specification must be an object")
            specification = {}
        if specification.get("spec_sha256") != actual_spec_hash:
            errors.append(f"{figure_id}: run record specification hash is stale")
        if specification.get("evidence_pack_sha256") != actual_evidence_hash:
            errors.append(f"{figure_id}: run record evidence hash is stale")
        if (
            str(specification.get("spec_path", "")).replace("\\", "/")
            != str(locked.get("spec_path", "")).replace("\\", "/")
        ):
            errors.append(f"{figure_id}: run record specification path differs from lock")
        if (
            str(specification.get("evidence_pack_path", "")).replace("\\", "/")
            != str(locked.get("evidence_path", "")).replace("\\", "/")
        ):
            errors.append(f"{figure_id}: run record evidence path differs from lock")
        if specification.get("detail_validation_status") != "passed":
            errors.append(f"{figure_id}: run record Detail validation is not passed")
        if specification.get("report_reread_for_requirements") is not False:
            errors.append(
                f"{figure_id}: report reread for requirements is not false"
            )
        if run_record.get("reread_events") != []:
            errors.append(f"{figure_id}: reread_events must be empty")

        expected_steps = runbook_step_ids(spec_path)
        if not expected_steps:
            errors.append(f"{figure_id}: specification has no runbook steps")
            continue
        entries = run_record.get("runbook_steps", [])
        if not isinstance(entries, list):
            errors.append(f"{figure_id}: runbook_steps must be a list")
            continue
        entry_by_step = {
            str(entry.get("spec_step")): entry
            for entry in entries
            if isinstance(entry, dict) and str(entry.get("spec_step", "")).strip()
        }
        missing_steps = [
            step_id for step_id in expected_steps if step_id not in entry_by_step
        ]
        extra_steps = sorted(set(entry_by_step) - set(expected_steps))
        if missing_steps:
            errors.append(
                f"{figure_id}: run record is missing "
                + ", ".join(missing_steps)
            )
        if extra_steps:
            errors.append(
                f"{figure_id}: run record has unknown steps "
                + ", ".join(extra_steps)
            )
        for step_id in expected_steps:
            entry = entry_by_step.get(step_id)
            if not isinstance(entry, dict):
                continue
            missing_fields = [
                field for field in REQUIRED_STEP_FIELDS if not has_content(entry.get(field))
            ]
            if missing_fields:
                errors.append(
                    f"{figure_id}: {step_id} run entry is missing "
                    + ", ".join(missing_fields)
                )
            if entry.get("status") != "completed":
                errors.append(f"{figure_id}: {step_id} is not completed")
            if str(entry.get("result", "")).lower() not in {
                "passed",
                "pass",
                "completed",
                "success",
            }:
                errors.append(
                    f"{figure_id}: {step_id} validation result is not passing"
                )

        validations.append(
            {
                "figure_id": figure_id,
                "run_record_path": str(
                    run_record_path.relative_to(repro_dir)
                ).replace("\\", "/"),
                "run_record_sha256": sha256(run_record_path),
                "spec_sha256": actual_spec_hash,
                "evidence_sha256": actual_evidence_hash,
                "runbook_steps": len(expected_steps),
            }
        )

    if errors:
        print(
            json.dumps(
                {
                    "status": "blocked",
                    "errors": errors,
                    "next": (
                        "/reprospec:analyse"
                        if needs_relock
                        else "/reprospec:reproduce"
                    ),
                },
                indent=2,
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 1

    validated_at = utc_now()
    updated_by_id: dict[str, dict[str, Any]] = {}
    for validation in validations:
        updated_by_id[validation["figure_id"]] = {
            "run_validation": {
                "status": "passed",
                "validated_at": validated_at,
                "run_record_path": validation["run_record_path"],
                "run_record_sha256": validation["run_record_sha256"],
                "spec_sha256": validation["spec_sha256"],
                "evidence_sha256": validation["evidence_sha256"],
                "runbook_steps": validation["runbook_steps"],
                "report_reread_for_requirements": False,
                "reread_events": 0,
            }
        }
    manifest["figures"] = [
        {
            **figure,
            **updated_by_id.get(str(figure.get("id", "")), {}),
        }
        for figure in manifest.get("figures", [])
    ]
    manifest["updated_at"] = validated_at
    write_json(manifest_path, manifest)
    print(
        json.dumps(
            {
                "status": "passed",
                "validated_at": validated_at,
                "count": len(validations),
                "items": validations,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
