#!/usr/bin/env python3
"""Assemble the final English ReproSpec delivery package."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path


ALLOWED_STATUSES = {"verified", "partial", "blocked"}
SECRET_NAMES = {".env", "credentials.json", "secrets.json"}
IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".tif",
    ".tiff",
    ".svg",
    ".pdf",
    ".eps",
}
TIME_RANGE_MODES = {"publication_period", "through_today"}
DEFINITION_REQUIRED_FIELDS = (
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


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_identifier(value: str, label: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", value):
        raise ValueError(f"{label} contains unsupported characters")
    return value


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def render_template(path: Path, values: dict[str, str]) -> str:
    content = path.read_text(encoding="utf-8")
    for key, value in values.items():
        content = content.replace("{{" + key + "}}", value)
    return content


def markdown_cell(value: object) -> str:
    text = str(value).replace("\r", " ").replace("\n", " ").strip()
    return text.replace("|", "\\|")


def find_figure_images(output_dir: Path) -> list[Path]:
    if not output_dir.is_dir():
        return []
    return sorted(
        path
        for path in output_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def flat_image_name(
    figure_id: str, output_dir: Path, image_path: Path
) -> str:
    relative = image_path.relative_to(output_dir).as_posix().replace("/", "__")
    return f"{figure_id}__{relative}"


def prepare_empty_directory(path: Path, expected_parent: Path) -> None:
    resolved = path.resolve()
    parent = expected_parent.resolve()
    if resolved.parent != parent:
        raise ValueError(
            f"refusing to clear directory outside {parent}: {resolved}"
        )
    if resolved.exists():
        shutil.rmtree(resolved)
    resolved.mkdir(parents=True)


def time_range_errors(manifest: dict) -> list[str]:
    policy = manifest.get("time_range_policy", {})
    if not isinstance(policy, dict):
        return ["time_range_policy must be an object"]

    errors: list[str] = []
    if policy.get("status") != "confirmed":
        errors.append("time range status must be confirmed")
    if policy.get("selection") not in TIME_RANGE_MODES:
        errors.append(
            "time range selection must be publication_period or through_today"
        )
    if policy.get("user_confirmed") is not True:
        errors.append("time range requires explicit user confirmation")
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, help="Workspace root")
    parser.add_argument("--paper-id", required=True, help="Stable paper ID")
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
    if not manifest_path.is_file():
        print(f"error: missing manifest: {manifest_path}", file=sys.stderr)
        return 1

    manifest = load_json(manifest_path)
    computation_policy = manifest.get("computation_policy", {})
    if (
        computation_policy.get("status") != "enforced"
        or computation_policy.get("published_values") != "comparison_only"
        or computation_policy.get("reproduction_inputs")
        != "approved_real_data_only"
    ):
        print(
            "error: computation-source policy is missing or not enforced",
            file=sys.stderr,
        )
        return 1
    range_errors = time_range_errors(manifest)
    if range_errors:
        print(
            json.dumps(
                {
                    "valid": False,
                    "errors": [
                        f"time_range_policy: {error}" for error in range_errors
                    ],
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1
    if manifest["master_spec"].get("status") != "locked":
        print("error: master specification is not locked", file=sys.stderr)
        return 1
    if manifest.get("data_integrity", {}).get("status") != "complete":
        print(
            "error: data integrity gate is not complete",
            file=sys.stderr,
        )
        return 1
    if not (repro_dir / "data_integrity.json").is_file():
        print("error: missing data_integrity.json", file=sys.stderr)
        return 1
    integrity_report = load_json(repro_dir / "data_integrity.json")
    data_plan = manifest.get("data_plan", {})
    if (
        data_plan.get("decision_required") is True
        or data_plan.get("status") == "decision_required"
    ):
        print(
            "error: unresolved supplement-or-skip data decision",
            file=sys.stderr,
        )
        return 1

    errors: list[str] = []
    definition_policy = manifest.get("definition_policy", {})
    if not isinstance(definition_policy, dict):
        errors.append("definition_policy must be an object")
        definition_policy = {}
    if definition_policy.get("status") != "enforced":
        errors.append("definition policy is not enforced")
    if definition_policy.get("decision_required") is not False:
        errors.append("definition-substitution decision is unresolved")
    definition_substitutions = definition_policy.get("substitutions", [])
    if not isinstance(definition_substitutions, list):
        errors.append("definition_policy.substitutions must be a list")
        definition_substitutions = []
    for index, substitution in enumerate(definition_substitutions, start=1):
        if not isinstance(substitution, dict):
            errors.append(
                f"definition substitution {index} must be an object"
            )
            continue
        substitution_id = str(substitution.get("id", f"record-{index}"))
        if substitution.get("status") != "approved":
            errors.append(
                f"{substitution_id}: definition substitution is not approved"
            )
        if substitution.get("user_approved") is not True:
            errors.append(
                f"{substitution_id}: definition substitution lacks "
                "user approval"
            )
        for field in DEFINITION_REQUIRED_FIELDS:
            if not str(substitution.get(field, "")).strip():
                errors.append(
                    f"{substitution_id}: {field} is required"
                )
        if not re.fullmatch(
            r"D-\d+",
            str(substitution.get("original_master_id", "")).strip(),
        ):
            errors.append(
                f"{substitution_id}: original_master_id must use D-NNN"
            )
        if not re.fullmatch(
            r"D-\d+",
            str(substitution.get("replacement_master_id", "")).strip(),
        ):
            errors.append(
                f"{substitution_id}: replacement_master_id must use D-NNN"
            )
        if not re.fullmatch(
            r"Q-\d+",
            str(substitution.get("decision_id", "")).strip(),
        ):
            errors.append(
                f"{substitution_id}: decision_id must use Q-NNN"
            )
        affected_figures = substitution.get("affected_figures", [])
        if not isinstance(affected_figures, list) or not affected_figures:
            errors.append(
                f"{substitution_id}: affected_figures must be a non-empty list"
            )
    figures_by_id = {
        str(figure.get("id")): figure
        for figure in manifest.get("figures", [])
        if isinstance(figure, dict) and str(figure.get("id", "")).strip()
    }
    for substitution in definition_substitutions:
        if not isinstance(substitution, dict):
            continue
        substitution_id = str(substitution.get("id", "unknown"))
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

    adjustments = manifest.get("adjustments", {})
    if not isinstance(adjustments, dict):
        errors.append("adjustments: manifest entry must be an object")
        adjustments = {}
    adjustment_history = adjustments.get("history", [])
    if not isinstance(adjustment_history, list):
        errors.append("adjustments: history must be a list")
        adjustment_history = []
    for index, record in enumerate(adjustment_history, start=1):
        if not isinstance(record, dict):
            errors.append(f"adjustments: record {index} must be an object")
            continue
        adjustment_id = str(record.get("id", f"record-{index}"))
        status = str(record.get("status", "draft"))
        if status != "completed":
            errors.append(
                f"adjustments: {adjustment_id} status {status} is unresolved"
            )
        if (
            record.get("computation_source")
            != "computed_from_approved_real_data"
        ):
            errors.append(
                f"adjustments: {adjustment_id} computation source is not "
                "verified from approved real data"
            )
    adjustment_log_path = repro_dir / str(
        adjustments.get("path", "adjustment_log.md")
    )
    if adjustment_history and not adjustment_log_path.is_file():
        errors.append("adjustments: missing adjustment_log.md")

    organization = manifest.get("organization", {})
    organization_record_path = repro_dir / str(
        organization.get("record", "data_organization.json")
    )
    organization_report_path = repro_dir / str(
        organization.get("report", "data_organization.md")
    )
    organization_inventory_path = repro_dir / str(
        organization.get("inventory", "data_inventory.csv")
    )
    organization_catalog_path = repro_dir / str(
        organization.get("catalog", "data_catalog.csv")
    )
    organized_dir = repro_dir / str(
        organization.get("organized_path", "data/organized")
    )
    disposition = str(organization.get("source_disposition", "pending"))
    disposition_requires_approval = disposition in {"move", "delete", "mixed"}
    canonical_formats = organization.get("canonical_formats", [])

    if organization.get("status") != "complete":
        errors.append(
            "organization: status "
            f"{organization.get('status', 'missing')} cannot be delivered"
        )
    if disposition not in {"retain", "move", "delete", "mixed"}:
        errors.append(f"organization: source disposition is {disposition}")
    if not isinstance(canonical_formats, list) or not canonical_formats:
        errors.append("organization: canonical_formats is missing or empty")
        canonical_formats = []
    if organization.get("canonical_checkpoint") is not True:
        errors.append("organization: canonical checkpoint is not complete")
    if disposition_requires_approval and organization.get(
        "user_approved"
    ) is not True:
        errors.append(
            "organization: original-data change is not user-approved"
        )
    if disposition_requires_approval and not str(
        organization.get("user_decision", "")
    ).strip():
        errors.append("organization: manifest lacks the user decision")
    for path, label in (
        (organization_record_path, "record"),
        (organization_report_path, "report"),
        (organization_inventory_path, "inventory"),
        (organization_catalog_path, "catalog"),
    ):
        if not path.is_file():
            errors.append(f"organization: missing {label} {path.name}")
    if not organized_dir.is_dir():
        errors.append("organization: missing canonical data directory")

    dataset_dirs = (
        sorted(path for path in organized_dir.iterdir() if path.is_dir())
        if organized_dir.is_dir()
        else []
    )
    declared_dataset_count = organization.get("dataset_count", 0)
    if not dataset_dirs:
        errors.append("organization: no canonical datasets found")
    try:
        declared_dataset_count = int(declared_dataset_count)
    except (TypeError, ValueError):
        errors.append("organization: dataset_count is not an integer")
        declared_dataset_count = 0
    if declared_dataset_count != len(dataset_dirs):
        errors.append(
            "organization: dataset_count does not match organized directory"
        )
    for dataset_dir in dataset_dirs:
        for required_name in (
            "schema.json",
            "metadata.json",
            "checksums.sha256",
        ):
            if not (dataset_dir / required_name).is_file():
                errors.append(
                    f"organization: {dataset_dir.name} lacks {required_name}"
                )
        if not any(
            path.is_file()
            and path.name.startswith("data.")
            for path in dataset_dir.iterdir()
        ):
            errors.append(
                f"organization: {dataset_dir.name} lacks a data file"
            )

    organization_verification: dict = {}
    if organization_record_path.is_file():
        try:
            organization_record = load_json(organization_record_path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"organization: invalid record: {exc}")
        else:
            organization_verification = organization_record.get(
                "verification", {}
            )
            if organization_record.get("canonical_checkpoint") is not True:
                errors.append(
                    "organization: record is not a canonical checkpoint"
                )
            record_formats = organization_record.get("canonical_formats", [])
            if not isinstance(record_formats, list) or not record_formats:
                errors.append(
                    "organization: record canonical_formats is missing or empty"
                )
            if organization_record.get("status") != "complete":
                errors.append(
                    "organization: record status is not complete"
                )
            if organization_verification.get("audit_ready") is not True:
                errors.append("organization: record is not audit-ready")
            if organization_verification.get("reuse_ready") is not True:
                errors.append("organization: record is not reuse-ready")
            if organization_verification.get(
                "required_coverage"
            ) is not True:
                errors.append(
                    "organization: required coverage is not verified"
                )
            if organization_verification.get("source_map_ready") is not True:
                errors.append(
                    "organization: source-map coverage is not verified"
                )
            if organization_verification.get(
                "load_without_raw"
            ) is not True:
                errors.append(
                    "organization: load-without-raw test is not verified"
                )
            if organization_record.get("source_disposition") != disposition:
                errors.append(
                    "organization: manifest and record disposition differ"
                )
            if disposition_requires_approval and organization_record.get(
                "user_approved"
            ) is not True:
                errors.append("organization: record lacks user approval")
            if disposition_requires_approval and not str(
                organization_record.get("user_decision", "")
            ).strip():
                errors.append("organization: record lacks the user decision")
            try:
                record_dataset_count = int(
                    organization_record.get("dataset_count", 0)
                )
            except (TypeError, ValueError):
                errors.append(
                    "organization: record dataset_count is not an integer"
                )
            else:
                if record_dataset_count != declared_dataset_count:
                    errors.append(
                        "organization: record dataset_count differs from manifest"
                    )

    figures = manifest.get("figures", [])
    source_evidence = manifest.get("source_evidence", {})
    if source_evidence.get("status") != "frozen":
        errors.append("source evidence is not frozen")
    evidence_items = source_evidence.get("items", [])
    if not isinstance(evidence_items, list):
        errors.append("source_evidence.items must be a list")
        evidence_items = []
    evidence_by_id = {
        str(item.get("figure_id")): item
        for item in evidence_items
        if isinstance(item, dict) and str(item.get("figure_id", "")).strip()
    }
    spec_lock = manifest.get("spec_lock", {})
    if not isinstance(spec_lock, dict) or spec_lock.get("status") != "locked":
        errors.append("spec_lock is missing or not locked")
        spec_lock = {}
    spec_lock_path = repro_dir / str(spec_lock.get("path", "spec_lock.json"))
    if not spec_lock_path.is_file():
        errors.append("spec_lock.json is missing")
    else:
        try:
            spec_lock_file = load_json(spec_lock_path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"spec_lock.json cannot be read: {exc}")
        else:
            if (
                spec_lock_file.get("figure_specs")
                != spec_lock.get("figure_specs")
            ):
                errors.append(
                    "manifest spec_lock differs from spec_lock.json"
                )
    locked_specs = spec_lock.get("figure_specs", [])
    if not isinstance(locked_specs, list):
        errors.append("spec_lock.figure_specs must be a list")
        locked_specs = []
    locked_spec_by_id = {
        str(item.get("figure_id")): item
        for item in locked_specs
        if isinstance(item, dict) and str(item.get("figure_id", "")).strip()
    }
    flat_images_by_figure: dict[str, list[tuple[Path, str]]] = {}
    flat_target_names: set[str] = set()
    for figure in figures:
        figure_id = str(figure.get("id", "unknown"))
        status = str(figure.get("status", "draft"))
        figure_dir = repro_dir / str(figure.get("path", ""))
        output_dir = figure_dir / "output"
        images = find_figure_images(output_dir)
        verification = figure.get("verification", {})
        if not isinstance(verification, dict):
            errors.append(f"{figure_id}: verification entry must be an object")
            verification = {}
        if (
            verification.get("computation_provenance")
            != "computed_from_approved_real_data"
        ):
            errors.append(
                f"{figure_id}: computation provenance is not verified "
                "from approved real data"
            )
        if status in {"verified", "partial"} or images:
            if verification.get("title_style_outcome") != "default":
                errors.append(
                    f"{figure_id}: title style is not verified as "
                    "matplotlib_notebook_default"
                )
            if (
                verification.get("source_derived_title_font_matching")
                is not False
            ):
                errors.append(
                    f"{figure_id}: source-derived title font matching is not "
                    "verified as false"
                )
            if verification.get("palette_outcome") not in {
                "matched",
                "not_applicable",
            }:
                errors.append(
                    f"{figure_id}: palette is not verified as matched or "
                    "evidenced not_applicable"
                )
            if not str(verification.get("palette_evidence", "")).strip():
                errors.append(
                    f"{figure_id}: palette verification evidence is missing"
                )
            challenge = verification.get("rework_challenge")
            if challenge is not None:
                if not isinstance(challenge, dict):
                    errors.append(
                        f"{figure_id}: rework challenge record must be an object"
                    )
                else:
                    challenge_status = challenge.get("status")
                    if challenge_status not in {
                        "issued",
                        "answered",
                        "resolved",
                        "blocked",
                    }:
                        errors.append(
                            f"{figure_id}: rework challenge status is invalid"
                        )
                    if (
                        verification.get("result") == "matched"
                        and challenge_status != "resolved"
                    ):
                        errors.append(
                            f"{figure_id}: matched result has an unresolved "
                            "rework challenge"
                        )
                    if (
                        status == "verified"
                        and challenge_status != "resolved"
                    ):
                        errors.append(
                            f"{figure_id}: verified status has an unresolved "
                            "rework challenge"
                        )
        if status not in ALLOWED_STATUSES:
            errors.append(f"{figure_id}: status {status} cannot be delivered")
        if status in {"partial", "blocked"} and not (
            figure_dir / "limitations.md"
        ).is_file():
            errors.append(f"{figure_id}: {status} requires limitations.md")
        spec_path = figure_dir / "spec.md"
        if not spec_path.is_file():
            errors.append(f"{figure_id}: missing spec.md")
        else:
            actual_spec_hash = sha256(spec_path)
            detail = figure.get("detail_validation", {})
            locked_spec = locked_spec_by_id.get(figure_id, {})
            if (
                not isinstance(detail, dict)
                or detail.get("status") != "passed"
                or detail.get("spec_sha256") != actual_spec_hash
            ):
                errors.append(
                    f"{figure_id}: specification is not valid against Detail"
                )
            if locked_spec.get("spec_sha256") != actual_spec_hash:
                errors.append(
                    f"{figure_id}: specification hash differs from spec_lock"
                )

        evidence_item = evidence_by_id.get(figure_id)
        if not isinstance(evidence_item, dict):
            errors.append(f"{figure_id}: frozen evidence pack is not registered")
        else:
            evidence_path = repro_dir / str(evidence_item.get("path", ""))
            if not evidence_path.is_file():
                errors.append(f"{figure_id}: frozen evidence pack is missing")
            elif sha256(evidence_path) != str(evidence_item.get("sha256", "")):
                errors.append(
                    f"{figure_id}: evidence pack changed after freezing"
                )
            locked_spec = locked_spec_by_id.get(figure_id, {})
            if locked_spec.get("evidence_sha256") != evidence_item.get("sha256"):
                errors.append(
                    f"{figure_id}: evidence hash differs from spec_lock"
                )
        run_validation = figure.get("run_validation", {})
        if (
            not isinstance(run_validation, dict)
            or run_validation.get("status") != "passed"
            or run_validation.get("report_reread_for_requirements") is not False
            or run_validation.get("reread_events") != 0
        ):
            errors.append(
                f"{figure_id}: run-record validation has not passed without "
                "report reread events"
            )
        else:
            run_record_path = figure_dir / str(
                run_validation.get("run_record_path", "logs/run_record.json")
            )
            if not run_record_path.is_file():
                errors.append(f"{figure_id}: validated run_record.json is missing")
            elif (
                sha256(run_record_path)
                != run_validation.get("run_record_sha256")
            ):
                errors.append(
                    f"{figure_id}: run record changed after validation"
                )
        if status in {"verified", "partial"} and not images:
            errors.append(f"{figure_id}: no rendered image found in output/")
        flat_images_by_figure[figure_id] = []
        for image_path in images:
            target_name = flat_image_name(figure_id, output_dir, image_path)
            normalized_name = target_name.casefold()
            if normalized_name in flat_target_names:
                errors.append(
                    f"{figure_id}: duplicate flat image name {target_name}"
                )
                continue
            flat_target_names.add(normalized_name)
            flat_images_by_figure[figure_id].append((image_path, target_name))

    audit = manifest.get("audit", {})
    audit_dir = repro_dir / str(audit.get("path", "audits"))
    audit_report_path = repro_dir / str(
        audit.get("report", "audit_report.md")
    )
    if audit.get("status") != "complete":
        errors.append(
            f"audit: status {audit.get('status', 'missing')} cannot be delivered"
        )
    if not audit_report_path.is_file():
        errors.append(f"audit: missing report {audit_report_path.name}")
    if not audit_dir.is_dir():
        errors.append(f"audit: missing directory {audit_dir.name}")
    audit_figures = audit.get("figures", {})
    if not isinstance(audit_figures, dict):
        errors.append("audit: figures must be an object")
        audit_figures = {}
    for figure in figures:
        figure_id = str(figure.get("id", "unknown"))
        audit_entry = audit_figures.get(figure_id, {})
        if not isinstance(audit_entry, dict):
            errors.append(f"{figure_id}: invalid audit record")
            continue
        if audit_entry.get("status") != "complete":
            errors.append(
                f"{figure_id}: audit status "
                f"{audit_entry.get('status', 'missing')} cannot be delivered"
            )
        if audit_entry.get("computation_integrity") != "passed":
            errors.append(
                f"{figure_id}: computation integrity is not confirmed as passed"
            )
        if audit_entry.get("runbook_coverage") != "complete":
            errors.append(
                f"{figure_id}: runbook coverage is not confirmed as complete"
            )
        if audit_entry.get("report_reread_for_requirements") is not False:
            errors.append(
                f"{figure_id}: report reread for requirements is not false"
            )
        audit_path = repro_dir / str(audit_entry.get("path", ""))
        if not audit_path.is_file():
            errors.append(f"{figure_id}: missing audit Markdown")
    if errors:
        print(json.dumps({"valid": False, "errors": errors}, indent=2))
        return 1

    for item in repro_dir.rglob("*"):
        if item.is_file() and item.name.lower() in SECRET_NAMES:
            print(f"error: secret-like file found: {item}", file=sys.stderr)
            return 1

    final_dir = workspace / "figure-output" / paper_id
    final_dir.mkdir(parents=True, exist_ok=True)
    for generated_directory in ("figures", "figure_details"):
        try:
            prepare_empty_directory(
                final_dir / generated_directory,
                final_dir,
            )
        except (OSError, ValueError) as exc:
            print(
                f"error: cannot prepare {generated_directory}: {exc}",
                file=sys.stderr,
            )
            return 1
    for directory in (
        final_dir / "data",
        final_dir / "specs",
        final_dir / "evidence",
        final_dir / "comparison_reports",
        final_dir / "limitations",
        final_dir / "audits",
        final_dir / "logs",
    ):
        directory.mkdir(parents=True, exist_ok=True)

    shutil.copy2(repro_dir / "master_spec.md", final_dir / "specs" / "master_spec.md")
    if (repro_dir / "spec_lock.json").is_file():
        shutil.copy2(
            repro_dir / "spec_lock.json",
            final_dir / "specs" / "spec_lock.json",
        )
    if (repro_dir / "data_gaps.csv").is_file():
        shutil.copy2(repro_dir / "data_gaps.csv", final_dir / "data" / "data_gaps.csv")
    if (repro_dir / "data_integrity.json").is_file():
        shutil.copy2(
            repro_dir / "data_integrity.json",
            final_dir / "data" / "data_integrity.json",
        )
    if (repro_dir / "data_integrity.md").is_file():
        shutil.copy2(
            repro_dir / "data_integrity.md",
            final_dir / "data" / "data_integrity.md",
        )
    if (repro_dir / "rework_log.md").is_file():
        shutil.copy2(repro_dir / "rework_log.md", final_dir / "logs" / "rework_log.md")
    if adjustment_log_path.is_file():
        shutil.copy2(
            adjustment_log_path,
            final_dir / "logs" / "adjustment_log.md",
        )
    shutil.copytree(
        organized_dir,
        final_dir / "data" / "organized",
        dirs_exist_ok=True,
    )
    if organization.get("include_raw_in_delivery") is True:
        raw_dir = repro_dir / "data" / "raw"
        if raw_dir.is_dir():
            shutil.copytree(
                raw_dir,
                final_dir / "data" / "raw",
                dirs_exist_ok=True,
            )
    for path, target in (
        (
            organization_inventory_path,
            final_dir / "data" / "data_inventory.csv",
        ),
        (
            organization_catalog_path,
            final_dir / "data" / "data_catalog.csv",
        ),
        (
            organization_record_path,
            final_dir / "data" / "data_organization.json",
        ),
        (
            organization_report_path,
            final_dir / "data" / "data_organization.md",
        ),
    ):
        shutil.copy2(path, target)
    if (repro_dir / "logs").is_dir():
        shutil.copytree(repro_dir / "logs", final_dir / "logs", dirs_exist_ok=True)

    for figure in figures:
        figure_id = str(figure["id"])
        figure_dir = repro_dir / str(figure["path"])
        ignore = (
            None
            if organization.get("include_raw_in_delivery") is True
            else shutil.ignore_patterns("data")
        )
        shutil.copytree(
            figure_dir,
            final_dir / "figure_details" / figure_dir.name,
            dirs_exist_ok=True,
            ignore=ignore,
        )
        for image_path, target_name in flat_images_by_figure[figure_id]:
            shutil.copy2(
                image_path,
                final_dir / "figures" / target_name,
            )
        spec_target = final_dir / "specs" / figure_id
        spec_target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(figure_dir / "spec.md", spec_target / "spec.md")
        comparison = figure_dir / "comparison_report.md"
        if comparison.is_file():
            shutil.copy2(
                comparison,
                final_dir / "comparison_reports" / f"{figure_id}.md",
            )
        limitations = figure_dir / "limitations.md"
        if limitations.is_file():
            shutil.copy2(
                limitations,
                final_dir / "limitations" / f"{figure_id}.md",
            )
        audit_source = repro_dir / str(audit_figures[figure_id]["path"])
        shutil.copy2(
            audit_source,
            final_dir / "audits" / f"{figure_id}.md",
        )
        evidence_item = evidence_by_id.get(figure_id, {})
        evidence_source = repro_dir / str(evidence_item.get("path", ""))
        if evidence_source.is_file():
            shutil.copy2(
                evidence_source,
                final_dir / "evidence" / f"{figure_id}.md",
            )

    shutil.copy2(audit_report_path, final_dir / "audit_report.md")

    counts = Counter(str(figure.get("status", "draft")) for figure in figures)
    excluded_count = len(manifest.get("excluded_figures", []))
    rendered_figure_count = sum(
        1 for images in flat_images_by_figure.values() if images
    )
    runbook_complete_count = sum(
        1
        for figure in figures
        if figure.get("run_validation", {}).get("status") == "passed"
    )
    report_reread_events = sum(
        int(
            figure.get("run_validation", {}).get("reread_events", 0)
            or 0
        )
        for figure in figures
    )
    palette_pass_count = sum(
        1
        for figure in figures
        if flat_images_by_figure.get(str(figure.get("id", "unknown")))
        and figure.get("verification", {}).get("palette_outcome")
        in {"matched", "not_applicable"}
    )
    palette_failure_count = rendered_figure_count - palette_pass_count
    palette_status = "PASS" if palette_failure_count == 0 else "FAIL"
    integrity_items = integrity_report.get("items", [])
    integrity_counts = {
        "items": len(integrity_items),
        "origin_confirmed": sum(
            1
            for item in integrity_items
            if str(item.get("origin", "unknown")).strip().lower()
            not in {"", "unknown"}
        ),
        "reliability_confirmed": sum(
            1
            for item in integrity_items
            if item.get("reliability") in {"high", "medium", "low"}
        ),
        "aligned": sum(
            1
            for item in integrity_items
            if item.get("definition_alignment") == "aligned"
        ),
        "user_confirmed": sum(
            1
            for item in integrity_items
            if item.get("user_confirmed") is True
        ),
    }
    substitution_count = len(definition_substitutions)
    substitution_ids = ", ".join(
        str(substitution.get("id", ""))
        for substitution in definition_substitutions
        if str(substitution.get("id", "")).strip()
    )
    replacement_master_ids = ", ".join(
        str(substitution.get("replacement_master_id", ""))
        for substitution in definition_substitutions
        if str(substitution.get("replacement_master_id", "")).strip()
    )
    delivered_at = utc_now()
    figure_summary_rows = []
    for figure in figures:
        figure_id = str(figure["id"])
        verification = figure.get("verification", {})
        limitation = "None"
        if figure.get("status") in {"partial", "blocked"} or verification.get(
            "result"
        ) in {"partial", "mismatched", "blocked"}:
            limitation = f"[limitations/{figure_id}.md](limitations/{figure_id}.md)"
        implementation_result = " / ".join(
            str(value)
            for value in (
                verification.get("chart_type_outcome", "not available"),
                verification.get("title_style_outcome", "not available"),
                verification.get("title_alignment_outcome", "not available"),
                verification.get("palette_outcome", "not available"),
                verification.get("tolerance_outcome", "not available"),
            )
        )
        figure_summary_rows.append(
            "| "
            + " | ".join(
                markdown_cell(value)
                for value in (
                    f"{figure_id}: {figure.get('title', '')}",
                    figure.get("status", "unknown"),
                    verification.get("report_consistency", "not available"),
                    implementation_result,
                    verification.get("primary_attribution", "not available"),
                    limitation,
                )
            )
            + " |"
        )

    data_source_rows = []
    for item in integrity_items:
        source = str(item.get("path", "unknown"))
        lower_source = source.lower()
        if lower_source.endswith(".pdf"):
            vintage = "2021-09-10 report PDF"
        elif lower_source.endswith(".json"):
            vintage = "CNINFO extraction through 2026-09-12"
        else:
            vintage = str(item.get("version", "user-supplied frozen file"))
        data_source_rows.append(
            "| "
            + " | ".join(
                markdown_cell(value)
                for value in (
                    source,
                    vintage,
                    "User-supplied local file",
                    "Yes; frozen by SHA-256",
                    (
                        f"Integrity item `{item.get('id', 'unknown')}`; "
                        f"reliability `{item.get('reliability', 'unknown')}`"
                    ),
                )
            )
            + " |"
        )
    external_count = len(
        list((repro_dir / "data" / "raw" / "external").glob("*.parquet"))
    )
    if external_count:
        data_source_rows.append(
            "| "
            + " | ".join(
                markdown_cell(value)
                for value in (
                    "Tushare Pro frozen extracts",
                    f"{external_count} canonical parquet inputs",
                    "Provider credential supplied outside the package",
                    "Yes from retained inputs; refresh requires provider access",
                    "Approved under Q-004 and Q-005; raw extracts are excluded from delivery",
                )
            )
            + " |"
        )
    if not data_source_rows:
        data_source_rows.append(
            "| _No source records available_ |  |  |  |  |"
        )

    master_version = str(manifest["master_spec"]["version"])
    rework_history = manifest.get("rework", {}).get("history", [])
    latest_reruns = (
        ", ".join(rework_history[-1].get("rerun_targets", []))
        if rework_history
        else "None"
    )
    master_history_rows = [
        "| "
        + " | ".join(
            markdown_cell(value)
            for value in (
                master_version,
                "Not recorded",
                (
                    "Only the final locked version is present in the manifest; "
                    "rework and adjustment records are preserved separately "
                    "in logs/rework_log.md and logs/adjustment_log.md"
                ),
                latest_reruns,
            )
        )
        + " |"
    ]

    workspace_arg = str(workspace)
    reproduction_commands = "\n".join(
        [
            "```powershell",
            "# Run from work/001-equity-incentive-feature-stock-selection.",
            "# Set TUSHARE_PRO_KEY in the environment; never record its value.",
            "$env:TUSHARE_PRO_KEY = '<credential>'",
            f"$workspace = '{workspace_arg}'",
            "python src/acquire_tushare.py",
            "python src/build_base.py",
            "python src/build_features.py",
            "python src/render_figures.py",
            "python src/verify_figures.py",
            "python src/build_organized_data.py",
            "python src/build_audit_records.py",
            (
                "python D:\\Dev\\ReproSpec\\skills\\deliver\\scripts\\"
                "assemble_delivery.py --workspace $workspace "
                "--paper-id 001-equity-incentive-feature-stock-selection"
            ),
            "```",
        ]
    )

    verification_summary = manifest.get("verification_summary", {})
    limitation_lines = [
        (
            f"- Result status: `{counts.get('verified', 0)}` verified, "
            f"`{counts.get('partial', 0)}` partial, and "
            f"`{counts.get('blocked', 0)}` blocked. The "
            f"`{verification_summary.get('mismatched', 0)}` mismatched figures "
            "remain explicit and are not silently promoted."
        ),
        (
            "- The approved extension through `2026-09-12`, including Beijing "
            "Stock Exchange events, changes annual samples and rule-level "
            "returns relative to the paper's 2021 baseline."
        ),
        (
            "- The supplied `records.json` is a model-extracted CNINFO corpus "
            "with medium reliability; provider supplements and the documented "
            "CNINFO validation controls are required."
        ),
        (
            "- Raw source files are retained in the work directory but excluded "
            "from delivery under the approved `retain`, "
            "`include_raw_in_delivery=false` disposition."
        ),
    ]
    limitation_lines.extend(
        f"- Accepted limitation: {text}"
        for text in dict.fromkeys(
            limitation
            for item in rework_history
            for limitation in item.get("accepted_limitations", [])
        )
    )
    overall_limitations = "\n".join(limitation_lines)

    report_template = (
        Path(__file__).resolve().parents[1]
        / "assets"
        / "reproduction-report-template.md"
    )
    report = render_template(
        report_template,
        {
            "PAPER_ID": paper_id,
            "PAPER_TITLE": str(manifest["paper"].get("title", "")),
            "SOURCE": str(manifest["paper"].get("source", "")),
            "SOURCE_HASH": str(manifest["paper"].get("sha256", "not available")),
            "MASTER_VERSION": str(manifest["master_spec"]["version"]),
            "DELIVERED_AT": delivered_at,
            "DATA_INTEGRITY_STATUS": str(
                integrity_report.get("status", "unknown")
            ),
            "INTEGRITY_ITEMS": str(integrity_counts["items"]),
            "INTEGRITY_ORIGIN_CONFIRMED": str(
                integrity_counts["origin_confirmed"]
            ),
            "INTEGRITY_RELIABILITY_CONFIRMED": str(
                integrity_counts["reliability_confirmed"]
            ),
            "INTEGRITY_ALIGNED": str(integrity_counts["aligned"]),
            "INTEGRITY_USER_CONFIRMED": str(
                integrity_counts["user_confirmed"]
            ),
            "DEFINITION_SUBSTITUTION_COUNT": str(substitution_count),
            "DEFINITION_SUBSTITUTION_IDS": substitution_ids or "None",
            "DEFINITION_REPLACEMENT_MASTER_IDS": (
                replacement_master_ids or "None"
            ),
            "AUDITED_FIGURES": str(len(figures)),
            "AUDIT_COMPLETE": str(len(figures)),
            "AUDIT_BLOCKED": "0",
            "COMPUTATION_INTEGRITY_STATUS": "passed",
            "COMPUTATION_FIGURES_CHECKED": str(len(figures)),
            "COMPUTATION_VIOLATIONS": "0",
            "EVIDENCE_PACK_COUNT": str(len(evidence_by_id)),
            "SPEC_LOCK_STATUS": str(spec_lock.get("status", "missing")),
            "RUNBOOK_COMPLETE_COUNT": str(runbook_complete_count),
            "RUNBOOK_MISSING_COUNT": str(
                len(figures) - runbook_complete_count
            ),
            "REPORT_REREAD_EVENTS": str(report_reread_events),
            "TIME_RANGE_SELECTION": str(
                manifest["time_range_policy"]["selection"]
            ),
            "TIME_RANGE_START": str(
                manifest["time_range_policy"]["start_date"]
            ),
            "TIME_RANGE_END": str(manifest["time_range_policy"]["end_date"]),
            "TIME_RANGE_TIMEZONE": str(
                manifest["time_range_policy"]["timezone"]
            ),
            "DATA_ORGANIZATION_STATUS": str(
                organization.get("status", "unknown")
            ),
            "ORGANIZATION_DATASETS": str(declared_dataset_count),
            "ORGANIZATION_CANONICAL_FORMATS_TEXT": ", ".join(
                str(value) for value in canonical_formats
            ),
            "ORGANIZATION_CANONICAL_CHECKPOINT_TEXT": str(
                organization.get("canonical_checkpoint") is True
            ).lower(),
            "ORGANIZATION_SOURCES": str(
                organization.get(
                    "raw_source_count",
                    organization.get("source_file_count", 0),
                )
            ),
            "DATA_DISPOSITION": disposition,
            "ORGANIZATION_AUDIT_READY": str(
                organization_verification.get("audit_ready", False)
            ).lower(),
            "ORGANIZATION_REUSE_READY": str(
                organization_verification.get("reuse_ready", False)
            ).lower(),
            "FLAT_FIGURE_COUNT": str(len(flat_target_names)),
            "PALETTE_STATUS": palette_status,
            "PALETTE_RENDERED_COUNT": str(rendered_figure_count),
            "PALETTE_PASS_COUNT": str(palette_pass_count),
            "PALETTE_FAILURE_COUNT": str(palette_failure_count),
            "FIGURE_SUMMARY_ROWS": "\n".join(figure_summary_rows),
            "DATA_SOURCE_ROWS": "\n".join(data_source_rows),
            "MASTER_HISTORY_ROWS": "\n".join(master_history_rows),
            "REPRODUCTION_COMMANDS": reproduction_commands,
            "OVERALL_LIMITATIONS": overall_limitations,
        },
    )
    report = report.replace(
        "| Verified |  |",
        f"| Verified | {counts.get('verified', 0)} |",
    )
    report = report.replace(
        "| Partial |  |",
        f"| Partial | {counts.get('partial', 0)} |",
    )
    report = report.replace(
        "| Blocked |  |",
        f"| Blocked | {counts.get('blocked', 0)} |",
    )
    report = report.replace(
        "| Excluded schematics |  |",
        f"| Excluded schematics | {excluded_count} |",
    )
    report = report.replace("| Stale |  |", "| Stale | 0 |")
    report = report.replace("| Draft |  |", "| Draft | 0 |")
    (final_dir / "reproduction_report.md").write_text(
        report, encoding="utf-8", newline="\n"
    )

    manifest_template = (
        Path(__file__).resolve().parents[1]
        / "assets"
        / "delivery-manifest.json"
    )
    delivery_manifest = json.loads(
        render_template(
            manifest_template,
            {
                "PAPER_ID": paper_id,
                "PAPER_TITLE": str(manifest["paper"].get("title", "")),
                "MASTER_VERSION": str(manifest["master_spec"]["version"]),
                "DELIVERED_AT": delivered_at,
                "DATA_INTEGRITY_STATUS": str(
                    integrity_report.get("status", "unknown")
                ),
                "INTEGRITY_ITEMS": str(integrity_counts["items"]),
                "INTEGRITY_ORIGIN_CONFIRMED": str(
                    integrity_counts["origin_confirmed"]
                ),
                "INTEGRITY_RELIABILITY_CONFIRMED": str(
                    integrity_counts["reliability_confirmed"]
                ),
                "INTEGRITY_ALIGNED": str(integrity_counts["aligned"]),
                "INTEGRITY_USER_CONFIRMED": str(
                    integrity_counts["user_confirmed"]
                ),
                "DEFINITION_SUBSTITUTION_COUNT": str(substitution_count),
                "DEFINITION_SUBSTITUTION_IDS_JSON": json.dumps(
                    [
                        substitution.get("id")
                        for substitution in definition_substitutions
                    ]
                ),
                "DEFINITION_REPLACEMENT_MASTER_IDS_JSON": json.dumps(
                    [
                        substitution.get("replacement_master_id")
                        for substitution in definition_substitutions
                    ]
                ),
                "VERIFIED_COUNT": str(counts.get("verified", 0)),
                "PARTIAL_COUNT": str(counts.get("partial", 0)),
                "BLOCKED_COUNT": str(counts.get("blocked", 0)),
                "EXCLUDED_COUNT": str(excluded_count),
                "AUDIT_STATUS": str(audit.get("status", "unknown")),
                "AUDIT_FIGURE_COUNT": str(len(figures)),
                "COMPUTATION_INTEGRITY_STATUS": "passed",
                "COMPUTATION_FIGURES_CHECKED": str(len(figures)),
                "COMPUTATION_VIOLATIONS": "0",
                "TIME_RANGE_SELECTION": str(
                    manifest["time_range_policy"]["selection"]
                ),
                "TIME_RANGE_START": str(
                    manifest["time_range_policy"]["start_date"]
                ),
                "TIME_RANGE_END": str(
                    manifest["time_range_policy"]["end_date"]
                ),
                "TIME_RANGE_TIMEZONE": str(
                    manifest["time_range_policy"]["timezone"]
                ),
                "ORGANIZATION_STATUS": str(
                    organization.get("status", "unknown")
                ),
                "ORGANIZATION_DATASETS": str(declared_dataset_count),
                "ORGANIZATION_CANONICAL_FORMATS": json.dumps(
                    canonical_formats
                ),
                "ORGANIZATION_CANONICAL_CHECKPOINT": json.dumps(
                    organization.get("canonical_checkpoint") is True
                ),
                "DATA_DISPOSITION": disposition,
                "ORGANIZATION_USER_APPROVED": json.dumps(
                    organization.get("user_approved") is True
                ),
                "ORGANIZATION_AUDIT_READY": json.dumps(
                    organization_verification.get("audit_ready", False) is True
                ),
                "ORGANIZATION_REUSE_READY": json.dumps(
                    organization_verification.get("reuse_ready", False) is True
                ),
                "EVIDENCE_PACK_COUNT": str(len(evidence_by_id)),
                "SPEC_LOCK_STATUS": str(spec_lock.get("status", "missing")),
                "RUNBOOK_COMPLETE_COUNT": str(runbook_complete_count),
                "RUNBOOK_MISSING_COUNT": str(
                    len(figures) - runbook_complete_count
                ),
                "REPORT_REREAD_EVENTS": str(report_reread_events),
                "FLAT_FIGURE_COUNT": str(len(flat_target_names)),
            },
        )
    )
    delivery_manifest["artifacts"] = [
        "figures",
        "figure_details",
        "data",
        "specs",
        "specs/spec_lock.json",
        "evidence",
        "comparison_reports",
        "limitations",
        "audits",
        "data/organized",
        "data/data_inventory.csv",
        "data/data_catalog.csv",
        "data/data_organization.json",
        "data/data_organization.md",
        "logs",
        "logs/adjustment_log.md",
        "audit_report.md",
        "reproduction_report.md",
    ]
    write_json(final_dir / "delivery_manifest.json", delivery_manifest)

    manifest["delivery"] = {
        "status": "delivered",
        "path": str(final_dir),
        "delivered_at": delivered_at,
    }
    if "deliver" not in manifest["workflow"]["completed_stages"]:
        manifest["workflow"]["completed_stages"].append("deliver")
    manifest["workflow"]["active_stage"] = "deliver"
    manifest["workflow"]["next_stage"] = None
    manifest["workflow"]["updated_at"] = delivered_at
    manifest["updated_at"] = delivered_at
    write_json(manifest_path, manifest)

    print(
        json.dumps(
            {
                "status": "delivered",
                "output": str(final_dir),
                "flat_figure_directory": str(final_dir / "figures"),
                "flat_figure_count": len(flat_target_names),
                "figure_counts": delivery_manifest["figure_counts"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
