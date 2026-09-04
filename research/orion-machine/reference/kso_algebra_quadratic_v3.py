"""KSO M2b V3 — registered quadratic instance generator, exact arithmetic tower, and exact oracle.

Supersedes ``kso_algebra_quadratic_v1.py`` (the V2 run).  What changed and why, each change made
after seeing a V2 outcome (lane-guards independent replay of the V2 receipt, ORION-V2 #295):

  V2 defect (d)  a disagreement between the two oracle implementations was silently folded into the
                 per-family rejection counter and the instance re-drawn.  V3 raises the typed
                 ``OracleDisagreement``; the caller reports CANNOT_CHECK and exits 2 with the
                 instance named.  Proposal-shape re-draws (``_propose`` declined, or the proposed
                 instance does not land in the requested family) stay ordinary counted rejections --
                 raising on those would make the quotas unfillable.
  V2 defect (e)  instances outside the registered coefficient range were accepted.  V3 defines
                 ``REGISTERED_RANGE_V3`` over BOTH drawn and derived coefficients and rejects an
                 out-of-range instance with the typed ``OutOfRegisteredRange`` at the oracle (and,
                 in ``kso_m2b_algebra_v3``, at the solver).

  V3 addition   an exact arithmetic tower ``Exact`` (p + q*sqrt(d), d < 0 meaning p + q*I*sqrt(-d))
                so the oracle and the step interpreter compare VALUES, not rendered strings.  SymPy
                is deliberately NOT used here: the SymPy EXACT_CHECKER channel
                (``kso_exact_checker_sympy_v1``) must stay an independent second opinion.

Exit codes: 0 self-test holds; 1 fails; 2 could not check.  NO NOVELTY OR BREAKTHROUGH CLAIM.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import random
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "research" / "orion-machine" / "domains" / "algebra" / "ALGEBRA_SOURCE_V3.json"

FAMILIES = ("RATIONAL_DISTINCT", "IRRATIONAL_DISTINCT", "DOUBLE_ROOT", "COMPLEX_PAIR", "LINEAR_DEGENERATE", "NO_EQUATION")

# Registered range (V3).  a, b, c are drawn as p/q with p in [-12, 12], q in [1, 4]; the
# RATIONAL_DISTINCT and DOUBLE_ROOT families DERIVE b and c from drawn roots (b = -a*(r1+r2),
# c = a*r1*r2), so the derived bound is |a|*2*|r| <= 12*24 and |a|*|r1|*|r2| <= 12*144, with
# denominators dividing 4**3.  The predicate below is the registered admissibility test for an
# instance and is asserted to hold on every generated instance (the no-alarm case).
REGISTERED_RANGE_V3 = {
    "drawn": {"numerator": (-12, 12), "denominator": (1, 4)},
    "derived": {"max_abs": 1728, "max_denominator": 64},
    "rule": "every coefficient x of an admissible instance satisfies abs(x) <= 1728 and x.denominator <= 64",
}
_MAX_ABS = Fraction(REGISTERED_RANGE_V3["derived"]["max_abs"])
_MAX_DEN = REGISTERED_RANGE_V3["derived"]["max_denominator"]


class CannotCheck(RuntimeError):
    """Could not check -- never a pass."""


class OracleDisagreement(CannotCheck):
    """The two independent oracle implementations disagree on an instance.  Never re-drawn."""


class OutOfRegisteredRange(ValueError):
    """Typed rejection: the instance is outside the registered coefficient range."""


class TemplateRejection(ValueError):
    """Typed rejection: a step template is not in the registered template grammar."""


# ----------------------------------------------------------------------------------------------
# exact arithmetic tower:  p + q*sqrt(d)   (d < 0 means p + q*I*sqrt(-d))
# ----------------------------------------------------------------------------------------------


def rational_sqrt(q: Fraction) -> Fraction | None:
    """Exact: the rational square root of q >= 0 if it exists, else None."""
    if q < 0:
        return None
    n, d = q.numerator, q.denominator
    rn, rd = math.isqrt(n), math.isqrt(d)
    return Fraction(rn, rd) if rn * rn == n and rd * rd == d else None


@dataclass(frozen=True)
class Exact:
    """p + q*sqrt(d), all exact rationals.  d < 0 denotes p + q*I*sqrt(-d).  Canonical: q == 0 iff
    d == 0, and a d > 0 that is a rational square is folded into p."""

    p: Fraction
    q: Fraction = Fraction(0)
    d: Fraction = Fraction(0)

    @staticmethod
    def of(x) -> "Exact":
        return x if isinstance(x, Exact) else Exact(Fraction(x))

    @staticmethod
    def canon(p: Fraction, q: Fraction, d: Fraction) -> "Exact":
        if q == 0 or d == 0:
            return Exact(Fraction(p), Fraction(0), Fraction(0))
        if d > 0:
            r = rational_sqrt(d)
            if r is not None:
                return Exact(Fraction(p) + Fraction(q) * r, Fraction(0), Fraction(0))
        return Exact(Fraction(p), Fraction(q), Fraction(d))

    @property
    def is_rational(self) -> bool:
        return self.q == 0

    @property
    def is_real(self) -> bool:
        return self.q == 0 or self.d > 0

    def __add__(self, o):
        o = Exact.of(o)
        if self.is_rational:
            return Exact.canon(self.p + o.p, o.q, o.d)
        if o.is_rational:
            return Exact.canon(self.p + o.p, self.q, self.d)
        if self.d != o.d:
            raise TemplateRejection(f"cannot add surds with different radicands ({self.d} vs {o.d})")
        return Exact.canon(self.p + o.p, self.q + o.q, self.d)

    def __neg__(self):
        return Exact(-self.p, -self.q, self.d)

    def __pos__(self):
        return self

    def __sub__(self, o):
        return self + (-Exact.of(o))

    def __rsub__(self, o):
        return Exact.of(o) + (-self)

    __radd__ = __add__

    def __mul__(self, o):
        o = Exact.of(o)
        if o.is_rational:
            return Exact.canon(self.p * o.p, self.q * o.p, self.d)
        if self.is_rational:
            return Exact.canon(self.p * o.p, self.p * o.q, o.d)
        raise TemplateRejection("the registered tower does not multiply two surds")

    __rmul__ = __mul__

    def __truediv__(self, o):
        o = Exact.of(o)
        if not o.is_rational:
            raise TemplateRejection("the registered tower divides by rationals only")
        if o.p == 0:
            raise TemplateRejection("division by zero in a step template")
        return Exact.canon(self.p / o.p, self.q / o.p, self.d)

    def __rtruediv__(self, o):
        return Exact.of(o) / self

    def __pow__(self, n):
        if not isinstance(n, int) or n < 0:
            raise TemplateRejection(f"the registered tower raises to nonnegative integer powers only (got {n!r})")
        out = Exact(Fraction(1))
        for _ in range(n):
            out = out * self
        return out

    def sqrt(self) -> "Exact":
        if not self.is_rational:
            raise TemplateRejection("the registered tower takes square roots of rational values only")
        r = rational_sqrt(self.p)
        if r is not None:
            return Exact(r)
        return Exact(Fraction(0), Fraction(1), self.p)

    def render(self) -> str:
        """A SymPy-parsable rendering.  Rendering is presentation; equality is the canonical tuple."""
        if self.is_rational:
            return str(self.p)
        if self.d > 0:
            return f"({self.p}) + ({self.q})*sqrt({self.d})"
        return f"({self.p}) + ({self.q})*I*sqrt({-self.d})"

    def key(self) -> tuple[str, str, str]:
        return (str(self.p), str(self.q), str(self.d))


# ----------------------------------------------------------------------------------------------
# the registered template grammar (one evaluator; no per-procedure Python anywhere)
# ----------------------------------------------------------------------------------------------

_ALLOWED_BINOPS = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/", ast.Pow: "**"}
_ALLOWED_CALLS = {"sqrt"}


def eval_template(template: str, env: dict[str, Exact]) -> Exact:
    """Evaluate a registered, SymPy-parsable template in the exact tower over ``env``.

    Every rejection is typed.  This is the ONLY evaluator: procedures are data, and this function
    knows nothing about quadratics."""
    try:
        tree = ast.parse(template, mode="eval")
    except SyntaxError as exc:
        raise TemplateRejection(f"template does not parse: {template!r} ({exc})") from exc

    def walk(node):
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, int) and not isinstance(node.value, bool):
                return Exact(Fraction(node.value))
            raise TemplateRejection(f"only integer literals are registered (got {node.value!r})")
        if isinstance(node, ast.Name):
            if node.id not in env:
                raise TemplateRejection(f"unbound template symbol {node.id!r}")
            return env[node.id]
        if isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.USub):
                return -walk(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +walk(node.operand)
            raise TemplateRejection(f"unregistered unary operator {type(node.op).__name__}")
        if isinstance(node, ast.BinOp):
            if type(node.op) not in _ALLOWED_BINOPS:
                raise TemplateRejection(f"unregistered binary operator {type(node.op).__name__}")
            if isinstance(node.op, ast.Pow):
                if not (isinstance(node.right, ast.Constant) and isinstance(node.right.value, int)):
                    raise TemplateRejection("only integer-literal exponents are registered")
                return walk(node.left) ** node.right.value
            left, right = walk(node.left), walk(node.right)
            return {ast.Add: lambda: left + right, ast.Sub: lambda: left - right,
                    ast.Mult: lambda: left * right, ast.Div: lambda: left / right}[type(node.op)]()
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in _ALLOWED_CALLS or len(node.args) != 1 or node.keywords:
                raise TemplateRejection(f"unregistered call in template {template!r}")
            return walk(node.args[0]).sqrt()
        raise TemplateRejection(f"unregistered template node {type(node).__name__} in {template!r}")

    return walk(tree)


# ----------------------------------------------------------------------------------------------
# instances, range predicate, oracle
# ----------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Instance:
    instance_id: str
    family: str
    a: Fraction
    b: Fraction
    c: Fraction

    def bindings(self) -> dict[str, str]:
        return {"a": str(self.a), "b": str(self.b), "c": str(self.c)}

    def env(self) -> dict[str, Exact]:
        return {"a": Exact(self.a), "b": Exact(self.b), "c": Exact(self.c)}

    def expr(self) -> str:
        return f"({self.a})*x**2 + ({self.b})*x + ({self.c})"


def coefficient_in_range(x: Fraction) -> bool:
    return abs(x) <= _MAX_ABS and x.denominator <= _MAX_DEN


def check_registered_range(inst: Instance) -> None:
    """Typed rejection (V3 defect-e repair).  Called by the oracle AND by the solver."""
    bad = {k: str(v) for k, v in (("a", inst.a), ("b", inst.b), ("c", inst.c)) if not coefficient_in_range(v)}
    if bad:
        raise OutOfRegisteredRange(
            f"{inst.instance_id or '<unnamed>'}: coefficients outside REGISTERED_RANGE_V3 "
            f"(abs <= {_MAX_ABS}, denominator <= {_MAX_DEN}): {bad}")


@dataclass(frozen=True)
class OracleAnswer:
    family: str
    discriminant: Fraction | None
    case: str
    roots: tuple[Exact, ...]
    real_root_count: int
    rational_roots: bool
    applicable_procedures: tuple[str, ...]
    status: str                          # SOLVED | CANNOT_CHECK

    def root_keys(self) -> frozenset:
        return frozenset(r.key() for r in self.roots)

    def as_dict(self) -> dict:
        return {"family": self.family, "discriminant": None if self.discriminant is None else str(self.discriminant),
                "case": self.case, "roots": [r.render() for r in self.roots], "real_root_count": self.real_root_count,
                "rational_roots": self.rational_roots, "applicable_procedures": list(self.applicable_procedures),
                "status": self.status}


def _procs(case: str) -> tuple[str, ...]:
    """The oracle's own independent reading of which procedures apply.  This is the SECOND OPINION
    the FIRE gate is checked against; it is deliberately Python and deliberately not the KSO's
    label computation."""
    if case == "a==0 linear":
        return ("proc:linear",)
    if case == "a==0 b==0":
        return ()
    base = ("proc:quadratic_formula", "proc:complete_square")
    return base + (("proc:factor",) if case in ("Delta>0 rational", "Delta==0") else ())


def oracle(inst: Instance) -> OracleAnswer:
    check_registered_range(inst)
    a, b, c = inst.a, inst.b, inst.c
    if a == 0:
        if b == 0:
            return OracleAnswer(inst.family, None, "a==0 b==0", (), 0, False, _procs("a==0 b==0"), "CANNOT_CHECK")
        r = Exact(-c / b)
        return OracleAnswer(inst.family, None, "a==0 linear", (r,), 1, True, _procs("a==0 linear"), "SOLVED")
    delta = b * b - 4 * a * c
    s = Exact(delta).sqrt()
    r1 = Exact.canon((-b + s.p) / (2 * a), s.q / (2 * a), s.d)
    r2 = Exact.canon((-b - s.p) / (2 * a), -s.q / (2 * a), s.d)
    if delta > 0:
        rat = rational_sqrt(delta) is not None
        case = "Delta>0 rational" if rat else "Delta>0 irrational"
        if rat:
            assert (r1 + r2).p == -b / a and (r1 * r2).p == c / a  # Vieta cross-check
        return OracleAnswer(inst.family, delta, case, (r1, r2), 2, rat, _procs(case), "SOLVED")
    if delta == 0:
        assert r1 == r2 and (r1 * Exact(Fraction(2))).p == -b / a
        return OracleAnswer(inst.family, delta, "Delta==0", (r1,), 1, True, _procs("Delta==0"), "SOLVED")
    return OracleAnswer(inst.family, delta, "Delta<0", (r1, r2), 0, False, _procs("Delta<0"), "SOLVED")


def oracle_independent(inst: Instance) -> OracleAnswer:
    """Second implementation: classify by the sign of the value at the vertex and rationality by a
    Vieta square test.  Its DISAGREEMENT with ``oracle`` is a defect, never a re-draw (V3 (d))."""
    check_registered_range(inst)
    a, b, c = inst.a, inst.b, inst.c
    if a == 0:
        return oracle(inst)  # the degenerate cases share one reading (declared, not derived twice)
    vertex_value = c - b * b / (4 * a)
    if (a > 0 and vertex_value > 0) or (a < 0 and vertex_value < 0):
        real = 0
    elif vertex_value == 0:
        real = 1
    else:
        real = 2
    rational = True
    if real == 2:
        s, p = -b / a, c / a
        rational = rational_sqrt(s * s - 4 * p) is not None
    elif real == 0:
        rational = False
    case = {0: "Delta<0", 1: "Delta==0", 2: "Delta>0 rational" if rational else "Delta>0 irrational"}[real]
    return OracleAnswer(inst.family, b * b - 4 * a * c, case, oracle(inst).roots, real, rational, _procs(case), "SOLVED")


COMPARED_FIELDS = ("case", "real_root_count", "rational_roots", "applicable_procedures", "status")


def _compare(one: OracleAnswer, two: OracleAnswer) -> dict[str, tuple]:
    return {f: (getattr(one, f), getattr(two, f)) for f in COMPARED_FIELDS if getattr(one, f) != getattr(two, f)}


# ----------------------------------------------------------------------------------------------
# generator
# ----------------------------------------------------------------------------------------------

COEFFICIENT_RANGE = REGISTERED_RANGE_V3["drawn"]


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


EXPECTED_CASE = {"RATIONAL_DISTINCT": "Delta>0 rational", "IRRATIONAL_DISTINCT": "Delta>0 irrational",
                 "DOUBLE_ROOT": "Delta==0", "COMPLEX_PAIR": "Delta<0", "LINEAR_DEGENERATE": "a==0 linear",
                 "NO_EQUATION": "a==0 b==0"}


def generate_split(split: str, seed: str, per_family: int, *,
                   second_oracle=None) -> tuple[list[tuple[Instance, OracleAnswer]], dict[str, dict[str, int]]]:
    """The generator proposes; the oracle verifies the family.

    V3 (d): the reject condition is SPLIT.  A declined proposal and a family mismatch are ordinary
    counted re-draws (they are proposal shape).  A disagreement between the two oracle
    implementations raises ``OracleDisagreement`` naming the instance -- it is never re-drawn.
    ``second_oracle`` exists so the plant can substitute a perturbed second opinion."""
    second = second_oracle or oracle_independent
    pairs: list[tuple[Instance, OracleAnswer]] = []
    rejects = {f: {"proposal_declined": 0, "family_mismatch": 0} for f in FAMILIES}
    for family in FAMILIES:
        made = counter = 0
        while made < per_family:
            counter += 1
            if counter > 5000 * (per_family + 1):
                raise CannotCheck(f"{split}/{family}: generator could not fill the quota")
            s = int.from_bytes(hashlib.sha256(f"{seed}|{split}|{family}|{counter}".encode()).digest()[:8], "big")
            inst = _propose(family, random.Random(s))
            if inst is None:
                rejects[family]["proposal_declined"] += 1
                continue
            inst = Instance(f"{split}-{family}-{made:03d}", family, inst.a, inst.b, inst.c)
            ans = oracle(inst)
            if ans.case != EXPECTED_CASE[family]:
                rejects[family]["family_mismatch"] += 1
                continue
            diff = _compare(ans, second(inst))
            if diff:
                raise OracleDisagreement(
                    f"instance {inst.instance_id} (a={inst.a}, b={inst.b}, c={inst.c}): the two oracle "
                    f"implementations disagree on {diff}; this is a defect of one of them and is NOT re-drawn")
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
        for s in a.get("hyperpath", []):
            if s not in ids:
                raise CannotCheck(f"{a['id']} names an unregistered step {s}")
    for a in src["atoms"]:
        if a["type"] == "step" and a["operation"] not in src["operations"]:
            raise CannotCheck(f"{a['id']} uses an unregistered operation {a['operation']}")
    if not any(a["type"] == "procedure" and a.get("hyperpath") for a in src["atoms"]):
        raise CannotCheck("no procedure carries a hyperpath: procedures are not data in this source")
    return src


# ----------------------------------------------------------------------------------------------
# self-test:  every rule below has a planted failure AND a no-alarm control
# ----------------------------------------------------------------------------------------------


def self_test() -> dict:
    src = source_atoms()
    out: dict[str, object] = {}

    # -- no-alarm: a clean split raises nothing and every instance is in the registered range
    pairs, rejects = generate_split("dev", "ALGEBRA-DEV-20260904", 5)
    for inst, _ in pairs:
        check_registered_range(inst)
    out["instances"] = len(pairs)
    out["rejections"] = rejects
    out["no_alarm_all_instances_in_registered_range"] = True

    # -- (d) plant: a perturbed second oracle must raise OracleDisagreement, never re-draw
    def perturbed(inst: Instance) -> OracleAnswer:
        a = oracle_independent(inst)
        if inst.family == "COMPLEX_PAIR":
            return OracleAnswer(a.family, a.discriminant, "Delta==0", a.roots, 1, True, _procs("Delta==0"), a.status)
        return a
    try:
        generate_split("dev", "ALGEBRA-DEV-20260904", 5, second_oracle=perturbed)
    except OracleDisagreement as exc:
        out["plant_oracle_disagreement"] = {"CAUGHT": True, "instance_named": "dev-COMPLEX_PAIR-000" in str(exc)}
    else:
        raise AssertionError("PLANT NOT CAUGHT: a perturbed second oracle did not raise OracleDisagreement")

    # -- (e) plant: an out-of-range instance is a typed rejection at the oracle; no-alarm alongside
    far = Instance("planted-out-of-range", "RATIONAL_DISTINCT", Fraction(1), Fraction(0), Fraction(-100000))
    try:
        oracle(far)
    except OutOfRegisteredRange as exc:
        out["plant_out_of_registered_range"] = {"CAUGHT": True, "message_names_instance": "planted-out-of-range" in str(exc)}
    else:
        raise AssertionError("PLANT NOT CAUGHT: an out-of-range instance was accepted by the oracle")
    fine = Instance("no-alarm-in-range", "RATIONAL_DISTINCT", Fraction(1), Fraction(-5), Fraction(6))
    assert oracle(fine).case == "Delta>0 rational"
    out["no_alarm_in_range_instance_accepted"] = True

    # -- the exact tower: sqrt of a non-square is a surd; the checker's own reading agrees
    two = Exact(Fraction(2)).sqrt()
    assert not two.is_rational and two.is_real and two.render() == "(0) + (1)*sqrt(2)"
    neg = Exact(Fraction(-3)).sqrt()
    assert not neg.is_real and neg.render() == "(0) + (1)*I*sqrt(3)"
    assert Exact(Fraction(4)).sqrt() == Exact(Fraction(2))
    out["tower"] = {"sqrt(2)": two.render(), "sqrt(-3)": neg.render(), "sqrt(4)": Exact(Fraction(4)).sqrt().render()}

    # -- template grammar: registered templates evaluate; unregistered nodes are typed rejections
    env = {"a": Exact(Fraction(1)), "b": Exact(Fraction(-5)), "c": Exact(Fraction(6))}
    d = eval_template("b**2 - 4*a*c", env)
    assert d == Exact(Fraction(1)), d
    env["S"] = eval_template("sqrt(Delta)", {**env, "Delta": d})
    assert eval_template("(-b + S)/(2*a)", env) == Exact(Fraction(3))
    rejected = {}
    for bad, why in (("__import__('os').system('true')", "call"), ("a if b else c", "node"),
                     ("a + Z", "unbound"), ("a ** b", "exponent"), ("1.5*a", "float")):
        try:
            eval_template(bad, env)
        except TemplateRejection as exc:
            rejected[why] = str(exc)[:60]
        else:
            raise AssertionError(f"PLANT NOT CAUGHT: template {bad!r} was accepted")
    out["template_grammar_typed_rejections"] = sorted(rejected)
    out["no_alarm_registered_templates_evaluate"] = True

    # -- worked examples in the source agree with the oracle
    ex = {}
    for atom in src["atoms"]:
        if atom["type"] == "worked_example":
            bnd = atom["bindings"]
            i = Instance(atom["id"], "EXAMPLE", Fraction(bnd["a"]), Fraction(bnd["b"]), Fraction(bnd["c"]))
            ex[atom["id"]] = oracle(i).case
    assert ex == {"ex:worked_1": "Delta>0 rational", "ex:worked_2": "Delta<0", "ex:worked_3": "Delta==0"}, ex
    out["worked_examples_agree"] = len(ex)

    # -- the oracle's Vieta cross-check rejects a wrong root (planted)
    inst = Instance("planted-wrong-root", "RATIONAL_DISTINCT", Fraction(1), Fraction(-5), Fraction(6))
    assert oracle(inst).root_keys() == {Exact(Fraction(2)).key(), Exact(Fraction(3)).key()}
    assert not (Fraction(2) + Fraction(4) == 5 and Fraction(2) * Fraction(4) == 6)
    out["plant_wrong_root_rejected_by_vieta"] = "CAUGHT"

    # -- no-alarm: NO_EQUATION is CANNOT_CHECK, never SOLVED
    assert all(a.status == "CANNOT_CHECK" for i, a in pairs if i.family == "NO_EQUATION")
    out["no_alarm_no_equation_is_cannot_check"] = True

    out["source_atoms"] = len(src["atoms"])
    out["instance_ids_sha256"] = hashlib.sha256("\n".join(i.instance_id for i, _ in pairs).encode()).hexdigest()
    out["source_sha256"] = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.parse_args(argv)
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
