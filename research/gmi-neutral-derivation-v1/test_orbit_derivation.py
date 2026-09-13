"""Independent registered finite checks; run on the verification laptop."""

import copy
import hashlib
import json
import unittest
from fractions import Fraction as F
from pathlib import Path

from orbit_compiler import compile_affine, execute
from orbit_oracle import check_certificate, exact_risk, predict

HERE = Path(__file__).resolve().parent


def decode(case):
    ni, no = case["inputs"], case["outputs"]
    ident_i, ident_o = tuple(range(ni)), tuple(range(no))
    cycle_i, cycle_o = tuple((i + 1) % ni for i in range(ni)), tuple((i + 1) % no for i in range(no))
    action = case["action"]
    if action == "none":
        generators = []
    elif action == "independent":
        generators = [(cycle_i, ident_o), (ident_i, cycle_o)]
    elif action in ("cycle", "dihedral", "symmetric"):
        generators = [(cycle_i, cycle_o)]
        if action == "dihedral":
            generators += [(tuple(-i % ni for i in range(ni)), tuple(-i % no for i in range(no)))]
        if action == "symmetric":
            generators += [((1, 0) + ident_i[2:], (1, 0) + ident_o[2:])]
    else:
        raise ValueError("unregistered action")
    allowed = {(r, c) for r in range(no) for c in range(ni + 1)}
    if case["support"] == "radius2":
        allowed = {(r, c) for r, c in allowed if c == ni or (c - r) % ni in {0, 1, 2, ni - 1, ni - 2}}
    elif case["support"] == "forbid00":
        allowed.remove((0, 0))
    elif case["support"] != "full":
        raise ValueError("unregistered support")
    return ni, no, generators, allowed


def registered_results():
    raw = (HERE / "orbit_registration.json").read_bytes()
    cases = json.loads(raw)["cases"]
    results = []
    for case in cases:
        args = decode(case)
        prediction = predict(*args)
        compiled = compile_affine(*args)
        if prediction["dimension"] != case["dimension"] or prediction["group_size"] != case["group_size"]:
            raise ValueError("registered prediction refuted: " + case["id"])
        if not check_certificate(compiled, prediction):
            raise ValueError("constraint compiler disagrees with finite-action oracle")
        parameters = tuple(F(i + 1, 2) for i in range(compiled["dimension"]))
        x = tuple(F(2 * i - 3, 3) for i in range(args[0]))
        actual, trace = execute(compiled, parameters, x)
        matrix = [sum(p * b[i] for p, b in zip(parameters, compiled["basis"]))
                  for i in range(args[1] * (args[0] + 1))]
        expected = tuple(sum(matrix[r * (args[0] + 1) + c] * (x + (F(1),))[c]
                             for c in range(args[0] + 1)) for r in range(args[1]))
        if actual != expected or trace["multiplications"] != len(prediction["core"]):
            raise ValueError("generated instruction semantics or trace mismatch")
        theta = tuple(F(i % 3 - 1) for i in range(len(matrix)))
        risk, law, bias = exact_risk(theta, prediction["orbits"], args[0] + 1)
        if risk != law:
            raise ValueError("projection-risk law refuted")
        results.append({"id": case["id"], "dimension": compiled["dimension"],
                        "group_size": prediction["group_size"], "active_entries": len(prediction["core"]),
                        "compiler": compiled["counters"], "oracle_generator_products": prediction["generator_products"],
                        "runtime": trace, "risk": str(risk), "projection_bias2": str(bias)})
    return {"registration_sha256": hashlib.sha256(raw).hexdigest(), "cases": results}


class OrbitDerivationTests(unittest.TestCase):
    def test_registered_predictions_and_independent_oracle(self):
        self.assertEqual(len(registered_results()["cases"]), 7)

    def test_incomplete_and_forged_certificates_fail(self):
        case = json.loads((HERE / "orbit_registration.json").read_text())["cases"][1]
        args = decode(case)
        oracle = predict(*args)
        good = compile_affine(*args)
        self.assertTrue(check_certificate(good, oracle))
        missing = copy.deepcopy(good)
        missing["basis"] = missing["basis"][:-1]
        self.assertFalse(check_certificate(missing, oracle))
        forged = copy.deepcopy(good)
        vector = list(forged["basis"][0])
        vector[0] = F(3)
        forged["basis"] = (tuple(vector),) + forged["basis"][1:]
        self.assertFalse(check_certificate(forged, oracle))
        wrong = {**oracle, "dimension": oracle["dimension"] + 1}
        self.assertFalse(check_certificate(good, wrong))
        wrong_program = {**good, "instructions": ()}
        self.assertFalse(check_certificate(wrong_program, oracle))
        wrong_trace = {**good, "counters": {**good["counters"], "active_entries": 0}}
        self.assertFalse(check_certificate(wrong_trace, oracle))

    def test_noninvariant_support_removes_whole_orbit(self):
        args = decode(json.loads((HERE / "orbit_registration.json").read_text())["cases"][-1])
        result = predict(*args)
        self.assertEqual(result["dimension"], 3)
        self.assertTrue(all((i, i) not in result["core"] for i in range(3)))

    def test_reject_invalid_permutation(self):
        with self.assertRaises(ValueError):
            compile_affine(2, 2, [((0, 0), (0, 1))], {(0, 0)})


if __name__ == "__main__":
    unittest.main()
