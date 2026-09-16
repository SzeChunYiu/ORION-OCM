from __future__ import annotations
import importlib.util, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location('real_transition_protocol_v1',ROOT/'real_transition_protocol_v1.py')
m=importlib.util.module_from_spec(SPEC); assert SPEC.loader; sys.modules[SPEC.name]=m; SPEC.loader.exec_module(m)

class TestProtocol(unittest.TestCase):
    def test_certificate(self):
        r=m.finite_certificate(); self.assertEqual(r['verdict'],'GREEN'); self.assertTrue(all(r['checks'].values())); self.assertFalse(r['scientific_row_earned'])
    def test_empty_is_insufficient(self):
        self.assertEqual(m.evaluate([])['terminal'],'INSUFFICIENT_REAL_SYSTEM_EVIDENCE')
    def test_protocol_fixture_rejected_scientifically(self):
        r=m.protocol_fixture(1); self.assertEqual(m.shape_errors(r),[]); self.assertIn('NOT_REAL_SYSTEM_EVIDENCE',m.real_receipt_errors(r))
    def test_five_logic_fixture(self):
        rs=[m.protocol_fixture(i,'REAL_SYSTEM') for i in range(5)]; self.assertEqual(m.evaluate(rs)['qualifying_count'],5)
    def test_duplicate(self):
        rs=[m.protocol_fixture(1,'REAL_SYSTEM'),m.protocol_fixture(1,'REAL_SYSTEM')]; x=m.evaluate(rs); self.assertEqual(x['qualifying_count'],1); self.assertEqual(x['rejected'][0]['reasons'],['DUPLICATE_SYSTEM_ID'])
    def test_no_transition(self):
        r=m.protocol_fixture(1,'REAL_SYSTEM'); r['predicted_after_property']='A'; r['observed_after_property']='A'; self.assertIn('NO_PREDICTED_TRANSITION',m.real_receipt_errors(r)); self.assertIn('NO_OBSERVED_TRANSITION',m.real_receipt_errors(r))
    def test_leakage(self):
        r=m.protocol_fixture(1,'REAL_SYSTEM'); r['protected_outcome_leakage']=True; self.assertIn('PROTECTED_OUTCOME_LEAKAGE',m.real_receipt_errors(r))
    def test_missing_resources(self):
        r=m.protocol_fixture(1,'REAL_SYSTEM'); r['resources_before']=[]; self.assertTrue(m.real_receipt_errors(r))

if __name__=='__main__': unittest.main()
