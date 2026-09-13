"""Independent entropy-law and exhaustive read-order controls."""

import hashlib
import json
import unittest
from fractions import Fraction as F
from itertools import product
from pathlib import Path

from memory_synthesis import ReadCompiler, partitions, profile, search

HERE = Path(__file__).resolve().parent


def all_read_orders(remaining):
    if not remaining:
        yield None
        return
    for bit in remaining:
        children = tuple(all_read_orders(tuple(i for i in remaining if i != bit)))
        for left, right in product(children, repeat=2):
            yield bit, left, right


def oracle_cost(code, n):
    databases = tuple(product((0, 1), repeat=n))

    def cost(tree, fiber):
        if len({code[i] for i in fiber}) == 1:
            return F(0)
        bit, left, right = tree
        zero = tuple(i for i in fiber if not databases[i][bit])
        one = tuple(i for i in fiber if databases[i][bit])
        return 1 + (len(zero) * cost(left, zero) + len(one) * cost(right, one)) / len(fiber)

    return min(cost(tree, tuple(range(2 ** n))) for tree in all_read_orders(tuple(range(n))))


def registered_results():
    raw = (HERE / "memory_registration.json").read_bytes()
    rows = []
    for case in json.loads(raw)["cases"]:
        p = tuple(F(v) for v in case["probabilities"])
        prices = tuple(F(case[k]) for k in ("cA", "cM", "cR", "H"))
        result = search(case["n"], case["memory_max"], p, *prices)
        cA, cM, cR, horizon = prices
        sorted_p = sorted(p, reverse=True)
        law = [(cA + cM) * m + horizon * cR * (1 - sum(sorted_p[:m]))
               for m in range(case["memory_max"] + 1)]
        sizes = [m for m, cost in enumerate(law) if cost == min(law)]
        if result["minimum"] != min(law) or min(law) != F(case["minimum"]):
            raise ValueError("registered memory cost law refuted")
        if result["memory_sizes"] != sizes or sizes != case["optimal_memory_sizes"]:
            raise ValueError("registered optimal property fiber refuted")
        if result["encoders"] != 2795:
            raise ValueError("incomplete retained-code enumeration")
        codes = result.pop("optimal_codes")
        rows.append({"id": case["id"], **result, "minimum": str(result["minimum"]),
                     "optimal_code_count": len(codes), "witness": codes[0],
                     "all_optimal_codes_sha256": hashlib.sha256(json.dumps(codes).encode()).hexdigest()})
    return {"registration_sha256": hashlib.sha256(raw).hexdigest(), "cases": rows}


class MemoryDerivationTests(unittest.TestCase):
    def test_registered_full_encoder_search(self):
        self.assertEqual(len(registered_results()["cases"]), 5)

    def test_read_compiler_against_independent_full_tree_enumeration(self):
        for n, symbols in ((2, 4), (3, 2)):
            compiler = ReadCompiler(n)
            for code in partitions(2 ** n, symbols):
                self.assertEqual(compiler.solve(code)[0], oracle_cost(code, n))

    def test_partition_completeness_and_coded_memory(self):
        codes = tuple(partitions(8, 4))
        self.assertEqual(len(codes), len(set(codes)))
        self.assertEqual(len(codes), 2795)
        parity = tuple(sum(x) % 2 for x in product((0, 1), repeat=3))
        self.assertIn(parity, codes)
        m, acquisition, retrieval = profile(parity, ReadCompiler(3), (F(1, 3),) * 3)
        self.assertEqual((m, acquisition, retrieval), (1, 3, 1))

    def test_full_retention_and_no_retention(self):
        compiler = ReadCompiler(3)
        p = (F(1, 2), F(1, 3), F(1, 6))
        self.assertEqual(profile(tuple(range(8)), compiler, p), (3, 3, 0))
        self.assertEqual(profile((0,) * 8, compiler, p), (0, 0, 1))


if __name__ == "__main__":
    unittest.main()
