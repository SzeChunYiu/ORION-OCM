"""SymPy EXACT_CHECKER channel: every rule has a plant that fails it; CANNOT_CHECK is never VALID;
only this checker warrants a ROOT_CLAIM, whatever the producer's label says."""
from __future__ import annotations

import importlib.util
import json
import random
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MOD = ROOT / "research" / "orion-machine" / "reference" / "kso_exact_checker_sympy_v1.py"
sympy = pytest.importorskip("sympy", reason="SymPy is the channel; without it the checker answers CANNOT_CHECK (covered below by the CLI test)")


@pytest.fixture(scope="module")
def m():
    spec = importlib.util.spec_from_file_location("kso_exact_checker_sympy_v1", MOD)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["kso_exact_checker_sympy_v1"] = mod
    spec.loader.exec_module(mod)
    return mod


E = "a*x**2 + b*x + c"
FORMULA = ("(-b + sqrt(b**2 - 4*a*c))/(2*a)", "(-b - sqrt(b**2 - 4*a*c))/(2*a)")


def atom(aid, root, domain="C", label="EXACT_CHECKER", expr=E, **extra):
    d = {"atom_id": aid, "kind": "ROOT_CLAIM", "variable": "x", "expr": expr, "root": root, "domain": domain, "label_channel": label}
    d.update(extra)
    return d


def inst(a, b, c):
    return {"instance_id": f"i-{a}-{b}-{c}", "bindings": {"a": str(a), "b": str(b), "c": str(c)}}


def test_plant_table_holds(m):
    for name, at, ins, want in m.plant_table():
        assert m.check(at, ins)["status"] == want, name


@pytest.mark.parametrize("name,at,ins,want", [(n, a, i, w) for n, a, i, w in [
    ("wrong root -> INVALID", atom("p1", "3"), inst(1, -3, 2), "INVALID"),
    ("Δ<0 symbolic root over C -> VALID", atom("p2", FORMULA[0]), inst(1, 0, 1), "VALID"),
    ("Δ<0 the same over R -> INVALID", atom("p3", FORMULA[0], "R"), inst(1, 0, 1), "INVALID"),
    ("a=0 linear path VALID", atom("p4", "2", "Q"), inst(0, 2, -4), "VALID"),
    ("a=0 linear path INVALID", atom("p5", "5", "Q"), inst(0, 2, -4), "INVALID"),
    ("a=b=0 -> CANNOT_CHECK by rule", atom("p6", "0"), inst(0, 0, 5), "CANNOT_CHECK"),
    ("unparsable -> CANNOT_CHECK never VALID", atom("p7", "2", expr="a*x**2 +"), inst(1, -3, 2), "CANNOT_CHECK"),
    ("Q-domain irrational root -> INVALID", atom("p8", "sqrt(2)", "Q"), inst(1, 0, -2), "INVALID"),
]])
def test_named_plants(m, name, at, ins, want):
    assert m.check(at, ins)["status"] == want, name


def test_instruction_label_never_warrants_a_wrong_root(m):
    r = m.check(atom("w", "3", label="INSTRUCTION"), inst(1, -3, 2))
    assert r["status"] == "INVALID" and not m.is_warranted(r) and m.warrant_label(r, 1) == ()
    assert r["producer_label_ignored"] == "INSTRUCTION" and r["certificate"] == "EXACT_CHECKER"


def test_only_a_valid_result_is_warranted_and_the_label_composes_with_the_procedure(m):
    r = m.check(atom("ok", "1", "Q", label="INSTRUCTION", produced_by="proc:factoring"), inst(1, -3, 2))
    assert m.is_warranted(r) and r["produced_by"] == "proc:factoring"
    assert m.warrant_label(r, 9) == (frozenset({9}),)
    assert m.warrant_label(r, 9, (frozenset({2}), frozenset({4}))) == (frozenset({2, 9}), frozenset({4, 9}))


def test_cannot_check_is_never_valid_and_carries_a_reason(m):
    for at, ins in [(atom("c1", "2", expr="sqrt("), inst(1, 2, 3)), (atom("c2", "2", "Z"), inst(1, 2, 3)),
                    (atom("c3", "2", kind="worked_example"), inst(1, 2, 3)), (atom("c4", "2"), {"bindings": {"a": "1"}}),
                    (atom("c5", "x"), inst(1, 2, 3)), (atom("c6", FORMULA[0], "R"), {"bindings": {"a": "1", "b": "p", "c": "q"}})]:
        r = m.check(at, ins)
        assert r["status"] == "CANNOT_CHECK" and r["witness"].get("reason") and not m.is_warranted(r)


def test_quadratic_formula_roots_are_valid_over_c_for_random_rational_coefficients(m):
    rng = random.Random(20260904)
    n_valid = 0
    for _ in range(25):
        a = Fraction(rng.randint(1, 9), rng.randint(1, 5)) * rng.choice((-1, 1))
        b = Fraction(rng.randint(-9, 9), rng.randint(1, 5))
        c = Fraction(rng.randint(-9, 9), rng.randint(1, 5))
        ins = inst(a, b, c)
        for root in FORMULA:
            r = m.check(atom("f", root), ins)
            assert r["status"] == "VALID", (a, b, c, root, r["witness"])
            n_valid += 1
        # a shifted root is never a root of a quadratic with a != 0 (it would need two roots at distance 1 to coincide)
        shifted = m.check(atom("s", f"({FORMULA[0]}) + 1"), ins)
        assert shifted["status"] in ("INVALID", "VALID")
        if shifted["status"] == "VALID":
            # only possible when the other root is exactly root+1: check that is what happened
            sp = sympy
            x = sp.Symbol("x")
            roots = sp.solve(sp.Rational(a.numerator, a.denominator) * x**2 + sp.Rational(b.numerator, b.denominator) * x + sp.Rational(c.numerator, c.denominator), x)
            assert len(roots) == 2 and sp.simplify(abs(roots[0] - roots[1]) - 1) == 0
    assert n_valid == 50


def test_real_domain_uses_membership_not_a_numeric_guess(m):
    # sqrt(2) is real and VALID over R; I*sqrt(2) is not
    assert m.check(atom("r1", "sqrt(2)", "R"), inst(1, 0, -2))["status"] == "VALID"
    assert m.check(atom("r2", "I*sqrt(2)", "R"), inst(1, 0, 2))["status"] == "INVALID"
    assert m.check(atom("r3", "I*sqrt(2)", "C"), inst(1, 0, 2))["status"] == "VALID"


def test_cli_exit_codes(m, tmp_path):
    ins = tmp_path / "inst.json"; ins.write_text(json.dumps(inst(1, -3, 2)))
    good = tmp_path / "good.json"; good.write_text(json.dumps([atom("g1", "1", "Q"), atom("g2", "2", "Q")]))
    bad = tmp_path / "bad.json"; bad.write_text(json.dumps([atom("g1", "1", "Q"), atom("b1", "3", "Q")]))
    cnc = tmp_path / "cnc.json"; cnc.write_text(json.dumps([atom("g1", "1", "Q"), atom("u1", "sqrt(", "Q")]))
    empty = tmp_path / "empty.json"; empty.write_text("[]")
    run = lambda f: subprocess.run([sys.executable, str(MOD), "--atoms", str(f), "--instance", str(ins)], capture_output=True, text=True)  # noqa: E731
    assert run(good).returncode == 0
    assert run(bad).returncode == 1
    r = run(cnc); assert r.returncode == 2 and "COULD NOT CHECK" in r.stderr
    r = run(empty); assert r.returncode == 2 and "empty list is not a pass" in r.stderr
    st = subprocess.run([sys.executable, str(MOD), "--self-test"], capture_output=True, text=True)
    assert st.returncode == 0 and "self-test passed" in st.stdout and "SymPy" in st.stdout


def test_without_sympy_the_checker_answers_cannot_check(tmp_path):
    # run the CLI in an interpreter where `import sympy` fails, by shadowing it on sys.path
    shadow = tmp_path / "sympy"; shadow.mkdir()
    (shadow / "__init__.py").write_text("raise ImportError('shadowed for the test')\n")
    env = {"PYTHONPATH": str(tmp_path), "PATH": "/usr/bin:/bin"}
    r = subprocess.run([sys.executable, str(MOD), "--self-test"], capture_output=True, text=True, env=env)
    assert r.returncode == 2 and "SymPy is not importable" in r.stdout


# ---- agreement with lane-ocm-3's quadratic generator/oracle on the 30 dev instances -------------
# A disagreement is attributed per instance, never averaged. Skips with an explicit PENDING reason
# while `reference/kso_algebra_quadratic_v1.py` is not on the branch; that skip is reported in the PR.

ALGEBRA = ROOT / "research" / "orion-machine" / "reference" / "kso_algebra_quadratic_v1.py"


def _load_algebra():
    if not ALGEBRA.exists():
        pytest.skip(f"PENDING: {ALGEBRA.name} (lane-ocm-3) is not on this branch; agreement not run")
    spec = importlib.util.spec_from_file_location("kso_algebra_quadratic_v1", ALGEBRA)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["kso_algebra_quadratic_v1"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_checker_agrees_with_the_quadratic_oracle_on_every_dev_instance(m):
    alg = _load_algebra()
    gen = getattr(alg, "generate_split", None) or getattr(alg, "generate_dev", None) or getattr(alg, "dev_instances", None)
    assert gen is not None, "kso_algebra_quadratic_v1 exposes no generate_split/generate_dev/dev_instances"
    # Successor adapter: the archived generator returns (pairs, rejection counts)
    # and requires an explicit quota. Five per each of six families gives 30.
    instances, rejected = gen("dev", "ALGEBRA-DEV-20260904", 5)
    assert set(rejected) == set(alg.FAMILIES)
    assert len(instances) == 30, len(instances)
    disagreements = []
    decided = 0
    for it in instances:
        inst = it[0] if isinstance(it, tuple) else it
        out = alg.oracle(inst)
        status = getattr(out, "status", None) or (out.get("status") if isinstance(out, dict) else "DECIDED")
        roots = getattr(out, "roots", None) if not isinstance(out, dict) else out.get("roots")
        bindings = inst.bindings() if callable(getattr(inst, "bindings", None)) else {"a": str(inst.a), "b": str(inst.b), "c": str(inst.c)}
        expr = inst.expr() if callable(getattr(inst, "expr", None)) else "(a)*x**2 + (b)*x + (c)"
        instance = {"instance_id": inst.instance_id, "bindings": bindings}
        if status == "CANNOT_CHECK" or not roots:
            # the oracle declines (NO_EQUATION etc.): the checker must not warrant any root either
            r = m.check(atom(f"{inst.instance_id}:probe", "0", "C", expr=expr), instance)
            if r["status"] != "CANNOT_CHECK" and status == "CANNOT_CHECK":
                disagreements.append((inst.instance_id, "oracle CANNOT_CHECK but checker VALID on x=0"))
            continue
        for k, root in enumerate(roots):
            r = m.check(atom(f"{inst.instance_id}:root{k}", str(root), "C", expr=expr), instance)
            decided += 1
            if r["status"] != "VALID":
                disagreements.append((inst.instance_id, f"oracle root {root} -> checker {r['status']}: {r['witness'].get('reason')}"))
        # A shifted root can be the OTHER valid root. Choose a rational point
        # with independently nonzero exact polynomial residual instead.
        point = Fraction(0)
        while inst.a * point * point + inst.b * point + inst.c == 0:
            point += 1
        wrong = m.check(atom(f"{inst.instance_id}:wrong", str(point), "C", expr=expr), instance)
        if wrong["status"] != "INVALID":
            disagreements.append((inst.instance_id, "known nonroot was not rejected"))
    assert decided > 0
    assert not disagreements, "\n".join(f"{i}: {why}" for i, why in disagreements)


def test_shifted_root_is_not_necessarily_a_wrong_root(m):
    # x^2 - 3x + 2 has both 1 and 1+1 as valid roots.
    assert m.check(atom("other-root", "1+1", "Q"), inst(1, -3, 2))["status"] == "VALID"
    assert m.check(atom("nonroot", "0", "Q"), inst(1, -3, 2))["status"] == "INVALID"
