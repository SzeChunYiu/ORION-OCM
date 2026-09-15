#!/usr/bin/env python3
"""Fail-closed, idempotent reconciliation for HST issue #233."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
DEFAULT_SPEC = HERE / "ISSUE_233_RECONCILIATION_V1.json"
API_ROOT = "https://api.github.com"


class ReconcileError(RuntimeError):
    pass


def canonical_sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def api_json(method: str, url: str, token: str, payload: dict | None = None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        url,
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "orion-ocm-hst-issue-233-reconciler-v1",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise ReconcileError(f"GitHub API {method} {url} failed: {exc.code}: {body}") from exc


def locate_section(body: str, anchor: str) -> tuple[int, int]:
    count = body.count(anchor)
    if count != 1:
        raise ReconcileError(f"anchor must occur exactly once: {anchor!r}; found {count}")
    start = body.index(anchor)
    first_line_end = body.find("\n", start)
    heading_line = body[start:first_line_end if first_line_end != -1 else len(body)]
    level = len(heading_line) - len(heading_line.lstrip("#"))
    if level <= 0:
        raise ReconcileError(f"anchor is not a Markdown heading: {anchor!r}")

    cursor = first_line_end + 1 if first_line_end != -1 else len(body)
    end = len(body)
    while cursor < len(body):
        next_nl = body.find("\n", cursor)
        if next_nl == -1:
            next_nl = len(body)
        line = body[cursor:next_nl]
        if line.startswith("#"):
            next_level = len(line) - len(line.lstrip("#"))
            if 0 < next_level <= level:
                end = cursor
                break
        cursor = next_nl + 1
    return start, end


def reconcile_body(body: str, spec: dict) -> tuple[str, list[dict]]:
    if spec.get("schema") != "HST_ISSUE_233_RECONCILIATION_V1":
        raise ReconcileError("unknown reconciliation schema")
    if spec.get("issue") != 233:
        raise ReconcileError("this reconciler is intentionally pinned to issue 233")

    updated = body
    rows: list[dict] = []
    for index, row in enumerate(spec.get("replacements", []), start=1):
        anchor, old, new = row.get("anchor"), row.get("old"), row.get("new")
        if not all(isinstance(value, str) and value for value in (anchor, old, new)):
            raise ReconcileError(f"replacement {index} is malformed")
        if old == new or "- [ ]" not in old or "- [x]" not in new:
            raise ReconcileError(f"replacement {index} is not an unchecked->checked transition")

        start, end = locate_section(updated, anchor)
        segment = updated[start:end]
        old_count = segment.count(old)
        new_count = segment.count(new)
        if new_count == 1 and old_count == 0:
            status = "ALREADY_RECONCILED"
        elif new_count == 0 and old_count == 1:
            segment = segment.replace(old, new, 1)
            updated = updated[:start] + segment + updated[end:]
            status = "READY_TO_APPLY"
        else:
            raise ReconcileError(
                f"replacement {index} under {anchor!r} ambiguous: old_count={old_count}, new_count={new_count}"
            )
        rows.append({"index": index, "anchor": anchor, "old": old, "new": new, "status": status})

    return updated, rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("check", "apply"), default="check")
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", ""))
    parser.add_argument("--token-env", default="GITHUB_TOKEN")
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    args = parser.parse_args()

    if not args.repository or "/" not in args.repository:
        raise ReconcileError("--repository owner/name is required")
    token = os.environ.get(args.token_env, "")
    if not token:
        raise ReconcileError(f"environment variable {args.token_env} is required")

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    issue_url = f"{API_ROOT}/repos/{args.repository}/issues/{spec['issue']}"
    issue = api_json("GET", issue_url, token)
    body = issue.get("body") or ""
    updated, rows = reconcile_body(body, spec)
    changed = updated != body
    if args.mode == "apply" and changed:
        api_json("PATCH", issue_url, token, {"body": updated})

    result = {
        "schema": "HST_ISSUE_233_RECONCILIATION_RECEIPT_V1",
        "mode": args.mode,
        "issue": 233,
        "issue_state": issue.get("state"),
        "replacement_count": len(rows),
        "already_reconciled": sum(row["status"] == "ALREADY_RECONCILED" for row in rows),
        "ready_to_apply": sum(row["status"] == "READY_TO_APPLY" for row in rows),
        "body_changed": changed,
        "body_sha256_before": canonical_sha(body),
        "body_sha256_after": canonical_sha(updated),
        "claim_ceiling": spec.get("claim_ceiling"),
        "rows": rows,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ReconcileError as exc:
        print(json.dumps({"schema": "HST_ISSUE_233_RECONCILIATION_RECEIPT_V1", "verdict": "FAIL", "error": str(exc)}, indent=2))
        raise SystemExit(1)
