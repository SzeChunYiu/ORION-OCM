"""Preregistered source custody, including the contents of inherited receipts."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

PACKAGE = "research/gmi-1068-r1-integrated-core-v29"
FREEZE = "3fa87a62c9571e504fb14864cb63ffd66cab0b67"
FREEZE_FILES = {
    "API_V29.md": "7b17d351a86fd756aa198ec292b70fb86c00c49b13d898994832db899c0a390e",
    "FREEZE_V29.md": "03ff85eb9d2391225cd355e05fcab4d77ccf002d16d5fc2c47838e9a31dd4559",
    "INHERITED_PROOFS_V29.json": "8c88f7e3214affd9d52acfd4236217313777c84695be3befb1b24c1f522532f6",
    "ORIGINAL_CROSSWALK_V29.json": "50aac7a4ed2e226d86373199a19c81a312795d6e4f01df177a11b3bab7cd0297",
    "SOURCE_PINS_V29.json": "9b0a2fab21aa4bfb9b080d6cbefc94f554817b3b1de358fcf62bbcce8f70204b",
}
FREEZE_SHA, PINS_SHA = FREEZE_FILES["FREEZE_V29.md"], FREEZE_FILES["SOURCE_PINS_V29.json"]
RECEIPTS = (
    "research/gmi-1068-irreducibility-witnesses-v28/RESULT_V28.json",
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
    bindings = {}
    for name, expected in FREEZE_FILES.items():
        relative = PACKAGE + "/" + name
        frozen = git(root, "show", FREEZE + ":" + relative)
        if frozen.returncode:
            raise CannotCheck("preregistration commit/file unavailable")
        if hashlib.sha256(frozen.stdout).hexdigest() != expected:
            raise ValueError("preregistered bytes changed:" + name)
        if safe_path(root, relative).read_bytes() != frozen.stdout:
            raise ValueError("working preregistration drift:" + name)
        bindings[relative] = expected
    ancestry = git(root, "merge-base", "--is-ancestor", FREEZE, "HEAD")
    if ancestry.returncode == 1:
        raise ValueError("preregistration is not an ancestor")
    if ancestry.returncode:
        raise CannotCheck("cannot resolve preregistration ancestry")
    inventory = git(root, "ls-tree", "-r", "--name-only", FREEZE, "--", PACKAGE)
    if inventory.returncode:
        raise CannotCheck("cannot inspect preregistration tree")
    if inventory.stdout.decode().splitlines() != [PACKAGE + "/" + n for n in sorted(FREEZE_FILES)]:
        raise ValueError("outcomes present before preregistration")
    manifest = json.loads(safe_path(root, PACKAGE + "/SOURCE_PINS_V29.json").read_text())
    if manifest["schema"] != "GMI_1068_R1_INTEGRATED_SOURCE_PINS_V29":
        raise ValueError("source manifest schema")
    companions = {n: h for n, h in FREEZE_FILES.items() if n != "SOURCE_PINS_V29.json"}
    if manifest["freeze_companions"] != companions:
        raise ValueError("freeze companion binding drift")
    if len(manifest["sources"]) != 117 or len(manifest["lean_source_order"]) != 63 or len(manifest["python_load_order"]) != 18:
        raise ValueError("preregistered source inventory changed")
    bindings.update(manifest["sources"])
    for relative, expected in bindings.items():
        if digest(safe_path(root, relative)) != expected:
            raise ValueError("preregistered source drift:" + relative)
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
