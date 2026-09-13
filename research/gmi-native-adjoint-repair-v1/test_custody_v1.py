"""Hostile controls use complete packet copies and no new ecology calls."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from custody_v1 import CustodyError, replay, verify_manifest, strict_json
ROOT=Path(__file__).resolve().parent

class CustodyTests(unittest.TestCase):
    def copy(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        root=Path(temp.name)/'unit';shutil.copytree(ROOT,root)
        return root

    def test_complete_real_no_alarm_and_full_replay(self):
        self.assertGreater(len(verify_manifest(ROOT)[1]['files']),10)
        self.assertEqual(replay(ROOT)['status'],'FULL_NATIVE_ADJOINT_PAYLOAD_REPLAY_PASS')

    def test_same_status_changed_numeric_payload_rejected(self):
        expected=json.loads((ROOT/'RECEIPT_V1.json').read_text())
        expected['native_vm_controls']['B0/corrected/zero_input']['stages'][-1]['cells']['dense_w0']=9
        self.assertEqual(expected['status'],'PASS')
        with self.assertRaises(CustodyError): replay(ROOT,lambda _:json.dumps(expected).encode())

    def test_rehashed_manifest_mutation_rejected(self):
        root=self.copy();wanted=(root/'RECEIPT_V1.json').read_bytes();calls=[]
        def worker(path):
            calls.append(1)
            document=path/'CORE.md';document.write_text(document.read_text()+'\nmodified\n')
            manifest=json.loads((path/'MANIFEST_V1.json').read_text())
            data=document.read_bytes()
            manifest['files']['CORE.md']={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
            (path/'MANIFEST_V1.json').write_text(json.dumps(manifest))
            verify_manifest(path)  # The altered unit is internally self-consistent.
            return wanted
        with self.assertRaisesRegex(CustodyError,'manifest changed'): replay(root,worker)
        self.assertEqual(calls,[1])

    def test_raw_and_code_changes_rejected(self):
        for name in ['native_controls_v1.py','corrected_source/gmi_microscope/vm.py']:
            root=self.copy();p=root/name;p.write_bytes(p.read_bytes()+b'\n')
            with self.assertRaises(CustodyError): verify_manifest(root)

    def test_hidden_file_and_missing_member_rejected(self):
        root=self.copy();(root/'.unregistered').write_text('x')
        with self.assertRaises(CustodyError): verify_manifest(root)
        root=self.copy();(root/'CORE.md').unlink()
        with self.assertRaises(CustodyError): verify_manifest(root)

    def test_symlink_directory_and_fifo_rejected(self):
        for kind in ('file','directory','fifo'):
            root=self.copy();path=root/'unexpected'
            if kind=='fifo': os.mkfifo(path)
            else: path.symlink_to(root/'CORE.md' if kind=='file' else root/'raw',target_is_directory=kind=='directory')
            with self.assertRaises(CustodyError): verify_manifest(root)

    def test_duplicate_json_and_nonlocal_path_rejected(self):
        with self.assertRaises(CustodyError): strict_json('{"a":1,"a":2}')
        with self.assertRaises(CustodyError): strict_json('{"a":NaN}')
        root=self.copy();p=root/'MANIFEST_V1.json';manifest=json.loads(p.read_text())
        manifest['files']['../CORE.md']=manifest['files'].pop('CORE.md')
        p.write_text(json.dumps(manifest))
        with self.assertRaises(CustodyError): verify_manifest(root)

    def test_late_unbound_change_rejected_even_with_correct_payload(self):
        root=self.copy();wanted=(root/'RECEIPT_V1.json').read_bytes()
        def worker(path):
            (path/'native_controls_v1.py').write_bytes(b'changed')
            return wanted
        with self.assertRaises(CustodyError): replay(root,worker)

if __name__=='__main__': unittest.main()
