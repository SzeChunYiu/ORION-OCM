"""Real KSO/runtime integration with unavailable kernel; no substitute checker."""
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.kso.warrant import Liveness
from ocm.runtime.solve import Decision
from ocm_adapter import TheoremView
from kernel import KernelSession
from native import atom,imp
from substrate import Refusal

class AdapterHostiles(unittest.TestCase):
    def test_open_obligation_persists_without_truth(self):
        with tempfile.TemporaryDirectory() as d:
            rt=OCMRuntime(d); v=TheoremView(rt); g=v.open('unit',imp(atom('A'),atom('A')))
            rt.persist(); restarted=TheoremView(OCMRuntime(d))
            self.assertEqual(restarted.status(g),'OPEN')
            self.assertEqual(restarted.runtime.state.ks.atom(g).warrant.liveness(()),Liveness.UNKNOWN)
    def test_same_name_changed_statement_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            v=TheoremView(OCMRuntime(d)); v.open('unit',atom('A'))
            with self.assertRaises(Refusal): v.open('unit',atom('B'))
    def test_native_execution_uses_canonical_solve_and_stays_open(self):
        with tempfile.TemporaryDirectory() as d, KernelSession(None) as checker:
            v=TheoremView(OCMRuntime(d)); g=v.open('unit',imp(atom('A'),atom('A')))
            row=v.attempt(g,checker)
            self.assertEqual(row['outcome']['decision'],'CANNOT_CHECK')
            self.assertEqual(row['proposal']['terminal'],'NATIVE_CANDIDATE_CONSTRUCTED')
            self.assertEqual(v.status(g),'OPEN')
            self.assertEqual(row['checker']['terminal'],'CANNOT_CHECK_TOOLCHAIN')
            comp=[s for s in row['outcome']['trace']['stages'] if s['stage']=='COMPOSITION'][0]
            self.assertEqual(comp['payload']['operator_selection']['mode'],'EXACT_INPUT_INDEX')
            self.assertFalse(any(a.atom_type=='claim' for a in v.runtime.state.ks.atoms))
    def test_failed_search_not_false_after_restart(self):
        with tempfile.TemporaryDirectory() as d, KernelSession(None) as checker:
            v=TheoremView(OCMRuntime(d)); g=v.open('unproved',atom('A'))
            row=v.attempt(g,checker)
            self.assertEqual(row['proposal']['terminal'],'FAILED_UNDER_BUDGET')
            self.assertEqual(TheoremView(OCMRuntime(d)).status(g),'OPEN')
    def test_cannot_forge_checker_receipt(self):
        with tempfile.TemporaryDirectory() as d, KernelSession(None) as checker:
            v=TheoremView(OCMRuntime(d)); g=v.open('unit',imp(atom('A'),atom('A')))
            with self.assertRaises(Refusal): v.admit_checked(g,checker,{'kernel_verified':True},('lam','h0',('var','h0')))

    def test_two_goals_share_registered_grammar_after_restart(self):
        with tempfile.TemporaryDirectory() as d, KernelSession(None) as checker:
            v=TheoremView(OCMRuntime(d))
            a=v.open('first',imp(atom('A'),atom('A'))); v.attempt(a,checker)
            v=TheoremView(OCMRuntime(d))
            b=v.open('second',imp(atom('B'),atom('B')))
            self.assertEqual(v.attempt(b,checker)['checker']['terminal'],'CANNOT_CHECK_TOOLCHAIN')

if __name__=='__main__': unittest.main()
