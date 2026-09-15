#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "finite_search_budget_v1", HERE / "finite_search_budget_v1.py"
)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


class FiniteSearchBudgetMorphologyV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = mod.build_receipt()

    def test_01_receipt_green_and_byte_reproducible(self):
        expected = json.loads((HERE / "RESULT_V1.json").read_text())
        self.assertEqual(self.r["verdict"], "GREEN")
        self.assertTrue(all(self.r["checks"].values()))
        self.assertEqual(json.loads(mod.canonical_json(self.r)), expected)
        self.assertEqual(mod.canonical_json(self.r), (HERE / "RESULT_V1.json").read_text())

    def test_02_prefix_completion_thresholds(self):
        ms=("a","b","c"); pi=("a","b","c")
        obj={"a":2,"b":1,"c":0}; costs={"a":2,"b":3,"c":1}
        self.assertEqual(mod.select_at_budget(ms,pi,obj,costs,1)["evaluated_prefix"], ())
        self.assertEqual(mod.select_at_budget(ms,pi,obj,costs,2)["evaluated_prefix"], ("a",))
        self.assertEqual(mod.select_at_budget(ms,pi,obj,costs,4)["evaluated_prefix"], ("a",))
        self.assertEqual(mod.select_at_budget(ms,pi,obj,costs,5)["evaluated_prefix"], ("a","b"))
        self.assertEqual(mod.select_at_budget(ms,pi,obj,costs,6)["evaluated_prefix"], ("a","b","c"))

    def test_03_no_evaluated_candidate_is_typed_terminal(self):
        c=mod.select_at_budget(("a",),("a",),{"a":0},{"a":2},1)
        self.assertIsNone(c["selected"])
        self.assertIsNone(c["selected_value"])
        self.assertIsNone(c["regret"])
        self.assertEqual(c["terminal"], "NO_EVALUATED_CANDIDATE")

    def test_04_earliest_seen_tie_is_stable(self):
        c=mod.select_at_budget(
            ("a","b","c"),("a","b","c"),{"a":0,"b":0,"c":1},{"a":1,"b":1,"c":1},2
        )
        self.assertEqual(c["selected"], "a")

    def test_05_global_recovery_threshold_with_tied_optima(self):
        ms=("a","b","c"); pi=("c","b","a")
        obj={"a":0,"b":0,"c":1}; costs={"a":2,"b":3,"c":1}
        self.assertEqual(mod.recovery_threshold(ms,pi,obj,costs), Fraction(4))
        self.assertFalse(mod.select_at_budget(ms,pi,obj,costs,3)["global_value_recovered"])
        self.assertTrue(mod.select_at_budget(ms,pi,obj,costs,4)["global_value_recovered"])

    def test_06_incumbent_value_and_regret_do_not_worsen(self):
        ms=("a","b","c"); pi=("a","b","c")
        obj={"a":2,"b":1,"c":0}; costs={"a":1,"b":1,"c":1}
        vals=[mod.select_at_budget(ms,pi,obj,costs,b) for b in (1,2,3)]
        self.assertEqual([v["selected_value"] for v in vals],[2,1,0])
        self.assertEqual([v["regret"] for v in vals],[2,1,0])

    def test_07_identity_changes_iff_strict_improvement_after_initial(self):
        c=mod.threshold_transition_certificate(
            ("a","b","c","d"),("a","b","c","d"),
            {"a":2,"b":2,"c":1,"d":1},{"a":1,"b":1,"c":1,"d":1}
        )
        rows=c["rows"]
        self.assertEqual([r["identity_changed"] for r in rows],[True,False,True,False])
        self.assertTrue(c["all_post_initial_changes_iff_strict_improvement"])

    def test_08_complete_enumeration_recovers_global(self):
        c=mod.schedule_certificate(
            ("a","b","c"),("c","a","b"),{"a":0,"b":2,"c":1},{"a":3,"b":2,"c":1}
        )
        self.assertTrue(c["complete_recovers_global_value"])
        self.assertEqual(c["complete_selection"], "a")
        self.assertEqual(c["complete_value"], Fraction(0))

    def test_09_alternate_orders_change_recovery_threshold(self):
        w=self.r["witnesses"]["alternate_order"]
        self.assertEqual(w["early_best"]["recovery_threshold"], Fraction(1))
        self.assertEqual(w["late_best"]["recovery_threshold"], Fraction(3))
        self.assertTrue(w["different_recovery_thresholds"])

    def test_10_alternate_orders_change_finite_budget_morphology(self):
        w=self.r["witnesses"]["alternate_order"]
        self.assertEqual(w["budget_1_early"]["selected"], "best")
        self.assertEqual(w["budget_1_late"]["selected"], "bad")
        self.assertTrue(w["different_budget_1_morphologies"])

    def test_11_exact_rational_costs_and_budget(self):
        c=mod.select_at_budget(
            ("a","b"),("a","b"),{"a":"1","b":"0"},{"a":"1/2","b":"3/2"},"1/2"
        )
        self.assertEqual(c["evaluated_prefix"],("a",))
        self.assertEqual(c["spent_completed_cost"],Fraction(1,2))
        self.assertEqual(mod.recovery_threshold(
            ("a","b"),("a","b"),{"a":"1","b":"0"},{"a":"1/2","b":"3/2"}
        ), Fraction(2))

    def test_12_exhaustive_census_exact_size_and_zero_failures(self):
        c=self.r["census"]
        self.assertEqual(c["schedule_worlds"],162009)
        self.assertEqual(c["budget_points"],1448631)
        self.assertEqual(c["failures"],[])

    def test_13_census_exercises_ties_improvements_and_empty_prefixes(self):
        c=self.r["census"]
        self.assertGreater(c["strict_improvement_events"],0)
        self.assertGreater(c["tied_nonpromotion_events"],0)
        self.assertGreater(c["no_candidate_points"],0)
        self.assertGreater(c["zero_regret_points"],0)

    def test_14_parent_boundary_keeps_stochastic_e2_outside_theorem(self):
        p=self.r["parent_boundary"]["section_e_e2"]
        self.assertTrue(p["parent_owned"])
        self.assertIn("stochastic",p["outside_child_theorem"])

    def test_15_parent_pins_exact(self):
        self.assertEqual(
            self.r["parent_pins"]["section_e_e1"]["blob"],
            "369d3bd09279c4136ffeed469d0ffb0b6b5d443b",
        )
        self.assertEqual(
            self.r["parent_pins"]["section_e_e2"]["blob"],
            "106653e98a2c0415720a10cb6c5f86a6c7243fe6",
        )
        self.assertEqual(
            self.r["parent_pins"]["global_vs_reachable"]["blob"],
            "37a0dda56649c02de1dd733b20a1266d481a3d30",
        )

    def test_16_claim_ceiling_and_forbidden_promotions(self):
        self.assertEqual(
            self.r["claim_ceiling"],
            "GMI_FINITE_SEARCH_PREFIX_MORPHOLOGY_SELECTION_DERIVED_AT_REGISTERED_SCOPE",
        )
        self.assertIn("STOCHASTIC_SEARCH_THEOREM",self.r["forbidden_promotions"])
        self.assertIn("COMPLETE_GMI",self.r["forbidden_promotions"])

    def test_17_empty_universe_rejected(self):
        with self.assertRaisesRegex(ValueError,"nonempty"):
            mod.validate_universe(())

    def test_18_duplicate_universe_rejected(self):
        with self.assertRaisesRegex(ValueError,"unique"):
            mod.validate_universe(("a","a"))

    def test_19_incomplete_order_rejected(self):
        with self.assertRaisesRegex(ValueError,"complete"):
            mod.validate_order(("a","b"),("a",))

    def test_20_duplicate_order_rejected(self):
        with self.assertRaisesRegex(ValueError,"duplicates"):
            mod.validate_order(("a","b"),("a","a"))

    def test_21_outside_order_rejected(self):
        with self.assertRaisesRegex(ValueError,"permutation"):
            mod.validate_order(("a","b"),("a","c"))

    def test_22_missing_or_extra_objective_rejected(self):
        with self.assertRaisesRegex(ValueError,"exactly every"):
            mod.validate_objective(("a","b"),{"a":0})
        with self.assertRaisesRegex(ValueError,"exactly every"):
            mod.validate_objective(("a",),{"a":0,"b":1})

    def test_23_inexact_objective_rejected(self):
        with self.assertRaisesRegex(ValueError,"floats"):
            mod.validate_objective(("a",),{"a":0.5})
        with self.assertRaisesRegex(ValueError,"booleans"):
            mod.validate_objective(("a",),{"a":True})

    def test_24_missing_or_extra_cost_rejected(self):
        with self.assertRaisesRegex(ValueError,"exactly every"):
            mod.validate_costs(("a","b"),{"a":1})
        with self.assertRaisesRegex(ValueError,"exactly every"):
            mod.validate_costs(("a",),{"a":1,"b":2})

    def test_25_nonpositive_cost_rejected(self):
        with self.assertRaisesRegex(ValueError,"strictly positive"):
            mod.validate_costs(("a",),{"a":0})
        with self.assertRaisesRegex(ValueError,"strictly positive"):
            mod.validate_costs(("a",),{"a":-1})

    def test_26_float_cost_rejected(self):
        with self.assertRaisesRegex(ValueError,"floats"):
            mod.validate_costs(("a",),{"a":1.0})

    def test_27_negative_budget_rejected(self):
        with self.assertRaisesRegex(ValueError,"nonnegative"):
            mod.validate_budget(-1)

    def test_28_inexact_budget_rejected(self):
        with self.assertRaisesRegex(ValueError,"floats"):
            mod.validate_budget(1.0)
        with self.assertRaisesRegex(ValueError,"booleans"):
            mod.validate_budget(True)

    def test_29_schedule_completion_costs_are_exact(self):
        s=mod.cumulative_schedule(
            ("a","b"),("b","a"),{"a":0,"b":1},{"a":"1/3","b":"2/3"}
        )
        self.assertEqual(s,(("b",Fraction(2,3),Fraction(2,3)),("a",Fraction(1,3),Fraction(1))))

    def test_30_global_argmin_preserves_universe_order_not_search_order(self):
        g=mod.global_argmin(("a","b","c"),{"a":0,"b":1,"c":0})
        self.assertEqual(g,("a","c"))

    def test_31_no_floats_in_receipt(self):
        def walk(x):
            if isinstance(x,float):
                self.fail("float found in exact receipt")
            if isinstance(x,dict):
                for v in x.values(): walk(v)
            elif isinstance(x,(list,tuple)):
                for v in x: walk(v)
        walk(self.r)


if __name__ == "__main__":
    unittest.main()
