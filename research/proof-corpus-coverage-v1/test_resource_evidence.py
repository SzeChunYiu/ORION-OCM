"""Portable resource evidence fixtures; no controller, profile or native dispatch."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from resource_evidence import audit_resource, shared
from unittest.mock import patch

def raw(value): return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
def binding(data): return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}

class ResourceEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "records"; self.root.mkdir()
        self.source = self.base / "source"; self.source.mkdir()
        (self.source / "a.py").write_bytes(b"source")
        stream = io.BytesIO()
        with gzip.GzipFile(fileobj=stream, mode="wb", mtime=0, filename="") as gz:
            with tarfile.open(fileobj=gz, mode="w", format=tarfile.USTAR_FORMAT) as tar:
                info = tarfile.TarInfo("raw.json"); info.size = 3
                tar.addfile(info, io.BytesIO(b"raw"))
        archive = stream.getvalue()
        members = raw({"raw.json": binding(b"raw")})
        source = raw({"count": 1, "files": {"a.py": {**binding(b"source"),
                     "origin": "/forbidden/host/source", "snapshot": "/forbidden/host/snapshot"}}})
        result = raw({"scope": "fixture data only"})
        index = raw({"schema": "ocm.f1.resource-evidence-archive.v1",
            "source_freeze": binding(source), "result": binding(result),
            "external_host_inputs_not_copied": [{"path": "/forbidden/omitted", **binding(b"not opened")}],
            "archives": [{"archive": "a.tar.gz", **binding(archive), "members": 1, "raw_bytes": 3,
                          "member_map": {"file": "a.members.json", **binding(members)}}]})
        for name, data in {"a.tar.gz": archive, "a.members.json": members, "SOURCE_FREEZE.json": source,
                           "RESULT.json": result, "INDEX.json": index}.items():
            (self.root / name).write_bytes(data)
        self.expected = self.rebind()

    def rebind(self):
        seal = raw({"schema": "ocm.f1.resource-evidence-seal.v1", "terminal": "COMPLETE",
                    "files": {p.name: binding(p.read_bytes()) for p in self.root.iterdir() if p.name != "SEAL.json"}})
        (self.root / "SEAL.json").write_bytes(seal)
        return hashlib.sha256(seal).hexdigest()

    def audit(self): return audit_resource(self.root, self.expected, self.source)

    def edit_index(self, mutate):
        path = self.root / "INDEX.json"; value = json.loads(path.read_bytes()); mutate(value)
        path.write_bytes(raw(value)); self.expected = self.rebind()

    def test_clean_archive_and_source_ignore_omitted_host_paths(self):
        result = self.audit()
        self.assertEqual((result["archive_members"], result["current_sources"]), (1, 1))
        self.assertFalse(result["omitted_host_inputs_revalidated"])

    def test_source_drift(self):
        (self.source / "a.py").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "CURRENT_RESOURCE_SOURCE"): self.audit()

    def test_replaced_seal(self):
        (self.root / "SEAL.json").write_bytes(b"{}")
        with self.assertRaisesRegex(ValueError, "RESOURCE_SEAL_HASH"): self.audit()

    def test_corrupted_archive(self):
        (self.root / "a.tar.gz").write_bytes(b"bad")
        with self.assertRaisesRegex(ValueError, "RESOURCE_FILE_HASH"): self.audit()

    def test_boolean_archive_count(self):
        self.edit_index(lambda j: j["archives"][0].update(members=True))
        with self.assertRaisesRegex(ValueError, "RESOURCE_COUNT_TYPE"): self.audit()

    def test_wrong_index_archive_hash(self):
        self.edit_index(lambda j: j["archives"][0].update(sha256="0" * 64))
        with self.assertRaisesRegex(ValueError, "RESOURCE_ARCHIVE_HASH"): self.audit()

    def test_wrong_member_payload(self):
        (self.root / "a.members.json").write_bytes(raw({"raw.json": binding(b"bad")}))
        self.edit_index(lambda j: j["archives"][0]["member_map"].update(binding((self.root / "a.members.json").read_bytes())))
        with self.assertRaisesRegex(ValueError, "MEMBER_HASH"): self.audit()

    def test_duplicate_archive_row(self):
        self.edit_index(lambda j: j["archives"].append(j["archives"][0].copy()))
        with self.assertRaisesRegex(ValueError, "DUPLICATE_RESOURCE_ARCHIVE"): self.audit()

    def test_unsealed_extra_file(self):
        (self.root / "extra").write_bytes(b"")
        with self.assertRaisesRegex(ValueError, "RESOURCE_PACKAGE_SET"): self.audit()

    def test_unbound_helper_source_refuses_before_execution(self):
        with patch("resource_evidence.Path.read_bytes", return_value=b"unbound source"):
            with patch("resource_evidence.compile", side_effect=AssertionError("must not compile"), create=True):
                with self.assertRaisesRegex(ValueError, "RESOURCE_AUDIT_HELPER_IDENTITY"): shared()

    def test_source_symlink_refuses(self):
        (self.source / "a.py").unlink()
        (self.base / "outside").write_bytes(b"source")
        (self.source / "a.py").symlink_to(self.base / "outside")
        with self.assertRaisesRegex(ValueError, "RESOURCE_SOURCE_PATH"): self.audit()

if __name__ == "__main__": unittest.main()
