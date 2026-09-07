import hashlib
import io
import tarfile
import pytest
from registration_evidence_archive import read_archive


def packed(tmp_path, entries):
    path = tmp_path / "fixture.tar.gz"
    with tarfile.open(path, "w:gz") as archive:
        for name, raw, kind in entries:
            member = tarfile.TarInfo(name); member.type = kind
            member.size = len(raw) if kind == tarfile.REGTYPE else 0
            if kind == tarfile.SYMTYPE: member.linkname = "/host"
            archive.addfile(member, io.BytesIO(raw) if kind == tarfile.REGTYPE else None)
    return path


def ident(raw):
    return {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def test_exact_regular_archive_no_alarm(tmp_path):
    path = packed(tmp_path, [("nested/data.json", b"{}", tarfile.REGTYPE)])
    assert read_archive(path, {"nested/data.json": ident(b"{}")}) == {"nested/data.json": b"{}"}


@pytest.mark.parametrize("name", [".", "../escape", "/absolute", "a/../b", "a//b", "a\\b"])
def test_ambiguous_member_refuses(tmp_path, name):
    path = packed(tmp_path, [(name, b"x", tarfile.REGTYPE)])
    with pytest.raises(ValueError): read_archive(path, {name: ident(b"x")})


@pytest.mark.parametrize("kind", [tarfile.SYMTYPE, tarfile.LNKTYPE, tarfile.DIRTYPE])
def test_nonregular_member_refuses(tmp_path, kind):
    path = packed(tmp_path, [("data", b"", kind)])
    with pytest.raises(ValueError): read_archive(path, {"data": ident(b"")})


def test_duplicate_member_refuses(tmp_path):
    path = packed(tmp_path, [("data", b"x", tarfile.REGTYPE)] * 2)
    with pytest.raises(ValueError): read_archive(path, {"data": ident(b"x")})


@pytest.mark.parametrize("members", [{}, {"data": ident(b"bad")}, {"missing": ident(b"x")}])
def test_membership_or_bytes_tamper_refuses(tmp_path, members):
    path = packed(tmp_path, [("data", b"x", tarfile.REGTYPE)])
    with pytest.raises(ValueError): read_archive(path, members)


@pytest.mark.parametrize("second", ["excluded", "included"])
def test_members_after_tar_end_records_are_checked(tmp_path, second):
    import gzip
    def raw_tar(name):
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w") as archive:
            member = tarfile.TarInfo(name); member.size = 1
            archive.addfile(member, io.BytesIO(b"x"))
        return buffer.getvalue()
    path = tmp_path/"concatenated.tar.gz"
    path.write_bytes(gzip.compress(raw_tar("included") + raw_tar(second)))
    with pytest.raises(ValueError): read_archive(path, {"included": ident(b"x")})
