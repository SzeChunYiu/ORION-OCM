from pathlib import Path
import shutil
import pytest
from registration_evidence import audit

PACKAGE = Path(__file__).resolve().parent


def test_actual_derived_records_no_alarm():
    assert audit(PACKAGE) == {"terminal": "DERIVED_REGISTRATION_RECORDS_PASS", "population": 29511, "assignments": 4,
                            "continuation_cursor": 4, "current_source_bindings": 18, "omitted_inputs": 4,
                            "raw_input_scope": "OMITTED_RAW_METADATA_NOT_REVALIDATED"}


@pytest.mark.parametrize("name", ["MANIFEST.json", "registration-derived.tar.gz", "registration-derived.members.json", "supporting.tar.gz", "OMITTED.json"])
def test_authentic_package_tamper_refuses(tmp_path, name):
    records = tmp_path / "records"; shutil.copytree(PACKAGE/"registration-records", records)
    with (records/name).open("ab") as f: f.write(b"tamper")
    with pytest.raises(ValueError): audit(PACKAGE, records)


def test_isolated_cli_ignores_matching_header_bytecode(tmp_path):
    import os
    import py_compile
    import subprocess
    import sys
    names = ["registration_evidence.py", "registration_evidence_archive.py", "registration_evidence_order.py", "registration_evidence_bindings.py"]
    for name in names: shutil.copyfile(PACKAGE/name, tmp_path/name)
    path = tmp_path/"registration_evidence_archive.py"; original = path.read_bytes(); stamp = path.stat()
    sentinel = tmp_path/"cache-executed"
    poison = ("from pathlib import Path; Path(" + repr(str(sentinel)) + ").write_text(\"cache\")\n").encode()
    assert len(poison) < len(original)
    path.write_bytes(poison + b" "*(len(original)-len(poison)))
    os.utime(path, ns=(stamp.st_atime_ns, stamp.st_mtime_ns)); py_compile.compile(str(path), doraise=True)
    path.write_bytes(original); os.utime(path, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
    normal = subprocess.run([sys.executable,"-I","-S","-c", "import sys; sys.path.insert(0," + repr(str(tmp_path)) + "); import registration_evidence_archive"], capture_output=True)
    assert normal.returncode == 0 and sentinel.read_text() == "cache"
    sentinel.unlink()
    qualified = subprocess.run([sys.executable,"-I","-S",str(tmp_path/"registration_evidence.py")], capture_output=True)
    assert qualified.returncode == 2 and b"CANNOT_CHECK" in qualified.stdout
    assert not sentinel.exists()
