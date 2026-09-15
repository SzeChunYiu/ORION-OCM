#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("axiom_core_v1", HERE / "axiom_core_v1.py")
mod = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


class FiniteAxiomCoreV1Tests(unittest.TestCase):
    def test_parent_result_pins(self):
        audit = mod.audit_parents()
        self.assertTrue(audit["all_ok"])
        self.assertEqual(len(audit["rows"]), 4)
        self.assertTrue(all(r["blob_ok"] and r["claim_ceiling_ok"] for r in audit["rows"]))

    def test_parent_mutation_fails_closed(self):
        root = mod.repo_root()
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            for path, _, _ in mod.PARENT_PINS:
                src = root / path
                dst = tmp / path
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)
            victim = tmp / mod.PARENT_PINS[0][0]
            victim.write_bytes(victim.read_bytes() + b"\n")
            audit = mod.audit_parents(tmp)
            self.assertFalse(audit["all_ok"])
            self.assertFalse(audit["rows"][0]["blob_ok"])

    def test_explicit_finite_model_satisfies_all_six_axioms(self):
        out = mod.validate_model(mod.base_model())
        self.assertTrue(out["satisfies"])
        self.assertEqual(out["violated_axioms"], ())

    def test_protected_response_equivalence_is_derived(self):
        model = mod.base_model()
        quotient = mod.protected_response_quotient(model)
        relation = mod.quotient_relation(model)
        self.assertEqual(quotient, (("s0", "s1"), ("s2",)))
        self.assertTrue(mod.relation_is_equivalence(model["states"], relation))

    def test_reachability_is_derived_from_development_and_resources(self):
        self.assertEqual(mod.reachable_versions(mod.base_model()), ("v0", "v1"))

    def test_capability_impossibility_region_is_derived(self):
        self.assertEqual(mod.capability_impossibility_ids(mod.base_model()), ("hidden_world",))

    def test_query_abstention_and_identification_are_derived(self):
        obj = mod.base_model()["uncertainty"]["feasible"]
        self.assertEqual(mod.query_disposition(obj, lambda x: x)["terminal"], "CANNOT_IDENTIFY")
        self.assertEqual(mod.query_disposition(obj, lambda x: 7), {"terminal": "IDENTIFIED", "values": (7,)})
        self.assertEqual(mod.query_disposition(obj, None)["terminal"], "CANNOT_CHECK")

    def test_axiom_1_independence_witness(self):
        self.assertEqual(mod.validate_model(mod.hostile_model("AX-1"))["violated_axioms"], ("AX-1",))

    def test_axiom_2_independence_witness(self):
        self.assertEqual(mod.validate_model(mod.hostile_model("AX-2"))["violated_axioms"], ("AX-2",))

    def test_axiom_3_independence_witness(self):
        self.assertEqual(mod.validate_model(mod.hostile_model("AX-3"))["violated_axioms"], ("AX-3",))

    def test_axiom_4_independence_witness(self):
        self.assertEqual(mod.validate_model(mod.hostile_model("AX-4"))["violated_axioms"], ("AX-4",))

    def test_axiom_5_independence_witness(self):
        self.assertEqual(mod.validate_model(mod.hostile_model("AX-5"))["violated_axioms"], ("AX-5",))

    def test_axiom_6_multiple_independent_hostiles(self):
        for label in ("AX-6-outside", "AX-6-empty", "AX-6-predictive"):
            with self.subTest(label=label):
                self.assertEqual(mod.validate_model(mod.hostile_model(label))["violated_axioms"], ("AX-6",))

    def test_hypercube_exhaustively_attributes_128_combinations(self):
        h = mod.hostile_hypercube()
        self.assertEqual(h["cases"], 128)
        self.assertEqual(h["failures"], ())
        self.assertEqual(h["satisfying_cases"], 1)
        self.assertEqual(h["violation_histogram"]["NONE"], 1)

    def test_dependency_graph_is_acyclic_and_definitions_are_not_axioms(self):
        graph = mod.dependency_graph()
        self.assertTrue(mod.graph_is_acyclic(graph))
        self.assertEqual(set(mod.AXIOMS), {f"AX-{i}" for i in range(1, 7)})
        self.assertTrue(all(node not in mod.AXIOMS for node in ("DEF-1", "DEF-2", "DEF-3", "DEF-4", "DEF-5", "META-1", "META-2")))

    def test_scope_governance_is_not_object_inconsistency(self):
        bad = mod.hostile_model("META-1")
        self.assertTrue(mod.validate_model(bad)["satisfies"])
        self.assertIn("ILLEGAL_SCOPE_PROMOTION", mod.check_meta1(bad)[0])

    def test_claim_ceiling_governance_is_not_object_inconsistency(self):
        bad = mod.hostile_model("META-2")
        self.assertTrue(mod.validate_model(bad)["satisfies"])
        self.assertTrue(any(x.startswith("FORBIDDEN_PROMOTION") for x in mod.check_meta2(bad)))

    def test_negative_resource_names_ax3_not_generic_false(self):
        out = mod.validate_model(mod.hostile_model("AX-3"))
        self.assertEqual(out["violated_axioms"], ("AX-3",))
        self.assertTrue(any("NEGATIVE" in x for x in out["details"]["AX-3"]))

    def test_empty_acceptance_names_ax1(self):
        out = mod.validate_model(mod.hostile_model("AX-1"))
        self.assertTrue(any("EMPTY_ACCEPTED_SET" in x for x in out["details"]["AX-1"]))

    def test_outside_development_edge_names_ax4(self):
        out = mod.validate_model(mod.hostile_model("AX-4"))
        self.assertTrue(any("OUTSIDE_CARRIER" in x for x in out["details"]["AX-4"]))

    def test_above_ceiling_names_ax5(self):
        out = mod.validate_model(mod.hostile_model("AX-5"))
        self.assertTrue(any("ABOVE_CEILING" in x for x in out["details"]["AX-5"]))

    def test_receipt_green_and_byte_stable(self):
        receipt = mod.build_receipt(mod.audit_parents())
        expected = json.loads((HERE / "RESULT_V1.json").read_text())
        self.assertEqual(receipt["verdict"], "GREEN")
        self.assertTrue(all(receipt["checks"].values()))
        self.assertEqual(json.loads(mod.canonical_json(receipt)), expected)
        self.assertEqual(mod.canonical_json(receipt), (HERE / "RESULT_V1.json").read_text())

    def test_no_float_in_exact_receipt(self):
        def walk(x):
            if isinstance(x, float):
                self.fail("float in exact receipt")
            if isinstance(x, dict):
                for v in x.values():
                    walk(v)
            elif isinstance(x, (list, tuple)):
                for v in x:
                    walk(v)
        walk(mod.build_receipt({"all_ok": True, "rows": []}))

    def test_claim_ceiling_bounded(self):
        receipt = mod.build_receipt({"all_ok": True, "rows": []})
        self.assertEqual(receipt["claim_ceiling"], mod.CLAIM_CEILING)
        self.assertIn("ZFC_CONSISTENCY_PROVED", receipt["forbidden_promotions"])
        self.assertIn("COMPLETE_GMI", receipt["forbidden_promotions"])


if __name__ == "__main__":
    unittest.main()
