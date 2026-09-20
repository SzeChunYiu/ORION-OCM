"""Tests for `gmi-833-kl-revival-v1`.

Run both ways:
  python3 -I -B  test_kl_revival_v1.py -v
  python3 -I -O -B test_kl_revival_v1.py -v

Every assertion is a unittest method call, so -O cannot silently disable any of
them.  The receipts are read from the package; the bridge, the truthfulness
count, the scores and the custody clauses are re-derived here rather than
trusted.  Off-repository source bytes are not needed.
"""

from fractions import Fraction
import glob
import hashlib
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import heldout_universes_real4_v1 as r4   # noqa: E402
import kl_revival_v1 as A                 # noqa: E402
import oracle_route_b_v1 as B             # noqa: E402

hu = r4.hu


def load(name):
    with open(os.path.join(HERE, name)) as h:
        return json.load(h)


RESULT = load("RESULT_V1.json")
ORACLE = load("ORACLE_RESULT_V1.json")
ROWS = load("FREEZE_ROWS_V1.json")
RECON = load("ISSUE_833_RECONCILIATION_KL_REVIVAL_V1.json")
MANIFEST = load("MANIFEST_V1.json")
FROZEN = load("FROZEN_PREDICTIONS_REAL4_V1.json")
RECEIPT_V4 = load(os.path.join("REAL_RUNS_V4", "REAL_MEASURED_V4.json"))
K = RESULT["row_K"]
L = RESULT["row_L"]
W1 = L["windows"]["W1"]
W2 = L["windows"]["W2"]


class BridgeDerivation(unittest.TestCase):
    def test_cr1_re_derives_the_frozen_table(self):
        table, evidence = r4.derive_bridge()
        self.assertEqual(table, r4.FROZEN_SB_TABLE)
        self.assertEqual(evidence["untrained"]["solved"], 0)
        self.assertEqual(evidence["T0_trained"]["solved"], 24)
        self.assertEqual(evidence["MLP_T1_trained"]["solved"], 0)
        self.assertEqual(evidence["MLP_T2_trained"]["solved"], 0)

    def test_route_b_derivation_agrees(self):
        _intervals, summary = B.derive_intervals(B.receipts())
        self.assertTrue(summary["untrained_all_unsolved"])
        self.assertTrue(summary["T0_solved"])
        self.assertTrue(summary["MLP_T1_unsolved"])
        self.assertTrue(summary["MLP_T2_unsolved"])
        self.assertEqual(summary["GRU_T1_threshold"], 12)
        self.assertIsNone(summary["GRU_T2_threshold"])

    def test_admissible_sets_on_named_machines(self):
        table = r4.FROZEN_SB_TABLE
        self.assertEqual(r4.admissible_bits(table, ("MLP", 6, 0, 1)), (1,))
        self.assertEqual(r4.admissible_bits(table, ("MLP", 48, 1, 7)), (1,))
        self.assertEqual(r4.admissible_bits(table, ("GRU", 48, 0, 3)), (3,))
        self.assertEqual(r4.admissible_bits(table, ("GRU", 48, 0, 5)), (1, 5))
        self.assertEqual(r4.admissible_bits(table, ("GRU", 6, 0, 7)), (1, 3, 5, 7))
        self.assertEqual(r4.admissible_bits(table, ("GRU", 6, 1, 3)), (1, 3))

    def test_bridge_lies_between_the_two_extremes_and_is_not_total(self):
        table = r4.FROZEN_SB_TABLE
        abstaining = 0
        for m in r4.REAL4_MACHINES:
            adm = set(r4.admissible_bits(table, m))
            self.assertTrue(adm <= set(r4.proto_admissible_bits(m)))
            self.assertGreaterEqual(len(adm), 1)
            if len(adm) > 1:
                abstaining += 1
        self.assertEqual(abstaining, 32 - K["resolved_machines"])
        self.assertEqual(K["resolved_machines"], 22)
        self.assertEqual(K["committed_cells"], 84)
        self.assertEqual(len(r4.committed_cells(table, r4.REAL4_MACHINES)), 84)


class RowK(unittest.TestCase):
    def test_measured_bits_follow_the_registered_band(self):
        band = Fraction(99, 100)
        acc = RECEIPT_V4["per_head_exact_accuracy"]
        for m in r4.REAL4_MACHINES:
            mech, size, w, h = m
            bits = 0
            for j in range(3):
                key = "%s|%d|%d|%d" % (mech, size, w, j)
                a = Fraction(acc[key]["trained"] if (h >> j) & 1 else acc[key]["untrained"])
                if a >= band:
                    bits |= 1 << j
            self.assertEqual(bits, RECEIPT_V4["measured_solved_bits"][r4.machine_key(m)])
        self.assertTrue(all(Fraction(a["untrained"]) < band for a in acc.values()))
        self.assertTrue(K["receipt"]["untrained_heads_below_band"])

    def test_truthfulness_recomputed_from_the_receipt(self):
        table = r4.FROZEN_SB_TABLE
        truthful = 0
        for m in r4.REAL4_MACHINES:
            if RECEIPT_V4["measured_solved_bits"][r4.machine_key(m)] in r4.admissible_bits(table, m):
                truthful += 1
        self.assertEqual(truthful, 32)
        self.assertEqual(K["truthfulness"]["truthful"], 32)
        self.assertEqual(K["truthfulness"]["falsified_cells"], {})
        self.assertEqual(ORACLE["row_K"]["truthful"], 32)

    def test_census_matches_the_frozen_prediction_file(self):
        self.assertEqual(K["census"], FROZEN["set_valued_census"])
        self.assertEqual(K["census"]["nd2"], 2100)
        self.assertEqual(K["census"]["nd1"], 7976)
        self.assertEqual(K["census"]["inputs"], 51840)
        self.assertEqual(K["census"]["nd2_values"], {"8/17": 2100})
        self.assertTrue(K["frozen_stream"]["reproduced"])
        self.assertEqual(K["frozen_stream"]["frozen_sha256"], FROZEN["stream_sha256"])
        self.assertEqual(ORACLE["row_K"]["stream_sha256_route_a_format"], K["frozen_stream"]["executor_sha256"])

    def test_live_census_re_derived_here(self):
        parent = hu.load_parent()
        spec = r4.sigma_real4(r4.FROZEN_SB_TABLE)
        hu.install_universe(parent, r4.clean_spec(spec))
        structure = A.input_structure(parent)
        imgs = A.images(parent, structure, A.bitmap_of_table(r4.FROZEN_SB_TABLE, r4.REAL4_MACHINES),
                        r4.REAL4_MACHINES, hu.MU_REAL)
        census = A.census_of(imgs)
        self.assertEqual(census, K["census"])
        real_bits = A.measured_bits_from_receipt(RECEIPT_V4, r4.REAL4_MACHINES)
        snd = A.soundness(parent, structure, imgs, real_bits, hu.MU_REAL)
        self.assertEqual(snd["violating_pairs"], 0)
        self.assertEqual(snd["pairs"], K["soundness"]["pairs"])
        self.assertEqual(snd["pairs"], 131136)

    def test_soundness_and_controls(self):
        self.assertEqual(K["soundness"]["violating_pairs"], 0)
        self.assertEqual(K["soundness"]["violating_inputs"], 0)
        pk1 = K["positive_controls"]["PK1_v3_point_law"]
        pk2 = K["positive_controls"]["PK2_cb_proto"]
        self.assertGreater(pk1["nd2"], K["census"]["nd2"])
        self.assertEqual(pk1["nd2"], 3376)
        self.assertEqual(pk1["truthful_machines"], 28)
        self.assertGreater(pk1["soundness"]["violating_pairs"], 0)
        self.assertTrue(pk2["both_zero"])
        self.assertEqual(pk2["truthful_machines"], 32)

    def test_null_is_beaten_and_not_vacuous(self):
        null = K["null"]["NULL_RANDOM_COMMIT"]
        self.assertEqual(null["seeds"], 200)
        self.assertEqual(null["committed_cells"], 84)
        self.assertEqual(null["fully_truthful_seeds"], 0)
        self.assertLess(null["max_truthful_machines"], 32)
        self.assertGreater(null["nd2_max"], 0)
        self.assertTrue(null["beaten"])

    def test_hostiles_move_their_own_quantities(self):
        h = K["hostiles"]
        self.assertTrue(h["HK1_drop_protocol_clause"]["detected"])
        self.assertLess(h["HK1_drop_protocol_clause"]["nd2"], K["census"]["nd2"])
        self.assertLess(h["HK1_drop_protocol_clause"]["nd1"], K["census"]["nd1"])
        self.assertTrue(h["HK2_degenerate_counted"]["detected"])
        self.assertEqual(h["HK2_degenerate_counted"]["nd2"], K["census"]["point"])
        self.assertTrue(h["HK3_planted_false_commitment"]["applicable"])
        self.assertTrue(h["HK3_planted_false_commitment"]["detected"])
        expected_flagged = sum(1 for m in r4.REAL4_MACHINES
                               if m[0] == "MLP" and (m[3] & 2)
                               and not (RECEIPT_V4["measured_solved_bits"][r4.machine_key(m)] >> 1) & 1)
        self.assertEqual(h["HK3_planted_false_commitment"]["flagged"], expected_flagged)
        self.assertEqual(expected_flagged, 8)
        self.assertTrue(h["HK4_receipt_mutation"]["applicable"])
        self.assertTrue(h["HK4_receipt_mutation"]["detected"])
        self.assertGreater(h["HK4_receipt_mutation"]["violating_pairs"], 0)
        self.assertTrue(h["HK5_route_disagreement"]["mutation_changes_stream"])
        self.assertTrue(ORACLE["agreement"]["HK5_route_disagreement_detected"])
        self.assertTrue(h["HK7_parent_blob_mutation"]["detected"])
        self.assertEqual(h["HK7_parent_blob_mutation"]["true_blob"], hu.PARENT_BLOB_SHA)

    def test_parent_blob_refusal_is_live(self):
        A.verify_parent_blob(hu.PARENT_FILE)
        with self.assertRaises(ValueError):
            A.verify_parent_blob(os.path.join(HERE, "kl_revival_v1.py"))

    def test_routes_agree_and_the_row_closes(self):
        agree = ORACLE["agreement"]
        self.assertTrue(agree["all"])
        self.assertTrue(all(agree["row_K"].values()))
        self.assertTrue(agree["row_K"]["per_input_stream"])
        self.assertEqual(ORACLE["row_K"]["random_world_consistency"]["inconsistent"], 0)
        self.assertTrue(K["decision"]["closes_pending_route_b"])
        self.assertTrue(all(K["decision"]["clauses"].values()))
        self.assertTrue(K["parent_code_unchanged"])
        self.assertEqual(K["parent_file_blob_sha"], hu.PARENT_BLOB_SHA)


class RowLCustody(unittest.TestCase):
    def test_checker_validated_both_directions(self):
        cv = L["checker_validation"]
        self.assertTrue(cv["validated_both_directions"])
        self.assertTrue(cv["fixtures"]["PLANTED_ADMISSIBLE"]["verdict"]["admissible"])
        for name in ("HL1_pre_freeze_timestamp", "HL1b_inside_guard", "HL2_repository_blob",
                     "HL3_outside_hash_mismatch", "PARENT_IN_SESSION_AUTHORED"):
            self.assertFalse(cv["fixtures"][name]["verdict"]["admissible"], name)
        self.assertGreaterEqual(sum(1 for n in cv["fixtures"] if n.startswith("PARENT_")), 6)

    def test_checker_live_recall_and_no_alarm(self):
        cust = A.Custody(A.FREEZE_COMMIT)
        if cust.t_freeze is None or cust.blobs is None:
            self.skipTest("freeze commit unreachable in this checkout")
        live = A.validate_custody_checker(cust)
        self.assertTrue(live["validated_both_directions"])

    def test_every_window_source_is_posterior_and_attested(self):
        for wid, win in (("W1", W1), ("W2", W2)):
            if win.get("status") != "OK":
                continue
            anchor = A.parse_iso(win["anchor_committer_time_utc"])
            for v in win["custody"]["verdicts"]:
                self.assertTrue(v["admissible"], "%s %s" % (wid, v["source_id"]))
                self.assertGreater(A.parse_iso(v["creation_timestamp"]),
                                   anchor + A.datetime.timedelta(seconds=A.GUARD_SECONDS))
                self.assertTrue(all(v["clauses"][c] is True for c in
                                    ("1_dated", "2_posterior", "3_exogenous", "4_attested")))
            self.assertGreaterEqual(win["custody"]["admissible"], 6)

    def test_ps1_replay_live_on_the_committed_records(self):
        for win in A.WINDOWS:
            record = A.load_posterior_record(win["record"])
            if record is None:
                continue
            t = A.freeze_time(win["anchor_commit"])
            if t is None:
                self.skipTest("anchor commit unreachable")
            rep = A.replay_ps1(record, t)
            self.assertTrue(rep["ok"], rep["checks"])
            self.assertEqual(rep["verdict_mismatches"], [])

    def test_window_2_is_posterior_to_window_1_fetch(self):
        if W2.get("status") != "OK":
            self.skipTest("window 2 not scored")
        t_fetch_1 = A.parse_iso(W1["record"]["T_fetch_utc"])
        for v in W2["custody"]["verdicts"]:
            self.assertGreater(A.parse_iso(v["creation_timestamp"]), t_fetch_1)
        self.assertGreater(A.parse_iso(W2["anchor_committer_time_utc"]), t_fetch_1)

    def test_no_admitted_source_is_a_repository_blob_at_its_anchor(self):
        cust = A.Custody(A.FREEZE_COMMIT)
        if cust.blobs is None:
            self.skipTest("freeze commit unreachable")
        shas = cust.freeze_blob_sha256s()
        for win in (W1, W2):
            for v in win.get("custody", {}).get("verdicts", []):
                self.assertNotIn(v["sha256"], shas)

    def test_hostiles(self):
        for wid, win in (("W1", W1), ("W2", W2)):
            if win.get("status") != "OK":
                continue
            h = win["hostiles"]
            for name in ("HL1_pre_freeze_timestamp", "HL2_repository_blob", "HL3_outside_hash_mismatch",
                         "HL5_tie_receipt"):
                self.assertTrue(h[name]["detected"], "%s %s" % (wid, name))
            self.assertTrue(h["HL4_swapped_receipt"]["detected"] or not h["HL4_swapped_receipt"]["applicable"])
            self.assertTrue(h["HL6_wrong_freeze_commit"]["detected"] or not h["HL6_wrong_freeze_commit"]["applicable"])


class RowLScores(unittest.TestCase):
    def recompute(self, runs, prefix, pos_base, neg_base, record_name):
        record = A.load_posterior_record(record_name)
        out = []
        for n, src in enumerate(record["admitted"]):
            pos_id = "T%02d" % (pos_base + n)
            pil = load(os.path.join(runs, "pilot_%s.json" % pos_id))
            if pil.get("B_prop") is None:
                continue  # AT_FLOOR_OR_CEILING source excluded by PR-1, not scored
            p = load(os.path.join(runs, "%s_%s.json" % (prefix, pos_id)))
            q = load(os.path.join(runs, "%s_%s.json" % (prefix, "T%02d" % (neg_base + n))))
            self.assertEqual(p["source_sha256"], src["sha256"])
            self.assertEqual(q["source_sha256"], src["sha256"])
            self.assertEqual(p["c"], pil["B_prop"])
            self.assertEqual(q["c"], pil["B_prop"])
            crit = p["criterion_correct"]
            self.assertEqual(crit, 112)
            out.append((sum(1 for x in p["scores_QH_B2"] if x >= crit),
                        sum(1 for x in q["scores_QH_B2"] if x >= crit),
                        sum(1 for x in p["scores_Q0_B2"] if x >= crit),
                        max(p["scores_QH_B2"]), max(q["scores_QH_B2"])))
        return out

    def test_window_1_scores_recomputed(self):
        rows = self.recompute("REAL_RUNS_L4", "cl4", 21, 31, "POSTERIOR_SOURCES_V1.json")
        t = W1["tally"]
        self.assertEqual([r[0] for r in rows], t["pH_pos_hits"])
        self.assertEqual([r[1] for r in rows], t["pH_neg_hits"])
        self.assertEqual([r[2] for r in rows], t["p0_pos_hits"])
        self.assertEqual([r[3] for r in rows], t["C_pot_QH_pos"])
        self.assertEqual([r[4] for r in rows], t["C_pot_QH_neg"])
        self.assertEqual(sum(1 for r in rows if r[0] > r[1]), t["EP1_hits"])
        self.assertEqual(t["EP1_hits"], 5)
        self.assertEqual(t["scored_admissible_sources"], 6)
        self.assertEqual(t["EP1_misses"], ["P05"])
        self.assertEqual(t["EP2_hits"], 6)
        self.assertEqual(t["EP4_hits"], 6)
        self.assertEqual(t["pH_pos_hits"], [13, 6, 12, 16, 0, 12])
        self.assertEqual(t["pH_neg_hits"], [0, 0, 0, 0, 0, 0])
        self.assertEqual(t["C_pot_QH_pos"], [123, 118, 123, 125, 103, 123])
        self.assertEqual(t["C_pot_QH_neg"], [79, 81, 101, 89, 78, 77])

    def test_window_1_is_open_under_freeze_v1_with_one_stage_attributed(self):
        d = W1["decision"]
        self.assertFalse(d["closes_pending_route_b"])
        self.assertFalse(d["clauses"]["3_EP1_k_of_k_with_k_at_least_6"])
        self.assertTrue(d["clauses"]["1_at_least_6_admissible"])
        self.assertTrue(d["clauses"]["2_pilot_interior_on_scored"])
        self.assertEqual(d["attribution"]["stage"], "prediction")
        self.assertEqual(d["attribution"]["misses"], ["P05"])
        self.assertEqual(d["attribution"]["sub_stage"], "instrument_threshold_resolution")
        md = d["attribution"]["miss_detail"][0]
        self.assertEqual((md["pH_pos"], md["pH_neg"], md["C_pot_QH_pos"], md["C_pot_QH_neg"]), (0, 0, 103, 78))
        self.assertLess(md["C_pot_QH_pos"], md["criterion"])
        self.assertEqual(W1["tally"]["exact_null_probability_observed_or_better"], "7/64")

    def test_pilot_rule_replayed_on_every_source(self):
        for win in (W1, W2):
            if win.get("status") != "OK":
                continue
            for s in win["scores"]:
                if s.get("status") != "SCORED":
                    self.assertEqual(s["status"], "AT_FLOOR_OR_CEILING")
                    self.assertTrue(s["pilot"]["PR1_replay"]["ok"])
                    continue
                self.assertTrue(s["pilot"]["PR1_replay"]["ok"])
                self.assertEqual(s["pilot"]["B_prop"], s["c"])
                self.assertEqual(s["B1"], max(1, s["c"] // 3))
                self.assertEqual(s["B2"], s["c"])
                self.assertTrue(s["receipt_counts_consistent"])
                self.assertEqual(s["N_prop"], 24)

    def test_window_2_scores_recomputed_if_present(self):
        if W2.get("status") != "OK":
            self.skipTest("window 2 not scored")
        rows = self.recompute("REAL_RUNS_L5", "cl5", 41, 51, "POSTERIOR_SOURCES_V2_EXTENDED.json")
        t = W2["tally"]
        self.assertEqual([r[0] for r in rows], t["pH_pos_hits"])
        self.assertEqual([r[1] for r in rows], t["pH_neg_hits"])
        self.assertEqual([r[3] for r in rows], t["C_pot_QH_pos"])
        self.assertEqual([r[4] for r in rows], t["C_pot_QH_neg"])
        self.assertEqual(sum(1 for r in rows if r[0] > r[1]), t["EP1_hits"])
        self.assertEqual(t["scored_admissible_sources"], 6)
        self.assertEqual(t["EP1_hits"], 6)
        self.assertEqual(t["EP1_misses"], [])
        self.assertEqual(t["excluded_at_floor_or_ceiling"], 1)
        self.assertEqual(t["pH_pos_hits"], [9, 17, 1, 1, 10, 7])
        self.assertEqual(t["pH_neg_hits"], [0, 0, 0, 0, 0, 0])
        d = W2["decision"]
        self.assertTrue(d["closes_pending_route_b"])
        self.assertTrue(d["clauses"]["3_EP1_k_of_k_with_k_at_least_6"])
        self.assertEqual(t["EP1_hits"], t["scored_admissible_sources"])

    def test_combined_record_and_nulls(self):
        c = L["combined"]
        n1 = W1["tally"]["scored_admissible_sources"]
        n2 = W2["tally"]["scored_admissible_sources"] if W2.get("status") == "OK" else 0
        h1 = W1["tally"]["EP1_hits"]
        h2 = W2["tally"]["EP1_hits"] if W2.get("status") == "OK" else 0
        self.assertEqual(c["sources"], n1 + n2)
        self.assertEqual(c["EP1_hits"], h1 + h2)
        self.assertEqual(c["sources"], 12)
        self.assertEqual(c["EP1_hits"], 11)
        self.assertEqual(c["EP1_misses"], ["W1:P05"])
        self.assertEqual(Fraction(c["record_level_null_observed_or_better"]), A.binomial_tail(h1 + h2, n1 + n2))
        self.assertEqual(Fraction(c["procedure_level_null_two_windows"]), Fraction(70, 4096))
        self.assertEqual(A.binomial_tail(6, 6), Fraction(1, 64))
        self.assertEqual(A.binomial_tail(5, 6), Fraction(7, 64))
        self.assertEqual(A.binomial_tail(11, 12), Fraction(13, 4096))
        ns = c["NULL_RANDOM_SIGN_combined"]
        self.assertTrue(ns["beaten"])
        self.assertEqual(ns["seeds"], 200)

    def test_ep4_records(self):
        e = L["EP4_developmental_potential"]
        self.assertTrue(e["parent_seven_sources_post_hoc"]["available"])
        self.assertEqual(e["parent_seven_sources_post_hoc"]["EP4_hits"], 7)
        self.assertEqual(e["parent_seven_sources_post_hoc"]["of"], 7)
        self.assertTrue(e["parent_seven_sources_post_hoc"]["post_hoc"])
        self.assertEqual(e["window_1_post_hoc"], {"hits": 6, "of": 6})
        self.assertEqual(e["window_2_prospective"], {"hits": 6, "of": 6})

    def test_final_decision_is_consistent_with_the_windows(self):
        d = L["decision"]
        w1c = W1["decision"]["closes_pending_route_b"]
        w2c = W2.get("decision", {}).get("closes_pending_route_b", False)
        self.assertEqual(d["closes_pending_route_b"], bool(w1c or w2c))
        self.assertFalse(w1c)
        if d["closes_pending_route_b"]:
            self.assertEqual(d["closing_window"], "W2")
        else:
            self.assertIsNotNone(d["attribution"])

    def test_routes_agree_on_row_l(self):
        agree = ORACLE["agreement"]["row_L"]
        for wid in ("W1", "W2"):
            self.assertTrue(agree[wid]["present_in_both"])
            for key, val in agree[wid].items():
                self.assertTrue(val, "%s %s" % (wid, key))
        self.assertTrue(agree["combined_EP1_hits"])
        self.assertTrue(agree["combined_sources"])


class Reconciliation(unittest.TestCase):
    def test_shape_and_rows(self):
        self.assertEqual(RECON["schema"], "GMI_ISSUE_RECONCILIATION_V2")
        self.assertEqual(RECON["issue"], 833)
        self.assertFalse(RECON["issue_body_edited_by_this_package"])
        frozen_old = set(r["old"] for r in ROWS["rows"].values())
        seen = []
        for rep in RECON["replacements"]:
            self.assertIn(rep["old"], frozen_old)
            self.assertTrue(rep["new"].startswith("- [x] " + rep["old"][6:] + " — ✅ gmi-833-kl-revival-v1 "))
            seen.append(rep["row"])
        for row in RECON["rows_deliberately_left_open"]:
            self.assertIn(row["old"], frozen_old)
            seen.append(row["row"])
        for row in RECON.get("rows_already_closed_by_prior_packages", []):
            self.assertEqual(row["row"], "ROW_K")
            self.assertIn(row["old"], frozen_old)
            self.assertTrue(row["current_body_line"].startswith("- [x] "))
            seen.append(row["row"])
        self.assertEqual(sorted(seen), ["ROW_K", "ROW_L"])
        self.assertEqual([r["row"] for r in RECON["replacements"]], ["ROW_L"])
        self.assertEqual(RECON["routes_agree"], ORACLE["agreement"]["all"])

    def test_row_k_already_closed_by_the_merged_k_package(self):
        closed = dict((r["row"], r) for r in RECON.get("rows_already_closed_by_prior_packages", []))
        self.assertIn("ROW_K", closed)
        line = closed["ROW_K"]["current_body_line"]
        self.assertIn("- [x] Test predictor on real trained systems.", line)
        self.assertIn("#1106", line)
        self.assertTrue(all(r["row"] != "ROW_K" for r in RECON["replacements"]))
        self.assertTrue(all(r["row"] != "ROW_K" for r in RECON["rows_deliberately_left_open"]))

    def test_row_l_line_quotes_window_1_verbatim(self):
        entries = dict((r["row"], r) for r in RECON["replacements"] + RECON["rows_deliberately_left_open"])
        text = entries["ROW_L"].get("new") or entries["ROW_L"].get("reason")
        t1 = W1["tally"]
        self.assertIn("window 1 EP-1 %d/%d" % (t1["EP1_hits"], t1["scored_admissible_sources"]), text)
        self.assertIn("P05", text)
        self.assertIn("0/24", text)
        if "ROW_L" in dict((r["row"], r) for r in RECON["replacements"]):
            self.assertIn("window 2", text)
            self.assertIn("combined record %d/%d" % (L["combined"]["EP1_hits"], L["combined"]["sources"]), text)

    def test_forbidden_promotions_include_the_amendment(self):
        for name in ("POTENTIAL_ORDERING_CLOSES_EVOLVABILITY_ROW", "THIRD_WINDOW_OPENED",
                     "FIRST_WINDOW_RESCORED_OR_DROPPED", "FOURTH_REGISTRATION_LAW", "SECTION_L_COMPLETE"):
            self.assertIn(name, RECON["forbidden_promotions"])
            self.assertIn(name, MANIFEST["forbidden_promotions"])


class Manifest(unittest.TestCase):
    def test_package_digests(self):
        for rel, ent in MANIFEST["package_files"].items():
            with open(os.path.join(HERE, rel), "rb") as h:
                self.assertEqual(hashlib.sha256(h.read()).hexdigest(), ent["sha256"], rel)
        self.assertNotIn("MANIFEST_V1.json", MANIFEST["package_files"])
        for name in ("FREEZE_V1.md", "FREEZE_V1_AMENDMENT_1.md", "RESULT_V1.json", "ORACLE_RESULT_V1.json",
                     "POSTERIOR_SOURCES_V1.json", "KL_REVIVAL_THEOREMS_V1.md", "CORE.md"):
            self.assertIn(name, MANIFEST["package_files"])

    def test_parent_pins(self):
        self.assertEqual(MANIFEST["freeze_commit"], A.FREEZE_COMMIT)
        self.assertEqual(MANIFEST["source_main"], A.SOURCE_MAIN)
        for pin in MANIFEST["parent_pins"]:
            with open(os.path.join(REPO, pin["path"]), "rb") as h:
                data = h.read()
            self.assertEqual(hashlib.sha256(data).hexdigest(), pin["sha256"], pin["path"])
            self.assertEqual(A.git_blob_sha(data), pin["blob_sha"], pin["path"])
        paths = set(p["path"] for p in MANIFEST["parent_pins"])
        self.assertIn("research/gmi-833-capability-predictor-v1/capability_predictor_v1.py", paths)


class FreezeCustody(unittest.TestCase):
    def test_freeze_files_unchanged_since_first_commit(self):
        for name in ("FREEZE_V1.md", "FREEZE_ROWS_V1.json", "FREEZE_V1_AMENDMENT_1.md"):
            p = subprocess.run(["git", "log", "--reverse", "--format=%H", "--", A.PKG + "/" + name],
                               cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            lines = [ln for ln in p.stdout.decode().split("\n") if ln.strip()]
            if p.returncode != 0 or not lines:
                self.skipTest("no history in this checkout")
            then = subprocess.run(["git", "show", "%s:%s/%s" % (lines[0], A.PKG, name)], cwd=REPO,
                                  stdout=subprocess.PIPE).stdout
            with open(os.path.join(HERE, name), "rb") as h:
                now = h.read()
            self.assertEqual(then, now, name)

    def test_frozen_rows_match_the_freeze_text(self):
        with open(os.path.join(HERE, "FREEZE_V1.md")) as h:
            freeze = h.read()
        for row in ROWS["rows"].values():
            self.assertIn(row["old"], freeze)
            self.assertEqual(hashlib.sha256(row["old"].encode("utf-8")).hexdigest(), row["old_sha256"])
        self.assertIn("No neighboring row is earned here.", freeze)


if __name__ == "__main__":
    unittest.main()
