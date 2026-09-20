"""Reproduce a disclosed V9 witness; no prospective empirical claim."""
from copy import deepcopy
import importlib.util
from itertools import product
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import independent_context_v11 as independent

COVERAGE = {}


def v9_module():
    path = independent.ROOT / independent.V9 / "semantic_v9.py"
    spec = importlib.util.spec_from_file_location("bound_semantic_v9", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ContextTests(unittest.TestCase):
    def test_bound_full_process_same_domain_collision(self):
        result = independent.audit()
        expected = dict(typed_histories=182, evaluator_disagreements=156,
                        identity_only_histories=26, padded_ranking_reversals=36,
                        full_process_comparisons=1, path_admission_comparisons=182)
        self.assertEqual(result["coverage"], expected)
        COVERAGE.update(result["coverage"])
        v9 = v9_module()
        names = {a: i for i, a in enumerate(independent.ARROWS)}
        comparisons = cells = 0
        for start, path in independent.histories(12):
            for objective in independent.OBJECTIVES:
                actual = v9.evaluate_history(3, tuple(objective[a] for a in independent.ARROWS),
                                             start, tuple(names[a] for a in path))
                self.assertEqual(actual, independent.evaluate(objective, start, path))
                comparisons += 1
        for a, b in product(independent.ARROWS, repeat=2):
            if independent.ENDS[a][1] == independent.ENDS[b][0]:
                self.assertEqual(names[independent.compose(a, b)], v9.compose(names[a], names[b]))
            else:
                with self.assertRaises(ValueError):
                    independent.compose(a, b)
                with self.assertRaises(ValueError):
                    v9.compose(names[a], names[b])
            cells += 1
        self.assertEqual((comparisons, cells), (364, 16))
        COVERAGE.update(v9_evaluation_comparisons=comparisons, composition_cells=cells)

    def test_actual_collision_mutants_and_positive_control(self):
        process = independent.process_record()
        a, b = independent.OBJECTIVES
        self.assertEqual(independent.verify_collision(process, deepcopy(process), a, b),
                         ((1, 0), (0, 1)))
        mutants = []
        for index in range(len(process)):
            other = list(process)
            other[index] = ()
            mutants.append((process, tuple(other), a, b))
        for objective_index, label in product(range(2), independent.ARROWS):
            objectives = [dict(a), dict(b)]
            objectives[objective_index][label] = 1 - objectives[objective_index][label]
            if label in ("a", "b"):
                mutants.append((process, process, *objectives))
        for bad in ({"a": 1, "b": 0}, dict(a, alien=0), dict(a, a=True)):
            mutants.append((process, process, bad, b))
        alias = ((False, 1),) + process[1:]
        mutants.extend(((alias, alias, a, b), (process, process, None, b)))
        rejected = 0
        for args in mutants:
            with self.assertRaises(ValueError):
                independent.verify_collision(*args)
            rejected += 1
        for args in ((a, True, ()), (a, 0, ("i1",)), (a, 0, ("a", "b")),
                     (a, 1, ("a",)), (a, 0, (False,)), (a, 0, [])):
            with self.assertRaises(ValueError):
                independent.evaluate(*args)
            rejected += 1
        self.assertEqual(rejected, 20)
        COVERAGE["context_semantic_rejections"] = rejected

    def test_custody_invalid_and_missing_are_distinct(self):
        root = independent.ROOT
        real_read = Path.read_bytes
        def corrupted(path):
            data = real_read(path)
            return data + b" " if path == root / next(iter(independent.BINDINGS)) else data
        with patch.object(Path, "read_bytes", corrupted):
            with self.assertRaises(ValueError):
                independent.audit(root)
        with tempfile.TemporaryDirectory() as empty:
            with self.assertRaises(FileNotFoundError):
                independent.audit(empty)
        COVERAGE["context_custody_controls"] = 2


if __name__ == "__main__":
    unittest.main()
