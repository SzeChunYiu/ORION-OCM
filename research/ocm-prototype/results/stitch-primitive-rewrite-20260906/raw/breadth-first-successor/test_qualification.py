"""Harmless controls only: no Stitch or native verifier imports/calls."""
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'source'))
import qualification as Q
import generation_clia as G
from clia_grammar import forms, dump

class QualificationTests(unittest.TestCase):
    def setUp(self):
        self.group=json.loads((ROOT/'manual.json').read_text())
    def test_prepare_retains_exact_opposite_side_and_assignment(self):
        rows=Q.prepare(self.group)
        self.assertEqual(len(rows),4)
        self.assertEqual(rows[0]['original'],self.group['records'][0]['candidate'])
        self.assertNotEqual(rows[0]['program'],rows[0]['original'])
    def test_noop_cannot_pass_effective_normalization(self):
        rows=Q.prepare(self.group)
        with patch.object(G,'equivalent',return_value={'status':'PASS','native_invoked':False}):
            receipt=Q.assess(self.group,rows,[r['program'] for r in rows])
        self.assertEqual(receipt['status'],'CANNOT_CHECK_NORMALIZATION')
    def test_clean_declared_rewrites_use_original_on_left(self):
        rows=Q.prepare(self.group)
        outputs=[G.encode(r['expected'],p['sigs'])[0]['program'] for r,p in zip(self.group['records'],rows)]
        calls=[]
        def equivalent(left,right,sigs):
            calls.append((left,right)); return {'status':'PASS','native_invoked':False}
        with patch.object(G,'equivalent',side_effect=equivalent):
            receipt=Q.assess(self.group,rows,outputs)
        self.assertEqual(receipt['status'],'MANUAL_BOUNDARY_QUALIFIED')
        self.assertEqual(len(calls),4)
        self.assertEqual(calls[0][0],self.group['records'][0]['candidate'])
        self.assertEqual(forms(calls[0][1]),forms(self.group['records'][0]['expected']))
    def test_inventory_loss_is_not_success(self):
        rows=Q.prepare(self.group)
        with patch.object(G,'equivalent',side_effect=AssertionError('native check forbidden')):
            receipt=Q.assess(self.group,rows,[])
        self.assertEqual(receipt['status'],'CANNOT_CHECK_NORMALIZATION')
    def test_shadowing_refused_before_native(self):
        group={'group':'manual','records':[{'id':'shadow','name':'f','parameters':['x'],'candidate':'(define-fun f ((x Int)) Int (let ((x 1)) x))','expected':''}]}
        with self.assertRaises(ValueError):
            Q.prepare(group)

if __name__=='__main__':
    unittest.main(verbosity=2)
