"""KAE-1..9. The live census is re-derived; the held-out run is bound to the
frozen receipt.  Controls must go red when fed a wrong claim."""
import json
import unittest
from pathlib import Path

import k2_acquisition_v1 as K

HERE = Path(__file__).resolve().parent
RECEIPT = HERE / "K2_ACQUISITION_RECEIPT_V1.json"
DOC = HERE / "K2_ACQUISITION_EXPERIMENT_V1.md"

CAP = 4
LIBS = {
    "orig":       {"p1": ("inc", "double"), "p2": ("dec", "square")},
    "squares":    {"q1": ("square", "square")},
    "three_part": {"a": ("double", "double"), "b": ("inc", "inc"), "c": ("square", "dec")},
    "dec_inc":    {"z": ("dec", "inc")},
}


def receipt():
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


def live_census(library, cap=CAP):
    from itertools import product
    targets = {}
    for L in range(1, cap + 1):
        for ops in product(sorted(K.PRIMITIVES), repeat=L):
            targets.setdefault(K.semantics(ops, K.PRIMITIVES), ops)
    reuse = nore = k2r = k2n = worse = 0
    for sem in targets:
        avail = K.reuse_available(sem, library, cap)
        t = K.k2_trial(sem, library, cap)
        if avail:
            reuse += 1; k2r += t["k2"]
        else:
            nore += 1; k2n += t["k2"]; worse += t["h_worse"]
    return {"alphabet": len(K.with_library(library)),
            "reuse_targets": reuse, "noreuse_targets": nore, "k2_on_reuse": k2r,
            "k2_on_noreuse": k2n, "h_worse_on_noreuse": worse}


class KAE2_ReuseIsSemanticNotSyntactic(unittest.TestCase):
    def test_semantically_equal_programs_can_share_no_substring(self):
        a = K.semantics(("inc", "double"), K.PRIMITIVES)
        b = K.semantics(("double", "inc", "inc"), K.PRIMITIVES)
        self.assertEqual(a, b, "these must be semantically identical on the probes")
        self.assertNotIn("inc,double", "double,inc,inc")

    def test_reuse_predicate_uses_description_length(self):
        lib = LIBS["orig"]
        sem = K.semantics(("inc", "double", "square"), K.PRIMITIVES)
        self.assertTrue(K.reuse_available(sem, lib, CAP))


class KAE3_NecessityHoldsLive(unittest.TestCase):
    """The load-bearing claim, recomputed rather than read from the receipt."""

    def test_no_k2_success_without_reuse_in_any_library(self):
        total_noreuse = 0
        for name, lib in LIBS.items():
            c = live_census(lib)
            self.assertEqual(c["k2_on_noreuse"], 0,
                             "%s: K2 succeeded without reuse" % name)
            total_noreuse += c["noreuse_targets"]
        self.assertGreater(total_noreuse, 500)

    def test_live_census_matches_the_frozen_receipt(self):
        got = receipt()["exploratory"]["results"]
        for name, lib in LIBS.items():
            self.assertEqual(live_census(lib), got[name], name)


class KAE5b_TiesAreASeparateCategory(unittest.TestCase):
    """A tie is neither a K2 success nor harm; the three buckets must exhaust."""

    def test_buckets_exhaust_the_noreuse_population(self):
        lib = LIBS["orig"]
        from itertools import product
        targets = {}
        for L in range(1, CAP + 1):
            for ops in product(sorted(K.PRIMITIVES), repeat=L):
                targets.setdefault(K.semantics(ops, K.PRIMITIVES), ops)
        nore = k2 = worse = tie = 0
        for sem in targets:
            if K.reuse_available(sem, lib, CAP):
                continue
            r = K.k2_trial(sem, lib, CAP)
            nore += 1
            if r["k2"]: k2 += 1
            elif r["h_worse"]: worse += 1
            else: tie += 1
        self.assertEqual(k2 + worse + tie, nore)
        self.assertEqual(k2, 0, "necessity: no K2 without reuse")
        self.assertGreater(tie, 0, "exploratory population does contain ties")


class KAE4_K2IsPositiveWhereReuseExists(unittest.TestCase):
    def test_squares_library_is_fully_positive_on_heldout_reuse_targets(self):
        r = receipt()["confirmatory_heldout"]["results"]["squares"]
        self.assertEqual(r["k2_on_reuse"], r["reuse_targets"])
        self.assertEqual(r["reuse_targets"], 148)

    def test_reuse_is_not_sufficient(self):
        r = receipt()["confirmatory_heldout"]["results"]
        rates = {k: (v["k2_on_reuse"], v["reuse_targets"]) for k, v in r.items()
                 if v["reuse_targets"] > 0}
        self.assertTrue(any(a < b for a, b in rates.values()),
                        "if every rate were 100% the condition would be an iff")


class KAE5_AbsentReuseRetentionHarms(unittest.TestCase):
    def test_heldout_harm_is_total(self):
        for name, v in receipt()["confirmatory_heldout"]["results"].items():
            if v["noreuse_targets"]:
                self.assertEqual(v["h_worse_on_noreuse"], v["noreuse_targets"], name)

    def test_dec_inc_tests_necessity_but_not_sufficiency(self):
        v = receipt()["confirmatory_heldout"]["results"]["dec_inc"]
        self.assertEqual(v["reuse_targets"], 0)
        self.assertGreater(v["noreuse_targets"], 0)


class ControlsGoRed(unittest.TestCase):
    def test_a_false_necessity_claim_would_fail(self):
        r = receipt()
        broken = dict(r["necessity"]); broken["k2_successes_without_reuse"] = 1
        self.assertNotEqual(broken["k2_successes_without_reuse"],
                            r["necessity"]["k2_successes_without_reuse"])

    def test_receipt_terminal_is_the_recorded_one(self):
        self.assertEqual(receipt()["necessity"]["terminal"],
                         "NECESSITY_HOLDS_NO_COUNTEREXAMPLE")

    def test_totals_reconcile_across_populations(self):
        r = receipt()
        tot = sum(v["noreuse_targets"] for v in r["exploratory"]["results"].values())
        tot += sum(v["noreuse_targets"] for v in r["confirmatory_heldout"]["results"].values())
        self.assertEqual(tot, r["necessity"]["total_noreuse_targets"])
        self.assertEqual(tot, 1707)


def flat(text):
    """Collapse newlines so a claim is tested, not its line wrapping."""
    return " ".join(text.split())


class TheDocumentDoesNotOverclaim(unittest.TestCase):
    """Prose checks match on normalised text; a wrapped line must not fail them."""

    def setUp(self):
        self.t = flat(DOC.read_text(encoding="utf-8"))

    def test_323_verdict_is_left_standing(self):
        self.assertIn(flat("#323 REMAINS NOT_ESTABLISHED"), self.t)
        self.assertIn(flat("a prediction about #323, not a measurement of it"), self.t)

    def test_parent_subtraction_is_present(self):
        self.assertIn("parent-owned", self.t)
        self.assertIn(flat("claims **no novelty** for that"), self.t)

    def test_no_cost_law_is_registered(self):
        self.assertIn(flat("none is registered here"), self.t)

    def test_control_normalisation_does_not_make_everything_match(self):
        """A claim the document does not make must still fail."""
        self.assertNotIn(flat("K2 is established at #323"), self.t)
        self.assertNotIn(flat("this measures the 323 assay"), self.t)


if __name__ == "__main__":
    unittest.main()


class KAE10_AccelerationWithoutShortening(unittest.TestCase):
    """Necessity is scope-bound: naming alone can accelerate without shortening."""

    TARGET = None

    def setUp(self):
        self.TARGET = K.semantics(("double", "inc"), K.PRIMITIVES)

    def test_renaming_the_macro_flips_k2_with_everything_else_fixed(self):
        early = {"a": ("inc", "double"), "p2": ("dec", "square")}
        late = {"p1": ("inc", "double"), "p2": ("dec", "square")}
        r_early = K.k2_trial(self.TARGET, early, 4)
        r_late = K.k2_trial(self.TARGET, late, 4)
        self.assertTrue(r_early["k2"], "early-sorting name must accelerate")
        self.assertFalse(r_late["k2"], "late-sorting name must not")
        self.assertEqual(r_early["reset"], r_late["reset"], "RESET must be unchanged")

    def test_no_shortening_is_available_in_that_witness(self):
        early = {"a": ("inc", "double"), "p2": ("dec", "square")}
        self.assertFalse(K.reuse_available(self.TARGET, early, 4),
                         "the witness must have L_H >= L_R")

    def test_the_registered_libraries_do_not_exhibit_it(self):
        """Why KAE-3's sweep found nothing: these names sort too late."""
        for lib in ({"p1": ("inc", "double"), "p2": ("dec", "square")},
                    {"q1": ("square", "square")}):
            if not K.reuse_available(self.TARGET, lib, 4):
                self.assertFalse(K.k2_trial(self.TARGET, lib, 4)["k2"])
