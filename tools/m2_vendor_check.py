"""Drift checker for docs/provenance/VENDORED_SOURCE_MANIFEST_V1.json.

Recomputes the git blob sha (``sha1("blob <len>\\0" + bytes)``, no git needed)
of every ``target_path`` in the manifest and compares it with the recorded
``target_blob_sha``; with the source repositories reachable it also re-derives
each ``source_blob_sha`` from ``<source_repo>`` at ``<source_commit>`` and
checks the recorded ``byte_identical`` flag.

Exit codes:
  0  no drift
  1  drift (a target file changed, is missing, or a recorded sha/flag is wrong)
  2  a source repository (or the pinned commit inside it) is unreachable — the
     target check still ran; pass ``--targets-only`` to skip sources entirely
  3  the manifest itself is missing or malformed

Usage: python tools/m2_vendor_check.py [--manifest PATH] [--targets-only] [--repo-root PATH]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

DEFAULT_MANIFEST = Path("docs/provenance/VENDORED_SOURCE_MANIFEST_V1.json")


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def source_blob_sha(repo: Path, commit: str, path: str) -> str | None:
    """Return the blob sha of ``path`` at ``commit`` in ``repo``, or None if unreachable."""

    if not (repo / ".git").exists() and not (repo / "HEAD").exists():
        return None
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--verify", "--quiet", f"{commit}:{path}"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--repo-root", type=Path, default=None, help="OCM checkout root (default: manifest's grandparent's parent)")
    parser.add_argument("--targets-only", action="store_true", help="do not consult the source repositories")
    args = parser.parse_args(argv)

    manifest_path = args.manifest
    if not manifest_path.is_absolute():
        manifest_path = Path.cwd() / manifest_path
    repo_root = args.repo_root or manifest_path.parent.parent.parent
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        files = manifest["files"]
        repos = manifest["source_repos"]
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"MALFORMED manifest {manifest_path}: {error}")
        return 3

    drift = 0
    unreachable = 0
    checked = 0
    for row in files:
        target = repo_root / row["target_path"]
        try:
            data = target.read_bytes()
        except OSError:
            print(f"DRIFT   missing target {row['target_path']}")
            drift += 1
            continue
        actual = git_blob_sha(data)
        checked += 1
        if actual != row["target_blob_sha"]:
            print(f"DRIFT   {row['target_path']}: recorded {row['target_blob_sha'][:12]} actual {actual[:12]}")
            drift += 1
        if row.get("source_path") is None:
            continue
        expected_identical = row["source_blob_sha"] == row["target_blob_sha"]
        if bool(row["byte_identical"]) != expected_identical:
            print(f"DRIFT   {row['target_path']}: byte_identical flag disagrees with recorded shas")
            drift += 1
        if args.targets_only:
            continue
        repo_info = repos.get(row["source_repo"])
        if repo_info is None:
            print(f"DRIFT   {row['target_path']}: unknown source_repo {row['source_repo']!r}")
            drift += 1
            continue
        remote = source_blob_sha(Path(repo_info["local_path"]), row["source_commit"], row["source_path"])
        if remote is None:
            print(f"UNREACH {row['source_repo']}@{row['source_commit'][:12]}:{row['source_path']}")
            unreachable += 1
            continue
        if remote != row["source_blob_sha"]:
            print(f"DRIFT   {row['target_path']}: source blob {remote[:12]} != recorded {row['source_blob_sha'][:12]}")
            drift += 1

    print(f"checked {checked} target(s): {drift} drift, {unreachable} unreachable source(s)")
    if drift:
        return 1
    if unreachable:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
