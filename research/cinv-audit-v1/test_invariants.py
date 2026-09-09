from __future__ import annotations

import json
import unittest
from pathlib import Path

from ocm.kso.jump import JumpAssessment
from ocm.kso.nogoods import NogoodSet
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.selfmodel.jump_evidence import assess_jump_from_evidence
from ocm.selfmodel.proposal import ChangeClass

import audit


class TestConstitutionalInvariants(unittest.TestCase):
    def test_audit_passes_all_section_3_boxes(self):
        result = audit.audit()
        self.assertEqual(result["n_fail_closed"], sum(1 for i in result["invariants"] if i["status"] == "FAIL"))
        self.assertEqual(result["n_cannot_check"], sum(1 for i in result["invariants"] if i["status"] == "CANNOT_CHECK"))
        self.assertEqual(result["n_cannot_check"], 0)
        self.assertEqual(result["n_fail_closed"], 0)
        self.assertEqual(result["n_pass"], len(result["invariants"]))
        self.assertEqual(result["terminal"], "CONSTITUTIONAL_INVARIANTS_PRESERVED_AT_SCOPE")
        ids = {i["id"] for i in result["invariants"]}
        required = {
            "exact_object_identity", "evidence_identity", "provenance", "warrant_uncertainty",
            "scope", "authority", "polarity_contradiction", "alternate_vs_conjunctive",
            "dependency_semantics", "exact_revocation", "UNKNOWN", "CANNOT_CHECK",
            "resource_accounting", "replay_restart", "historical_receipt_identity",
            "failure_not_impossibility", "external_adoption_authority",
        }
        self.assertEqual(required, ids)
        self.assertTrue(all(i["status"] == "PASS" for i in result["invariants"]))

    def test_budget_failure_is_not_logical_nogood(self):
        ng = NogoodSet.of()
        self.assertFalse(ng.violated_by(frozenset({"budget-miss"})))
        wp = WarrantProfile.of({"budget-miss"})
        self.assertIs(wp.liveness(()), Liveness.LIVE)

    def test_timeout_does_not_assess_as_jump_without_certificate(self):
        from ocm.kso.jump import JumpProposal, JumpTrigger, JumpLevel, TriggerKind
        trigger = JumpTrigger(
            "t",
            TriggerKind.RESOURCE_EXHAUSTION,
            JumpLevel.ACTION_PARAMETER,
            ("w",),
            ("SEARCH_MORE",),
        )
        self.assertFalse(trigger.is_admissible)
        # RESOURCE_EXHAUSTION is not a strong trigger.

    def test_constitution_class_exists(self):
        self.assertEqual(ChangeClass.C6_CONSTITUTION.value, "C6")


if __name__ == "__main__":
    unittest.main()
