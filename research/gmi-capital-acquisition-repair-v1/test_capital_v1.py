import unittest
from copy import deepcopy
from itertools import product

from machine_v1 import Ledger, clone, empty, evaluate, gate, names
from search_v1 import acquire, solve
from parent_oracle_v1 import first_hit, words
from experiment_v1 import acquisition, run, task
from cost_oracle_v1 import check
from certificate_v1 import certify
from countercontrols_v1 import run as controls


class CapitalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run()

    def test_actual_acquisition_and_new_stored_mediator(self):
        r = self.result
        before = r["traces"]["acquisition_H"]["before"]
        after = r["traces"]["acquisition_H"]["after"]
        self.assertEqual(before["library"], [["h", ["inc", "inc"]]])
        self.assertEqual(after["library"][-1], ["m", ["inc"] * 4])
        self.assertLess(r["conditional_acquisition"]["H"], r["conditional_acquisition"]["RESET_empty"])

    def test_lesion_sham_restore_complete_state_and_trace(self):
        r = self.result
        a = r["traces"]["later_acquired"]
        for arm in ("sham", "restored"):
            self.assertEqual(a, r["traces"]["later_" + arm])
        b = r["traces"]["later_disabled"]
        self.assertEqual(a["before"]["library"], b["before"]["library"])
        self.assertEqual(b["before"]["active"], ["h"])
        self.assertLess(a["result"]["rank"], b["result"]["rank"])
        self.assertLess(a["cost"], b["cost"])

    def test_descendant_primitive_work_is_charged(self):
        events = self.result["traces"]["later_acquired"]["events"]
        self.assertTrue(any(e["kind"] == "lookup" and e["name"] == "m" for e in events))
        self.assertGreater(sum(e["kind"] == "arithmetic" for e in events),
                           sum(e["kind"] == "lookup" for e in events))
        self.assertTrue(check(self.result)["all_phase_costs_agree"])

    def test_all_first_hit_rows_verify_without_earlier_success(self):
        for p in self.result["traces"].values():
            rows = p["result"]["candidates"]
            self.assertFalse(any(x["pass"] for x in rows[:-1]))
            self.assertTrue(rows[-1]["pass"])
            t = [(x, y) for x, y in zip(range(4), rows[-1]["outputs"])]
            expected = first_hit(p["before"], t, 5)
            self.assertEqual(expected["rank"], len(rows))
            self.assertEqual(expected["body"], rows[-1]["body"])

    def test_missing_stored_mediator_rejects_actual_record(self):
        r = deepcopy(self.result)
        r["traces"]["acquisition_H"]["after"]["library"].pop()
        with self.assertRaisesRegex(ValueError, "stored mediator"):
            certify(r)

    def test_no_later_effect_rejects_actual_record(self):
        r = deepcopy(self.result)
        r["traces"]["later_disabled"]["cost"] = r["traces"]["later_acquired"]["cost"]
        with self.assertRaisesRegex(ValueError, "no later effect"):
            certify(r)

    def test_reset_also_acquires_a_useful_new_mediator(self):
        r = self.result["traces"]
        self.assertEqual(r["acquisition_H"]["result"]["stored"],
                         r["acquisition_RESET"]["result"]["stored"])
        self.assertLess(r["from_empty_serving"]["result"]["rank"],
                        r["empty_without_new_serving"]["result"]["rank"])
        self.assertLess(r["from_empty_serving"]["cost"],
                        r["empty_without_new_serving"]["cost"])

    def test_parent_is_same_complete_phase(self):
        self.assertEqual(self.result["traces"]["acquisition_H"],
                         self.result["traces"]["same_library_parent"])
        self.assertEqual(self.result["terminal"], "PARENT_SUFFICIENT")

    def test_fresh_inputs_are_distinct_and_exact(self):
        p = self.result["traces"]["later_acquired"]["result"]
        self.assertEqual(p["fresh_inputs"], [4, 5])
        self.assertEqual(p["fresh_outputs"], [9, 10])

    def test_exhaustion_is_not_acquisition(self):
        s = empty()
        ledger = Ledger()
        result = acquire(s, "m", task(7), 1, ledger)
        self.assertEqual(result["status"], "EXHAUSTED")
        self.assertIsNone(result["rank"])
        self.assertEqual(s, empty())
        self.assertGreater(ledger.record()["cost"], 0)

    def test_existing_capital_cannot_be_renamed_as_new(self):
        s, _ = acquisition(empty(), 2, "h")
        with self.assertRaisesRegex(ValueError, "already"):
            acquire(s, "new_label", task(2), 5, Ledger())

    def test_illegal_gate_and_nested_body_refused(self):
        with self.assertRaises(ValueError):
            gate(empty(), "m", False, Ledger())
        with self.assertRaises(ValueError):
            names({"library": [["m", ["missing"]]], "active": ["m"]})

    def test_failed_call_retains_incurred_dispatch(self):
        ledger = Ledger()
        with self.assertRaises(ValueError):
            evaluate(("inc", "missing"), empty(), 0, ledger)
        self.assertEqual([e["kind"] for e in ledger.events], ["dispatch", "arithmetic", "dispatch"])
        self.assertEqual(ledger.record()["cost"], 3)

    def test_joint_clones_do_not_alias(self):
        state, _ = acquisition(empty(), 2, "h")
        saved = deepcopy(state)
        twin = clone(state, Ledger())
        twin["library"][0][1].append("inc")
        twin["active"].clear()
        self.assertEqual(state, saved)

    def test_independent_schedule_all_small_words(self):
        for n in range(1, 5):
            alphabet = tuple(range(n))
            expected = [w for k in range(1, 4) for w in product(alphabet, repeat=k)]
            self.assertEqual(list(words(alphabet, 3)), expected)

    def test_equal_length_countermodel_has_real_functions(self):
        r = controls()["same_functions_renamed"]
        self.assertEqual(r["H"]["length"], r["RESET"]["length"])
        self.assertLess(r["H"]["cost"], r["RESET"]["cost"])

    def test_cannot_infer_lifecycle_savings_from_conditional_gain(self):
        r = controls()["conditional_vs_lifecycle"]
        self.assertLess(r["acq_H"], r["acq_RESET"])
        self.assertGreater(r["H_total"], r["RESET_total"])

    def test_every_event_is_nonnegative_and_experiment_sums(self):
        r = self.result
        ps = list(r["traces"].values()) + list(r["diagnostics"].values())
        for p in ps:
            self.assertEqual(p["cost"], sum(e["quantity"] for e in p["events"]))
            self.assertTrue(all(type(e["quantity"]) is int and e["quantity"] >= 0 for e in p["events"]))
        self.assertEqual(r["experiment_cost"], sum(p["cost"] for p in ps))


if __name__ == "__main__":
    unittest.main()
