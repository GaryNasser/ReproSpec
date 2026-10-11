#!/usr/bin/env python3
"""Validate self-contained ReproSpec figure specifications."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_HEADINGS = (
    "## Published Claim",
    "## Source Evidence Freeze",
    "### Specification Evidence Map",
    "### Rejected or Resolved Ambiguities",
    "## Data Contract",
    "### Input Artifact Contract",
    "### Global Transformation Contract",
    "## Panel and Chart Contract",
    "### Forbidden Chart Changes",
    "## Execution Runbook",
    "## Rendering Contract",
    "## Artifact Contract",
    "## Validation and Stop Conditions",
    "## Comparison Contract",
    "## No-Reread Checklist",
)
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
VAGUE_PATTERNS = {
    r"\bclean the data\b": "clean the data",
    r"\bhandle appropriately\b": "handle appropriately",
    r"\bnormalize as needed\b": "normalize as needed",
    r"\bstandard treatment\b": "standard treatment",
    r"\breasonable default\b": "reasonable default",
    r"\buse a suitable source\b": "use a suitable source",
    r"\badjust if necessary\b": "adjust if necessary",
    r"\bsimilar to the report\b": "similar to the report",
    r"\bTBD\b": "TBD",
    r"\bTODO\b": "TODO",
}
PLACEHOLDER_RE = re.compile(r"\{\{[^}]+\}\}")


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


def parse_steps(runbook: str) -> list[tuple[str, str]]:
    pattern = re.compile(
        r"^###\s+(S\d{2,3})\b[^\n]*\n(.*?)(?=^###\s+S\d{2,3}\b|^##\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    return [(match.group(1), match.group(2)) for match in pattern.finditer(runbook)]


def step_field(step_text: str, label: str) -> str:
    lines = step_text.splitlines()
    for index, line in enumerate(lines):
        match = re.match(
            rf"^- {re.escape(label)}:[ \t]*(.*)$",
            line,
        )
        if match is None:
            continue
        value = match.group(1).strip()
        if value:
            return value
        continuation: list[str] = []
        for following in lines[index + 1 :]:
            if re.match(r"^- [^:]+:", following) or following.startswith("### "):
                break
            continuation.append(following)
        return "\n".join(continuation).strip()
    return ""


def evidence_ids(text: str) -> set[str]:
    return set(re.findall(r"\bE\d{3,}\b", text))


def validate_spec_text(
    figure_id: str,
    spec_path: Path,
    evidence_path: Path,
    evidence_rel_path: str,
    evidence_sha: str,
    source_sha: str,
) -> tuple[list[str], dict[str, Any]]:
    if not spec_path.is_file():
        return [f"{figure_id}: missing specification: {spec_path}"], {}
    if not evidence_path.is_file():
        return [f"{figure_id}: missing evidence pack: {evidence_path}"], {}

    text = spec_path.read_text(encoding="utf-8")
    evidence_text = evidence_path.read_text(encoding="utf-8")
    errors: list[str] = []
    needs_outline = False

    if not re.search(
        rf"^# Figure Specification:[ \t]*{re.escape(figure_id)}[ \t]*$",
        text,
        re.MULTILINE,
    ):
        errors.append(f"{figure_id}: specification title does not match the figure ID")
    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"{figure_id}: missing heading {heading}")

    placeholders = sorted(set(PLACEHOLDER_RE.findall(text)))
    if placeholders:
        errors.append(
            f"{figure_id}: unresolved specification placeholders: "
            + ", ".join(placeholders)
        )
    if PLACEHOLDER_RE.search(evidence_text):
        errors.append(f"{figure_id}: evidence pack contains unresolved placeholders")

    evidence_path_value = field_value(text, "Source evidence pack")
    if not evidence_path_value:
        errors.append(f"{figure_id}: Source evidence pack is missing")
    else:
        if evidence_path_value.replace("\\", "/") != evidence_rel_path:
            errors.append(
                f"{figure_id}: Source evidence pack must be "
                f"{evidence_rel_path}"
            )

    recorded_evidence_sha = field_value(text, "Evidence pack SHA-256")
    if not re.fullmatch(r"[0-9a-f]{64}", recorded_evidence_sha):
        errors.append(f"{figure_id}: Evidence pack SHA-256 is not a SHA-256 digest")
    elif recorded_evidence_sha != evidence_sha:
        errors.append(f"{figure_id}: Evidence pack SHA-256 does not match the freeze record")

    recorded_source_sha = field_value(text, "Source SHA-256")
    if source_sha and recorded_source_sha != source_sha:
        errors.append(f"{figure_id}: Source SHA-256 does not match the manifest")
    if not source_sha and recorded_source_sha and not re.fullmatch(
        r"[0-9a-f]{64}", recorded_source_sha
    ):
        errors.append(f"{figure_id}: Source SHA-256 is not a SHA-256 digest")

    if field_value(text, "Self-contained execution").lower() != "yes":
        errors.append(f"{figure_id}: Self-contained execution must be yes")
    if (
        field_value(text, "Report reread for requirements").lower()
        != "prohibited"
    ):
        errors.append(
            f"{figure_id}: Report reread for requirements must be prohibited"
        )

    published_claim = section_text(text, "## Published Claim")
    if not evidence_ids(published_claim):
        errors.append(f"{figure_id}: Published Claim must cite at least one E### ID")

    evidence_map = section_text(text, "### Specification Evidence Map")
    map_refs = evidence_ids(evidence_map)
    if not map_refs:
        errors.append(f"{figure_id}: Specification Evidence Map has no E### references")

    frozen_ids = {
        match.group(1)
        for line in evidence_text.splitlines()
        if (match := re.match(r"^\|\s*(E\d{3,})\s*\|", line))
    }
    if not frozen_ids:
        errors.append(f"{figure_id}: evidence pack has no extracted E### rows")
    missing_evidence_ids = sorted(
        evidence_ids(text) - frozen_ids
    )
    if missing_evidence_ids:
        errors.append(
            f"{figure_id}: specification cites evidence IDs absent from the "
            "frozen pack: "
            + ", ".join(missing_evidence_ids)
        )

    runbook = section_text(text, "## Execution Runbook")
    steps = parse_steps(runbook)
    if len(steps) < 3:
        errors.append(f"{figure_id}: Execution Runbook must contain at least 3 steps")
    expected_step_ids = [f"S{index:02d}" for index in range(1, len(steps) + 1)]
    actual_step_ids = [step_id for step_id, _ in steps]
    if actual_step_ids != expected_step_ids:
        errors.append(
            f"{figure_id}: runbook step IDs must be contiguous from S01; "
            f"found {', '.join(actual_step_ids) or 'none'}"
        )

    for step_id, step_body in steps:
        if not re.search(rf"^###\s+{step_id}\s+\S", runbook, re.MULTILINE):
            errors.append(f"{figure_id}: {step_id} has no descriptive step name")
        for field in REQUIRED_STEP_FIELDS:
            value = step_field(step_body, field)
            if not value:
                errors.append(f"{figure_id}: {step_id} is missing {field}")
                continue
            if PLACEHOLDER_RE.search(value):
                errors.append(
                    f"{figure_id}: {step_id} {field} contains a template placeholder"
                )
            if field == "Formula or logic" and value.lower().startswith(
                "not_applicable"
            ):
                if len(value) < 25:
                    errors.append(
                        f"{figure_id}: {step_id} must explain why Formula or logic "
                        "is not_applicable"
                    )
            if field == "Failure action" and not re.search(
                r"\b(stop|return|blocked|block|skip)\b",
                value,
                re.IGNORECASE,
            ):
                errors.append(
                    f"{figure_id}: {step_id} Failure action must state stop, "
                    "return, block, or skip behavior"
                )
        for pattern, label in VAGUE_PATTERNS.items():
            if re.search(pattern, step_body, re.IGNORECASE):
                errors.append(
                    f"{figure_id}: {step_id} contains prohibited vague language "
                    f"'{label}'"
                )

    checklist = section_text(text, "## No-Reread Checklist")
    checked = re.findall(r"^\s*-\s+\[[xX]\]", checklist, re.MULTILINE)
    unchecked = re.findall(r"^\s*-\s+\[\s\]", checklist, re.MULTILINE)
    if len(checked) < 5:
        errors.append(f"{figure_id}: No-Reread Checklist has fewer than 5 checked items")
    if unchecked:
        errors.append(f"{figure_id}: No-Reread Checklist contains unchecked items")

    summary = {
        "spec_sha256": sha256(spec_path),
        "evidence_sha256": evidence_sha,
        "runbook_steps": len(steps),
        "evidence_ids": len(frozen_ids),
    }
    return errors, summary


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
    source_evidence = manifest.get("source_evidence", {})
    if source_evidence.get("status") != "frozen":
        print(
            json.dumps(
                {
                    "status": "blocked",
                    "errors": [
                        "source_evidence.status must be frozen before Detail "
                        "validation"
                    ],
                    "next": "/reprospec:outline",
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1

    evidence_items = source_evidence.get("items", [])
    evidence_by_id = {
        str(item.get("figure_id")): item
        for item in evidence_items
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
        print(
            f"error: unknown figure IDs: {', '.join(unknown)}",
            file=sys.stderr,
        )
        return 1

    errors: list[str] = []
    validations: list[dict[str, Any]] = []
    needs_outline = False
    source_sha = str(manifest.get("paper", {}).get("sha256") or "")
    for figure_id in selected_ids:
        figure = figure_by_id[figure_id]
        item = evidence_by_id.get(figure_id)
        if not isinstance(item, dict):
            errors.append(f"{figure_id}: no frozen evidence pack is registered")
            needs_outline = True
            continue
        if item.get("status") != "frozen":
            errors.append(f"{figure_id}: evidence pack status is not frozen")
            needs_outline = True
            continue
        evidence_path = repro_dir / str(item.get("path", ""))
        if not evidence_path.is_file():
            errors.append(f"{figure_id}: frozen evidence pack file is missing")
            needs_outline = True
            continue
        current_evidence_sha = sha256(evidence_path)
        if current_evidence_sha != str(item.get("sha256", "")):
            errors.append(
                f"{figure_id}: frozen evidence pack changed after Outline"
            )
            needs_outline = True
            continue
        figure_evidence = figure.get("source_evidence", {})
        if (
            isinstance(figure_evidence, dict)
            and figure_evidence
            and (
                figure_evidence.get("path") != item.get("path")
                or figure_evidence.get("sha256") != item.get("sha256")
            )
        ):
            errors.append(
                f"{figure_id}: manifest evidence hash differs from source_evidence"
            )
            needs_outline = True
            continue

        figure_dir = repro_dir / str(figure.get("path", ""))
        spec_path = figure_dir / "spec.md"
        item_errors, summary = validate_spec_text(
            figure_id,
            spec_path,
            evidence_path,
            str(item.get("path", "")).replace("\\", "/"),
            current_evidence_sha,
            source_sha,
        )
        errors.extend(item_errors)
        if not item_errors:
            validations.append(
                {
                    "figure_id": figure_id,
                    "spec_path": str(spec_path.relative_to(repro_dir)).replace(
                        "\\", "/"
                    ),
                    **summary,
                }
            )

    if errors:
        print(
            json.dumps(
                {
                    "status": "blocked",
                    "errors": errors,
                    "next": (
                        "/reprospec:outline"
                        if needs_outline
                        else "/reprospec:detail"
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
        figure_id = validation["figure_id"]
        item = evidence_by_id[validation["figure_id"]]
        updated_by_id[figure_id] = {
            "source_evidence": {
                "path": str(item.get("path", "")),
                "sha256": str(item.get("sha256", "")),
                "status": "frozen",
            },
            "detail_validation": {
                "status": "passed",
                "validated_at": validated_at,
                "spec_sha256": validation["spec_sha256"],
                "evidence_sha256": validation["evidence_sha256"],
                "runbook_steps": validation["runbook_steps"],
                "evidence_ids": validation["evidence_ids"],
            },
        }
    manifest["figures"] = [
        {
            **{
                key: value
                for key, value in figure.items()
                if key != "run_validation"
            },
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
