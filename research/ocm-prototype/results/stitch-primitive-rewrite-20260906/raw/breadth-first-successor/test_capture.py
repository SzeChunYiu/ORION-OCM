"""All calls below are explicit fakes; no native Stitch or Z3 execution."""
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'source'))
import caller as C
import launch_once as L
import qualification as Q
import generation_clia as G
import generation_stitch as D
import clia_process

class CaptureTests(unittest.TestCase):
    def test_actual_call_boundary_serializes_exact_rule_and_native_args(self):
        group=json.loads((ROOT/'manual.json').read_text()); prepared=Q.prepare(group)
        rewritten=[G.encode(r['expected'],p['sigs'])[0]['program'] for r,p in zip(group['records'],prepared)]
        dispatch=[]
        class FakeDonor:
            Abstraction=SimpleNamespace
            def rewrite(self,programs,abstractions,**kwargs):
                dispatch.append((programs,[vars(x) for x in abstractions],kwargs))
                return SimpleNamespace(json={'source':'HARMLESS_FAKE','rewritten':rewritten},rewritten=rewritten)
        with tempfile.TemporaryDirectory() as tmp, patch.object(D,'donor',return_value=FakeDonor()), patch.object(clia_process,'invoke',return_value={'status':'PASS','native_invoked':False}):
            directory=Path(tmp)/'calls'
            self.assertEqual(C.main(ROOT/'manual.json',directory),0)
            receipt=json.loads((directory/'caller-receipt.json').read_text())
            self.assertEqual(receipt['qualification_status'],'MANUAL_BOUNDARY_QUALIFIED')
            self.assertEqual(len(dispatch),1);self.assertEqual(dispatch[0][1],[Q.RULE])
            self.assertEqual(dispatch[0][2],{'hole_choice':'breadth-first'})
            self.assertEqual(json.loads((directory/'rewrite-request.json').read_text())['kwargs'],{'hole_choice':'breadth-first'})
            self.assertEqual(len(list(directory.glob('verify-*-request.json'))),4)
            self.assertEqual(json.loads((directory/'rewrite-return.json').read_text())['source'],'HARMLESS_FAKE')
    def test_train_noop_is_separate_and_uses_exact_four_checks(self):
        group=json.loads((ROOT/'train.json').read_text()); prepared=Q.prepare(group)
        class FakeDonor:
            Abstraction=SimpleNamespace
            def rewrite(self,programs,abstractions,**kwargs):
                return SimpleNamespace(json={'source':'HARMLESS_NOOP','rewritten':programs},rewritten=programs)
        fake={'status':'PASS','native_invoked':False,'metrics':{},'solver_result':'FAKE_NOT_NATIVE'}
        with tempfile.TemporaryDirectory() as tmp, patch.object(D,'donor',return_value=FakeDonor()), patch.object(clia_process,'invoke',return_value=fake):
            directory=Path(tmp)/'calls'
            self.assertEqual(C.main(ROOT/'train.json',directory),0)
            receipt=json.loads((directory/'qualification.json').read_text())
            self.assertEqual(receipt['status'],'TRAIN_EQUIVALENT_NO_EFFECTIVE_NORMALIZATION')
            self.assertEqual(receipt['assigned'],2)
            self.assertEqual(len(list(directory.glob('verify-*-request.json'))),4)
    def test_truncated_and_nonobject_responses_preserve_final_seal(self):
        for payload in ('{"native_invoked":','[]'):
            with self.subTest(payload=payload), tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp); input_path=root/'input.json';input_path.write_text('{}')
                manifest={'output':str(root/'capture'),'python_resolved':str(Path(sys.executable).resolve()),
                  'bindings':{},'watchdog_seconds':49,
                  'groups':[{'group':g,'input':str(input_path),'argv':['HARMLESS_FAKE']} for g in ('manual','train')]}
                path=root/'manifest.json';path.write_text(json.dumps(manifest))
                def fake_capture(argv,stdin,directory,cwd,watchdog):
                    directory.mkdir();calls=directory.parent/'calls';calls.mkdir()
                    (calls/'verify-00-request.json').write_text('{}')
                    (calls/'verify-00-result.json').write_text(payload)
                    for name in ('rewrite-request.json','rewrite-return.json'):
                        (calls/name).write_text('{}')
                    (calls/'caller-receipt.json').write_text(json.dumps({'status':'CALLER_RETURNED','qualification_status':'MANUAL_BOUNDARY_QUALIFIED'}))
                    return {'exit_code':0,'source':'HARMLESS_FAKE'}
                with patch.object(L,'capture_one',side_effect=fake_capture):
                    self.assertEqual(L.run(path),2)
                receipt=json.loads((root/'capture/receipt.json').read_text())
                self.assertEqual(receipt['status'],'CANNOT_CHECK_EXECUTION')
                self.assertEqual(len(receipt['groups']),2)
                self.assertTrue((root/'capture/seal.json').is_file())
                for group in receipt['groups']:
                    self.assertEqual(group['observations']['native_invocations_overall'],'UNKNOWN')
                    self.assertEqual((root/'capture'/group['group']/'calls/verify-00-result.json').read_text(),payload)

if __name__=='__main__':
    unittest.main(verbosity=2)
