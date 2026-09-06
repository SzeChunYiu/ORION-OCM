"""Development controls, not the preregistered R1 outcome."""
import unittest
from native import EqualityTask, construct, render, validate_proof


class NativeControls(unittest.TestCase):
    def test_development_composition(self):
        task = EqualityTask(('x', 'y', 'z'), (('x', 'y'), ('y', 'z')), ('x', 'z'))
        result = construct(task, 32)
        self.assertEqual(result['terminal'], 'CANDIDATE_CONSTRUCTED')
        self.assertTrue(validate_proof(task, result['proof']))
        self.assertNotIn('sorry', render(task, result['proof']))

    def test_exact_cap_keeps_a_found_candidate(self):
        task = EqualityTask(('x', 'y', 'z'), (('x', 'y'), ('x', 'z')), ('x', 'y'))
        result = construct(task, 1)
        self.assertEqual(result['terminal'], 'CANDIDATE_CONSTRUCTED')
        self.assertEqual(result['metrics']['edge_examinations'], 1)

    def test_failed_route_is_not_refutation(self):
        task = EqualityTask(('x', 'y', 'z'), (('x', 'y'),), ('x', 'z'))
        result = construct(task, 32)
        self.assertEqual(result['terminal'], 'NO_ROUTE_IN_REGISTERED_FRAGMENT')
        self.assertIsNone(result['proof'])

    def test_budget_is_not_impossibility(self):
        task = EqualityTask(('x', 'y'), (('x', 'y'),), ('x', 'y'))
        self.assertEqual(construct(task, 0)['terminal'], 'FAILED_UNDER_BUDGET')

    def test_identifiers_cannot_inject_lean(self):
        with self.assertRaises(ValueError):
            EqualityTask(('x\naxiom bad : False', 'y'), (), ('y', 'y'))

    def test_forged_proof_is_not_accepted(self):
        task = EqualityTask(('x', 'y', 'z'), (('x', 'y'),), ('x', 'z'))
        self.assertFalse(validate_proof(task, ['hyp', 0]))
        self.assertFalse(validate_proof(task, ['axiom', 'x', 'z']))


if __name__ == '__main__':
    unittest.main()
