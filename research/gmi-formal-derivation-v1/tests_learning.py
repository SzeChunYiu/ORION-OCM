"""Exact finite witnesses for learning claims, not proofs of infinite laws."""
from fractions import Fraction as F
from itertools import product
import unittest


def admit(old, new, observed_error, radius, debt, horizon, margin):
    lower = old - new + observed_error - radius
    return lower > margin + debt / horizon


def run_lifecycle(initial, proposals, radius, margin):
    """Account actual paid charges and each task's population-cost forecast."""
    incumbent, debt, forecast_delta = initial, F(0), F(0)
    settled_uses, switches = 0, 0
    for challenger, acquisition, horizon in proposals:
        debt += acquisition
        forecast_delta += acquisition
        if admit(incumbent, challenger, F(0), radius, debt, horizon, margin):
            incumbent = challenger
            debt = F(0)
            settled_uses += horizon
            switches += 1
        forecast_delta += horizon * (incumbent - initial)
    return forecast_delta, debt, settled_uses, switches, incumbent


def evaluate_and_reverse(nodes, inputs):
    """Ordinary scalar DAG execution; shared nodes/edges stay shared."""
    values = []
    for node in nodes:
        if node[0] == "input":
            values.append(inputs[node[1]])
        elif node[0] == "add":
            values.append(values[node[1]] + values[node[2]])
        elif node[0] == "mul":
            values.append(values[node[1]] * values[node[2]])
        else:
            raise ValueError(node[0])
    adjoints = [F(0) for _ in nodes]
    adjoints[-1] = F(1)
    for index in reversed(range(len(nodes))):
        node = nodes[index]
        if node[0] == "add":
            adjoints[node[1]] += adjoints[index]
            adjoints[node[2]] += adjoints[index]
        elif node[0] == "mul":
            adjoints[node[1]] += adjoints[index] * values[node[2]]
            adjoints[node[2]] += adjoints[index] * values[node[1]]
    return values[-1], adjoints


# F=(w*x+w*z+b)^2: w has two consumers; the residual has two square edges.
SHARED_GRAPH = [("input", name) for name in ("w", "x", "z", "b")] + [
    ("mul", 0, 1), ("mul", 0, 2), ("add", 4, 5),
    ("add", 6, 3), ("mul", 7, 7),
]


def polynomial(values):
    return (values["w"] * (values["x"] + values["z"]) + values["b"]) ** 2


class LearningWitnesses(unittest.TestCase):
    def test_confidence_admission_safety_and_sufficient_progress(self):
        grid = tuple(F(i, 4) for i in range(5))
        count = accepted = deferred_positive = 0
        for old, new, radius, debt, horizon, margin in product(
            grid, grid, (F(0), F(1, 8), F(1, 4)),
            (F(0), F(1, 4), F(1), F(2)), (1, 2, 4, 8), (F(1, 8), F(1, 4))
        ):
            for error in (-radius, F(0), radius):
                decision = admit(old, new, error, radius, debt, horizon, margin)
                count += 1
                if decision:
                    accepted += 1
                    self.assertLess(debt + horizon * new, horizon * (old - margin))
                    self.assertGreater(old - new, margin)
                elif old - new > 0:
                    deferred_positive += 1
                if old - new > margin + 2 * radius + debt / horizon:
                    self.assertTrue(decision)
                if old <= new:
                    self.assertFalse(decision)
        self.assertEqual(count, 7200)
        self.assertGreater(accepted, 0)
        self.assertGreater(deferred_positive, 0)
        self.assertFalse(admit(F(1), F(0), F(0), F(0), F(3, 4), 1, F(1, 4)))

    def test_full_ledger_against_direct_two_episode_forecasts(self):
        grid = tuple(F(i, 4) for i in range(5))
        count = 0
        for initial, q1, q2, a1, a2, h1, h2, radius in product(
            (F(1, 2), F(1)), grid, grid, (F(0), F(1, 4), F(1)),
            (F(0), F(1, 4), F(1)), (1, 4, 16), (1, 4, 16), (F(0), F(1, 8))
        ):
            margin = F(1, 8)
            actual, pending, uses, switches, incumbent = run_lifecycle(
                initial, ((q1, a1, h1), (q2, a2, h2)), radius, margin)
            self.assertLessEqual(actual, pending - margin * uses)
            self.assertLessEqual(incumbent, initial)
            self.assertLessEqual(switches, initial // margin)
            count += 1
        self.assertEqual(count, 8100)

    def test_rejected_acquisition_debt_cannot_be_erased(self):
        first = (F(1), F(2), 1)
        short = run_lifecycle(F(1), (first, (F(0), F(0), 2)), F(0), F(1, 8))
        self.assertEqual(short, (F(2), F(2), 0, 0, F(1)))
        self.assertTrue(admit(F(1), F(0), F(0), F(0), F(0), 2, F(1, 8)))
        revived = run_lifecycle(F(1), (first, (F(0), F(0), 3)), F(0), F(1, 8))
        self.assertEqual(revived, (F(-1), F(0), 3, 1, F(0)))

    def test_registered_rational_finite_progress_witness(self):
        outcomes = ((0, F(1, 4)), (1, F(3, 4)))
        old = sum(probability * int(label != 0) for label, probability in outcomes)
        new = sum(probability * int(label != 1) for label, probability in outcomes)
        delta, alpha, radius, n = F(1, 20), F(1, 40), F(1, 8), 4096
        self.assertEqual((old, new), (F(3, 4), F(1, 4)))
        self.assertEqual(alpha, delta / 2)
        self.assertEqual(n * radius ** 2 / 2, 32)
        # e>2 implies 2 exp(-32)<2^-31; compare the remaining bound exactly.
        self.assertLess(F(1, 2 ** 31), alpha / (n * (n + 1)))
        cost, horizon, margin = n * F(1, 32) + 128, 4096, F(1, 8)
        self.assertEqual(cost, F(256))
        self.assertTrue(admit(old, new, -radius, radius, cost, horizon, margin))
        self.assertEqual(horizon * (old - new) - cost, F(1792))
        self.assertEqual(128 * (old - new) - cost, F(-192))

    def test_shared_parameter_reverse_mode_against_exact_finite_difference(self):
        count, step = 0, F(1, 7)
        for scalars in product((F(-2), F(0), F(3, 2)), repeat=4):
            values = dict(zip(("w", "x", "z", "b"), scalars))
            output, adjoints = evaluate_and_reverse(SHARED_GRAPH, values)
            self.assertEqual(output, polynomial(values))
            for index, parameter in enumerate(("w", "x", "z", "b")):
                plus, minus = dict(values), dict(values)
                plus[parameter] += step
                minus[parameter] -= step
                # Each one-variable restriction is quadratic: no remainder.
                independent = (polynomial(plus) - polynomial(minus)) / (2 * step)
                self.assertEqual(adjoints[index], independent)
                count += 1
        self.assertEqual(count, 324)

    def test_zero_input_exposes_product_as_parameter_tagging(self):
        for weight, bias in product((F(-2), F(0), F(3)), (F(-1), F(1))):
            values = {"w": weight, "x": F(0), "z": F(0), "b": bias}
            _, adjoints = evaluate_and_reverse(SHARED_GRAPH, values)
            self.assertEqual(adjoints[0], F(0))
            # Hostile control: tagging each product as the parameter omits x,z.
            incorrect_product_tags = adjoints[4] + adjoints[5]
            self.assertEqual(incorrect_product_tags, 4 * bias)
            self.assertNotEqual(incorrect_product_tags, adjoints[0])


if __name__ == "__main__":
    unittest.main()
