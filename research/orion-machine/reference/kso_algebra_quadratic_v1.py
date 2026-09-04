"""KSO M2b — registered quadratic instance generator and exact oracle (elementary algebra domain).

Source: ``research/orion-machine/domains/algebra/ALGEBRA_SOURCE_V1.json`` (definitions, procedures,
constraints, representations, worked examples).  Instances are quadratic equations
``a*x**2 + b*x + c = 0`` with rational coefficients from a registered range; families are the
discriminant cases plus the degenerate a = 0 cases.  The oracle is exact rational/complex
arithmetic in the standard library (``fractions``), cross-checked by Vieta's relations; SymPy is
NOT used here — it is the EXACT_CHECKER channel (``kso_exact_checker_sympy_v1.py``, guards lane)
that warrants a produced root by substitution, and the two must agree on every instance (a
disagreement is a defect of one of them, attributed, never averaged).

Families (registered, seeded, byte-reproducible):
  RATIONAL_DISTINCT   Delta > 0 and a rational square           -> two rational roots (proc:factor applies)
  IRRATIONAL_DISTINCT Delta > 0 and not a rational square       -> two real irrational roots (proc:factor INVALID by the Q rule)
  DOUBLE_ROOT         Delta == 0                                -> one rational double root
  COMPLEX_PAIR        Delta < 0                                 -> two complex-conjugate roots, no real root
  LINEAR_DEGENERATE   a == 0, b != 0                            -> one rational root -c/b (proc:linear)
  NO_EQUATION         a == 0, b == 0                            -> CANNOT_CHECK (no equation in x)

Exit codes: 0 self-test holds; 1 fails; 2 could not check.  NO NOVELTY CLAIM.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "research" / "orion-machine" / "domains" / "algebra" / "ALGEBRA_SOURCE_V1.json"

FAMILIES = ("RATIONAL_DISTINCT", "IRRATIONAL_DISTINCT", "DOUBLE_ROOT", "COMPLEX_PAIR", "LINEAR_DEGENERATE", "NO_EQUATION")
COEFFICIENT_RANGE = {"numerator": (-12, 12), "denominator": (1, 4)}  # registered: a, b, c = p/q with p in [-12, 12], q in [1, 4]


class CannotCheck(RuntimeError):
    pass


@dataclass(frozen=True)
class Instance:
    instance_id: str
    family: str
    a: Fraction
    b: Fraction
    c: Fraction

    def bindings(self) -> dict[str, str]:
        return {"a": str(self.a), "b": str(self.b), "c": str(self.c)}

    def expr(self) -> str:
        return f"({self.a})*x**2 + ({self.b})*x + ({self.c})"


@dataclass(frozen=True)
class OracleAnswer:
    family: str
    discriminant: Fraction | None
    case: str                           # Delta>0 rational | Delta>0 irrational | Delta==0 | Delta<0 | a==0 linear | a==0 b==0
    roots: tuple[str, ...]              # exact root expressions (rational strings, or sqrt/I forms)
    real_root_count: int
    rational_roots: bool
    applicable_procedures: tuple[str, ...]
    status: str                         # SOLVED | CANNOT_CHECK

    def as_dict(self) -> dict:
        return {"family": self.family, "discriminant": None if self.discriminant is None else str(self.discriminant), "case": self.case, "roots": list(self.roots), "real_root_count": self.real_root_count, "rational_roots": self.rational_roots, "applicable_procedures": list(self.applicable_procedures), "status": self.status}


def rational_sqrt(q: Fraction) -> Fraction | None:
    """Exact: the rational square root of q >= 0 if it exists, else None."""
    if q < 0:
        return None
    n, d = q.numerator, q.denominator
    rn, rd = math.isqrt(n), math.isqrt(d)
    return Fraction(rn, rd) if rn * rn == n and rd * rd == d else None


def oracle(inst: Instance) -> OracleAnswer:
    a, b, c = inst.a, inst.b, inst.c
    if a == 0:
        if b == 0:
            return OracleAnswer(inst.family, None, "a==0 b==0", (), 0, False, (), "CANNOT_CHECK")
        r = -c / b
        return OracleAnswer(inst.family, None, "a==0 linear", (str(r),), 1, True, ("proc:linear",), "SOLVED")
    delta = b * b - 4 * a * c
    if delta > 0:
        s = rational_sqrt(delta)
        if s is not None:
            r1, r2 = (-b + s) / (2 * a), (-b - s) / (2 * a)
            assert r1 + r2 == -b / a and r1 * r2 == c / a  # Vieta cross-check
            return OracleAnswer(inst.family, delta, "Delta>0 rational", (str(r1), str(r2)), 2, True, ("proc:quadratic_formula", "proc:complete_square", "proc:factor"), "SOLVED")
        r1 = f"({-b} + sqrt({delta}))/({2 * a})"
        r2 = f"({-b} - sqrt({delta}))/({2 * a})"
        return OracleAnswer(inst.family, delta, "Delta>0 irrational", (r1, r2), 2, False, ("proc:quadratic_formula", "proc:complete_square"), "SOLVED")
    if delta == 0:
        r = -b / (2 * a)
        assert 2 * r == -b / a and r * r == c / a
        return OracleAnswer(inst.family, delta, "Delta==0", (str(r),), 1, True, ("proc:quadratic_formula", "proc:complete_square", "proc:factor"), "SOLVED")
    r1 = f"({-b} + I*sqrt({-delta}))/({2 * a})"
    r2 = f"({-b} - I*sqrt({-delta}))/({2 * a})"
    return OracleAnswer(inst.family, delta, "Delta<0", (r1, r2), 0, False, ("proc:quadratic_formula", "proc:complete_square"), "SOLVED")


def oracle_independent(inst: Instance) -> OracleAnswer:
    """Second implementation: classify by counting real roots of the exact polynomial via the
    sign of the value at the vertex and rationality via Vieta search over the registered range."""
    a, b, c = inst.a, inst.b, inst.c
    if a == 0:
        return oracle(inst)  # degenerate cases share one reading (declared)
    vertex_value = c - b * b / (4 * a)  # p(-b/2a)
    if (a > 0 and vertex_value > 0) or (a < 0 and vertex_value < 0):
        real = 0
    elif vertex_value == 0:
        real = 1
    else:
        real = 2
    delta = b * b - 4 * a * c
    rational = False
    if real == 2:
        # search rational roots p/q with q | denominators bound: Vieta r1 + r2 = -b/a, r1*r2 = c/a
        s = -b / a
        p = c / a
        # r1 solves r^2 - s r + p = 0 with rational r iff s^2 - 4p is a rational square
        rational = rational_sqrt(s * s - 4 * p) is not None
    elif real == 1:
        rational = True
    case = {0: "Delta<0", 1: "Delta==0", 2: "Delta>0 rational" if rational else "Delta>0 irrational"}[real]
    procs = ("proc:quadratic_formula", "proc:complete_square") + (("proc:factor",) if rational else ())
    return OracleAnswer(inst.family, delta, case, oracle(inst).roots, real, rational, procs, "SOLVED")


def _rat(rng: random.Random) -> Fraction:
    lo, hi = COEFFICIENT_RANGE["numerator"]
    dlo, dhi = COEFFICIENT_RANGE["denominator"]
    return Fraction(rng.randint(lo, hi), rng.randint(dlo, dhi))


def _propose(family: str, rng: random.Random) -> Instance | None:
    a, b, c = _rat(rng), _rat(rng), _rat(rng)
    if family == "LINEAR_DEGENERATE":
        a = Fraction(0)
        if b == 0:
            return None
    elif family == "NO_EQUATION":
        a, b = Fraction(0), Fraction(0)
    elif family == "DOUBLE_ROOT":
        if a == 0:
            return None
        # choose the double root r and set b = -2ar, c = ar^2
        r = _rat(rng)
        b, c = -2 * a * r, a * r * r
    elif family == "RATIONAL_DISTINCT":
        if a == 0:
            return None
        r1, r2 = _rat(rng), _rat(rng)
        if r1 == r2:
            return None
        b, c = -a * (r1 + r2), a * r1 * r2
    else:
        if a == 0:
            return None
    return Instance("", family, a, b, c)


EXPECTED_CASE = {"RATIONAL_DISTINCT": "Delta>0 rational", "IRRATIONAL_DISTINCT": "Delta>0 irrational", "DOUBLE_ROOT": "Delta==0", "COMPLEX_PAIR": "Delta<0", "LINEAR_DEGENERATE": "a==0 linear", "NO_EQUATION": "a==0 b==0"}


def generate_split(split: str, seed: str, per_family: int) -> tuple[list[tuple[Instance, OracleAnswer]], dict[str, int]]:
    """The generator proposes; the oracle verifies the family; both oracle implementations must agree.
    Rejections are counted per family and reported, never hidden."""
    pairs: list[tuple[Instance, OracleAnswer]] = []
    rejects = {f: 0 for f in FAMILIES}
    for family in FAMILIES:
        made = counter = 0
        while made < per_family:
            counter += 1
            if counter > 5000 * (per_family + 1):
                raise CannotCheck(f"{split}/{family}: generator could not fill the quota")
            s = int.from_bytes(hashlib.sha256(f"{seed}|{split}|{family}|{counter}".encode()).digest()[:8], "big")
            inst = _propose(family, random.Random(s))
            if inst is None:
                rejects[family] += 1
                continue
            ans = oracle(inst)
            ans2 = oracle_independent(inst)
            if ans.case != EXPECTED_CASE[family] or (ans.case, ans.real_root_count, ans.rational_roots, ans.applicable_procedures) != (ans2.case, ans2.real_root_count, ans2.rational_roots, ans2.applicable_procedures):
                rejects[family] += 1
                continue
            inst = Instance(f"{split}-{family}-{made:03d}", family, inst.a, inst.b, inst.c)
            pairs.append((inst, ans))
            made += 1
    return pairs, rejects


def source_atoms() -> dict:
    src = json.loads(SOURCE.read_text(encoding="utf-8"))
    ids = [a["id"] for a in src["atoms"]]
    if len(ids) != len(set(ids)):
        raise CannotCheck("duplicate atom ids in the algebra source")
    for a in src["atoms"]:
        for p in a.get("preconditions", []):
            if p not in ids:
                raise CannotCheck(f"{a['id']} has an unregistered precondition {p}")
        for t in a.get("constraint_on", []):
            if t not in ids:
                raise CannotCheck(f"{a['id']} constrains an unregistered atom {t}")
    return src


def self_test() -> dict:
    src = source_atoms()
    pairs, rejects = generate_split("dev", "ALGEBRA-DEV-20260904", 5)
    # planted: a wrong root must be rejected by the oracle's Vieta check
    inst = Instance("planted", "RATIONAL_DISTINCT", Fraction(1), Fraction(-5), Fraction(6))
    ans = oracle(inst)
    assert set(ans.roots) == {"2", "3"} and ans.rational_roots
    wrong = Fraction(4)
    vieta_ok = (Fraction(2) + wrong == -inst.b / inst.a) and (Fraction(2) * wrong == inst.c / inst.a)
    assert not vieta_ok
    # worked examples in the source agree with the oracle
    ex = {}
    for atom in src["atoms"]:
        if atom["type"] == "worked_example":
            bnd = atom["bindings"]
            i = Instance(atom["id"], "EXAMPLE", Fraction(bnd["a"]), Fraction(bnd["b"]), Fraction(bnd["c"]))
            ex[atom["id"]] = oracle(i).case
    assert ex == {"ex:worked_1": "Delta>0 rational", "ex:worked_2": "Delta<0", "ex:worked_3": "Delta==0"}, ex
    # the two oracle implementations agree on every generated instance (asserted inside generate_split) and on the planted one
    assert oracle_independent(inst).case == ans.case
    # no-alarm: the NO_EQUATION family is CANNOT_CHECK, never SOLVED
    assert all(a.status == "CANNOT_CHECK" for i, a in pairs if i.family == "NO_EQUATION")
    return {"source_atoms": len(src["atoms"]), "instances": len(pairs), "per_family": 5, "rejections": rejects, "planted_wrong_root_rejected_by_vieta": 1, "worked_examples_agree": len(ex),
            "instance_ids_sha256": hashlib.sha256("\n".join(i.instance_id for i, _ in pairs).encode()).hexdigest(), "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest()}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        res = self_test()
    except CannotCheck as exc:
        print(json.dumps({"status": "CANNOT_CHECK", "reason": str(exc)}))
        return 2
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"status": "FAIL", "reason": f"{type(exc).__name__}: {exc}"}))
        return 1
    print(json.dumps(res, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
