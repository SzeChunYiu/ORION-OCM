import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import copy
import json
import os
import shutil
import tempfile
import unittest
from custody_v1 import verify,sha
from replay_v1 import replay
ROOT=Path(__file__).resolve().parent

def rebind(root,path):
    target=root/"MANIFEST_V1.json"
    data=json.loads(target.read_bytes())
    raw=(root/path).read_bytes()
    for row in data["payloads"]:
        if row["path"]==path:
            row.update(bytes=len(raw),sha256=sha(raw))
            break
    else:
        raise ValueError("not in manifest")
    target.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")

class CustodyTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)/"unit"
        shutil.copytree(ROOT,self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_complete_real_packet_no_alarm(self):
        raw,expected=verify(self.root)
        result=replay(self.root,worker=lambda _:expected)
        self.assertEqual(result["manifest_sha256"],sha(raw))

    def test_real_source_mutation(self):
        binding=json.loads((self.root/"SOURCE_BINDINGS_V1.json").read_text())[0]
        path=self.root/binding["copy"]
        path.write_bytes(path.read_bytes()+b"\n")
        with self.assertRaises(ValueError):
            verify(self.root)

    def test_missing_payload(self):
        (self.root/"CORE.md").unlink()
        with self.assertRaises(ValueError):
            verify(self.root)

    def test_hidden_extra_payload(self):
        (self.root/".unbound").write_bytes(b"x")
        with self.assertRaises(ValueError):
            verify(self.root)

    def test_link_and_fifo_rejected(self):
        path=self.root/"CORE.md"
        saved=path.read_bytes()
        path.unlink()
        path.symlink_to(self.root/"VALIDATION_V1.md")
        with self.assertRaises(ValueError):
            verify(self.root)
        path.unlink()
        os.mkfifo(path)
        with self.assertRaises(ValueError):
            verify(self.root)

    def test_full_payload_not_pass_flag_projection(self):
        _,expected=verify(self.root)
        changed=json.loads(expected)
        changed["memory"]["rows"][0]["setup"]["total_operations"]+=1
        self.assertEqual(changed["status"],"PASS")
        with self.assertRaises(ValueError):
            replay(self.root,worker=lambda _:json.dumps(changed).encode())

    def test_self_consistent_rebinding_during_worker(self):
        initial,expected=verify(self.root)
        def worker(root):
            (root/"CORE.md").write_bytes((root/"CORE.md").read_bytes()+b"\nchanged\n")
            rebind(root,"CORE.md")
            current,current_expected=verify(root)
            self.assertNotEqual(current,initial)
            self.assertEqual(current_expected,expected)
            return expected
        with self.assertRaisesRegex(ValueError,"authority changed"):
            replay(self.root,worker=worker)

    def test_changed_expected_receipt_during_worker(self):
        _,expected=verify(self.root)
        def worker(root):
            (root/"RECEIPT_V1.json").write_bytes(expected+b"\n")
            rebind(root,"RECEIPT_V1.json")
            return expected+b"\n"
        with self.assertRaisesRegex(ValueError,"authority changed"):
            replay(self.root,worker=worker)

if __name__=="__main__":
    unittest.main()
