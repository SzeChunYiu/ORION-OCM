"""Harmless controls only: no installed Stitch/cvc5/Z3 invocation."""
import ast
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import caller
import launch_once
import clia_process
from supervision import capture_one, sha

class Controls(unittest.TestCase):
    def test_input_export_and_python_syntax(self):
        data=json.loads((ROOT/'experiences.json').read_text())
        self.assertEqual([x['task']['task_id'] for x in data['experiences']],
                         ['jmbl_fg_max3','jmbl_fg_mpg_guard2'])
        self.assertEqual(sorted(p.name for p in (ROOT/'source'/'clia_fixtures').glob('*.sl')),
                         ['jmbl_fg_max3.sl','jmbl_fg_mpg_guard2.sl'])
        for x in data['experiences']:
            self.assertEqual(x['historical_check']['status'],'PASS')
            self.assertEqual(x['historical_check']['solver_result'],'unsat')
        for p in list(ROOT.glob('*.py'))+list((ROOT/'source').glob('*.py')):
            ast.parse(p.read_text(),filename=str(p))
    def test_verbatim_observation_no_actual_native(self):
        seen=[]; native_result={'status':'PASS','native_invoked':True,'synthetic':True}
        def fake(action,payload,**kwargs):
            seen.append((action,deepcopy(payload),deepcopy(kwargs)));return native_result
        donor_result=SimpleNamespace(json={'synthetic':True,'abstractions':[],'rewritten':['x','y']})
        donor_seen=[]
        def compress(*args,**kwargs):
            donor_seen.append((args,kwargs));return donor_result
        module=SimpleNamespace(donor=lambda:SimpleNamespace(compress=compress))
        with tempfile.TemporaryDirectory(dir=ROOT/'controls') as td,patch.object(clia_process,'invoke',fake):
            directory=Path(td); counts=caller.observed(module,directory)
            payload={'smt2':'SYNTHETIC_ONLY'};kwargs={'timeout_ms':5000,'deadline_s':10}
            self.assertIs(clia_process.invoke('verify',payload,**kwargs),native_result)
            self.assertEqual(seen,[('verify',payload,kwargs)])
            self.assertEqual(json.loads((directory/'verify-00-result.json').read_text()),native_result)
            result=module.donor().compress(['x','y'],iterations=1,max_arity=2,threads=1,silent=True)
            self.assertIs(result,donor_result)
            self.assertEqual(json.loads((directory/'compress-return.json').read_text()),donor_result.json)
            with self.assertRaises(ValueError): module.donor().compress(['x','y'])
            with self.assertRaises(ValueError): clia_process.invoke('synthesize',payload)
            self.assertEqual(len(donor_seen),1)
            self.assertEqual(counts,{'verify_boundary_calls':1,'native_verify_invocations':1,'compress_calls':1})
    def test_raw_return_precedes_later_failure_and_exception_is_retained(self):
        def failing(*args,**kwargs): raise RuntimeError('SYNTHETIC_ONLY')
        module=SimpleNamespace(donor=lambda:SimpleNamespace(compress=failing))
        with tempfile.TemporaryDirectory(dir=ROOT/'controls') as td,patch.object(clia_process,'invoke',failing):
            directory=Path(td); caller.observed(module,directory)
            with self.assertRaises(RuntimeError): module.donor().compress(['a','b'],iterations=1)
            with self.assertRaises(RuntimeError): clia_process.invoke('verify',{'x':1})
            self.assertEqual(json.loads((directory/'compress-exception.json').read_text())['message'],'SYNTHETIC_ONLY')
            self.assertTrue((directory/'verify-00-request.json').is_file())
            self.assertTrue((directory/'verify-00-exception.json').is_file())
    def test_binding_clean_and_actual_same_size_tamper_refusal(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'controls') as td:
            p=Path(td)/'canary';p.write_bytes(b'GOOD')
            m={'bindings':{str(p):{'bytes':4,'sha256':sha(p)}},
               'python_resolved':str(Path(sys.executable).resolve())}
            launch_once.verify(m)
            p.write_bytes(b'EVIL')
            with self.assertRaisesRegex(ValueError,'BINDING_DRIFT'):launch_once.verify(m)
    def test_existing_supervision_clean_and_failure_custody(self):
        target=ROOT/'controls'
        ok=capture_one([sys.executable,'-B','-E','-s','-c','print("SYNTHETIC_ONLY")'],
                       b'{}',target/'supervisor-clean',ROOT,5)
        self.assertEqual(ok['exit_code'],0)
        bad=capture_one([str(ROOT/'NONEXISTENT_SYNTHETIC_EXECUTABLE')],b'{}',
                        target/'supervisor-missing',ROOT,5)
        self.assertIsNone(bad['exit_code']);self.assertIn('FileNotFoundError',bad['error'])
        self.assertTrue((target/'supervisor-missing'/'result.json').is_file())

if __name__=='__main__': unittest.main()
