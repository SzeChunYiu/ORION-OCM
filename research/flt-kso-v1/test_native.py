"""Native search engineering tests: no Lean result is inferred from these."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from native import atom, imp, conj, synthesize, emit_source, validate_formula
from substrate import Refusal

class NativeHostiles(unittest.TestCase):
    def test_identity_constructed(self):
        r=synthesize(imp(atom('A'),atom('A')))
        self.assertEqual(r['terminal'],'NATIVE_CANDIDATE_CONSTRUCTED')
        self.assertEqual(r['truth_warrant'],'NONE')
        self.assertIn('fun h0',emit_source(r['formula'],r['term']))
    def test_modus_ponens_constructed(self):
        a,b=atom('A'),atom('B')
        r=synthesize(imp(imp(a,b),imp(a,b)))
        self.assertEqual(r['terminal'],'NATIVE_CANDIDATE_CONSTRUCTED')
    def test_pair_constructor(self):
        a=atom('A'); r=synthesize(imp(a,conj(a,a)))
        self.assertIn('And.intro',emit_source(r['formula'],r['term']))
    def test_failed_search_not_refutation(self):
        r=synthesize(atom('A'))
        self.assertEqual(r['terminal'],'FAILED_UNDER_BUDGET')
        self.assertEqual(r['truth_warrant'],'NONE')
        self.assertNotIn('REFUTED',str(r))
    def test_budget_is_hard(self):
        r=synthesize(imp(atom('A'),atom('A')),max_expansions=1)
        self.assertEqual(r['terminal'],'FAILED_UNDER_BUDGET')
        self.assertEqual(r['metrics']['proof_state_expansions'],1)
    def test_zero_budget_refused(self):
        with self.assertRaises(Refusal): synthesize(atom('A'),max_expansions=0)
    def test_cyclic_application_bounded(self):
        a=atom('A'); r=synthesize(imp(imp(a,a),a))
        self.assertEqual(r['terminal'],'FAILED_UNDER_BUDGET')
        self.assertGreater(r['metrics']['duplicate_states_avoided'],0)
    def test_deterministic(self):
        goal=imp(atom('A'),conj(atom('A'),atom('A')))
        self.assertEqual(synthesize(goal),synthesize(goal))
    def test_injected_identifier_refused(self):
        with self.assertRaises(Refusal): validate_formula(['atom','A\naxiom x : False'])
    def test_opaque_grammar_node_refused(self):
        with self.assertRaises(Refusal): validate_formula(['tactic','native_decide'])
    def test_injected_proof_text_refused(self):
        with self.assertRaises(Refusal): emit_source(atom('A'),['raw','sorry'])
    def test_free_local_variable_refused(self):
        with self.assertRaises(Refusal): emit_source(atom('A'),['var','h7'])

if __name__=='__main__': unittest.main()
