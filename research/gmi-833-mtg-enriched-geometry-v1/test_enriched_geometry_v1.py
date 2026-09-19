#!/usr/bin/env python3
"""Tests for gmi-833-mtg-enriched-geometry-v1.

Runs the hostiles, the no-alarm case, cross-checks route A (RESULT) against
route B (ORACLE) on every shared quantity, and writes TEST_RESULT_V1.json.
Imports the executor's functions directly; no subprocesses.
"""
from __future__ import annotations

import json
import os
import sys
import unittest
from fractions import Fraction
from typing import Dict, List, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import enriched_geometry_v1 as A  # noqa: E402
import independent_oracle_v1 as B  # noqa: E402

TEST_RECEIPT_NAME = "TEST_RESULT_V1.json"
TEST_SCHEMA = "GMI_833_MTG_ENRICHED_GEOMETRY_TEST_RESULT_V1"

SHARED_COUNT_KEYS = (
    "grid_universe_antichains",
    "empty_dominated_by_every_antichain_checks",
    "dominates_empty_only_if_empty_checks",
    "dominance_reflexive_checks",
    "dominance_pairs_evaluated",
    "dominance_related_pairs",
    "dominance_transitive_triples_checked",
    "dominance_antisymmetric_pairs_checked",
    "composition_monotone_checks",
    "join_upper_bound_checks",
    "join_least_upper_bound_checks",
    "graph_nodes",
    "graph_edges",
    "graph_ordered_pairs",
    "enrichment_triples_checked",
    "enrichment_identity_nodes_checked",
    "enrichment_triples_composite_nonempty_strictly_worse",
    "enrichment_triples_distinct_nodes_composite_equal",
    "budget_vectors",
    "basis_balls_including_empty",
    "open_sets",
    "relabelings",
    "relabel_closure_equalities",
    "relabel_topology_equalities",
    "graph_automorphisms",
    "null_draws",
    "null_closure_equalities",
    "null_topology_equalities",
    "lambdas",
    "rescale_closure_pair_checks",
    "rescale_closure_pair_equalities",
    "rescale_topology_equalities",
    "fixed_grid_lambdas_differing",
    "perturbation_patterns_registered",
    "perturbation_patterns_distinct",
    "perturbation_cells",
    "cells_stable_member",
    "cells_stable_nonmember",
    "cells_undetermined",
    "stable_cell_pattern_checks",
    "stable_cell_flips",
    "box_sandwich_checks",
    "cells_box_stable",
    "scalar_weights",
    "scalar_weight_pairs",
    "scalar_finite_lipschitz_checks",
    "scalar_infinite_pair_checks",
)
SHARED_WITNESS_KEYS = (
    "closure",
    "closure_min_path_lengths",
    "enrichment_strict_triple",
    "enrichment_equal_triple",
    "open_sets",
    "fixed_budget_grid_rescaling",
    "tightest_stable_member_cell",
    "margin_exceeding_perturbation_hostile",
    "scalar_distances",
)
SHARED_CHECK_KEYS = (
    "empty_antichain_dominated_by_every_antichain",
    "antichain_dominated_by_empty_only_if_empty",
    "dominance_reflexive",
    "dominance_transitive",
    "dominance_antisymmetric_on_universe",
    "composition_monotone_each_argument",
    "choice_is_upper_bound",
    "choice_is_least_upper_bound",
    "enrichment_lax_composition_law",
    "enrichment_identity_law",
    "relabeling_closure_transport_equal_all",
    "relabeling_topology_transport_equal_all",
    "relabeling_open_set_count_invariant",
    "graph_automorphism_group_trivial",
    "null_zero_closure_equalities",
    "null_topology_equalities_below_true_law",
    "registered_ball_family_is_basis_original",
    "rescaling_commutes_with_closure",
    "rescaled_budgets_generate_same_topology",
    "no_stable_cell_flips_under_registered_patterns",
    "pattern_membership_sandwiched_by_box_extremes",
    "frozen_stable_cells_subset_of_box_stable_cells",
    "scalar_projection_lipschitz_bound",
    "scalar_infinite_pairs_stay_infinite",
)


def cross_check(result: Dict[str, object], oracle: Dict[str, object]) -> List[Tuple[str, bool]]:
    rows: List[Tuple[str, bool]] = []
    rc, oc = result["counts"], oracle["counts"]  # type: ignore[index]
    for k in SHARED_COUNT_KEYS:
        rows.append(("counts." + k, k in rc and k in oc and rc[k] == oc[k]))  # type: ignore[index,operator]
    rw, ow = result["witnesses"], oracle["witnesses"]  # type: ignore[index]
    for k in SHARED_WITNESS_KEYS:
        rows.append(("witnesses." + k, k in rw and k in ow and rw[k] == ow[k]))  # type: ignore[index,operator]
    rk, ok = result["checks"], oracle["checks"]  # type: ignore[index]
    for k in SHARED_CHECK_KEYS:
        rows.append(("checks." + k, k in rk and k in ok and rk[k] is True and ok[k] is True))  # type: ignore[index,operator]
    rows.append(("registered.edges", result["registered"]["edges"] == oracle["witnesses"]["registered_edges"]))  # type: ignore[index]
    return rows


class EnrichedGeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = A.build_result()
        cls.oracle = B.build_oracle()
        cls.rows = cross_check(cls.result, cls.oracle)
        cls.nodes, cls.edges = A.registered_graph()
        cls.h, _ = A.floyd_warshall_closure(cls.nodes, cls.edges, A.DIM)

    # ---- algebra facts --------------------------------------------------------
    def test_empty_antichain_facts(self) -> None:
        universe = A.grid_universe(2, 2)
        self.assertEqual(len(universe), 20)
        for u in universe:
            self.assertTrue(A.dominated_by((), u))
            self.assertEqual(A.dominated_by(u, ()), u == ())

    def test_result_and_oracle_green(self) -> None:
        self.assertEqual(self.result["verdict"], "GREEN")
        self.assertEqual(self.result["status"], "GREEN")
        self.assertEqual(self.oracle["status"], "GREEN")
        self.assertTrue(all(self.result["checks"].values()))
        self.assertEqual(self.result["results"], ["ENR-1", "STAB-1", "STAB-2"])
        self.assertEqual(self.result["terminal"], A.TERMINAL)
        self.assertTrue(self.result["quantale_completeness_not_claimed"])
        self.assertEqual(self.result["claim_ceiling"], A.CLAIM_CEILING)
        self.assertEqual(self.result["forbidden_promotions"], list(A.FORBIDDEN_PROMOTIONS))

    def test_counts_are_ints(self) -> None:
        for k, v in self.result["counts"].items():
            self.assertIsInstance(v, int, k)
            self.assertNotIsInstance(v, bool, k)

    def test_closure_witnesses(self) -> None:
        self.assertEqual(
            self.h[("A", "C")],
            A.pareto((A.make_vec(("0", "5")), A.make_vec(("1", "1")), A.make_vec(("5/2", "3/4")), A.make_vec(("5", "0")))),
        )
        self.assertEqual(self.h[("A", "D")], ())
        self.assertEqual(self.h[("D", "A")], ())
        self.assertEqual(self.h[("B", "A")], A.pareto((A.make_vec(("7", "7")),)))
        self.assertEqual(self.result["counts"]["enrichment_triples_checked"], 125)
        self.assertEqual(self.result["counts"]["relabelings"], 120)
        self.assertEqual(self.result["counts"]["relabel_topology_equalities"], 120)

    # ---- hostiles ---------------------------------------------------------------
    def _hostile(self, name: str) -> None:
        hv = self.result["hostiles"][name]
        self.assertTrue(hv["applicable"], name + " not applicable")
        self.assertTrue(hv["detected"], name + " not detected")

    def test_hostile_negative_burden(self) -> None:
        self._hostile("negative_burden_rejected")
        with self.assertRaisesRegex(A.GeometryError, "NEGATIVE_BURDEN"):
            A.make_vec(("-1", "0"))

    def test_hostile_dimension_mismatch(self) -> None:
        self._hostile("dimension_mismatch_rejected")
        with self.assertRaisesRegex(A.GeometryError, "DIMENSION_MISMATCH"):
            A.compose(A.pareto((A.make_vec(("1", "2")),)), A.pareto((A.make_vec(("1", "2", "3")),)))

    def test_hostile_float_rejected(self) -> None:
        with self.assertRaisesRegex(A.GeometryError, "FLOAT"):
            A.make_vec((0.5, 1))
        with self.assertRaisesRegex(B.OracleError, "FLOAT"):
            B.qvec((0.5, 1))

    def test_hostile_coordinatewise_infimum(self) -> None:
        self._hostile("coordinatewise_infimum_fabrication_detected")
        f1 = A.pareto((A.make_vec(("1", "4")), A.make_vec(("4", "1"))))
        self.assertNotIn(A.make_vec(("1", "1")), f1)
        self.assertFalse(A.dominated_by((A.make_vec(("1", "1")),), f1))

    def test_hostile_planted_closure(self) -> None:
        self._hostile("planted_closure_entry_violating_enrichment_detected")
        planted = dict(self.h)
        planted[("A", "C")] = A.pareto((A.make_vec(("6", "6")),))
        bad, _ = A.enrichment_violations(self.nodes, planted)
        self.assertIn(("A", "B", "C"), bad)

    def test_hostile_non_bijective_relabeling(self) -> None:
        self._hostile("non_bijective_relabeling_rejected")
        with self.assertRaisesRegex(A.GeometryError, "NON_BIJECTIVE_RELABELING"):
            A.relabel_edges(self.nodes, self.edges, {"A": "A", "B": "A", "C": "C", "D": "D", "E": "E"})
        with self.assertRaisesRegex(A.GeometryError, "NON_BIJECTIVE_RELABELING"):
            A.relabel_edges(self.nodes, self.edges, {"A": "B", "B": "C", "C": "D", "D": "E", "E": "Z"})

    def test_hostile_fixed_budget_grid_rescaling(self) -> None:
        self._hostile("fixed_budget_grid_rescaling_changes_topology")
        rows = self.result["witnesses"]["fixed_budget_grid_rescaling"]
        self.assertEqual(len(rows), 3)
        self.assertTrue(any(r["differs"] for r in rows))
        # the original registered family is a basis (parent construction applies verbatim)
        self.assertTrue(self.result["checks"]["registered_ball_family_is_basis_original"])
        # subbasis generation is exercised: some fixed-grid rescaled family is not a basis
        self.assertTrue(any(not r["raw_ball_family_is_basis"] for r in rows))

    def test_hostile_margin_exceeding_perturbation(self) -> None:
        self._hostile("margin_exceeding_perturbation_flips_membership")
        w = self.result["witnesses"]["margin_exceeding_perturbation_hostile"]
        self.assertTrue(w["member_before"])
        self.assertFalse(w["member_after"])
        self.assertGreater(Fraction(w["uniform_delta"]), Fraction(w["registered_e"]))

    def test_hostile_tampered_receipt(self) -> None:
        self._hostile("tampered_receipt_edge_burden_detected")
        tampered = json.loads(A.canonical_json(self.result))
        tampered["registered"]["edges"]["E->C"] = [["3/1", "1/4"]]
        self.assertFalse(A.verify_receipt_closure(tampered))

    # ---- no-alarm case: the checkers stay silent on honest inputs ---------------
    def test_no_alarm_case(self) -> None:
        bad_triples, bad_nodes = A.enrichment_violations(self.nodes, self.h)
        self.assertEqual(bad_triples, [])
        self.assertEqual(bad_nodes, [])
        self.assertTrue(A.verify_receipt_closure(self.result))
        self.assertTrue(self.result["checks"]["untampered_receipt_closure_verifies"])
        self.assertEqual(self.result["counts"]["stable_cell_flips"], 0)
        identity_map = {n: n for n in self.nodes}
        self.assertEqual(A.relabel_edges(self.nodes, self.edges, identity_map), self.edges)
        # registered-e perturbation on the tight cell does not flip (bound respected)
        w = self.result["witnesses"]["tightest_stable_member_cell"]
        b = A.make_vec(w["budget"])
        e = A.F(A.PERTURBATION_E)
        keys = tuple(sorted(self.edges))
        hp, _ = A.floyd_warshall_closure(self.nodes, A.perturb_edges(self.edges, A.uniform_delta(keys, (e, e))), A.DIM)
        self.assertTrue(A.is_member(hp, w["source"], w["target"], b))

    def test_hostile_table_complete(self) -> None:
        hostiles = self.result["hostiles"]
        self.assertEqual(len(hostiles), 8)
        for name, hv in hostiles.items():
            self.assertTrue(hv["applicable"], name)
            self.assertTrue(hv["detected"], name)
        self.assertEqual(self.result["counts"]["hostiles_total"], 8)
        self.assertEqual(self.result["counts"]["hostiles_detected"], 8)
        self.assertEqual(self.result["counts"]["hostiles_applicable"], 8)

    # ---- route A vs route B ----------------------------------------------------
    def test_oracle_imports_nothing_from_route_a(self) -> None:
        with open(os.path.join(HERE, "independent_oracle_v1.py"), encoding="utf-8") as fh:
            src = fh.read()
        self.assertNotIn("enriched_geometry_v1", src)
        self.assertEqual(B.ORACLE_ROUTE, "SIMPLE_PATH_ENUMERATION_AND_EXPLICIT_UNION_CLOSURE")

    def test_cross_check_all_shared_quantities(self) -> None:
        failed = [name for name, ok in self.rows if not ok]
        self.assertEqual(failed, [])
        self.assertGreaterEqual(len(self.rows), 70)

    def test_oracle_simple_paths(self) -> None:
        edges = B.o_graph()
        paths = B.simple_paths(B.O_NODES, edges, "A", "C")
        self.assertEqual(sorted(len(p) for p in paths), [1, 2, 2])
        self.assertEqual(B.simple_paths(B.O_NODES, edges, "A", "D"), [])
        self.assertIn([], B.simple_paths(B.O_NODES, edges, "A", "A"))

    # ---- committed receipts replay byte-identically ------------------------------
    def test_committed_receipts_match_replay(self) -> None:
        with open(os.path.join(HERE, A.RECEIPT_NAME), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), A.receipt_text(self.result))
        with open(os.path.join(HERE, B.ORACLE_RECEIPT_NAME), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), B.oracle_text(self.oracle))

    # ---- write TEST_RESULT_V1.json (runs last by name) ----------------------------
    def test_zz_write_test_result(self) -> None:
        hostiles = self.result["hostiles"]
        detected = sum(1 for hv in hostiles.values() if hv["applicable"] and hv["detected"])
        all_rows_ok = all(ok for _, ok in self.rows)
        status = "GREEN" if (
            self.result["status"] == "GREEN" and self.oracle["status"] == "GREEN"
            and detected == len(hostiles) and all_rows_ok
        ) else "RED"
        null = self.result["null"]
        self.assertEqual(null["draws"], 200)
        self.assertEqual(null["closure_equalities"], 0)
        self.assertEqual(null["true_law_aligned_equalities"], 120)
        receipt = {
            "schema": TEST_SCHEMA,
            "hostiles_total": len(hostiles),
            "hostiles_detected": detected,
            "null_draws": null["draws"],
            "null_closure_equalities": null["closure_equalities"],
            "null_topology_equalities": null["topology_equalities"],
            "shared_quantities_compared": len(self.rows),
            "shared_quantities_equal": sum(1 for _, ok in self.rows if ok),
            "route_a": A.ROUTE,
            "route_b": B.ORACLE_ROUTE,
            "status": status,
        }
        with open(os.path.join(HERE, TEST_RECEIPT_NAME), "w", encoding="utf-8") as fh:
            fh.write(json.dumps(receipt, indent=1, sort_keys=True) + "\n")
        self.assertEqual(status, "GREEN")



class Counterexample(unittest.TestCase):
    """The frozen frontier-based non-membership criterion is refuted by a recorded counterexample on
    both routes, and the box criterion marks that cell UNDETERMINED (no-alarm for the corrected rule)."""

    def test_counterexample_agrees_across_routes(self):
        r = json.load(open(os.path.join(HERE, "RESULT_V1.json")))
        o = json.load(open(os.path.join(HERE, "ORACLE_RESULT_V1.json")))
        for key in ("frozen_nonmember_criterion_refuted_by_counterexample",
                    "box_criterion_marks_counterexample_undetermined"):
            self.assertTrue(r["checks"][key], key)
            self.assertTrue(o["checks"][key], key)
        wr = r["witnesses"]["frozen_nonmember_counterexample"]
        wo = o["witnesses"]["frozen_nonmember_counterexample"]
        for key in ("frozen_classification", "member_before", "member_after_all_edges_minus_e",
                    "box_criterion_stable"):
            self.assertEqual(wr[key], wo[key], key)
        self.assertEqual(wr["frozen_classification"], "STABLE_NONMEMBER")
        self.assertFalse(wr["member_before"])
        self.assertTrue(wr["member_after_all_edges_minus_e"])

if __name__ == "__main__":
    unittest.main(verbosity=2)
