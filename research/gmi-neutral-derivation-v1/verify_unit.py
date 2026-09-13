"""Exact finite proof replay. Exit0 checked;1 witness failed;2 not checked."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import types

ROOT = Path(__file__).resolve().parent
BASE = "df777cd79ba5ec6925fd82552e9341f8d73f3577"
REGISTRATIONS = {
    "orbit_registration.json": "b7a847643cb02f7f4b8a933a646eec90fa9454ea6bece60c53a7d1481dcc50c2",
    "orbit_raw_registration.json": "fe9254b1952d9cd4948c38b0aa4fc5faabd4de357c1a0d20678c9c783479ddb8",
    "memory_registration.json": "30423af4481b37ab13346a54501fcabed1f3c3f8c87193349e9e00a377b696f2",
    "neutral_registration.json": "3f9690238b81bf06b70e09763396e245a4ebcc942af7ab45df2af25da0fba1a3",
    "factor_registration.json": "1fab06ba8380973ec5e5a4f04a8e3b6ef23064c1b2dd49d7b5459f5257bf9252",
}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def inventory():
    files = [p for p in ROOT.iterdir() if p.is_file() and
             (p.suffix in (".py", ".md") or p.name.endswith("registration.json")
              or p.name == "PARENT_BINDINGS.json")]
    return {p.name: digest(p.read_bytes()) for p in sorted(files)}


def contracts():
    errors = []
    for name, expected in REGISTRATIONS.items():
        if digest((ROOT / name).read_bytes()) != expected:
            errors.append("pre-execution registration changed: " + name)
    for p in sorted(ROOT.glob("*.md")):
        content = p.read_text()
        length = len(content.splitlines())
        if length > (70 if p.name == "CORE.md" else 180):
            errors.append("overlong module: " + p.name)
        for target in re.findall(r"\]\(([^)]+)\)", content):
            if target.startswith(("https://", "http://", "#")):
                continue
            target = target.split("#", 1)[0]
            if target and not (p.parent / target).exists():
                errors.append("missing link: " + p.name + " -> " + target)
    return errors


def intact(source, before, paths):
    try:
        return inventory() == source and before == tuple(p.read_bytes() if p.is_file() else None for p in paths)
    except OSError:
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--receipt", required=True)
    args = parser.parse_args()
    resolved = Path(args.receipt).resolve()
    if resolved == ROOT or ROOT in resolved.parents:
        raise ValueError("receipt destination must be outside the verified unit")
    destination = Path(args.receipt)
    if destination.exists() and any(destination.samefile(p) for p in ROOT.rglob("*") if p.is_file()):
        raise ValueError("receipt destination aliases a verified payload")
    source = inventory()
    errors = contracts()
    freeze_path = ROOT / "UNIT_FREEZE.json"
    binding_path = ROOT / "SHA256SUMS"
    before = tuple(p.read_bytes() if p.is_file() else None for p in (freeze_path, binding_path))
    frozen = None
    if not args.freeze:
        if None in before:
            errors.append("missing source freeze")
        else:
            frozen = json.loads(before[0])
            if not isinstance(frozen, dict):
                raise ValueError("freeze root must be an object")
            if (frozen.get("schema") != "GMI_NEUTRAL_DERIVATION_V1" or
                    frozen.get("base") != BASE or frozen.get("source_sha256") != source):
                errors.append("source or lineage differs from freeze")
            if before[1] != (digest(before[0]) + "  UNIT_FREEZE.json\n").encode():
                errors.append("freeze binding mismatch")
    if errors:
        print(json.dumps({"status": "NOT_CHECKED", "problems": errors}, indent=2))
        return 2
    raw = (ROOT / "proof_runtime.py").read_bytes()
    if digest(raw) != source["proof_runtime.py"]:
        raise ValueError("runtime source changed before import")
    runtime = types.ModuleType("proof_runtime")
    runtime.__file__ = str(ROOT / "proof_runtime.py")
    sys.modules["proof_runtime"] = runtime
    exec(compile(raw, runtime.__file__, "exec"), runtime.__dict__)
    try:
        result, log = runtime.run(ROOT, source)
    except runtime.SourceMismatch as exc:
        print(json.dumps({"status": "NOT_CHECKED", "problems": [str(exc)]}))
        return 2
    except (ValueError, RuntimeError, AssertionError) as exc:
        if not intact(source, before, (freeze_path, binding_path)):
            print(json.dumps({"status": "NOT_CHECKED", "problems": ["source/freeze changed during failed replay"]}))
            return 2
        print(json.dumps({"status": "WITNESS_FAILED", "problems": [str(exc)]}))
        return 1
    if not intact(source, before, (freeze_path, binding_path)):
        print(json.dumps({"status": "NOT_CHECKED", "problems": ["source/freeze changed during replay"]}))
        return 2
    if result["status"] != "CHECKED":
        print(log, file=sys.stderr)
        print(json.dumps(result))
        return 1
    replay_hash = digest(json.dumps(result, sort_keys=True).encode())
    record = {"schema": "GMI_NEUTRAL_DERIVATION_V1", "base": BASE,
              "source_sha256": source, "tests": result["tests"],
              "tests_run": result["tests_run"], "replay_sha256": replay_hash}
    if args.freeze:
        freeze_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
        binding_path.write_text(digest(freeze_path.read_bytes()) + "  UNIT_FREEZE.json\n")
    elif record != frozen:
        print(json.dumps({"status": "NOT_CHECKED", "problems": ["replay differs from freeze"]}))
        return 2
    result["unit_freeze_sha256"] = digest(freeze_path.read_bytes())
    Path(args.receipt).write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"status": "CHECKED", "tests_run": result["tests_run"],
                      "replay_sha256": replay_hash, "receipt": args.receipt}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        code = main()
    except (OSError, ValueError, TypeError, KeyError, SyntaxError, UnicodeError) as error:
        print(json.dumps({"status": "NOT_CHECKED", "problems": [type(error).__name__ + ": " + str(error)]}))
        code = 2
    raise SystemExit(code)
