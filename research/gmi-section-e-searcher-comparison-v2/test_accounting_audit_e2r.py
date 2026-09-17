import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import accounting_audit_e2r as a
import section_e_searcher_comparison_witness as w


class E2RAccountingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = a.build_audit()

    def test_exit_green(self):
        self.assertTrue(self.r['exit_green'])
        self.assertTrue(self.r['all_frozen_predictions_match'])
        self.assertTrue(self.r['success_independence_reproduced'])

    def test_per_example_ops_derived_not_hardcoded(self):
        self.assertEqual(a.per_example_ops(), 26)

    def test_no_cache_strict_events(self):
        self.assertEqual(a.strict_no_cache_events(), 10)

    def test_drift_events_match_frozen_attempts(self):
        self.assertEqual(a.drift_events_exact(), Fraction(613, 125))
        self.assertEqual(a.drift_events_exact(), Fraction(w.neutral_drift_exact(T=5)['expected_proposal_or_mutation_attempts']))

    def test_a0_touches_reproduced_from_traces(self):
        t = self.r['traces']
        self.assertEqual(Fraction(32) * (Fraction(t['random']['cached_unique']) + Fraction(t['random']['relaxed_evals'])), 320)
        self.assertEqual(Fraction(32) * (Fraction(t['strict']['cached_unique']) + Fraction(t['strict']['relaxed_evals'])), 192)
        self.assertEqual(Fraction(32) * (Fraction(t['drift']['cached_unique']) + Fraction(t['drift']['relaxed_evals'])), Fraction(499904, 3125))
        self.assertEqual(Fraction(32) * (Fraction(t['nas']['cached_unique']) + Fraction(t['nas']['relaxed_evals'])), 352)
        self.assertEqual(Fraction(32) * (Fraction(t['darts']['cached_unique']) + Fraction(t['darts']['relaxed_evals'])), 64)

    def test_every_predicted_row_matches(self):
        for name, rows in self.r['accountings'].items():
            for searcher, row in rows.items():
                self.assertTrue(row['prediction_match'], f"{name}/{searcher}: {row}")

    def test_v_nas_flips_only_under_a4(self):
        flips = {n: rows['nas']['relation_to_a0'] for n, rows in self.r['accountings'].items()}
        self.assertEqual(flips, {
            'A1_EVAL_COUNT': 'HOLD', 'A2_EXEC_B': 'HOLD', 'A3_OP_PRICE': 'HOLD',
            'A3B_OP_PRICE_NOCACHE': 'HOLD', 'A4_VERIFIER_EXEMPT': 'FLIP'})

    def test_nas_at_or_over_claim_revived(self):
        c = self.r['claims']['C-NAS-AT-OR-OVER']
        self.assertEqual(c['disposition'], 'REVIVED')
        self.assertTrue(c['at_or_over_everywhere'])
        self.assertTrue(c['never_strictly_within'])
        self.assertTrue(c['darts_strictly_cheaper_everywhere'])

    def test_c_nas_over_registered_sensitive_with_flip_witness(self):
        c = self.r['claims']['C-NAS-OVER']
        self.assertEqual(c['disposition'], 'ACCOUNTING_SENSITIVE')
        self.assertEqual(c['flip_witnesses'], {'A4_VERIFIER_EXEMPT': {'from': 'over', 'to': 'at'}})

    def test_c_ordering_accounting_robust(self):
        c = self.r['claims']['C-ORDERING']
        self.assertEqual(c['disposition'], 'ACCOUNTING_ROBUST')
        self.assertTrue(all(c['per_accounting'].values()))

    def test_pins_present(self):
        pins = self.r['pins']
        for k in ('FREEZE_E2.md', 'ACCOUNTING_FREEZE_E2.md',
                  'section_e_searcher_comparison_witness.py', 'ACCOUNTING_AUDIT_FREEZE_E2R.md'):
            self.assertEqual(len(pins[k]), 64)

    def test_receipt_reproduction(self):
        here = Path(__file__).resolve().parent
        committed = json.loads((here / 'ACCOUNTING_AUDIT_RESULT_E2R.json').read_text())
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'result.json'
            p.write_text(json.dumps(a.build_audit(), indent=2, sort_keys=True) + '\n')
            rerun = json.loads(p.read_text())
        self.assertEqual(committed, rerun)


if __name__ == '__main__':
    unittest.main()
