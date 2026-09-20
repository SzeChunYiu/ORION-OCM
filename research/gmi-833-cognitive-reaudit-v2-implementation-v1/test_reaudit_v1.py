#!/usr/bin/env python3
"""Tests for the #833 Section-M hierarchy/planning/causal re-audit.

Runnable with no third-party dependency:

    python3 -I -B  research/gmi-833-cognitive-reaudit-v2-implementation-v1/test_reaudit_v1.py -v
    python3 -I -O -B research/gmi-833-cognitive-reaudit-v2-implementation-v1/test_reaudit_v1.py -v

`-I` removes the script directory from ``sys.path``, so the path is restored
explicitly below, exactly as the executor does.
"""

from __future__ import annotations

import ast
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import parents_v1 as parents          # noqa: E402
import stopping_bellman_v1 as bellman  # noqa: E402

RESULT_PATH = HERE / "RESULT_V1.json"
FREEZE_SHA256 = "5f457a7f2fa6af1fce554e29e90df4ee3afd58c1cd6656418fcdfbde76bd3e2c"
LEDGER_KEYS = {"hierarchy": "b54aa4a07f07", "planning": "cae1b23a7b71", "causal": "363a75a09b44"}
SECTION = "# M. Cognitive-function derivation upgrade"
ROWS = {
    "hierarchy": "Re-audit hierarchical skills/chunking.",
    "planning": "Re-audit planning and stopping.",
    "causal": "Re-audit causal cognition/intervention/counterfactuals.",
}


def ledger_key(row: str) -> str:
    return hashlib.sha256((SECTION + "\x00" + row).encode("utf-8")).hexdigest()[:12]


class TestExactnessDiscipline(unittest.TestCase):
    def test_no_float_literals_in_any_package_source(self):
        for name in ("stopping_bellman_v1.py", "parents_v1.py",
                     "executor_v1.py", "replay_v1.py",
                     "test_reaudit_v1.py"):
            tree = ast.parse((HERE / name).read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, float):
                    self.fail("float literal %r in %s line %d"
                              % (node.value, name, node.lineno))

    def test_exact_guard_rejects_floats_and_bools(self):
        self.assertEqual(bellman.exact(3), F(3))
        self.assertEqual(bellman.exact(F(1, 3)), F(1, 3))
        with self.assertRaises(ValueError):
            bellman.exact(float(1))
        with self.assertRaises(ValueError):
            bellman.exact(True)


class TestLedgerKeys(unittest.TestCase):
    def test_ledger_keys_match_the_evidence_ledger(self):
        for name, row in ROWS.items():
            self.assertEqual(ledger_key(row), LEDGER_KEYS[name],
                             "ledger key mismatch for %s" % name)


class TestPlanningTheorem(unittest.TestCase):
    def test_bellman_equation_exact_on_xor_graph(self):
        g = bellman.xor_graph(F(1, 8))
        self.assertEqual(g.best("root"), F(1, 2))
        self.assertEqual(g.value("root"), F(3, 4))
        self.assertEqual(g.cont("root", "t1"), F(3, 4))
        self.assertEqual(g.value("f1=0"), F(7, 8))
        self.assertEqual(g.value("00"), F(1))

    def test_stop_optimality_criterion(self):
        g = bellman.xor_graph(F(1, 8))
        self.assertFalse(g.stop_is_optimal("root"))
        g_clean = bellman.xor_graph(F(1))
        self.assertTrue(g_clean.stop_is_optimal("root"))


class TestPlanningHostiles(unittest.TestCase):
    def test_hostile_fires_exact_numbers(self):
        h = bellman.hostile_report(F(1, 8))
        self.assertEqual(h["k"], "1/8")
        self.assertEqual(h["myopic_evc_t1"], "-1/8")
        self.assertTrue(h["myopic_stops"])
        self.assertEqual(h["bellman_continuation_t1"], "3/4")
        self.assertTrue(h["bellman_continues"])
        self.assertFalse(h["stop_is_optimal"])
        self.assertEqual(h["optimal_value_vstar_root"], "3/4")
        self.assertEqual(h["two_step_plan_net_value"], "1/4")

    def test_clean_variant_no_alarm(self):
        c = bellman.hostile_report(F(1))
        self.assertTrue(c["stop_is_optimal"])
        self.assertEqual(c["optimal_value_vstar_root"], "1/2")
        self.assertEqual(c["best_root"], "1/2")

    def test_policy_search_matches_bellman(self):
        for k in (F(1, 8), F(1), F(1, 4)):
            g = bellman.xor_graph(k)
            self.assertEqual(bellman.optimal_value_by_policy_search(g, "root"),
                             g.value("root"))

    def test_tie_control_keeps_sets(self):
        t = bellman.tie_control()
        self.assertEqual(set(t["optimal_choice_set"]), {"stop", "t1", "t2"})
        self.assertEqual(len(t["optimal_choice_set"]), 3)
        self.assertEqual(set(t["best_terminal_action_set"]), {"a0", "a1"})
        self.assertEqual(len(t["best_terminal_action_set"]), 2)

    def test_refusals(self):
        r = bellman.refusal_controls()
        self.assertTrue(r["missing_goal_model_refused"])
        self.assertTrue(r["cyclic_unbounded_graph_refused"])

    def test_myopic_scope_13_of_35(self):
        m = bellman.planning_myopic_legacy_report()
        self.assertEqual(m["myopic_greedy_optimality_13_of_35"], [13, 35])
        self.assertEqual(m["disagree_witness"], ["t1"])


class TestHierarchyHostiles(unittest.TestCase):
    def test_lifecycle_and_charges(self):
        e = parents.exercise_hierarchy()
        self.assertEqual(e["lifecycle"], [3060, 3032, 1233])
        self.assertGreater(e["second_gain"], e["first_gain"])

    def test_greedy_longest_match_fails(self):
        e = parents.exercise_hierarchy()
        self.assertEqual(e["greedy_exact_cost"], 2)
        self.assertEqual(e["source_greedy_cost"], 3)

    def test_hierarchy_loses_workload(self):
        e = parents.exercise_hierarchy()
        self.assertEqual(e["h_freezer_2_hierarchy_loses"]["solver_cost"], 2)
        self.assertEqual(e["h_freezer_2_hierarchy_loses"]["retained_invocation_price"], 9)


class TestCausalHostiles(unittest.TestCase):
    def test_observation_equivalent_different_targets(self):
        e = parents.exercise_causal()
        self.assertTrue(e["c_freezer_1"]["six_original_all_nine_joint_laws_equal"])
        self.assertNotEqual(e["c_freezer_1"]["six_original_left_pn"],
                            e["c_freezer_1"]["six_original_right_pn"])
        self.assertTrue(e["c_freezer_1"]["three_treatment_supported"])

    def test_incompatible_refused_and_identified_control(self):
        e = parents.exercise_causal()
        self.assertTrue(e["c_freezer_2"]["empty_compatible_class_refused"])
        self.assertEqual(e["c_freezer_2"]["disjoint_class_status"], "INCOMPATIBLE")
        self.assertEqual(e["c_freezer_3"]["uniform_n1_status"], "IDENTIFIED")
        self.assertEqual((e["c_freezer_3"]["lower"], e["c_freezer_3"]["upper"]), ("1", "1"))

    def test_faithfulness_does_not_orient(self):
        e = parents.exercise_causal()
        self.assertTrue(e["c_freezer_4"]["same_full_support_observed"])
        self.assertTrue(e["c_freezer_4"]["dependent"])
        self.assertEqual(e["c_freezer_4"]["forward_do1"], "3/4")
        self.assertEqual(e["c_freezer_4"]["reverse_do1"], "1/2")

    def test_undefined_conditioning_distinct_refusal(self):
        e = parents.exercise_causal()
        self.assertTrue(e["c_freezer_5"]["undefined_conditioning_refused"])


class TestParentCustody(unittest.TestCase):
    def test_frozen_parent_pins_all_match(self):
        audit = parents.audit_parent_pins()
        self.assertTrue(audit["all_pinned"])
        self.assertEqual(len(audit["rows"]), 8)

    def test_legacy_replays_byte_exact(self):
        replays = parents.legacy_replays()
        for name in ("hierarchy", "causal"):
            self.assertTrue(replays[name]["isolated_replay_byte_exact"], name)
            self.assertTrue(replays[name]["receipt_sha256_ok"], name)

    def test_foundation_and_axiom_exercised(self):
        e = parents.exercise_parents()
        self.assertTrue(e["foundation"]["regenerated_matches_committed"])
        self.assertTrue(e["foundation"]["contains_COMPLETE_GMI"])
        self.assertTrue(e["axiom_core"]["regenerated_matches_committed"])
        self.assertTrue(e["axiom_core"]["base_model_satisfies_all_axioms"])
        self.assertTrue(e["axiom_core"]["dependency_graph_acyclic"])

    def test_freeze_copy_is_verbatim(self):
        data = (HERE / "FREEZE_V1.md").read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), FREEZE_SHA256)


class TestReconciliationSpecs(unittest.TestCase):
    def test_specs_structure_and_owned_rows(self):
        owned = set(ROWS.values())
        for name, row in ROWS.items():
            spec = json.loads((HERE / ("ISSUE_833_RECONCILIATION_%s_V2.json" % name.upper())).read_text())
            self.assertEqual(spec["schema"], "GMI_ISSUE_RECONCILIATION_V2")
            self.assertEqual(spec["issue"], 833)
            self.assertEqual(spec["section"], "M")
            self.assertEqual(len(spec["replacements"]), 1)
            entry = spec["replacements"][0]
            self.assertEqual(entry["anchor"], SECTION)
            self.assertEqual(entry["old"], "- [ ] " + row)
            self.assertTrue(entry["new"].startswith("- [x] " + row + " — ✅ "))
            self.assertIn(" L:" + LEDGER_KEYS[name], entry["new"])
            self.assertIn(row, entry["new"])


class TestResultVerdict(unittest.TestCase):
    def test_committed_result_is_green(self):
        result = json.loads(RESULT_PATH.read_text())
        self.assertEqual(result["verdict"], "GREEN")
        self.assertTrue(all(result["checks"].values()))
        self.assertEqual(result["claim_ceiling"],
                         "GMI_833_HIERARCHY_PLANNING_CAUSAL_REAUDIT_AT_REGISTERED_EXACT_SCOPE")


if __name__ == "__main__":
    unittest.main()
