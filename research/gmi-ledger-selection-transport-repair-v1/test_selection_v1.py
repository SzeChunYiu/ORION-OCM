"""Load-bearing applicability, adequacy and independent path controls."""
import sys
import unittest
from fractions import Fraction as F
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import selection_v1 as S
import checks_v1 as C
import oracles_v1 as O

class SelectionTests(unittest.TestCase):
    def test_zero_normalizer_and_supported_boundary(self):
        self.assertEqual(S.posterior((F(1,2),F(1,2)),(0,0))["status"],"UNDEFINED_ZERO_NORMALIZER")
        self.assertEqual(S.posterior((F(1,2),F(1,2)),(0,2))["posterior"],(0,1))
        self.assertEqual(S.posterior((0,1),(2,0))["status"],"UNDEFINED_ZERO_NORMALIZER")

    def test_positive_entropy_bayes_identity(self):
        for a in (1,2,3):
            p=(F(a,4),1-F(a,4))
            for likelihood in ((1,2),(3,1),(1,1)):
                self.assertEqual(S.posterior(p,likelihood)["posterior"],
                                 S.entropy_update_from_factors(p,likelihood))

    def test_projection_rule_requires_nonempty_set_and_positive_eta(self):
        self.assertEqual(S.euclidean_box_step(1,2,F(1,2),0,2),0)
        self.assertEqual(S.euclidean_box_step(1,-3,1,0,2),2)
        for args in ((1,1,0,0,2),(1,1,-1,0,2),(1,1,1,3,2)):
            with self.assertRaises(ValueError):S.euclidean_box_step(*args)

    def test_malformed_or_negative_probability_refused(self):
        for p,l in (((1,1),(1,2)),((F(-1),2),(1,2)),((1,),(1,2)),((True,),(1,))):
            with self.assertRaises(ValueError):S.posterior(p,l)
        with self.assertRaises(ValueError):S.entropy_update_from_factors((1,0),(1,1))

    def test_same_task_adequacy_before_price(self):
        got=C.witnesses()["common_task_selection"]
        self.assertEqual(got["winners"],("exact",))
        self.assertEqual(got["shared_charge"],5)
        self.assertEqual(got["total"],7)

    def test_table_contract_rejects_unchecked_domains_and_missing_costs(self):
        with self.assertRaises(ValueError):S.select_tables({0:{1}},{'a':{}},{'a':0})
        with self.assertRaises(ValueError):S.select_tables({0:{1}},{'a':{0:1}},{})
        with self.assertRaises(ValueError):S.select_tables({0:set()},{'a':{0:1}},{'a':0})

    def test_empty_adequate_menu_charges_all_failed_checks(self):
        got=S.select_tables({0:{1},1:{1}},{'bad':{0:0,1:0}},{'bad':0},
                            setup=2,check_fee=3,visit_fee=7)
        self.assertEqual(got["status"],"NO_ADEQUATE_REGISTERED_TABLE")
        self.assertEqual((got["checks"],got["shared_charge"],got["cost_visits"]),(2,8,0))

    def test_ties_retained_and_outside_setup_comparator(self):
        got=S.select_tables({0:{1}},{'a':{0:1},'b':{0:1}},{'a':1,'b':1},setup=10)
        self.assertEqual(got["winners"],("a","b"))
        self.assertGreater(got["total"],2)  # outside adequate method avoids shared setup

    def test_local_trap_and_charged_escape(self):
        got=C.witnesses()
        self.assertEqual(got["ordinal_trap"]["bad_minima"],(0,))
        self.assertEqual(got["escape_edge_revival"]["bad_minima"],())
        self.assertGreater(got["escape_edge_revival"]["edge_comparisons"],
                           got["ordinal_trap"]["edge_comparisons"])

    def test_plateau_and_invalid_graph(self):
        self.assertEqual(S.certify_descent((1,1),((1,),(0,)),{1})["bad_minima"],(0,))
        with self.assertRaises(ValueError):S.certify_descent((1,),((1,),),{0})
        with self.assertRaises(ValueError):S.certify_descent((1,),((0,0),),{0})

    def test_restricted_start_does_not_need_unreachable_minimum(self):
        paths=O.terminal_paths((0,0),((),()),1)
        self.assertTrue(all(p[-1]==1 for p in paths))
        self.assertEqual(S.certify_descent((0,0),((),()),{1})["bad_minima"],(0,))

    def test_independent_table_census(self):
        self.assertEqual(C.table_census()["complete_table_cost_cases"],144)

    def test_independent_all_path_census(self):
        self.assertEqual(C.descent_census()["graph_objective_adequacy_cases"],13824)

if __name__=="__main__":unittest.main()
