"""Preregistered source custody, including the contents of inherited receipts."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

PACKAGE = "research/gmi-1068-affine-regimes-v23"
FREEZE = "ee52f48a6fb4c66c0a618a6ade52e730d726f663"
FREEZE_SHA = "9ea709007b043a8a426d11c434b774a8ed6e37da4295b272acbfce89c1189b17"
RECEIPTS = (
    "research/gmi-1068-permission-barriers-v22/RESULT_V22.json",
    "research/gmi-1068-corrected-targets-v16/RESULT_V16.json",
    "research/gmi-1068-amendment-governance-v16/RESULT_V16.json",
)
QUALIFIED = ["GMI2-R2-003@r1", "GMI2-R2-007@r1"]


class CannotCheck(RuntimeError):
    pass


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(root, *args):
    try:
        result = subprocess.run(["/usr/bin/git", "-C", str(root), *args],
                                capture_output=True, check=False)
    except OSError as exc:
        raise CannotCheck(str(exc)) from exc
    return result


def safe_path(root, relative):
    if type(relative) is not str or not relative or Path(relative).is_absolute():
        raise ValueError("invalid source path")
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or ".." in Path(relative).parts:
        raise ValueError("source path escapes repository")
    return path


def verify(root):
    root = Path(root).resolve()
    frozen = git(root, "show", FREEZE + ":" + PACKAGE + "/FREEZE_V23.md")
    if frozen.returncode:
        raise CannotCheck("preregistration commit unavailable")
    if hashlib.sha256(frozen.stdout).hexdigest() != FREEZE_SHA:
        raise ValueError("preregistration bytes changed")
    ancestry = git(root, "merge-base", "--is-ancestor", FREEZE, "HEAD")
    if ancestry.returncode == 1:
        raise ValueError("preregistration is not an ancestor")
    if ancestry.returncode:
        raise CannotCheck("cannot resolve preregistration ancestry")
    inventory = git(root, "ls-tree", "-r", "--name-only", FREEZE, "--", PACKAGE)
    if inventory.returncode:
        raise CannotCheck("cannot inspect preregistration tree")
    if inventory.stdout.decode().splitlines() != [PACKAGE + "/FREEZE_V23.md"]:
        raise ValueError("outcome artifacts already present at preregistration")
    freeze_path = root / PACKAGE / "FREEZE_V23.md"
    if freeze_path.read_bytes() != frozen.stdout:
        raise ValueError("working preregistration drift")
    bindings = dict(re.findall(r"^- `(research/[^`]+)` `([0-9a-f]{64})`$",
                               frozen.stdout.decode(), re.MULTILINE))
    if len(bindings) != 21:
        raise ValueError("preregistered source inventory changed")
    bindings[PACKAGE + "/FREEZE_V23.md"] = FREEZE_SHA
    for relative, expected in bindings.items():
        if digest(safe_path(root, relative)) != expected:
            raise ValueError("preregistered source drift: " + relative)
    inherited = {}
    for relative in RECEIPTS:
        path = safe_path(root, relative)
        receipt = json.loads(path.read_text())
        local = receipt["inputs"]
        sources = receipt.get("source_bindings", {})
        if type(local) is not dict or not local or type(sources) is not dict:
            raise ValueError("invalid inherited source inventory")
        expanded = dict(sources)
        for name, expected in local.items():
            if type(name) is not str or Path(name).name != name:
                raise ValueError("inherited input must be a basename")
            expanded[str(path.parent.relative_to(root) / name)] = expected
        for name, expected in expanded.items():
            if type(expected) is not str or not re.fullmatch("[0-9a-f]{64}", expected):
                raise ValueError("invalid inherited source digest")
            if digest(safe_path(root, name)) != expected:
                raise ValueError("inherited input drift: " + name)
            if name in bindings and bindings[name] != expected:
                raise ValueError("inconsistent inherited source binding")
            bindings[name] = expected
        inherited[relative] = {"sha256": digest(path), "verified_input_count": len(expanded)}
    gov = json.loads((root / RECEIPTS[2]).read_text())
    science = json.loads((root / RECEIPTS[1]).read_text())
    if gov["science_receipt_sha256"] != digest(root / RECEIPTS[1]):
        raise ValueError("qualified replacement science binding drift")
    ledger_path = root / "research/gmi-1068-amendment-governance-v16/AMENDMENT_LEDGER_V16.json"
    if gov["ledger_sha256"] != digest(ledger_path):
        raise ValueError("qualified replacement ledger binding drift")
    if gov["accounting"]["qualified_revision_ids"] != QUALIFIED:
        raise ValueError("qualified replacement identity drift")
    if science["original_atoms_closed"] != []:
        raise ValueError("historical replacement promoted original atoms")
    carry = {"qualified_revision_ids": QUALIFIED,
             "ledger_sha256": digest(ledger_path),
             "governance_receipt_sha256": digest(root / RECEIPTS[2]),
             "scope": "two immutable qualified readings only; original atoms remain UNKNOWN"}
    return {"source_bindings": dict(sorted(bindings.items())),
            "inherited_receipts": inherited, "amendment_carry": carry}
