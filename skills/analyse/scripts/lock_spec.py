#!/usr/bin/env python3
"""Lock the final ReproSpec master specification."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path


ALLOWED_INSPECTION_STATUSES = {"inspected", "metadata_only"}
ALLOWED_RELIABILITY = {"high", "medium", "low"}
ALLOWED_TIME_RANGE_MODES = {"publication_period", "through_today"}
ALLOWED_DEFINITION_BASES = {
    "source_explicit",
    "approved_substitution",
}
REQUIRED_STEP_FIELDS = (
    "Depends on",
    "Input",
    "Operation",
    "Formula or logic",
    "Parameters",
    "Code entrypoint",
    "Output",
    "Validation",
    "Failure action",
    "Handoff",
)
PLACEHOLDER_RE = re.compile(r"\{\{[^}]+\}\}")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def validate_identifier(value: str, label: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", value):
        raise ValueError(f"{label} contains unsupported characters")
    return value


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def field_value(text: str, label: str) -> str:
    match = re.search(
        rf"^- {re.escape(label)}:[ \t]*(.*?)[ \t]*$",
        text,
        re.MULTILINE,
    )
    if match is None:
        return ""
    value = match.group(1).strip()
    if value.startswith("`") and value.endswith("`"):
        value = value[1:-1].strip()
    return value


def section_text(text: str, heading: str) -> str:
    start = text.find(heading)
    if start < 0:
        return ""
    tail_start = start + len(heading)
    tail = text[tail_start:]
    level = len(heading) - len(heading.lstrip("#"))
    next_heading = re.search(
        rf"^{'#' * level}[^#]",
        tail,
        re.MULTILINE,
    )
    if next_heading is None:
        return tail
    return tail[: next_heading.start()]


def parse_runbook_steps(text: str) -> list[tuple[str, str]]:
    runbook = section_text(text, "## Execution Runbook")
    pattern = re.compile(
        r"^###\s+(S\d{2,3})\b[^\n]*\n(.*?)(?=^###\s+S\d{2,3}\b|^##\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    return [(match.group(1), match.group(2)) for match in pattern.finditer(runbook)]


def step_has_field(step_text: str, label: str) -> bool:
    lines = step_text.splitlines()
    for index, line in enumerate(lines):
        match = re.match(
            rf"^- {re.escape(label)}:[ \t]*(.*)$",
            line,
        )
        if match is None:
            continue
        if match.group(1).strip():
            return True
        for following in lines[index + 1 :]:
            if re.match(r"^- [^:]+:", following) or following.startswith("### "):
                return False
            if following.strip():
                return True
        return False
    return False


def write_json(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def definition_policy_errors(
    manifest: dict, report: dict
) -> list[str]:
    errors: list[str] = []
    policy = manifest.get("definition_policy", {})
    if not isinstance(policy, dict):
        return ["definition_policy must be an object"]
    if policy.get("status") != "enforced":
        errors.append("definition policy must be enforced")
    if policy.get("decision_required") is not False:
        errors.append("definition-substitution decision is still required")

    substitutions = policy.get("substitutions", [])
    if not isinstance(substitutions, list):
        return errors + ["definition_policy.substitutions must be a list"]

    approved: dict[str, dict] = {}
    required_fields = (
        "original_master_id",
        "original_term",
        "source_location",
        "source_status",
        "replacement_master_id",
        "replacement_term",
        "replacement_definition",
        "functional_rationale",
        "source",
        "unit",
        "period_and_frequency",
        "universe",
        "transformation",
        "known_deviation",
        "decision_id",
        "approved_at",
    )
    for index, substitution in enumerate(substitutions, start=1):
        if not isinstance(substitution, dict):
            errors.append(
                f"definition substitution {index} must be an object"
            )
            continue
        substitution_id = str(substitution.get("id", "")).strip()
        if not re.fullmatch(r"SUB-\d+", substitution_id):
            errors.append(
                f"definition substitution {index} has an invalid ID"
            )
            continue
        if substitution_id in approved:
            errors.append(
                f"definition substitution ID is duplicated: {substitution_id}"
            )
            continue
        for field in required_fields:
            if not str(substitution.get(field, "")).strip():
                errors.append(
                    f"{substitution_id}: {field} is required"
                )
        for field in ("original_master_id", "replacement_master_id"):
            if not re.fullmatch(
                r"D-\d+", str(substitution.get(field, "")).strip()
            ):
                errors.append(
                    f"{substitution_id}: {field} must use D-NNN"
                )
        if not re.fullmatch(
            r"Q-\d+", str(substitution.get("decision_id", "")).strip()
        ):
            errors.append(
                f"{substitution_id}: decision_id must use Q-NNN"
            )
        if substitution.get("source_status") not in {
            "missing",
            "underspecified",
            "conflicting",
        }:
            errors.append(
                f"{substitution_id}: source_status must be missing, "
                "underspecified, or conflicting"
            )
        if (
            str(substitution.get("original_master_id", "")).strip()
            == str(substitution.get("replacement_master_id", "")).strip()
        ):
            errors.append(
                f"{substitution_id}: replacement_master_id must be a new field"
            )
        affected_figures = substitution.get("affected_figures", [])
        if not isinstance(affected_figures, list) or not affected_figures:
            errors.append(
                f"{substitution_id}: affected_figures must be a non-empty list"
            )
        elif any(not str(figure).strip() for figure in affected_figures):
            errors.append(
                f"{substitution_id}: affected_figures cannot contain blanks"
            )
        if substitution.get("user_approved") is not True:
            errors.append(
                f"{substitution_id}: explicit user approval is required"
            )
        if substitution.get("status") != "approved":
            errors.append(
                f"{substitution_id}: status must be approved"
            )
        approved[substitution_id] = substitution

    figures_by_id = {
        str(figure.get("id")): figure
        for figure in manifest.get("figures", [])
        if isinstance(figure, dict) and str(figure.get("id", "")).strip()
    }
    for substitution_id, substitution in approved.items():
        for figure_id in substitution.get("affected_figures", []):
            figure = figures_by_id.get(str(figure_id))
            if figure is None:
                continue
            declared = figure.get("definition_substitutions", [])
            if substitution_id not in declared:
                errors.append(
                    f"{figure_id}: affected substitution {substitution_id} "
                    "is not recorded on the figure"
                )
    for figure_id, figure in figures_by_id.items():
        declared = figure.get("definition_substitutions", [])
        if not isinstance(declared, list):
            errors.append(
                f"{figure_id}: definition_substitutions must be a list"
            )
            continue
        for substitution_id in declared:
            if str(substitution_id) not in approved:
                errors.append(
                    f"{figure_id}: unknown or unapproved substitution "
                    f"{substitution_id}"
                )

    for item in report.get("items", []):
        item_id = str(item.get("id", "unknown"))
        basis = item.get("definition_basis")
        if basis not in ALLOWED_DEFINITION_BASES:
            errors.append(
                f"{item_id}: definition_basis must be source_explicit or "
                "approved_substitution"
            )
            continue
        substitution_id = str(item.get("substitution_id") or "").strip()
        if basis == "source_explicit":
            if substitution_id:
                errors.append(
                    f"{item_id}: source_explicit data cannot reference "
                    "a substitution"
                )
            continue
        if not substitution_id:
            errors.append(
                f"{item_id}: approved_substitution requires substitution_id"
            )
            continue
        substitution = approved.get(substitution_id)
        if substitution is None:
            errors.append(
                f"{item_id}: substitution {substitution_id} is missing "
                "or not approved"
            )
            continue
        recorded_definition = str(
            item.get("replacement_definition", "")
        ).strip()
        approved_definition = str(
            substitution.get("replacement_definition", "")
        ).strip()
        if not recorded_definition:
            errors.append(
                f"{item_id}: replacement_definition is required"
            )
        elif recorded_definition != approved_definition:
            errors.append(
                f"{item_id}: replacement definition does not match "
                f"{substitution_id}"
            )
    return errors


def data_integrity_errors(repro_dir: Path, manifest: dict) -> list[str]:
    report_path = repro_dir / "data_integrity.json"
    if not report_path.is_file():
        return ["missing data_integrity.json; run /reprospec:plan first"]

    try:
        report = load_json(report_path)
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read data_integrity.json: {exc}"]

    errors: list[str] = []
    if report.get("status") != "complete":
        errors.append(
            "data integrity status must be complete before locking"
        )
    for index, issue in enumerate(report.get("blocking_issues", []), start=1):
        errors.append(f"data integrity blocking issue {index}: {issue}")

    for item in report.get("items", []):
        item_id = str(item.get("id", "unknown"))
        source_path = repro_dir.parent.parent / str(item.get("path", ""))
        if not source_path.is_file():
            errors.append(f"{item_id}: source file does not exist")
        else:
            expected_hash = str(item.get("sha256", ""))
            if not expected_hash:
                errors.append(f"{item_id}: source hash is missing")
            elif sha256(source_path) != expected_hash:
                errors.append(f"{item_id}: source file changed after inspection")
        if item.get("present") is not True:
            errors.append(f"{item_id}: source file is missing")
        if item.get("inspection_status") not in ALLOWED_INSPECTION_STATUSES:
            errors.append(f"{item_id}: preliminary inspection is incomplete")
        if str(item.get("origin", "unknown")).strip().lower() in {"", "unknown"}:
            errors.append(f"{item_id}: origin has not been confirmed")
        if not str(item.get("origin_evidence", "")).strip():
            errors.append(f"{item_id}: origin evidence is required")
        if item.get("reliability") not in ALLOWED_RELIABILITY:
            errors.append(f"{item_id}: reliability has not been confirmed")
        if not str(item.get("reliability_evidence", "")).strip():
            errors.append(f"{item_id}: reliability evidence is required")
        if item.get("reliability") == "low" and not item.get("quality_risks"):
            errors.append(f"{item_id}: low reliability requires documented risks")
        if item.get("definition_alignment") != "aligned":
            errors.append(f"{item_id}: data definition is not aligned")
        if item.get("user_confirmed") is not True:
            errors.append(f"{item_id}: user confirmation is required")
    return errors + definition_policy_errors(manifest, report)


def time_range_errors(manifest: dict) -> list[str]:
    policy = manifest.get("time_range_policy", {})
    if not isinstance(policy, dict):
        return ["time_range_policy must be an object"]

    errors: list[str] = []
    if policy.get("status") != "confirmed":
        errors.append("time range status must be confirmed")
    if policy.get("selection") not in ALLOWED_TIME_RANGE_MODES:
        errors.append(
            "time range selection must be publication_period or through_today"
        )
    if policy.get("user_confirmed") is not True:
        errors.append("time range requires explicit user confirmation")
    if not str(policy.get("confirmed_at", "")).strip():
        errors.append("time range confirmation timestamp is required")
    if not str(policy.get("timezone", "")).strip():
        errors.append("time range timezone is required")
    if not str(policy.get("basis", "")).strip():
        errors.append("time range basis is required")

    parsed_dates: dict[str, date] = {}
    for field in ("start_date", "end_date"):
        raw_value = str(policy.get(field, "")).strip()
        if not raw_value:
            errors.append(f"time range {field} is required")
            continue
        try:
            parsed_dates[field] = date.fromisoformat(raw_value)
        except ValueError:
            errors.append(f"time range {field} must use ISO YYYY-MM-DD")

    if (
        "start_date" in parsed_dates
        and "end_date" in parsed_dates
        and parsed_dates["end_date"] < parsed_dates["start_date"]
    ):
        errors.append("time range end_date must not precede start_date")
    return errors


def source_evidence_records(
    repro_dir: Path, manifest: dict
) -> tuple[list[str], dict[str, dict]]:
    errors: list[str] = []
    policy = manifest.get("source_evidence", {})
    if not isinstance(policy, dict):
        return ["source_evidence must be an object"], {}
    if policy.get("status") != "frozen":
        errors.append("source evidence must be frozen before locking")

    records: dict[str, dict] = {}
    for item in policy.get("items", []):
        if not isinstance(item, dict):
            errors.append("source_evidence item must be an object")
            continue
        figure_id = str(item.get("figure_id", "")).strip()
        if not figure_id:
            errors.append("source_evidence item has no figure_id")
            continue
        if figure_id in records:
            errors.append(f"{figure_id}: duplicate source_evidence item")
            continue
        if item.get("status") != "frozen":
            errors.append(f"{figure_id}: evidence pack is not frozen")
            continue
        path = repro_dir / str(item.get("path", ""))
        if not path.is_file():
            errors.append(f"{figure_id}: frozen evidence pack is missing")
            continue
        expected_hash = str(item.get("sha256", "")).strip()
        if not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
            errors.append(f"{figure_id}: evidence hash is invalid")
            continue
        if sha256(path) != expected_hash:
            errors.append(f"{figure_id}: evidence pack changed after freezing")
            continue
        records[figure_id] = item
    return errors, records


def figure_specification_records(
    repro_dir: Path,
    figures: list[dict],
    evidence_records: dict[str, dict],
) -> tuple[list[str], list[dict]]:
    errors: list[str] = []
    locked_records: list[dict] = []

    for figure in figures:
        figure_id = str(figure.get("id", "unknown"))
        item = evidence_records.get(figure_id)
        if item is None:
            errors.append(f"{figure_id}: no frozen evidence pack is approved")
            continue

        figure_dir = repro_dir / str(figure.get("path", ""))
        spec_path = figure_dir / "spec.md"
        if not spec_path.is_file():
            errors.append(f"{figure_id}: missing spec.md")
            continue

        actual_spec_hash = sha256(spec_path)
        detail = figure.get("detail_validation", {})
        if not isinstance(detail, dict) or detail.get("status") != "passed":
            errors.append(
                f"{figure_id}: detail validation has not passed; "
                "rerun /reprospec:detail"
            )
            continue
        if detail.get("spec_sha256") != actual_spec_hash:
            errors.append(
                f"{figure_id}: specification changed after Detail validation"
            )
            continue
        if detail.get("evidence_sha256") != str(item.get("sha256", "")):
            errors.append(
                f"{figure_id}: validated evidence hash differs from the freeze"
            )
            continue

        declared_evidence = figure.get("source_evidence", {})
        if not isinstance(declared_evidence, dict) or (
            declared_evidence.get("path") != item.get("path")
            or declared_evidence.get("sha256") != item.get("sha256")
            or declared_evidence.get("status") != "frozen"
        ):
            errors.append(
                f"{figure_id}: manifest evidence record differs from the freeze"
            )
            continue

        text = spec_path.read_text(encoding="utf-8")
        if PLACEHOLDER_RE.search(text):
            errors.append(f"{figure_id}: specification contains placeholders")
        if field_value(text, "Self-contained execution").lower() != "yes":
            errors.append(f"{figure_id}: specification is not self-contained")
        if (
            field_value(text, "Report reread for requirements").lower()
            != "prohibited"
        ):
            errors.append(
                f"{figure_id}: report reread for requirements is not prohibited"
            )
        if field_value(text, "Evidence pack SHA-256") != item.get("sha256"):
            errors.append(
                f"{figure_id}: specification evidence hash differs from the freeze"
            )

        steps = parse_runbook_steps(text)
        if len(steps) < 3:
            errors.append(
                f"{figure_id}: execution runbook has fewer than 3 steps"
            )
        expected_ids = [f"S{index:02d}" for index in range(1, len(steps) + 1)]
        actual_ids = [step_id for step_id, _ in steps]
        if actual_ids != expected_ids:
            errors.append(
                f"{figure_id}: runbook step IDs are not contiguous from S01"
            )
        for step_id, step_body in steps:
            missing_fields = [
                field
                for field in REQUIRED_STEP_FIELDS
                if not step_has_field(step_body, field)
            ]
            if missing_fields:
                errors.append(
                    f"{figure_id}: {step_id} is missing "
                    + ", ".join(missing_fields)
                )

        checklist = section_text(text, "## No-Reread Checklist")
        if len(re.findall(r"^\s*-\s+\[[xX]\]", checklist, re.MULTILINE)) < 5:
            errors.append(
                f"{figure_id}: No-Reread Checklist is incomplete"
            )
        if re.search(r"^\s*-\s+\[\s\]", checklist, re.MULTILINE):
            errors.append(
                f"{figure_id}: No-Reread Checklist contains unchecked items"
            )

        locked_records.append(
            {
                "figure_id": figure_id,
                "spec_path": str(spec_path.relative_to(repro_dir)).replace(
                    "\\", "/"
                ),
                "spec_sha256": actual_spec_hash,
                "evidence_path": str(item.get("path", "")),
                "evidence_sha256": str(item.get("sha256", "")),
                "runbook_steps": len(steps),
            }
        )

    return errors, locked_records


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, help="Workspace root")
    parser.add_argument("--paper-id", required=True, help="Stable paper ID")
    parser.add_argument("--version", required=True, help="Locked master version")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        paper_id = validate_identifier(args.paper_id, "paper-id")
        version = validate_identifier(args.version, "version")
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
    integrity_errors = data_integrity_errors(repro_dir, manifest)
    if integrity_errors:
        print(
            json.dumps(
                {
                    "error": "data integrity gate failed",
                    "blocking": integrity_errors,
                    "next": "/reprospec:plan",
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1

    range_errors = time_range_errors(manifest)
    if range_errors:
        print(
            json.dumps(
                {
                    "error": "reproduction time range gate failed",
                    "blocking": range_errors,
                    "next": "/reprospec:analyse",
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1

    figures = manifest.get("figures", [])
    evidence_errors, evidence_records = source_evidence_records(
        repro_dir, manifest
    )
    if evidence_errors:
        print(
            json.dumps(
                {
                    "error": "source evidence freeze gate failed",
                    "blocking": evidence_errors,
                    "next": "/reprospec:outline",
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1

    spec_errors, locked_figure_specs = figure_specification_records(
        repro_dir, figures, evidence_records
    )
    if spec_errors:
        print(
            json.dumps(
                {
                    "error": "self-contained figure specification gate failed",
                    "blocking": spec_errors,
                    "next": "/reprospec:detail",
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1

    locked_at = utc_now()
    manifest["master_spec"]["version"] = version
    manifest["master_spec"]["status"] = "locked"
    manifest["figures"] = [
        {
            **{
                key: value
                for key, value in figure.items()
                if key != "run_validation"
            },
            "master_spec_version": version,
        }
        for figure in figures
    ]
    completed = manifest["workflow"].setdefault("completed_stages", [])
    for stage in ("outline", "detail", "plan", "analyse"):
        if stage not in completed:
            completed.append(stage)
    manifest["workflow"]["active_stage"] = "analyse"
    manifest["workflow"]["next_stage"] = "reproduce"
    manifest["workflow"]["updated_at"] = locked_at
    manifest["data_plan"]["status"] = "ready"
    manifest.setdefault("data_integrity", {})["status"] = "complete"
    manifest["spec_lock"] = {
        "path": "spec_lock.json",
        "status": "locked",
        "locked_at": locked_at,
        "figure_specs": locked_figure_specs,
    }
    manifest["updated_at"] = locked_at
    write_json(manifest_path, manifest)

    lock_record = {
        "paper_id": paper_id,
        "master_spec_version": version,
        "locked_at": locked_at,
        "figure_count": len(figures),
        "figure_specs": locked_figure_specs,
        "source_evidence": {
            "status": "frozen",
            "count": len(evidence_records),
            "items": [
                {
                    "figure_id": figure_id,
                    "path": item.get("path"),
                    "sha256": item.get("sha256"),
                }
                for figure_id, item in sorted(evidence_records.items())
            ],
        },
        "data_plan_status": "ready",
        "data_integrity_status": "complete",
        "definition_substitutions": {
            "count": len(
                manifest.get("definition_policy", {}).get(
                    "substitutions", []
                )
            ),
            "ids": [
                substitution.get("id")
                for substitution in manifest.get("definition_policy", {}).get(
                    "substitutions", []
                )
            ],
            "replacement_master_ids": [
                substitution.get("replacement_master_id")
                for substitution in manifest.get("definition_policy", {}).get(
                    "substitutions", []
                )
            ],
        },
        "time_range": {
            "selection": manifest["time_range_policy"]["selection"],
            "start_date": manifest["time_range_policy"]["start_date"],
            "end_date": manifest["time_range_policy"]["end_date"],
            "timezone": manifest["time_range_policy"]["timezone"],
        },
    }
    write_json(repro_dir / "spec_lock.json", lock_record)

    print(json.dumps({"status": "locked", **lock_record}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
