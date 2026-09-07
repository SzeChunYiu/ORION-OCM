"""Custody controls; no native proof result is inferred from these unit tests."""
from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import env_inputs as I
import env_check as C


def record(path): return {"path": str(path), **I.file_record(path)}


def prepared(tmp_path):
    root = tmp_path / "prepared"; root.mkdir()
    for name in ("execution/native/permitted.ndjson", "execution/native/target.ndjson",
                 "execution/native/registration.json", "inputs/primitive_packet.ndjson"):
        path = root / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(name)
    receipt = {"schema": "ocm.proof-environment.receipt.v1", "operation": "prepare", "terminal": "PREPARED",
               "environment_id": "a" * 64, "runtime_sha256": "b" * 64, "files": I.inventory(root)}
    path = root / "receipt.json"; I.write_json(path, receipt)
    return root, record(path)


def test_issued_environment_requires_exact_bytes_and_issuer(tmp_path):
    root, issued = prepared(tmp_path)
    values = C.prepared_inputs(issued, "a" * 64, "b" * 64)
    assert set(values) == {"permitted_packet", "target_packet", "registration", "primitive_packet"}
    with pytest.raises(ValueError, match="authorized"):
        C.prepared_inputs(issued, "c" * 64, "b" * 64)
    with pytest.raises(ValueError, match="authorized"):
        C.prepared_inputs(issued, "a" * 64, "c" * 64)
    (root / "execution/native/target.ndjson").write_text("easier target")
    with pytest.raises(ValueError, match="custody"):
        C.prepared_inputs(issued, "a" * 64, "b" * 64)


def test_consistent_target_and_receipt_replacement_needs_new_authorization(tmp_path):
    root, issued = prepared(tmp_path)
    receipt = I.bound_json(issued["path"], issued["sha256"])
    changed = root / "execution/native/target.ndjson"; changed.write_text("easier target")
    receipt["files"]["execution/native/target.ndjson"] = I.file_record(changed)
    Path(issued["path"]).write_bytes(I.canonical(receipt))
    with pytest.raises(ValueError, match="binding differs"):
        C.prepared_inputs(issued, "a" * 64, "b" * 64)


@pytest.mark.parametrize("raw", [b'{"a":1,"a":2}', b'{"a":NaN}', b'{"a":Infinity}'])
def test_ambiguous_json_rejected(raw):
    with pytest.raises(ValueError): I.parse_json(raw)


def test_copy_and_authorization_detect_drift(tmp_path):
    source = tmp_path / "source"; source.write_bytes(b"original")
    bound = record(source); dest = tmp_path / "copy"
    assert I.snapshot(bound, dest)["sha256"] == bound["sha256"]
    source.write_bytes(b"different")
    with pytest.raises(ValueError, match="binding differs"): I.verify_file(bound)
    assert dest.read_bytes() == b"original"
    with pytest.raises(FileExistsError): I.write_bytes(dest, b"overwrite")


def test_symlinked_files_and_extra_prepared_files_refused(tmp_path):
    root, issued = prepared(tmp_path)
    secret = tmp_path / "secret"; secret.write_text("source proof")
    link = root / "unexpected"; link.symlink_to(secret)
    with pytest.raises(ValueError, match="regular file"): I.file_record(link)
    with pytest.raises(ValueError, match="symlink"): C.prepared_inputs(issued, "a" * 64, "b" * 64)
    link.unlink(); link.write_text("additional file")
    with pytest.raises(ValueError, match="custody"): C.prepared_inputs(issued, "a" * 64, "b" * 64)


def test_failed_preparation_does_not_issue_environment(tmp_path):
    root, issued = prepared(tmp_path)
    receipt = I.bound_json(issued["path"], issued["sha256"]); receipt["terminal"] = "CANNOT_CHECK"
    Path(issued["path"]).write_bytes(I.canonical(receipt))
    with pytest.raises(ValueError, match="authorized"):
        C.prepared_inputs(record(root / "receipt.json"), "a" * 64, "b" * 64)
