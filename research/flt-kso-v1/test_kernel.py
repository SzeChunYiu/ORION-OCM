"""Kernel boundary unit controls. Process fakes are not mathematical evidence."""
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from kernel import KernelSession, accepted_capture, clean_environment, run_process
from native import atom,imp

class KernelHostiles(unittest.TestCase):
    def capture(self,output):
        return {'exit_code':0,'timed_out':False,'output_limit_exceeded':False,'stderr':'','stdout':output}
    def test_exact_empty_axiom_report(self):
        self.assertTrue(accepted_capture(self.capture("'FLTMicro.goal' does not depend on any axioms\n")))
    def test_axiom_and_sorry_rejected(self):
        for text in ("'FLTMicro.goal' depends on axioms: [sorryAx]", "'FLTMicro.goal' depends on axioms: [injected]"):
            self.assertFalse(accepted_capture(self.capture(text)))
    def test_extra_report_rejected(self):
        text="'FLTMicro.goal' does not depend on any axioms\n'other' does not depend on any axioms"
        self.assertFalse(accepted_capture(self.capture(text)))
    def test_nonzero_exit_never_passes(self):
        c=self.capture("'FLTMicro.goal' does not depend on any axioms"); c['exit_code']=1
        self.assertFalse(accepted_capture(c))
    def test_timeout_never_passes(self):
        c=self.capture("'FLTMicro.goal' does not depend on any axioms"); c['timed_out']=True
        self.assertFalse(accepted_capture(c))
    def test_absent_archive_no_fallback(self):
        with KernelSession(None) as s:
            result=s.check(imp(atom('A'),atom('A')),('lam','h0',('var','h0')))
            self.assertEqual(result['terminal'],'CANNOT_CHECK_TOOLCHAIN')
            self.assertEqual(s.metrics['Lean_checker_calls'],0)
            self.assertFalse(s.authentic_for({'run_id':'forged'},imp(atom('A'),atom('A')),('lam','h0',('var','h0'))))
    def test_wrong_archive_refused(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad';p.write_bytes(b'not lean')
            with KernelSession(p) as s:
                self.assertEqual(s.report['terminal'],'CHECKER_OR_ENVIRONMENT_MISMATCH')
    def test_environment_is_allowlist(self):
        env=clean_environment(Path('/tmp'))
        self.assertNotIn('PYTHONPATH',env);self.assertNotIn('LD_PRELOAD',env)
        self.assertNotIn('ELAN_HOME',env);self.assertNotIn('LAKE_HOME',env)
    def test_real_process_timeout_capture(self):
        with tempfile.TemporaryDirectory() as d:
            r=run_process([sys.executable,'-I','-c','import time; time.sleep(2)'],Path(d),0.05)
            self.assertTrue(r['timed_out']);self.assertNotEqual(r['exit_code'],0)

if __name__=='__main__': unittest.main()
