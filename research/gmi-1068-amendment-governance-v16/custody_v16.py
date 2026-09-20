"""Read the immutable preregistration through git before trusting any receipt."""
import hashlib
import json
from pathlib import Path
import subprocess
from ledger_structure_v16 import CONTRACT_SHA, FREEZE, SNAPSHOT

SCIENCE = "research/gmi-1068-corrected-targets-v16"
CONTRACT = SCIENCE + "/TARGET_CONTRACT_V16.json"


class CannotCheck(RuntimeError):
    pass


def git(root, *args):
    try:
        result = subprocess.run(["/usr/bin/git", "-C", str(root), *args],
                                capture_output=True, check=False)
    except OSError as exc:
        raise CannotCheck(str(exc)) from exc
    if result.returncode:
        raise CannotCheck("git custody input unavailable: " + " ".join(args))
    return result.stdout


def read_contract(root):
    git(root, "cat-file", "-e", FREEZE + "^{commit}")
    ancestor = subprocess.run(["/usr/bin/git", "-C", str(root), "merge-base",
                               "--is-ancestor", FREEZE, "HEAD"], capture_output=True)
    if ancestor.returncode == 1:
        raise ValueError("freeze is not an ancestor")
    if ancestor.returncode:
        raise CannotCheck("ancestry could not be checked")
    prior_files = git(root, "ls-tree", "-r", "--name-only", FREEZE, "--", SCIENCE,
                      "research/gmi-1068-amendment-governance-v16").decode().splitlines()
    if set(prior_files) != {CONTRACT, SCIENCE + "/FREEZE_V16.md"}:
        raise ValueError("outcome implementation predates preregistration")
    pinned = git(root, "show", FREEZE + ":" + CONTRACT)
    raw = (root / CONTRACT).read_bytes()
    if raw != pinned or hashlib.sha256(raw).hexdigest() != CONTRACT_SHA:
        raise ValueError("preregistered target contract changed")
    freeze = SCIENCE + "/FREEZE_V16.md"
    if (root / freeze).read_bytes() != git(root, "show", FREEZE + ":" + freeze):
        raise ValueError("preregistered freeze changed")
    contract = json.loads(raw)
    for path, expected in contract["source_bindings"].items():
        if hashlib.sha256((root / path).read_bytes()).hexdigest() != expected:
            raise ValueError("immutable original/source changed: " + path)
    snapshot = json.loads((root / SNAPSHOT).read_text())
    atoms = [atom for node in snapshot["rounds"].values() for atom in node["obligations"]]
    if len(atoms) != 222 or sum(atom["status"] == "CLOSED" for atom in atoms) != 18:
        raise ValueError("original accounting mismatch")
    return contract
