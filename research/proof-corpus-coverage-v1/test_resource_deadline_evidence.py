"""Current-byte and historical substitution controls against the retained resource records."""
import hashlib
import json
from pathlib import Path
import shutil
from unittest.mock import patch

import pytest
import resource_deadline_evidence as target


def binding(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def rebind(root):
    records = {str(p.relative_to(root)): binding(p.read_bytes())
               for p in root.rglob("*") if p.is_file() and p.name != "SEAL.json"}
    raw = json.dumps({"schema": "ocm.f1.resource-successor-seal.v1", "terminal": "COMPLETE",
                      "files": records}, sort_keys=True, separators=(",", ":")).encode()
    (root / "SEAL.json").write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


@pytest.fixture
def records(tmp_path):
    source = Path(target.__file__).parent
    for name in ("resource-records", "resource-successor-records", "resource-exitcode-records",
                 "resource-deadline-records"):
        shutil.copytree(source / name, tmp_path / name)
    root = tmp_path / "resource-deadline-records"
    live = tmp_path / "current"
    shutil.copytree(root / "source", live)
    return root, live


def test_real_retained_no_alarm():
    result = target.audit_deadline(Path(target.__file__).parent / "resource-deadline-records")
    assert result["terminal"] == "RESOURCE_DEADLINE_CUSTODY_PASS"
    assert result["current_resource_sources"] == 29
    assert result["historical"]["current_sources"] == 23
    assert result["historical"]["prior_successor_sources"] == 22
    assert result["historical"]["historical_sources"] == 19
    assert result["omitted_host_inputs_revalidated"] is False


def test_current_file_drift(records):
    root, live = records
    (live / "resource_deadline.py").write_bytes(b"changed current")
    with pytest.raises(ValueError, match="CURRENT_SUCCESSOR_SOURCE"):
        target.audit_deadline(root, source_root=live)


@pytest.mark.parametrize("where,donor,reason", [
    ("prior-source/build_profile.py", "source/build_profile.py", "DEADLINE_HISTORICAL_SOURCE"),
    ("source/build_profile.py", "prior-source/build_profile.py", "DEADLINE_SNAPSHOT_SOURCE"),
])
def test_historical_current_substitution(records, where, donor, reason):
    root, live = records
    (root / where).write_bytes((root / donor).read_bytes())
    with pytest.raises(ValueError, match=reason):
        target.audit_deadline(root, rebind(root), live)


def test_wrong_seal(records):
    root, live = records
    with pytest.raises(ValueError, match="SEAL_HASH"):
        target.audit_deadline(root, "0" * 64, live)


def test_qualification_receipt_drift(records):
    root, live = records
    (root / "tests.xml").write_bytes(b"unrelated qualification")
    with pytest.raises(ValueError, match="DEADLINE_QUALIFICATION_BINDING"):
        target.audit_deadline(root, rebind(root), live)


@pytest.mark.parametrize("change", ["extra", "missing"])
def test_exact_record_membership(records, change):
    root, live = records
    if change == "extra":
        (root / "extra.txt").write_bytes(b"unbound extra")
    else:
        (root / "source/resource_deadline.py").unlink()
    with pytest.raises(ValueError, match="DEADLINE_RECORD_SET"):
        target.audit_deadline(root, rebind(root), live)


def test_noncanonical_source_path(records):
    root, live = records
    path = root / "SOURCE-FREEZE.json"; value = json.loads(path.read_bytes())
    name = next(iter(value["source"]))
    value["source"]["../outside.py"] = value["source"].pop(name)
    path.write_text(json.dumps(value))
    with pytest.raises(ValueError, match="PATH"):
        target.audit_deadline(root, rebind(root), live)


def test_duplicate_source_manifest_key(records):
    root, live = records
    path = root / "SOURCE-FREEZE.json"; raw = path.read_bytes()
    path.write_bytes(b'{"schema":"duplicate",' + raw.lstrip()[1:])
    with pytest.raises(ValueError):
        target.audit_deadline(root, rebind(root), live)


def test_source_symlink_refuses(records):
    root, live = records
    path = live / "resource_deadline.py"; path.unlink()
    path.symlink_to(root / "source/resource_deadline.py")
    with pytest.raises(ValueError):
        target.audit_deadline(root, source_root=live)


def test_unbound_previous_guard_cannot_execute():
    with patch.object(target.Path, "read_bytes", return_value=b"unbound"):
        with patch.object(target, "compile", side_effect=AssertionError("must not compile"), create=True):
            with pytest.raises(ValueError, match="DEADLINE_PRIOR_GUARD_IDENTITY"):
                target.previous()
