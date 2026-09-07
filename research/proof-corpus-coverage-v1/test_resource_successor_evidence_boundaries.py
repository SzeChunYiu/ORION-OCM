"""Additional source-only and custody-boundary controls; never run a resource source."""
import importlib.util
import json
import os
from pathlib import Path
import py_compile
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import resource_successor_evidence as successor
from test_resource_successor_fixture import binding,make_fixture,raw,seal

class SuccessorBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name)
        self.root,self.old,self.source,self.oldpin=make_fixture(self.base)
        self.pin=seal(self.root,"ocm.f1.resource-successor-seal.v1")
    def run_audit(self):return successor.audit_successor(self.root,self.pin,self.source,self.old,self.oldpin)
    def test_current_source_root_alias_refuses(self):
        self.source.rename(self.base/"outside");self.source.symlink_to(self.base/"outside",target_is_directory=True)
        with self.assertRaisesRegex(ValueError,"SOURCE_PATH"):self.run_audit()
    def test_historical_root_alias_refuses(self):
        self.old.rename(self.base/"outside");self.old.symlink_to(self.base/"outside",target_is_directory=True)
        with self.assertRaisesRegex(ValueError,"PACKAGE_PATH"):self.run_audit()
    def test_archive_changed_during_audit_refuses(self):
        old,audit=successor.helpers();original=audit.audit_archive
        def changed(path,members):
            result=original(path,members)
            if Path(path).parent==self.root:Path(path).write_bytes(b"changed after member read")
            return result
        audit.audit_archive=changed
        with patch.object(successor,"helpers",return_value=(old,audit)):
            with self.assertRaisesRegex(ValueError,"SUCCESSOR_FILE_HASH"):self.run_audit()
    def test_current_source_changed_during_first_check_refuses(self):
        old,audit=successor.helpers();original=audit.read_file
        def changed(path,limit):
            result=original(path,limit)
            if Path(path)==self.source/"a.py":Path(path).write_bytes(b"changed after source read")
            return result
        audit.read_file=changed
        with patch.object(successor,"helpers",return_value=(old,audit)):
            with self.assertRaisesRegex(ValueError,"CURRENT_SUCCESSOR_SOURCE"):self.run_audit()
    def test_late_extra_historical_file_refuses(self):
        old,audit=successor.helpers();original=old.audit_resource
        def changed(*args,**kwargs):
            result=original(*args,**kwargs)
            (self.old/"late-extra.json").write_bytes(b"unsealed")
            return result
        old.audit_resource=changed
        with patch.object(successor,"helpers",return_value=(old,audit)):
            with self.assertRaisesRegex(ValueError,"HISTORICAL_PACKAGE_SET"):self.run_audit()
    def test_boolean_archive_count_refuses(self):
        p=self.root/"INDEX.json";index=json.loads(p.read_bytes());index["archives"][0]["members"]=True
        p.write_bytes(raw(index));self.pin=seal(self.root,"ocm.f1.resource-successor-seal.v1")
        with self.assertRaisesRegex(ValueError,"COUNT_TYPE"):self.run_audit()
    def test_unbound_helper_is_not_compiled(self):
        with patch.object(successor.Path,"read_bytes",return_value=b"unbound"):
            with patch.object(successor,"compile",side_effect=AssertionError("must not execute"),create=True):
                with self.assertRaisesRegex(ValueError,"GUARD_IDENTITY"):successor.helpers()
    def test_matching_header_cached_helpers_are_ignored(self):
        package=Path(successor.__file__).parent;copied=self.base/"entry";copied.mkdir()
        for name in ("resource_successor_evidence.py","resource_evidence.py","native_evidence.py"):
            shutil.copyfile(package/name,copied/name)
        for name in ("resource_evidence","native_evidence"):
            with self.subTest(helper=name):
                target=copied/(name+".py");data=target.read_bytes();marker=copied/(name+".marker")
                poison=("from pathlib import Path; Path("+repr(str(marker))+").write_text('cached')\n").encode()
                self.assertLess(len(poison),len(data));poison+=b" "*(len(data)-len(poison))
                target.write_bytes(poison);stamp=target.stat()
                py_compile.compile(str(target),doraise=True,invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
                target.write_bytes(data);os.utime(target,ns=(stamp.st_atime_ns,stamp.st_mtime_ns))
                script="import sys; sys.path.insert(0,"+repr(str(copied))+"); import "+name+"; import resource_successor_evidence as s; s.helpers(); print('SOURCE_ONLY_HELPERS_PASS')"
                result=subprocess.run([sys.executable,"-I","-S","-c",script],cwd=self.base,capture_output=True)
                self.assertEqual(result.returncode,0,result.stderr.decode())
                self.assertEqual(result.stdout,b"SOURCE_ONLY_HELPERS_PASS\n")
                self.assertEqual(marker.read_text(),"cached")

if __name__=="__main__":unittest.main()
