"""Tests for #833 Section Z subsection Z6.

Runs under `python3 -I -B` and `python3 -I -O -B`; every assertion raises
explicitly so `-O` cannot strip it.  Stdlib only.
"""
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
A_PY = os.path.join(HERE, "z6_discrimination_v1.py")
B_PY = os.path.join(HERE, "independent_discrimination_oracle_v1.py")
RES = os.path.join(HERE, "RESULT_V1.json")
ORA = os.path.join(HERE, "ORACLE_RESULT_V1.json")
REG = os.path.join(HERE, "FAILED_PREDICTION_REGISTER_V1.json")


def need(c, m):
    if not c:
        raise AssertionError(m)


def load(path, regen):
    if not os.path.exists(path):
        r = subprocess.run([sys.executable, "-I", "-B", regen],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        need(r.returncode == 0, "%s failed: %s" % (regen,
                                                   r.stderr.decode()[-2000:]))
    with open(path) as fh:
        return json.load(fh)


class Z6(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a = load(RES, A_PY)
        cls.b = load(ORA, B_PY)
        with open(REG) as fh:
            cls.r = json.load(fh)

    # ------------------------------------------------------------ two routes
    def test_01_routes_agree_on_the_scoreboard(self):
        for name in ("T01_GMI", "GMI_REPAIRED", "T09_MDL", "T10_OCCAM_HARD",
                     "T12_SRM"):
            fa = self.a["scores"][name]["by_family"]
            fb = self.b["scores"][name]
            for fam in ("E-LIN", "E-SKEW", "E-COD"):
                for k in ("win", "loss", "abstain", "tie"):
                    need(fa[fam][k] == fb[fam][k],
                         "route disagreement %s/%s/%s: %r vs %r"
                         % (name, fam, k, fa[fam][k], fb[fam][k]))

    def test_02_routes_agree_on_the_R2_readout(self):
        ra = self.a["R2_disagreements_vs_declared_truth"]
        rb = self.b["R2_mismatch_vs_truth"]
        for k in rb:
            need(ra[k] == rb[k], "R2 disagreement for %s: %r vs %r"
                 % (k, ra[k], rb[k]))

    def test_03_routes_agree_on_world_and_point_counts(self):
        need(self.a["worlds"]["total"] == self.b["worlds_total"],
             "world count disagreement")
        need(self.a["universe_candidates"] == self.b["universe_candidates"],
             "universe size disagreement")
        need(self.a["distinct_summaries"]["uniform_points"] ==
             self.b["uniform_points"], "uniform point count disagreement")

    def test_04_route_B_analytic_boundary_reproduces_the_truth(self):
        need(self.b["analytic_boundary_agreements"] ==
             self.b["analytic_boundary_worlds"],
             "the analytic re-derivation misses %d worlds"
             % (self.b["analytic_boundary_worlds"]
                - self.b["analytic_boundary_agreements"]))
        need(self.b["analytic_boundary_worlds"] == 384,
             "analytic world count moved")

    # ------------------------------------------------------------- the rows
    def test_05_registry_covers_every_named_parent(self):
        need(len(self.a["scores"]) >= 13,
             "fewer than 13 registered rules: %d" % len(self.a["scores"]))
        for t in ("T01_GMI", "T02_BAYES", "T03_BOUNDED", "T04_ALGSEL",
                  "T05_NAS", "T06_ACTINF", "T07_RLCTRL", "T08_PROGSYN",
                  "T09_MDL", "T10_OCCAM_HARD", "T11_INFOTHEORY", "T12_SRM",
                  "T13_EVOPEN"):
            need(t in self.a["scores"], "parent %s missing from the registry" % t)

    def test_06_disagreement_is_real_and_adjudicated(self):
        h = self.a["hypotheses"]
        need(h["D3_MDL_disagrees_and_is_wrong_on_E_LIN"], "D3 failed")
        need(h["D4_OCCAM_disagrees_and_is_wrong_on_E_LIN"], "D4 failed")
        need(h["D11_SRM_disagrees_and_is_wrong_on_E_LIN"], "D11 failed")
        for t in ("T09_MDL", "T10_OCCAM_HARD", "T12_SRM"):
            need(self.a["scores"][t]["by_family"]["E-LIN"]["loss"] == 40,
                 "%s E-LIN losses moved from 40" % t)

    def test_07_the_registered_law_loses_where_it_must(self):
        h = self.a["hypotheses"]
        need(h["D5_GMI_correct_on_every_E_LIN_world"],
             "the registered law missed an E-LIN world")
        need(h["D6_GMI_incorrect_on_some_E_SKEW_world"],
             "D6 refuted: the registered law never loses, so it was not tested")
        need(self.a["scores"]["T01_GMI"]["by_family"]["E-SKEW"]["loss"] == 108,
             "E-SKEW loss count moved from 108")
        need(len(self.a["scores"]["T01_GMI"]["first_misses"]) > 0,
             "a loss is claimed with no witness")

    def test_08_the_repair_is_exact_everywhere(self):
        s = self.a["scores"]["GMI_REPAIRED"]["by_family"]
        for fam, n in (("E-LIN", 60), ("E-SKEW", 324), ("E-COD", 20)):
            need(s[fam]["loss"] == 0, "the repaired law loses in %s" % fam)
            need(s[fam]["win"] == n, "%s win count %d != %d"
                 % (fam, s[fam]["win"], n))

    def test_09_observational_equivalence_is_measured_not_assumed(self):
        need(self.a["hypotheses"]
             ["D12_repaired_law_R1_equivalent_to_declared_cost_parents"],
             "D12 failed")
        for t in ("T02_BAYES", "T03_BOUNDED", "T04_ALGSEL", "T05_NAS",
                  "T06_ACTINF", "T07_RLCTRL", "T08_PROGSYN"):
            need(self.a["vs_GMI_REPAIRED"][t]["R1_disagreements"] == 0,
                 "%s disagrees with the repaired law" % t)
        need(self.a["hypotheses"]["D10_infotheory_and_evopen_abstain_everywhere"],
             "D10 failed: an abstaining parent emitted a class prediction")

    def test_10_refuted_hypotheses_are_published(self):
        h = self.a["hypotheses"]
        need(h["D1_T02_T08_R1_equivalent_to_GMI_everywhere"] is False,
             "D1 refutation not recorded")
        need(h["D2_some_T02_T08_disagrees_on_R2"] is False,
             "D2 refutation not recorded")
        ids = dict((e["id"], e["verdict"]) for e in self.r["entries"])
        need(ids.get("DP-1") == "REFUTED", "DP-1 must be REFUTED")
        need(ids.get("DP-3") == "REFUTED", "DP-3 must be REFUTED")
        need(ids.get("DP-4") == "REFUTED", "DP-4 must be REFUTED")
        need(ids.get("DP-2") == "CONFIRMED", "DP-2 must be CONFIRMED")
        e1 = [e for e in self.r["entries"] if e["id"] == "DP-1"][0]
        need("claim_ceiling_change" in e1,
             "a refuted law must name the claim text it retires")

    # ------------------------------------------------------------ the nulls
    def test_11_null_N1_is_not_inert_and_is_beaten(self):
        need(self.a["N1_null_rules"] == 200, "null size moved")
        need(self.a["N1_null_rules_R1_equivalent_to_GMI"] == 0,
             "%d random monotone rules reproduce the equivalence, so it is "
             "an artifact of the readout"
             % self.a["N1_null_rules_R1_equivalent_to_GMI"])

    def test_12_null_N2_and_N3(self):
        need(self.a["N2_shifted_threshold_E_LIN_losses"] > 0,
             "the shifted control never misses, so the test cannot falsify")
        need(self.a["N2_shifted_threshold_E_LIN_losses"] == 40,
             "shifted control E-LIN misses moved from 40")
        need(self.a["N3_always_abstain_wins"] == 0
             and self.a["N3_always_abstain_losses"] == 0,
             "the always-abstainer scored something")
        need(self.a["hostiles"]["HS3_abstainer_not_counted_as_equivalent"],
             "abstention was counted as agreement")

    # --------------------------------------------------------- the hostiles
    def test_13_every_hostile_fires(self):
        h = self.a["hostiles"]
        need(h["HS1_planted_oracle_reader_detected"],
             "the planted ground-truth reader was not detected")
        need(h["HS1_no_registered_theory_leaks"],
             "a registered theory moved when the truth was permuted")
        need(h["HS2_every_world_has_candidates"], "an empty world survived")
        need(h["HS4_disagreements_exclude_abstentions"], "HS4 failed")
        need(h["HS5_shifted_control_misses"], "HS5 failed")
        need(h["HS6_exact_boundary_worlds_reported_as_tie"] == 20,
             "exact-boundary worlds not reported as ties: %r"
             % h["HS6_exact_boundary_worlds_reported_as_tie"])

    def test_14_abstentions_are_excluded_and_counted(self):
        for t in ("T09_MDL", "T10_OCCAM_HARD", "T12_SRM", "T02_BAYES"):
            need(self.a["vs_T01_GMI"][t]["excluded_abstentions"] == 20,
                 "%s abstention exclusion count moved from 20" % t)

    # ------------------------------------------------------- bookkeeping
    def test_15_world_bookkeeping_closes(self):
        w = self.a["worlds"]
        need(w["E_LIN"] + w["E_SKEW"] + w["E_COD"] == w["total"],
             "world counts do not sum")
        need(w["total"] == 404, "world total moved from 404")
        for name, sc in self.a["scores"].items():
            tot = sum(sc["by_family"][f]["win"] + sc["by_family"][f]["loss"]
                      + sc["by_family"][f]["abstain"]
                      for f in sc["by_family"])
            need(tot == w["total"],
                 "%s scored %d of %d worlds" % (name, tot, w["total"]))

    def test_16_no_float_and_ceiling_present(self):
        blob = json.dumps(self.a) + json.dumps(self.b)
        for tok in (".0,", ".0}", "e-0", "e+0"):
            need(tok not in blob, "float-looking token %r in a receipt" % tok)
        need(self.a["claim_ceiling"].startswith("GMI_833_Z6_"),
             "claim ceiling missing")
        with open(os.path.join(HERE, "MANIFEST_V1.json")) as fh:
            man = json.load(fh)
        for f in ("GMI_TRUER_THAN_MDL", "PARENT_THEORIES_REFUTED",
                  "UNIVERSAL_OBSERVATIONAL_EQUIVALENCE",
                  "FLAGSHIP_LAW_VALIDATED_BEYOND_UNIFORM_INPUTS",
                  "REPAIRED_LAW_IS_UNIVERSAL"):
            need(f in man["forbidden_promotions"],
                 "forbidden promotion %s missing" % f)


if __name__ == "__main__":
    unittest.main(verbosity=2)
