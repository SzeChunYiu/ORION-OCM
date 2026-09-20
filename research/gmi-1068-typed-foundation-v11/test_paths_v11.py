"""Complete acyclic free categories and independently computed interpretations."""
import unittest
from functools import lru_cache
from itertools import product
import independent_paths_v11 as oracle
import paths_v11 as core

COVERAGE = {}


@lru_cache(maxsize=1)
def corpus():
    return tuple((graph, tuple(sorted(oracle.complete_dag_paths(graph))))
                 for graph in oracle.primary_graphs())


class PathTests(unittest.TestCase):
    def test_complete_categories(self):
        graphs = paths_seen = units = pairs = triples = incompatible = evaluations = quotients = relabels = 0
        for graph, paths in corpus():
            graphs += 1
            actual = core.enumerate_dag(graph)
            self.assertEqual(len(actual), len(set(actual)))
            self.assertEqual(set(actual), set(paths))
            ends = {p: oracle.vertices(graph, p)[-1] for p in paths}
            domains = (2, 3, 2, 4)
            maps = tuple(tuple((value + index) % domains[target] for value in range(domains[source]))
                         for index, (source, target) in enumerate(graph[1]))
            images, signatures, labels = {}, {}, {}
            for path in paths:
                paths_seen += 1
                self.assertEqual(core.endpoint(graph, path), ends[path])
                self.assertEqual(core.compose(graph, core.identity(graph, path[0]), path), path)
                self.assertEqual(core.compose(graph, path, core.identity(graph, ends[path])), path)
                units += 2
                image = oracle.concrete_evaluation(graph, path, domains, maps)
                self.assertEqual(core.interpret(graph, path, domains, maps), image)
                images[path] = image
                signature = path[0], ends[path], image
                if signature not in signatures:
                    signatures[signature] = len(signatures)
                labels[path] = signatures[signature]
                evaluations += 1
            following = {p: tuple(q for q in paths if p[0] == ends[q]) for p in paths}
            for p, q in product(paths, repeat=2):
                if ends[p] != q[0]:
                    with self.assertRaises(ValueError):
                        core.compose(graph, p, q)
                    incompatible += 1
                    continue
                pq = oracle.concatenate(graph, p, q)
                self.assertEqual(core.compose(graph, p, q), pq)
                self.assertIn(pq, ends)
                self.assertEqual(ends[pq], ends[q])
                self.assertEqual(images[pq], tuple(images[q][value] for value in images[p]))
                pairs += 1
                for r in paths:
                    if ends[q] == r[0]:
                        left = core.compose(graph, core.compose(graph, p, q), r)
                        right = core.compose(graph, p, core.compose(graph, q, r))
                        self.assertEqual(left, right)
                        self.assertEqual(left, oracle.concatenate(graph, pq, r))
                        triples += 1
            quotient = core.quotient_dag(graph, labels)
            self.assertEqual(len(quotient["arrows"]), len(signatures))
            for p in paths:
                self.assertEqual(quotient["arrows"][labels[p]], (p[0], ends[p]))
                for q in following[p]:
                    self.assertEqual(quotient["composition"][labels[q], labels[p]],
                                     labels[oracle.concatenate(graph, q, p)])
            for obj in range(4):
                self.assertEqual(quotient["identities"][obj], labels[(obj, ())])
            quotients += 1
            # Reverse both object and generator names, retaining the entire diagram.
            edge_count = len(graph[1])
            renamed = (4, tuple((3-source, 3-target) for source, target in graph[1][::-1]))
            transported = {(3-start, tuple(edge_count-1-edge for edge in word)) for start, word in paths}
            self.assertEqual(set(core.enumerate_dag(renamed)), transported)
            self.assertEqual(oracle.complete_dag_paths(renamed), transported)
            relabels += 1
        self.assertEqual(graphs, 729)
        self.assertEqual(quotients, graphs)
        self.assertEqual(relabels, graphs)
        self.assertGreater(triples, pairs)
        COVERAGE.update(dag_graphs=graphs, complete_paths=paths_seen, unit_equations=units,
                        legal_compositions=pairs, legal_triples=triples, incompatible_compositions=incompatible,
                        concrete_interpretations=evaluations, extensional_quotients=quotients,
                        renamed_graphs=relabels)

    def test_all_generator_admissions(self):
        cases = membership = closures = identity_checks = 0
        for graph, paths in corpus():
            ends = {p: oracle.vertices(graph, p)[-1] for p in paths}
            legal = tuple((p, q, oracle.concatenate(graph, p, q)) for p, q in product(paths, repeat=2)
                          if ends[p] == q[0])
            for allowed in oracle.restrictions(len(graph[1])):
                admitted = {p for p in paths if all(edge in allowed for edge in p[1])}
                for path in paths:
                    self.assertEqual(core.admitted(graph, path, allowed), path in admitted)
                    membership += 1
                for obj in range(4):
                    self.assertIn((obj, ()), admitted)
                    identity_checks += 1
                for p, q, pq in legal:
                    if p in admitted and q in admitted:
                        self.assertIn(pq, admitted)
                        closures += 1
                cases += 1
        self.assertEqual(cases, 117649)
        self.assertEqual(identity_checks, 470596)
        COVERAGE.update(admission_subsets=cases, path_admission_checks=membership,
                        admitted_composition_checks=closures, admitted_identity_checks=identity_checks)

    def test_all_two_element_operations(self):
        tables = associative = lawful = words_checked = 0
        graph = (1, ((0, 0), (0, 0)))
        for table, is_associative, units in oracle.monoids_two():
            tables += 1
            associative += is_associative
            if not is_associative or not units:
                continue
            self.assertEqual(len(units), 1)
            unit = units[0]
            lawful += 1
            maps = tuple(tuple(table[x][generator] for x in range(2)) for generator in range(2))
            for length in range(7):
                for word in product(range(2), repeat=length):
                    value = unit
                    for generator in word:
                        value = table[value][generator]
                    expected = tuple(table[x][value] for x in range(2))
                    self.assertEqual(core.interpret(graph, (0, word), (2,), maps), expected)
                    self.assertEqual(oracle.concrete_evaluation(graph, (0, word), (2,), maps), expected)
                    words_checked += 1
        self.assertEqual(tables, 16)
        self.assertEqual(lawful, 4)
        self.assertEqual(words_checked, 508)
        COVERAGE.update(binary_operation_tables=tables, associative_tables=associative,
                        lawful_monoids=lawful, monoid_word_interpretations=words_checked)


if __name__ == "__main__":
    unittest.main()
