import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import section_d_uncertainty_extrap_witness as w

class V5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = w.build_results()

    def test_all_frozen_predictions(self):
        self.assertTrue(self.r["all_frozen_predictions_pass"])
        self.assertTrue(all(self.r["assertions"].values()))

    def test_exact_fit_and_heldout(self):
        a,b = w.fit_alpha_beta()
        self.assertEqual((a,b), (Fraction(3), Fraction(-3)))
        self.assertEqual(w.extrapolated(a,b,7), Fraction(18,7))
        self.assertEqual(w.extrapolated(a,b,8), Fraction(21,8))

    def test_uncertainty_exact_enumeration(self):
        for n in w.HELDOUT:
            vals=list(w.uncertainty_walls(n).values())
            self.assertEqual(min(vals), Fraction(3*n-5,n))
            self.assertEqual(max(vals), Fraction(3*n-1,n))
            self.assertTrue(min(vals) <= w.exact_boundary(n) <= max(vals))

    def test_abstention_inside_band(self):
        for n in w.HELDOUT:
            self.assertEqual(w.robust_winner(n, Fraction(2))[0], "dual_index")
            self.assertEqual(w.robust_winner(n, Fraction(5,2))[0], w.CANNOT)
            self.assertEqual(w.robust_winner(n, Fraction(3))[0], "value_index")

    def test_batch_twin_breaks_fit(self):
        a,b=w.fit_alpha_beta()
        self.assertTrue(any(w.extrapolated(a,b,n) != w.batch_boundary(n) for n in w.HELDOUT))

    def test_selectors_independent_agreement(self):
        for n in w.SCALES:
            vecs=tuple(w.resource_vector(name,n) for name in w.CANDIDATES)
            wall=w.exact_boundary(n)
            for x in (Fraction(1), wall-Fraction(1,10), wall, wall+Fraction(1,10), Fraction(4)):
                self.assertEqual(w.direct_winners(vecs,x), w.hull_winners(vecs,x))

    def test_receipt_reproduction(self):
        here=Path(__file__).resolve().parent
        committed=json.loads((here/"RESULT_V5.json").read_text())
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"result.json"
            p.write_text(json.dumps(w.build_results(), indent=2, sort_keys=True)+"\n")
            rerun=json.loads(p.read_text())
        self.assertEqual(committed, rerun)

if __name__ == "__main__":
    unittest.main()
