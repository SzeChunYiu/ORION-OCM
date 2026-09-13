"""Independent recomputation of the ECOLOGY_PREDICTION_V1 table.

The minimiser here does not read the document; it recomputes the winner by
exhaustive comparison over the admissible set and is checked against the
predictions stated by hand.
"""
from fractions import Fraction as F
import unittest

import learning_law_selection_v1 as M

ECOLOGIES = {
    "E1_SAMPLE_SCARCE":      {"LIKELIHOOD_EVAL": F(5), "GRADIENT_EVAL": F(1)},
    "E2_MODEL_KNOWN":        {"LIKELIHOOD_EVAL": F(1), "GRADIENT_EVAL": F(5)},
    "E3_ENUMERABLE":         {"ENUMERATION": F(1, 2)},
    "E4_COMPARISON_ONLY":    {"COMPARISON": F(1, 2)},
    "E5_PROJECTION_CHEAP":   {"PROJECTION": F(1, 3)},
    "E6_NORMALISATION_CHEAP": {"NORMALIZATION": F(1, 3)},
}

MIXED = frozenset({"DIFFERENTIABLE_OBJECTIVE", "SIMPLEX_GEOMETRY",
                   "LIKELIHOOD_MODEL", "FINITE_HYPOTHESES"})
DISCRETE = frozenset({"DISCRETE_PROGRAM_SPACE", "ORDINAL_COMPARISON"})
GEOMETRIES = frozenset({"DIFFERENTIABLE_OBJECTIVE", "EUCLIDEAN_GEOMETRY",
                        "SIMPLEX_GEOMETRY"})

PREDICTIONS = [
    ("P1", MIXED,     "E1_SAMPLE_SCARCE",       "MIRROR_DESCENT"),
    ("P2", MIXED,     "E2_MODEL_KNOWN",         "BAYES_UPDATE"),
    ("P3", DISCRETE,  "E3_ENUMERABLE",          "EXACT_SEARCH"),
    ("P4", DISCRETE,  "E4_COMPARISON_ONLY",     "ORDINAL_HILL_CLIMB"),
    ("P5", GEOMETRIES, "E5_PROJECTION_CHEAP",   "GRADIENT_STEP"),
    ("P6", GEOMETRIES, "E6_NORMALISATION_CHEAP", "MIRROR_DESCENT"),
]

PAIRS = (("P1", "P2"), ("P3", "P4"), ("P5", "P6"))


def prices_for(ecology):
    p = M.uniform_prices()
    p.update(ECOLOGIES[ecology])
    return p


def independent_winner(caps, prices):
    """Exhaustive minimiser written without reference to the prediction table."""
    best, winners = None, []
    for law in sorted(M.LAWS):
        if not M.LAWS[law]["requires"] <= frozenset(caps):
            continue
        c = sum(prices[op] for op in M.LAWS[law]["uses"])
        if best is None or c < best:
            best, winners = c, [law]
        elif c == best:
            winners.append(law)
    return winners[0] if len(winners) == 1 else None


class EcologyPredictions(unittest.TestCase):
    def test_each_prediction_is_recomputed_independently(self):
        for tag, caps, eco, predicted in PREDICTIONS:
            got = independent_winner(caps, prices_for(eco))
            self.assertEqual(got, predicted, "%s: predicted %s, recomputed %s"
                             % (tag, predicted, got))

    def test_model_selection_agrees_with_the_independent_minimiser(self):
        for tag, caps, eco, _ in PREDICTIONS:
            self.assertEqual(M.select(caps, prices_for(eco))["law"],
                             independent_winner(caps, prices_for(eco)), tag)

    def test_each_pair_actually_separates(self):
        byname = {t: (c, e) for t, c, e, _ in PREDICTIONS}
        for a, b in PAIRS:
            ca, ea = byname[a]; cb, eb = byname[b]
            self.assertEqual(ca, cb, "%s/%s must share capabilities" % (a, b))
            self.assertNotEqual(independent_winner(ca, prices_for(ea)),
                                independent_winner(cb, prices_for(eb)),
                                "%s/%s did not separate" % (a, b))

    def test_control_a_wrong_prediction_would_fail(self):
        caps, eco = MIXED, "E1_SAMPLE_SCARCE"
        self.assertNotEqual(independent_winner(caps, prices_for(eco)), "BAYES_UPDATE")

    def test_named_capability_sets_admit_only_the_listed_laws(self):
        self.assertEqual(M.admissible(MIXED), ("BAYES_UPDATE", "MIRROR_DESCENT"))
        self.assertEqual(M.admissible(DISCRETE), ("EXACT_SEARCH", "ORDINAL_HILL_CLIMB"))
        self.assertEqual(M.admissible(GEOMETRIES), ("GRADIENT_STEP", "MIRROR_DESCENT"))


if __name__ == "__main__":
    unittest.main()
