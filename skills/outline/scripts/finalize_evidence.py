#!/usr/bin/env python3
"""Validate and freeze figure source-evidence packs."""

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
    "## Source Snapshot",
    "## Evidence Rules",
    "## Figure Anatomy",
    "### Panel Evidence",
    "## Extracted Evidence",
    "## Data Semantics",
    "## Comparison Values",
    "## Palette Evidence",
    "## Open Questions and Resolutions",
    "## Freeze Summary",
)
PLACEHOLDER_PATTERN = re.compile(r"\{\{[^}]+\}\}")
REQUIRED_FREEZE_DECLARATIONS = {
    "All visible panels captured": {"yes"},
    "All axes and series captured": {"yes"},
    "All visible text captured": {"yes"},
    "All required definitions resolved": {"yes"},
    "All palette evidence captured or `not_applicable`": {
        "yes",
        "not_applicable",
    },
    "All comparison values captured": {"yes"},
    "Missing evidence": {"none"},
}


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


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def figure_ids(manifest: dict[str, Any], evidence_dir: Path) -> list[str]:
    ids: set[str] = set()
    for key in ("figures", "included_figures"):
        for figure in manifest.get(key, []):
            if isinstance(figure, dict) and str(figure.get("id", "")).strip():
                ids.add(str(figure["id"]))
            elif isinstance(figure, str) and figure.strip():
                ids.add(figure)
    for path in evidence_dir.glob("*.md"):
        ids.add(path.stem)
    return sorted(ids)


def freeze_evidence_text(path: Path, frozen_at: str) -> str:
    text = path.read_text(encoding="utf-8")
    text, status_count = re.subn(
        r"^- Evidence status:[ \t]*`draft`[ \t]*$",
        "- Evidence status: `frozen`",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    del status_count
    text, frozen_count = re.subn(
        r"^- Frozen at:[ \t]*.*$",
        f"- Frozen at: `{frozen_at}`",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    del frozen_count
    return text


def evidence_errors(path: Path, candidate_text: str | None = None) -> list[str]:
    if not path.is_file():
        return [f"missing evidence pack: {path}"]
    text = (
        candidate_text
        if candidate_text is not None
        else path.read_text(encoding="utf-8")
    )
    errors: list[str] = []
    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"{path.name}: missing heading {heading}")
    if PLACEHOLDER_PATTERN.search(text):
        errors.append(f"{path.name}: unresolved template placeholders")
    if not re.search(
        r"^- No report reread required:[ \t]*`yes`[ \t]*$",
        text,
        re.M,
    ):
        errors.append(
            f"{path.name}: Freeze Summary must set No report reread required to yes"
        )
    if not re.search(
        r"^- Evidence status:[ \t]*`frozen`[ \t]*$",
        text,
        re.M,
    ):
        errors.append(f"{path.name}: Evidence status must be frozen")
    if not re.search(
        r"^- Frozen at:[ \t]*`[^`]+`[ \t]*$",
        text,
        re.M,
    ):
        errors.append(f"{path.name}: Frozen at timestamp is required")
    for label, allowed in REQUIRED_FREEZE_DECLARATIONS.items():
        match = re.search(
            rf"^- {re.escape(label)}:[ \t]*`?([^`\n]+)`?[ \t]*$",
            text,
            re.MULTILINE,
        )
        if match is None:
            errors.append(f"{path.name}: missing Freeze Summary field {label}")
            continue
        value = match.group(1).strip().strip("`").lower()
        if value not in allowed:
            errors.append(
                f"{path.name}: {label} must be "
                + " or ".join(sorted(allowed))
            )
    if re.search(
        r"^\|(?:[^|\n]*\|)*\s*"
        r"(open|pending|unresolved|draft|blocked)\s*\|",
        text,
        re.MULTILINE | re.IGNORECASE,
    ):
        errors.append(f"{path.name}: unresolved Open Questions row remains")
    if "| E001 |" not in text:
        errors.append(f"{path.name}: at least one Extracted Evidence row is required")
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
    evidence_dir = repro_dir / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    ids = figure_ids(manifest, evidence_dir)
    if not ids:
        print(
            "error: no included figure IDs found; complete the outline first",
            file=sys.stderr,
        )
        return 1

    frozen_at = utc_now()
    errors: list[str] = []
    items: list[dict[str, Any]] = []
    pending_writes: dict[Path, str] = {}
    for figure_id in ids:
        path = evidence_dir / f"{figure_id}.md"
        candidate_text = None
        if path.is_file():
            candidate_text = freeze_evidence_text(path, frozen_at)
        item_errors = evidence_errors(path, candidate_text)
        if item_errors:
            errors.extend(item_errors)
            continue
        assert candidate_text is not None
        pending_writes[path] = candidate_text
        items.append(
            {
                "figure_id": figure_id,
                "path": str(path.relative_to(repro_dir)).replace("\\", "/"),
                "sha256": sha256_text(candidate_text),
                "status": "frozen",
            }
        )

    if errors:
        print(
            json.dumps(
                {
                    "status": "blocked",
                    "errors": errors,
                    "next": "/reprospec:outline",
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1

    for path, text in pending_writes.items():
        path.write_text(text, encoding="utf-8", newline="\n")

    manifest["source_evidence"] = {
        "status": "frozen",
        "directory": "evidence",
        "items": items,
        "updated_at": frozen_at,
    }
    manifest["updated_at"] = frozen_at
    write_json(manifest_path, manifest)
    print(
        json.dumps(
            {
                "status": "frozen",
                "count": len(items),
                "items": items,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
