"""Authored engineering controls, separate from the frozen developmental sample."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from itertools import product
from pathlib import Path
import tempfile
import unittest

import experiment as E
import representation as R


def record(program=('double',), x=0):
    value = E.M.evaluate_polynomial(E.M.normal_form(program), x)
    task = E.M.PolynomialTask('authored-failure', (value + 1,))
    return {'schema': E.SCHEMA, 'program': list(program), 'x': x,
            'value': str(value), 'target_value': str(value + 1),
            'task': E.task_data(task), 'context': E.context(),
            'outcome': 'CHECKED_POINT_MISMATCH'}


class RepresentationTests(unittest.TestCase):
    def test_prefix_values_exhaustive(self):
        records = [record(p, x) for p in ((), ('double',), ('inc',), ('inc', 'square')) for x in range(4)]
        index, _ = R.build(records, 'P2')
        n = 0
        for length in range(6):
            for p in product(E.M.PRIMITIVES, repeat=length):
                for x in range(4):
                    counts, used = Counter(), Counter()
                    value = R.point_value(p, x, index, counts, used)
                    self.assertEqual(value, E.REAL_EXECUTE(p, x))
                    self.assertEqual(value, E.M.evaluate_polynomial(E.M.normal_form(p), x))
                    self.assertEqual(counts['interpreter_steps'] + counts['avoided_interpreter_steps'], len(p))
                    n += 1
        self.assertEqual(n, 5460)

    def test_first_solutions_same_budget(self):
        for kind in ('P1', 'P2'):
            index, _ = R.build([record(p) for p in ((), ('inc',), ('double',), ('inc', 'square'))], kind)
            for n in range(4):
                for p in product(E.M.PRIMITIVES, repeat=n):
                    task = E.M.PolynomialTask('oracle', E.M.normal_form(p))
                    self.assertEqual(R.solve(task, index=index)['result'], E.M.solve(task, E.BUDGET).as_dict())

    def test_exact_point_parent_refinement(self):
        index, _ = R.build([record(), record(('inc',))], 'P1')
        task = E.M.PolynomialTask('same', (3, 4))
        new, old = R.solve(task, index=index), E.solve(task, index=index)
        self.assertEqual(new['result'], old['result'])
        self.assertEqual(new['used'], old['used'])
        counts = dict(new['counts']); counts.pop('full_hits', None)
        self.assertEqual(counts, old['counts'])

    def test_longest_prefix_not_first(self):
        index, _ = R.build([record(('inc',)), record(('inc', 'double'))], 'P2')
        counts, used = Counter(), Counter()
        self.assertEqual(R.point_value(('inc', 'double', 'square'), 0, index, counts, used), 4)
        self.assertEqual(counts['avoided_interpreter_steps'], 2)
        self.assertEqual(counts['interpreter_steps'], 1)
        self.assertEqual(counts['positive_proper_prefix_hits'], 1)
        self.assertEqual(used, {E.digest(record(('inc', 'double'))): 1})

    def test_missing_input_falls_back(self):
        index, _ = R.build([record(('inc',))], 'P2')
        counts = Counter()
        self.assertEqual(R.point_value(('inc', 'double'), 1, index, counts, Counter()), 4)
        self.assertEqual(counts['hits'], 0)
        self.assertEqual(counts['interpreter_steps'], 2)

    def test_zero_prefix_cannot_manufacture_gain(self):
        index, _ = R.build([record(())], 'P2')
        c = Counter()
        R.point_value(('double',), 0, index, c, Counter())
        self.assertEqual(c['avoided_interpreter_steps'], 0)
        self.assertEqual(c['positive_proper_prefix_hits'], 0)

    def test_fractional_input_composition(self):
        index, _ = R.build([record(('inc',), 1)], 'P2')
        c = Counter()
        self.assertEqual(R.point_value(('inc', 'square'), Fraction(1), index, c, Counter()), 4)

    def test_immutable_trie(self):
        r = record(); index, _ = R.build([r], 'P2')
        r['value'] = '999'
        with self.assertRaises(TypeError): index.nodes[0].edges['inc'] = 100
        with self.assertRaises(TypeError): index.nodes[1].values[0] = (999, 'forged')
        self.assertEqual(R.point_value(('double',), 0, index, Counter(), Counter()), 0)

    def test_invalid_certificate_rejected(self):
        for key, value in (('value', '123'), ('outcome', 'TIMEOUT'), ('x', True)):
            r = record(); r[key] = value
            with self.assertRaises(ValueError): R.build([r], 'P2')

    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError): R.build([record(), record()], 'P2')

    def test_budget_change_reopens(self):
        index, _ = R.build([record()], 'P2')
        task = E.M.PolynomialTask('budget', (5, 1))
        budget = E.M.SearchBudget(5, 5)
        result = R.solve(task, budget, index)
        self.assertEqual(result['counts']['context_reopens'], 1)
        self.assertEqual(result['used'], {})
        self.assertEqual(result['result'], E.M.solve(task, budget).as_dict())

    def test_environment_change_reopens(self):
        index, _ = R.build([record()], 'P2')
        task = E.M.PolynomialTask('env', (2, 1))
        result = R.solve(task, index=index, environment='different-interpreter.v2')
        self.assertEqual(result['used'], {})
        self.assertEqual(result['counts']['context_reopens'], 1)

    def test_unqualified_index_rejected(self):
        with self.assertRaises(ValueError): R.solve(E.M.PolynomialTask('x', (0, 1)), index={'forged': 1})

    def test_exception_restores_interpreter(self):
        original = E.M.solve
        def explode(*args): raise RuntimeError('authored control')
        E.M.solve = explode
        try:
            with self.assertRaises(RuntimeError): R.solve(E.M.PolynomialTask('x', (0, 1)))
            self.assertIs(E.M.execute, E.REAL_EXECUTE)
        finally:
            E.M.solve = original

    def test_task_label_not_used(self):
        index, _ = R.build([record(('inc',))], 'P2')
        a = R.solve(E.M.PolynomialTask('a', (2, 1)), index=index)
        b = R.solve(E.M.PolynomialTask('b', (2, 1)), index=index)
        for k in ('result', 'counts', 'used'): self.assertEqual(a[k], b[k])

    def test_misleading_observer_refuted(self):
        ps = [('double',), ('square',)]
        old = R.observer_certificate(ps, (0,))
        self.assertEqual(old['terminal'], 'ADEQUATE_FOR_DECLARED_FINITE_OBSERVATIONS')
        new = R.observer_certificate(ps, (0, 1))
        self.assertEqual(new['terminal'], 'REPRESENTATION_INSUFFICIENT')
        self.assertFalse(R.certificate_applicable(old, ps, (0, 1)))
        self.assertTrue(R.certificate_applicable(old, ps, (0,)))
        self.assertEqual(R.diagnose(observation_witness=new), 'REPRESENTATION_INSUFFICIENT')

    def test_diagnostic_witness_not_trusted(self):
        new = R.observer_certificate([('double',), ('square',)], (0, 1))
        new['witness']['right_value'] = new['witness']['left_value']
        with self.assertRaises(ValueError): R.diagnose(observation_witness=new)

    def test_bounded_failure_not_representation_failure(self):
        for status in ('BUDGET_EXHAUSTED', 'TIMEOUT', 'UNKNOWN'):
            self.assertEqual(R.diagnose(solver_status=status), 'RESOURCE_BOUND')
        for status in ('EXHAUSTED_DECLARED_GRAMMAR', 'VERIFIED_POLYNOMIAL_IDENTITY', None):
            self.assertEqual(R.diagnose(solver_status=status), 'CANNOT_CHECK')

    def test_selection_complete_equal_population(self):
        task = E.M.PolynomialTask('selection', (2, 1))
        v = {k: [R.solve(task, index=R.build([record(('inc',))], k)[0])] for k in R.KINDS}
        self.assertEqual(R.choose(v), min(R.KINDS, key=lambda k: R.selection_key(k, v[k])))
        for change in ('missing', 'empty', 'foreign', 'duplicate'):
            bad = deepcopy(v)
            if change == 'missing': bad.pop('P2')
            elif change == 'empty': bad['P2'] = []
            elif change == 'foreign': bad['P2'][0]['result']['task_fingerprint'] = 'forged'
            else: bad['P2'] *= 2
            with self.assertRaises(ValueError): R.choose(bad)

    def test_conjunctive_support_real_runtime(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            memory = E.admit(root, [record(('inc',))])
            rep = R.admit(root, memory, 'P2', 'synthetic-selection', 'synthetic-qualification')
            rows, kind, state = R.load(root, memory, rep)
            self.assertEqual(kind, 'P2'); self.assertTrue(state['representation_live'])
            rt = E.OCMRuntime(root); rt.revoke([rep['assurance']]); rt.persist()
            self.assertEqual(R.load(root, memory, rep)[1], 'P1')
            rt = E.OCMRuntime(root); rt.revoke([memory['evidence']]); rt.persist()
            self.assertEqual(R.load(root, memory, rep)[1], 'P0')
            rt = E.OCMRuntime(root); rt.reinstate([rep['assurance']]); rt.persist()
            self.assertEqual(R.load(root, memory, rep)[1], 'P0')
            rt = E.OCMRuntime(root); rt.reinstate([memory['evidence']]); rt.persist()
            self.assertEqual(R.load(root, memory, rep)[1], 'P2')

    def test_cannot_admit_from_dead_memory(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); memory = E.admit(root, [record()])
            rt = E.OCMRuntime(root); rt.revoke([memory['evidence']]); rt.persist()
            with self.assertRaises(ValueError): R.admit(root, memory, 'P2', 'x', 'x')

    def test_stored_representation_identity_checked(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); memory = E.admit(root, [record()])
            rep = R.admit(root, memory, 'P2', 'x', 'x')
            rep['payload_digest'] = 'wrong'
            with self.assertRaises(ValueError): R.load(root, memory, rep)


if __name__ == '__main__':
    unittest.main(verbosity=2)
