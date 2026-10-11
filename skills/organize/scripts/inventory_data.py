#!/usr/bin/env python3
"""Inventory raw and intermediate data used by one ReproSpec paper workspace."""

from __future__ import annotations

import argparse
import csv
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
        raise ValueError(f"{label} contains unsupported characters")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, help="Workspace root")
    parser.add_argument("--paper-id", required=True, help="Stable paper ID")
    parser.add_argument(
        "--path",
        action="append",
        default=[],
        help=(
            "Relative raw-source file or directory to inventory; "
            "repeat as needed"
        ),
    )
    parser.add_argument(
        "--output",
        default="data_inventory.csv",
        help="Output CSV path relative to the reproduction directory",
    )
    return parser.parse_args()


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def resolve_scan_paths(
    repro_dir: Path,
    workspace: Path,
    manifest: dict,
    requested: list[str],
) -> list[tuple[Path, str]]:
    if requested:
        resolved: list[tuple[Path, str]] = []
        for value in requested:
            candidate = Path(value)
            if not candidate.is_absolute():
                repro_candidate = repro_dir / candidate
                candidate = (
                    repro_candidate
                    if repro_candidate.exists()
                    else workspace / candidate
                )
            candidate = candidate.resolve()
            if not is_within(candidate, workspace):
                raise ValueError(f"path is outside the workspace: {value}")
            if not candidate.exists():
                raise ValueError(f"path does not exist: {value}")
            resolved.append((candidate, "requested"))
        return resolved

    paths: list[tuple[Path, str]] = []
    for name in ("raw", "interim", "processed"):
        data_dir = repro_dir / "data" / name
        if data_dir.is_dir():
            paths.append((data_dir, f"workspace-{name}"))
    inputs_dir = workspace / "inputs"
    if inputs_dir.is_dir():
        paths.append((inputs_dir, "workspace-inputs"))
    for figure in manifest.get("figures", []):
        figure_data = repro_dir / str(figure.get("path", "")) / "data"
        if figure_data.is_dir():
            paths.append((figure_data, f"figure:{figure.get('id', 'unknown')}"))
    return paths


def display_path(path: Path, repro_dir: Path, workspace: Path) -> str:
    if is_within(path, repro_dir):
        return path.relative_to(repro_dir).as_posix()
    return (Path("workspace") / path.relative_to(workspace)).as_posix()


def iter_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(
        item
        for item in path.rglob("*")
        if item.is_file() and not item.is_symlink() and item.name != ".gitkeep"
    )


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

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    try:
        scan_paths = resolve_scan_paths(
            repro_dir, workspace, manifest, args.path
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    output = Path(args.output)
    if not output.is_absolute():
        output = repro_dir / output
    output = output.resolve()
    if not is_within(output, repro_dir):
        print("error: output must be inside the reproduction directory", file=sys.stderr)
        return 2

    records = []
    seen_paths: set[Path] = set()
    for scan_path, scope in scan_paths:
        for path in iter_files(scan_path):
            resolved = path.resolve()
            if resolved in seen_paths:
                continue
            seen_paths.add(resolved)
            stat = resolved.stat()
            records.append(
                {
                    "path": display_path(resolved, repro_dir, workspace),
                    "scope": scope,
                    "size_bytes": stat.st_size,
                    "sha256": sha256(resolved),
                    "duplicate_of": "",
                    "modified_at": datetime.fromtimestamp(
                        stat.st_mtime, timezone.utc
                    )
                    .replace(microsecond=0)
                    .isoformat(),
                }
            )

    first_by_hash: dict[str, str] = {}
    for record in records:
        digest = str(record["sha256"])
        if digest in first_by_hash:
            record["duplicate_of"] = first_by_hash[digest]
        else:
            first_by_hash[digest] = str(record["path"])

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "path",
                "scope",
                "size_bytes",
                "sha256",
                "duplicate_of",
                "modified_at",
            ],
        )
        writer.writeheader()
        writer.writerows(records)

    print(
        json.dumps(
            {
                "status": "inventoried",
                "output": str(output),
                "files": len(records),
                "bytes": sum(int(record["size_bytes"]) for record in records),
                "duplicates": sum(
                    1 for record in records if record["duplicate_of"]
                ),
                "updated_at": utc_now(),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
