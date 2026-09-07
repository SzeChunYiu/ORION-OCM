"""Successor custody falsification; fixtures contain inert, never-executed source."""
import gzip
import json
from pathlib import Path
import tempfile
import unittest
from resource_successor_evidence import audit_successor
from test_resource_successor_fixture import archive,binding,make_fixture,put_archive,raw,seal

class SuccessorEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name)
        self.root,self.old,self.source,self.oldpin=make_fixture(self.base);self.rebind()
    def rebind(self): self.pin=seal(self.root,"ocm.f1.resource-successor-seal.v1")
    def run_audit(self):
        return audit_successor(self.root,self.pin,self.source,self.old,self.oldpin)
    def edit_index(self,fn):
        p=self.root/"INDEX.json";v=json.loads(p.read_bytes());fn(v);p.write_bytes(raw(v));self.rebind()
    def test_distinct_historical_current_sources_and_no_host_access(self):
        result=self.run_audit()
        self.assertEqual(result["terminal"],"RESOURCE_SUCCESSOR_CUSTODY_PASS")
        self.assertEqual((result["historical_sources"],result["current_sources"]),(1,1))
        self.assertEqual((result["historical_archive_members"],result["successor_archive_members"]),(2,2))
        self.assertFalse(result["omitted_host_inputs_revalidated"])
    def test_historical_copy_drift(self):
        (self.root/"historical-source/a.py").write_bytes(b"changed");self.rebind()
        with self.assertRaisesRegex(ValueError,"CURRENT_RESOURCE_SOURCE"):self.run_audit()
    def test_current_source_drift(self):
        (self.source/"a.py").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError,"CURRENT_SUCCESSOR_SOURCE"):self.run_audit()
    def test_historical_authority_cannot_be_replaced_in_new_index(self):
        self.edit_index(lambda j:j["historical"].update(seal_sha256="0"*64))
        with self.assertRaisesRegex(ValueError,"HISTORICAL_AUTHORITY"):self.run_audit()
    def test_original_archive_drift(self):
        (self.old/"final-qualification.tar.gz").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError,"RESOURCE_FILE_HASH"):self.run_audit()
    def test_new_archive_drift(self):
        (self.root/"final-qualification.tar.gz").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError,"SUCCESSOR_FILE_HASH"):self.run_audit()
    def test_boolean_source_count(self):
        self.edit_index(lambda j:j["historical"].update(source_count=True))
        with self.assertRaisesRegex(ValueError,"SOURCE_COUNT"):self.run_audit()
    def test_extra_recursive_file(self):
        (self.root/"historical-source/extra.py").write_bytes(b"extra")
        with self.assertRaisesRegex(ValueError,"SUCCESSOR_PACKAGE_SET"):self.run_audit()
    def test_extra_sealed_historical_source(self):
        (self.root/"historical-source/extra.py").write_bytes(b"extra");self.rebind()
        with self.assertRaisesRegex(ValueError,"HISTORICAL_SOURCE_SET"):self.run_audit()
    def test_duplicate_archive_row(self):
        self.edit_index(lambda j:j["archives"].append(j["archives"][0].copy()))
        with self.assertRaisesRegex(ValueError,"DUPLICATE_SUCCESSOR_ARCHIVE"):self.run_audit()
    def test_omission_binding_drift(self):
        self.edit_index(lambda j:j["omissions"].update(sha256="0"*64))
        with self.assertRaisesRegex(ValueError,"OMISSION_BINDING"):self.run_audit()
    def test_current_source_symlink(self):
        data=(self.source/"a.py").read_bytes();(self.source/"a.py").unlink()
        (self.base/"outside").write_bytes(data);(self.source/"a.py").symlink_to(self.base/"outside")
        with self.assertRaisesRegex(ValueError,"SOURCE_PATH|FILE_KIND"):self.run_audit()
    def test_historical_directory_symlink(self):
        old=self.root/"historical-source";old.rename(self.base/"outside")
        old.symlink_to(self.base/"outside",target_is_directory=True)
        with self.assertRaisesRegex(ValueError,"PACKAGE_PATH"):self.run_audit()
    def test_current_snapshot_differs_from_current_freeze(self):
        row=put_archive(self.root,{"SOURCE_FREEZE.json":(self.root/"SOURCE_FREEZE.json").read_bytes(),"source/a.py":b"different"})
        self.edit_index(lambda j:j.update(archives=[row]))
        with self.assertRaisesRegex(ValueError,"SNAPSHOT_BINDING"):self.run_audit()
    def test_extra_and_duplicate_members_after_tar_end(self):
        for name in ["extra","source/a.py"]:
            with self.subTest(name=name):
                p=self.root/"final-qualification.tar.gz";original=p.read_bytes()
                p.write_bytes(gzip.compress(gzip.decompress(original)+gzip.decompress(archive([(name,b"extra")])),mtime=0))
                self.edit_index(lambda j:j["archives"][0].update(binding(p.read_bytes())))
                with self.assertRaisesRegex(ValueError,"MEMBER_SET|DUPLICATE_MEMBER"):self.run_audit()
                p.write_bytes(original);self.edit_index(lambda j:j["archives"][0].update(binding(original)))

if __name__=="__main__":unittest.main()
