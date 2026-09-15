#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest
from fractions import Fraction

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
SPEC = importlib.util.spec_from_file_location("no_smuggling_audit_v1", HERE / "no_smuggling_audit_v1.py")
mod = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)

class NoSmugglingAuditV1Tests(unittest.TestCase):
    def test_clean_fixture_is_clean(self):
        out=mod.audit_record(mod.clean_record()); self.assertEqual(out["terminal"],mod.CLEAN); self.assertTrue(all(t==mod.CLEAN for t in out["terminals"]))
    def test_lexical_variants_fire(self):
        for name in ["transformer","self_attention","SelfAttention","Conv2D","lstm_gate","rag_retriever","RAG-Retriever"]:
            with self.subTest(name=name): self.assertEqual(mod.lexical_audit(mod.lexical_hostile(name))["terminal"],"LEXICAL_LEAKAGE")
    def test_semantic_rename_defeats_lexical_only_screen(self):
        r=mod.semantic_rename_hostile(); self.assertEqual(mod.lexical_audit(r)["terminal"],mod.CLEAN); self.assertEqual(mod.semantic_audit(r)["terminal"],"SEMANTIC_MACRO_LEAKAGE")
    def test_local_shared_macro_flags_semantically(self):
        r=mod.local_shared_hostile(); self.assertEqual(mod.lexical_audit(r)["terminal"],mod.CLEAN); self.assertEqual(mod.semantic_audit(r)["terminal"],"SEMANTIC_MACRO_LEAKAGE")
    def test_decomposed_generic_primitives_remain_clean(self): self.assertEqual(mod.semantic_audit(mod.clean_record())["terminal"],mod.CLEAN)
    def test_cost_scalarization_reversal(self):
        o=mod.cost_audit(mod.cost_reversal_hostile()); self.assertEqual(o["terminal"],"COST_PRIOR_SENSITIVE"); self.assertTrue(o["winner_reversal"]); self.assertEqual(dict(o["winners"])["compute_price_high"],("compute_light",)); self.assertEqual(dict(o["winners"])["memory_price_high"],("memory_light",))
    def test_zero_cost_privileged_operation_flags(self):
        o=mod.cost_audit(mod.zero_cost_hostile()); self.assertEqual(o["terminal"],"COST_PRIOR_SENSITIVE"); self.assertTrue(any(f["kind"]=="ZERO_COST_PRIVILEGED_OPERATOR" for f in o["findings"]))
    def test_negative_resource_fails_cost_audit(self):
        r=mod.clean_record(); r["cost"]["candidates"][0]["resources"]["compute"]="-1"; o=mod.cost_audit(r); self.assertEqual(o["terminal"],"COST_PRIOR_SENSITIVE"); self.assertTrue(any(f["kind"]=="NEGATIVE_RESOURCE_COORDINATE" for f in o["findings"]))
    def test_search_order_sensitivity(self): self.assertEqual(dict(mod.search_audit(mod.search_order_hostile())["winners"]),{"forward":"a","reverse":"b"})
    def test_exhaustive_search_removes_order_dependence_for_unique_optimum(self):
        o=mod.search_audit(mod.clean_record()); self.assertEqual(o["terminal"],mod.CLEAN); self.assertEqual({w for _,w in o["winners"]},{"a"})
    def test_evaluation_target_id_bonus_flags(self):
        o=mod.evaluation_audit(mod.evaluation_id_hostile()); self.assertEqual(o["terminal"],"EVALUATION_PRIOR_SENSITIVE"); k={f["kind"] for f in o["findings"]}; self.assertIn("ARCHITECTURE_ID_IN_SCORE",k); self.assertIn("TARGET_ID_BONUS",k)
    def test_evaluation_metric_reversal_flags_universal_claim(self):
        o=mod.evaluation_audit(mod.evaluation_metric_hostile()); self.assertEqual(o["terminal"],"EVALUATION_PRIOR_SENSITIVE"); self.assertTrue(o["winner_reversal"])
    def test_ecology_positive_only_sample_from_balanced_frame_flags(self):
        o=mod.ecology_audit(mod.ecology_bias_hostile()); self.assertEqual(o["terminal"],"ECOLOGY_SELECTION_BIAS"); self.assertEqual(o["frame_prevalence"],Fraction(1,2)); self.assertEqual(o["sample_prevalence"],Fraction(1))
    def test_unknown_frame_preserves_abstention(self): self.assertEqual(mod.ecology_audit(mod.unknown_frame_hostile())["terminal"],"CANNOT_AUDIT_FRAME_REPRESENTATIVENESS")
    def test_missing_disclosures_fail_closed(self):
        for b in ("lexical","semantic","cost","search","evaluation","ecology"):
            with self.subTest(block=b): self.assertTrue(mod.audit_record(mod.missing_disclosure_hostile(b))["subaudits"][b]["terminal"].startswith("CANNOT_AUDIT_"))
    def test_full_hostiles_are_not_coerced_clean(self):
        for f in (mod.semantic_rename_hostile,mod.cost_reversal_hostile,mod.search_order_hostile,mod.evaluation_id_hostile,mod.ecology_bias_hostile):
            with self.subTest(fixture=f.__name__): self.assertEqual(mod.audit_record(f())["terminal"],"AUDIT_NOT_CLEAN")
    def test_receipt_is_green_and_byte_stable(self):
        r=mod.build_receipt(); self.assertEqual(r["verdict"],"GREEN"); self.assertTrue(all(r["checks"].values())); p=HERE/"RESULT_V1.json"; expected=json.loads(p.read_text()); self.assertEqual(json.loads(mod.canonical_json(r)),expected); self.assertEqual(mod.canonical_json(r),p.read_text())
    def test_claim_ceiling_stays_bounded(self):
        r=mod.build_receipt(); self.assertEqual(r["claim_ceiling"],mod.CLAIM_CEILING); self.assertIn("COMPLETE_GMI",r["forbidden_promotions"]); self.assertIn("SEMANTIC_NEUTRALITY_PROVED",r["forbidden_promotions"])
    def test_no_float_in_receipt(self):
        def walk(x):
            if isinstance(x,float): self.fail("float found in exact receipt")
            if isinstance(x,dict):
                for v in x.values(): walk(v)
            elif isinstance(x,(list,tuple)):
                for v in x: walk(v)
        walk(mod.build_receipt())

if __name__=="__main__": unittest.main()
