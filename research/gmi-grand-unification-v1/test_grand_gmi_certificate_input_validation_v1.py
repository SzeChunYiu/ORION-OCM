"""Hostile packets must not become finite NN/non-NN derivation certificates."""

import contextlib
import importlib.util
import io
import json
from fractions import Fraction
from decimal import Decimal
from itertools import permutations
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent


def load(stem):
    spec = importlib.util.spec_from_file_location(stem, HERE / (stem + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


D = load("grand_gmi_nn_nonnn_derivation_certificate_checks_v1")
E = load("grand_gmi_nn_nonnn_empirical_protocol_checks_v1")
UNDECIDED = "UNDECIDED_FROM_CURRENT_EVIDENCE"


def derive(candidates, **kwargs):
    return D.derive(candidates, profile_dimension=2, **kwargs)


class DerivationInputTests(unittest.TestCase):
    def packet(self):
        return [D.candidate("N", "NEURAL", (1, 1)),
                D.candidate("P", "NON_NEURAL", (2, 2))]

    def test_truncated_profile_cannot_win(self):
        packet = [D.candidate("N", "NEURAL", (1,)),
                  D.candidate("P", "NON_NEURAL", (2, 0))]
        self.assertEqual(derive(packet)[0], UNDECIDED)

    def test_registered_dimension_is_required_and_not_inferred(self):
        self.assertEqual(D.derive(self.packet())[0], UNDECIDED)
        for dimension in (None, False, 0, -1, 2.0, "2", 3):
            with self.subTest(dimension=dimension):
                self.assertEqual(D.derive(self.packet(), profile_dimension=dimension)[0], UNDECIDED)
        both_truncated = [D.candidate("N", "NEURAL", (1,)),
                          D.candidate("P", "NON_NEURAL", (2,))]
        self.assertEqual(derive(both_truncated)[0], UNDECIDED)

    def test_raw_dominance_rejects_incomparable_dimensions(self):
        with self.assertRaises(ValueError):
            D.dominates({"profile": (1,)}, {"profile": (2, 0)})

    def test_invalid_resource_coordinates_abstain(self):
        for profile in [(), (True, 0), (float("nan"), 0),
                        (float("inf"), 0), (float("-inf"), 0), ("1", "1"),
                        (Decimal("NaN"), 0), (Decimal("sNaN"), 0),
                        (Decimal("Infinity"), 0)]:
            with self.subTest(profile=profile):
                packet = self.packet()
                packet[0]["profile"] = profile
                self.assertEqual(derive(packet)[0], UNDECIDED)

    def test_duplicate_or_unknown_identity_abstains(self):
        for field, value in [("name", "P"), ("name", ""),
                             ("family", "ALIEN")]:
            with self.subTest(field=field, value=value):
                packet = self.packet()
                packet[0][field] = value
                self.assertEqual(derive(packet)[0], UNDECIDED)

    def test_missing_or_nonboolean_hard_evidence_abstains(self):
        for field in ("realization_valid", "adequate", "substrate_legal",
                      "reachable", "hard_feasible"):
            for value in (None, "false", 0, 1):
                with self.subTest(field=field, value=value):
                    packet = self.packet()
                    packet[0][field] = value
                    self.assertEqual(derive(packet)[0], UNDECIDED)
            packet = self.packet()
            del packet[0][field]
            with self.subTest(field=field, missing=True):
                self.assertEqual(derive(packet)[0], UNDECIDED)

    def test_packet_evidence_flags_are_boolean(self):
        for kwargs in ({"evidence_complete": "false"},
                       {"evidence_ambiguous": 0},
                       {"receipt_consistent": 1}):
            with self.subTest(kwargs=kwargs):
                self.assertEqual(derive(self.packet(), **kwargs)[0], UNDECIDED)

    def test_invalid_packets_abstain(self):
        for packet in (None, "not a registry", [None], [{}]):
            with self.subTest(packet=packet):
                self.assertEqual(derive(packet)[0], UNDECIDED)

    def test_proved_inadequacy_is_distinct_from_unknown_evidence(self):
        packet = self.packet()
        packet[0]["adequate"] = False
        self.assertEqual(derive(packet)[0], "DERIVED_NON_NEURAL")
        packet[0]["adequate"] = None
        self.assertEqual(derive(packet)[0], UNDECIDED)

    def test_valid_exact_profiles_are_order_independent(self):
        packet = [D.candidate("N", "NEURAL", (Fraction(1, 3), 10 ** 400)),
                  D.candidate("P", "NON_NEURAL", (Fraction(2, 3), 10 ** 400))]
        for order in permutations(packet):
            self.assertEqual(derive(list(order)),
                             ("DERIVED_NEURAL", ["N"], ["NEURAL"]))
        packet[0]["profile"] = (Decimal("0.3"), 10 ** 400)
        self.assertEqual(derive(packet)[0], "DERIVED_NEURAL")


class EmpiricalInputTests(unittest.TestCase):
    def packet(self):
        return [E.c("N", "NEURAL", 8, 9), E.c("P", "NON_NEURAL", 11, 13)]

    def test_missing_deployment_cannot_eliminate_a_competitor(self):
        packet = [E.c("N", "NEURAL", 8, 9),
                  E.c("P", "NON_NEURAL", 1, 2, deploy=False)]
        self.assertEqual(E.adjudicate_scalar(packet), UNDECIDED)
        packet[0]["deployment_evidence_present"] = False
        self.assertEqual(E.adjudicate_scalar(packet), UNDECIDED)

    def test_inverted_nonfinite_or_nonnumeric_intervals_abstain(self):
        for lo, hi in [(100, 1), (float("nan"), 1), (1, float("nan")),
                       (0, float("inf")), (float("-inf"), 1), (False, 1),
                       ("1", "2"), (Decimal("sNaN"), 1),
                       (0, Decimal("Infinity"))]:
            with self.subTest(lo=lo, hi=hi):
                packet = [E.c("N", "NEURAL", lo, hi),
                          E.c("P", "NON_NEURAL", 2, 101)]
                self.assertEqual(E.adjudicate_scalar(packet), UNDECIDED)

    def test_missing_or_nonboolean_evidence_abstains(self):
        for field in ("hard_gate_pass", "development_reached",
                      "deployment_evidence_present"):
            for value in (None, "false", 0, 1):
                with self.subTest(field=field, value=value):
                    packet = self.packet()
                    packet[0][field] = value
                    self.assertEqual(E.adjudicate_scalar(packet), UNDECIDED)
            packet = self.packet()
            del packet[0][field]
            with self.subTest(field=field, missing=True):
                self.assertEqual(E.adjudicate_scalar(packet), UNDECIDED)

    def test_duplicate_or_unknown_identity_abstains(self):
        for field, value in [("candidate_id", "P"), ("candidate_id", ""),
                             ("family", "ALIEN")]:
            with self.subTest(field=field, value=value):
                packet = self.packet()
                packet[0][field] = value
                self.assertEqual(E.adjudicate_scalar(packet), UNDECIDED)

    def test_packet_evidence_flag_is_boolean(self):
        for value in (None, "false", 0, 1):
            self.assertEqual(E.adjudicate_scalar(self.packet(), value), UNDECIDED)

    def test_invalid_packets_abstain(self):
        for packet in (None, "not a registry", [None], [{}]):
            with self.subTest(packet=packet):
                self.assertEqual(E.adjudicate_scalar(packet), UNDECIDED)

    def test_explicit_gate_failure_can_exclude_without_deployment(self):
        packet = [E.c("N", "NEURAL", 8, 9),
                  E.c("P", "NON_NEURAL", 1, 2, hard=False, deploy=False)]
        self.assertEqual(E.adjudicate_scalar(packet),
                         "DERIVED_NEURAL_AT_REGISTERED_SCOPE")
        packet[0]["hard_gate_pass"] = False
        self.assertEqual(E.adjudicate_scalar(packet), "INFEASIBLE_AT_REGISTERED_SCOPE")

    def test_valid_exact_intervals_and_ties_are_order_independent(self):
        packet = [E.c("N", "NEURAL", Fraction(1, 3), Fraction(1, 2)),
                  E.c("P", "NON_NEURAL", 10 ** 400, 10 ** 400)]
        for order in permutations(packet):
            self.assertEqual(E.adjudicate_scalar(list(order)),
                             "DERIVED_NEURAL_AT_REGISTERED_SCOPE")
        self.assertEqual(E.adjudicate_scalar([E.c("N", "NEURAL", 1, 2),
                                             E.c("P", "NON_NEURAL", 2, 3)]), UNDECIDED)


class FrozenReceiptCompatibilityTests(unittest.TestCase):
    def test_receipts_equal_current_synthetic_execution(self):
        for module, name in [(D, "GRAND_GMI_NN_NONNN_DERIVATION_CERTIFICATE_RECEIPT_V1.json"),
                             (E, "GRAND_GMI_NN_NONNN_EMPIRICAL_PROTOCOL_RECEIPT_V1.json")]:
            with self.subTest(receipt=name):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    module.main()
                self.assertEqual(json.loads(output.getvalue()),
                                 json.loads((HERE / name).read_text()))


if __name__ == "__main__":
    unittest.main()
