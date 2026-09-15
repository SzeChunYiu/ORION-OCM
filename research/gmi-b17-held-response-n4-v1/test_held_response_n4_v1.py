import importlib.util
from fractions import Fraction as F
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("held_n4", HERE / "held_response_n4_v1.py")
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


class TargetTests(unittest.TestCase):
    def setUp(self):
        self.t = MOD.targets()

    def test_frozen_support_sizes(self):
        expected = {
            "FULL":16, "HALF":8, "EVEN":8, "DIAGONAL":2, "HAMMING2":6,
            "EQUAL01":8, "AND_GRAPH":8, "BIASED_SWAP":16, "DELTA0":1,
        }
        self.assertEqual({k: len(MOD.support(v)) for k,v in self.t.items()}, expected)

    def test_every_target_exact_and_normalized(self):
        for P in self.t.values():
            self.assertEqual(sum(P, F(0)), F(1))
            self.assertTrue(all(type(x) is F for x in P))

    def test_biased_swap_is_coordinate_permutation(self):
        base = MOD.bases()["BIASED"]
        self.assertEqual(self.t["BIASED_SWAP"], MOD.permute_coordinates(base, (3,2,1,0)))


class ARTests(unittest.TestCase):
    def setUp(self):
        self.t = MOD.targets()

    def test_all_24_orders_reconstruct_every_registered_ar_target(self):
        for name in ("FULL","EVEN","DIAGONAL","HAMMING2","HALF","AND_GRAPH"):
            for order in MOD.ORDERS:
                self.assertEqual(MOD.ar_reconstruct(self.t[name], order), self.t[name])

    def test_frozen_ar_extrema(self):
        expected = {
            "FULL": (4,4), "EVEN": (5,5), "DIAGONAL": (7,7),
            "HAMMING2": (8,8), "HALF": (4,4), "AND_GRAPH": (5,9),
        }
        for name,pair in expected.items():
            response = MOD.ar_response(self.t[name])
            self.assertEqual((response["min"], response["max"]), pair)
            self.assertEqual(len(response["orders"]), 24)

    def test_symmetric_controls_have_full_stabilizer_and_are_flat(self):
        for name in ("FULL","EVEN","DIAGONAL","HAMMING2"):
            response = MOD.ar_response(self.t[name])
            self.assertEqual(response["stabilizer"], 24)
            self.assertEqual(response["min"], response["max"])

    def test_half_is_asymmetric_but_flat(self):
        response = MOD.ar_response(self.t["HALF"])
        self.assertLess(response["stabilizer"], 24)
        self.assertEqual(response["stabilizer"], 6)
        self.assertEqual((response["min"], response["max"]), (4,4))

    def test_and_graph_min_orders_put_output_last(self):
        response = MOD.ar_response(self.t["AND_GRAPH"])
        mins = [row for row in response["orders"] if row["cost"] == response["min"]]
        self.assertEqual(len(mins), 6)
        self.assertTrue(all(row["order"][-1] == 3 for row in mins))

    def test_and_graph_has_maximum_cost_nine(self):
        response = MOD.ar_response(self.t["AND_GRAPH"])
        maxs = [row for row in response["orders"] if row["cost"] == 9]
        self.assertTrue(maxs)
        self.assertEqual(response["max"], 9)


class LatentTests(unittest.TestCase):
    def setUp(self):
        self.t = MOD.targets()

    def test_subcube_census_has_81(self):
        self.assertEqual(len(MOD.SUBCUBES), 81)
        self.assertEqual(len(set(MOD.SUBCUBES)), 81)
        self.assertTrue(all(cube for cube in MOD.SUBCUBES))

    def test_frozen_cover_numbers(self):
        expected = {"FULL":1,"HALF":1,"DIAGONAL":2,"EQUAL01":2,"EVEN":8,"HAMMING2":6}
        for name,k in expected.items():
            self.assertEqual(MOD.rectangle_cover_number(self.t[name]), k)

    def test_registered_mixture_certificates_exact(self):
        for name in ("FULL","HALF","DIAGONAL","EQUAL01","EVEN","HAMMING2"):
            cert = MOD.mixture_certificate(name)
            self.assertEqual(MOD.mixture_reconstruct(cert), self.t[name])
            self.assertEqual(len(cert), MOD.rectangle_cover_number(self.t[name]))

    def test_even_and_hamming_have_only_singleton_admissible_subcubes(self):
        for name in ("EVEN","HAMMING2"):
            S = frozenset(MOD.support(self.t[name]))
            admissible = [cube for cube in MOD.SUBCUBES if cube.issubset(S)]
            self.assertTrue(admissible)
            self.assertTrue(all(len(cube) == 1 for cube in admissible))

    def test_equal01_not_one_product_support(self):
        S = frozenset(MOD.support(self.t["EQUAL01"]))
        self.assertNotIn(S, MOD.SUBCUBES)
        self.assertEqual(MOD.rectangle_cover_number(self.t["EQUAL01"]), 2)


class FlowTests(unittest.TestCase):
    def setUp(self):
        self.t = MOD.targets()
        self.b = MOD.bases()

    def test_frozen_positive_base(self):
        expected = {
            "FULL":"U16", "HALF":"U8", "EVEN":"U8", "DIAGONAL":"U2",
            "HAMMING2":"U6", "EQUAL01":"U8", "AND_GRAPH":"U8",
            "BIASED_SWAP":"BIASED",
        }
        for target_name, base_name in expected.items():
            mapping = MOD.matching_bijection(self.b[base_name], self.t[target_name])
            self.assertIsNotNone(mapping)
            self.assertEqual(MOD.push_by_mapping(self.b[base_name], mapping), self.t[target_name])
            self.assertTrue(MOD.multiset_reachable(self.b[base_name], self.t[target_name]))

    def test_uniform_support_size_matrix(self):
        uniform_bases = {"U16":16,"U8":8,"U6":6,"U2":2}
        uniform_targets = {
            "FULL":16,"HALF":8,"EVEN":8,"DIAGONAL":2,
            "HAMMING2":6,"EQUAL01":8,"AND_GRAPH":8,
        }
        for tn,tsize in uniform_targets.items():
            for bn,bsize in uniform_bases.items():
                expected = tsize == bsize
                self.assertEqual(MOD.multiset_reachable(self.b[bn], self.t[tn]), expected)
                self.assertEqual(MOD.matching_bijection(self.b[bn], self.t[tn]) is not None, expected)

    def test_biased_swap_reachable_but_uniform_full_not_from_biased(self):
        self.assertIsNotNone(MOD.matching_bijection(self.b["BIASED"], self.t["BIASED_SWAP"]))
        self.assertIsNone(MOD.matching_bijection(self.b["BIASED"], self.t["FULL"]))

    def test_matching_and_multiset_predicate_agree_all_registered_cells(self):
        for P in self.t.values():
            for Q in self.b.values():
                self.assertEqual(MOD.matching_bijection(Q,P) is not None, MOD.multiset_reachable(Q,P))


class LocalRefinementTests(unittest.TestCase):
    def setUp(self):
        self.t = MOD.targets()

    def test_positive_min_steps(self):
        expected = {"DELTA0":0, "FULL":4, "HALF":3}
        for name,k in expected.items():
            status = MOD.local_refinement_status(self.t[name])
            self.assertTrue(status["reachable"])
            self.assertEqual(status["min_steps"], k)
            self.assertEqual(MOD.reconstruct_local(status), self.t[name])

    def test_correlated_targets_are_nonproduct(self):
        for name in ("EVEN","DIAGONAL","HAMMING2","EQUAL01","AND_GRAPH"):
            P = self.t[name]
            self.assertNotEqual(MOD.product_of_marginals(P), P)
            status = MOD.local_refinement_status(P)
            self.assertFalse(status["reachable"])
            self.assertEqual(status["reason"], "NONPRODUCT")

    def test_biased_swap_is_product_but_outside_grid(self):
        P = self.t["BIASED_SWAP"]
        self.assertEqual(MOD.product_of_marginals(P), P)
        status = MOD.local_refinement_status(P)
        self.assertFalse(status["reachable"])
        self.assertEqual(status["reason"], "OUTSIDE_REFRESH_GRID")
        self.assertEqual(status["marginals"], ["1/5","1/4","1/3","1/2"])

    def test_refresh_is_independent_and_last_refresh_wins(self):
        P = self.t["DELTA0"]
        P = MOD.apply_refresh(P, 0, F(1,2))
        P = MOD.apply_refresh(P, 0, F(1))
        self.assertEqual(MOD.marginals(P)[0], F(1))
        self.assertEqual(MOD.product_of_marginals(P), P)

    def test_outside_grid_refresh_rejected(self):
        with self.assertRaises(ValueError):
            MOD.apply_refresh(self.t["DELTA0"], 0, F(1,3))


class HostileAndReceiptTests(unittest.TestCase):
    def test_distribution_rejects_float(self):
        bad = tuple([F(1,16)]*15 + [1/16])
        with self.assertRaises(ValueError):
            MOD._distribution(bad)

    def test_invalid_coordinate_permutation_rejected(self):
        with self.assertRaises(ValueError):
            MOD.permute_coordinates(MOD.targets()["FULL"], (0,0,1,2))

    def test_old_false_converse_guard_is_live(self):
        receipt = MOD.build_receipt()
        guard = receipt["old_false_converse_guard"]
        self.assertLess(guard["HALF_coordinate_stabilizer"], 24)
        self.assertTrue(guard["HALF_ar_flat"])
        self.assertFalse(guard["asymmetry_implies_sensitivity"])

    def test_claim_guards_and_freeze_flag(self):
        g = MOD.build_receipt()["claim_guards"]
        self.assertTrue(g["prediction_frozen_before_outcome"])
        self.assertFalse(g["continuous_flow_claimed"])
        self.assertFalse(g["general_diffusion_claimed"])

    def test_receipt_has_no_float(self):
        def walk(x):
            if isinstance(x, dict):
                for k,v in x.items():
                    walk(k); walk(v)
            elif isinstance(x, (list, tuple)):
                for v in x: walk(v)
            else:
                self.assertNotIsInstance(x, float)
        walk(MOD.build_receipt())

    def test_receipt_deterministic_and_frozen_cells(self):
        a = MOD.build_receipt()
        b = MOD.build_receipt()
        self.assertEqual(a,b)
        self.assertEqual((a["ar"]["AND_GRAPH"]["min"],a["ar"]["AND_GRAPH"]["max"]), (5,9))
        self.assertEqual(a["latent"]["EVEN"]["components"], 8)
        self.assertEqual(a["latent"]["HAMMING2"]["components"], 6)
        self.assertTrue(a["flow"]["BIASED_SWAP"]["BIASED"]["certificate_verified"])
        self.assertEqual(a["local_refinement"]["FULL"]["min_steps"], 4)
        self.assertEqual(a["local_refinement"]["HALF"]["min_steps"], 3)


if __name__ == "__main__":
    unittest.main()
