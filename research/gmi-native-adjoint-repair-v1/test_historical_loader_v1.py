"""The historical source selector rejects altered records even after import."""
from pathlib import Path
import importlib.util
import marshal
import struct
import shutil
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("historical_vm_loader_control",ROOT/"corrected_source/gmi_microscope/historical_vm_v1.py")
loader=importlib.util.module_from_spec(spec);spec.loader.exec_module(loader)
PACKET=ROOT/"raw/pr551-grad-audit-20260913"

class HistoricalLoaderTests(unittest.TestCase):
    def copy(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        path=Path(temp.name)/"packet";shutil.copytree(PACKET,path);return path
    def test_complete_frozen_source_has_distinct_old_bug_semantics(self):
        old=loader.historical_vm(PACKET)
        self.assertTrue(old.__name__.startswith("historical_gmi_vm_"))
        self.assertEqual(old.__file__,str(PACKET/"raw/gmi_microscope/vm.py"))
        from source_loader_v1 import source_modules
        self.assertIsNot(old,source_modules("corrected")[-1])
    def test_source_mutation_rejected_after_prior_success(self):
        loader.historical_vm(PACKET)
        root=self.copy();path=root/"raw/gmi_microscope/vm.py";path.write_bytes(path.read_bytes()+b"\n")
        with self.assertRaisesRegex(ValueError,"source differs"):loader.historical_vm(root)
    def test_manifest_mutation_rejected(self):
        root=self.copy();path=root/"AUDIT_MANIFEST_V1.json";path.write_bytes(path.read_bytes()+b"\n")
        with self.assertRaisesRegex(ValueError,"manifest differs"):loader.historical_vm(root)

    def test_valid_stale_bytecode_is_ignored(self):
        root=self.copy();source=root/"raw/gmi_microscope/__init__.py"
        cache=Path(importlib.util.cache_from_source(str(source)));cache.parent.mkdir(exist_ok=True)
        data=source.read_bytes();stat=source.stat()
        payload=compile('raise RuntimeError("stale bytecode executed")',str(source),"exec")
        header=importlib.util.MAGIC_NUMBER+struct.pack("<III",0,int(stat.st_mtime),len(data))
        cache.write_bytes(header+marshal.dumps(payload))
        spec=importlib.util.spec_from_file_location("ordinary_stale_loader_control",source)
        ordinary=importlib.util.module_from_spec(spec)
        with self.assertRaisesRegex(RuntimeError,"stale bytecode"):spec.loader.exec_module(ordinary)
        self.assertTrue(loader.historical_vm(root).VMRow)
    def test_mutated_prior_module_is_never_reused(self):
        old=loader.historical_vm(PACKET);original=old.VMRow
        old.VMRow="poisoned cached object"
        new=loader.historical_vm(PACKET)
        self.assertIsNot(new,old);self.assertTrue(callable(new.VMRow))
        self.assertNotEqual(new.VMRow,old.VMRow)
        old.VMRow=original

if __name__=="__main__":unittest.main()
