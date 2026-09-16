from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEDGER = HERE / "GMI_BARRIER_PARENT_LEDGER_V1.json"


def fail(message: str) -> None:
    raise RuntimeError(message)


def main() -> None:
    ledger = json.loads(LEDGER.read_text())
    auth = ledger["issue_comment_authorities"]["HSG_V2_CLOSURE_AMENDMENT"]
    owner_repo = os.environ.get("GITHUB_REPOSITORY", "SzeChunYiu/ORION-OCM")
    url = f"https://api.github.com/repos/{owner_repo}/issues/comments/{auth['comment_id']}"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "gmi-833-af-parent-authority-v1",
    }
    token = os.environ.get("GITHUB_TOKEN", "")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            obj = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"GitHub API authority fetch failed: {exc.code} {exc.read().decode('utf-8','replace')}") from exc
    if obj.get("id") != auth["comment_id"]:
        fail("HSG authority comment id drift")
    if obj.get("updated_at") != auth["updated_at"]:
        fail(f"HSG authority updated_at drift: {obj.get('updated_at')} != {auth['updated_at']}")
    if auth["required_heading"] not in obj.get("body", ""):
        fail("HSG-T51 authority heading missing")
    print(json.dumps({"status": "GREEN", "comment_id": auth["comment_id"], "updated_at": auth["updated_at"]}, sort_keys=True))


if __name__ == "__main__":
    main()
