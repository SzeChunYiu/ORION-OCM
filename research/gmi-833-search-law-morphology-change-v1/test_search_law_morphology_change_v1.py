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
    "search_law_morphology_change_v1", HERE / "search_law_morphology_change_v1.py"
)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


class SearchLawMorphologyChangeV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = mod.build_receipt()

    def test_01_receipt_green_and_byte_reproducible(self):
        expected = json.loads((HERE / "RESULT_V1.json").read_text())
        self.assertEqual(self.r["verdict"], "GREEN")
        self.assertTrue(all(self.r["checks"].values()))
        self.assertEqual(json.loads(mod.canonical_json(self.r)), expected)
        self.assertEqual(mod.canonical_json(self.r), (HERE / "RESULT_V1.json").read_text())

    def test_02_value_disagreement(self):
        w=self.r["witnesses"]["value_disagreement"]
        self.assertTrue(w["identity_disagreement"])
        self.assertTrue(w["value_disagreement"])
        self.assertEqual(w["classification"],"DISAGREEMENT_VALUE")

    def test_03_equal_value_identity_disagreement(self):
        w=self.r["witnesses"]["equal_value_identity_disagreement"]
        self.assertTrue(w["identity_disagreement"])
        self.assertFalse(w["value_disagreement"])
        self.assertEqual(w["classification"],"DISAGREEMENT_EQUAL_VALUE_IDENTITY")
        self.assertEqual(w["law1"]["regret"], Fraction(0))
        self.assertEqual(w["law2"]["regret"], Fraction(0))

    def test_04_changed_law_need_not_change_morphology(self):
        rows=self.r["witnesses"]["changed_law_no_morphology_change"]
        self.assertTrue(all(not x["identity_disagreement"] for x in rows))
        self.assertEqual([x["law1"]["selected"] for x in rows],[None,"best","best","best"])
        self.assertEqual([x["law2"]["selected"] for x in rows],[None,"best","best","best"])

    def test_05_unique_global_eventual_agreement(self):
        w=self.r["witnesses"]["unique_global_eventual_agreement"]
        self.assertTrue(w["unique_global_optimum"])
        self.assertEqual(w["joint_recovery_threshold"],Fraction(3))
        self.assertTrue(w["unique_optimum_eventual_identity_agreement"])
        self.assertEqual(w["at_joint_threshold"]["law1"]["selected"],"best")
        self.assertEqual(w["at_joint_threshold"]["law2"]["selected"],"best")

    def test_06_tied_global_identity_persists_after_complete_search(self):
        w=self.r["witnesses"]["tied_global_complete_identity_persistence"]
        self.assertFalse(w["unique_global_optimum"])
        c=w["at_joint_threshold"]
        self.assertTrue(c["identity_disagreement"])
        self.assertEqual(c["classification"],"DISAGREEMENT_EQUAL_VALUE_IDENTITY")
        self.assertEqual(c["law1"]["regret"],Fraction(0))
        self.assertEqual(c["law2"]["regret"],Fraction(0))

    def test_07_availability_disagreement_is_typed(self):
        w=self.r["witnesses"]["availability_disagreement"]
        self.assertEqual(w["classification"],"DISAGREEMENT_AVAILABILITY")
        self.assertEqual(w["law1"]["selected"],"a")
        self.assertIsNone(w["law2"]["selected"])

    def test_08_rational_threshold_cells_are_constant(self):
        c=self.r["witnesses"]["rational_threshold_cells"]
        self.assertTrue(c["all_cells_constant"])
        self.assertEqual([row["start"] for row in c["cells"]],[Fraction(0),Fraction(1,2),Fraction(3,2),Fraction(2),Fraction(3),Fraction(4)])
        self.assertTrue(all(row["constant"] for row in c["cells"]))

    def test_09_threshold_union_contains_both_laws(self):
        ms=("a","b","c")
        c1={"a":"1/2","b":"3/2","c":"1"}
        c2={"a":"1/2","b":"3/2","c":"2"}
        cells=mod.combined_threshold_cells(ms,("a","b","c"),c1,("b","a","c"),c2)
        self.assertEqual(cells,(
            (Fraction(0),Fraction(1,2)),
            (Fraction(1,2),Fraction(3,2)),
            (Fraction(3,2),Fraction(2)),
            (Fraction(2),Fraction(3)),
            (Fraction(3),Fraction(4)),
            (Fraction(4),None),
        ))

    def test_10_injective_objective_disagreement_is_value_disagreement(self):
        ms=("a","b","c")
        obj={"a":0,"b":1,"c":2}; unit={m:1 for m in ms}
        r=mod.compare_at_budget(ms,obj,("a","b","c"),unit,("c","b","a"),unit,1)
        self.assertEqual(r["classification"],"DISAGREEMENT_VALUE")

    def test_11_same_identity_same_value_agreement(self):
        ms=("a","b"); obj={"a":0,"b":1}; unit={m:1 for m in ms}
        r=mod.compare_at_budget(ms,obj,("a","b"),unit,("a","b"),unit,1)
        self.assertEqual(r["classification"],"AGREEMENT_IDENTITY")
        self.assertFalse(r["identity_disagreement"])

    def test_12_both_empty_agreement(self):
        r=mod.compare_at_budget(("a",),{"a":0},("a",),{"a":2},("a",),{"a":3},1)
        self.assertEqual(r["classification"],"AGREEMENT_NO_EVALUATED_CANDIDATE")
        self.assertFalse(r["identity_disagreement"])

    def test_13_recovery_threshold_exact_rational(self):
        ms=("a","b"); obj={"a":1,"b":0}
        self.assertEqual(mod.recovery_threshold(ms,obj,("a","b"),{"a":"1/3","b":"2/3"}),Fraction(1))

    def test_14_exhaustive_census_exact_size(self):
        c=self.r["census"]
        self.assertEqual(c["schedule_pairs"],47667)
        self.assertEqual(c["budget_points"],237282)
        self.assertEqual(c["failures"],[])

    def test_15_census_nonvacuity_counts(self):
        c=self.r["census"]
        self.assertEqual(c["value_disagreement_points"],47724)
        self.assertEqual(c["equal_value_identity_disagreement_points"],56130)
        self.assertEqual(c["changed_law_all_budget_agreement_worlds"],5220)
        self.assertEqual(c["tied_complete_identity_disagreement_worlds"],14784)
        self.assertGreater(c["unique_eventual_agreement_checks"],0)
        self.assertGreater(c["injective_disagreement_checks"],0)

    def test_16_parent_pins_exact(self):
        self.assertEqual(self.r["parent_pins"]["finite_search_budget"]["blob"],"4ea315e651475cc8afcc39860a0d2ac621e9f571")
        self.assertEqual(self.r["parent_pins"]["section_e_e1"]["blob"],"369d3bd09279c4136ffeed469d0ffb0b6b5d443b")
        self.assertEqual(self.r["parent_pins"]["section_e_e2"]["blob"],"106653e98a2c0415720a10cb6c5f86a6c7243fe6")

    def test_17_parent_boundary_keeps_stochastic_outside(self):
        p=self.r["parent_boundary"]["section_e_712_724"]
        self.assertTrue(p["parent_owned"])
        self.assertIn("stochastic",p["outside_child_theorem"])

    def test_18_claim_ceiling_and_forbidden_promotions(self):
        self.assertEqual(self.r["claim_ceiling"],"GMI_FINITE_DETERMINISTIC_SEARCH_LAW_MORPHOLOGY_DISAGREEMENT_DERIVED_AT_REGISTERED_SCOPE")
        self.assertIn("ANY_SEARCH_LAW_CHANGE_ALTERS_MORPHOLOGY",self.r["forbidden_promotions"])
        self.assertIn("SEARCH_LAW_INVARIANT_IDENTITY_UNDER_GLOBAL_TIES",self.r["forbidden_promotions"])
        self.assertIn("COMPLETE_GMI",self.r["forbidden_promotions"])

    def test_19_empty_universe_rejected(self):
        with self.assertRaisesRegex(ValueError,"nonempty"):
            mod.validate_universe(())

    def test_20_duplicate_universe_rejected(self):
        with self.assertRaisesRegex(ValueError,"unique"):
            mod.validate_universe(("a","a"))

    def test_21_incomplete_duplicate_outside_orders_rejected(self):
        with self.assertRaisesRegex(ValueError,"complete"):
            mod.validate_order(("a","b"),("a",))
        with self.assertRaisesRegex(ValueError,"duplicates"):
            mod.validate_order(("a","b"),("a","a"))
        with self.assertRaisesRegex(ValueError,"permutation"):
            mod.validate_order(("a","b"),("a","c"))

    def test_22_missing_extra_inexact_objectives_rejected(self):
        with self.assertRaisesRegex(ValueError,"exactly every"):
            mod.validate_objective(("a","b"),{"a":0})
        with self.assertRaisesRegex(ValueError,"exactly every"):
            mod.validate_objective(("a",),{"a":0,"b":1})
        with self.assertRaisesRegex(ValueError,"floats"):
            mod.validate_objective(("a",),{"a":0.5})
        with self.assertRaisesRegex(ValueError,"booleans"):
            mod.validate_objective(("a",),{"a":True})

    def test_23_bad_costs_rejected(self):
        with self.assertRaisesRegex(ValueError,"exactly every"):
            mod.validate_costs(("a","b"),{"a":1})
        with self.assertRaisesRegex(ValueError,"strictly positive"):
            mod.validate_costs(("a",),{"a":0})
        with self.assertRaisesRegex(ValueError,"strictly positive"):
            mod.validate_costs(("a",),{"a":-1})
        with self.assertRaisesRegex(ValueError,"floats"):
            mod.validate_costs(("a",),{"a":1.0})

    def test_24_bad_budget_rejected(self):
        with self.assertRaisesRegex(ValueError,"nonnegative"):
            mod.validate_budget(-1)
        with self.assertRaisesRegex(ValueError,"floats"):
            mod.validate_budget(1.0)
        with self.assertRaisesRegex(ValueError,"booleans"):
            mod.validate_budget(True)

    def test_25_mismatched_world_universe_rejected(self):
        w1={"morphologies":("a","b"),"objective":{"a":0,"b":1},"order":("a","b"),"costs":{"a":1,"b":1}}
        w2={"morphologies":("a","c"),"objective":{"a":0,"c":1},"order":("a","c"),"costs":{"a":1,"c":1}}
        with self.assertRaisesRegex(ValueError,"same morphology universe"):
            mod.compare_registered_worlds(w1,w2,1)

    def test_26_mismatched_world_objective_rejected(self):
        w1={"morphologies":("a","b"),"objective":{"a":0,"b":1},"order":("a","b"),"costs":{"a":1,"b":1}}
        w2={"morphologies":("a","b"),"objective":{"a":1,"b":0},"order":("a","b"),"costs":{"a":1,"b":1}}
        with self.assertRaisesRegex(ValueError,"identical objective semantics"):
            mod.compare_registered_worlds(w1,w2,1)

    def test_27_exact_fraction_strings_supported(self):
        self.assertEqual(mod.validate_budget("7/3"),Fraction(7,3))
        self.assertEqual(mod.validate_costs(("a",),{"a":"2/5"})["a"],Fraction(2,5))

    def test_28_completion_thresholds_strictly_increase(self):
        t=mod.completion_thresholds(("a","b","c"),("b","a","c"),{"a":"1/2","b":"3/2","c":"2"})
        self.assertEqual(t,(Fraction(3,2),Fraction(2),Fraction(4)))
        self.assertTrue(all(a<b for a,b in zip(t,t[1:])))

    def test_29_decomposition_is_total_for_valid_world(self):
        ms=("a","b","c"); obj={"a":0,"b":0,"c":2}
        c1={"a":1,"b":1,"c":1}; c2={"a":2,"b":1,"c":1}
        for b in (0,1,2,3,4):
            self.assertTrue(mod.compare_at_budget(ms,obj,("a","b","c"),c1,("b","c","a"),c2,b)["decomposition_ok"])

    def test_30_no_floats_in_receipt(self):
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
