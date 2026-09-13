import copy
import unittest
from call_capture_v1 import V2, capture, summarize, validate_charges
from legacy_terminal_v1 import original_control, terminal
from native_source_v1 import load
from qualification_v1 import check_split


class CallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native = load()
        cls.g = cls.native.zoo.program_search(grammar=1, budget=32)
        cls.spec = cls.native.ecology.REGISTRY["E_smooth3"]
        cls.rows = [capture(cls.native, cls.spec, cls.g, j) for j in V2]
        cls.failed = capture(cls.native, cls.spec, cls.g, "standard", fail_at=4)

    def test_native_observer_no_alarm_full_response(self):
        plain = self.native.ecology.run_genotype(self.spec, self.g, self.native.bases.B0, "standard")
        self.assertEqual(plain, self.rows[0]["response"])
        self.assertEqual(summarize(self.rows, V2)["status"], "COMPLETE_EXPOSED_ASSAY")

    def test_failed_native_feedback_retains_incurred_charges(self):
        failed = self.failed
        self.assertEqual(failed["status"], "ERROR")
        self.assertEqual(len(failed["charge_events"]), 4)
        self.assertTrue(validate_charges(failed))
        self.assertTrue(any(c["method"] == "feedback" and c["status"] == "ERROR"
                            for c in failed["calls"]))
        self.assertGreater(failed["final_ledger"]["upd"], 0)
        self.assertIs(self.native.ecology.Machine, self.native.core.Machine)
        self.assertIs(self.native.ecology.VM, self.native.vm.VM)

    def test_errors_not_distinct_answers_or_complete(self):
        failed = [dict(copy.deepcopy(self.failed), intervention=j) for j in V2]
        result = summarize(failed, V2)
        self.assertEqual(result["distinct_answer_vectors"], 0)
        self.assertEqual(result["status"], "UNRESOLVED_INCOMPLETE")
        self.assertEqual(summarize([self.failed] + self.rows[1:], V2)["status"],
                         "UNRESOLVED_INCOMPLETE")

    def test_explicit_family_missing_duplicate_legacy_refused(self):
        for family in (self.native.ecology.INTERVENTION_FAMILY_V1, tuple(self.native.ecology.INTERVENTIONS), V2[:-1]):
            with self.assertRaises(ValueError):
                summarize(self.rows, family)
        with self.assertRaises(ValueError):
            summarize(self.rows[:-1] + [self.rows[0]], V2)

    def test_actual_v2_feedback_and_scoring_disjoint(self):
        for row in self.rows:
            result = check_split(self.native, row)
            self.assertFalse(set(result["actual_feedback_inputs"]) & set(result["scored_inputs"]))
        extra = check_split(self.native, self.rows[-1])
        self.assertEqual(extra["scored_inputs"], [8, 11, 13, 14])
        self.assertTrue(set(self.native.smooth.UNSEEN[:4]) <= set(extra["actual_feedback_inputs"]))

    def test_charge_omission_and_false_answer_refused(self):
        bad = copy.deepcopy(self.rows[0])
        del bad["charge_events"][2]
        with self.assertRaises(ValueError):
            validate_charges(bad)
        bad = copy.deepcopy(self.rows)
        bad[0]["response"]["trace"][-1][0] = "ERR"
        with self.assertRaises(ValueError):
            summarize(bad, V2)

    def test_actual_historical_terminal_countercontrol(self):
        bad, good = original_control(self.native, False), original_control(self.native, True)
        self.assertEqual(bad["original_full_result"]["terminal"], "NN_NONNN_PACKET_DECIDED_AT_MICROSCOPE_SCOPE")
        self.assertFalse(bad["original_full_result"]["tasks"]["fixture"]["evidence_complete"])
        self.assertEqual(bad["successor_terminal"], "UNRESOLVED_INCOMPLETE")
        self.assertEqual(good["successor_terminal"], "COMPLETE_AT_DECLARED_REGISTER_ONLY")
        self.assertEqual(bad["native_candidate_calls"], 0)

    def test_missing_task_cannot_be_vacuously_complete(self):
        self.assertEqual(terminal({}, ()), "UNRESOLVED_INCOMPLETE")
        self.assertEqual(terminal({}, ("fixture",)), "UNRESOLVED_INCOMPLETE")


if __name__ == "__main__":
    unittest.main()
