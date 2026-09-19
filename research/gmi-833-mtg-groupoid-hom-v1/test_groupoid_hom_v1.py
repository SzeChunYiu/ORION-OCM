# -*- coding: utf-8 -*-
"""Tests for gmi-833-mtg-groupoid-hom-v1: hostiles (detected AND applicable), null, no-alarm,
two-route agreement.  Runs identically under -O (no bare assert).  Writes TEST_RESULT_V1.json.

    python3 -I -B test_groupoid_hom_v1.py ; python3 -I -O -B test_groupoid_hom_v1.py
"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import groupoid_hom_v1 as G  # noqa: E402

SHARED = (
    ("distinct_quotient_classes", "distinct_quotient_classes"),
    ("counts.orbit_size_max", "orbit_size_max"),
    ("witnesses.grp3.first_hit_before", "first_hit_before"),
    ("witnesses.grp3.first_hit_after", "first_hit_after"),
    ("witnesses.grp3.search_order_invariant", "search_order_invariant"),
    ("counts.hom_hom_maps_total", "hom_maps_total"),
    ("counts.hom_composition_pairs", "composition_pairs"),
    ("counts.hom_tier_min_rule_strict", "tier_min_rule_strict"),
    ("counts.hom_tier_sum_bound_coarser_than_min", "tier_sum_bound_coarser_than_min"),
    ("counts.hom_eps_bound_sound", "eps_bound_sound"),
    ("counts.hom_contract_rule_strict", "contract_rule_strict"),
    ("counts.hom_eps_subadditive", "eps_subadditive"),
    ("counts.hom_associativity_triples", "associativity_triples"),
    ("counts.hom3_pairs", "hom3_pairs"),
    ("counts.hom3_relabeling_pairs", "hom3_relabeling_pairs"),
    ("counts.hom3_maps_checked", "hom3_maps_checked"),
    ("counts.hom3_fields_preserved", "hom3_fields_preserved"),
    ("counts.hom3_bijective", "hom3_bijective"),
    ("tier_census", "tier_census"),
)


def dig(doc, path):
    cur = doc
    for seg in path.split("."):
        cur = cur[seg]
    return cur


class Hostiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fx = G.fixture()
        cls.hostiles, cls.null = G.run_hostiles_and_null(cls.fx)
        cls.hom = G.run_hom(cls.fx)

    def test_every_hostile_is_applicable_and_detected(self):
        table = dict(self.hostiles)
        table.update(self.hom["hostiles"])
        self.assertGreaterEqual(len(table), 16)
        for name, h in sorted(table.items()):
            self.assertTrue(h["applicable"], name + " is vacuous")
            self.assertTrue(h["detected"], name + " not detected")

    def test_null_zero_of_200(self):
        self.assertEqual(self.null["draws"], 200)
        self.assertEqual(self.null["accepted_as_valid"], 0)

    def test_no_alarm_valid_relabeling_is_accepted(self):
        D = self.fx["pop"][0]
        r = {"s0": "s1", "s1": "s2", "s2": "s0"}
        t = {"ADD_STATE": "ADD_EDGE", "ADD_EDGE": "ADD_STATE"}
        self.assertEqual(G.audit_relabeling(D, G.act((r, t), D), r, t), "VALID")

    def test_no_alarm_required_evidence_carried(self):
        self.assertTrue(self.hom["evidence_carried_no_alarm"])

    def test_tampered_receipt_detected_by_recomputation(self):
        path = os.path.join(HERE, "RESULT_V1.json")
        doc = json.load(open(path))
        live = G.run_grp(self.fx)
        self.assertEqual(doc["distinct_quotient_classes"], live["distinct_quotient_classes"])
        tampered = dict(doc, distinct_quotient_classes=doc["distinct_quotient_classes"] + 1)
        self.assertNotEqual(tampered["distinct_quotient_classes"], live["distinct_quotient_classes"])

    def test_declared_field_composition_laws_are_sound(self):
        c = self.hom["counts"]
        self.assertEqual(c["tier_min_rule_sound"], c["composition_pairs"])
        self.assertEqual(c["tier_sum_bound_sound"], c["composition_pairs"])
        self.assertEqual(c["eps_bound_sound"], c["composition_pairs"])
        self.assertEqual(c["contract_rule_sound"], c["composition_pairs"])
        self.assertEqual(c["eps_subadditive"], c["composition_pairs"])
        self.assertEqual(c["tier_min_rule_equal"] + c["tier_min_rule_strict"], c["composition_pairs"])
        # equality with recomputation is NOT claimed: the strict witness (a repair) is recorded
        if c["tier_min_rule_strict"]:
            self.assertIsNotNone(self.hom["tier_witness"])

    def test_first_run_fraction_defect_was_the_wrong_object(self):
        """The fraction-of-cells defect is refuted as a composable object: it is not carried along a
        collapsing state map. Re-derive one failing pair from the frozen fixture (recall of the negative)."""
        P = self.fx["presentations"]
        found = False
        names = ("M1", "M2", "M3", "M5")
        for a in names:
            for b in names:
                for c in names:
                    for T in G.hom_set(P[a], P[b]):
                        for U in G.hom_set(P[b], P[c]):
                            comp = {x: U["tau"][T["tau"][x]] for x in P[a]["X"]}
                            def frac(M, N, tau):
                                cells = [(x, aa) for x in M["X"] for aa in M["A"]]
                                bad = sum(1 for (x, aa) in cells if tau[M["delta"][(x, aa)]] != N["delta"][(tau[x], aa)])
                                return G.Fraction(bad, len(cells))
                            if frac(P[a], P[c], comp) > frac(P[a], P[b], T["tau"]) + frac(P[b], P[c], U["tau"]):
                                found = True
        self.assertTrue(found, "the fraction defect should fail subadditivity on this fixture")


class TwoRoutes(unittest.TestCase):
    def test_result_and_oracle_agree_on_every_shared_quantity(self):
        r = json.load(open(os.path.join(HERE, "RESULT_V1.json")))
        o = json.load(open(os.path.join(HERE, "ORACLE_RESULT_V1.json")))
        self.assertEqual(r["status"], "GREEN")
        self.assertEqual(o["status"], "GREEN")
        for pa, pb in SHARED:
            self.assertEqual(dig(r, pa), o[pb], pa)
        self.assertEqual(r["counts"]["conclusion_checks"], o["orbit_conclusion_checks"])
        self.assertTrue(o["orbit_conclusions_all_equal"])
        self.assertTrue(r["checks"]["grp2_conclusions_commute"])


def write_receipt(result):
    fx = G.fixture()
    hostiles, null = G.run_hostiles_and_null(fx)
    hom = G.run_hom(fx)
    table = dict(hostiles)
    table.update(hom["hostiles"])
    doc = {"schema": "GMI_833_MTG_GROUPOID_HOM_TEST_RESULT_V1",
           "hostiles_total": len(table),
           "hostiles_detected": sum(1 for h in table.values() if h["detected"]),
           "hostiles_applicable": sum(1 for h in table.values() if h["applicable"]),
           "null_draws": null["draws"], "null_accepted": null["accepted_as_valid"],
           "shared_quantities_compared": len(SHARED) + 1,
           "tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
           "status": "GREEN" if result.wasSuccessful() else "RED"}
    with open(os.path.join(HERE, "TEST_RESULT_V1.json"), "w") as fh:
        json.dump(doc, fh, indent=1, sort_keys=True)
        fh.write("\n")
    return doc


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    res = unittest.TextTestRunner(verbosity=2).run(suite)
    print(json.dumps(write_receipt(res), sort_keys=True))
    raise SystemExit(0 if res.wasSuccessful() else 1)
