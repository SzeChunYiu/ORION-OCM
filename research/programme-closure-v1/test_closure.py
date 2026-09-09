"""Hostile tests for the #165 programme closure ledger.

This ledger is the artifact that declares a multi-year programme closed. The
failure mode is not an exception, it is flattery: a gate quietly left blank, a
terminal invented that the roadmap never registered, a CANNOT_CHECK that
discloses nothing, a receipt cited but absent, or a positive programme terminal
emitted while gates are unmeasured. Every one of those has a test.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent


def _load():
    spec = importlib.util.spec_from_file_location("closure", HERE / "closure.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


C = _load()


class Vocabularies(unittest.TestCase):
    """The roadmap is the authority; the ledger only reads it."""

    def test_the_vendored_roadmap_body_is_the_one_that_was_pinned(self):
        self.assertTrue(C.body_is_authentic(),
                        "the vendored #165 body does not match its recorded sha256")

    def test_every_gate_vocabulary_is_found_in_the_roadmap(self):
        vocab = C.vocabularies()
        for gate in C.GATES:
            self.assertIn(gate["vocabulary"], vocab, gate["gate"])
            self.assertTrue(vocab[gate["vocabulary"]], gate["gate"])

    def test_vocabularies_are_parsed_not_transcribed(self):
        """If these were retyped, a terminal could be invented. They are read out
        of the body, so a hand-edited body changes the vocabulary and the digest."""
        source = (HERE / "closure.py").read_text()
        self.assertIn("BODY.read_text()", source)
        vocab = C.vocabularies()
        self.assertIn("CANNOT_CHECK_<reason>", vocab["G1 exit terminals"])
        self.assertIn("MINIMUM_SELF_EXTENDING_VESSEL_SUPPORTED_AT_SCOPE",
                      vocab["G1 exit terminals"])

    def test_a_tampered_body_is_detected(self):
        vocab = C.vocabularies("## Fake exit terminals\n\n```text\nINVENTED\n```\n")
        self.assertEqual(vocab["Fake exit terminals"], ("INVENTED",))
        self.assertNotIn("INVENTED", C.vocabularies()["G1 exit terminals"])


class Membership(unittest.TestCase):
    def test_an_unregistered_terminal_is_refused(self):
        self.assertFalse(C.registered(("A", "B"), "C"))

    def test_a_parameterised_terminal_accepts_a_suffix(self):
        self.assertTrue(C.registered(("CANNOT_CHECK_<reason>",),
                                     "CANNOT_CHECK_NO_INTEGRATED_PROTOTYPE_EXISTS"))

    def test_a_bare_parameterised_terminal_discloses_nothing_and_is_refused(self):
        """`CANNOT_CHECK_` with no reason is exactly the terminal that hides an
        unmeasured gate behind the vocabulary meant to expose it."""
        self.assertFalse(C.registered(("CANNOT_CHECK_<reason>",), "CANNOT_CHECK_"))

    def test_partial_signature_needs_a_which(self):
        self.assertFalse(C.registered(("PARTIAL_SIGNATURE_ONLY_<which>",),
                                      "PARTIAL_SIGNATURE_ONLY_"))
        self.assertTrue(C.registered(("PARTIAL_SIGNATURE_ONLY_<which>",),
                                     "PARTIAL_SIGNATURE_ONLY_G2"))


class Validation(unittest.TestCase):
    def _gate(self, **over):
        base = dict(name="X", vocabulary="G1 exit terminals",
                    dispositions=["COMPACT_VESSEL_PARTIAL"],
                    receipts=["research/programme-closure-v1/closure.py"],
                    basis="x" * 120, unconverted=None)
        base.update(over)
        return C.gate(base["name"], base["vocabulary"], base["dispositions"],
                      base["receipts"], base["basis"], base["unconverted"])

    def test_the_real_ledger_validates(self):
        out = C.validate()
        self.assertTrue(out["valid"], out["problems"])

    def test_a_gate_with_no_disposition_is_a_problem(self):
        out = C.validate([self._gate(dispositions=[])])
        self.assertTrue(any(p["why"] == "no disposition" for p in out["problems"]))

    def test_an_unregistered_disposition_is_a_problem(self):
        out = C.validate([self._gate(dispositions=["TOTALLY_INVENTED_WIN"])])
        self.assertTrue(any(p["why"] == "disposition not registered"
                            for p in out["problems"]))

    def test_a_cannot_check_without_a_conversion_is_a_problem(self):
        out = C.validate([self._gate(dispositions=["CANNOT_CHECK_SOMETHING"],
                                     unconverted=None)])
        self.assertTrue(any("without a stated conversion" in p["why"]
                            for p in out["problems"]))

    def test_a_missing_receipt_is_a_problem(self):
        out = C.validate([self._gate(receipts=["research/does-not-exist/nope.json"])])
        self.assertTrue(any(p["why"] == "cited receipt is missing"
                            for p in out["problems"]))

    def test_a_gate_with_no_receipt_at_all_is_a_problem(self):
        out = C.validate([self._gate(receipts=[])])
        self.assertTrue(any(p["why"] == "no receipt cited" for p in out["problems"]))

    def test_a_thin_basis_is_a_problem(self):
        out = C.validate([self._gate(basis="because")])
        self.assertTrue(any("basis too thin" in p["why"] for p in out["problems"]))

    def test_every_real_gate_cites_a_file_that_exists(self):
        for gate in C.GATES:
            for relative in gate["receipts"]:
                self.assertTrue((C.REPO / relative).is_file(),
                                f"{gate['gate']} cites missing {relative}")


class ProgrammeTerminal(unittest.TestCase):
    def _gate(self, name, dispositions, unconverted="something"):
        return C.gate(name, "G1 exit terminals", dispositions,
                      ["research/programme-closure-v1/closure.py"], "x" * 120, unconverted)

    def test_a_gate_without_a_disposition_leaves_the_programme_open(self):
        out = C.programme_terminal([self._gate("A", [])])
        self.assertEqual(out["terminal"], "PROGRAMME_NOT_CLOSED")
        self.assertFalse(out["closed"])

    def test_a_positive_terminal_is_unreachable_while_a_gate_is_unmeasured(self):
        """The single most important test here. An unmeasured gate must not be
        able to sit beside positives and let the programme claim the full
        signature."""
        out = C.programme_terminal([
            self._gate("A", ["MINIMUM_SELF_EXTENDING_VESSEL_SUPPORTED_AT_SCOPE"]),
            self._gate("B", ["CANNOT_CHECK_NOT_RUN"]),
        ])
        self.assertNotEqual(out["terminal"],
                            "HETEROGENEOUS_MACHINE_EPISTEMICS_SIGNATURE_SUPPORTED")
        self.assertTrue(out["terminal"].startswith("PARTIAL_SIGNATURE_ONLY_"))

    def test_the_full_positive_needs_every_gate_positive_and_none_unmeasured(self):
        out = C.programme_terminal([
            self._gate("A", ["MINIMUM_SELF_EXTENDING_VESSEL_SUPPORTED_AT_SCOPE"]),
        ])
        self.assertEqual(out["terminal"],
                         "HETEROGENEOUS_MACHINE_EPISTEMICS_SIGNATURE_SUPPORTED")

    def test_no_positive_anywhere_does_not_become_a_partial_signature(self):
        out = C.programme_terminal([self._gate("A", ["CANNOT_CHECK_NOT_RUN"])])
        self.assertEqual(out["terminal"], "CANNOT_CHECK_NO_GATE_REACHED_A_POSITIVE")

    def test_parent_product_sufficient_is_never_emitted_without_a_prototype(self):
        out = C.programme_terminal()
        self.assertNotEqual(out["terminal"], "PARENT_PRODUCT_SUFFICIENT")
        self.assertIn("integrated prototype", out["reason"])

    def test_the_real_programme_closes_mixed_and_says_so(self):
        out = C.programme_terminal()
        self.assertTrue(out["closed"])
        self.assertTrue(out["terminal"].startswith("PARTIAL_SIGNATURE_ONLY_"))
        self.assertIn("closes MIXED, not positive", out["reason"])
        self.assertTrue(out["unmeasured_gates"])

    def test_every_supported_gate_that_is_parent_sufficient_is_named_as_such(self):
        """Parent-sufficient gates must be NAMED, so a reader can see which
        mechanisms an ordinary parent reproduces -- and named as an absorption,
        which is what section 12 calls it, not as evidence against the thesis."""
        out = C.programme_terminal()
        self.assertIn("G2", out["parent_sufficient_gates"])
        self.assertIn("Ordinary parents reproduce the mechanisms", out["reason"])
        self.assertIn("NOT programme failure", out["reason"])

    def test_the_derivation_rule_is_stated_before_the_dispositions(self):
        source = (HERE / "closure.py").read_text()
        self.assertLess(source.index("DERIVATION"), source.index("def programme_terminal"))
        self.assertIn("written before the dispositions were filled in", source)


class Coverage(unittest.TestCase):
    def test_every_gate_named_in_the_roadmap_has_a_ledger_entry(self):
        """Closure is 'every REQUIRED gate'. A gate the roadmap registers a
        terminal vocabulary for but the ledger omits would be a silent gap."""
        vocab = set(C.vocabularies())
        covered = {g["vocabulary"] for g in C.GATES}
        missing = {v for v in vocab if v.endswith("exit terminals")} - covered
        self.assertFalse(missing, f"gates with a vocabulary but no disposition: {missing}")

    def test_the_ledger_disclaims_its_own_authority(self):
        doc = C.build()
        self.assertIn("closes no issue on its own authority", doc["what_this_does_not_do"])
        self.assertIn("runs no study", doc["what_this_does_not_do"])




class IssueTerminals(unittest.TestCase):
    """Section 22's Final list must also be complete, and must not drift from the
    gate ledger."""

    def test_every_governing_issue_in_the_final_list_has_a_terminal(self):
        expected = {38, 42, 49, 50, 62, 69, 70, 71, 72, 73, 93, 115, 143, 144, 145,
                    149, 151, 152}
        self.assertEqual({int(k) for k in C.issue_terminals()}, expected)

    def test_an_issue_that_owns_a_gate_inherits_it_exactly(self):
        out = C.issue_terminals()
        gates = {g["gate"]: g for g in C.GATES}
        for issue, row in out.items():
            owner = row["inherited_from_gate"]
            if owner:
                self.assertEqual(row["terminal"], gates[owner]["dispositions"], issue)
                self.assertEqual(row["receipts"], gates[owner]["receipts"], issue)

    def test_an_issue_without_a_lane_says_so_rather_than_guessing(self):
        out = C.issue_terminals()
        self.assertTrue(out["49"]["terminal"][0].startswith("CANNOT_CHECK_NO_LANE_ON_THIS_HEAD"))
        self.assertIsNone(out["49"]["inherited_from_gate"])

    def test_every_issue_terminal_cites_a_receipt_that_exists(self):
        for issue, row in C.issue_terminals().items():
            self.assertTrue(row["receipts"], issue)
            for relative in row["receipts"]:
                self.assertTrue((C.REPO / relative).is_file(), f"#{issue}: {relative}")

    def test_71_inherits_the_router_terminal_and_stays_blocked(self):
        self.assertIn("LEARNED_ROUTER_NOT_NEEDED", C.issue_terminals()["71"]["terminal"])




class AbsorptionDoctrine(unittest.TestCase):
    """Section 12 says PARENT_SUFFICIENT is not programme failure. An earlier draft
    of this ledger read the collection of parent-sufficient mechanisms as the
    decisive negative finding, which inverts the doctrine. These tests exist so
    that error cannot come back."""

    def test_the_roadmap_says_parent_sufficient_is_not_failure(self):
        body = C.BODY.read_text()
        self.assertIn("`PARENT_SUFFICIENT` is not programme failure.", body)
        self.assertIn("OCM must rediscover all existing algorithms itself", body)
        self.assertIn("every learned component must be novel", body)

    def test_a_parent_sufficient_gate_still_counts_as_supported(self):
        out = C.programme_terminal()
        supported = {g for g, _ in
                     [(r["gate"], r["disposition"]) for r in out["supported_gates"]]}
        self.assertIn("G2", supported)
        self.assertIn("G2", out["parent_sufficient_gates"])

    def test_the_reason_does_not_read_parent_sufficiency_as_evidence_against(self):
        reason = C.programme_terminal()["reason"]
        self.assertIn("NOT programme failure", reason)
        self.assertIn("designed absorption", reason)
        self.assertNotIn("none of the supported parts is an architecture residual", reason)

    def test_the_derivation_puts_the_novelty_question_one_level_up(self):
        self.assertIn("mere component integration remains", C.DERIVATION)
        for target in ("developmental law", "cross-domain invariance", "phase boundary",
                       "lifetime regime", "principled impossibility"):
            self.assertIn(target, C.DERIVATION)


class UpperLevel(unittest.TestCase):
    def test_every_section_12_upward_target_has_a_disposition(self):
        expected = {"developmental_law", "cross_domain_invariance", "phase_boundary",
                    "lifetime_regime", "principled_impossibility",
                    "integrated_interaction_effect"}
        self.assertEqual(set(C.UPPER_LEVEL), expected)

    def test_every_upper_level_receipt_exists(self):
        for name, row in C.UPPER_LEVEL.items():
            self.assertTrue(row["receipts"], name)
            for relative in row["receipts"]:
                self.assertTrue((C.REPO / relative).is_file(), f"{name}: {relative}")

    def test_every_upper_level_candidate_states_its_boundary(self):
        """An E2 synthetic candidate that does not say it is synthetic would be the
        most damaging overclaim available to this programme."""
        for name, row in C.UPPER_LEVEL.items():
            self.assertTrue(row["boundary"], name)
        self.assertIn("synthetic", C.UPPER_LEVEL["phase_boundary"]["boundary"].lower())

    def test_the_validator_checks_upper_level_receipts_too(self):
        out = C.validate()
        self.assertTrue(out["valid"], out["problems"])
        source = (HERE / "closure.py").read_text()
        self.assertIn("for name, row in UPPER_LEVEL.items():", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
