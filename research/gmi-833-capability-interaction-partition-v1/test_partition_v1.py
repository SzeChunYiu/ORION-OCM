"""Controls for gmi-833-capability-interaction-partition-v1 (CIP-1..CIP-4).

Run: python3 -I -B test_partition_v1.py -v
     python3 -I -O -B test_partition_v1.py -v      (asserts must not carry the claims)
Stdlib only; exact arithmetic only.
"""
import importlib.util
import pathlib
import sys
import unittest
from fractions import Fraction

ROOT = pathlib.Path(__file__).resolve().parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


W = _load("partition_witness_v1", ROOT / "partition_witness_v1.py")       # ROUTE A
O = _load("partition_oracle_v1", ROOT / "partition_oracle_v1.py")          # ROUTE B/C

# The corrected object lives one directory over; used ONLY to prove the input tables
# agree (data), never for classification logic.
SHIPPED = ROOT.parent / "gmi-capability-interactions-unified-v1" / "interactions_witness.py"
S = _load("interactions_witness_shipped", SHIPPED) if SHIPPED.exists() else None

CENSUS = W.census()
ROUTE_B = O.route_b_census()
ROUTE_C = O.route_c_closed_form()

EXPECTED = {"INDEPENDENT": 8, "REDUNDANT": 287, "PARTIAL_SHARING": 56, "INTERFERING": 0}


class InputAgreement(unittest.TestCase):
    """The three routes must be reading the SAME A4 contract."""

    def test_route_a_has_27_capabilities(self):
        self.assertEqual(27, len(W.CAPABILITY_IDS))

    def test_route_b_table_matches_route_a(self):
        b = dict((cid, frozenset(sig)) for cid, sig in O.A4_TABLE)
        self.assertEqual(dict(W.RESOURCE_CHANNELS), b)

    def test_tables_match_the_shipped_contract(self):
        if S is None:
            self.skipTest("shipped package not present")
        self.assertEqual(dict(S.RESOURCE_CHANNELS), dict(W.RESOURCE_CHANNELS))

    def test_shipped_overlap_label_reproduced_exactly(self):
        """Route A reproduces interactions_witness.interaction_type as DATA."""
        if S is None:
            self.skipTest("shipped package not present")
        ids = W.CAPABILITY_IDS
        for i, x in enumerate(ids):
            for y in ids[i + 1:]:
                cx, cy = W.RESOURCE_CHANNELS[x], W.RESOURCE_CHANNELS[y]
                self.assertEqual(S.interaction_type(cx, cy), W.shipped_overlap_label(cx, cy))


class CIP1Partition(unittest.TestCase):
    """CIP-1: exactly one class per admissible burden triple."""

    def test_integer_grid_partitions(self):
        n, fails = W.verify_partition_on_grid()
        self.assertGreater(n, 400)
        self.assertEqual([], fails)

    def test_rational_grid_partitions(self):
        n, fails = W.verify_partition_on_rational_grid()
        self.assertGreater(n, 100)
        self.assertEqual([], fails)

    def test_max_le_joint_le_sum_under_union_accounting(self):
        ok, n = W.union_accounting_is_subadditive()
        self.assertTrue(ok)
        self.assertEqual(351, n)

    def test_redundant_guard_makes_classes_disjoint(self):
        """max == sum (zero-burden partner) is INDEPENDENT alone, never also REDUNDANT."""
        self.assertEqual(["INDEPENDENT"], W.classes_holding(3, 0, 3))
        self.assertEqual("INDEPENDENT", W.classify(3, 0, 3))

    def test_redundant_guard_does_not_break_exhaustiveness(self):
        """Every admissible triple with max == sum still lands in exactly one class."""
        for b in range(0, 8):
            for j in range(b, 2 * b + 4):
                held = W.classes_holding(b, 0, j)
                self.assertEqual(1, len(held), "b=%d j=%d -> %s" % (b, j, held))

    def test_interfering_class_is_reachable(self):
        bx, by, j = W.ce2_interfering_triple()
        self.assertGreater(j, bx + by)
        self.assertEqual("INTERFERING", W.classify(bx, by, j))

    def test_saving_class_is_the_disjoint_union(self):
        """The original 'Synergistic' condition joint < sum survives exactly as
        REDUNDANT (disjoint union) PARTIAL_SHARING. Nothing is deleted."""
        for bx in range(0, 7):
            for by in range(0, 7):
                for j in range(max(bx, by), bx + by + 3):
                    k = W.classify(bx, by, j)
                    self.assertEqual(j < bx + by, k in W.SAVING_CLASSES,
                                     "%s %s %s -> %s" % (bx, by, j, k))

    def test_inadmissible_triple_is_rejected_not_absorbed(self):
        self.assertEqual([], W.classes_holding(4, 2, 3))
        self.assertRaises(W.Inadmissible, W.classify, 4, 2, 3)

    def test_negative_burden_rejected(self):
        self.assertRaises(W.Inadmissible, W.classify, -1, 2, 2)


class CIP2Census(unittest.TestCase):
    """CIP-2: the corrected 27x27 census, two materially independent routes + closed form."""

    def test_route_a_counts(self):
        self.assertEqual(351, CENSUS["pairs"])
        self.assertEqual(EXPECTED, CENSUS["corrected_counts"])

    def test_route_b_counts(self):
        self.assertEqual(351, ROUTE_B["pairs"])
        self.assertEqual(EXPECTED, ROUTE_B["counts"])

    def test_route_c_closed_form_counts(self):
        self.assertEqual(351, ROUTE_C["pairs"])
        self.assertEqual(EXPECTED, ROUTE_C["counts"])

    def test_routes_agree_pair_by_pair(self):
        a = dict(((r["x"], r["y"]), r["corrected_class"]) for r in CENSUS["rows"])
        b = dict(((r["x"], r["y"]), r["corrected_class"]) for r in ROUTE_B["rows"])
        self.assertEqual(351, len(a))
        self.assertEqual(a, b)

    def test_route_b_burdens_agree_pair_by_pair(self):
        a = dict(((r["x"], r["y"]), (r["B_x"], r["B_y"], r["joint"])) for r in CENSUS["rows"])
        b = dict(((r["x"], r["y"]), (r["B_x"], r["B_y"], r["joint"])) for r in ROUTE_B["rows"])
        self.assertEqual(a, b)

    def test_def1_count(self):
        self.assertEqual(56, CENSUS["def1_shipped_contradicts_section_1_2"])

    def test_def2_count(self):
        self.assertEqual(287, CENSUS["def2_pairs_with_non_unique_1_2_label"])

    def test_labels_changed(self):
        self.assertEqual(217, CENSUS["labels_changed"])

    def test_shipped_counts_reproduced(self):
        self.assertEqual({"independent": 8, "synergistic": 161, "redundant": 182},
                         CENSUS["shipped_counts"])

    def test_def1_set_equals_partial_sharing_class(self):
        """DEF-1's 56 contradictions are EXACTLY the PARTIAL_SHARING class."""
        d1 = set((r["x"], r["y"]) for r in CENSUS["rows"] if r["shipped_contradicts_1_2"])
        ps = set((r["x"], r["y"]) for r in CENSUS["rows"] if r["corrected_class"] == "PARTIAL_SHARING")
        self.assertEqual(56, len(d1))
        self.assertEqual(d1, ps)

    def test_def2_set_equals_redundant_class(self):
        """DEF-2's 287 multi-label pairs are EXACTLY the REDUNDANT class (joint = max < sum
        satisfies both 'Redundant' and 'Synergistic' under the shipped Section 1.2)."""
        d2 = set((r["x"], r["y"]) for r in CENSUS["rows"] if len(r["legacy_1_2_labels"]) > 1)
        red = set((r["x"], r["y"]) for r in CENSUS["rows"] if r["corrected_class"] == "REDUNDANT")
        self.assertEqual(287, len(d2))
        self.assertEqual(d2, red)

    def test_named_example_from_the_defect_report(self):
        row = [r for r in CENSUS["rows"]
               if r["x"] == "cap-perception" and r["y"] == "cap-communication"][0]
        self.assertEqual((2, 2, 3, 4), (row["B_x"], row["B_y"], row["joint"], row["sum"]))
        self.assertEqual("redundant", row["shipped_label"])
        self.assertEqual("PARTIAL_SHARING", row["corrected_class"])
        self.assertTrue(row["shipped_contradicts_1_2"])

    def test_delta_table_totals(self):
        total = sum(d["pairs"] for d in W.delta_table(CENSUS))
        self.assertEqual(351, total)
        changed = sum(d["pairs"] for d in W.delta_table(CENSUS) if d["changed"])
        self.assertEqual(217, changed)

    def test_diagonal_is_redundant_under_burden_classification(self):
        """A capability with itself: joint = max < sum -> REDUNDANT (the shipped overlap
        predicate calls this 'synergistic'; both readings are pinned here)."""
        for cap in W.CAPABILITY_IDS:
            q = W.a4_claims(cap)
            b = W.burden(q)
            self.assertEqual("REDUNDANT", W.classify(b, b, W.joint_burden(q, q)))
            self.assertEqual("synergistic",
                             W.shipped_overlap_label(W.RESOURCE_CHANNELS[cap],
                                                     W.RESOURCE_CHANNELS[cap]))


class CIP3Correspondence(unittest.TestCase):
    """CIP-3: exact coincidence on INDEPENDENT; exact divergence elsewhere."""

    def test_independent_iff_disjoint_channels(self):
        ok, n = W.cip3_independent_coincidence(CENSUS)
        self.assertTrue(ok)
        self.assertEqual(8, n)

    def test_equal_fibre_is_entirely_redundant(self):
        self.assertEqual({"REDUNDANT": 161}, W.cip3_fibres(CENSUS)["equal"])

    def test_partial_fibre_splits(self):
        """The overlap predicate's 'partial overlap' fibre is NOT a single class:
        proper nesting -> REDUNDANT (126), non-nested -> PARTIAL_SHARING (56)."""
        fib = W.cip3_fibres(CENSUS)
        self.assertEqual({"REDUNDANT": 126}, fib["nested-proper"])
        self.assertEqual({"PARTIAL_SHARING": 56}, fib["non-nested-overlap"])
        self.assertEqual(182, 126 + 56)

    def test_nesting_is_the_needed_refinement(self):
        """class is a function of (relation) once nesting is exposed; the shipped
        predicate cannot see nesting, which is exactly where it goes wrong."""
        seen = {}
        for r in CENSUS["rows"]:
            k = seen.setdefault(r["relation"], r["corrected_class"])
            self.assertEqual(k, r["corrected_class"])


class CIP4LemmaB(unittest.TestCase):
    """CIP-4: Lemma B's `iff nested` needs strict positivity of mu."""

    def test_counting_measure_gives_the_iff(self):
        ok, ce = W.lemma_b_nested_iff(W.COUNTING_WEIGHTS)
        self.assertTrue(ok)
        self.assertIsNone(ce)

    def test_null_unit_measure_breaks_the_iff(self):
        ok, ce = W.lemma_b_nested_iff(W.NULL_UNIT_WEIGHTS)
        self.assertFalse(ok)
        self.assertIsNotNone(ce)

    def test_nested_implies_max_holds_for_any_non_negative_mu(self):
        """The `if` direction never needed strict positivity."""
        w = W.NULL_UNIT_WEIGHTS
        units = sorted(w)
        subsets = []
        for mask in range(1 << len(units)):
            subsets.append(frozenset(units[k] for k in range(len(units)) if mask >> k & 1))
        for qx in subsets:
            for qy in subsets:
                if qx <= qy or qy <= qx:
                    mx = W.mu_counting(qx, w)
                    my = W.mu_counting(qy, w)
                    self.assertEqual(max(mx, my), W.mu_counting(qx | qy, w))

    def test_explicit_counterexample_is_exact(self):
        w = W.NULL_UNIT_WEIGHTS
        qx, qy = frozenset({"u1"}), frozenset({"u3"})
        self.assertEqual(Fraction(1), W.mu_counting(qx | qy, w))
        self.assertEqual(Fraction(1), max(W.mu_counting(qx, w), W.mu_counting(qy, w)))
        self.assertFalse(qx <= qy or qy <= qx)


class Hostiles(unittest.TestCase):
    """Deliberately broken variants that MUST be detected."""

    def test_a_double_class_detected(self):
        det, detail = W.hostile_a_double_class()
        self.assertTrue(det, detail)

    def test_b_missing_interfering_detected(self):
        det, detail = W.hostile_b_missing_interfering()
        self.assertTrue(det, detail)

    def test_c_degenerate_zero_burden_detected(self):
        det, detail = W.hostile_c_degenerate_zero_burden()
        self.assertTrue(det, detail)

    def test_d_non_strictly_positive_mu_detected(self):
        det, detail = W.hostile_d_non_strictly_positive_mu()
        self.assertTrue(det, detail)

    def test_e_inadmissible_functional_detected(self):
        det, detail = W.hostile_e_inadmissible_functional()
        self.assertTrue(det, detail)

    def test_oracle_also_rejects_inadmissible(self):
        self.assertIsNone(O.oracle_class(4, 2, 3))


class ControlsAndNull(unittest.TestCase):
    """No-alarm controls and the null the true result beats."""

    def test_no_alarm_disjoint_pairs(self):
        ok, n = W.no_alarm_control_disjoint_pairs()
        self.assertTrue(ok)
        self.assertEqual(8, n)

    def test_no_alarm_chain_contract_has_zero_def1(self):
        """On a nesting-closed (chain) contract the DEF-1 detector stays SILENT.
        The checker does not cry wolf."""
        ok, n = W.no_alarm_control_chain_contract()
        self.assertTrue(ok)
        self.assertEqual(6, n)

    def test_null_random_classifiers(self):
        good, trials = W.null_random_classifiers()
        self.assertEqual(200, trials)
        self.assertEqual(0, good)

    def test_true_classifier_is_fully_justified(self):
        n = 0
        for r in CENSUS["rows"]:
            held = W.classes_holding(r["B_x"], r["B_y"], r["joint"])
            self.assertEqual([r["corrected_class"]], held)
            n += 1
        self.assertEqual(351, n)


if __name__ == "__main__":
    unittest.main()
