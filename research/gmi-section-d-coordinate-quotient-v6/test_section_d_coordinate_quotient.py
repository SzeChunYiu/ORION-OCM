import json
import tempfile
import unittest
from pathlib import Path

import section_d_coordinate_quotient_witness as w


class D6Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = w.build_results()
        cls.cells = w.build_atlas()

    def test_all_frozen_predictions(self):
        self.assertTrue(self.r['all_frozen_predictions_pass'])
        self.assertTrue(all(self.r['assertions'].values()))

    def test_full_schema_is_decision_sufficient(self):
        _, bad = w.fiber_report(self.cells)
        self.assertEqual(bad, [])
        self.assertTrue(self.r['quotient_theorem_check']['full_schema_sufficient'])

    def test_every_group_has_registered_drop_one_collision(self):
        self.assertEqual(set(self.r['drop_one_required_collision_pass']), set(w.GROUPS))
        self.assertTrue(all(self.r['drop_one_required_collision_pass'].values()))
        for group in w.GROUPS:
            _, bad = w.fiber_report(self.cells, group)
            self.assertTrue(bad, group)

    def test_remint_twins_are_same_schema_fiber_and_frontier(self):
        for source, row in self.r['source_remint_checks'].items():
            self.assertTrue(all(row.values()), source)

    def test_schema_values_do_not_leak_candidate_identity(self):
        self.assertTrue(w.no_leakage(self.cells))

    def test_verifier_changes_cost_not_exactness(self):
        ext = next(c for c in self.cells if c.specimen == 'A_cap64_Q16_ext')
        proof = next(c for c in self.cells if c.specimen == 'A_cap64_Q16_proof')
        self.assertEqual(ext.truth_digest, proof.truth_digest)
        self.assertEqual(ext.vectors['xor_fold'][2], True)
        self.assertEqual(proof.vectors['xor_fold'][2], True)
        self.assertEqual(ext.vectors['xor_fold'][:2], (4, 84))
        self.assertEqual(proof.vectors['xor_fold'][:2], (4, 56))
        self.assertEqual(ext.frontier, ('default_exceptions', 'full_map', 'xor_fold'))
        self.assertEqual(proof.frontier, ('xor_fold',))

    def test_expected_decision_partition_and_atlas_size(self):
        self.assertEqual(self.r['atlas_size'], 14)
        self.assertEqual(self.r['full_schema']['fiber_count'], 7)
        self.assertEqual(self.r['quotient_theorem_check']['decision_classes'], 5)

    def test_receipt_reproduction(self):
        here = Path(__file__).resolve().parent
        committed = json.loads((here / 'RESULT_V6.json').read_text())
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / 'result.json'
            out.write_text(json.dumps(w.receipt(w.build_results()), indent=2, sort_keys=True) + '\n')
            reproduced = json.loads(out.read_text())
        self.assertEqual(committed, reproduced)


if __name__ == '__main__':
    unittest.main()
