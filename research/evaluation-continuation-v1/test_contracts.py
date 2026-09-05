from copy import deepcopy
from pathlib import Path
import sys
import unittest

import contracts as C

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from ocm.kso.warrant import WarrantProfile, all_profiles, leq, powerset


def cases():
    return [{"lifetime": "development-1", "family": "transfer", "case": f"case-{i}",
             "order": i, "task_sha256": C.identity(["task", i]),
             "rubric_sha256": C.identity(["rubric", i]),
             "information_sha256": C.identity("same-information"),
             "channel_sha256": C.identity("same-candidates"),
             "budget": {"steps": 100, "verifier_calls": 20}}
            for i in range(6)]


def outcomes(plan, value=True):
    return [{**{k: row[k] for k in ("lifetime", "family", "case")},
             "case_binding": C.identity(row), "status": "OBSERVED", "success": value}
            for row in plan]


def self_record():
    h = C.identity
    return {"target": "layer-D3", "assurance_target": "layer-D3",
            "components": {"layer-D3": h("incumbent")},
            "predecessor": h("incumbent"), "incumbent": h("incumbent"),
            "candidate": h("challenger"), "assurance_subject": h("challenger"),
            "candidate_channel": "registered-diagnoses", "parent_channel": "registered-diagnoses",
            **{k: h(k) for k in ("source_sha256", "scenario_sha256", "preservation_sha256",
                                "proposal_sha256", "parent_sha256", "adoption_receipt_sha256")}}


class PairingTests(unittest.TestCase):
    def test_six_versus_four_is_not_a_pair(self):
        with self.assertRaises(C.CannotCheck):
            C.match_cases(cases(), cases()[:4])

    def test_matching_six_cases(self):
        self.assertEqual(len(C.match_cases(cases(), list(reversed(cases())))), 6)

    def test_same_count_different_identity(self):
        b = cases(); b[0]["case"] = "different"
        with self.assertRaises(C.CannotCheck):
            C.match_cases(cases(), b)

    def test_duplicate_cannot_hide_missing_case(self):
        b = cases(); b[-1] = deepcopy(b[0])
        with self.assertRaises(C.CannotCheck):
            C.match_cases(cases(), b)

    def test_empty_denominator(self):
        with self.assertRaises(C.CannotCheck):
            C.match_cases([], [])

    def test_changed_task_rubric_information_channel(self):
        for key in ("task_sha256", "rubric_sha256", "information_sha256", "channel_sha256"):
            with self.subTest(key=key):
                b = cases(); b[0][key] = C.identity("different")
                with self.assertRaises(C.CannotCheck):
                    C.match_cases(cases(), b)

    def test_budgets_and_order_must_match(self):
        for field, value in (("budget", {"steps": 99}), ("order", 100)):
            b = cases(); b[0][field] = value
            with self.assertRaises(C.CannotCheck):
                C.match_cases(cases(), b)

    def test_malformed_shared_declarations_are_not_matches(self):
        for field, value in (("budget", {}), ("order", True), ("task_sha256", "unbound"),
                             ("budget", {"steps": -1}), ("budget", {"steps": True})):
            a = cases(); a[0][field] = value
            with self.assertRaises(C.CannotCheck):
                C.match_cases(a, deepcopy(a))

    def test_order_collision(self):
        a = cases(); a[1]["order"] = a[0]["order"]
        with self.assertRaises(C.CannotCheck):
            C.match_cases(a, deepcopy(a))

    def test_complete_scores_remain_descriptive(self):
        a = cases()
        result = C.paired_descriptives(a, a, outcomes(a), outcomes(a, False))
        self.assertEqual(result["rows"][0]["difference"], "1")
        self.assertEqual(result["rows"][0]["paired_cases"], 6)
        self.assertEqual(result["unit"], "lifetime")
        self.assertTrue(result["scientific_terminal"].startswith("CANNOT_CHECK"))

    def test_undecided_or_missing_scores_never_imputed(self):
        a = cases()
        for mutation in ("missing", "cannot-check", "truthy", "drift"):
            b = outcomes(a)
            if mutation == "missing": b.pop()
            if mutation == "cannot-check": b[0]["status"] = "CANNOT_CHECK"
            if mutation == "truthy": b[0]["success"] = "False"
            if mutation == "drift": b[0]["case_binding"] = C.identity("other-plan")
            with self.assertRaises(C.CannotCheck):
                C.paired_descriptives(a, a, outcomes(a), b)


class LifecycleTests(unittest.TestCase):
    def test_alternative_support_survives_revoked_lesson(self):
        result = C.grade_lifecycle([["lesson"], ["prior-knowledge"]],
                                   [["lesson"], ["prior-knowledge"]], ["lesson"], "LIVE")
        self.assertTrue(result["success"])

    def test_preexisting_knowledge_is_not_forced_unknown(self):
        self.assertTrue(C.grade_lifecycle([["prior"]], [["prior"]], [], "LIVE")["success"])

    def test_complete_sole_support_dies(self):
        self.assertTrue(C.grade_lifecycle([["lesson"]], [["lesson"]], ["lesson"], "DEAD")["success"])

    def test_incomplete_support_is_unknown_not_dead(self):
        self.assertTrue(C.grade_lifecycle([["lesson"]], [[]], ["lesson"], "UNKNOWN")["success"])

    def test_unrelated_revocation_preserves(self):
        self.assertTrue(C.grade_lifecycle([["a", "b"]], [["a", "b"]], ["other"], "LIVE")["success"])

    def test_unearned_assertion_fails(self):
        self.assertFalse(C.grade_lifecycle([], [[]], [], "LIVE")["success"])

    def test_invalid_interval_and_unknown_measurement(self):
        for args in (([["a"]], [], [], "LIVE"), ([], [], [], "PASS")):
            with self.assertRaises(C.CannotCheck): C.grade_lifecycle(*args)

    def test_exhaustive_parity_with_current_runtime(self):
        profiles = all_profiles(3)
        count = 0
        for lower in profiles:
            for upper in profiles:
                if not leq(lower, upper): continue
                runtime = WarrantProfile(lower, upper)
                encode = lambda ps: [list(map(str, sorted(w))) for w in ps]
                for dead in powerset(tuple(range(3))):
                    self.assertEqual(C.expected_liveness(encode(lower), encode(upper), list(map(str, dead))),
                                     runtime.liveness(dead).value)
                    count += 1
        self.assertEqual(count, 1344)


class SelfChangeTests(unittest.TestCase):
    def test_consistent_metadata_does_not_authorize_adoption(self):
        result = C.check_self_change_binding(self_record())
        self.assertEqual(result["status"], "BINDINGS_CONSISTENT")
        self.assertFalse(result["adoption_authorized"])

    def test_wrong_predecessor_target_and_candidate(self):
        for field in ("predecessor", "incumbent", "candidate", "assurance_target", "parent_channel"):
            row = self_record(); row[field] = C.identity("wrong")
            with self.assertRaises(C.CannotCheck): C.check_self_change_binding(row)

    def test_machine_alias_cannot_replace_named_target(self):
        row = self_record(); row["components"] = {"machine": C.identity("incumbent")}
        with self.assertRaises(C.CannotCheck): C.check_self_change_binding(row)

    def test_missing_assurance_or_source_is_not_adoption(self):
        for key in ("adoption_receipt_sha256", "source_sha256", "preservation_sha256"):
            row = self_record(); del row[key]
            with self.assertRaises(C.CannotCheck): C.check_self_change_binding(row)


if __name__ == "__main__":
    unittest.main()
