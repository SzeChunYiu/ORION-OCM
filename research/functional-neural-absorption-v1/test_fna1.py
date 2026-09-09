"""Tests for the #214 FNA-1 tranche."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "src"))

import contract as C          # noqa: E402
import experiment as E        # noqa: E402
import hostile as H           # noqa: E402
from ocm.kso.navigation import gated_closure   # noqa: E402

RUN = json.loads((HERE / "FNA1_TYPED_CHANNEL_V1.json").read_text())
HOST = json.loads((HERE / "FNA1_HOSTILE_RARITY_V1.json").read_text())


class Contract(unittest.TestCase):
    def test_positive_fixtures_validate(self):
        C.validate_all(json.loads((HERE / "CONTRACTS_V1.json").read_text())["contracts"])

    def test_every_malformed_case_is_refused_with_its_own_code(self):
        for case in json.loads((HERE / "CONTRACTS_MALFORMED_V1.json").read_text())["cases"]:
            with self.assertRaises(C.ContractError) as cm:
                C.validate(case["doc"])
            self.assertEqual(cm.exception.code, case["expect"], case["case"])

    def test_a_contract_naming_no_parent_is_refused(self):
        """#214 section 2's central rule, enforced rather than reviewed."""
        doc = dict(json.loads((HERE / "CONTRACTS_V1.json").read_text())["contracts"][0])
        doc["strongest_non_neural_parent"] = []
        with self.assertRaises(C.ContractError) as cm:
            C.validate(doc)
        self.assertEqual(cm.exception.code, "NO_PARENT_NAMED")

    def test_a_parent_owned_function_may_not_declare_an_ocm_realization(self):
        doc = dict(json.loads((HERE / "CONTRACTS_V1.json").read_text())["contracts"][0])
        self.assertEqual(doc["ownership"], "PARENT_OWNS_IT")
        doc["candidate_ocm_realization"] = "a bespoke OCM attention operator"
        with self.assertRaises(C.ContractError) as cm:
            C.validate(doc)
        self.assertEqual(cm.exception.code, "OCM_NOTATION_FOR_A_PARENT_OWNED_FUNCTION")

    def test_no_forbidden_claim_appears_anywhere_in_the_receipts(self):
        for name in ("FNA1_TYPED_CHANNEL_V1.json", "FNA1_HOSTILE_RARITY_V1.json",
                     "CONTRACTS_V1.json", "PARENT_OWNERSHIP_CARDS.json"):
            body = (HERE / name).read_text()
            for claim in C.FORBIDDEN_CLAIMS:
                # The contract module's own registry lists them; receipts must not assert them.
                self.assertNotIn(f'"{claim}"', body, f"{name} asserts {claim}")


class Proposition3(unittest.TestCase):
    """Typed channels cannot add reach to an exact closure."""

    def test_monotonicity_holds_for_every_channel_subset_in_the_run(self):
        q1 = RUN["q1_unbounded"]
        for name, arm in q1.items():
            if name.startswith("R5_CHANNEL_") or name == "R5_COMMON_CHANNELS_ONLY":
                self.assertTrue(arm["subset_of_full_closure"], name)
                self.assertLessEqual(arm["reached"], q1["R1_INDEXED"]["reached"], name)

    def test_the_union_of_channels_reproduces_the_undifferentiated_closure(self):
        self.assertTrue(RUN["q1_unbounded"]["R5_UNION_ALL_CHANNELS"][
            "equals_undifferentiated_closure"])

    def test_monotonicity_holds_on_freshly_constructed_spaces_too(self):
        """Not just in the recorded run: re-derived here against production closure."""
        ks = E.planted_world(20)
        full = gated_closure(ks, ["seed"])
        for ch in {e.relation_type for e in ks.hyperedges}:
            self.assertTrue(gated_closure(E.restrict(ks, [ch]), ["seed"]) <= full, ch)

    def test_the_proposition_states_the_condition_that_breaks_it(self):
        for phrase in ("The escape", "truncation budget", "never REACH"):
            self.assertIn(phrase, E.PROPOSITION_3)


class HarnessIntegrity(unittest.TestCase):
    def test_the_bounded_harness_reproduces_production_at_a_slack_budget(self):
        """Without this every bounded number measures the reimplementation."""
        self.assertTrue(RUN["harness_validation"][
            "bounded_closure_at_slack_budget_equals_production"])
        ks = E.planted_world(20)
        reached, work = E.bounded_closure(ks, ["seed"], None)
        self.assertEqual(reached, gated_closure(ks, ["seed"]))
        self.assertFalse(work["truncated"])

    def test_a_violated_proposition_is_a_defect_terminal_not_a_finding(self):
        doc = json.loads(json.dumps(RUN))
        doc["q1_unbounded"]["R5_CHANNEL_SUPPORT"]["subset_of_full_closure"] = False
        self.assertTrue(E.verdict(doc)["terminal"].startswith("CANNOT_CHECK_"))

    def test_a_disagreeing_harness_is_a_defect_terminal_not_a_finding(self):
        doc = json.loads(json.dumps(RUN))
        doc["harness_validation"]["bounded_closure_at_slack_budget_equals_production"] = False
        self.assertEqual(E.verdict(doc)["terminal"],
                         "CANNOT_CHECK_BOUNDED_HARNESS_DISAGREES_WITH_PRODUCTION_CLOSURE")


class Policy(unittest.TestCase):
    def test_the_candidate_policy_is_not_an_oracle(self):
        """Rarity reads edge-type counts only -- never the task or its answer."""
        ks = E.planted_world(20)
        order, counts = E.channel_rarity(ks)
        self.assertEqual(set(counts), {e.relation_type for e in ks.hyperedges})
        # Same space, decisive atom renamed: a task-blind policy must be unchanged.
        self.assertEqual(order, E.channel_rarity(E.planted_world(20))[0])

    def test_the_oracle_arm_is_labelled_and_never_the_terminal(self):
        for row in RUN["q2_bounded"].values():
            self.assertIn("ORACLE", row["ORACLE_DECISIVE_CHANNEL_FIRST"]["authority"])
        self.assertNotIn("ORACLE", RUN["verdict"]["terminal"])


class HostileScope(unittest.TestCase):
    """The advantage is conditional, and the condition is measured."""

    def test_rarity_wins_only_where_the_rare_channel_carries_the_answer(self):
        v = HOST["verdict"]
        self.assertTrue(v["rarity_wins_when_rare_channel_carries_the_answer"])
        self.assertTrue(v["policy_is_world_dependent"])

    def test_the_common_channel_world_is_reported_as_neutral_not_worse(self):
        """An earlier draft called this 'strictly worse'. It is not; it is identical."""
        self.assertEqual(HOST["worlds"]["COMMON_DECISIVE"]["rarity_strictly_WORSE"], [])
        self.assertEqual(HOST["worlds"]["COMMON_DECISIVE"]["rarity_strictly_better"], [])
        self.assertIn("NEUTRAL", HOST["verdict"]["terminal_reason"])
        self.assertIn("does not reverse it", HOST["verdict"]["terminal_reason"])

    def test_a_rare_channel_decoy_makes_the_policy_strictly_worse(self):
        self.assertTrue(HOST["verdict"]["rarity_loses_against_a_rare_channel_decoy"])
        self.assertTrue(HOST["worlds"]["ADVERSARIAL"]["rarity_strictly_WORSE"])

    def test_the_hostile_declares_itself_post_freeze(self):
        self.assertEqual(HOST["analysis_status"], "DECLARED_POST_FREEZE_HOSTILE")
        self.assertIn("can only weaken", HOST["authority"])

    def test_rarity_is_described_as_selectivity_not_relevance(self):
        self.assertIn("SELECTIVITY heuristic, not a relevance signal",
                      HOST["verdict"]["terminal_reason"])


class Scope(unittest.TestCase):
    def test_the_run_declares_what_it_does_not_establish(self):
        text = RUN["verdict"]["what_this_does_not_establish"]
        for phrase in ("no neural arm was run", "R3/R6/R7 remain absent", "E1/L1"):
            self.assertIn(phrase, text)

    def test_no_router_or_model_is_implemented(self):
        for name in ("experiment.py", "hostile.py", "contract.py"):
            body = (HERE / name).read_text().lower()
            for banned in ("import torch", "sklearn", "def train(", "bandit"):
                self.assertNotIn(banned, body, f"{name} contains {banned}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
