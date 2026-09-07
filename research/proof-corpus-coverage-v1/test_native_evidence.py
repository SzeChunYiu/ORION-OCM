"""Portable archive custody controls; never invoke native proofs."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from native_evidence import audit_archive, audit_package

def digest(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}

def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()

def archive(rows):
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode="wb", filename="", mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode="w", format=tarfile.USTAR_FORMAT) as tar:
            for name, raw, kind in rows:
                info = tarfile.TarInfo(name); info.type = kind
                info.size = len(raw) if kind == tarfile.REGTYPE else 0
                info.mode = 0o644
                tar.addfile(info, io.BytesIO(raw) if info.size else None)
    return output.getvalue()

class NativeArchiveControls(unittest.TestCase):
    def check(self, rows, members):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "test.tar.gz"; path.write_bytes(archive(rows))
            return audit_archive(path, members)

    def test_clean_roundtrip(self):
        result = self.check([("nested/raw.json", b"exact raw", tarfile.REGTYPE)],
                            {"nested/raw.json": digest(b"exact raw")})
        self.assertEqual(result, {"members": 1, "bytes": 9})

    def test_changed_member(self):
        with self.assertRaisesRegex(ValueError, "MEMBER_HASH"):
            self.check([("x", b"bad", tarfile.REGTYPE)], {"x": digest(b"raw")})

    def test_missing_member(self):
        with self.assertRaisesRegex(ValueError, "MEMBER_SET"):
            self.check([], {"x": digest(b"")})

    def test_extra_member(self):
        with self.assertRaisesRegex(ValueError, "MEMBER_SET"):
            self.check([("x", b"", tarfile.REGTYPE)], {})

    def test_duplicate_member(self):
        with self.assertRaisesRegex(ValueError, "DUPLICATE"):
            self.check([("x", b"", tarfile.REGTYPE)] * 2, {"x": digest(b"")})

    def test_traversal_member(self):
        with self.assertRaisesRegex(ValueError, "PATH"):
            self.check([("../x", b"", tarfile.REGTYPE)], {"../x": digest(b"")})

    def test_link_member(self):
        with self.assertRaisesRegex(ValueError, "FILE_TYPE"):
            self.check([("x", b"", tarfile.SYMTYPE)], {"x": digest(b"")})

    def test_absolute_member(self):
        with self.assertRaisesRegex(ValueError, "PATH"):
            self.check([("/x", b"", tarfile.REGTYPE)], {"/x": digest(b"")})

    def make_package(self, root):
        payload = archive([("x", b"raw", tarfile.REGTYPE)])
        files = {"data.tar.gz": payload, "data.members.json": canonical({"x": digest(b"raw")}),
                 "SOURCE_BINDINGS.json": canonical({}),
                 "INDEX.json": canonical({"schema": "ocm.coverage.native-archives.v1", "archives": [
                     {"archive": "data.tar.gz", "members": "data.members.json", "count": 1, "raw_bytes": 3}]})}
        for name, raw in files.items(): (root / name).write_bytes(raw)
        seal = canonical({"schema": "ocm.coverage.native-archive-seal.v1",
                          "files": {name: digest(raw) for name, raw in files.items()}})
        (root / "SEAL.json").write_bytes(seal)
        return hashlib.sha256(seal).hexdigest()

    def test_clean_package(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); expected = self.make_package(root)
            self.assertEqual(audit_package(root, expected, root)["archive_members"], 1)

    def test_seal_cannot_self_reauthorize(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); expected = self.make_package(root)
            (root / "SEAL.json").write_bytes(b"{}")
            with self.assertRaisesRegex(ValueError, "SEAL_HASH"): audit_package(root, expected, root)

    def test_archive_corruption(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); expected = self.make_package(root)
            (root / "data.tar.gz").write_bytes(b"corrupt")
            with self.assertRaisesRegex(ValueError, "FILE_HASH"): audit_package(root, expected, root)

    def rebind(self, root):
        files = {p.name: digest(p.read_bytes()) for p in root.iterdir() if p.name != "SEAL.json"}
        raw = canonical({"schema": "ocm.coverage.native-archive-seal.v1", "files": files})
        (root / "SEAL.json").write_bytes(raw)
        return hashlib.sha256(raw).hexdigest()

    def test_current_source_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "records"; root.mkdir()
            self.make_package(root)
            source = Path(temp) / "source.py"; source.write_bytes(b"original")
            (root / "SOURCE_BINDINGS.json").write_bytes(canonical({"source.py": digest(b"original")}))
            expected = self.rebind(root)
            self.assertEqual(audit_package(root, expected, Path(temp))["current_sources"], 1)
            source.write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "CURRENT_SOURCE_HASH"):
                audit_package(root, expected, Path(temp))

    def test_wrong_declared_count(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); self.make_package(root)
            index = json.loads((root / "INDEX.json").read_bytes()); index["archives"][0]["count"] = 2
            (root / "INDEX.json").write_bytes(canonical(index))
            expected = self.rebind(root)
            with self.assertRaisesRegex(ValueError, "ARCHIVE_COUNTS"): audit_package(root, expected, root)

    def test_duplicate_json_key(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); self.make_package(root)
            (root / "SOURCE_BINDINGS.json").write_bytes(b'{"x":{},"x":{}}')
            expected = self.rebind(root)
            with self.assertRaisesRegex(ValueError, "DUPLICATE_JSON_KEY"): audit_package(root, expected, root)

    def test_source_symlink_cannot_escape_registered_root(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp); root = base / "records"; root.mkdir(); self.make_package(root)
            current = base / "current"; current.mkdir()
            (base / "outside").write_bytes(b"outside")
            (current / "linked").symlink_to(base, target_is_directory=True)
            (root / "SOURCE_BINDINGS.json").write_bytes(canonical({"linked/outside": digest(b"outside")}))
            expected = self.rebind(root)
            with self.assertRaisesRegex(ValueError, "SOURCE_PATH"): audit_package(root, expected, current)

    def test_boolean_count_refuses(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); self.make_package(root)
            index = json.loads((root / "INDEX.json").read_bytes()); index["archives"][0]["count"] = True
            (root / "INDEX.json").write_bytes(canonical(index))
            expected = self.rebind(root)
            with self.assertRaisesRegex(ValueError, "ARCHIVE_COUNT_TYPE"): audit_package(root, expected, root)

    def test_index_archive_binding_mismatch_refuses(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); self.make_package(root)
            index = json.loads((root / "INDEX.json").read_bytes())
            index["archives"][0]["archive_binding"] = digest(b"wrong")
            (root / "INDEX.json").write_bytes(canonical(index))
            expected = self.rebind(root)
            with self.assertRaisesRegex(ValueError, "INDEX_ARCHIVE_HASH"): audit_package(root, expected, root)

    def test_unsealed_file_refuses(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); expected = self.make_package(root)
            (root / "extra").write_bytes(b"")
            with self.assertRaisesRegex(ValueError, "PACKAGE_SET"): audit_package(root, expected, root)

if __name__ == "__main__": unittest.main()
