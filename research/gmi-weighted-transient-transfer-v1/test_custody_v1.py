import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from custody_v1 import verify,sha
from replay_v1 import replay

ROOT=Path(__file__).resolve().parent

class CustodyTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.unit=Path(self.tmp.name)/"unit"
        shutil.copytree(ROOT,self.unit)

    def test_real_unit_no_alarm(self):
        raw,payload=verify(self.unit)
        result=replay(self.unit,lambda root:payload)
        self.assertEqual(result["manifest_sha256"],sha(raw))

    def test_numeric_payload_mutation_rejected(self):
        _,payload=verify(self.unit)
        mutated=json.loads(payload)
        mutated["data_selected_policy"]["fee_aware_total"]="999"
        with self.assertRaises(ValueError):
            replay(self.unit,lambda root:json.dumps(mutated).encode())

    def test_parent_mutation_rejected(self):
        p=self.unit/"raw/parents/ARC.md"
        p.write_bytes(p.read_bytes()+b"changed")
        with self.assertRaises(ValueError):
            verify(self.unit)

    def test_hidden_extra_file_rejected(self):
        (self.unit/".unregistered").write_text("x")
        with self.assertRaises(ValueError):
            verify(self.unit)

    def test_nonregular_entry_rejected(self):
        os.mkfifo(self.unit/"unregistered_pipe")
        with self.assertRaises(ValueError):
            verify(self.unit)

    def test_symlink_substitution_rejected(self):
        p=self.unit/"CORE.md"
        p.unlink()
        p.symlink_to(ROOT/"CORE.md")
        with self.assertRaises(ValueError):
            verify(self.unit)

    def test_self_consistent_rebinding_during_worker_rejected(self):
        _,expected=verify(self.unit)
        def worker(root):
            p=root/"CORE.md"
            p.write_bytes(p.read_bytes()+b"\nchanged during worker\n")
            m=root/"MANIFEST_V1.json"
            content=json.loads(m.read_bytes())
            row=next(r for r in content["payloads"] if r["path"]=="CORE.md")
            row.update(bytes=len(p.read_bytes()),sha256=sha(p.read_bytes()))
            m.write_text(json.dumps(content,sort_keys=True,indent=2)+"\n")
            # Establish that the replacement manifest is internally consistent.
            verify(root)
            return expected
        with self.assertRaisesRegex(ValueError,"authority changed"):
            replay(self.unit,worker)

    def test_late_source_change_rejected_without_rebinding(self):
        _,expected=verify(self.unit)
        def worker(root):
            p=root/"weighted_transfer_v1.py"
            p.write_bytes(p.read_bytes()+b"\n# mutation\n")
            return expected
        with self.assertRaises(ValueError):
            replay(self.unit,worker)

if __name__=="__main__":
    unittest.main()
