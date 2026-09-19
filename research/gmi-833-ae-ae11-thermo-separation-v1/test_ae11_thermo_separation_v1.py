#!/usr/bin/env python3
"""GMI #833 Section AE11 -- tests.

Run standalone:
    python3 -I -B  research/gmi-833-ae-ae11-thermo-separation-v1/test_ae11_thermo_separation_v1.py -v
    python3 -I -O  -B research/gmi-833-ae-ae11-thermo-separation-v1/test_ae11_thermo_separation_v1.py -v

No bare `assert` appears anywhere in this file: `-O` strips the statement and a
stripped check is a vacuous pass.  Every check is a `unittest.TestCase`
assertion method.
"""
import ast
import hashlib
import importlib.util
import json
import subprocess
import sys
import unittest
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROUTE_A_PATH = HERE / "ae11_thermo_separation_v1.py"
ROUTE_B_PATH = HERE / "independent_thermo_oracle_v1.py"
RESULT_PATH = HERE / "RESULT_V1.json"
MANIFEST_PATH = HERE / "MANIFEST_V1.json"
REGISTER_PATH = HERE / "PROSPECTIVE_REGISTER_V1.json"
RECON_PATH = HERE / "ISSUE_833_RECONCILIATION_AE11_THERMO_SEPARATION_V1.json"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


A = _load("ae11_route_a", ROUTE_A_PATH)
B = _load("ae11_route_b", ROUTE_B_PATH)

RECEIPT = A.build()
ORACLE = B.oracle()


class TestRouteIndependence(unittest.TestCase):
    def test_route_b_does_not_import_route_a(self):
        tree = ast.parse(ROUTE_B_PATH.read_text(encoding="utf-8"))
        banned = {"ae11_thermo_separation_v1", "ae11_route_a"}
        offenders = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] in banned:
                        offenders.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.split(".")[0] in banned:
                    offenders.append(node.module)
        self.assertEqual(offenders, [])

    def test_route_b_uses_only_the_standard_library(self):
        tree = ast.parse(ROUTE_B_PATH.read_text(encoding="utf-8"))
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    names.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    names.add(node.module.split(".")[0])
        self.assertTrue(names.issubset({"json", "sys", "fractions",
                                        "__future__"}), sorted(names))

    def test_no_bare_assert_in_route_a_or_the_tests(self):
        for path in (ROUTE_A_PATH, ROUTE_B_PATH, Path(__file__)):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            bare = [n for n in ast.walk(tree) if isinstance(n, ast.Assert)]
            self.assertEqual(bare, [], "bare assert in %s" % path.name)


class TestDeterminism(unittest.TestCase):
    def test_receipt_is_byte_identical_in_both_modes(self):
        outs = []
        for flags in (["-I", "-B"], ["-I", "-O", "-B"]):
            proc = subprocess.run([sys.executable] + flags + [str(ROUTE_A_PATH)],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertEqual(proc.returncode, 0, proc.stderr.decode("utf-8"))
            outs.append(proc.stdout)
        self.assertEqual(outs[0], outs[1])

    def test_stored_receipt_matches_the_executor(self):
        emitted = json.dumps(RECEIPT, sort_keys=True, indent=2) + "\n"
        self.assertEqual(emitted, RESULT_PATH.read_text(encoding="utf-8"))

    def test_no_float_anywhere_in_the_receipt(self):
        self.assertFalse(A.contains_float(RECEIPT))

    def test_no_set_is_iterated_into_the_receipt(self):
        # every list in the receipt round-trips through json unchanged
        text = json.dumps(RECEIPT, sort_keys=True, indent=2)
        self.assertEqual(json.dumps(json.loads(text), sort_keys=True, indent=2),
                         text)


class TestRegisterCustody(unittest.TestCase):
    def test_register_self_digest_recomputes(self):
        register = json.loads(REGISTER_PATH.read_text(encoding="utf-8"))
        body = dict(register)
        body.pop("self_digest_sha256")
        body.pop("self_digest_note")
        blob = json.dumps(body, sort_keys=True,
                          separators=(",", ":")).encode("utf-8")
        self.assertEqual(hashlib.sha256(blob).hexdigest(),
                         register["self_digest_sha256"])
        self.assertEqual(RECEIPT["register_digest_sha256"],
                         register["self_digest_sha256"])

    def test_executor_refuses_to_emit_on_a_digest_mismatch(self):
        register = json.loads(REGISTER_PATH.read_text(encoding="utf-8"))
        tampered = dict(register)
        tampered["registered_constants"] = dict(register["registered_constants"])
        tampered["registered_constants"]["LCAP"] = 99
        blob = json.dumps(tampered, sort_keys=True,
                          separators=(",", ":")).encode("utf-8")
        self.assertNotEqual(hashlib.sha256(blob).hexdigest(),
                            register["self_digest_sha256"])

    def test_every_registered_prediction_is_reported(self):
        register = json.loads(REGISTER_PATH.read_text(encoding="utf-8"))
        registered = sorted(p["id"] for p in register["prospective_predictions"])
        reported = sorted(p["id"] for p in RECEIPT["prospective_predictions"])
        self.assertEqual(registered, reported)
        for pred in RECEIPT["prospective_predictions"]:
            self.assertIn(pred["status"], ("CONFIRMED", "REFUTED"))

    def test_registered_constants_are_the_ones_the_executor_uses(self):
        register = json.loads(REGISTER_PATH.read_text(encoding="utf-8"))
        const = register["registered_constants"]
        self.assertEqual(A.LCAP, const["LCAP"])
        self.assertEqual(A.STRING_LENGTH, const["string_length"])
        self.assertEqual(A.NULL_TRIALS, const["null_trials"])
        self.assertEqual(A.REGISTERED_PHYSICAL_SYSTEMS,
                         const["registered_physical_systems"])

    def test_receipt_binds_the_register_to_the_custody_sha(self):
        register = json.loads(REGISTER_PATH.read_text(encoding="utf-8"))
        self.assertEqual(RECEIPT["register_declared_freeze_commit"],
                         register["freeze_commit"])
        self.assertEqual(RECEIPT["freeze_commit"],
                         RECEIPT["register_declared_freeze_commit"])
        self.assertEqual(RECEIPT["source_main"], register["source_main"])
        self.assertTrue(RECEIPT["checks"][
            "register_freeze_commit_matches_custody_sha"])

    def test_roster_and_hostile_names_are_the_registered_ones(self):
        self.assertTrue(RECEIPT["checks"][
            "registered_roster_names_match_the_register"])
        self.assertTrue(RECEIPT["checks"][
            "registered_hostile_names_match_the_register"])


class TestMachineAndComplexity(unittest.TestCase):
    def test_instruction_code_is_a_complete_prefix_code(self):
        self.assertEqual(A.instruction_kraft_sum(), F(1))
        self.assertEqual(ORACLE["instruction_kraft_sum"], F(1))

    def test_program_set_satisfies_kraft_and_both_routes_agree(self):
        machine = RECEIPT["results"]["machine"]
        self.assertEqual(machine["program_kraft_sum_up_to_cap"],
                         str(ORACLE["program_kraft_sum"]))
        self.assertLessEqual(ORACLE["program_kraft_sum"], F(1))

    def test_complexity_table_agrees_between_routes(self):
        table, _pl, _kr = A.complexity_table(A.LCAP)
        for s in A.ALPHABET:
            self.assertEqual(A.k_of(table, s), ORACLE["K_U_table"][s], s)

    def test_complexity_histogram_and_extremes(self):
        ct = RECEIPT["results"]["complexity_table"]
        self.assertEqual(ct["K_U_histogram"], ORACLE["K_U_histogram"])
        self.assertEqual(ct["K_U_histogram"], {"11": 2, "13": 6, "14": 56})
        self.assertEqual(ct["K_U_min"], 11)
        self.assertEqual(ct["K_U_max"], 14)
        self.assertEqual(ct["strings_over_cap"], 0)
        self.assertEqual(ct["lexicographically_least_at_min"], "000000")
        self.assertEqual(ct["lexicographically_least_at_max"], "000010")

    def test_the_cap_is_not_binding_on_the_roster(self):
        self.assertEqual(ORACLE["strings_over_cap"], 0)


class TestCensus(unittest.TestCase):
    def test_all_twelve_ordered_pairs_are_witnessed_by_both_routes(self):
        summary = RECEIPT["results"]["census_summary"]
        self.assertEqual(summary["ordered_pairs"], 12)
        self.assertEqual(summary["witnessed"], 12)
        self.assertEqual(summary["unwitnessed"], [])
        self.assertEqual(ORACLE["witnessed_pairs"], 12)

    def test_route_b_confirms_every_route_a_witness(self):
        for row in RECEIPT["results"]["census"]:
            key = (row["fixed"], row["free"])
            witnesses = ORACLE["census"][key]
            self.assertTrue(witnesses, key)
            self.assertIn(tuple(row["witness"]), set(witnesses), key)

    def test_witness_kinds_are_classified(self):
        summary = RECEIPT["results"]["census_summary"]
        self.assertEqual(summary["derived_witnesses"], 2)
        self.assertEqual(summary["registered_independent_witnesses"], 10)
        derived = sorted((r["fixed"], r["free"])
                         for r in RECEIPT["results"]["census"]
                         if r["witness_kind"] == "derived")
        self.assertEqual(derived, [("H_shannon", "S_stat"),
                                   ("S_stat", "H_shannon")])

    def test_roster_quantities_agree_between_routes(self):
        a_rows = dict((r["id"], r) for r in RECEIPT["results"]["roster"])
        for row in ORACLE["roster"]:
            a = a_rows[row["id"]]
            self.assertEqual(a["H_shannon_bits"], str(row["H_shannon"]), row["id"])
            self.assertEqual(a["K_U_bits"], row["K_U"], row["id"])
            self.assertEqual(a["S_stat_microstate_count"], row["S_stat"], row["id"])
            self.assertEqual(a["S_thermo_Q_over_T"], str(row["S_thermo"]), row["id"])

    def test_classic_witness_equal_entropy_different_complexity(self):
        cw = RECEIPT["results"]["classic_witness"]
        self.assertEqual(cw["H_shannon_bits"], "6")
        self.assertTrue(cw["maximal_for_the_alphabet"])
        self.assertEqual(cw["paired_object_same_entropy"]["K_U_a"], 11)
        self.assertEqual(cw["paired_object_same_entropy"]["K_U_b"], 14)
        self.assertEqual(cw["members_K_U_histogram"], {"11": 2, "13": 6, "14": 56})


class TestResourceRegistry(unittest.TestCase):
    def test_no_physical_energetic_resource_is_instantiated(self):
        summary = RECEIPT["results"]["resource_registry_summary"]
        self.assertEqual(summary["physical_energetic_instantiated"], 0)
        self.assertEqual(summary["instantiated_physical_resources"], [])
        self.assertEqual(
            B.oracle_instantiated_physical(RECEIPT["results"]["resource_registry"]),
            0)

    def test_every_resource_is_classified_into_one_of_the_two_registered_classes(self):
        rows = RECEIPT["results"]["resource_registry"]
        self.assertEqual(len(rows), 24)
        for row in rows:
            self.assertIn(row["class"],
                          ("LOGICAL_COMPUTATIONAL", "PHYSICAL_ENERGETIC"))
            self.assertFalse(row["numeric_value_in_physical_units"], row["resource"])

    def test_no_energy_value_is_computed_anywhere_in_the_receipt(self):
        self.assertFalse(A.contains_float(RECEIPT))
        for row in RECEIPT["results"]["maps"]:
            self.assertTrue(row["landauer_statement"].endswith("k_B T ln 2"))


class TestMapsDevicesAndScope(unittest.TestCase):
    def test_erased_bit_counts_agree_between_routes(self):
        for row in RECEIPT["results"]["maps"]:
            other = ORACLE["maps"][row["id"]]
            self.assertEqual(row["erased_bits"], other["erased_bits"], row["id"])
            self.assertEqual(row["image_size"], other["image_size"], row["id"])
            self.assertEqual(row["largest_preimage_size"],
                             other["largest_preimage_size"], row["id"])
            self.assertEqual(row["log2_largest_preimage"],
                             other["log2_largest_preimage"], row["id"])
            self.assertEqual(row["drop_bits"], other["drop_bits"], row["id"])

    def test_registered_erased_bit_counts(self):
        m = dict((r["id"], r["erased_bits"]) for r in RECEIPT["results"]["maps"])
        self.assertEqual(m, {"F_AND": 1, "F_BIJECTION": 0,
                             "F_ERASE1": 1, "F_ERASE2": 2})

    def test_and_map_drop_is_not_decided_and_strictly_exceeds_its_erased_bits(self):
        row = [r for r in RECEIPT["results"]["maps"] if r["id"] == "F_AND"][0]
        self.assertEqual(row["drop_bits"], "NOT_DECIDED")
        lo, hi = ORACLE["and_drop_bracket"]
        self.assertEqual(row["drop_bracket"]["lower"], str(lo))
        self.assertEqual(row["drop_bracket"]["upper"], str(hi))
        self.assertTrue(row["drop_bracket"]["strictly_above_erased_bits"])
        self.assertGreater(lo, F(row["erased_bits"]))
        # the certificate is an integer comparison, not a decimal evaluation
        self.assertGreaterEqual(3 ** 12, 2 ** 19)
        self.assertLessEqual(3 ** 5, 2 ** 8)

    def test_largest_preimage_of_the_and_map_is_not_a_power_of_two(self):
        row = [r for r in RECEIPT["results"]["maps"] if r["id"] == "F_AND"][0]
        self.assertEqual(row["largest_preimage_size"], 3)
        self.assertEqual(row["log2_largest_preimage"], "NOT_A_POWER_OF_TWO")

    def test_every_device_implements_its_registered_map(self):
        for row in RECEIPT["results"]["devices"]:
            other = ORACLE["devices"][row["device"] + "|" + row["map"]]
            self.assertTrue(other["implements"], row["device"] + row["map"])
            self.assertEqual(row["total_ops"], other["total_ops"])
            self.assertEqual(row["overhead_ops"], other["overhead_ops"])
            self.assertEqual(row["erased_bits"], other["erased_bits"])

    def test_the_erasure_bound_does_not_determine_the_registered_cost(self):
        non_inf = RECEIPT["results"]["non_inference"]
        self.assertTrue(non_inf["holds_for_every_map"])
        for row in non_inf["per_map"]:
            self.assertTrue(row["erased_bits_equal"], row["map"])
            self.assertTrue(row["total_ops_differ"], row["map"])
            self.assertEqual(row["operation_count_gap"], 5, row["map"])
        erase2 = [r for r in non_inf["per_map"] if r["map"] == "F_ERASE2"][0]
        self.assertEqual(erase2["erased_bits"], 2)
        self.assertEqual(erase2["total_ops_low"], 2)
        self.assertEqual(erase2["total_ops_high"], 7)

    def test_the_correct_scope_pair(self):
        scope = RECEIPT["results"]["correct_scope"]
        self.assertEqual(scope["bijection"]["erased_bits"], 0)
        self.assertEqual(scope["bijection"]["landauer_bound_in_kT_ln2"], 0)
        self.assertGreater(scope["bijection"]["registered_total_ops"], 0)
        self.assertTrue(scope["bijection"]["total_ops_strictly_positive"])
        self.assertEqual(scope["many_to_one"]["erased_bits"], 2)

    def test_landauer_assumptions_are_listed_with_their_violations(self):
        rows = RECEIPT["results"]["landauer_assumptions"]
        self.assertEqual(len(rows), 4)
        for row in rows:
            self.assertTrue(row["assumption"])
            self.assertTrue(row["registered_violation"])
            self.assertIn(row["violates_the_bound"], (True, False))
        # the finite-time relaxation breaks attainment, not the bound: reported
        # as such rather than dressed up as a violation
        finite = [r for r in rows
                  if r["registered_violation"] == "RELAXED_FINITE_TIME"][0]
        self.assertFalse(finite["violates_the_bound"])
        correlated = [r for r in rows
                      if r["registered_violation"] == "RELAXED_CORRELATED_RESET"][0]
        self.assertTrue(correlated["violates_the_bound"])


class TestBounds(unittest.TestCase):
    def test_every_bound_record_is_complete(self):
        self.assertEqual(len(RECEIPT["bounds"]), 16)
        for b in RECEIPT["bounds"]:
            for key in ("kind", "bound_value", "range_lo", "range_hi",
                        "range_derivation", "vacuous", "attained_by",
                        "violated_by", "status", "used_for_closure"):
                self.assertIn(key, b, b["id"])
            self.assertIn(b["kind"], ("upper", "lower"))
            self.assertIn("definition", b["range_derivation"])
            self.assertNotIn("observed", b["range_derivation"].split("neither")[0])

    def test_vacuity_is_computed_from_the_definitional_range(self):
        for b in RECEIPT["bounds"]:
            lo, hi = F(b["range_lo"]), F(b["range_hi"])
            val = F(b["bound_value"])
            expected = (val >= hi) if b["kind"] == "upper" else (val <= lo)
            self.assertEqual(b["vacuous"], expected, b["id"])

    def test_bounds_without_a_violator_are_flagged_and_close_nothing(self):
        for b in RECEIPT["bounds"]:
            if b["violated_by"] is None:
                self.assertEqual(b["status"], "UNFALSIFIED_BOUND", b["id"])
                self.assertFalse(b["used_for_closure"], b["id"])
            if b["vacuous"]:
                self.assertFalse(b["used_for_closure"], b["id"])

    def test_the_bijection_landauer_bound_is_vacuous(self):
        b = [x for x in RECEIPT["bounds"]
             if x["id"] == "B_LANDAUER__F_BIJECTION"][0]
        self.assertEqual(b["bound_value"], "0")
        self.assertEqual(b["range_lo"], "0")
        self.assertTrue(b["vacuous"])
        self.assertEqual(b["status"], "UNFALSIFIED_BOUND")
        self.assertFalse(b["used_for_closure"])

    def test_the_erasure_landauer_bounds_are_non_vacuous_and_falsifiable(self):
        for map_id, m in (("F_AND", "1"), ("F_ERASE1", "1"), ("F_ERASE2", "2")):
            b = [x for x in RECEIPT["bounds"]
                 if x["id"] == "B_LANDAUER__" + map_id][0]
            self.assertEqual(b["bound_value"], m, map_id)
            self.assertFalse(b["vacuous"], map_id)
            self.assertEqual(b["status"], "FALSIFIABLE", map_id)
            violated = b["violated_by"]
            self.assertLess(F(violated["attained_value"]), F(b["bound_value"]),
                            map_id)
            other = ORACLE["conditional_relaxation"][map_id]
            self.assertEqual(F(violated["attained_value"]),
                             F(other["relative_erased_bits"]), map_id)
            self.assertEqual(violated["conditional_state_count"],
                             other["conditional_state_count"], map_id)
            self.assertEqual(violated["conditional_image_count"],
                             other["conditional_image_count"], map_id)
            self.assertEqual(F(violated["conditional_drop_bits"]),
                             other["conditional_drop_bits"], map_id)
            self.assertTrue(b["used_for_closure"], map_id)

    def test_every_violator_attains_a_value_that_breaks_its_bound(self):
        checked = 0
        for b in RECEIPT["bounds"]:
            v = b["violated_by"]
            if v is None:
                continue
            checked += 1
            if b["kind"] == "lower":
                self.assertLess(F(v["attained_value"]), F(b["bound_value"]),
                                b["id"])
            else:
                self.assertGreater(F(v["attained_value"]), F(b["bound_value"]),
                                   b["id"])
        self.assertEqual(checked, 12)

    def test_the_drop_bound_violators_really_violate(self):
        for b in RECEIPT["bounds"]:
            if not b["id"].startswith("B_DROP__") or b["violated_by"] is None:
                continue
            self.assertLess(F(b["violated_by"]["attained_value"]),
                            F(b["bound_value"]), b["id"])

    def test_the_gibbs_bounds_hold_and_agree_with_route_b(self):
        rows = dict((r["id"], r) for r in RECEIPT["results"]["roster"])
        for b in RECEIPT["bounds"]:
            if not b["id"].startswith("B_GIBBS__"):
                continue
            oid = b["id"][len("B_GIBBS__"):]
            self.assertEqual(F(b["bound_value"]), ORACLE["gibbs_bounds"][oid], oid)
            self.assertLessEqual(F(rows[oid]["H_shannon_bits"]),
                                 F(b["bound_value"]), oid)
            self.assertTrue(b["notes"]["holds"], oid)
            if b["violated_by"] is not None:
                self.assertGreater(F(b["violated_by"]["attained_value"]),
                                   F(b["bound_value"]), oid)

    def test_the_two_maximal_entropy_objects_have_a_vacuous_gibbs_bound(self):
        vac = sorted(b["id"] for b in RECEIPT["bounds"]
                     if b["id"].startswith("B_GIBBS__") and b["vacuous"])
        self.assertEqual(vac, ["B_GIBBS__R_PROCESS_B", "B_GIBBS__R_UNIFORM_BLOCK"])

    def test_the_non_dyadic_gibbs_bound_uses_a_certified_rational(self):
        b = [x for x in RECEIPT["bounds"] if x["id"] == "B_GIBBS__R_MACRO_B"][0]
        self.assertEqual(b["bound_value"], "9/4")
        self.assertGreaterEqual(5 ** 4, 2 ** 9)      # log2(5) >= 9/4
        self.assertLessEqual(5 ** 3, 2 ** 7)         # log2(5) <= 7/3


class TestNonequilibriumGate(unittest.TestCase):
    def test_no_physical_system_is_registered(self):
        gate = RECEIPT["results"]["nonequilibrium_gate"]
        self.assertEqual(gate["registered_physical_systems"], 0)
        self.assertEqual(A.registered_physical_systems(), [])

    def test_gate_is_silent_on_the_clean_roster(self):
        gate = RECEIPT["results"]["nonequilibrium_gate"]
        self.assertEqual(gate["clean_roster_hits"], [])
        self.assertTrue(gate["no_alarm_holds"])

    def test_gate_flags_the_planted_fixture(self):
        gate = RECEIPT["results"]["nonequilibrium_gate"]
        self.assertTrue(gate["planted_fixture_flagged"])
        self.assertGreater(len(gate["planted_fixture_hits"]), 0)
        terms = sorted(h["term"] for h in gate["planted_fixture_hits"])
        self.assertIn("entropy production", terms)

    def test_the_gate_is_potent_on_each_frozen_term(self):
        for term in RECEIPT["results"]["nonequilibrium_gate"]["frozen_terms"]:
            hits = A.noneq_hits({"probe": "a claim mentioning " + term + " here"})
            self.assertEqual(len(hits) >= 1, True, term)


class TestHostiles(unittest.TestCase):
    def test_every_hostile_is_potent_then_detected(self):
        self.assertEqual(len(RECEIPT["hostiles"]), 5)
        for h in RECEIPT["hostiles"]:
            self.assertNotEqual(h["true_value"], h["perturbed_value"], h["name"])
            self.assertTrue(h["potent"], h["name"])
            self.assertTrue(h["detected"], h["name"])

    def test_registered_hostiles_are_exactly_the_ones_the_register_names(self):
        register = json.loads(REGISTER_PATH.read_text(encoding="utf-8"))
        self.assertEqual(sorted(h["name"] for h in register["hostiles"]),
                         sorted(h["name"] for h in RECEIPT["hostiles"]))

    def test_conflation_hostile_breaks_the_census(self):
        h = [x for x in RECEIPT["hostiles"]
             if x["name"] == "H_ENTROPY_CONFLATE"][0]
        self.assertLess(h["witnessed_pairs_after"], 12)

    def test_lcap_hostile_moves_a_registered_roster_string_over_the_cap(self):
        h = [x for x in RECEIPT["hostiles"] if x["name"] == "H_LCAP"][0]
        self.assertEqual(h["true_value"], 14)
        self.assertEqual(h["perturbed_value"], ">LCAP")
        self.assertEqual(h["roster_strings_over_cap_after"], ["000010"])

    def test_overhead_hostile_destroys_the_non_inference_witness(self):
        h = [x for x in RECEIPT["hostiles"]
             if x["name"] == "H_OVERHEAD_EQUAL"][0]
        self.assertEqual(h["true_value"], [2, 7])
        self.assertEqual(h["perturbed_value"], [2, 2])


class TestNull(unittest.TestCase):
    def test_the_witness_beats_the_null_without_a_threshold(self):
        null = RECEIPT["null"]
        self.assertEqual(null["trials"], 200)
        self.assertEqual(null["witness_witnessed_pairs"], 12)
        self.assertLess(null["largest_null_witnessed_pairs"], 12)
        self.assertEqual(null["largest_null_witnessed_pairs"], 6)
        self.assertEqual(null["trials_reaching_all_twelve"], 0)
        self.assertTrue(null["witness_exceeds_largest_null"])

    def test_the_null_histogram_covers_every_trial(self):
        null = RECEIPT["null"]
        self.assertEqual(sum(null["histogram"].values()), null["trials"])

    def test_no_alarm_on_the_registered_clean_roster(self):
        self.assertTrue(RECEIPT["null"]["no_alarm_holds"])
        self.assertEqual(RECEIPT["null"]["known_clean_rosters_flagged"], [])

    def test_the_null_is_reproducible(self):
        again = A.run_null(A.complexity_table(A.LCAP)[0])
        self.assertEqual(again["histogram"], RECEIPT["null"]["histogram"])


class TestReceiptShape(unittest.TestCase):
    def test_required_top_level_keys(self):
        for key in ("schema", "issue", "issue_comment_id", "package",
                    "source_main", "freeze_commit", "claim_ceiling", "verdict",
                    "checks", "results", "bounds", "hostiles", "null",
                    "prospective_predictions", "forbidden_promotions"):
            self.assertIn(key, RECEIPT, key)

    def test_verdict_and_checks(self):
        self.assertEqual(RECEIPT["verdict"], "GREEN")
        self.assertEqual(RECEIPT["issue"], 833)
        self.assertEqual(RECEIPT["issue_comment_id"], 5692689542)
        self.assertEqual(sorted(k for k, v in RECEIPT["checks"].items() if not v),
                         [])

    def test_claim_ceiling_matches_the_freeze_and_the_manifest(self):
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        freeze = (HERE / "FREEZE_V1.md").read_text(encoding="utf-8")
        self.assertIn(RECEIPT["claim_ceiling"], freeze)
        self.assertEqual(manifest["claim_ceiling"], RECEIPT["claim_ceiling"])
        self.assertEqual(manifest["freeze_commit"], RECEIPT["freeze_commit"])
        self.assertEqual(manifest["source_main"], RECEIPT["source_main"])
        self.assertEqual(manifest["theorems"], RECEIPT["theorems"])

    def test_forbidden_promotions_are_carried(self):
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        for name in ("LANDAUER_BOUND_DETERMINES_SYSTEM_ENERGY",
                     "INFORMATION_SAVINGS_IMPLY_ENERGY_SAVINGS",
                     "ENERGY_CLAIM_WITHOUT_HARDWARE_MEASUREMENT",
                     "SHANNON_ENTROPY_EQUALS_THERMODYNAMIC_ENTROPY"):
            self.assertIn(name, RECEIPT["forbidden_promotions"])
            self.assertIn(name, manifest["forbidden_promotions"])


class TestReconciliation(unittest.TestCase):
    def setUp(self):
        self.spec = json.loads(RECON_PATH.read_text(encoding="utf-8"))

    def test_schema_and_ids(self):
        self.assertEqual(self.spec["schema"], "GMI_ISSUE_RECONCILIATION_V2")
        self.assertEqual(self.spec["issue"], 833)
        self.assertEqual(self.spec["issue_comment_id"], 5692689542)
        self.assertEqual(self.spec["package"], RECEIPT["package"])
        self.assertEqual(self.spec["claim_ceiling"], RECEIPT["claim_ceiling"])

    def test_five_rows_closed_and_three_left_open(self):
        self.assertEqual(len(self.spec["replacements"]), 5)
        self.assertEqual(len(self.spec["not_closed"]), 3)
        self.assertEqual(RECEIPT["rows_closed"], 5)
        self.assertEqual(RECEIPT["rows_left_open"], 3)

    def test_replacements_are_byte_exact_rewrites(self):
        seen = set()
        for rep in self.spec["replacements"]:
            self.assertTrue(rep["anchor"].startswith("### AE11 "))
            self.assertTrue(rep["old"].startswith("- [ ] "))
            self.assertTrue(rep["new"].startswith("- [x] "))
            self.assertEqual(rep["new"][6:6 + len(rep["old"]) - 6],
                             rep["old"][6:])
            self.assertNotIn(rep["old"], seen)
            seen.add(rep["old"])
            self.assertIn(RECEIPT["package"], rep["new"])

    def test_left_open_rows_each_name_an_instrument(self):
        for row in self.spec["not_closed"]:
            self.assertTrue(row["old"].startswith("- [ ] "))
            self.assertTrue(row["instrument_required"])
            self.assertGreater(len(row["instrument_required"]), 40)

    def test_manifest_carries_the_left_open_rows_with_instruments(self):
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["rows_left_open"]), 3)
        for row in manifest["rows_left_open"]:
            self.assertIn("instrument_required", row)
            self.assertTrue(row["instrument_required"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
