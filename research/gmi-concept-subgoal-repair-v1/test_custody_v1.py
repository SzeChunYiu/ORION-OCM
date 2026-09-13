"""Real-packet no-alarm and hostile source/payload controls; workers mocked."""
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import custody_v1 as c
from source_evidence_v1 import verify_sources

ROOT=Path(__file__).resolve().parent


def rebind(root):
    m=json.loads((root/'MANIFEST_V1.json').read_bytes())
    for n in m['files']:
        b=(root/n).read_bytes();m['files'][n]=dict(bytes=len(b),sha256=c.digest(b))
    (root/'MANIFEST_V1.json').write_text(json.dumps(m,sort_keys=True,indent=2)+'\n')


class CustodyTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='csg-custody-')
        self.root=Path(self.tmp.name)/'unit';shutil.copytree(ROOT,self.root)

    def tearDown(self):self.tmp.cleanup()

    def test_real_complete_packet_no_alarm(self):
        initial,expected=c.verify(self.root)
        with patch.object(c,'HERE',self.root),patch('check_v1.run',return_value=json.loads(expected)):
            self.assertEqual(c.replay(self.root),expected)
        self.assertEqual(c.verify(self.root)[0],initial)

    def test_root_refusal_precedes_worker(self):
        with patch('check_v1.run') as worker:
            with self.assertRaisesRegex(ValueError,'source root'):c.replay(self.root)
            worker.assert_not_called()

    def test_numeric_change_with_pass_status_refused(self):
        _,expected=c.verify(self.root);bad=json.loads(expected);bad['prefix']['cases']+=1
        with patch.object(c,'HERE',self.root),patch('check_v1.run',return_value=bad):
            with self.assertRaisesRegex(ValueError,'payload mismatch'):c.replay(self.root)

    def test_original_payload_field_projection_refused(self):
        _,expected=c.verify(self.root);bad=json.loads(expected)
        del bad['original']['replays']['subgoal_witness.py']['original_payload']['states']
        with patch.object(c,'HERE',self.root),patch('check_v1.run',return_value=bad):
            with self.assertRaisesRegex(ValueError,'payload mismatch'):c.replay(self.root)

    def test_missing_extra_link_fifo(self):
        p=self.root/'CORE.md';b=p.read_bytes();p.unlink()
        with self.assertRaises(ValueError):c.verify(self.root)
        p.write_bytes(b);extra=self.root/'.extra';extra.write_text('x')
        with self.assertRaises(ValueError):c.verify(self.root)
        extra.unlink();extra.symlink_to(p)
        with self.assertRaises(ValueError):c.verify(self.root)
        extra.unlink();os.mkfifo(extra)
        with self.assertRaises(ValueError):c.verify(self.root)

    def test_changed_raw_source_refused(self):
        binding=json.loads((self.root/'SOURCE_BINDINGS_V1.json').read_bytes());p=self.root/binding['sources'][0]['raw']
        p.write_bytes(p.read_bytes()+b'changed')
        with self.assertRaises(ValueError):verify_sources(self.root)
        with self.assertRaises(ValueError):c.verify(self.root)

    def test_later_source_and_authority_rebinding_refused(self):
        _,expected=c.verify(self.root);verified=[]
        def worker():
            p=self.root/'CORE.md';p.write_bytes(p.read_bytes()+b'\nchanged\n')
            rebind(self.root);c.verify(self.root);verified.append(True)
            return json.loads(expected)
        with patch.object(c,'HERE',self.root),patch('check_v1.run',side_effect=worker):
            with self.assertRaisesRegex(ValueError,'authority changed'):c.replay(self.root)
        self.assertEqual(verified,[True])


if __name__=='__main__':unittest.main()
