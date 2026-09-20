"""Select the target branch's current snapshot, or its introduction predecessor."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys


class CannotCheck(RuntimeError):
    pass


def git(repo, *args):
    try:
        result = subprocess.run(["/usr/bin/git", "-C", str(repo), *args],
                                capture_output=True, check=False)
    except OSError as exc:
        raise CannotCheck(str(exc)) from exc
    if result.returncode:
        raise CannotCheck(result.stderr.decode(errors="replace"))
    return result.stdout


def select_baseline(repo, base, current, predecessor):
    if not re.fullmatch("[0-9a-f]{40}", base):
        raise ValueError("exact base commit SHA required")
    for path in (current, predecessor):
        if not path or path.startswith("/") or ".." in Path(path).parts:
            raise ValueError("repository-relative snapshot path required")
    git(repo, "cat-file", "-e", base + "^{commit}")
    entries = git(repo, "ls-tree", "-z", base, "--", current)
    if entries:
        records = entries.rstrip(b"\0").split(b"\0")
        if len(records) != 1:
            raise ValueError("ambiguous current snapshot entry")
        metadata, path = records[0].split(b"\t", 1)
        if metadata.split()[1] != b"blob" or path.decode() != current:
            raise ValueError("current snapshot is not the expected blob")
        selected = current
    else:
        selected = predecessor
    data = git(repo, "show", base + ":" + selected)
    parsed = json.loads(data)
    if not isinstance(parsed, dict) or parsed.get("schema") != "GMI_1068_SCOPE_SNAPSHOT_V3":
        raise ValueError("invalid scope snapshot schema")
    return data, selected


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--current", required=True)
    parser.add_argument("--predecessor", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    data, selected = select_baseline(args.repo, args.base_sha, args.current, args.predecessor)
    Path(args.output).write_bytes(data)
    print(json.dumps({"status": "PASS", "selected": selected, "bytes": len(data)}))


if __name__ == "__main__":
    try:
        main()
    except (CannotCheck, OSError) as exc:
        print("CANNOT_CHECK:" + str(exc), file=sys.stderr)
        sys.exit(2)
    except (ValueError, KeyError, TypeError) as exc:
        print("CHECKED_INVALID:" + str(exc), file=sys.stderr)
        sys.exit(1)
