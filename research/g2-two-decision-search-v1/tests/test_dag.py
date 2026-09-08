"""REFACTOR subtree matching and Wernhard save-value — no 1-step identity."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

import dag as D  # noqa: E402


class NodeSteps(unittest.TestCase):
    def test_getsteps_skips_floating_and_keeps_assertions(self):
        cin = D.Node("cin", [D.Node("cA", [], "$f"), D.Node("cB", [], "$f")], "$a")
        incom = D.Node("incom", [D.Node("cA", [], "$f"), D.Node("cB", [], "$f")], "$p")
        difeq = D.Node(
            "difeq1i",
            [cin, cin, D.Node("cC", [], "$f"), incom],
            "$p",
            n_floating=3,
        )
        self.assertEqual(difeq.steps(), ["cin", "cin", "incom", "difeq1i"])
        self.assertEqual(difeq.semantic_spine(), ["incom", "difeq1i"])

    def test_proper_subtree_is_not_root_identity(self):
        leaf = D.Node("incom", [], "$p")
        mid = D.Node("difeq1i", [D.Node("cA", [], "$f"), D.Node("cB", [], "$f"),
                                D.Node("cC", [], "$f"), leaf], "$p", n_floating=3)
        root = D.Node("3eqtr3i", [mid, D.Node("indif2", [], "$p")], "$p", n_floating=0)
        lemma = ["incom", "difeq1i"]
        hits = D.match_semantic_spine(root, lemma)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["proper_subtree"], True)
        self.assertEqual(hits[0]["label"], "difeq1i")

    def test_whole_proof_spine_is_rejected_as_one_step_identity(self):
        leaf = D.Node("incom", [], "$p")
        root = D.Node("difeq1i", [D.Node("cA", [], "$f"), D.Node("cB", [], "$f"),
                                 D.Node("cC", [], "$f"), leaf], "$p", n_floating=3)
        hits = D.match_semantic_spine(root, ["incom", "difeq1i"])
        self.assertEqual(len(hits), 1)
        self.assertFalse(hits[0]["proper_subtree"])


class SaveValue(unittest.TestCase):
    def test_zero_heldout_occurrences_is_no_recurrence(self):
        row = D.save_value(n_heldout_proper=0, semantic_size=2)
        self.assertEqual(row["save_value"], 0)
        self.assertEqual(row["terminal"], "NO_RECURRENCE")

    def test_single_later_use_still_zero_save_value(self):
        row = D.save_value(n_heldout_proper=1, semantic_size=2)
        self.assertEqual(row["save_value"], 0)
        self.assertEqual(row["terminal"], "SINGLE_HELD_OUT_USE")

    def test_two_later_uses_save_one_times_size_minus_one(self):
        row = D.save_value(n_heldout_proper=2, semantic_size=2)
        self.assertEqual(row["save_value"], 1)
        self.assertEqual(row["terminal"], "RECURRENCE")


class CompressedExpand(unittest.TestCase):
    def test_rpn_builds_parent_child(self):
        arities = {"cin": 2, "incom": 2, "difeq1i": 4, "cA": 0, "cB": 0, "cC": 0}
        kinds = {"cin": "$a", "incom": "$p", "difeq1i": "$p",
                 "cA": "$f", "cB": "$f", "cC": "$f"}
        rpn = ["cA", "cB", "cin", "cB", "cA", "cin", "cC", "cA", "cB", "incom", "difeq1i"]
        root = D.tree_from_rpn(rpn, arities, kinds, floating_counts={"difeq1i": 3, "incom": 2, "cin": 2})
        self.assertEqual(root.label, "difeq1i")
        self.assertEqual(root.children[3].label, "incom")
        self.assertEqual(root.semantic_spine(), ["incom", "difeq1i"])


if __name__ == "__main__":
    unittest.main()
