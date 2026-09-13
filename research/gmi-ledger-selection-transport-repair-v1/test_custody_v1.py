"""Complete real-packet controls; mocked workers never run experiments."""
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

def rebind(root,path):
    mp=root/"MANIFEST_V1.json"
    manifest=json.loads(mp.read_bytes())
    data=(root/path).read_bytes()
    for row in manifest["payloads"]:
        if row["path"]==path:
            row.update(bytes=len(data),sha256=sha(data))
    mp.write_text(json.dumps(manifest,sort_keys=True,indent=2)+"\n")

class CustodyTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="lst-custody-")
        self.root=Path(self.temp.name)/"unit"
        shutil.copytree(ROOT,self.root)

    def tearDown(self):
        self.temp.cleanup()

    def test_no_alarm_complete_real_payload(self):
        raw,expected=verify(self.root)
        result=replay(self.root,lambda root:expected)
        self.assertEqual(result["manifest_sha256"],sha(raw))

    def test_changed_full_payload_with_retained_status_rejects(self):
        _,expected=verify(self.root)
        changed=json.loads(expected);changed["descent"]["adequate_certificates"]+=1
        with self.assertRaises(ValueError):
            replay(self.root,lambda root:json.dumps(changed).encode())

    def test_source_drift_rejects_before_worker(self):
        p=self.root/"selection_v1.py";p.write_bytes(p.read_bytes()+b"\n")
        calls=[]
        with self.assertRaises(ValueError):replay(self.root,lambda root:calls.append(1))
        self.assertEqual(calls,[])

    def test_raw_parent_drift_rejects(self):
        p=next((self.root/"raw/parents").rglob("OPTIMIZATION.md"))
        p.write_bytes(p.read_bytes()+b"changed")
        with self.assertRaises(ValueError):verify(self.root)

    def test_late_payload_mutation_rejects(self):
        _,expected=verify(self.root)
        def worker(root):
            p=root/"CORE.md";p.write_bytes(p.read_bytes()+b"late")
            return expected
        with self.assertRaises(ValueError):replay(self.root,worker)

    def test_self_consistent_authority_rebinding_rejects(self):
        _,expected=verify(self.root)
        checked=[]
        def worker(root):
            p=root/"CORE.md";p.write_bytes(p.read_bytes()+b"\nrebound\n")
            rebind(root,"CORE.md")
            verify(root)  # independently establishes the altered packet is self-consistent
            checked.append(True)
            return expected
        with self.assertRaises(ValueError):replay(self.root,worker)
        self.assertEqual(checked,[True])

    def test_missing_and_extra_hidden_payloads_reject(self):
        p=self.root/"CORE.md";original=p.read_bytes();p.unlink()
        with self.assertRaises(ValueError):verify(self.root)
        p.write_bytes(original)
        (self.root/".unregistered").write_text("extra")
        with self.assertRaises(ValueError):verify(self.root)

    def test_links_and_fifo_reject(self):
        p=self.root/"link";p.symlink_to(self.root/"CORE.md")
        with self.assertRaises(ValueError):verify(self.root)
        p.unlink();os.mkfifo(p)
        with self.assertRaises(ValueError):verify(self.root)

if __name__=="__main__":unittest.main()
