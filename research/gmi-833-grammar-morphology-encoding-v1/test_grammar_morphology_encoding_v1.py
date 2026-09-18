#!/usr/bin/env python3
"""Test battery for `gmi-833-grammar-morphology-encoding-v1`.

Run:  python3 -I -B  test_grammar_morphology_encoding_v1.py
      python3 -I -O -B test_grammar_morphology_encoding_v1.py

Covers: the D-COST core algebra, the V1-V5 validation bar, the hostile battery, executor
<-> independent-oracle field agreement, receipt/claim-ceiling discipline, and the A4
idempotence assertion.
"""
from __future__ import annotations

import json
import sys
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import adapters_v1                      # noqa: E402
import grammar_morphology_encoding_v1 as E   # noqa: E402
import independent_oracle_v1 as O       # noqa: E402

GRAMMARS = adapters_v1.load_all()
BY_ID = dict((g["grammar_id"], g) for g in GRAMMARS)


class CoreAlgebra(unittest.TestCase):
    def test_mu_is_none_when_unreachable(self):
        pres = [{"pid": "a", "leaves": ["u"], "cost": 3, "sem": "S"}]
        self.assertIsNone(E.mu(pres, "T"))
        self.assertEqual(E.mu(pres, "S"), 3)

    def test_mu_never_uses_a_sentinel(self):
        pres = [{"pid": "a", "leaves": ["u"], "cost": 1, "sem": "S"}]
        kept = E.delete_productions(pres, set(["u"]))
        self.assertEqual(kept, [])
        self.assertIsNone(E.mu(kept, "S"))

    def test_costs_are_exact_ints(self):
        for g in GRAMMARS:
            for p in g["presentations"]:
                self.assertIsInstance(p["cost"], int)
                self.assertNotIsInstance(p["cost"], bool)

    def test_argmin_keeps_full_tie_set(self):
        m = {"A": 1, "B": 1, "C": 2}
        self.assertEqual(E.argmin_classes(m), frozenset(["A", "B"]))

    def test_dep_is_computed_from_costs_not_names(self):
        pres = [{"pid": "a", "leaves": ["TARGETish"], "cost": 1, "sem": "X"},
                {"pid": "b", "leaves": ["z"], "cost": 1, "sem": "X"}]
        u = E.classes_of(pres)
        base = E.mu_map(pres, u)
        after = E.mu_map(E.delete_productions(pres, set(["TARGETish"])), u)
        self.assertEqual(E.dep_classes(base, after), frozenset())

    def test_production_vocabulary_is_string_valued_only(self):
        for g in GRAMMARS:
            for p in g["presentations"]:
                for q in p["leaves"]:
                    self.assertIsInstance(q, str)

    def test_no_presentation_identity_is_a_production(self):
        for g in GRAMMARS:
            pids = set(str(p["pid"]) for p in g["presentations"])
            vocab = set(x for p in g["presentations"] for x in p["leaves"])
            self.assertEqual(vocab & pids, set(), g["grammar_id"])


class Adapters(unittest.TestCase):
    def test_anchor_packages_present(self):
        pkgs = set(g["package"] for g in GRAMMARS)
        for want in ("gmi-833-g0-cost-privilege-v1", "gmi-cross-grammar-four-family-v1",
                     "gmi-833-g0-grammar-growth-v1", "gmi-833-g0-grammar-bias-v1"):
            self.assertIn(want, pkgs)

    def test_out_anchors_absent(self):
        pkgs = set(g["package"] for g in GRAMMARS)
        for bad in ("gmi-833-corpus-census-v1", "gmi-833-depgraph-adjudication-v1",
                    "gmi-833-theory-baseline-v1", "gmi-833-terminology-migration-v1",
                    "ocm-prototype", "programme"):
            self.assertNotIn(bad, pkgs)

    def test_every_declared_target_is_cited_verbatim(self):
        for g in GRAMMARS:
            if g["declared_target"] is None:
                self.assertIsNone(g["target_citation"])
                continue
            c = g["target_citation"]
            self.assertTrue(c["path"] and c["verbatim"], g["grammar_id"])

    def test_declared_target_is_a_real_class_of_its_grammar(self):
        for g in GRAMMARS:
            if g["declared_target"] is None:
                continue
            self.assertIn(g["declared_target"], E.classes_of(g["presentations"]))

    def test_a1_anchor_state_A_is_numeric_and_state_B_is_named(self):
        va = set(x for p in BY_ID["cross_grammar_state_A"]["presentations"]
                 for x in p["leaves"])
        vb = set(x for p in BY_ID["cross_grammar_state_B"]["presentations"]
                 for x in p["leaves"])
        self.assertEqual(va, set())
        self.assertTrue({"not_s"} <= vb)

    def test_a2_anchor_growth_has_composites(self):
        self.assertEqual(sorted(BY_ID["grammar_growth_G2"]["composites"]), ["m1", "m2"])


class ValidationBar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v = E.run_validation(GRAMMARS)

    def test_V1_anchor_891_refound(self):
        v = self.v["V1_anchor_891"]
        self.assertTrue(v["pass"])
        self.assertEqual(v["GA_selection"], ["ALPHA"])
        self.assertEqual(v["GB_selection"], ["BETA"])
        self.assertTrue(v["semantic_coverage_equal"])
        self.assertGreaterEqual(v["r2_selection_reversals_on_GA"], 1)

    def test_V2_planted_recall_is_total(self):
        v = self.v["V2_planted_recall"]
        self.assertTrue(v["pass"])
        self.assertEqual(v["caught"], v["n"])
        self.assertGreater(v["n"], 0)

    def test_V3_no_alarm(self):
        v = self.v["V3_no_alarm"]
        self.assertTrue(v["r3_all_invariant"])
        self.assertEqual(v["clean_control_hits"], 0)

    def test_V4_every_hostile_detected(self):
        r = self.v["V4_hostiles"]["results"]
        for k, val in sorted(r.items()):
            if k.startswith("_"):
                continue
            self.assertEqual(val, "DETECTED", k)

    def test_V5_null_zero_spurious(self):
        v = self.v["V5_null"]
        self.assertEqual(v["spurious_changes"], 0)
        self.assertGreaterEqual(v["randomized_isometry_controls"], 200)

    def test_all_pass(self):
        self.assertTrue(self.v["ALL_PASS"])


class IsometryAndRemint(unittest.TestCase):
    def test_r3_is_an_isometry(self):
        for g in GRAMMARS:
            self.assertTrue(E.is_isometry(g["presentations"],
                                          E.r3_relabel(g["presentations"], 5)))

    def test_cost_mutation_breaks_isometry(self):
        pres = BY_ID["grammar_growth_G2"]["presentations"]
        bad = [dict(p) for p in E.r3_relabel(pres, 5)]
        bad[0]["cost"] = int(bad[0]["cost"]) + 1
        self.assertFalse(E.is_isometry(pres, bad))

    def test_r2_preserves_semantic_coverage(self):
        for g in GRAMMARS:
            base = set(E.classes_of(g["presentations"]))
            for r in E.r2_remints(g["presentations"]):
                self.assertEqual(set(E.classes_of(r["presentations"])), base)

    def test_r2_reproduces_891_bias1(self):
        rep = E.r2_report(BY_ID["cost_privilege_GA"])
        self.assertTrue(rep["bias1_reproduced"])


class OracleAgreement(unittest.TestCase):
    """Freeze section 7c: two materially independent implementation routes."""

    def test_oracle_does_not_import_the_executor(self):
        import re as _re
        src = (HERE / "independent_oracle_v1.py").read_text()
        bad = _re.findall(
            r"^\s*(?:from|import)\s+(grammar_morphology_encoding_v1|adapters_v1)\b",
            src, _re.M)
        self.assertEqual(bad, [])
        self.assertEqual(sorted(set(_re.findall(r"^\s*import\s+(\w+)", src, _re.M))),
                         ["json"])

    def test_field_for_field_agreement(self):
        for g in GRAMMARS:
            hits, notes = E.r1_hits(g)
            mine = E.adjudicate(g, hits, notes)
            theirs = O.run(g)
            self.assertEqual(mine["disposition"], theirs["disposition"], g["grammar_id"])
            self.assertEqual(
                bool(mine.get("tier2_decisive_selection_flip_via_R1")),
                bool(theirs["tier2_decisive_selection_flip_via_R1"]), g["grammar_id"])
            self.assertEqual(len(mine.get("tier1_hits", [])), theirs["n_tier1_hits"],
                             g["grammar_id"])
            self.assertEqual(sorted(set(h["kind"] for h in mine.get("tier1_hits", []))),
                             theirs["tier1_kinds"], g["grammar_id"])
            for a, b in zip(sorted(mine.get("tier1_hits", []),
                                   key=lambda h: (h["via"], tuple(h["productions"]))),
                            theirs["hits"]):
                for f in ("via", "productions", "kind", "mu_target_before",
                          "mu_target_after", "dep", "argmin_before", "argmin_after",
                          "tier2_decisive_selection_flip", "n_presentations_using",
                          "n_target_presentations", "encoding_kind",
                          "indicator_margin"):
                    self.assertEqual(a[f], b[f], "%s %s" % (g["grammar_id"], f))


class A5ClassIndicator(unittest.TestCase):
    def test_growth_library_is_cost_measured(self):
        hits, _ = E.r1_hits(BY_ID["grammar_growth_G2"])
        self.assertTrue(hits)
        for h in hits:
            self.assertEqual(h["encoding_kind"], "COST_MEASURED", h["productions"])

    def test_cross_grammar_hits_are_class_indicators(self):
        """Five of the six cross-grammar hits are pure class indicators (margin 0)."""
        for gid in ("cross_grammar_local_A", "cross_grammar_local_B",
                    "cross_grammar_state_B", "cross_grammar_storage_A",
                    "cross_grammar_storage_B"):
            hits, _ = E.r1_hits(BY_ID[gid])
            self.assertTrue(hits, gid)
            for h in hits:
                self.assertEqual(h["encoding_kind"], "PRODUCTION_IS_CLASS_INDICATOR", gid)
                self.assertEqual(h["indicator_margin"], 0, gid)

    def test_routing_B_is_cost_measured_on_a_thin_margin(self):
        """`branches` also appears in one FIXED_READ presentation (the all-equal-leaves
        candidate), so it does NOT mark the target class exactly. The A5 test is decided
        by incidence, and the margin is published so a reader can see how thin it is."""
        hits, _ = E.r1_hits(BY_ID["cross_grammar_routing_B"])
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["encoding_kind"], "COST_MEASURED")
        self.assertEqual(hits[0]["indicator_margin"], 1)
        self.assertEqual(hits[0]["kind"], "TARGET_IS_A_PRIMITIVE")

    def test_growth_margin_is_wide(self):
        hits, _ = E.r1_hits(BY_ID["grammar_growth_G2"])
        for h in hits:
            self.assertEqual(h["encoding_kind"], "COST_MEASURED")
            self.assertEqual(h["indicator_margin"], 0)
            self.assertEqual(h["kind"], "TARGET_SPECIFIC_SHORTCUT")

    def test_indicator_is_computed_from_incidence_not_names(self):
        pres = [{"pid": "a", "leaves": ["zzz"], "cost": 1, "sem": "T"},
                {"pid": "b", "leaves": ["zzz"], "cost": 2, "sem": "T"},
                {"pid": "c", "leaves": ["w"], "cost": 3, "sem": "U"}]
        self.assertTrue(E.is_class_indicator(pres, "T", set(["zzz"])))
        pres2 = pres + [{"pid": "d", "leaves": ["k"], "cost": 9, "sem": "T"}]
        self.assertFalse(E.is_class_indicator(pres2, "T", set(["zzz"])))

    def test_fixture_is_not_in_the_corpus_population(self):
        self.assertFalse(BY_ID["clean_control_NEUTRAL"]["corpus"])
        for gid, g in sorted(BY_ID.items()):
            if gid != "clean_control_NEUTRAL":
                self.assertTrue(g["corpus"], gid)


class Receipt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = json.loads((HERE / "RESULT_V1.json").read_text())

    def test_claim_ceiling_and_pins(self):
        self.assertEqual(self.r["claim_ceiling"], E.CLAIM_CEILING)
        self.assertEqual(self.r["source_main"], E.SOURCE_MAIN)
        self.assertEqual(self.r["freeze_commit"], E.FREEZE_COMMIT)

    def test_forbidden_promotions_carry_891_list(self):
        fp = set(self.r["forbidden_promotions"])
        for k in ("G0_UNBIASED", "SEARCH_NEUTRALITY_PROVED",
                  "ARCHITECTURE_PRIOR_FREE_GRAMMAR", "GRAMMAR_NEUTRALITY_PROVED",
                  "NO_GRAMMAR_ENCODES_TARGET_UNIVERSALLY"):
            self.assertIn(k, fp)

    def test_891_boundary_is_cited_not_overturned(self):
        self.assertEqual(self.r["parent_boundary"]["issue"], 891)
        self.assertIn("NOT_OVERTURNED", self.r["parent_boundary"]["status"])

    def test_registered_open_instance_is_carried(self):
        self.assertEqual(self.r["registered_open_instance"]["id"],
                         "INSTANCE-AJ9-NOSMUGGLING-SCOPE")
        self.assertFalse(self.r["registered_open_instance"]
                         ["in_mechanical_reach_of_this_pass"])

    def test_every_dlex_hit_is_adjudicated_with_a_reason(self):
        adj = json.loads((HERE / "ADJUDICATION_V1.json").read_text())["d_lex_adjudication"]
        self.assertEqual(adj["n_hits"], self.r["d_lex"]["hits"])
        for row in adj["rows"]:
            self.assertTrue(row["reason"].strip(), row)
            self.assertNotEqual(row["class"], "NEEDS_READ", row)

    def test_screened_is_not_conflated_with_clean(self):
        adj = json.loads((HERE / "ADJUDICATION_V1.json").read_text())["rows"]
        for row in adj:
            if row["disposition"] == "NEUTRAL_AT_REGISTERED_SCOPE":
                self.assertNotIn("R1_NOT_APPLICABLE:NO_PRODUCTION_STRUCTURE",
                                 row.get("notes", []))
                self.assertNotIn("R1_NOT_APPLICABLE:NUMERIC_PARAMETER_SPACE",
                                 row.get("notes", []))

    def test_headline_counts_exclude_the_fixture(self):
        pop = self.r["population"]
        self.assertEqual(pop["validation_fixtures"], 1)
        self.assertEqual(pop["corpus_grammar_instances"],
                         pop["total_instances_loaded"] - 1)
        self.assertNotIn("gmi-833-grammar-morphology-encoding-v1", pop["corpus_packages"])

    def test_encoding_kinds_are_never_summed(self):
        dc = self.r["d_cost"]
        self.assertEqual(
            dc["ENCODES_total"],
            dc["ENCODES_COST_MEASURED__DISCLOSED_CHARGED"]
            + dc["ENCODES_CLASS_INDICATOR__DISCLOSED_CHARGED"]
            + dc["ENCODES_UNDISCLOSED"])
        self.assertTrue(dc["cost_measured_grammars"])
        self.assertTrue(dc["class_indicator_grammars"])
        self.assertEqual(set(dc["cost_measured_grammars"])
                         & set(dc["class_indicator_grammars"]), set())

    def test_authority_self_skip_recorded(self):
        self.assertEqual(self.r["d_lex"]["authority_self_skip"],
                         "gmi-833-grammar-morphology-encoding-v1")

    def test_plex_screen_is_idempotent(self):
        """Amendment A4: the screen must not see its own output."""
        lex = json.loads((HERE / "PLEX_SCREEN_V1.json").read_text())
        self.assertNotIn("gmi-833-grammar-morphology-encoding-v1", lex["population"])
        self.assertEqual(lex["authority_self_skip"],
                         "gmi-833-grammar-morphology-encoding-v1")

    def test_no_floats_anywhere_in_the_receipt(self):
        def walk(o):
            if isinstance(o, float):
                raise AssertionError("float in receipt: %r" % (o,))
            if isinstance(o, dict):
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(self.r)


if __name__ == "__main__":
    unittest.main(verbosity=2)
