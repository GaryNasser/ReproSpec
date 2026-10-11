#!/usr/bin/env python3
"""Initialize one ReproSpec paper workspace."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def validate_identifier(value: str, label: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", value):
        raise ValueError(
            f"{label} must start with a letter or digit and contain only "
            "letters, digits, dots, underscores, and hyphens"
        )
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, help="Workspace root")
    parser.add_argument("--paper-id", required=True, help="Stable paper ID")
    parser.add_argument("--paper-title", required=True, help="Paper title")
    parser.add_argument("--source", default="", help="Paper path, URL, or description")
    parser.add_argument(
        "--time-range",
        required=True,
        choices=("publication_period", "through_today"),
        help="User-confirmed reproduction time-range mode",
    )
    parser.add_argument(
        "--time-range-timezone",
        required=True,
        help="Explicit timezone for interpreting the reproduction dates",
    )
    parser.add_argument(
        "--time-range-start",
        default=None,
        help="Optional ISO start date when already known",
    )
    parser.add_argument(
        "--time-range-end",
        default=None,
        help="Optional ISO end date when already known",
    )
    parser.add_argument(
        "--time-range-basis",
        default="",
        help="Source or calculation basis for the selected time-range mode",
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
    if repro_dir.exists():
        print(f"error: workspace already exists: {repro_dir}", file=sys.stderr)
        return 1

    for directory in (
        repro_dir / "figures",
        repro_dir / "evidence",
        repro_dir / "audits",
        repro_dir / "data" / "raw",
        repro_dir / "data" / "interim",
        repro_dir / "data" / "processed",
        repro_dir / "data" / "organized",
        repro_dir / "logs",
    ):
        directory.mkdir(parents=True, exist_ok=True)

    for name in ("raw", "interim", "processed", "organized"):
        (repro_dir / "data" / name / ".gitkeep").write_text(
            "", encoding="utf-8", newline="\n"
        )

    created_at = utc_now()
    source_path = Path(args.source).expanduser()
    source_hash = None
    if args.source and source_path.is_file():
        source_hash = sha256(source_path.resolve())

    master_spec = (
        "# Master Data Specification\n\n"
        f"- Paper ID: `{paper_id}`\n"
        f"- Title: `{args.paper_title}`\n"
        f"- Source: `{args.source}`\n"
        f"- Source hash: `{source_hash or ''}`\n"
        "- Version: `1.0.0`\n"
        "- Status: `draft`\n\n"
        "## Computation Source Policy\n\n"
        "Publication numbers are comparison targets only. Reproduction values "
        "and plot coordinates must be computed from approved real data through "
        "traceable code. Missing real data requires a user decision to "
        "supplement the data or skip the affected item.\n\n"
        f"Reproduction time-range mode selected at Init: `{args.time_range}`. "
        "Exact start and end dates must be confirmed at the analysis gate "
        "before locking or reproduction.\n\n"
        "## Source Snapshot\n\n"
        "## Research Scope\n\n"
        "## Stable Data Contract\n\n"
        "## Definition Substitutions\n\n"
        "## Data Integrity\n\n"
        "## Processing Rules\n\n"
        "## Missing Data and Revisions\n\n"
        "## Source Priority\n\n"
        "## User-Confirmed Decisions\n\n"
        "## Version History\n\n"
        "## Known Limitations\n"
    )
    (repro_dir / "master_spec.md").write_text(
        master_spec, encoding="utf-8", newline="\n"
    )
    (repro_dir / "data_gaps.csv").write_text(
        "master_id,figure_ids,required_definition,source_candidate,"
        "access_method,permission_required,status,fallback,evidence_path,"
        "last_verified,integrity_id,definition_status,substitution_id,"
        "replacement_definition,user_approved\n",
        encoding="utf-8",
        newline="\n",
    )
    (repro_dir / "data_inventory.csv").write_text(
        "path,scope,size_bytes,sha256,duplicate_of,modified_at\n",
        encoding="utf-8",
        newline="\n",
    )
    (repro_dir / "data_catalog.csv").write_text(
        "dataset_id,title,organized_path,role,format,rows,columns,"
        "schema_path,metadata_path,source_paths,source_sha256,"
        "source_map,extraction_methods,organized_sha256,figure_ids,"
        "audit_ids,definition_substitutions,reuse_status,last_verified\n",
        encoding="utf-8",
        newline="\n",
    )
    data_organization = {
        "schema_version": "0.2.0",
        "paper_id": paper_id,
        "status": "pending",
        "updated_at": None,
        "inventory": "data_inventory.csv",
        "catalog": "data_catalog.csv",
        "report": "data_organization.md",
        "organized_path": "data/organized",
        "raw_source_count": 0,
        "dataset_count": 0,
        "canonical_formats": [],
        "canonical_checkpoint": False,
        "source_disposition": "pending",
        "user_decision": None,
        "user_approved": False,
        "user_confirmed_at": None,
        "include_raw_in_delivery": False,
        "datasets": [],
        "verification": {
            "status": "pending",
            "required_coverage": False,
            "source_map_ready": False,
            "load_without_raw": False,
            "audit_ready": False,
            "reuse_ready": False,
            "checks": [],
        },
    }
    write_json(repro_dir / "data_organization.json", data_organization)
    (repro_dir / "data_organization.md").write_text(
        "# Data Organization Report\n\n"
        "## Identity\n\n"
        f"- Paper ID: `{paper_id}`\n"
        "- Status: `pending`\n"
        "- Updated at:\n\n"
        "## Organization Map\n\n"
        "No canonical datasets have been created.\n\n"
        "## Dataset Catalog\n\n"
        "No datasets have been cataloged.\n\n"
        "## Provenance\n\n"
        "No dataset provenance has been recorded.\n\n"
        "## Audit and Reuse Verification\n\n"
        "No verification has been performed.\n\n"
        "## Source Disposition Decision\n\n"
        "No user decision has been recorded.\n\n"
        "## Applied Actions\n\n"
        "No original data has been moved or removed.\n\n"
        "## Remaining Source Data\n\n"
        "Original data remains unchanged.\n\n"
        "## Audit Handoff\n\n"
        "Data organization is pending.\n",
        encoding="utf-8",
        newline="\n",
    )
    (repro_dir / "rework_log.md").write_text(
        "# Rework Log\n\nNo rework rounds recorded.\n",
        encoding="utf-8",
        newline="\n",
    )
    (repro_dir / "adjustment_log.md").write_text(
        "# Adjustment Log\n\nNo manual-review adjustments recorded.\n",
        encoding="utf-8",
        newline="\n",
    )
    (repro_dir / "audit_report.md").write_text(
        "# Traceability Audit Report\n\n"
        "## Identity\n\n"
        f"- Paper ID: `{paper_id}`\n"
        "- Audit status: `pending`\n"
        "- Updated at:\n\n"
        "## Summary\n\n"
        "- Included figures:\n"
        "- Complete audits:\n"
        "- Blocked audits:\n"
        "- Documented steps:\n"
        "- Critical gaps:\n\n"
        "## Figure Audits\n\n"
        "No figure audits have been completed.\n\n"
        "## Open Gaps\n\n"
        "None recorded.\n\n"
        "## Delivery Assessment\n\n"
        "Audit is pending.\n",
        encoding="utf-8",
        newline="\n",
    )
    (repro_dir / "data_integrity.md").write_text(
        "# Data Integrity Report\n\n"
        "## Identity\n\n"
        f"- Paper ID: `{paper_id}`\n"
        "- Status: `pending`\n"
        "- Last inspected:\n"
        "- User confirmation date:\n\n"
        "## Summary\n\n"
        "- Data items:\n"
        "- Origin confirmed:\n"
        "- Reliability confirmed:\n"
        "- Definition aligned:\n"
        "- User confirmed:\n"
        "- Blocking issues:\n\n"
        "## Items\n\n"
        "No data items have been inspected.\n",
        encoding="utf-8",
        newline="\n",
    )
    data_integrity = {
        "schema_version": "0.2.0",
        "paper_id": paper_id,
        "status": "pending",
        "updated_at": created_at,
        "items": [],
        "blocking_issues": [],
    }
    write_json(repro_dir / "data_integrity.json", data_integrity)

    manifest = {
        "schema_version": "0.13.0",
        "paper": {
            "id": paper_id,
            "title": args.paper_title,
            "source": args.source,
            "sha256": source_hash,
        },
        "workflow": {
            "active_stage": "init",
            "completed_stages": ["init"],
            "next_stage": "outline",
            "updated_at": created_at,
        },
        "computation_policy": {
            "status": "enforced",
            "published_values": "comparison_only",
            "reproduction_inputs": "approved_real_data_only",
            "missing_data_action": "ask_user_to_supplement_or_skip",
        },
        "definition_policy": {
            "status": "enforced",
            "undefined_data_action": "negotiate_explicit_substitute",
            "decision_required": False,
            "substitutions": [],
        },
        "time_range_policy": {
            "status": "selection_confirmed",
            "options": ["publication_period", "through_today"],
            "selection": args.time_range,
            "decision_required": False,
            "user_confirmed": True,
            "confirmed_at": created_at,
            "start_date": args.time_range_start,
            "end_date": args.time_range_end,
            "timezone": args.time_range_timezone,
            "basis": args.time_range_basis
            or "user-selected at Init; exact dates require Analyse confirmation",
        },
        "master_spec": {
            "path": "master_spec.md",
            "version": "1.0.0",
            "status": "draft",
        },
        "source_evidence": {
            "status": "pending",
            "directory": "evidence",
            "items": [],
            "updated_at": None,
        },
        "figures": [],
        "excluded_figures": [],
        "data_plan": {
            "path": "data_gaps.csv",
            "status": "pending",
            "decision_required": False,
            "decision": None,
            "decision_options": ["supplement_data", "skip"],
        },
        "data_integrity": {
            "path": "data_integrity.json",
            "report": "data_integrity.md",
            "status": "pending",
        },
        "rework": {
            "round": 0,
            "path": "rework_log.md",
            "history": [],
        },
        "adjustments": {
            "session": 0,
            "path": "adjustment_log.md",
            "history": [],
        },
        "organization": {
            "status": "pending",
            "inventory": "data_inventory.csv",
            "catalog": "data_catalog.csv",
            "report": "data_organization.md",
            "record": "data_organization.json",
            "organized_path": "data/organized",
            "raw_source_count": 0,
            "dataset_count": 0,
            "canonical_formats": [],
            "canonical_checkpoint": False,
            "source_disposition": "pending",
            "user_decision": None,
            "user_approved": False,
            "include_raw_in_delivery": False,
            "updated_at": None,
        },
        "audit": {
            "status": "pending",
            "path": "audits",
            "report": "audit_report.md",
            "figures": {},
            "updated_at": None,
        },
        "delivery": {
            "status": "pending",
            "path": None,
        },
        "created_at": created_at,
        "updated_at": created_at,
    }
    write_json(repro_dir / "reproduction_manifest.json", manifest)

    print(
        json.dumps(
            {
                "status": "created",
                "paper_id": paper_id,
                "reproduction_dir": str(repro_dir),
                "manifest": str(repro_dir / "reproduction_manifest.json"),
                "computation_policy": manifest["computation_policy"],
                "definition_policy": manifest["definition_policy"],
                "time_range_policy": manifest["time_range_policy"],
                "source_sha256": source_hash,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
