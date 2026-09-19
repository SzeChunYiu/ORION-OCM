"""Tests for gmi-833-real-developmental-validation-v1 (real-system sections).

stdlib only; runs as `python3 -I -B test_real_dev_validation_v1.py -v` and
`python3 -I -O -B ...`. Scores from the committed REAL_RUNS artifacts and does
not need torch.
"""
import copy
import json
import os
import subprocess
import sys
import unittest
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import real_dev_validation_v1 as RV  # noqa: E402

RESULT = os.path.join(HERE, "RESULT_V1.json")
ORACLE = os.path.join(HERE, "ORACLE_RESULT_V1.json")


def load(p):
    with open(p) as f:
        return json.load(f)


def has_float(o):
    if isinstance(o, float):
        return True
    if isinstance(o, dict):
        return any(has_float(v) for v in o.values())
    if isinstance(o, list):
        return any(has_float(v) for v in o)
    return False


class FrozenReproduction(unittest.TestCase):
    def test_no_reproduction_errors(self):
        r = load(RESULT)
        self.assertEqual(r["freeze_reproduction_errors"], [])

    def test_six_ecologies_and_sha256(self):
        r = load(RESULT)
        self.assertEqual(len(r["ecologies"]), 6)
        for e in r["ecologies"]:
            self.assertEqual(e["source_sha256"], RV.FROZEN_SHA256[e["system_id"]])
            self.assertFalse(e["fallback_used"])

    def test_frozen_labels_match(self):
        r = load(RESULT)
        for e in r["ecologies"]:
            got = [e["ul11_labels"][n] for n in RV.PRICE_NAMES]
            self.assertEqual(got, RV.FROZEN_UL11[e["system_id"]])

    def test_no_float_anywhere(self):
        self.assertFalse(has_float(load(RESULT)))
        self.assertFalse(has_float(load(ORACLE)))


class SectionITally(unittest.TestCase):
    def test_tally_is_the_reported_one(self):
        t = load(RESULT)["section_I_tally"]
        self.assertEqual(t["HIT"], 20)
        self.assertEqual(t["MISS"], 20)
        self.assertEqual(t["ABSTAIN_MATCHED"], 8)
        self.assertEqual(t["ABSTAIN_UNMATCHED"], 0)
        self.assertEqual(t["TIE_NONIDENTIFYING"], 0)
        self.assertEqual(sum(t.values()), 48)

    def test_comparators_never_ranked(self):
        r = load(RESULT)
        for sid, v in r["section_I"].items():
            if "cells" not in v:
                continue
            for c in v["cells"].values():
                self.assertNotIn(c["observed"], ("BASE-0", "NULL-0"))
            self.assertEqual(len(v.get("comparators_recorded_not_ranked", [])), 2)

    def test_both_sides_predicted(self):
        r = load(RESULT)
        fams = set()
        for e in r["ecologies"]:
            fams.update(e["ul11_labels"].values())
        self.assertGreaterEqual(len([f for f in fams if f.startswith("SIG-")]), 6)
        self.assertIn("ABSTAIN_UNDERDETERMINED", fams)

    def test_rv3_divergence_is_real(self):
        d = load(RESULT)["section_I_divergence"]
        self.assertEqual(d["realizations_compared"], 52)
        self.assertEqual(len(d["signatures_with_any_coordinate_divergence"]), 9)
        self.assertEqual(d["realizations_whose_measured_loss_differs_from_analytic"], 29)


class SectionLContinual(unittest.TestCase):
    def test_v3_matched_control(self):
        r = load(RESULT)
        self.assertEqual(r["section_L_matched_control_pairs"], 7)
        self.assertEqual(r["section_L_matched_control_hits"], 7)
        for v in r["section_L_matched_control"].values():
            self.assertGreater(F(v["pH_pos"]), F(v["pH_neg"]))

    def test_capital_gate_clean_on_v3(self):
        r = load(RESULT)
        self.assertEqual(r["section_L_capital_gate_clean"], 14)
        for v in r["section_L_continual_v3"].values():
            self.assertNotEqual(v["capital"]["status"],
                                "CANNOT_IDENTIFY_STORED_SOLUTION_CONTAMINATION")

    def test_v1_gate_did_fire_the_alarm(self):
        """no-alarm AND alarm cases both exhibited on real data"""
        r = load(RESULT)
        fired = sum(1 for v in r["section_L_continual_v1"].values()
                    if v["capital"]["status"] ==
                    "CANNOT_IDENTIFY_STORED_SOLUTION_CONTAMINATION")
        self.assertEqual(fired, 6)

    def test_dp1a_monotonicity_and_overhead_flip(self):
        r = load(RESULT)
        v3 = r["section_L_continual_v3"]
        self.assertEqual(len(v3), 14)
        for v in v3.values():
            self.assertTrue(v["checks"]["CL3-P5a"])
            self.assertTrue(v["checks"]["CL3-P3"])
            self.assertNotEqual(v["verdict_h_high"], "HISTORY_STRICTLY_IMPROVES")

    def test_terminal(self):
        r = load(RESULT)
        self.assertEqual(
            r["section_L_terminal"],
            "DEVELOPMENTAL_PREDICTIONS_VALIDATED_ON_REAL_CONTINUAL_"
            "SYSTEMS_AT_REGISTERED_SCOPE")

    def test_reported_misses_are_reported(self):
        v3 = load(RESULT)["section_L_continual_v3"]
        p5b = sum(1 for v in v3.values() if v["checks"]["CL3-P5b"])
        p6 = sum(1 for v in v3.values() if v["checks"]["CL3-P6"])
        p1 = sum(1 for v in v3.values() if v["checks"]["CL3-P1"])
        self.assertEqual((p5b, p6, p1), (7, 5, 10))


class TwoRoutes(unittest.TestCase):
    def setUp(self):
        self.a, self.b = load(RESULT), load(ORACLE)

    def test_invariants_thresholds_labels_agree(self):
        for e in self.a["ecologies"]:
            o = self.b["ecologies"][e["system_id"]]
            for k in ("Mprime", "r", "mu", "Dmin", "Dmin_L", "cover", "RS_size",
                      "Bmin", "Tsteps", "alpha_gain", "target_in_H"):
                self.assertEqual(e["invariants"][k], o["invariants"][k],
                                 "%s/%s" % (e["system_id"], k))
            for k in ("beta_star", "chi_star", "pistar_star", "tau_star"):
                self.assertEqual(str(e["thresholds"][k]), str(o["thresholds"][k]),
                                 "%s/%s" % (e["system_id"], k))
            self.assertEqual(e["ul11_labels"], o["ul11_labels"])

    def test_observed_argmin_agrees(self):
        n = 0
        for sid, v in self.a["section_I"].items():
            if "cells" not in v:
                continue
            o = self.b["ecologies"][sid]["observed_argmin"]
            for k, c in v["cells"].items():
                if c["observed"] is not None:
                    self.assertEqual(c["observed"], o[k], "%s/%s" % (sid, k))
                    n += 1
        self.assertEqual(n, 40)

    def test_continual_verdicts_agree(self):
        for k, v in self.a["section_L_continual_v1"].items():
            self.assertEqual(v["verdict_h_low"],
                             self.b["continual"][k]["verdict_h_low"])


class Hostiles(unittest.TestCase):
    """Every hostile must be DETECTED. Also asserts the no-alarm case."""

    def setUp(self):
        self.eco = RV.derive(*RV.SOURCES[0])
        p = os.path.join(HERE, "REAL_RUNS", "ecology_X1-gutenberg-1342.json")
        self.run = load(p)

    def test_HR0_no_alarm_on_clean_data(self):
        self.assertEqual(RV.check_frozen(self.eco), [])
        cells = RV.score_real_systems(self.eco, self.run)
        self.assertEqual(len(cells), 8)
        self.assertTrue(all(c["verdict"] in ("HIT", "MISS") for c in cells.values()))

    def test_HR1_source_sha256_mismatch_detected(self):
        e = copy.deepcopy(self.eco)
        e["source_sha256"] = "0" * 64
        self.assertIn("SOURCE_SHA256_MISMATCH:X1-gutenberg-1342",
                      RV.check_frozen(e))

    def test_HR2_tampered_invariant_detected(self):
        e = copy.deepcopy(self.eco)
        e["invariants"]["alpha_gain"] += 1
        self.assertTrue(any(x.startswith("INVARIANT_MISMATCH")
                            for x in RV.check_frozen(e)))

    def test_HR3_tampered_threshold_detected(self):
        e = copy.deepcopy(self.eco)
        e["thresholds"]["beta_star"] = "1/2"
        self.assertTrue(any(x.startswith("THRESHOLD_MISMATCH")
                            for x in RV.check_frozen(e)))

    def test_HR4_negative_measured_coordinate_detected(self):
        r = copy.deepcopy(self.run)
        k = sorted(r["measured"])[0]
        r["measured"][k][0] = -1
        self.assertRaises(RuntimeError, RV.score_real_systems, self.eco, r)

    def test_HR5_tie_is_never_resolved_into_a_regime(self):
        r = copy.deepcopy(self.run)
        o2s = r["opaque_to_signature"]
        ids = [o for o in sorted(r["measured"]) if o2s[o] in RV.RANKED]
        # make two ranked systems cost exactly zero, so they tie at the argmin
        # for every registered price vector
        r["measured"][ids[0]] = [0] * RV.NPRICE
        r["measured"][ids[1]] = [0] * RV.NPRICE
        cells = RV.score_real_systems(self.eco, r)
        self.assertTrue(all(c["verdict"] == "TIE_NONIDENTIFYING"
                            for c in cells.values()))
        for c in cells.values():
            self.assertIsNone(c["observed"])
            self.assertEqual(len(c["tied"]), 2)

    def test_HR6_stored_contamination_fails_closed(self):
        c = RV.classify_capital(True, True, "HISTORY_STRICTLY_IMPROVES")
        self.assertEqual(c["status"], "CANNOT_IDENTIFY_STORED_SOLUTION_CONTAMINATION")
        self.assertIsNone(c["search_policy_capital"])

    def test_HR7_zero_mass_never_gets_a_finite_burden(self):
        ev = RV.ev1a_band(F(0), F(3))
        self.assertEqual(ev["status"], "UNREACHABLE_ZERO_USEFUL_MASS")
        self.assertIsNone(ev["expected"])

    def test_HR8_comparator_smuggled_into_argmin_changes_the_answer(self):
        """proves the exclusion of BASE-0/NULL-0 is load-bearing, not cosmetic"""
        o2s = self.run["opaque_to_signature"]
        pr = dict(RV.ANCHORED)["A1-unit"]
        allids = sorted(self.run["measured"])
        ranked = [o for o in allids if o2s[o] in RV.RANKED]
        best_all = min(allids, key=lambda o: RV.charge(self.run["measured"][o], pr))
        best_rk = min(ranked, key=lambda o: RV.charge(self.run["measured"][o], pr))
        self.assertNotEqual(o2s[best_all], o2s[best_rk])
        self.assertIn(o2s[best_all], ("BASE-0", "NULL-0"))


class NullControl(unittest.TestCase):
    def test_random_label_predictor_does_not_beat_ul11(self):
        """200 randomized predictors over the 40 decided cells, from a
        registered deterministic LCG. UL-11 scores 20."""
        r = load(RESULT)
        truth = []
        for sid, v in sorted(r["section_I"].items()):
            if "cells" not in v:
                continue
            for k in sorted(v["cells"]):
                c = v["cells"][k]
                if c["observed"] is not None:
                    truth.append(c["observed"])
        self.assertEqual(len(truth), 40)
        fams = sorted(RV.RANKED)
        state, beat, best = 12345, 0, 0
        for _trial in range(200):
            hits = 0
            for t in truth:
                state = (1103515245 * state + 12345) % (1 << 31)
                if fams[state % len(fams)] == t:
                    hits += 1
            best = max(best, hits)
            if hits >= 20:
                beat += 1
        self.assertEqual(beat, 0, "null beat UL-11 %d/200 (best %d)" % (beat, best))
        self.assertLess(best, 20)


class Custody(unittest.TestCase):
    def test_freeze_order_gate_passes(self):
        root = os.path.abspath(os.path.join(HERE, "..", ".."))
        if not os.path.exists(os.path.join(root, ".git")):  # file in a worktree
            # "could not check" is NOT "checked and fine": skip loudly. CI runs
            # check_freeze_order_v1.py as its own required step inside the repo.
            self.skipTest("CUSTODY_NOT_CHECKABLE_OUTSIDE_REPO: %s" % root)
        p = subprocess.Popen(
            [sys.executable, "-I", "-B",
             os.path.join(HERE, "check_freeze_order_v1.py"), root],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        text = out.decode("utf-8", "replace")
        self.assertEqual(p.returncode, 0, text + err.decode("utf-8", "replace"))
        # One state line per freeze. FREEZE_ORDER_OK on a linear history;
        # FREEZE_ORDER_NOT_REDERIVABLE once squash-published (4ba7e89c), with
        # the HEAD-derivable checks listed. Never a violation, never silent.
        states = [ln for ln in text.splitlines()
                  if ln.startswith("FREEZE_ORDER_OK:")
                  or ln.startswith("FREEZE_ORDER_NOT_REDERIVABLE:")]
        self.assertEqual(len(states), 3, text)
        self.assertNotIn("FREEZE_ORDER_VIOLATION", text)
        self.assertNotIn("FREEZE_ORDER_COULD_NOT_CHECK", text)
        self.assertIn("freeze order: 3 freezes checked, no violation", text)


class Determinism(unittest.TestCase):
    def test_result_is_reproducible_byte_for_byte(self):
        import tempfile
        with open(RESULT, "rb") as f:
            want = f.read()
        d = tempfile.mkdtemp()
        p1 = os.path.join(d, "a.json")
        rc = subprocess.call([sys.executable, "-I", "-B",
                              os.path.join(HERE, "real_dev_validation_v1.py"), p1],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(rc, 0)
        with open(p1, "rb") as f:
            got1 = f.read()
        p2 = os.path.join(d, "b.json")
        rc = subprocess.call([sys.executable, "-I", "-O", "-B",
                              os.path.join(HERE, "real_dev_validation_v1.py"), p2],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(rc, 0)
        with open(p2, "rb") as f:
            got2 = f.read()
        self.assertEqual(got1, got2)
        self.assertEqual(got1, want)


if __name__ == "__main__":
    unittest.main(verbosity=2)
