from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REGISTRY = HERE / "ISSUE_833_AF_RECONCILIATION_V1.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def load_registry() -> dict:
    obj = json.loads(REGISTRY.read_text())
    require(obj["registry_id"] == "ISSUE_833_AF_RECONCILIATION_V1", "registry id drift")
    require(obj["repository"] == "SzeChunYiu/ORION-OCM", "repository drift")
    require(obj["issue"] == 833 and obj["comment_id"] == 5693269426, "issue/comment authority drift")
    tasks = obj["tasks"]
    require(len(tasks) == 23, f"expected 23 directly reconcilable AF0-AF3 tasks, got {len(tasks)}")
    require(len(set(tasks)) == len(tasks), "duplicate reconciliation task")
    require(all(t.startswith("- [ ] ") for t in tasks), "all registry tasks must be exact unchecked markdown rows")
    return obj


def request_json(method: str, url: str, payload: dict | None = None) -> dict:
    token = os.environ.get("GITHUB_TOKEN", "")
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "gmi-833-af-reconciler-v1",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        raise RuntimeError(f"GitHub API {method} {url} failed: {exc.code} {body}") from exc


def reconcile_body(body: str, tasks: list[str], apply: bool) -> tuple[str, int, int]:
    out = body
    unchecked = 0
    checked = 0
    for task in tasks:
        done = task.replace("- [ ] ", "- [x] ", 1)
        has_unchecked = out.count(task)
        has_checked = out.count(done)
        require(has_unchecked + has_checked == 1, f"task missing or ambiguous in authoritative comment: {task}")
        if has_checked:
            checked += 1
            continue
        unchecked += 1
        if apply:
            out = out.replace(task, done, 1)
    return out, unchecked, checked


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("static-check", "remote-check", "apply"), default="static-check")
    args = ap.parse_args()
    reg = load_registry()
    if args.mode == "static-check":
        print(json.dumps({"status": "GREEN", "mode": args.mode, "task_count": len(reg["tasks"])}, sort_keys=True))
        return

    owner, repo = reg["repository"].split("/", 1)
    comment_url = f"https://api.github.com/repos/{owner}/{repo}/issues/comments/{reg['comment_id']}"
    comment = request_json("GET", comment_url)
    require(comment.get("id") == reg["comment_id"], "fetched wrong comment")
    body = comment.get("body", "")
    new_body, unchecked, checked = reconcile_body(body, reg["tasks"], apply=args.mode == "apply")
    if args.mode == "remote-check":
        print(json.dumps({"status": "GREEN", "mode": args.mode, "unchecked": unchecked, "already_checked": checked}, sort_keys=True))
        return

    require(os.environ.get("GITHUB_TOKEN"), "GITHUB_TOKEN required for apply")
    if new_body != body:
        request_json("PATCH", comment_url, {"body": new_body})
    print(json.dumps({"status": "GREEN", "mode": args.mode, "newly_checked": unchecked, "already_checked": checked}, sort_keys=True))


if __name__ == "__main__":
    main()
