#!/usr/bin/env python3
"""Create one detailed ReproSpec figure workspace."""

from __future__ import annotations

import argparse
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


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "figure"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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
    parser.add_argument("--figure-id", required=True, help="Figure ID such as F001")
    parser.add_argument("--title", required=True, help="Figure title")
    parser.add_argument("--source-page", default="", help="Source location")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        paper_id = validate_identifier(args.paper_id, "paper-id")
        figure_id = validate_identifier(args.figure_id, "figure-id")
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
            "error: source evidence must be frozen before a figure specification "
            "can be created; return to /reprospec:outline",
            file=sys.stderr,
        )
        return 1
    evidence_items = source_evidence.get("items", [])
    evidence_item = next(
        (
            item
            for item in evidence_items
            if isinstance(item, dict)
            and str(item.get("figure_id", "")) == figure_id
        ),
        None,
    )
    if not isinstance(evidence_item, dict):
        print(
            f"error: missing frozen evidence pack for {figure_id}; "
            "return to /reprospec:outline",
            file=sys.stderr,
        )
        return 1

    figure_slug = slugify(args.title)
    figure_dir = repro_dir / "figures" / f"{figure_id}_{figure_slug}"
    if figure_dir.exists():
        print(f"error: figure directory already exists: {figure_dir}", file=sys.stderr)
        return 1

    for directory in (
        figure_dir / "data",
        figure_dir / "src",
        figure_dir / "output",
        figure_dir / "logs",
        figure_dir / "pixel_evidence",
    ):
        directory.mkdir(parents=True, exist_ok=True)

    template_path = Path(__file__).resolve().parents[1] / "assets" / "figure-spec-template.md"
    content = template_path.read_text(encoding="utf-8")
    replacements = {
        "{{FIGURE_ID}}": figure_id,
        "{{FIGURE_TITLE}}": args.title,
        "{{FIGURE_SLUG}}": figure_slug,
        "{{PAPER_ID}}": paper_id,
        "{{SOURCE_EVIDENCE_PACK}}": str(evidence_item.get("path", "")),
        "{{SOURCE_SHA256}}": str(manifest.get("paper", {}).get("sha256") or ""),
        "{{EVIDENCE_PACK_SHA256}}": str(
            evidence_item.get("sha256", "")
        ),
    }
    for key, value in replacements.items():
        content = content.replace(key, value)
    (figure_dir / "spec.md").write_text(content, encoding="utf-8", newline="\n")

    manifest["figures"].append(
        {
            "id": figure_id,
            "title": args.title,
            "source_page": args.source_page,
            "path": str(figure_dir.relative_to(repro_dir)).replace("\\", "/"),
            "status": "draft",
            "master_spec_version": manifest["master_spec"]["version"],
            "master_dependencies": [],
            "definition_substitutions": [],
            "source_evidence": {
                "path": str(evidence_item.get("path", "")),
                "sha256": str(evidence_item.get("sha256", "")),
                "status": "frozen",
            },
            "detail_validation": {
                "status": "pending",
                "validated_at": None,
                "spec_sha256": None,
                "evidence_sha256": None,
                "runbook_steps": 0,
            },
        }
    )
    manifest["workflow"]["active_stage"] = "detail"
    manifest["workflow"]["next_stage"] = "detail"
    manifest["workflow"]["updated_at"] = utc_now()
    manifest["updated_at"] = utc_now()
    write_json(manifest_path, manifest)

    print(
        json.dumps(
            {
                "status": "created",
                "figure_id": figure_id,
                "figure_dir": str(figure_dir),
                "spec": str(figure_dir / "spec.md"),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
