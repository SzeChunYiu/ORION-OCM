"""Synthetic timeout files only; all process launches are replaced by a harmless stub."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parent
MODE=sys.argv[1]; sys.argv.pop(1)
source=ROOT/'preflight-history-v1'/'launch_once.py' if MODE=='baseline' else ROOT/'launch_once.py'
sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location('launcher_under_test',source)
L=importlib.util.module_from_spec(spec);spec.loader.exec_module(L)
BASE=ROOT/'controls-v2'/MODE;BASE.mkdir()
class ObservationControls(unittest.TestCase):
    def exercise(self,name,body,expected_status):
        case=BASE/name;case.mkdir();input_path=case/'input.json';input_path.write_text('{}')
        output=case/'capture'
        def fake_capture(argv,stdin_bytes,directory,cwd,watchdog):
            Path(directory).mkdir()
            calls=output/'calls';calls.mkdir()
            (calls/'verify-00-request.json').write_text('{"synthetic":true}')
            (calls/'verify-00-result.json').write_bytes(body)
            if expected_status=='RAW_CAPTURE_COMPLETE':
                (calls/'caller-receipt.json').write_text('{"synthetic":true}')
            return {'exit_code':0 if expected_status=='RAW_CAPTURE_COMPLETE' else 124,'synthetic':True}
        manifest={'input':str(input_path),'output':str(output),'argv':['NEVER_EXECUTED'],
                  'watchdog_seconds':1,'bindings':{},
                  'python_resolved':str(Path(sys.executable).resolve())}
        path=case/'manifest.json';path.write_text(json.dumps(manifest))
        with patch.object(L,'capture_one',fake_capture):
            code=L.run(path)
        self.assertEqual(code,0 if expected_status=='RAW_CAPTURE_COMPLETE' else 2)
        receipt=json.loads((output/'receipt.json').read_text())
        self.assertEqual(receipt['status'],expected_status)
        self.assertEqual((output/'calls'/'verify-00-result.json').read_bytes(),body)
        self.assertTrue((output/'seal.json').is_file())
        return receipt['observed_boundaries']
    def test_clean_return_no_alarm(self):
        r=self.exercise('clean',b'{"native_invoked":true,"synthetic":true}','RAW_CAPTURE_COMPLETE')
        self.assertEqual(r['verify_completed_responses'],1)
        self.assertEqual(r['native_verify_true_in_returned_responses'],1)
        self.assertEqual(r.get('invalid_or_incomplete_response_files',[]),[])
    def test_truncated_timeout_retains_receipt_seal_and_unknown(self):
        r=self.exercise('truncated',b'{"native_invoked":','CANNOT_CHECK_EXECUTION')
        self.assertEqual(r['verify_completed_responses'],0)
        self.assertEqual(r['verify_without_response'],1)
        self.assertEqual(r['native_invocations_overall'],'UNKNOWN')
        self.assertEqual(len(r['invalid_or_incomplete_response_files']),1)
    def test_nonobject_timeout_retains_receipt_seal_and_unknown(self):
        r=self.exercise('nonobject',b'[]','CANNOT_CHECK_EXECUTION')
        self.assertEqual(r['verify_completed_responses'],0)
        self.assertEqual(r['verify_without_response'],1)
        self.assertEqual(r['native_invocations_overall'],'UNKNOWN')
        self.assertEqual(len(r['invalid_or_incomplete_response_files']),1)
if __name__=='__main__':unittest.main()
