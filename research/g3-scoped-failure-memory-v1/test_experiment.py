"""Authored controls, not protected scientific tasks."""
from copy import deepcopy
from fractions import Fraction
from itertools import product
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import experiment as E


def fixture():
    task = E.M.PolynomialTask('failure-source', (1, 1))
    row = E.solve(task, E.BUDGET, acquire=True)
    return row['failures'][0]


class FailureMemoryTests(unittest.TestCase):
    def test_exact_control_grid(self):
        record = fixture()
        index, _ = E.index_records([record], E.context())
        comparisons = 0
        for n in range(4):
            for p in product(E.M.PRIMITIVES, repeat=n):
                task = E.M.PolynomialTask('control', E.M.normal_form(p))
                for slots in (0, 1, 5, 100):
                    budget = E.M.SearchBudget(slots, 3)
                    actual = E.solve(task, budget, index)['result']
                    expected = E.M.solve(task, budget).as_dict()
                    self.assertEqual(actual, expected)
                    comparisons += 1
        self.assertEqual(comparisons, 340)

    def test_matching_context_grid(self):
        record = fixture()
        index, _ = E.index_records([record], E.context())
        for p in product(E.M.PRIMITIVES, repeat=3):
            task = E.M.PolynomialTask('same-context', E.M.normal_form(p))
            self.assertEqual(E.solve(task, index=index)['result'], E.M.solve(task, E.BUDGET).as_dict())

    def test_outside_failed_task_success(self):
        record = fixture()
        index, _ = E.index_records([record], E.context())
        task = E.M.PolynomialTask('new-success', E.M.normal_form(tuple(record['program'])))
        row = E.solve(task, index=index)
        self.assertEqual(row['result']['status'], 'VERIFIED_POLYNOMIAL_IDENTITY')
        self.assertGreater(row['counts'].get('hits', 0), 0)

    def test_label_not_lookup_key(self):
        record = fixture(); index, _ = E.index_records([record], E.context())
        a = E.solve(E.M.PolynomialTask('one', (2, 1)), index=index)
        b = E.solve(E.M.PolynomialTask('two', (2, 1)), index=index)
        self.assertEqual((a['result'], a['counts'], a['used']), (b['result'], b['counts'], b['used']))

    def test_bad_value(self):
        r = fixture(); r['value'] = '987'
        with self.assertRaises(ValueError): E.validate_record(r)

    def test_bad_target(self):
        r = fixture(); r['target_value'] = r['value']
        with self.assertRaises(ValueError): E.validate_record(r)

    def test_bad_task_identity(self):
        r = fixture(); r['task']['fingerprint'] = 'bad'
        with self.assertRaises(ValueError): E.validate_record(r)

    def test_unknown_never_certificate(self):
        for outcome in ('UNKNOWN', 'BUDGET_EXHAUSTED', 'TIMEOUT', 'EXHAUSTED_DECLARED_GRAMMAR'):
            r = fixture(); r['outcome'] = outcome
            with self.assertRaises(ValueError): E.validate_record(r)

    def test_point_bool_rejected(self):
        r = fixture(); r['x'] = True
        with self.assertRaises(ValueError): E.validate_record(r)

    def test_foreign_source_rejected(self):
        r = fixture(); r['context']['source_blob'] = '0' * 40
        with self.assertRaises(ValueError): E.validate_record(r)

    def test_unproved_domain_rejected(self):
        r = fixture(); r['context']['domain'] = 'unproved-domain'
        with self.assertRaises(ValueError): E.validate_record(r)

    def test_duplicate_certificate_rejected(self):
        r = fixture()
        with self.assertRaises(ValueError): E.index_records([r, r], E.context())

    def test_budget_change_reopens(self):
        index, _ = E.index_records([fixture()], E.context())
        task = E.M.PolynomialTask('budget-change', (2, 1))
        budget = E.M.SearchBudget(1, 5)
        row = E.solve(task, budget, index)
        self.assertEqual(row['counts'].get('hits', 0), 0)
        self.assertEqual(row['counts']['context_reopens'], 1)
        self.assertEqual(row['result'], E.M.solve(task, budget).as_dict())

    def test_environment_change_reopens(self):
        index, _ = E.index_records([fixture()], E.context())
        row = E.solve(E.M.PolynomialTask('env-change', (2, 1)), index=index, environment='revision.v2')
        self.assertEqual(row['counts'].get('hits', 0), 0)
        self.assertEqual(row['counts']['context_reopens'], 1)

    def test_index_immutable(self):
        index, _ = E.index_records([fixture()], E.context())
        with self.assertRaises(TypeError): index.entries[((), 0)] = (Fraction(7), 'bad')

    def test_solver_restores_interpreter_after_exception(self):
        old = E.M.solve
        def explode(*args): raise RuntimeError('authored exception')
        E.M.solve = explode
        try:
            with self.assertRaises(RuntimeError): E.solve(E.M.PolynomialTask('x', (0, 1)))
            self.assertIs(E.M.execute, E.REAL_EXECUTE)
        finally:
            E.M.solve = old

    def test_live_revoke_restore_actual_runtime(self):
        with tempfile.TemporaryDirectory() as tmp:
            identity = E.admit(Path(tmp), [fixture()])
            live, state = E.load_ocm(Path(tmp), identity)
            self.assertTrue(state['live']); self.assertEqual(len(live), 1)
            rt = E.OCMRuntime(tmp); rt.revoke([identity['evidence']]); rt.persist()
            dead, state = E.load_ocm(Path(tmp), identity)
            self.assertFalse(state['live']); self.assertEqual(dead, [])
            rt = E.OCMRuntime(tmp); rt.reinstate([identity['evidence']]); rt.persist()
            again, state = E.load_ocm(Path(tmp), identity)
            self.assertTrue(state['live']); self.assertEqual(again, live)

    def test_three_cold_workers_support_lifecycle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            record = fixture(); identity = E.admit(root / 'lineage', [record])
            tests = [E.task_data(E.M.PolynomialTask('cold-control', (2, 1)))]
            E.write(root / 'TESTS.json', tests); E.write(root / 'ORDINARY.json', [record])
            request = {'engine': E.source_pin(), 'memory': identity, 'tests_digest': E.digest(tests),
                       'source_sha256': E.hashlib.sha256(Path(E.__file__).read_bytes()).hexdigest()}
            E.write(root / 'REQUEST.json', request)
            reports = []; launches = []
            for mode in E.MODES:
                if mode in ('ocm-revoked', 'ocm-restored'):
                    rt = E.OCMRuntime(root / 'lineage')
                    (rt.revoke if mode == 'ocm-revoked' else rt.reinstate)([identity['evidence']]); rt.persist()
                path = root / (mode + '.json')
                proc = subprocess.Popen([sys.executable, '-I', '-S', '-B', '-X', 'pycache_prefix=' + str(root / ('cache-' + mode)),
                                E.__file__, '--worker', str(root), mode, str(path)],
                               env={**os.environ, 'OCM_REPO': str(E.REPO)}, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = proc.communicate(timeout=30)
                self.assertEqual(proc.returncode, 0, stderr.decode())
                launches.append({'mode': mode, 'pid': proc.pid, 'returncode': proc.returncode})
                reports.append(E.read(path))
            result = E.reconcile(tests, reports, E.digest(request), launches)
            self.assertTrue(result['all_results_equal'])
            for mutate in ('missing-arm', 'truncated', 'duplicate-process', 'forged-task'):
                bad = deepcopy(reports)
                if mutate == 'missing-arm': bad.pop()
                elif mutate == 'truncated': bad[1]['rows'] = []
                elif mutate == 'duplicate-process': bad[1]['pid'] = bad[0]['pid']
                else: bad[1]['rows'][0]['result']['task_fingerprint'] = 'foreign'
                with self.assertRaises(ValueError): E.reconcile(tests, bad, E.digest(request), launches)

    def test_empty_population_rejected(self):
        with self.assertRaises(ValueError): E.reconcile([], [], 'none', [])

    def test_task_payload_fields(self):
        data = E.task_data(E.M.PolynomialTask('control', (0, 1)))
        data['answer'] = 'hidden'
        with self.assertRaises(ValueError): E.task_from(data)


if __name__ == '__main__':
    unittest.main(verbosity=2)
