"""Episode boundary validation; successful process exit alone grants no credit."""
import unittest
from episode import validate_worker


def proposal():
    return {'status': 'FOUND', 'candidate': ['const', 0], 'reason': 'proposal only',
            'counters': {'applications': 2}, 'limits': {}, 'used_constants': [0],
            'worker_audit': {'schema': 'mechanical-worker-audit-v1', 'guard_sealed': True,
                             'prohibited_events': [],
                             'imported_modules': [{'name': n, 'origin': '/app/' + n + '.py'}
                                                  for n in ['worker_guard', 'f0_terms', 'f0_search']],
                             'constant_occurrences': {'proof_term': {'0': 1}, 'type_annotations': {}}}}


class EpisodeTests(unittest.TestCase):
    def test_closed_proposal_is_not_promoted_to_kernel_pass(self):
        result = validate_worker(proposal())
        self.assertEqual(result['status'], 'FOUND')

    def test_bad_or_unsealed_worker_cannot_be_used(self):
        for field, value in [('guard_sealed', False), ('prohibited_events', ['subprocess.Popen'])]:
            record = proposal()
            record['worker_audit'][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError): validate_worker(record)

    def test_missing_candidate_or_forged_acceptance_status_refused(self):
        for field, value in [('status', 'KERNEL_PASS'), ('candidate', None), ('counters', {'applications': -1})]:
            record = proposal()
            record[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError): validate_worker(record)

    def test_exhaustion_has_no_candidate_and_does_not_assert_falsity(self):
        record = proposal()
        record.update(status='EXHAUSTED_REGISTERED_BOUND', candidate=None, used_constants=[])
        record['worker_audit']['constant_occurrences'] = {'proof_term': {}, 'type_annotations': {}}
        self.assertEqual(validate_worker(record)['status'], 'EXHAUSTED_REGISTERED_BOUND')
        record['candidate'] = ['const', 0]
        with self.assertRaises(ValueError): validate_worker(record)

    def test_missing_inventory_or_invented_dependency_is_refused(self):
        for field, value in [('imported_modules', []), ('schema', 'invented'),
                             ('constant_occurrences', {'proof_term': {}, 'type_annotations': {}})]:
            record = proposal()
            record['worker_audit'][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError): validate_worker(record)
        record = proposal()
        record['used_constants'] = []
        with self.assertRaises(ValueError): validate_worker(record)

    def test_unregistered_origin_is_not_a_declared_stdlib_module(self):
        record = proposal()
        record['worker_audit']['imported_modules'].append({'name': 'torch', 'origin': 'built-in'})
        with self.assertRaises(ValueError): validate_worker(record)

    def test_malformed_inventory_and_boolean_counts_are_not_valid_metadata(self):
        for entry in ['module', None, {'name': 'sys'}]:
            record = proposal()
            record['worker_audit']['imported_modules'].append(entry)
            with self.subTest(entry=entry), self.assertRaises(ValueError): validate_worker(record)
        record = proposal()
        record['used_constants'] = [False]
        with self.assertRaises(ValueError): validate_worker(record)
        record = proposal()
        record['worker_audit']['constant_occurrences']['proof_term']['0'] = True
        with self.assertRaises(ValueError): validate_worker(record)


if __name__ == '__main__': unittest.main()
