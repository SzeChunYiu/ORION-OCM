"""A published V16 ledger is immutable; successors need a new anchored package."""
from pathlib import Path
import sys

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from custody_v16 import CannotCheck, git

LEDGER = "research/gmi-1068-amendment-governance-v16/AMENDMENT_LEDGER_V16.json"


def check_published_bytes(published, current):
    if type(current) is not bytes or (published is not None and type(published) is not bytes):
        raise ValueError("exact ledger bytes required")
    if published is not None and published != current:
        raise ValueError("published V16 ledger changed; create an anchored successor package")
    return "INITIAL_PUBLICATION" if published is None else "PUBLISHED_V16_UNCHANGED"


def evaluate(root, base_sha):
    git(root, "cat-file", "-e", base_sha + "^{commit}")
    found = git(root, "ls-tree", "--name-only", base_sha, "--", LEDGER).decode().splitlines()
    if found not in ([], [LEDGER]):
        raise ValueError("ambiguous target-base ledger inventory")
    prior = git(root, "show", base_sha + ":" + LEDGER) if found else None
    return check_published_bytes(prior, (root / LEDGER).read_bytes())


if __name__ == "__main__":
    try:
        if len(sys.argv) != 3 or sys.argv[1] != "--base-sha":
            raise ValueError("--base-sha is required")
        print(evaluate(Path(__file__).resolve().parents[2], sys.argv[2]))
    except (OSError, CannotCheck) as exc:
        print("CANNOT_CHECK: " + str(exc), file=sys.stderr)
        sys.exit(2)
    except (ValueError, TypeError) as exc:
        print("CHECKED_INVALID: " + str(exc), file=sys.stderr)
        sys.exit(1)
