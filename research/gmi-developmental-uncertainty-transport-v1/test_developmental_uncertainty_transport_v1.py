import itertools
import importlib.util
from fractions import Fraction as F
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("dut", HERE / "developmental_uncertainty_transport_v1.py")
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)

TransportContract = MOD.TransportContract
TransportCampaign = MOD.TransportCampaign
ConfidenceObject = MOD.ConfidenceObject


def simple_contract(beta=F(0)):
    x0 = (F(0), F(1))
    x1 = (F(0), F(1), F(2))
    return TransportContract("step", 0, 1, "INFO", x0, x1, ((F(0), F(1)), (F(1), F(2))), beta)


class ContractValidationTests(unittest.TestCase):
    def test_exact_contract_accepted(self):
        c = simple_contract()
        self.assertEqual(c.to_version, 1)

    def test_contract_is_frozen(self):
        c = simple_contract()
        with self.assertRaises(Exception):
            c.name = "changed"

    def test_version_skip_rejected(self):
        with self.assertRaises(ValueError):
            TransportContract("bad", 0, 2, "INFO", (F(0),), (F(0),), ((F(0), F(0)),))

    def test_back_edge_rejected(self):
        with self.assertRaises(ValueError):
            TransportContract("bad", 2, 1, "INFO", (F(0),), (F(0),), ((F(0), F(0)),))

    def test_unknown_kind_rejected(self):
        with self.assertRaises(ValueError):
            TransportContract("bad", 0, 1, "MAGIC", (F(0),), (F(0),), ((F(0), F(0)),))

    def test_incomplete_relation_rejected(self):
        with self.assertRaises(ValueError):
            TransportContract("bad", 0, 1, "INFO", (F(0), F(1)), (F(0),), ((F(0), F(0)),))

    def test_out_of_domain_source_rejected(self):
        with self.assertRaises(ValueError):
            TransportContract("bad", 0, 1, "INFO", (F(0),), (F(0),), ((F(1), F(0)),))

    def test_out_of_domain_target_rejected(self):
        with self.assertRaises(ValueError):
            TransportContract("bad", 0, 1, "INFO", (F(0),), (F(0),), ((F(0), F(1)),))

    def test_float_budget_rejected(self):
        with self.assertRaises(ValueError):
            simple_contract(0.1)

    def test_negative_budget_rejected(self):
        with self.assertRaises(ValueError):
            simple_contract(F(-1, 10))

    def test_over_one_budget_rejected(self):
        with self.assertRaises(ValueError):
            simple_contract(F(11, 10))


class CampaignGovernanceTests(unittest.TestCase):
    def test_post_activation_registration_rejected(self):
        c = simple_contract()
        camp = TransportCampaign(0, c.source_domain, F(1, 20))
        camp.activate_source((F(0),))
        with self.assertRaises(RuntimeError):
            camp.register(c)

    def test_source_outside_domain_rejected(self):
        camp = TransportCampaign(0, (F(0), F(1)), F(1, 20))
        with self.assertRaises(ValueError):
            camp.activate_source((F(2),))

    def test_chain_source_domain_mismatch_rejected(self):
        camp = TransportCampaign(0, (F(0),), F(0))
        bad = TransportContract("bad", 0, 1, "INFO", (F(1),), (F(1),), ((F(1), F(1)),))
        with self.assertRaises(ValueError):
            camp.register(bad)

    def test_chain_version_mismatch_rejected(self):
        c = simple_contract()
        camp = TransportCampaign(0, c.source_domain, F(0))
        camp.register(c)
        wrong = TransportContract("wrong", 0, 1, "INFO", c.source_domain, c.target_domain, c.relation)
        with self.assertRaises(ValueError):
            camp.register(wrong)

    def test_propagate_before_activation_rejected(self):
        camp = TransportCampaign(0, (F(0),), F(0))
        with self.assertRaises(RuntimeError):
            camp.propagate_all()


class ImageAndBudgetTests(unittest.TestCase):
    def test_relational_image_matches_independent_comprehension(self):
        values = (F(-1), F(1))
        relation = tuple((F(x), F(y)) for x in range(-2, 3) for y in range(-2, 3) if (x + y) % 2 == 0)
        actual = MOD.relational_image(values, relation)
        expected = tuple(sorted({y for x, y in relation if x in set(values)}))
        self.assertEqual(actual, expected)

    def test_exact_relation_preserves_failure_budget(self):
        c = simple_contract(F(0))
        camp = TransportCampaign(0, c.source_domain, F(1, 20))
        camp.register(c)
        camp.activate_source((F(0),))
        target = camp.propagate_all()[-1]
        self.assertEqual(target.failure_budget, F(1, 20))

    def test_uncertain_relation_adds_budget_without_independence(self):
        c = simple_contract(F(1, 100))
        camp = TransportCampaign(0, c.source_domain, F(1, 20))
        camp.register(c)
        camp.activate_source((F(0),))
        self.assertEqual(camp.propagate_all()[-1].failure_budget, F(3, 50))

    def test_two_uncertain_betas_frozen_result(self):
        self.assertEqual(MOD.cumulative_failure(F(1, 20), (F(1, 100), F(1, 200))), F(13, 200))
        self.assertEqual(F(1) - F(13, 200), F(187, 200))

    def test_countable_beta_allocation_telescopes(self):
        beta = F(1, 20)
        for n in (1, 2, 5, 1000):
            partial = sum((MOD.beta_allocation(beta, t) for t in range(1, n + 1)), F(0))
            self.assertEqual(partial, beta * F(n, n + 1))
            self.assertLess(partial, beta)
        self.assertEqual(F(1) - F(1,20) - beta, F(9,10))

    def test_failure_budget_caps_at_one(self):
        self.assertEqual(MOD.cumulative_failure(F(9,10), (F(1,5),)), F(1))


class FiveKindChainTests(unittest.TestCase):
    def setUp(self):
        self.contracts = MOD._five_kind_contracts()
        self.camp = TransportCampaign(0, self.contracts[0].source_domain, F(1,20))
        for c in self.contracts:
            self.camp.register(c)
        self.source = self.camp.activate_source((F(-1), F(0), F(1)), raw_evidence_count=2048)
        self.chain = self.camp.propagate_all()

    def test_all_five_registered_kinds_appear(self):
        self.assertEqual(tuple(c.change_kind for c in self.contracts), MOD.ALLOWED_KINDS)

    def test_frozen_images(self):
        expected = (
            (F(-1), F(0), F(1)),
            (F(0), F(1), F(2)),
            (F(0), F(1), F(2)),
            (F(0), F(1), F(2), F(3)),
            (F(-1), F(0), F(1), F(2), F(3), F(4)),
            (F(0), F(1), F(4), F(9), F(16)),
        )
        self.assertEqual(tuple(x.values for x in self.chain), expected)

    def test_exact_chain_preserves_alpha(self):
        self.assertEqual({x.failure_budget for x in self.chain}, {F(1,20)})

    def test_target_versions_inherit_no_raw_evidence(self):
        self.assertEqual(self.source.raw_evidence_count, 2048)
        self.assertTrue(all(x.raw_evidence_count == 0 for x in self.chain[1:]))


class IgnoranceTests(unittest.TestCase):
    def setUp(self):
        self.obj = ConfidenceObject(5, (F(0), F(1)), (F(0),), F(1,20), "TRANSPORTED", 0)
        self.camp = TransportCampaign(0, (F(0),), F(1,20))

    def test_no_relation_returns_full_target_domain(self):
        target = self.camp.propagate_unknown(self.obj, 6, (F(0), F(1), F(2)))
        self.assertEqual(target.values, (F(0), F(1), F(2)))
        self.assertEqual(target.terminal, "CANNOT_IDENTIFY_NO_RELATION")
        self.assertEqual(target.raw_evidence_count, 0)

    def test_no_relation_does_not_copy_source_set(self):
        target = self.camp.propagate_unknown(self.obj, 6, (F(0), F(1)))
        self.assertNotEqual(target.values, self.obj.values)
        self.assertEqual(target.values, target.domain)

    def test_arbitrary_update_copying_has_zero_coverage_counterexample(self):
        source_set = {F(0)}
        target_truth = F(1)
        self.assertNotIn(target_truth, source_set)
        self.assertIn(target_truth, {F(0), F(1)})

    def test_mixed_query_abstains(self):
        target = self.camp.propagate_unknown(self.obj, 6, (F(0), F(1), F(2)))
        table = {F(0): False, F(1): True, F(2): True}
        self.assertEqual(MOD.identify_boolean(target, table), "CANNOT_IDENTIFY")

    def test_constant_query_identified_even_under_state_ignorance(self):
        target = self.camp.propagate_unknown(self.obj, 6, (F(0), F(1), F(2)))
        table = {x: True for x in target.domain}
        self.assertEqual(MOD.identify_boolean(target, table), "IDENTIFIED_TRUE")


class ExactSpecialCaseTests(unittest.TestCase):
    def test_interval_affine_frozen_result(self):
        self.assertEqual(MOD.affine_interval(F(1,4), F(3,4), F(-2), F(3), F(1,10)), (F(7,5), F(13,5)))

    def test_interval_affine_matches_exhaustive_corners(self):
        lo, hi, a, b, eps = F(1,4), F(3,4), F(-2), F(3), F(1,10)
        brute = [a*x + b + e for x, e in itertools.product((lo, hi), (-eps, eps))]
        self.assertEqual(MOD.affine_interval(lo, hi, a, b, eps), (min(brute), max(brute)))

    def test_nonlinear_set_valued_image(self):
        src = (F(-1), F(0), F(1))
        relation = MOD.relation_from_successors(src, lambda x: (x*x - 1, x*x, x*x + 1))
        self.assertEqual(MOD.relational_image(src, relation), (F(-1), F(0), F(1), F(2)))


class ReceiptTests(unittest.TestCase):
    def test_receipt_deterministic_and_frozen(self):
        a = MOD.build_receipt()
        b = MOD.build_receipt()
        self.assertEqual(a, b)
        self.assertEqual(a["interval_affine"]["result"], ["7/5", "13/5"])
        self.assertEqual(a["nonlinear_relation"]["result"], ["-1", "0", "1", "2"])
        self.assertEqual(a["uncertain_relation_budget"]["failure_budget"], "13/200")
        self.assertEqual(a["unknown_relation"]["mixed_query"], "CANNOT_IDENTIFY")
        self.assertTrue(a["target_evidence_noninheritance"])
        self.assertTrue(a["no_independence_assumption"])


if __name__ == "__main__":
    unittest.main()
