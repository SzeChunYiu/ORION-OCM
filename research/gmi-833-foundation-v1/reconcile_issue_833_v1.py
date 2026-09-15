#!/usr/bin/env python3
"""Line-exact, section-exact, idempotent reconciliation for issue #833."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
DEFAULT_SPEC = HERE / "ISSUE_833_RECONCILIATION_FOUNDATION_V1.json"
API_ROOT = "https://api.github.com"


class ReconcileError(RuntimeError):
    pass


def canonical_sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def api_json(method: str, url: str, token: str, payload: dict | None = None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "orion-ocm-issue-833-reconciler-v1",
    }
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = Request(url, data=data, method=method, headers=headers)
    try:
        with urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise ReconcileError(f"GitHub API {method} {url} failed: {exc.code}: {body}") from exc


def _heading_level(line: str) -> int:
    if not line.startswith("#"):
        return 0
    hashes = len(line) - len(line.lstrip("#"))
    return hashes if len(line) > hashes and line[hashes] == " " else 0


def locate_section(lines: list[str], anchor: str) -> tuple[int, int]:
    matches = [i for i, line in enumerate(lines) if line == anchor]
    if len(matches) != 1:
        raise ReconcileError(f"anchor must match exactly one heading line: {anchor!r}; found {len(matches)}")
    start = matches[0]
    level = _heading_level(lines[start])
    if level == 0:
        raise ReconcileError(f"anchor is not a Markdown heading line: {anchor!r}")
    end = len(lines)
    for i in range(start + 1, len(lines)):
        next_level = _heading_level(lines[i])
        if next_level and next_level <= level:
            end = i
            break
    return start, end


def reconcile_body(body: str, spec: dict) -> tuple[str, list[dict]]:
    if spec.get("schema") != "GMI_ISSUE_RECONCILIATION_V2":
        raise ReconcileError("unknown reconciliation schema")
    if spec.get("issue") != 833:
        raise ReconcileError("this reconciler is pinned to issue 833")
    replacements = spec.get("replacements")
    if not isinstance(replacements, list) or not replacements:
        raise ReconcileError("replacements must be a nonempty list")

    trailing_newline = body.endswith("\n")
    lines = body.splitlines()
    receipt = []

    for idx, row in enumerate(replacements, 1):
        anchor, old, new = row.get("anchor"), row.get("old"), row.get("new")
        if not all(isinstance(x, str) and x for x in (anchor, old, new)):
            raise ReconcileError(f"replacement {idx} malformed")
        if "\n" in old or "\n" in new or "\n" in anchor:
            raise ReconcileError(f"replacement {idx} must use single exact lines")
        if old == new or not old.startswith("- [ ] ") or not new.startswith("- [x] "):
            raise ReconcileError(f"replacement {idx} must be an unchecked->checked exact line")

        start, end = locate_section(lines, anchor)
        section_indices = range(start + 1, end)
        old_hits = [i for i in section_indices if lines[i] == old]
        new_hits = [i for i in section_indices if lines[i] == new]
        if len(new_hits) == 1 and not old_hits:
            status = "ALREADY_RECONCILED"
        elif len(old_hits) == 1 and not new_hits:
            lines[old_hits[0]] = new
            status = "READY_TO_APPLY"
        else:
            raise ReconcileError(
                f"replacement {idx} ambiguous under {anchor!r}: exact old hits={len(old_hits)}, exact new hits={len(new_hits)}"
            )
        receipt.append({"index": idx, "anchor": anchor, "old": old, "new": new, "status": status})

    updated = "\n".join(lines) + ("\n" if trailing_newline else "")
    return updated, receipt


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
    if spec.get("issue") != 833:
        raise ReconcileError("spec issue must be 833")

    issue_url = f"{API_ROOT}/repos/{args.repository}/issues/833"
    issue = api_json("GET", issue_url, token)
    body = issue.get("body") or ""
    updated, rows = reconcile_body(body, spec)
    changed = updated != body
    if args.mode == "apply" and changed:
        api_json("PATCH", issue_url, token, {"body": updated})

    print(json.dumps({
        "schema": "GMI_ISSUE_RECONCILIATION_RECEIPT_V2",
        "mode": args.mode,
        "issue": 833,
        "issue_state": issue.get("state"),
        "replacement_count": len(rows),
        "body_changed": changed,
        "body_sha256_before": canonical_sha(body),
        "body_sha256_after": canonical_sha(updated),
        "forbidden_promotions_preserved": spec.get("forbidden_promotions", []),
        "rows": rows,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ReconcileError as exc:
        print(json.dumps({"schema":"GMI_ISSUE_RECONCILIATION_RECEIPT_V2","verdict":"FAIL","error":str(exc)}, indent=2))
        raise SystemExit(1)
