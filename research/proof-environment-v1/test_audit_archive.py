"""Archive data controls; never extract or run recorded programs."""
from hashlib import sha256
import io
import json
from pathlib import Path
import sys
import tarfile
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_data import read_archive, load_json


def record(raw): return {"sha256": sha256(raw).hexdigest(), "bytes": len(raw)}


def archive(tmp_path, entries):
    path = tmp_path / "data.tar.gz"
    with tarfile.open(path, "w:gz") as tar:
        for name, value in entries:
            info = tarfile.TarInfo(name)
            if value is None: info.type = tarfile.SYMTYPE; info.linkname = "target"
            else: info.size = len(value)
            tar.addfile(info, None if value is None else io.BytesIO(value))
    return path


def test_real_tar_bytes_are_read_without_extraction(tmp_path):
    p = archive(tmp_path, [("nested/raw.bin", b"actual bytes"), ("empty", b"")])
    expected = {"nested/raw.bin": record(b"actual bytes"), "empty": record(b"")}
    assert read_archive(p, expected) == {"nested/raw.bin": b"actual bytes", "empty": b""}
    assert list(tmp_path.iterdir()) == [p]


@pytest.mark.parametrize("name", ["../outside", "/absolute", "a//b", "./x", "a/../x"])
def test_ambiguous_or_escaping_member_refuses(tmp_path, name):
    p = archive(tmp_path, [(name, b"x")])
    with pytest.raises(ValueError): read_archive(p, {name: record(b"x")})


def test_duplicate_member_refuses_even_when_bytes_identical(tmp_path):
    p = archive(tmp_path, [("x", b"x"), ("x", b"x")])
    with pytest.raises(ValueError): read_archive(p, {"x": record(b"x")})


def test_link_member_refuses_without_following_it(tmp_path):
    p = archive(tmp_path, [("x", None)])
    with pytest.raises(ValueError): read_archive(p, {"x": record(b"")})


@pytest.mark.parametrize("change", ["missing", "extra", "changed", "wrong_size", "boolean_size"])
def test_membership_and_exact_bytes_refuse(tmp_path, change):
    entries = [("x", b"x")]; expected = {"x": record(b"x")}
    if change == "missing": entries = []
    if change == "extra": entries.append(("y", b"y"))
    if change == "changed": entries = [("x", b"y")]
    if change == "wrong_size": expected["x"]["bytes"] = 2
    if change == "boolean_size": expected["x"]["bytes"] = True
    with pytest.raises(ValueError): read_archive(archive(tmp_path, entries), expected)


@pytest.mark.parametrize("raw", [b'{"a":1,"a":2}', b'{"v":NaN}', b'{"v":Infinity}', b'{"v":1e400}'])
def test_ambiguous_or_nonfinite_json_refuses(raw):
    with pytest.raises(ValueError): load_json(raw)


def test_json_keeps_exact_large_integer():
    raw = ('{"v":' + '9' * 400 + '}').encode()
    assert load_json(raw)["v"] == int('9' * 400)
