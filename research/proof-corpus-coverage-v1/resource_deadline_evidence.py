"""Check three historical resource generations and the separately qualified deadline sources."""
import argparse
import hashlib
import json
from pathlib import Path
import types

PRIOR_GUARD = "c392fc1ae67299bc817e64a3e850f6c34bfb99c234af5fa0ce7d0cc7b888441f"
SEAL_SHA256 = "b7938a231cec14f4a98ec913d51e8db357bcf72772bf7b2be8796b91bc747a82"
PREFIX = "research/proof-corpus-coverage-v1/"
ADDED = {"resource_deadline.py", "deadline_test_support.py", "test_resource_deadline.py",
         "test_profile_deadline.py", "acquisition_run.py", "materialize_boot.py"}
RECORDS = {"SOURCE-FREEZE.json", "tests.xml", "COMMAND.json", "PROCESS.json",
           "SOURCE-BEFORE.json", "SOURCE-AFTER.json", "stdout.bin", "stderr.bin"}


def previous():
    path = Path(__file__).resolve().parent / "resource_exitcode_evidence.py"
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 65536:
        raise ValueError("DEADLINE_PRIOR_GUARD_FILE")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != PRIOR_GUARD:
        raise ValueError("DEADLINE_PRIOR_GUARD_IDENTITY")
    module = types.ModuleType("deadline_prior_custody")
    module.__file__ = str(path)
    exec(compile(raw, str(path), "exec"), module.__dict__)
    return module


def audit_deadline(root, expected_seal=SEAL_SHA256, source_root=None):
    old = previous(); base = old.helper(); _, audit = base.helpers()
    root = Path(root)
    current = Path(source_root) if source_root is not None else Path(__file__).resolve().parent
    historical = root.parent / "resource-exitcode-records"
    values = base.package(audit, root, expected_seal)
    old_values = base.package(audit, historical, old.SEAL_SHA256)
    old_freeze = base.source_freeze(audit, old_values["SOURCE_FREEZE.json"])
    if old_freeze["count"] != 23:
        raise ValueError("DEADLINE_HISTORICAL_COUNT")
    selected = set(old_freeze["files"]) | ADDED
    if len(selected) != 29:
        raise ValueError("DEADLINE_SELECTED_COUNT")
    expected = RECORDS | {"prior-source/" + n for n in old_freeze["files"]}
    expected |= {"source/" + n for n in selected}
    if set(values) != expected:
        raise ValueError("DEADLINE_RECORD_SET")
    freeze = audit.parse(values["SOURCE-FREEZE.json"])
    if (set(freeze) != {"schema", "scope", "qualified_by", "source"}
            or freeze["schema"] != "ocm.unary-launch-current-source.v1"
            or type(freeze["source"]) is not dict or len(freeze["source"]) != 376):
        raise ValueError("DEADLINE_SOURCE_FREEZE")
    for name in freeze["source"]:
        audit.safe_name(name)
    audit.checked(values["tests.xml"], base.binding(freeze["qualified_by"]), "DEADLINE_QUALIFICATION_BINDING")
    current_freeze = {"files": {n: freeze["source"][PREFIX + n] for n in selected}}
    for n, binding in old_freeze["files"].items():
        audit.checked(values["prior-source/" + n], base.binding(binding), "DEADLINE_HISTORICAL_SOURCE")
    for n, binding in current_freeze["files"].items():
        audit.checked(values["source/" + n], base.binding(binding), "DEADLINE_SNAPSHOT_SOURCE")
    base.check_current(audit, current, current_freeze)
    inherited = old.audit_exitcode(historical, source_root=root / "prior-source")
    base.package(audit, root, expected_seal)
    base.check_current(audit, current, current_freeze)
    return {"terminal": "RESOURCE_DEADLINE_CUSTODY_PASS", "current_resource_sources": 29,
            "qualification_source_map_entries": 376, "historical": inherited,
            "omitted_host_inputs_revalidated": False,
            "scope": "Archive and current-byte custody only. The inherited 23-source generation is historical; "
                     "29 deadline/dependency sources match their separately retained qualification. "
                     "No tests, controller, native code or scientific study executed by this check."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent / "resource-deadline-records")
    parser.add_argument("--seal-sha256", default=SEAL_SHA256)
    args = parser.parse_args()
    try:
        result = audit_deadline(args.root, args.seal_sha256); code = 0
    except Exception as exc:
        result = {"terminal": "CANNOT_CHECK_RESOURCE_DEADLINE_CUSTODY", "reason": str(exc)}; code = 2
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
