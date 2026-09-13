"""Independent finite trace/path references for exact stopping."""

from fractions import Fraction as F
from itertools import product
from pathlib import Path
import types
import unittest

model = types.ModuleType("voc_checked")
path = Path(__file__).with_name("value_of_computation_model_v1.py")
exec(compile(path.read_bytes(), str(path), "exec"), model.__dict__)


def path_values(stops, edges, s, remaining):
    out = list(stops[s])
    if remaining:
        for e, t in edges[s]:
            out.extend(e + v for v in path_values(stops, edges, t, remaining - 1))
    return out


def stationary_reference(stops, edges, initial):
    choices = []
    for s in stops:
        row = [("stop", i) for i in range(len(stops[s]))]
        row += [("cognitive", i) for i in range(len(edges[s]))]
        choices.append(row or [("dead", 0)])
    values = []
    for actions in product(*choices):
        policy = dict(zip(stops, actions))
        # Independent interpreter, not the value recursion or model executor.
        state, visited, cost = initial, set(), F(0)
        while state not in visited:
            visited.add(state)
            kind, i = policy[state]
            if kind == "dead":
                break
            if kind == "stop":
                values.append(cost + stops[state][i])
                break
            e, state = edges[state][i]
            cost += e
    return min(values) if values else None


def two_state_registers(costs):
    for terminal in product((None, F(0), F(3)), repeat=2):
        stops = {s: (() if terminal[s] is None else (terminal[s],)) for s in (0, 1)}
        for selected in product((None,) + costs, repeat=4):
            edges = {s: tuple((selected[2*s+t], t) for t in (0, 1)
                              if selected[2*s+t] is not None) for s in (0, 1)}
            yield stops, edges


class StoppingGraphControls(unittest.TestCase):
    def test_viable_value_does_not_hide_reachable_trap(self):
        stops = {0: (F(1),), 1: ()}
        edges = {0: ((F(1), 1),), 1: ((F(1), 1),)}
        values = model.positive_values(stops, edges)
        self.assertEqual(values, {0: F(1), 1: None})
        self.assertEqual(model.viable_states(stops, edges), frozenset({0}))
        self.assertEqual(model.bellman(stops, edges, values), values)
        with self.assertRaisesRegex(ValueError, "no finite"):
            model.choose_stop_on_ties(stops, edges, values, 1)

    def test_positive_cycle_with_exit_has_unique_finite_value(self):
        stops = {0: (F(3),)}
        edges = {0: ((F(1), 0),)}
        values = model.positive_values(stops, edges)
        self.assertEqual(values, {0: F(3)})
        for candidate in map(F, range(7)):
            fixed = model.bellman(stops, edges, {0: candidate})[0] == candidate
            self.assertEqual(fixed, candidate == 3)

    def test_zero_cycles_are_refused_by_positive_solver(self):
        with self.assertRaises(ValueError):
            model.positive_values({0: (F(1),)}, {0: ((F(0), 0),)})

    def test_equal_cost_continuation_is_optimal_but_stop_is_selected(self):
        stops = {0: (F(1),), 1: (F(0),)}
        edges = {0: ((F(1), 1),), 1: ()}
        values = model.positive_values(stops, edges)
        self.assertEqual(model.choose_stop_on_ties(stops, edges, values, 0), ("stop", 0))
        self.assertEqual(model.execute_stationary(stops, edges,
                         {0: ("cognitive", 0), 1: ("stop", 0)}, 0), (F(1), 1))

    def test_zero_cost_local_minimizer_is_not_a_progress_certificate(self):
        stops = {0: (), 1: (F(0),)}
        edges = {0: ((F(0), 0), (F(0), 1)), 1: ()}
        values = model.ranked_values(stops, edges, 1)
        self.assertEqual(values, {0: F(0), 1: F(0)})
        # Tied self-loop has the right local value but fails to serve.
        self.assertEqual(model.execute_stationary(stops, edges,
                         {0: ("cognitive", 0), 1: ("stop", 0)}, 0)[0], None)
        self.assertEqual(model.execute_stationary(stops, edges,
                         {0: ("cognitive", 1), 1: ("stop", 0)}, 0), (F(0), 1))
        with self.assertRaises(ValueError):
            model.choose_stop_on_ties(stops, edges, values, 0)

    def test_two_probe_graph_revives_myopic_stopping(self):
        stops = {0: (F(10),), 1: (F(10),), 2: (F(10),), 3: (F(1),)}
        edges = {0: ((F(1), 1), (F(1), 2)), 1: ((F(1), 3),),
                 2: ((F(1), 3),), 3: ()}
        self.assertEqual(model.ranked_values(stops, edges, 1)[0], F(10))
        self.assertEqual(model.positive_values(stops, edges)[0], F(3))

    def test_exact_positive_census_against_all_stationary_policies(self):
        count = 0
        for stops, edges in two_state_registers((F(1), F(2))):
            values = model.positive_values(stops, edges)
            self.assertEqual(model.bellman(stops, edges, values), values)
            viable = model.viable_states(stops, edges)
            for state in stops:
                self.assertEqual(values[state], stationary_reference(stops, edges, state))
                self.assertEqual(values[state] is not None, state in viable)
            count += 1
        self.assertEqual(count, 729)

    def test_ranked_census_against_all_bounded_paths(self):
        count = 0
        for stops, edges in two_state_registers((F(0), F(1))):
            for rank in range(3):
                values = model.ranked_values(stops, edges, rank)
                for state in stops:
                    paths = path_values(stops, edges, state, rank)
                    self.assertEqual(values[state], min(paths) if paths else None)
                    count += 1
        self.assertEqual(count, 4374)

    def test_certified_bound_uses_complete_cost(self):
        stops = {0: (F(5),), 1: (), 2: (F(1),)}
        edges = {0: ((F(1), 1),), 1: ((F(1), 2),), 2: ()}
        values = model.positive_values(stops, edges)
        policy = {s: model.choose_stop_on_ties(stops, edges, values, s) for s in stops}
        total, steps = model.execute_stationary(stops, edges, policy, 0)
        self.assertEqual((total, steps), (F(3), 2))
        self.assertLessEqual(steps, F(5) // F(1))

    def test_stochastic_boundary_has_no_finite_path_bound(self):
        # Separate declared stochastic witness, not input to deterministic solver.
        self.assertEqual(F(1) + F(1, 2)*F(2), F(2))
        for horizon in range(9):
            # Direct finite geometric-prefix expectation plus paid failure fallback.
            total = sum(F(n, 2**n) for n in range(1, horizon + 1))
            total += F(horizon + 3, 2**horizon)
            self.assertEqual(total, F(2) + F(1, 2**horizon))
            self.assertGreater(F(1, 2**horizon), 0)

    def test_invalid_register_cannot_supply_a_certificate(self):
        for stops, edges in [
            ({0: (F(1),)}, {0: ((F(1), 1),)}),
            ({0: (F(-1),)}, {0: ()}),
            ({0: (F(1),)}, {0: ((F(-1), 0),)}),
        ]:
            with self.assertRaises(ValueError):
                model.positive_values(stops, edges)


if __name__ == "__main__":
    unittest.main()
