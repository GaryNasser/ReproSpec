#!/usr/bin/env python3
"""Begin one traceable ReproSpec rework round."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


ALLOWED_CAUSE_TYPES = {
    "data",
    "outline",
    "detail",
    "implementation",
    "style",
    "pixel",
    "impossible",
}
REQUIRED_RESPONSE_FIELDS = (
    "cause_type",
    "causal_evidence",
    "rejected_alternatives",
    "affected_lineage_or_code",
    "minimum_change",
    "falsification_test",
    "expected_effect",
    "acceptance_check",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def validate_identifier(value: str, label: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", value):
        raise ValueError(f"{label} contains unsupported characters")
    return value


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def has_content(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def load_challenge(
    challenge_path: Path,
    figure_id: str,
) -> tuple[dict | None, list[str]]:
    errors: list[str] = []
    if not challenge_path.is_file():
        return None, [f"missing challenge: {challenge_path}"]
    try:
        challenge = load_json(challenge_path)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return None, [f"invalid challenge JSON: {exc}"]
    if not isinstance(challenge, dict):
        return None, ["challenge must be a JSON object"]

    challenge_id = challenge.get("challenge_id")
    if not isinstance(challenge_id, str) or not re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9._-]*", challenge_id
    ):
        errors.append("challenge_id is missing or invalid")
    if challenge.get("figure_id") != figure_id:
        errors.append(
            f"challenge figure_id must be {figure_id!r}"
        )
    if challenge.get("status") != "issued":
        errors.append("challenge status must be issued")
    if not has_content(challenge.get("question")):
        errors.append("challenge question is missing")

    deviation = challenge.get("deviation")
    if not isinstance(deviation, dict):
        errors.append("challenge deviation must be an object")
    else:
        if deviation.get("kind") not in {
            "quantitative",
            "structural",
            "rendering",
        }:
            errors.append("challenge deviation kind is invalid")
        if not has_content(deviation.get("summary")):
            errors.append("challenge deviation summary is missing")
        if not has_content(deviation.get("evidence_paths")):
            errors.append("challenge deviation evidence_paths is empty")
        if not has_content(deviation.get("acceptance_check")):
            errors.append("challenge deviation acceptance_check is empty")

    response = challenge.get("response")
    if not isinstance(response, dict):
        errors.append("challenge response must be an object")
    else:
        for field in REQUIRED_RESPONSE_FIELDS:
            if not has_content(response.get(field)):
                errors.append(f"challenge response field {field} is empty")
        if response.get("cause_type") not in ALLOWED_CAUSE_TYPES:
            errors.append("challenge response cause_type is invalid")
        elif response.get("cause_type") == "impossible":
            errors.append(
                "an impossible cause must set the challenge status to blocked"
            )
    return challenge, errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, help="Workspace root")
    parser.add_argument("--paper-id", required=True, help="Stable paper ID")
    parser.add_argument("--reason", required=True, help="Reason for this round")
    parser.add_argument(
        "--root-cause",
        default="unresolved",
        help="Root cause summary",
    )
    parser.add_argument("--cause-type", default="unknown", help="Cause classification")
    parser.add_argument(
        "--stale",
        action="append",
        default=[],
        help="Figure ID to mark stale; repeat for multiple figures",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        paper_id = validate_identifier(args.paper_id, "paper-id")
        stale_ids = [
            validate_identifier(value, "stale figure ID") for value in args.stale
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
    figure_map = {str(figure.get("id")): figure for figure in manifest["figures"]}
    missing = sorted(set(stale_ids) - set(figure_map))
    if missing:
        print(f"error: unknown figure IDs: {', '.join(missing)}", file=sys.stderr)
        return 1

    round_number = int(manifest["rework"].get("round", 0)) + 1
    timestamp = utc_now()
    challenge_records: list[tuple[Path, dict]] = []
    challenge_errors: list[str] = []
    for figure_id in stale_ids:
        figure = figure_map[figure_id]
        figure_dir = repro_dir / str(figure.get("path", ""))
        challenge_path = figure_dir / "rework_challenge.json"
        challenge, errors = load_challenge(challenge_path, figure_id)
        if errors:
            challenge_errors.extend(
                f"{figure_id}: {error}" for error in errors
            )
            continue
        assert challenge is not None
        challenge_records.append((challenge_path, challenge))
    if challenge_errors:
        print(
            json.dumps(
                {"valid": False, "errors": challenge_errors},
                indent=2,
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 1

    challenge_summaries = []
    for challenge_path, challenge in challenge_records:
        response = challenge["response"]
        challenge["status"] = "answered"
        challenge["updated_at"] = timestamp
        challenge.setdefault("history", []).append(
            {
                "phase": "rework",
                "status": "answered",
                "round": round_number,
                "at": timestamp,
                "cause_type": response["cause_type"],
                "falsification_test": response["falsification_test"],
                "response": response,
            }
        )
        write_json(challenge_path, challenge)
        challenge_summaries.append(
            {
                "challenge_id": challenge["challenge_id"],
                "path": str(challenge_path),
                "cause_type": response["cause_type"],
            }
        )

    for figure_id in stale_ids:
        figure_map[figure_id]["status"] = "stale"

    event_cause_type = (
        challenge_summaries[0]["cause_type"]
        if len(challenge_summaries) == 1
        else (
            "mixed"
            if challenge_summaries
            else args.cause_type
        )
    )
    event = {
        "round": round_number,
        "started_at": timestamp,
        "reason": args.reason,
        "root_cause": args.root_cause,
        "cause_type": event_cause_type,
        "challenges": challenge_summaries,
        "stale_figures": stale_ids,
    }
    manifest["rework"]["round"] = round_number
    manifest["rework"].setdefault("history", []).append(event)
    manifest["workflow"]["active_stage"] = "rework"
    manifest["workflow"]["next_stage"] = "reproduce" if stale_ids else "adjust"
    manifest["workflow"]["updated_at"] = timestamp
    manifest["updated_at"] = timestamp
    write_json(manifest_path, manifest)

    log_path = repro_dir / "rework_log.md"
    if not log_path.exists():
        log_path.write_text("# Rework Log\n\n", encoding="utf-8", newline="\n")
    with log_path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(
            f"\n## Round {round_number}\n\n"
            "### Identity\n\n"
            f"- Date: {timestamp}\n"
            f"- Cause type: {event_cause_type}\n"
            f"- Root cause: {args.root_cause}\n"
            f"- Reason: {args.reason}\n"
            f"- Challenges: "
            f"{', '.join(item['challenge_id'] for item in challenge_summaries) or 'none'}\n"
            f"- Stale figures: {', '.join(stale_ids) or 'none'}\n"
            "- Status: in progress\n"
        )

    print(json.dumps(event, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
