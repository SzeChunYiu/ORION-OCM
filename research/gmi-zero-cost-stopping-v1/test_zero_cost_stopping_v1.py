"""Independent actual policy traces, not a second Bellman implementation."""
from fractions import Fraction as F
from itertools import product
import unittest
from zero_cost_stopping_v1 import Graph, solve


def trace(graph, policy, start):
    seen, cost, steps = set(), F(0), 0
    while start not in seen:
        seen.add(start)
        action = policy[start]
        if action is None:
            return None
        kind, index = action
        if kind == "stop":
            return cost + graph.terminals[start][index], steps
        target, charge = graph.edges[start][index]
        cost += charge
        steps += 1
        start = target
    return None


def enumerate_optima(graph):
    choices = []
    for terminals, edges in zip(graph.terminals, graph.edges):
        actions = [("stop", i) for i in range(len(terminals))]
        actions += [("edge", i) for i in range(len(edges))]
        choices.append(actions or [None])
    rows = [[] for _ in choices]
    for policy in product(*choices):
        for state in range(len(choices)):
            outcome = trace(graph, policy, state)
            if outcome is not None:
                rows[state].append(outcome)
    return tuple(min(row, default=None) for row in rows)


class ProperStopping(unittest.TestCase):
    def check_graph(self, graph):
        labels, policy = solve(graph)
        self.assertEqual(labels, enumerate_optima(graph))
        for state, expected in enumerate(labels):
            self.assertEqual(trace(graph, policy, state), expected)
            if expected is not None:
                self.assertLessEqual(expected[1], len(labels) - 1)

    def test_all_two_state_graphs_zero_positive_missing(self):
        # All 3^4 directed edge tables (including self-loops), 3^2 terminal tables.
        count = 0
        for stops in product((None, F(0), F(1)), repeat=2):
            for charges in product((None, F(0), F(1)), repeat=4):
                graph = Graph(tuple(() if c is None else (c,) for c in stops),
                              tuple(tuple((t, charges[2*s+t]) for t in range(2)
                                          if charges[2*s+t] is not None) for s in range(2)))
                self.check_graph(graph)
                count += 1
        self.assertEqual(count, 729)

    def test_three_state_zero_cycle_with_exit(self):
        graph = Graph(((), (), (F(2),)), (((1, F(0)),), ((0, F(0)), (2, F(0))), ()))
        self.check_graph(graph)
        self.assertEqual(solve(graph)[0], ((F(2), 2), (F(2), 1), (F(2), 0)))

    def test_scalar_greedy_can_loop_but_paired_selector_serves(self):
        graph = Graph(((), (F(0),)), (((0, F(0)), (1, F(0))), ()))
        self.assertIsNone(trace(graph, (("edge", 0), ("stop", 0)), 0))
        self.check_graph(graph)
        self.assertEqual(solve(graph)[1][0], ("edge", 1))

    def test_zero_iteration_fixed_point_is_not_proper_value(self):
        graph = Graph(((F(1),),), (((0, F(0)),),))
        for value in (F(0), F(1, 2), F(1)):
            self.assertEqual(value, min(F(1), value))
        self.check_graph(graph)
        self.assertEqual(solve(graph)[0], ((F(1), 0),))

    def test_zero_trap_is_infeasible_not_free(self):
        graph = Graph(((F(1),), ()), (((1, F(0)),), ((1, F(0)),)))
        self.check_graph(graph)
        self.assertEqual(solve(graph)[0], ((F(1), 0), None))

    def test_cost_priority_precedes_path_length(self):
        graph = Graph(((F(4),), (), (F(1),)), (((1, F(1)),), ((2, F(1)),), ()))
        self.check_graph(graph)
        self.assertEqual(solve(graph)[0][0], (F(3), 2))

    def test_terminal_tie_chooses_zero_steps(self):
        graph = Graph(((F(1), F(2)), (F(1),)), (((1, F(0)),), ()))
        self.check_graph(graph)
        self.assertEqual(solve(graph)[1][0], ("stop", 0))

    def test_parallel_edges_and_rational_costs(self):
        graph = Graph(((), (F(1, 3),)), (((1, F(1, 2)), (1, F(1, 4))), ()))
        self.check_graph(graph)
        self.assertEqual(solve(graph)[0][0], (F(7, 12), 1))

    def test_input_contract_rejects_unproved_extensions(self):
        bad = [Graph((), ()), Graph(((),), ()), Graph(((0.0,),), ((),)),
               Graph(((True,),), ((),)), Graph(((F(-1),),), ((),)),
               Graph(((F(0),),), (((0, F(-1)),),)),
               Graph(((F(0),),), (((1, F(0)),),))]
        for graph in bad:
            with self.subTest(graph=graph), self.assertRaises(ValueError):
                solve(graph)



if __name__ == "__main__":
    unittest.main()
