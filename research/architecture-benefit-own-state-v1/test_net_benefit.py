from dataclasses import replace
from fractions import Fraction as F
from itertools import product
import unittest

from net_benefit import (Machine, Step, LifetimeEvidence, PHASES, complete_total,
                        refinement_certificate, rollout, live_use_value,
                        rational, product_pairs, synthesize_refinement)


def investment_pair(reset=False):
    events = ('query', 'reset') if reset else ('query',)
    csteps = {('cold', 'query'): Step('warm', ('EXACT',), (26,)),
              ('warm', 'query'): Step('warm', ('EXACT',), (2,))}
    psteps = {('only', 'query'): Step('only', ('EXACT',), (10,))}
    if reset:
        csteps.update({(s, 'reset'): Step('cold', ('RESET',), (1,)) for s in ('cold', 'warm')})
        psteps['only', 'reset'] = Step('only', ('RESET',), (1,))
    c = Machine(('cold', 'warm'), 'cold', (0,), events, csteps,
                {'cold': (3,), 'warm': (3,)}, {'cold': ('CLOSED',), 'warm': ('CLOSED',)})
    p = Machine(('only',), 'only', (0,), events, psteps,
                {'only': (1,)}, {'only': ('CLOSED',)})
    return c, p


def charges(cost):
    return {p: (cost if p == 'solve' else 0,) for p in PHASES}


class RefinementTests(unittest.TestCase):
    def test_exact_investment_bound_includes_close_debt(self):
        c, p = investment_pair()
        cert = refinement_certificate(c, p, (1,), F(1, 5),
                                      {('cold', 'only'): 0, ('warm', 'only'): -24})
        self.assertTrue(cert['verified'])
        self.assertEqual(cert['additive'], F(134, 5))
        for n in range(20):
            cc, co, _ = rollout(c, ['query'] * n, (1,))
            pc, po, _ = rollout(p, ['query'] * n, (1,))
            self.assertEqual(co, po)
            self.assertLessEqual(cc, cert['ratio'] * pc + cert['additive'])
            if n > 0:
                self.assertEqual(cc - pc, 26 - 8 * n)
        self.assertGreater(rollout(c, ['query'], (1,))[0], rollout(p, ['query'], (1,))[0])
        self.assertLess(rollout(c, ['query'] * 4, (1,))[0], rollout(p, ['query'] * 4, (1,))[0])

    def test_reset_invalidates_stable_lifetime_certificate(self):
        c, p = investment_pair(True)
        cert = refinement_certificate(c, p, (1,), F(1, 5),
                                      {('cold', 'only'): 0, ('warm', 'only'): -24})
        self.assertFalse(cert['verified'])
        self.assertTrue(any(row[2] == 'reset' for row in cert['failures']))

    def test_bounded_slowdown_survives_all_short_reset_words(self):
        c, p = investment_pair(True)
        cert = refinement_certificate(c, p, (1,), 3,
                                      {('cold', 'only'): 0, ('warm', 'only'): 4})
        self.assertTrue(cert['verified'])
        for n in range(8):
            for word in product(c.events, repeat=n):
                cc, co, _ = rollout(c, word, (1,))
                pc, po, _ = rollout(p, word, (1,))
                self.assertEqual(co, po)
                self.assertLessEqual(cc, 3 * pc + cert['additive'])

    def test_setup_is_not_free(self):
        c, p = investment_pair()
        c = replace(c, initial_cost=(100,))
        cert = refinement_certificate(c, p, (1,), F(1, 5),
                                      {('cold', 'only'): 0, ('warm', 'only'): -24})
        self.assertEqual(cert['additive'], F(634, 5))

    def test_stop_observation_must_be_preserved(self):
        c, p = investment_pair()
        c = replace(c, close_observations={'cold': ('CLOSED',), 'warm': ('WRONG_SUPPORT',)})
        self.assertFalse(refinement_certificate(c, p, (1,), 3,
                         {('cold', 'only'): 0, ('warm', 'only'): 4})['verified'])

    def test_both_own_states_are_used(self):
        c, p = investment_pair()
        persistent = replace(c, steps={('cold', 'query'): Step('warm', ('EXACT',), (20,)),
                                       ('warm', 'query'): Step('warm', ('EXACT',), (1,))})
        self.assertEqual(product_pairs(c, persistent), {('cold', 'cold'), ('warm', 'warm')})
        self.assertLess(rollout(persistent, ['query'] * 10, (1,))[0],
                        rollout(c, ['query'] * 10, (1,))[0])
        # Charging the persistent parent as cold on every query creates a fake win.
        self.assertGreater(20 * 10, rollout(c, ['query'] * 10, (1,))[0])

    def test_missing_transition_rejected(self):
        c, p = investment_pair()
        c = replace(c, steps={('cold', 'query'): c.steps['cold', 'query']})
        with self.assertRaises(ValueError):
            product_pairs(c, p)

    def test_unknown_successor_rejected(self):
        c, p = investment_pair()
        c = replace(c, steps={**c.steps, ('cold', 'query'): Step('absent', ('EXACT',), (1,))})
        with self.assertRaises(ValueError):
            product_pairs(c, p)

    def test_float_and_bool_costs_rejected(self):
        for x in (True, .1, float('nan'), '1'):
            with self.assertRaises(ValueError):
                rational(x)

    def test_zero_price_rejected(self):
        c, p = investment_pair()
        with self.assertRaises(ValueError):
            refinement_certificate(c, p, (0,), 1, {('cold', 'only'): 0, ('warm', 'only'): 0})

    def test_missing_potential_rejected(self):
        c, p = investment_pair()
        with self.assertRaises(ValueError):
            refinement_certificate(c, p, (1,), 1, {('cold', 'only'): 0})

    def test_potential_is_synthesized_not_hand_given(self):
        c, p = investment_pair()
        result = synthesize_refinement(c, p, (1,), F(1, 5))
        self.assertTrue(result['verified'])
        self.assertEqual(result['additive'], F(134, 5))
        self.assertEqual(result['potential'][('warm', 'only')], -24)

    def test_positive_reset_cycle_rejects_any_potential(self):
        c, p = investment_pair(True)
        result = synthesize_refinement(c, p, (1,), F(1, 5))
        self.assertFalse(result['verified'])
        self.assertEqual(result['reason'], 'REACHABLE_POSITIVE_CYCLE')
        self.assertTrue(synthesize_refinement(c, p, (1,), 3)['verified'])

    def test_zero_parent_cost_positive_loop_rejected(self):
        c, p = investment_pair()
        p = replace(p, steps={('only', 'query'): Step('only', ('EXACT',), (0,))})
        self.assertFalse(synthesize_refinement(c, p, (1,), 100000)['verified'])

    def test_synthesized_cost_bound_does_not_hide_observation_mismatch(self):
        c, p = investment_pair()
        p = replace(p, close_observations={'only': ('WRONG',)})
        self.assertFalse(synthesize_refinement(c, p, (1,), 3)['verified'])

    def test_joint_reuse_and_validity_not_marginals(self):
        self.assertEqual(live_use_value((F(1, 2), F(1, 4)), 8, 4), 2)
        self.assertEqual(live_use_value((0, 0), 8, 4), -4)
        with self.assertRaises(ValueError):
            live_use_value((2,), 8, 4)


class EvidenceTests(unittest.TestCase):
    def gate(self, parents=('strong',)):
        return LifetimeEvidence(parents, ((1,),), (100,), improvement=F(1, 20))

    def add(self, gate, i, c=20, p=80, co=('EXACT',), po=('EXACT',)):
        gate.add(str(i), charges(c), {name: charges(p) for name in gate.parents},
                 co, {name: po for name in gate.parents})

    def test_positive_control_crosses_not_architecture_proof(self):
        gate = self.gate()
        for i in range(100):
            self.add(gate, i)
        report = gate.report()
        self.assertEqual(report['terminal'], 'CONDITIONAL_IID_NET_BENEFIT_EVIDENCE')
        self.assertFalse(report['production_authorized'])
        self.assertFalse(report['sampling_independence_verified'])
        self.assertFalse(report['architecture_necessity_established'])

    def test_strong_parent_clone_blocks_a_weak_baseline_win(self):
        gate = self.gate(('weak', 'clone'))
        for i in range(100):
            gate.add(str(i), charges(20), {'weak': charges(80), 'clone': charges(20)},
                     ('EXACT',), {'weak': ('EXACT',), 'clone': ('EXACT',)})
        self.assertEqual(gate.report()['terminal'], 'INSUFFICIENT_NET_BENEFIT_EVIDENCE')

    def test_contract_failure_cannot_be_dropped(self):
        gate = self.gate()
        self.add(gate, 0, po=('REFUSED',))
        for i in range(1, 100):
            self.add(gate, i)
        self.assertEqual(gate.report()['terminal'], 'CONTRACT_MISMATCH')

    def test_duplicate_lifetime_rejected(self):
        gate = self.gate()
        self.add(gate, 0)
        with self.assertRaises(ValueError):
            self.add(gate, 0)
        self.assertEqual(gate.report()['lifetimes'], 1)

    def test_missing_cost_phase_rejected(self):
        incomplete = charges(20)
        del incomplete['discovery']
        with self.assertRaises(ValueError):
            complete_total(incomplete)

    def test_caps_cannot_be_fixed_by_clipping(self):
        gate = self.gate()
        with self.assertRaises(ValueError):
            self.add(gate, 0, c=101)
        self.assertEqual(gate.report()['lifetimes'], 0)

    def test_invalid_record_permanently_blocks_positive_claim(self):
        gate = self.gate()
        with self.assertRaises(ValueError):
            self.add(gate, 'overcap', c=101)
        for i in range(100):
            self.add(gate, i)
        self.assertEqual(gate.report()['terminal'], 'INVALID_EVALUATION_RECORD')

    def test_all_parents_required(self):
        gate = self.gate(('one', 'two'))
        with self.assertRaises(ValueError):
            gate.add('0', charges(20), {'one': charges(80)}, ('EXACT',), {'one': ('EXACT',)})

    def test_empty_evidence_not_a_pass(self):
        self.assertEqual(self.gate().report()['terminal'], 'INSUFFICIENT_NET_BENEFIT_EVIDENCE')

    def test_exact_e_process_null_expectation_enumerated(self):
        # Uniform fair +/- observations are a null. Average final wealth = 1.
        for lam in (F(1, 8), F(1, 4), F(1, 2)):
            wealths = []
            for path in product((-1, 1), repeat=7):
                wealth = F(1)
                for x in path:
                    wealth *= 1 + lam * x
                wealths.append(wealth)
            self.assertEqual(sum(wealths, F(0)) / len(wealths), 1)

    def test_multiresource_prices_are_separate(self):
        gate = LifetimeEvidence(('parent',), ((1, 0), (0, 1)), (100, 100))
        c = {ph: (10, 90) if ph == 'solve' else (0, 0) for ph in PHASES}
        p = {ph: (90, 10) if ph == 'solve' else (0, 0) for ph in PHASES}
        for i in range(100):
            gate.add(str(i), c, {'parent': p}, ('EXACT',), {'parent': ('EXACT',)})
        self.assertEqual(gate.report()['terminal'], 'INSUFFICIENT_NET_BENEFIT_EVIDENCE')


if __name__ == '__main__':
    unittest.main()
