import importlib.util
import itertools
from fractions import Fraction as F
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("ea", HERE / "epistemic_aleatoric_v1.py")
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)

LatentState = MOD.LatentState
FiniteLatentModel = MOD.FiniteLatentModel
MarginalOnly = MOD.MarginalOnly


def state(label, weight, kernel):
    return LatentState(label, weight, tuple(kernel))


class ValidationTests(unittest.TestCase):
    def test_empty_latent_space_rejected(self):
        with self.assertRaises(ValueError):
            FiniteLatentModel(())

    def test_duplicate_labels_rejected(self):
        first = state("a", F(1, 2), ((F(0), F(1)),))
        with self.assertRaises(ValueError):
            FiniteLatentModel((first, state("a", F(1, 2), ((F(1), F(1)),))))

    def test_weights_must_sum_one(self):
        with self.assertRaises(ValueError):
            FiniteLatentModel((state("a", F(1, 2), ((F(0), F(1)),)),))

    def test_float_weight_rejected(self):
        with self.assertRaises(ValueError):
            state("a", 0.5, ((F(0), F(1)),))

    def test_negative_weight_rejected(self):
        with self.assertRaises(ValueError):
            state("a", F(-1, 2), ((F(0), F(1)),))

    def test_float_outcome_rejected(self):
        with self.assertRaises(ValueError):
            state("a", F(1), ((0.0, F(1)),))

    def test_float_probability_rejected(self):
        with self.assertRaises(ValueError):
            state("a", F(1), ((F(0), 1.0),))

    def test_kernel_must_sum_one(self):
        with self.assertRaises(ValueError):
            state("a", F(1), ((F(0), F(1, 2)),))

    def test_duplicate_kernel_outcomes_rejected(self):
        with self.assertRaises(ValueError):
            state("a", F(1), ((F(0), F(1, 2)), (F(0), F(1, 2))))

    def test_empty_kernel_rejected(self):
        with self.assertRaises(ValueError):
            state("a", F(1), ())

    def test_empty_label_rejected(self):
        with self.assertRaises(ValueError):
            state("", F(1), ((F(0), F(1)),))


class FrozenModelTests(unittest.TestCase):
    def setUp(self):
        self.pa, self.pe, self.mx, self.sm, self.zw = MOD.frozen_models()

    def test_pure_aleatoric(self):
        result = MOD.decompose_model(self.pa)
        self.assertEqual((result.aleatoric, result.epistemic_mean, result.total), (F(1), F(0), F(1)))

    def test_pure_epistemic_mean(self):
        result = MOD.decompose_model(self.pe)
        self.assertEqual((result.aleatoric, result.epistemic_mean, result.total), (F(0), F(1), F(1)))

    def test_mixed_exact(self):
        result = MOD.decompose_model(self.mx)
        self.assertEqual(
            (result.mean, result.aleatoric, result.epistemic_mean, result.total),
            (F(0), F(1, 4), F(1, 4), F(1, 2)),
        )

    def test_same_mean_different_kernels(self):
        result = MOD.decompose_model(self.sm)
        self.assertEqual(result.epistemic_mean, F(0))
        self.assertFalse(result.positive_weight_kernels_identical)
        self.assertEqual(result.aleatoric, F(1, 2))

    def test_nonidentifiability_same_full_marginal(self):
        aleatoric = MOD.decompose_model(self.pa)
        epistemic = MOD.decompose_model(self.pe)
        self.assertEqual(aleatoric.marginal, epistemic.marginal)
        self.assertNotEqual(
            (aleatoric.aleatoric, aleatoric.epistemic_mean),
            (epistemic.aleatoric, epistemic.epistemic_mean),
        )

    def test_zero_weight_state_is_inert(self):
        base = MOD.decompose_model(self.pa)
        extended = MOD.decompose_model(self.zw)
        self.assertEqual(
            (base.mean, base.aleatoric, base.epistemic_mean, base.total, base.marginal),
            (extended.mean, extended.aleatoric, extended.epistemic_mean, extended.total, extended.marginal),
        )
        self.assertEqual(
            base.positive_weight_kernels_identical,
            extended.positive_weight_kernels_identical,
        )

    def test_marginal_only_fails_closed(self):
        result = MOD.decompose_model(self.pa)
        self.assertEqual(MOD.decompose(MarginalOnly(result.marginal)), MOD.CANNOT)

    def test_unsupported_object_rejected(self):
        with self.assertRaises(ValueError):
            MOD.decompose({"marginal": 1})


class InvarianceTests(unittest.TestCase):
    def test_latent_relabeling_invariant(self):
        first = FiniteLatentModel(
            (
                state("L", F(1, 3), ((F(-1), F(1, 2)), (F(0), F(1, 2)))),
                state("R", F(2, 3), ((F(0), F(1, 4)), (F(2), F(3, 4)))),
            )
        )
        second = FiniteLatentModel(
            (
                state("x", F(2, 3), ((F(0), F(1, 4)), (F(2), F(3, 4)))),
                state("y", F(1, 3), ((F(-1), F(1, 2)), (F(0), F(1, 2)))),
            )
        )
        a = MOD.decompose_model(first)
        b = MOD.decompose_model(second)
        self.assertEqual(
            (a.mean, a.aleatoric, a.epistemic_mean, a.total, a.marginal),
            (b.mean, b.aleatoric, b.epistemic_mean, b.total, b.marginal),
        )

    def test_zero_probability_representation_does_not_change_kernel_identity(self):
        model = FiniteLatentModel(
            (
                state("a", F(1, 2), ((F(-1), F(1, 2)), (F(0), F(0)), (F(1), F(1, 2)))),
                state("b", F(1, 2), ((F(-1), F(1, 2)), (F(1), F(1, 2)))),
            )
        )
        self.assertTrue(MOD.decompose_model(model).positive_weight_kernels_identical)


class ExhaustiveFamilyTests(unittest.TestCase):
    @staticmethod
    def kernels():
        outcomes = (F(-1), F(0), F(1))
        answer = []
        for a in range(3):
            for b in range(3 - a):
                c = 2 - a - b
                answer.append(tuple((y, F(n, 2)) for y, n in zip(outcomes, (a, b, c))))
        return tuple(answer)

    def test_exhaustive_small_rational_family_identity_and_bounds(self):
        kernels = self.kernels()
        count = 0
        for wa in (F(0), F(1, 2), F(1)):
            wb = F(1) - wa
            for ka, kb in itertools.product(kernels, repeat=2):
                model = FiniteLatentModel((state("a", wa, ka), state("b", wb, kb)))
                result = MOD.decompose_model(model)

                # Independent direct marginal accumulation; do not call the
                # production marginal helper here.
                probabilities = {}
                for weight, kernel in ((wa, ka), (wb, kb)):
                    for outcome, probability in kernel:
                        probabilities[outcome] = probabilities.get(outcome, F(0)) + weight * probability
                probabilities = {outcome: p for outcome, p in probabilities.items() if p > 0}
                mean = sum((p * outcome for outcome, p in probabilities.items()), F(0))
                total = sum((p * (outcome - mean) ** 2 for outcome, p in probabilities.items()), F(0))

                self.assertEqual(result.total, total)
                self.assertEqual(result.total, result.aleatoric + result.epistemic_mean)
                self.assertGreaterEqual(result.aleatoric, F(0))
                self.assertGreaterEqual(result.epistemic_mean, F(0))
                self.assertLessEqual(result.aleatoric, result.total)
                self.assertLessEqual(result.epistemic_mean, result.total)
                count += 1
        self.assertEqual(count, 108)


class ReceiptTests(unittest.TestCase):
    def test_receipt_deterministic_and_frozen(self):
        first = MOD.build_receipt()
        second = MOD.build_receipt()
        self.assertEqual(first, second)
        self.assertEqual(first["pure_aleatoric"]["aleatoric"], "1")
        self.assertEqual(first["pure_epistemic_mean"]["epistemic_mean"], "1")
        self.assertEqual(first["mixed"]["aleatoric"], "1/4")
        self.assertEqual(first["mixed"]["epistemic_mean"], "1/4")
        self.assertEqual(first["mixed"]["total"], "1/2")
        self.assertTrue(first["marginal_nonidentifiability"]["same_full_marginal"])
        self.assertTrue(first["marginal_nonidentifiability"]["different_decomposition"])
        self.assertFalse(first["same_mean_different_kernels"]["positive_weight_kernels_identical"])
        self.assertEqual(first["no_latent_semantics"], MOD.CANNOT)


if __name__ == "__main__":
    unittest.main()
