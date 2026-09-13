"""Source-frozen raw ecology tests; task builders are outside the compiler."""

import hashlib
import json
import unittest
from fractions import Fraction as F
from itertools import product
from pathlib import Path

from orbit_compiler import compile_affine, execute
from orbit_oracle import check_certificate, predict
from orbit_raw import infer

HERE = Path(__file__).resolve().parent


def task(case):
    table = {}
    for x in product((0, 1), repeat=case["inputs"]):
        if case["id"] == "raw_local4":
            y = tuple(1 + 2 * x[r] + x[(r + 1) % 4] for r in range(4))
        elif case["id"] == "raw_sum4":
            y = (1 + sum(x),)
        elif case["id"] == "raw_dense_rectangle":
            y = (1 + x[0] + 2 * x[1] + 3 * x[2], 2 + 4 * x[0] + 5 * x[1] + 6 * x[2])
        elif case["id"] == "raw_copy4":
            y = x
        else:
            raise ValueError("unknown registered task")
        table[x] = y
    return table


def registered_results():
    raw = (HERE / "orbit_raw_registration.json").read_bytes()
    results = []
    for case in json.loads(raw)["cases"]:
        table = task(case)
        ni, no = case["inputs"], case["outputs"]
        inferred = infer(table, ni, no)
        args = ni, no, inferred["generators"], inferred["allowed"]
        prediction = predict(*args)
        compiled = compile_affine(*args)
        if (prediction["dimension"], prediction["group_size"], len(prediction["core"])) != (
                case["dimension"], case["group_size"], case["active_entries"]):
            raise ValueError("prospective raw-table prediction refuted")
        if not check_certificate(compiled, prediction):
            raise ValueError("generic constraint certificate failed")
        flat = sum(inferred["matrix"], ())
        parameters = tuple(flat[next(i for i, v in enumerate(b) if v)] for b in compiled["basis"])
        for x, y in table.items():
            if execute(compiled, parameters, x)[0] != y:
                raise ValueError("generated code fails actual raw obligation")
            for pin, pout in inferred["generators"]:
                xp = [0] * ni
                yp = [0] * no
                for i in range(ni):
                    xp[pin[i]] = x[i]
                for r in range(no):
                    yp[pout[r]] = y[r]
                if table[tuple(xp)] != tuple(yp):
                    raise ValueError("inferred symmetry fails finite semantic oracle")
        results.append({"id": case["id"], "dimension": prediction["dimension"],
                        "group_size": prediction["group_size"],
                        "inference": inferred["counters"], "compiler": compiled["counters"]})
    return {"registration_sha256": hashlib.sha256(raw).hexdigest(), "cases": results}


class RawEcologyTests(unittest.TestCase):
    def test_complete_raw_ecology_to_executable_realization(self):
        self.assertEqual(len(registered_results()["cases"]), 4)

    def test_non_affine_task_rejected(self):
        table = {x: (sum(x) % 2,) for x in product((0, 1), repeat=2)}
        with self.assertRaisesRegex(ValueError, "not affine"):
            infer(table, 2, 1)

    def test_missing_ecology_is_not_certified(self):
        with self.assertRaisesRegex(ValueError, "complete"):
            infer({(0, 0): (F(0),)}, 2, 1)


if __name__ == "__main__":
    unittest.main()
