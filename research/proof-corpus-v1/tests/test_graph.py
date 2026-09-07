import unittest
from helpers import api, wrapper, solution


class GraphControls(unittest.TestCase):
    def records(self, dependencies):
        syntax = api("corpus_syntax")
        return ({k: syntax.extract_wrapper(wrapper(k), k) for k in dependencies},
                {k: syntax.extract_solution(solution(*deps), k) for k, deps in dependencies.items()})

    def test_pairs_and_topological_order_are_exact(self):
        wrappers, solutions = self.records({"A": (), "B": ("A",), "C": ("A", "B")})
        graph = api("corpus_graph").build_graph(wrappers, solutions, expected_count=3)
        self.assertEqual(graph["topological_order"], ["A", "B", "C"])
        self.assertEqual(graph["edge_count"], 3)
        self.assertEqual(graph["graph_kind"], "LEXICAL_THEOREM_IMPORT_GRAPH")
        self.assertFalse(graph["semantic_dependencies_verified"])

    def test_cyclic_imports_refuse(self):
        wrappers, solutions = self.records({"A": ("B",), "B": ("A",)})
        with self.assertRaisesRegex(api("corpus_contract").CorpusError, "IMPORT_CYCLE"):
            api("corpus_graph").build_graph(wrappers, solutions, expected_count=2)

    def test_dangling_imports_refuse(self):
        wrappers, solutions = self.records({"A": ("Missing",)})
        with self.assertRaisesRegex(api("corpus_contract").CorpusError, "DANGLING_IMPORT"):
            api("corpus_graph").build_graph(wrappers, solutions, expected_count=1)

    def test_pair_set_and_count_mismatch_refuse(self):
        wrappers, solutions = self.records({"A": ()})
        graph = api("corpus_graph")
        error = api("corpus_contract").CorpusError
        with self.assertRaisesRegex(error, "PAIR_COVERAGE"):
            graph.build_graph(wrappers, {}, expected_count=1)
        with self.assertRaisesRegex(error, "PAIR_COVERAGE"):
            graph.build_graph(wrappers, solutions, expected_count=2)

    def test_duplicate_imports_do_not_fabricate_multiple_edges(self):
        wrappers, solutions = self.records({"A": (), "B": ("A", "A")})
        graph = api("corpus_graph").build_graph(wrappers, solutions, expected_count=2)
        self.assertEqual(graph["edge_count"], 1)
        self.assertEqual(solutions["B"]["imports"].count("Theorems.Thm_A"), 2)

    def test_direct_solution_import_is_not_silently_hidden(self):
        syntax = api("corpus_syntax")
        wrappers, solutions = self.records({"A": ()})
        solutions["A"] = syntax.extract_solution("import Mathlib P2M.Sol.S_A\n", "A")
        with self.assertRaisesRegex(api("corpus_contract").CorpusError, "UNREGISTERED_PROOF_IMPORT"):
            api("corpus_graph").build_graph(wrappers, solutions, expected_count=1)

    def test_non_theorem_context_imports_are_preserved(self):
        row = api("corpus_syntax").extract_solution("import Mathlib Definitions.Context\n", "A")
        self.assertEqual(row["imports"], ["Mathlib", "Definitions.Context"])
        self.assertIn("solution_sha256", row)
        self.assertNotIn("solution_source", row)


if __name__ == "__main__":
    unittest.main()
