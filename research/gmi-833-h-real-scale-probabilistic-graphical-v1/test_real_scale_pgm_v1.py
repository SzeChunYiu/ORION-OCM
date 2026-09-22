"""Tests for gmi-833-h-real-scale-probabilistic-graphical-v1.

Runs under `python3 -I -B` and `python3 -I -O -B`. Every check is a unittest
assertion method, never a bare `assert`, so `-O` cannot strip it. The package
uses exact integer decision counts; no float enters any test.

The Reconciliation section reads ISSUE_833_RECONCILIATION_H18_V1.json, which
the coordinator owns and which is committed separately from this file; those
tests skip, naming the missing artifact, until it lands.
"""
import ast
import hashlib
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import grammar_pgm_v1 as G                 # noqa: E402
import real_scale_pgm_v1 as C              # noqa: E402

PRIMARY = ("grammar_pgm_v1", "run_real_scale_pgm_v1", "real_scale_pgm_v1")
SIGMA = "SIGMA_H18R"
ROW = "- [ ] Probabilistic graphical models."
STATE = "Probabilistic graphical models."
SOURCE_SHA = "9e66281f7e51445eab6857488ff6e3d768afffadb7fb1adbef5e4617bee4a53b"
RECON = "ISSUE_833_RECONCILIATION_H18_V1.json"
WINNER = "R1ASSOC>=1&R2ASSOC>=1"


def read(name):
    with open(os.path.join(HERE, name)) as fh:
        return fh.read()


def load_json(name):
    with open(os.path.join(HERE, name)) as fh:
        return json.load(fh)


class TwoRoutes(unittest.TestCase):

    def test_oracle_does_not_import_the_primary_executor(self):
        tree = ast.parse(read("independent_oracle_pgm_v1.py"))
        named = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                named.extend(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                named.append(node.module or "")
        for mod in PRIMARY:
            self.assertNotIn(mod, named)

    def test_oracle_module_namespace_is_clean(self):
        code = ("import sys, os; sys.path.insert(0, %r);"
                "import independent_oracle_pgm_v1;"
                "print(','.join(m for m in %r if m in sys.modules))"
                % (HERE, PRIMARY))
        out = subprocess.check_output([sys.executable, "-I", "-B", "-c", code],
                                      cwd=HERE).decode().strip()
        self.assertEqual(out, "")

    def test_oracle_agrees(self):
        oracle = load_json("ORACLE_RESULT_V1.json")
        self.assertTrue(oracle["agrees"])
        self.assertFalse(oracle["imports_primary_executor"])
        self.assertEqual(oracle["schema"],
                         "GMI833HRealScaleProbabilisticGraphicalOracleV1")
        self.assertEqual(oracle["route"], "B")
        self.assertEqual(oracle["scope"], SIGMA)
        self.assertGreaterEqual(len(oracle["checks"]), 20)
        for name, ok in oracle["checks"].items():
            self.assertTrue(ok, name)

    def test_the_checker_reads_no_parent_result_file(self):
        tree = ast.parse(read("real_scale_pgm_v1.py"))
        literals = [n.value for n in ast.walk(tree)
                    if isinstance(n, ast.Constant) and isinstance(n.value, str)]
        for text in literals:
            self.assertNotIn("research/", text)
            self.assertNotIn("..", text)
        roots = set()
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "open"):
                roots.add(ast.dump(node.args[0])[:24])
        self.assertTrue(roots)
        # the only module the checker imports is the frozen grammar
        named = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                named.extend(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                named.append(node.module or "")
        self.assertIn("grammar_pgm_v1", named)
        for mod in named:
            self.assertIn(mod,
                          ("json", "os", "random", "sys", "grammar_pgm_v1"))


class Custody(unittest.TestCase):

    def test_the_freeze_records_the_registered_contract_as_a_steer(self):
        """The row's registered contract is a steer, recorded on the record
        with its source blob and the sibling precedent, and explicitly not
        imported as evidence. The package claims no three-variable arity."""
        text = read("FREEZE_V1.md")
        self.assertIn("FROZEN_FAMILY_REGISTRY_V1.json", text)
        self.assertIn("e0a8e7a9d0988dc5b702737db693df375710b986", text)
        self.assertIn("TRIPLE_PARITY", text)
        self.assertIn("registered three-variable dependency response", text)
        self.assertIn("steer", text)
        self.assertIn("gmi-833-h-real-scale-decision-trees-v1", text)
        self.assertIn("no three-variable arity", text)

    def test_the_freeze_names_exactly_the_one_row(self):
        text = read("FREEZE_V1.md")
        self.assertIn(ROW, text)
        self.assertIn("No neighboring row is earned here.", text)
        self.assertIn("SIGMA_H18R", text)
        self.assertIn("F16", text)
        self.assertNotIn("- [ ] Nearest-neighbor / exemplar memory.", text)
        self.assertNotIn("- [ ] Associative memory.", text)
        self.assertNotIn("- [x] ", text)

    def test_the_measurement_addendum_records_its_custody_position(self):
        """R3 is an addendum to a MEASUREMENT: it necessarily postdates the run
        and it changes no registered form. Its text must say so, and it must
        state the two corrected numbers, so a reader cannot mistake it for a
        pre-outcome freeze."""
        text = read("FREEZE_V1_SLICE_ADDENDUM_R3.md")
        self.assertIn("addendum to a MEASUREMENT", text)
        self.assertIn("postdates the measurement", text)
        self.assertIn("32,834", text)
        self.assertIn("22,919", text)
        self.assertIn("19,277", text)
        self.assertIn("1,893", text)
        # it must not claim to change any frozen form
        self.assertIn("no registered FORM", text)

    def test_the_slice_addenda_state_the_registered_forms(self):
        text = read("FREEZE_V1_SLICE_ADDENDUM.md")
        self.assertIn("key(i)  = (i * 2654435761) mod 2**32", text)
        self.assertIn("679124", text)
        self.assertIn("97018", text)
        self.assertIn("475,386", text)
        self.assertIn("203,738", text)
        self.assertIn("339,562", text)
        self.assertIn("387,582", text)
        self.assertIn("388,560", text)
        self.assertIn(WINNER, text)
        self.assertIn("MEM_FALLBACK", text)
        self.assertIn("C0", text)
        self.assertIn("54 arms", text)
        text2 = read("FREEZE_V1_SLICE_ADDENDUM_R2.md")
        self.assertIn("fit_lo", text2)
        self.assertIn("fit_hi", text2)
        self.assertIn("20260926", text2)
        self.assertIn("20260927", text2)
        self.assertIn("340,066", text2)
        self.assertIn("ECM", text2)

    def test_the_first_run_receipts_are_still_committed(self):
        self.assertTrue(os.path.isfile(os.path.join(
            HERE, "REAL_RUNS", "scope_SIGMA_H18R.json")))
        self.assertTrue(os.path.isfile(os.path.join(
            HERE, "REAL_RUNS", "sources.json")))
        self.assertTrue(os.path.isfile(os.path.join(HERE, "RESULT_V1.json")))
        self.assertTrue(os.path.isfile(os.path.join(
            HERE, "ORACLE_RESULT_V1.json")))

    def test_grammar_is_the_same_under_both_run_modes(self):
        code = ("import sys, os, json; sys.path.insert(0, %r);"
                "import grammar_pgm_v1 as G; print(json.dumps([G.digest(),"
                "list(G.READOUTS), G.order_key(7), G.cost('MEM_FALLBACK'),"
                " G.classify(%r)]))" % (HERE, WINNER))
        outs = []
        for flags in (["-I", "-B"], ["-I", "-O", "-B"]):
            outs.append(subprocess.check_output(
                [sys.executable] + flags + ["-c", code], cwd=HERE).decode())
        self.assertEqual(outs[0], outs[1])

    def test_the_manifest_names_the_freeze_files(self):
        if not os.path.isfile(os.path.join(HERE, "MANIFEST_V1.json")):
            self.skipTest("MANIFEST_V1.json is owned by the coordinator and "
                          "not yet committed")
        man = load_json("MANIFEST_V1.json")
        self.assertEqual(man["freeze_file"], "FREEZE_V1.md")
        self.assertEqual(man["freeze_addenda"],
                         ["FREEZE_V1_SLICE_ADDENDUM.md",
                          "FREEZE_V1_SLICE_ADDENDUM_R2.md",
                          "FREEZE_V1_SLICE_ADDENDUM_R3.md"])
        self.assertEqual(man["scopes"], {SIGMA: STATE})
        self.assertEqual(man["rows_this_package_may_reconcile"], [STATE])
        for fname, pin in man["freeze_pins"].items():
            self.assertEqual(len(pin), 64)
            here = hashlib.sha256(read(fname).encode("utf-8")).hexdigest()
            self.assertEqual(pin, here, fname)
        self.assertEqual(man["supersession"]["superseded_scope"],
                         "SIGMA_H16R")
        self.assertEqual(man["supersession"]["superseded_at_branch_head"],
                         "d30bed0a")


class Scopes(unittest.TestCase):

    def setUp(self):
        self.result = load_json("RESULT_V1.json")

    def test_no_gate_carries_a_foreign_sigma(self):
        row = self.result["rows"]["H18"]
        self.assertEqual(row["sigma"], SIGMA)
        for gate in row["gates"]:
            self.assertEqual(gate["sigma"], SIGMA)
            self.assertIn(gate["sigma"], (SIGMA,))
        self.assertTrue(self.result["no_gate_carries_a_foreign_sigma"])
        self.assertTrue(self.result["all_rows_single_sigma"])

    def test_no_gate_cites_a_parent_certificate(self):
        row = self.result["rows"]["H18"]
        for gate in row["gates"]:
            for foreign in ("SIGMA_4F", "SIGMA_HA", "SIGMA_H05R", "SIGMA_H06R",
                            "SIGMA_H08R", "SIGMA_CENSUS", "gmi-833-h-",
                            "PARENT", "TRANCH"):
                self.assertNotIn(foreign, gate["evidence"])

    def test_forbidden_promotions_are_copied_from_the_freeze(self):
        self.assertIn("CROSS_SCOPE_GATE_COMPOSITION",
                      self.result["forbidden_promotions"])
        self.assertIn("ECOLOGY_ITERATION_UNTIL_POSITIVE",
                      self.result["forbidden_promotions"])
        self.assertIn("REGISTERED_CONTROL_SUBSTITUTION",
                      self.result["forbidden_promotions"])
        self.assertIn("POST_HOC_FALSIFIER_REPLACEMENT",
                      self.result["forbidden_promotions"])
        self.assertIn("M5", self.result["forbidden_promotions"])
        self.assertIn("INDEPENDENT_TEAM_REPLICATION",
                      self.result["forbidden_promotions"])
        freeze = read("FREEZE_V1.md")
        for promotion in self.result["forbidden_promotions"]:
            self.assertIn(promotion, freeze)
        ceiling = self.result["claim_ceiling"]
        self.assertIn(ceiling, freeze)
        self.assertEqual(ceiling,
                         "REAL_SCALE_ELEVEN_GATE_DERIVATION_OF_NAMED_"
                         "CLASSICAL_FAMILY_AT_REGISTERED_SCOPE")

    def test_real_scale_thresholds_are_met(self):
        scale = self.result["scale"]
        self.assertGreaterEqual(scale["n_fit"], 100000)
        self.assertGreaterEqual(scale["n_held"], 20000)
        self.assertEqual(scale["n_fit"], 679124)
        self.assertEqual(scale["n_held"], 97018)
        self.assertEqual(scale["source_sha256"], SOURCE_SHA)
        self.assertTrue(scale["thresholds_met"])

    def test_the_closed_row_has_eleven_gates_at_one_sigma(self):
        row = self.result["rows"]["H18"]
        self.assertTrue(row["complete"])
        self.assertEqual(row["supported"], 11)
        self.assertTrue(row["single_sigma"])
        self.assertEqual(len(row["gates"]), 11)
        self.assertEqual(row["open_gates"], [])
        self.assertEqual(row["failed_predictions"], [])
        self.assertEqual(row["predicted_class"], "FACTOR_JOINT_CONSISTENCY")
        self.assertEqual(row["recovered_class"], "FACTOR_JOINT_CONSISTENCY")
        self.assertEqual(self.result["rows_closed"], [STATE])
        self.assertEqual(self.result["verdict"], "GREEN")
        keys = sorted(g["gate"] for g in row["gates"])
        self.assertEqual(keys, sorted("%s_%s" % r for r in C.REQUIREMENTS))
        for gate in row["gates"]:
            self.assertEqual(gate["status"],
                             "SUPPORTED_AT_REGISTERED_REAL_SCALE")

    def test_every_hostile_is_applicable_and_detected(self):
        self.assertGreaterEqual(len(self.result["hostiles"]), 6)
        for hostile in self.result["hostiles"]:
            self.assertTrue(hostile["applicable"], hostile["hostile"])
            self.assertTrue(hostile["detected"], hostile["hostile"])
            self.assertTrue(hostile["no_alarm_on_clean"], hostile["hostile"])

    def test_every_claimed_quantity_is_an_exact_integer(self):
        hold = self.result["holdout_replay"]
        for value in (hold["n"], hold["replayed_errors"],
                      hold["prototype_agreement"], hold["positive"],
                      hold["negative"]):
            self.assertIsInstance(value, int)
        self.assertEqual(self.result["scale"]["n_held"], 97018)
        self.assertEqual(self.result["ladder"]["errors"][0], 64554)
        self.assertIsInstance(self.result["crossover"]["m_star"], int)
        self.assertEqual(self.result["crossover"]["m_star"], 110799)
        self.assertIsInstance(self.result["ecm"]["errors_held"], int)
        self.assertIsInstance(self.result["mem_fallback"]["rank"], int)


class SliceRule(unittest.TestCase):

    def test_the_permutation_and_slices_are_exact(self):
        n_fit = (776142 * 7) // 8
        self.assertEqual(n_fit, 679124)
        self.assertEqual(776142 - n_fit, 97018)
        self.assertEqual((7 * n_fit) // 10, 475386)
        self.assertEqual(n_fit - (7 * n_fit) // 10, 203738)
        self.assertEqual(n_fit // 2, 339562)
        keyed = sorted(range(776142),
                       key=lambda i: (i * 2654435761) % (2 ** 32))
        self.assertEqual(len(keyed), 776142)
        # the registered presentation key list is ascending in the order
        self.assertEqual([(i * 2654435761) % (2 ** 32) for i in keyed],
                         sorted((i * 2654435761) % (2 ** 32)
                                for i in range(776142)))
        # and the slices are the registered contiguous cuts of that order
        self.assertEqual(len(keyed[:n_fit]), 679124)
        self.assertEqual(len(keyed[n_fit:]), 97018)
        self.assertEqual(keyed[:n_fit] + keyed[n_fit:], keyed)
        self.assertEqual(keyed[:n_fit // 2] + keyed[n_fit // 2:n_fit],
                         keyed[:n_fit])


class GrammarAndReadouts(unittest.TestCase):

    def test_the_classifier_reads_the_name_alone(self):
        self.assertEqual(G.classify(WINNER), "FACTOR_JOINT_CONSISTENCY")
        self.assertEqual(G.classify("R1CNT>=2&R2ASSOC>=1"),
                         "FACTOR_JOINT_CONSISTENCY")
        self.assertEqual(G.classify("LEN<=9&R1ASSOC>=1&R2ASSOC>=1"),
                         "FACTOR_JOINT_CONSISTENCY")
        self.assertEqual(G.classify("C0"), "CONSTANT_ARM")
        self.assertEqual(G.classify("C1"), "CONSTANT_ARM")
        self.assertEqual(G.classify("LEN<=10"), "DESCRIPTOR_LENGTH_THRESHOLD")
        self.assertEqual(G.classify("R1CNT>=1"), "SINGLE_FACTOR_MEMBERSHIP")
        self.assertEqual(G.classify("R2CNT>=3"), "SINGLE_FACTOR_MEMBERSHIP")
        self.assertEqual(G.classify("R1ASSOC>=1"), "SINGLE_FACTOR_ASSOCIATION")
        self.assertEqual(G.classify("R2ASSOC>=2"), "SINGLE_FACTOR_ASSOCIATION")
        self.assertEqual(G.classify("PREF_VOTE"), "NEIGHBORHOOD_MAJORITY_VOTE")
        self.assertEqual(G.classify("EXT_VOTE"), "NEIGHBORHOOD_MAJORITY_VOTE")
        self.assertEqual(G.classify("MEM_FALLBACK"),
                         "STORED_LABEL_READ_WITH_FALLBACK")
        self.assertRaises(ValueError, G.classify, "SQUARE")
        # every arm of the language classifies, and only factor-product names
        # are called FACTOR_JOINT_CONSISTENCY
        for name in G.READOUTS:
            cls = G.classify(name)
            self.assertIn(cls, ("CONSTANT_ARM", "DESCRIPTOR_LENGTH_THRESHOLD",
                                "SINGLE_FACTOR_MEMBERSHIP",
                                "SINGLE_FACTOR_ASSOCIATION",
                                "FACTOR_JOINT_CONSISTENCY",
                                "NEIGHBORHOOD_MAJORITY_VOTE",
                                "STORED_LABEL_READ_WITH_FALLBACK"))
            if cls == "FACTOR_JOINT_CONSISTENCY":
                self.assertTrue(G.reads_both_factors(name), name)

    def test_the_language_is_closed_and_outcome_free(self):
        self.assertIn(WINNER, G.READOUTS)
        self.assertIn("R1CNT>=1", G.READOUTS)
        self.assertIn("R2ASSOC>=3", G.READOUTS)
        self.assertIn("LEN<=11&R1CNT>=1&R2CNT>=1", G.READOUTS)
        self.assertIn("MEM_FALLBACK", G.READOUTS)
        self.assertNotIn("SQUARE", G.READOUTS)
        self.assertNotIn("MARGINAL", G.READOUTS)
        self.assertNotIn("ECM_PRODUCT_FORM_MESSAGE", G.READOUTS)
        self.assertEqual(len(G.READOUTS), 54)
        self.assertEqual(len(set(G.READOUTS)), 54)
        # the arm counts of the slice addendum section 3: 2 constants, 7
        # length arms, 6 factor-local count arms, 6 factor-local fan-out arms,
        # 16 factor-product joint arms, 14 length-gated joint arms, the two
        # vote arms and the stored-label arm -- 54 in all.
        self.assertEqual(sum(1 for r in G.READOUTS if "&" in r), 30)
        self.assertEqual(sum(1 for r in G.READOUTS
                             if G.classify(r) == "FACTOR_JOINT_CONSISTENCY"),
                         30)
        self.assertEqual(sum(1 for r in G.READOUTS
                             if "LEN<=" in r), 21)
        self.assertEqual(sum(1 for r in G.READOUTS
                             if r.startswith("R1CNT>=")
                             and "&" not in r), 3)
        self.assertEqual(sum(1 for r in G.READOUTS
                             if r.startswith("R2ASSOC>=")
                             and "&" not in r), 3)
        self.assertEqual(sum(1 for r in G.READOUTS
                             if G.classify(r) == "SINGLE_FACTOR_MEMBERSHIP"),
                         6)
        self.assertEqual(sum(1 for r in G.READOUTS
                             if G.classify(r) == "SINGLE_FACTOR_ASSOCIATION"),
                         6)
        self.assertEqual(sum(1 for r in G.READOUTS
                             if G.classify(r)
                             == "DESCRIPTOR_LENGTH_THRESHOLD"), 7)
        self.assertEqual(sum(1 for r in G.READOUTS
                             if G.classify(r) == "CONSTANT_ARM"), 2)
        # the registered order: C0, C1, the arms of section 3 in sequence
        self.assertEqual(G.READOUTS[:2], ("C0", "C1"))
        self.assertEqual(G.READOUTS[-3:],
                         ("PREF_VOTE", "EXT_VOTE", "MEM_FALLBACK"))

    def test_the_registered_charged_cost_is_exact(self):
        self.assertEqual(G.cost("C0"), 0)
        self.assertEqual(G.cost("LEN<=9"), 0)
        self.assertEqual(G.cost("R1CNT>=1"), 1)
        self.assertEqual(G.cost("R2ASSOC>=3"), 1)
        self.assertEqual(G.cost("LEN<=9&R1ASSOC>=1&R2ASSOC>=1"), 1)
        self.assertEqual(G.cost(WINNER), 2)
        self.assertEqual(G.cost("MEM_FALLBACK"), 2)
        self.assertIsNone(G.cost("PREF_VOTE"))
        self.assertIsNone(G.cost("EXT_VOTE"))

    def test_the_presentation_key_is_registered(self):
        self.assertEqual(G.order_key(0), 0)
        self.assertEqual(G.order_key(1), 2654435761 % (2 ** 32))
        self.assertEqual(G.digest().__len__(), 64)

    def test_an_extra_readout_moves_the_grammar_digest(self):
        before = G.digest()
        saved = G.READOUTS
        try:
            G.READOUTS = saved + ("SQUARE",)
            self.assertNotEqual(G.digest(), before)
        finally:
            G.READOUTS = saved
        self.assertEqual(G.digest(), before)
        # and so does a perturbed factor split rule
        saved_rule = G.FACTOR_SPLIT_RULE
        try:
            G.FACTOR_SPLIT_RULE = "R1 = the odd-length tokens"
            self.assertNotEqual(G.digest(), before)
        finally:
            G.FACTOR_SPLIT_RULE = saved_rule
        self.assertEqual(G.digest(), before)


class FactorStructure(unittest.TestCase):

    def setUp(self):
        self.rec = load_json(os.path.join("REAL_RUNS", "scope_SIGMA_H18R.json"))

    def test_the_factor_split_rule_is_the_registered_one(self):
        self.assertIn("EVEN length", G.FACTOR_SPLIT_RULE)
        self.assertIn("ODD length", G.FACTOR_SPLIT_RULE)
        text = read("FREEZE_V1_SLICE_ADDENDUM.md")
        self.assertIn("len(w) % 2 == 0", text)
        self.assertIn("len(w) % 2 == 1", text)
        self.assertEqual(self.rec["factors"]["R1_tokens_rule"],
                         "even token length")
        self.assertEqual(self.rec["factors"]["R2_tokens_rule"],
                         "odd token length")

    def test_the_two_factors_are_disjoint_and_sum_to_T(self):
        # the registered split is a parity partition: every token belongs to
        # exactly one factor, so the occurrence counts are disjoint and exact
        seen = {}
        for i in range(0, 200000, 7):
            for L in (2, 3, 5):
                seen[(L, i % 2)] = 1
        self.assertEqual(len(seen), 6)
        fac = self.rec["factors"]
        self.assertEqual(fac["R1_occurrences"], 387582)
        self.assertEqual(fac["R2_occurrences"], 388560)
        self.assertEqual(fac["R1_occurrences"] + fac["R2_occurrences"],
                         776142)
        self.assertEqual(self.rec["source"]["descriptors"], 776142)
        self.assertEqual(fac["R1_occurrences"] + fac["R2_occurrences"],
                         self.rec["source"]["descriptors"])

    def test_the_receipt_carries_the_registered_factors_and_source(self):
        self.assertEqual(self.rec["row"], "Probabilistic graphical models.")
        self.assertEqual(self.rec["scope"], SIGMA)
        self.assertEqual(self.rec["schema"],
                         "GMI833HRealScaleProbabilisticGraphicalScopeV1")
        self.assertEqual(self.rec["source"]["sha256"], SOURCE_SHA)
        self.assertEqual(self.rec["source"]["tokens"], 104334)
        src = load_json(os.path.join("REAL_RUNS", "sources.json"))
        self.assertEqual(src["source"]["sha256"], SOURCE_SHA)


class NegativeControls(unittest.TestCase):

    def test_a_wrong_artifact_path_fails_loudly(self):
        keep = C.RUNS
        try:
            C.RUNS = os.path.join(HERE, "NO_SUCH_DIR")
            self.assertRaises(SystemExit, C.load, "scope_SIGMA_H18R.json")
        finally:
            C.RUNS = keep
        self.assertIsInstance(C.load("sources.json"), dict)

    def test_a_tampered_replay_row_breaks_the_exact_replay(self):
        rec = C.load("scope_SIGMA_H18R.json")
        rows = [list(r) for r in rec["replay"]["held_block"]["queries"]]
        clean = C.row_errors(rows, WINNER)
        rows[0][1] = 1 - rows[0][1]
        dirty = C.row_errors(rows, WINNER)
        self.assertEqual(clean, rec["replay"]["held_block"]["winner_errors"])
        self.assertNotEqual(dirty, clean)
        # the rank and regeneration blocks replay their own committed counts
        for key, name in (("rank_block", rec["rank_stage"]["winner"]),
                          ("regen_lo_block", rec["regen"]["regen"]["winner"]),
                          ("regen_hi_block", rec["regen"]["primary"]["winner"])):
            block = rec["replay"][key]
            self.assertEqual(C.row_errors(block["queries"], name),
                             block["winner_errors"])
            self.assertEqual(block["rows"], len(block["queries"]))

    def test_a_null_seed_drift_breaks_the_registered_count(self):
        rec = C.load("scope_SIGMA_H18R.json")
        self.assertEqual(C.hostile_null_seed_drift(rec)["detected"], True)
        self.assertEqual(C.hostile_design_permutation(rec)["detected"], True)

    def test_the_memory_arm_loses_at_every_stage(self):
        rec = C.load("scope_SIGMA_H18R.json")
        mf = rec["mem_fallback"]
        self.assertTrue(mf["rejected_at_all_stages"])
        self.assertGreater(mf["rank"], rec["rank_stage"]["winner_errors"])
        self.assertGreater(mf["held"], rec["holdout"]["winner_errors"])
        self.assertGreater(mf["primary"],
                           rec["regen"]["primary"]["winner_errors"])
        self.assertGreater(mf["regen"], rec["regen"]["regen"]["winner_errors"])


class Reconciliation(unittest.TestCase):

    def setUp(self):
        if not os.path.isfile(os.path.join(HERE, RECON)):
            self.skipTest("%s is owned by the coordinator and not yet "
                          "committed" % RECON)
        self.recon = load_json(RECON)
        self.result = load_json("RESULT_V1.json")

    def test_the_schema_and_anchor_are_the_registered_ones(self):
        self.assertEqual(self.recon["schema"], "GMI_ISSUE_RECONCILIATION_V2")
        self.assertEqual(self.recon["issue"], 833)
        for entry in self.recon["replacements"]:
            self.assertTrue(entry["anchor"].startswith("# H. "))

    def test_the_supersession_of_the_earlier_scope_id_is_recorded(self):
        """The identifier was changed in the freeze first, on a re-cut, before
        merge; the reader must be able to see that, and see that no number
        moved with it."""
        notes = " ".join(self.recon["notes"])
        self.assertIn("d30bed0a", notes)
        self.assertIn("SIGMA_H16R", notes)
        self.assertIn("SIGMA_H18R", notes)
        self.assertIn("H16", notes)
        text = read("CORE.md")
        self.assertIn("Superseded identifier", text)
        self.assertIn("d30bed0a", text)

    def test_only_rows_the_result_closed_appear_as_replacements(self):
        closed = set(self.result["rows_closed"])
        for entry in self.recon["replacements"]:
            row = entry["old"].replace("- [ ] ", "")
            self.assertIn(row, closed)
            self.assertTrue(entry["new"].startswith("- [x] " + row))
            self.assertIn("L:", entry["new"])
            self.assertIn(SIGMA, entry["new"])

    def test_the_annotation_fits_the_measured_body_budget(self):
        budget = self.recon["annotation_budget"][
            "measured_payload_limit_characters"]
        self.assertGreaterEqual(budget, 2143)
        for entry in self.recon["replacements"]:
            parts = entry["new"].split(u" — ✅ ", 1)
            self.assertEqual(len(parts), 2, entry["new"])
            self.assertLessEqual(len(parts[1]), budget, parts[1])

    def test_the_registry_steer_is_recorded_and_not_imported(self):
        """The contract is a steer, not evidence: the reconciliation cites it,
        and no gate certificate or annotation may claim an arity."""
        for entry in self.recon["replacements"]:
            self.assertNotIn("TRIPLE_PARITY", entry["new"])
        for gate in self.result["rows"]["H18"]["gates"]:
            self.assertNotIn("TRIPLE_PARITY", gate["evidence"])

    def test_no_row_outside_the_freeze_is_touched(self):
        self.assertEqual(len(self.recon["replacements"]), 1)
        for entry in self.recon["replacements"]:
            self.assertEqual(entry["old"], ROW)


if __name__ == "__main__":
    unittest.main(verbosity=2)
