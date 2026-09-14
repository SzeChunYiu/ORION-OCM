from pathlib import Path
import json,os,shutil,sys,tempfile,unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import custody_v1 as c
from source_evidence_v1 import verified_sources
ROOT=Path(__file__).resolve().parent

class CustodyChecks(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='causal-custody-')
        self.root=Path(self.tmp.name)/'unit';shutil.copytree(ROOT,self.root)
    def tearDown(self): self.tmp.cleanup()
    def test_real_packet_no_alarm(self):
        initial,expected=c.verify(self.root);verified_sources(self.root)
        with patch.object(c,'HERE',self.root),patch('check_v1.run',return_value=json.loads(expected)):
            self.assertEqual(c.replay(self.root),expected)
        self.assertEqual(c.verify(self.root)[0],initial)
    def test_foreign_root_before_execution(self):
        with patch('check_v1.run') as worker:
            with self.assertRaisesRegex(ValueError,'source root'): c.replay(self.root)
            worker.assert_not_called()
    def test_numeric_mutation_even_with_status_pass(self):
        _,b=c.verify(self.root);bad=json.loads(b);bad['rung_pairs']['six_original']['left_pn']='0'
        with patch.object(c,'HERE',self.root),patch('check_v1.run',return_value=bad):
            with self.assertRaisesRegex(ValueError,'payload mismatch'):c.replay(self.root)
    def test_omitted_original_payload(self):
        _,b=c.verify(self.root);bad=json.loads(b);del bad['original_source']
        with patch.object(c,'HERE',self.root),patch('check_v1.run',return_value=bad):
            with self.assertRaisesRegex(ValueError,'payload mismatch'):c.replay(self.root)
    def test_missing_extra_symlink_fifo(self):
        p=self.root/'CORE.md';b=p.read_bytes();p.unlink()
        with self.assertRaises(ValueError):c.verify(self.root)
        p.write_bytes(b);extra=self.root/'.extra';extra.write_text('x')
        with self.assertRaises(ValueError):c.verify(self.root)
        extra.unlink();extra.symlink_to(p)
        with self.assertRaises(ValueError):c.verify(self.root)
        extra.unlink();os.mkfifo(extra)
        with self.assertRaises(ValueError):c.verify(self.root)
    def test_source_and_binding_tamper(self):
        binding=verified_sources(self.root);p=self.root/binding['records'][0]['path']
        p.write_bytes(p.read_bytes()+b'changed')
        with self.assertRaises(ValueError):verified_sources(self.root)
        p=self.root/'SOURCE_BINDINGS_V1.json';p.write_bytes(p.read_bytes()+b' ')
        with self.assertRaises(ValueError):verified_sources(self.root)
    def test_midrun_rebinding_refused(self):
        _,expected=c.verify(self.root)
        def worker():
            p=self.root/'CORE.md';p.write_bytes(p.read_bytes()+b'\nchanged\n')
            m=json.loads((self.root/'MANIFEST_V1.json').read_bytes())
            m['files']['CORE.md']={'bytes':len(p.read_bytes()),'sha256':c.digest(p.read_bytes())}
            (self.root/'MANIFEST_V1.json').write_text(json.dumps(m,sort_keys=True,indent=2)+'\n')
            c.verify(self.root)
            return json.loads(expected)
        with patch.object(c,'HERE',self.root),patch('check_v1.run',side_effect=worker):
            with self.assertRaisesRegex(ValueError,'authority changed'):c.replay(self.root)

if __name__=='__main__':unittest.main()
