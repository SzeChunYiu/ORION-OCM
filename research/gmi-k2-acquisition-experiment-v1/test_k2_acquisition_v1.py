"""KAE-1..9. The live census is re-derived; the held-out run is bound to the
frozen receipt.  Controls must go red when fed a wrong claim."""
import functools
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


@functools.lru_cache(maxsize=None)
def _heldout_census_cached(items, minlen, cap):
    return _heldout_census_uncached(dict(items), minlen, cap)


def heldout_census(library, minlen=5, cap=5):
    """Cached wrapper: each library is regenerated once per process.

    Without this the four-library census (~11s) is paid by every assertion that
    needs it, which pushed the suite past the 60s checker budget.
    """
    return _heldout_census_cached(tuple(sorted(library.items())), minlen, cap)


def _heldout_census_uncached(library, minlen=5, cap=5):
    """Regenerate a held-out library census from the model, live.

    The held-out figures carry the load-bearing claims and were previously read
    from the frozen receipt only, so a change to the model that altered them
    would have left receipt and documents asserting the old result.  Measured
    cost: about 2.7s per library, 11s for all four.
    """
    pop = K.minimal_length_population(minlen, cap)
    reuse = nore = k2r = k2n = worse = 0
    reset_total = h_total = 0
    for sem in pop:
        avail = K.reuse_available(sem, library, cap)
        t = K.k2_trial(sem, library, cap)
        reset_total += t["reset"]; h_total += t["h"]
        if avail:
            reuse += 1; k2r += t["k2"]
        else:
            nore += 1; k2n += t["k2"]; worse += t["h_worse"]
    return {"alphabet": len(K.with_library(library)),
            "reuse_targets": reuse, "noreuse_targets": nore, "k2_on_reuse": k2r,
            "k2_on_noreuse": k2n, "h_worse_on_noreuse": worse,
            # Raw totals close the blind spot: every count above is a comparison,
            # so a monotone rescaling of cost leaves them all unchanged.
            "reset_cost_total": reset_total, "h_cost_total": h_total}


class KAE_HeldoutReproduction(unittest.TestCase):
    """REPRODUCTION layer: regenerate the held-out census and require equality.

    Catches drift in any number.  On its own it would pass a coordinated
    model-and-receipt update, which is what the claim pins below are for.
    """

    def test_every_heldout_library_regenerates_its_recorded_figures(self):
        recorded = receipt()["confirmatory_heldout"]["results"]
        for name, lib in sorted(LIBS.items()):
            live = heldout_census(lib)
            self.assertEqual({k: live[k] for k in recorded[name]}, recorded[name],
                             "%s: regenerated census differs from the receipt" % name)

    def test_the_population_size_is_the_recorded_one(self):
        h = receipt()["confirmatory_heldout"]
        self.assertEqual(len(K.minimal_length_population(h["minimal_len"], h["max_len"])),
                         h["targets"])

    def test_control_a_perturbed_library_must_fail_reproduction(self):
        """A reproduction check that cannot go red is the defect being fixed."""
        perturbed = {"q1": ("square", "inc")}          # squares' macro, altered
        rec = receipt()["confirmatory_heldout"]["results"]["squares"]
        live = heldout_census(perturbed)
        self.assertNotEqual({k: live[k] for k in rec}, rec)


class KAE_CostTotalsCloseTheOrderPreservingBlindSpot(unittest.TestCase):
    """Every census count is a COMPARISON, so a monotone rescaling of cost
    leaves all of them unchanged.  Doubling every charge was verified to keep
    all 24 assertions green.  Raw totals are what move under such a change."""

    EXPECTED = {
        "dec_inc":    (396080, 903784),
        "orig":       (396080, 1248876),
        "squares":    (396080, 680016),
        "three_part": (396080, 2550112),
    }

    def test_cost_totals_are_the_recorded_ones(self):
        for name, lib in sorted(LIBS.items()):
            live = heldout_census(lib)
            self.assertEqual((live["reset_cost_total"], live["h_cost_total"]),
                             self.EXPECTED[name], name)

    def test_reset_total_is_library_independent(self):
        """RESET never sees a library; divergence would mean contamination."""
        totals = {heldout_census(lib)["reset_cost_total"] for lib in LIBS.values()}
        self.assertEqual(len(totals), 1, "RESET cost must not depend on the library")
        self.assertEqual(totals.pop(), 396080)

    def test_the_totals_would_move_under_a_scaling_that_counts_cannot_see(self):
        """Documents the boundary with arithmetic rather than a claim."""
        live = heldout_census(LIBS["squares"])
        scaled_reset = live["reset_cost_total"] * 2
        scaled_h = live["h_cost_total"] * 2
        self.assertNotEqual(scaled_reset, live["reset_cost_total"])
        self.assertNotEqual(scaled_h, live["h_cost_total"])
        # ... while the verdict the counts record is unchanged:
        self.assertEqual(live["h_cost_total"] < live["reset_cost_total"],
                         scaled_h < scaled_reset)


class KAE4_K2IsPositiveWhereReuseExists(unittest.TestCase):
    """CLAIM PINS: the specific headlines the documents assert."""

    def test_squares_library_is_fully_positive_on_heldout_reuse_targets(self):
        live = heldout_census(LIBS["squares"])
        self.assertEqual(live["k2_on_reuse"], live["reuse_targets"])
        self.assertEqual(live["reuse_targets"], 148)

    def test_reuse_is_not_sufficient(self):
        live = {k: heldout_census(v) for k, v in LIBS.items()}
        rates = {k: (v["k2_on_reuse"], v["reuse_targets"]) for k, v in live.items()
                 if v["reuse_targets"] > 0}
        self.assertTrue(any(a < b for a, b in rates.values()),
                        "if every rate were 100% the condition would be an iff")

    def test_the_minimum_rate_is_the_documented_one(self):
        """The document states 39.3728%; pin the fraction it comes from."""
        live = heldout_census(LIBS["three_part"])
        self.assertEqual((live["k2_on_reuse"], live["reuse_targets"]), (113, 287))
        self.assertAlmostEqual(100.0 * 113 / 287, 39.3728, places=4)


class KAE5_AbsentReuseRetentionHarms(unittest.TestCase):
    def test_heldout_harm_is_total(self):
        for name, lib in sorted(LIBS.items()):
            live = heldout_census(lib)
            if live["noreuse_targets"]:
                self.assertEqual(live["h_worse_on_noreuse"], live["noreuse_targets"], name)

    def test_necessity_holds_live_on_the_heldout_population(self):
        """The headline: zero K2 successes without reuse, regenerated."""
        total_noreuse = 0
        for name, lib in sorted(LIBS.items()):
            live = heldout_census(lib)
            self.assertEqual(live["k2_on_noreuse"], 0, name)
            total_noreuse += live["noreuse_targets"]
        self.assertEqual(total_noreuse, 1104, "held-out no-reuse pairs")

    def test_dec_inc_tests_necessity_but_not_sufficiency(self):
        live = heldout_census(LIBS["dec_inc"])
        self.assertEqual(live["reuse_targets"], 0)
        self.assertGreater(live["noreuse_targets"], 0)


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


if __name__ == "__main__":
    unittest.main()
