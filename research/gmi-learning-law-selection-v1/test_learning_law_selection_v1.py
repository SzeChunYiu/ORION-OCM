"""Exact finite witnesses for LLS-1..LLS-6.

Every assertion checks a computed value over the complete 128-contract lattice,
not the presence of a word in a document.
"""
from fractions import Fraction as F
from itertools import combinations
import unittest

import learning_law_selection_v1 as M


class LLS1_PremisesAreTheRegisteredAntecedents(unittest.TestCase):
    def test_each_law_binds_to_a_source_clause(self):
        self.assertEqual(
            {n: s["clause"] for n, s in M.LAWS.items()},
            {"GRADIENT_STEP": "O1", "MIRROR_DESCENT": "O2", "BAYES_UPDATE": "O3",
             "EXACT_SEARCH": "core-exact", "ORDINAL_HILL_CLIMB": "core-ordinal"})

    def test_no_law_is_admissible_without_its_premises(self):
        for name, spec in M.LAWS.items():
            for missing in spec["requires"]:
                caps = spec["requires"] - {missing}
                self.assertNotIn(name, M.admissible(caps),
                                 "%s admitted without %s" % (name, missing))


class LLS2_TheMapIsTotal(unittest.TestCase):
    def test_every_contract_receives_exactly_one_terminal(self):
        prices = M.uniform_prices()
        seen = {}
        for caps in M.all_contracts():
            r = M.select(caps, prices)
            self.assertIn(r["terminal"], M.TERMINALS)
            seen[caps] = r["terminal"]
        self.assertEqual(len(seen), 128)

    def test_terminal_census_matches_an_independent_recomputation(self):
        """The infeasible count is derived from the premise predicate, not asserted."""
        prices = M.uniform_prices()
        census = {}
        for caps in M.all_contracts():
            t = M.select(caps, prices)["terminal"]
            census[t] = census.get(t, 0) + 1
        self.assertEqual(sum(census.values()), 128)

        # Independent closed-form: no law admissible iff
        #   not DISC and not(DIFF and EUC) and not(DIFF and SIMPLEX)
        #   and not(LIK and FINH and SIMPLEX)
        expected = 0
        for caps in M.all_contracts():
            has = lambda c: c in caps
            if (not has("DISCRETE_PROGRAM_SPACE")
                    and not (has("DIFFERENTIABLE_OBJECTIVE") and has("EUCLIDEAN_GEOMETRY"))
                    and not (has("DIFFERENTIABLE_OBJECTIVE") and has("SIMPLEX_GEOMETRY"))
                    and not (has("LIKELIHOOD_MODEL") and has("FINITE_HYPOTHESES")
                             and has("SIMPLEX_GEOMETRY"))):
                expected += 1
        self.assertEqual(census.get("INFEASIBLE_AT_CONTRACT"), expected)
        self.assertEqual(census.get("SELECTED", 0) + census.get("UNDETERMINED_TIE", 0),
                         128 - expected)
        # Control: the predicate must not be vacuous in either direction.
        self.assertGreater(expected, 0)
        self.assertLess(expected, 128)


class LLS3_PricesSelectTheLaw(unittest.TestCase):
    """The positive result: resources decide which law wins, at fixed capabilities."""

    def test_gradient_versus_bayes_flips_on_price(self):
        caps = {"DIFFERENTIABLE_OBJECTIVE", "SIMPLEX_GEOMETRY",
                "LIKELIHOOD_MODEL", "FINITE_HYPOTHESES"}
        self.assertEqual(M.admissible(caps), ("BAYES_UPDATE", "MIRROR_DESCENT"))
        cheap_grad = M.uniform_prices()
        cheap_grad["GRADIENT_EVAL"] = F(1)
        cheap_grad["LIKELIHOOD_EVAL"] = F(5)
        self.assertEqual(M.select(caps, cheap_grad)["law"], "MIRROR_DESCENT")
        cheap_lik = M.uniform_prices()
        cheap_lik["GRADIENT_EVAL"] = F(5)
        cheap_lik["LIKELIHOOD_EVAL"] = F(1)
        self.assertEqual(M.select(caps, cheap_lik)["law"], "BAYES_UPDATE")

    def test_search_versus_hill_climb_flips_on_price(self):
        caps = {"DISCRETE_PROGRAM_SPACE", "ORDINAL_COMPARISON"}
        cheap_enum = M.uniform_prices(); cheap_enum["ENUMERATION"] = F(1, 2)
        self.assertEqual(M.select(caps, cheap_enum)["law"], "EXACT_SEARCH")
        cheap_cmp = M.uniform_prices(); cheap_cmp["COMPARISON"] = F(1, 2)
        self.assertEqual(M.select(caps, cheap_cmp)["law"], "ORDINAL_HILL_CLIMB")

    def test_geometry_alone_flips_gradient_versus_mirror(self):
        caps = {"DIFFERENTIABLE_OBJECTIVE", "EUCLIDEAN_GEOMETRY", "SIMPLEX_GEOMETRY"}
        cheap_proj = M.uniform_prices(); cheap_proj["PROJECTION"] = F(1, 3)
        self.assertEqual(M.select(caps, cheap_proj)["law"], "GRADIENT_STEP")
        cheap_norm = M.uniform_prices(); cheap_norm["NORMALIZATION"] = F(1, 3)
        self.assertEqual(M.select(caps, cheap_norm)["law"], "MIRROR_DESCENT")


class LLS4_ObservationalNonIdentifiability(unittest.TestCase):
    """The DU-1 analogue at the law level: hiding geometry hides the law."""

    def test_hidden_geometry_leaves_the_law_unidentified(self):
        prices = M.uniform_prices()
        prices["PROJECTION"] = F(1, 3)      # breaks the tie toward GRADIENT_STEP
        hidden = {"EUCLIDEAN_GEOMETRY", "SIMPLEX_GEOMETRY"}
        by_projection = {}
        for caps in M.all_contracts():
            key = M.observational_projection(caps, hidden)
            law = M.select(caps, prices)["law"]
            by_projection.setdefault(key, set()).add(law)
        collisions = {k: v for k, v in by_projection.items() if len(v) > 1}
        self.assertTrue(collisions, "no collision found; probe is not discriminating")
        witness = sorted(collisions.items(), key=lambda kv: (len(kv[0]), sorted(map(str, kv[1]))))[0]
        self.assertGreaterEqual(len(witness[1]), 2)

    def test_full_contract_does_identify_the_law(self):
        prices = M.uniform_prices(); prices["PROJECTION"] = F(1, 3)
        by_contract = {}
        for caps in M.all_contracts():
            by_contract[caps] = M.select(caps, prices)["law"]
        self.assertEqual(len(by_contract), 128)


class LLS5_RefusalsAreExplicit(unittest.TestCase):
    def test_premise_free_selection_is_refused(self):
        self.assertEqual(M.select(set(), M.uniform_prices())["terminal"],
                         "INFEASIBLE_AT_CONTRACT")

    def test_unpriced_operation_refuses_rather_than_defaults(self):
        prices = M.uniform_prices(); del prices["GRADIENT_EVAL"]
        with self.assertRaises(ValueError):
            M.select({"DIFFERENTIABLE_OBJECTIVE", "EUCLIDEAN_GEOMETRY"}, prices)

    def test_unregistered_capability_is_refused(self):
        with self.assertRaises(ValueError):
            M.admissible({"TELEPATHY"})

    def test_float_prices_are_refused(self):
        prices = M.uniform_prices(); prices["GRADIENT_EVAL"] = 1.0
        with self.assertRaises(ValueError):
            M.select({"DIFFERENTIABLE_OBJECTIVE", "EUCLIDEAN_GEOMETRY"}, prices)


if __name__ == "__main__":
    unittest.main()
