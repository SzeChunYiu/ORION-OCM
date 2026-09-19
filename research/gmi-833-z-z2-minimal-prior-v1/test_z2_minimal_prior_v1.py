"""Tests for #833 Section Z subsection Z2.

Runs under `python3 -I -B` and `python3 -I -O -B`; every assertion is written
with an explicit raise so that `-O` cannot strip it.  Stdlib only.

The tests do three things and nothing else:
  * re-run both routes and require exact agreement on every shared number;
  * require every hostile to be DETECTED and, where the hostile perturbs a
    quantity, require that the quantity actually moved;
  * require the true result to beat its null.
"""
import json
import os
import subprocess
import sys
import unittest
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROUTE_A = os.path.join(HERE, "z2_minimal_prior_v1.py")
ROUTE_B = os.path.join(HERE, "independent_minimal_prior_oracle_v1.py")
AUDIT = os.path.join(HERE, "prior_free_site_audit_v1.py")
RES = os.path.join(HERE, "RESULT_V1.json")
ORA = os.path.join(HERE, "ORACLE_RESULT_V1.json")
SITE = os.path.join(HERE, "PRIOR_FREE_SITE_AUDIT_V1.json")

HALF = Fraction(1, 2)


def need(cond, msg):
    if not cond:
        raise AssertionError(msg)


def run(path):
    r = subprocess.run([sys.executable, "-I", "-B", path],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    need(r.returncode == 0,
         "%s exited %d: %s" % (path, r.returncode, r.stderr.decode()[-2000:]))


def load(path, regen):
    if not os.path.exists(path):
        run(regen)
    with open(path) as fh:
        return json.load(fh)


class Z2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a = load(RES, ROUTE_A)
        cls.b = load(ORA, ROUTE_B)
        cls.s = load(SITE, AUDIT)

    # ------------------------------------------------------------ two routes
    def test_01_routes_agree_on_every_shared_number(self):
        a, b = self.a, self.b
        m1, m2 = a["MP1_encoding_prior"], a["MP2_minimum_bias"]
        m1c = a["MP1c_enumeration_order"]
        pairs = [
            ("K", m1["K_semantic_classes"], b["K_semantic_classes"]),
            ("D_TV", m1["D_TV_syntax_vs_uniform_over_classes"],
             b["D_TV_syntax_vs_uniform_over_classes"]),
            ("class_min", m1["class_size_min"], b["class_size_min"]),
            ("class_max", m1["class_size_max"], b["class_size_max"]),
            ("fh_min", m1c["first_hit_min_probe"], b["first_hit_min_probe"]),
            ("fh_max", m1c["first_hit_max_probe"], b["first_hit_max_probe"]),
            ("pairs_full", m2["scored_pairs_full"], b["scored_pairs_full"]),
            ("pairs_det", m2["scored_pairs_determined"],
             b["scored_pairs_determined"]),
            ("pairs_und", m2["scored_pairs_undetermined"],
             b["scored_pairs_undetermined"]),
            ("A_syn_full", m2["A_syn_full"], b["A_syn_full"]),
            ("A_sem_full", m2["A_sem_full"], b["A_sem_full"]),
            ("A_syn_und", m2["A_syn_undetermined"], b["A_syn_undetermined"]),
            ("A_sem_und", m2["A_sem_undetermined"], b["A_sem_undetermined"]),
            ("dis_full", m2["disagreeing_buckets_full"],
             b["disagreeing_buckets_full"]),
            ("dis_und", m2["disagreeing_buckets_undetermined"],
             b["disagreeing_buckets_undetermined"]),
        ]
        for name, x, y in pairs:
            need(x == y, "route disagreement on %s: %r vs %r" % (name, x, y))

    def test_02_routes_agree_on_every_registered_feature(self):
        fa = self.a["MP2_minimum_bias"]["preference_only_accuracy_undetermined"]
        fb = self.b["preference_only_accuracy_undetermined"]
        shared = [k for k in fa if k in fb]
        need(len(shared) >= 12, "expected >= 12 shared features, got %d"
             % len(shared))
        for k in shared:
            need(fa[k] == fb[k], "feature %s: %s vs %s" % (k, fa[k], fb[k]))

    def test_03_routes_agree_on_the_extremal_swept_features(self):
        m2 = self.a["MP2_minimum_bias"]
        fb = self.b["preference_only_accuracy_undetermined"]
        need(m2["sweep_max_feature"] in fb,
             "route B did not re-score the best swept feature")
        need(fb[m2["sweep_max_feature"]] ==
             m2["sweep_max_accuracy_undetermined"],
             "swept maximum disagrees between routes")
        need(m2["sweep_min_feature"] in fb,
             "route B did not re-score the worst swept feature")
        need(fb[m2["sweep_min_feature"]] ==
             m2["sweep_min_accuracy_undetermined"],
             "swept minimum disagrees between routes")

    def test_04_routes_agree_on_family_recovery_and_invariance(self):
        rec = self.a["MP5_known_form_recovery"]["families"]
        okb = self.b["families_property_first_match_syntactic"]
        sizes = self.b["family_sizes"]
        for k in rec:
            need(rec[k]["exact_match"], "route A: %s not exact" % k)
            need(okb[k], "route B: %s not exact" % k)
            need(rec[k]["family_size"] == sizes[k],
                 "family size disagreement for %s" % k)
        inv_a = self.a["MP4_p3_standard"]["generators"]
        inv_b = self.b["invariance"]
        for g in inv_b:
            need(inv_a[g]["K_invariant"] == inv_b[g]["K_invariant"], g)
            need(inv_a[g]["histogram_invariant"] ==
                 inv_b[g]["histogram_invariant"], g)
            need((inv_a[g]["min_J_invariant"] and
                  inv_a[g]["winning_class_invariant"]) ==
                 inv_b[g]["min_J_and_winner_invariant"], g)
            need(inv_a[g]["per_candidate_membership_invariant"] ==
                 inv_b[g]["per_candidate_membership_invariant"], g)

    # ----------------------------------------------------------- the claims
    def test_05_MP1_encoding_prior_is_strictly_non_uniform(self):
        m = self.a["MP1_encoding_prior"]
        need(m["K_semantic_classes"] == 21904, "K moved")
        need(m["K_semantic_classes"] < self.a["universe"]["candidates"],
             "H1: encoding is not redundant")
        need(Fraction(m["D_TV_syntax_vs_uniform_over_classes"]) > 0,
             "H2: D_TV is zero")
        need(m["class_size_min"] == 1 and m["class_size_max"] == 785,
             "class size extremes moved")

    def test_06_MP3_zero_bits_is_chance_and_one_bit_is_not(self):
        m = self.a["MP2_minimum_bias"]
        need(m["A_free_undetermined_definitional"] == "1/2",
             "the preference-free baseline is not 1/2")
        best = Fraction(m["overall_best_one_bit_accuracy"])
        need(best > HALF, "best one-bit preference does not beat chance")
        need(Fraction(m["sweep_min_accuracy_undetermined"]) < HALF,
             "H6'': no one-bit preference falls below chance")
        need(len(m["one_bit_features_below_half"]) == 9,
             "expected exactly 9 sub-chance one-bit preferences, got %d"
             % len(m["one_bit_features_below_half"]))
        need(Fraction(m["A_syn_undetermined"]) > best,
             "a full measure should buy more than one bit")

    def test_07_MP4_refutation_is_published(self):
        m = self.a["MP2_minimum_bias"]
        need(m["H5_full_A_syn_ne_A_sem"] is False,
             "H5 refutation not recorded")
        need(m["disagreeing_buckets_full"] == 0 and
             m["disagreeing_buckets_undetermined"] == 0,
             "the two reference measures should agree on every bucket")
        need(m["A_syn_undetermined"] == m["A_sem_undetermined"],
             "measures disagree in accuracy but not in buckets")

    def test_08_MP5_invariance_table_and_H7c_refutation(self):
        p = self.a["MP4_p3_standard"]
        need(p["H7a_K_hist_DTV_invariant_under_all"], "H7a failed")
        need(p["H7b_minJ_and_winner_invariant_under_rename_and_state"],
             "H7b failed")
        need(p["H7c_some_generator_moves_minJ_or_winner"] is False,
             "H7c refutation not recorded")
        need(p["H7d_first_hit_moves_under_rename"], "H7d failed")
        need(p["H7e_membership_moves_under_state"], "H7e failed")
        for g, row in p["generators"].items():
            need(row["is_bijection_of_U"], "%s is not a bijection" % g)

    def test_09_MP7_corpus_has_no_live_flagship_site(self):
        s = self.s
        need(s["H9_no_live_flagship_site"],
             "live flagship prior-free sites: %r" % s["live_flagship_sites"])
        need(s["by_category"].get("LIVE_FLAGSHIP", 0) == 0, "category non-empty")
        need(s["occurrences"] == sum(s["by_category"].values()),
             "category counts do not sum to the occurrence count")

    # ----------------------------------------------------------- the nulls
    def test_10_null_N2_is_beaten_and_is_not_inert(self):
        m = self.a["MP2_minimum_bias"]
        need(m["N2_null_features"] == 200, "null size moved")
        need(m["N2_null_at_or_above_best_undetermined"] == 0,
             "%d null features reach the best registered/swept feature"
             % m["N2_null_at_or_above_best_undetermined"])
        need(m["H10_null_majority_not_at_or_above_best"], "H10 failed")
        # the null must not be inert: it has to produce a spread
        need(Fraction(m["N2_null_max_undetermined"]) >
             Fraction(m["N2_null_min_undetermined"]),
             "the null produced no spread at all -- it is inert")
        need(m["N2_null_below_half_undetermined"] == 0,
             "random features fall below chance; the sub-chance finding would "
             "then be generic")

    def test_11_null_N1_and_N3(self):
        need(self.a["MP1_encoding_prior"]["N1_control_is_zero"],
             "N1 control encoding did not return D_TV = 0")
        r = self.a["MP5_known_form_recovery"]
        need(r["N3_random_specs"] == 200, "N3 size moved")
        need(r["N3_random_specs_hitting_a_family"] == 0,
             "%d random specifications hit a registered family"
             % r["N3_random_specs_hitting_a_family"])
        need(r["spec_space_size"] == 531441, "spec space moved")

    # -------------------------------------------------------- the hostiles
    def test_12_every_hostile_is_detected(self):
        a = self.a
        checks = [
            ("HS1", a["vacuity"]["HS1_detected"]),
            ("HS2", a["MP4_p3_standard"]["HS2_nonbijection_detected"]),
            ("HS3", a["MP5_known_form_recovery"]["HS3_family_token_detected"]),
            ("HS4", a["MP2_minimum_bias"]["HS4_peeking_learner_detected"]),
            ("HS6", a["vacuity"]["HS6_detected"]),
            ("HS7", a["MP1_encoding_prior"]["HS7_detected"]),
        ]
        for name, ok in checks:
            need(ok, "hostile %s was not detected" % name)

    def test_13_hostiles_actually_move_their_quantity(self):
        a = self.a
        # HS1 must change the class count, not merely be flagged
        need(a["vacuity"]["HS1_coarse_semantics_K"] !=
             a["MP1_encoding_prior"]["K_semantic_classes"],
             "HS1 did not move the class count it perturbs")
        need(a["vacuity"]["HS1_coarse_semantics_K"] == 143,
             "coarse (e_now,e_delay) class count moved from 143")
        # HS7 must move D_TV to zero
        need(a["MP1_encoding_prior"]["HS7_uniform_histogram_D_TV"] == "0",
             "HS7 did not move D_TV")
        need(a["MP1_encoding_prior"]["D_TV_syntax_vs_uniform_over_classes"]
             != "0", "the real D_TV is zero, so HS7 moves nothing")
        # HS5 must fire in the site classifier's own validation
        v = self.s["validation"]
        need(v["recall_ok"], "planted live-flagship shapes did not all fire")
        need(v["no_false_alarm_ok"], "the classifier alarms on clean text")
        need(v["planted_positives"] >= 4 and v["planted_negatives"] >= 6,
             "the validation gate does not cover the amendment-4 shapes")

    def test_14_vacuity_classifier_separates_binding_from_non_binding(self):
        v = self.a["vacuity"]
        need(v["HS6_C4_shaped_bound_verdict"] == "NON_BINDING",
             "the C4-shaped bound was not classified vacuous")
        need(v["genuine_bound_verdict"] == "BINDING",
             "a genuinely binding bound was classified vacuous")
        need(v["genuine_bound_is_binding"], "binding flag not set")

    # ------------------------------------------------------- bookkeeping
    def test_15_exact_arithmetic_only(self):
        blob = json.dumps(self.a) + json.dumps(self.b)
        for tok in ('.0,', '.0}', 'e-0', 'e+0'):
            need(tok not in blob,
                 "a float-looking token %r appears in a receipt" % tok)
        m = self.a["MP2_minimum_bias"]
        need(m["scored_pairs_determined"] + m["scored_pairs_undetermined"] ==
             m["scored_pairs_full"], "pair bookkeeping does not close")
        need(Fraction(m["determined_fraction"]) ==
             Fraction(m["scored_pairs_determined"], m["scored_pairs_full"]),
             "determined fraction is not the ratio it claims")

    def test_16_claim_ceiling_and_forbidden_promotions_present(self):
        need(self.a["claim_ceiling"].startswith("GMI_833_Z2_"),
             "claim ceiling missing or wrong")
        with open(os.path.join(HERE, "MANIFEST_V1.json")) as fh:
            man = json.load(fh)
        for f in ("PRIOR_FREE_SEARCH_EXISTS", "UNIVERSAL_NO_FREE_LUNCH_PROVED",
                  "MINIMUM_BIAS_IS_UNIVERSALLY_ONE_BIT",
                  "BIAS_CANNOT_HURT_IN_GENERAL",
                  "P3_CERTIFICATE_IMPLIES_NECESSITY",
                  "TERMINOLOGY_MIGRATION_RE_EARNED_HERE"):
            need(f in man["forbidden_promotions"],
                 "forbidden promotion %s missing from the manifest" % f)


if __name__ == "__main__":
    unittest.main(verbosity=2)
