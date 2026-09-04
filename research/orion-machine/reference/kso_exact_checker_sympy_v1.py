"""KSO M2b — the SymPy EXACT_CHECKER channel for ROOT_CLAIM atoms.

A ROOT_CLAIM atom asserts that ``root`` is a root of ``expr`` in ``variable`` over ``domain``. The
only way such an atom becomes warranted is this checker: ``simplify(expr.subs(x, root)) == 0`` and
the root lies in the declared domain. The producer's label channel (INSTRUCTION, EXPERIMENTATION,
...) is recorded and ignored for the verdict, so an INSTRUCTION-labelled wrong root stays
unwarranted, and no other channel may set the certificate kind EXACT_CHECKER.

Schema (coordinated with lane-ocm-3, 2026-09-04; their algebra source lives at
``research/orion-machine/domains/algebra/ALGEBRA_SOURCE_V1.json`` and their generator/oracle at
``reference/kso_algebra_quadratic_v1.py``; this module reads neither for the verdict):

  atom     = {"atom_id": str, "kind": "ROOT_CLAIM", "variable": "x", "expr": <SymPy-parsable str>,
              "root": <SymPy-parsable str>, "domain": "C" | "R" | "Q",
              "label_channel": "INSTRUCTION" | "EXACT_CHECKER" | "EXPERIMENTATION",
              "produced_by": <procedure atom id, optional>}
  instance = {"instance_id": str, "bindings": {"a": <rational or symbolic str>, ...},
              "algebra_source": <path, optional, provenance only>}

  check(atom, instance) -> {"status": VALID | INVALID | CANNOT_CHECK, "certificate": "EXACT_CHECKER",
                            "assumption": "SymPy <version> checkeq: simplify(expr.subs(x, root)) == 0",
                            "witness": {"residual", "simplified", "domain_ok", "degenerate", "reason", ...}}

Rules, each with a plant in ``--self-test``:
  VALID          equality holds under simplify AND the root is in the declared domain (R: is_real,
                 Q: is_rational, C: anything); a Δ<0 symbolic root over C is VALID, the same root
                 over R is INVALID.
  INVALID        the residual simplifies to a nonzero number, or the root is provably outside the
                 domain (a Q-domain claim with an irrational root is INVALID).
  CANNOT_CHECK   SymPy cannot decide (``residual.equals(0)`` is None, or is_real / is_rational is
                 None), the statement does not parse, the kind is not ROOT_CLAIM, the expression is
                 degenerate (a = 0 AND b = 0: no equation in x -- while a = 0, b != 0 takes the
                 linear path and decides), a coefficient symbol is neither bound to a value nor
                 introduced by a symbolic binding (the statement was never instantiated), or SymPy
                 is not importable.
                 Never VALID.

Exit codes of the CLI (``--atoms FILE --instance FILE``): 0 every atom decided and VALID; 1 at least
one INVALID; 2 at least one CANNOT_CHECK, or SymPy missing. ``--self-test`` runs the plant table and
exits 2 if any row disagrees. NO NOVELTY OR BREAKTHROUGH CLAIM.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

VALID, INVALID, CANNOT_CHECK = "VALID", "INVALID", "CANNOT_CHECK"
CERTIFICATE = "EXACT_CHECKER"
CHECKABLE_KINDS = ("ROOT_CLAIM",)
DOMAINS = ("C", "R", "Q")
LABEL_CHANNELS = ("INSTRUCTION", "EXACT_CHECKER", "EXPERIMENTATION")
EXIT_VALID, EXIT_INVALID, EXIT_CANNOT_CHECK = 0, 1, 2


def _sympy():
    try:
        import sympy  # noqa: F401
        return sympy
    except Exception:  # pragma: no cover - environment
        return None


def assumption() -> str:
    sp = _sympy()
    ver = sp.__version__ if sp is not None else "unavailable"
    return f"SymPy {ver} checkeq: simplify(expr.subs(x, root)) == 0"


def _result(status: str, atom: dict, **witness) -> dict:
    return {"atom_id": atom.get("atom_id"), "status": status, "certificate": CERTIFICATE,
            "assumption": assumption(), "producer_label_ignored": atom.get("label_channel"),
            "produced_by": atom.get("produced_by"), "witness": witness}


def _parse(sp, text, local: dict):
    """Strict parse: standard transformations only; any failure is the caller's CANNOT_CHECK."""
    from sympy.parsing.sympy_parser import parse_expr, standard_transformations
    if not isinstance(text, str) or not text.strip():
        raise ValueError("empty statement")
    return parse_expr(text, local_dict=local, transformations=standard_transformations, evaluate=True)


def check(atom: dict, instance: dict) -> dict:
    sp = _sympy()
    if sp is None:
        return _result(CANNOT_CHECK, atom, reason="SymPy is not importable; nothing was checked")
    if not isinstance(atom, dict) or atom.get("kind") not in CHECKABLE_KINDS:
        return _result(CANNOT_CHECK, atom if isinstance(atom, dict) else {}, reason=f"kind {atom.get('kind') if isinstance(atom, dict) else '?'} is not checkable here (checkable: {CHECKABLE_KINDS})")
    domain = atom.get("domain")
    if domain not in DOMAINS:
        return _result(CANNOT_CHECK, atom, reason=f"domain {domain!r} not in {DOMAINS}")
    var_name = atom.get("variable") or "x"
    x = sp.Symbol(var_name)
    local = {var_name: x}
    bindings = (instance or {}).get("bindings") or {}
    try:
        bound = {k: _parse(sp, str(v), {}) for k, v in bindings.items()}
    except Exception as exc:  # noqa: BLE001 - any parse failure is could-not-check
        return _result(CANNOT_CHECK, atom, reason=f"a binding does not parse: {exc}")
    local.update({k: sp.Symbol(k) for k in bound})
    try:
        expr = _parse(sp, atom.get("expr"), local)
        root = _parse(sp, atom.get("root"), local)
    except Exception as exc:  # noqa: BLE001
        return _result(CANNOT_CHECK, atom, reason=f"statement does not parse: {exc}")
    subs = {sp.Symbol(k): v for k, v in bound.items()}
    expr_b = expr.subs(subs)
    root_b = root.subs(subs)
    if x in root_b.free_symbols:
        return _result(CANNOT_CHECK, atom, reason="the root mentions the variable itself")
    introduced = set().union(*(v.free_symbols for v in bound.values())) if bound else set()
    unbound = sorted(str(s) for s in (expr_b.free_symbols | root_b.free_symbols) - {x} - introduced)
    if unbound:
        # a symbol neither bound to a value nor introduced by a symbolic binding: the statement was
        # never instantiated on this instance, so there is nothing to decide
        return _result(CANNOT_CHECK, atom, reason=f"unbound symbol(s) {unbound}: the instance does not bind them", unbound_symbols=unbound)
    # degeneracy: a polynomial statement with no dependence on x is not an equation in x
    degenerate = None
    try:
        poly = sp.Poly(expr_b, x)
        deg = poly.degree()
        if deg <= 0:
            return _result(CANNOT_CHECK, atom, degenerate="a=0 and b=0: no equation in x", reason="degenerate statement (degree 0 in the variable)", unbound_symbols=unbound)
        if deg == 1 and atom.get("expected_degree", 2) == 2:
            degenerate = "a=0: linear path"
    except sp.PolynomialError:
        pass  # non-polynomial statements are still checked by substitution
    residual = expr_b.subs(x, root_b)
    simplified = sp.simplify(residual)
    holds = simplified == 0
    if not holds:
        eq = residual.equals(0)
        if eq is True:
            holds = True
        elif eq is None:
            return _result(CANNOT_CHECK, atom, residual=str(residual), simplified=str(simplified), degenerate=degenerate,
                           reason="SymPy cannot decide whether the residual is zero", unbound_symbols=unbound)
    if not holds:
        return _result(INVALID, atom, residual=str(residual), simplified=str(simplified), domain_ok=None, degenerate=degenerate,
                       reason="the residual is nonzero: the claimed root is not a root", unbound_symbols=unbound)
    # domain
    domain_ok: bool | None = True
    if domain == "R":
        domain_ok = root_b.is_real
    elif domain == "Q":
        domain_ok = root_b.is_rational
    if domain_ok is None:
        return _result(CANNOT_CHECK, atom, residual=str(residual), simplified="0", domain_ok=None, degenerate=degenerate,
                       reason=f"equality holds but SymPy cannot decide membership of {root_b} in {domain}", unbound_symbols=unbound)
    if domain_ok is False:
        return _result(INVALID, atom, residual=str(residual), simplified="0", domain_ok=False, degenerate=degenerate,
                       reason=f"equality holds but the root {root_b} is not in the declared domain {domain}", unbound_symbols=unbound)
    return _result(VALID, atom, residual=str(residual), simplified="0", domain_ok=True, degenerate=degenerate,
                   root_evaluated=str(root_b), unbound_symbols=unbound)


def is_warranted(result: dict) -> bool:
    """The only warrant this channel grants: VALID under the EXACT_CHECKER certificate."""
    return result.get("status") == VALID and result.get("certificate") == CERTIFICATE


def warrant_label(result: dict, verdict_index: int, procedure_profile=None):
    """ATMS profile for a warranted claim: {{verdict}} ⊗ (procedure label if produced_by).
    Unwarranted results carry no label (empty profile) whatever the producer said."""
    if not is_warranted(result):
        return ()
    mine = (frozenset({verdict_index}),)
    if procedure_profile:
        return tuple(frozenset(a | b) for a in mine for b in procedure_profile)
    return mine


# ----------------------------------------------------------------------------------------------
# self-test plants
# ----------------------------------------------------------------------------------------------


def _atom(aid, expr, root, domain="C", label="EXACT_CHECKER", kind="ROOT_CLAIM", **extra):
    d = {"atom_id": aid, "kind": kind, "variable": "x", "expr": expr, "root": root, "domain": domain, "label_channel": label}
    d.update(extra)
    return d


def plant_table() -> list[tuple[str, dict, dict, str]]:
    """(name, atom, instance, expected status)."""
    q = {"instance_id": "q", "bindings": {"a": "1", "b": "-3", "c": "2"}}          # x^2 - 3x + 2 = (x-1)(x-2)
    neg = {"instance_id": "neg", "bindings": {"a": "1", "b": "0", "c": "1"}}        # x^2 + 1: Δ < 0
    irr = {"instance_id": "irr", "bindings": {"a": "1", "b": "0", "c": "-2"}}       # x^2 - 2
    lin = {"instance_id": "lin", "bindings": {"a": "0", "b": "2", "c": "-4"}}       # 2x - 4
    dead = {"instance_id": "dead", "bindings": {"a": "0", "b": "0", "c": "5"}}      # 5 = 0: no equation
    sym = {"instance_id": "sym", "bindings": {"a": "1", "b": "p", "c": "q"}}        # symbolic coefficients
    e = "a*x**2 + b*x + c"
    formula_plus = "(-b + sqrt(b**2 - 4*a*c))/(2*a)"
    return [
        ("correct rational root over Q", _atom("t1", e, "2", "Q"), q, VALID),
        ("wrong root (INSTRUCTION-labelled) stays INVALID", _atom("t2", e, "3", "C", label="INSTRUCTION"), q, INVALID),
        ("quadratic-formula root, symbolic, over C", _atom("t3", e, formula_plus, "C"), q, VALID),
        ("Δ<0: symbolic root I over C is VALID", _atom("t4", e, formula_plus, "C"), neg, VALID),
        ("Δ<0: the same root over R is INVALID", _atom("t5", e, formula_plus, "R"), neg, INVALID),
        ("irrational root sqrt(2) over R is VALID", _atom("t6", e, "sqrt(2)", "R"), irr, VALID),
        ("irrational root sqrt(2) over Q is INVALID", _atom("t7", e, "sqrt(2)", "Q"), irr, INVALID),
        ("a=0: linear path decides VALID", _atom("t8", e, "2", "Q"), lin, VALID),
        ("a=0: linear path decides INVALID", _atom("t9", e, "3", "Q"), lin, INVALID),
        ("a=0 and b=0: CANNOT_CHECK by rule", _atom("t10", e, "0", "C"), dead, CANNOT_CHECK),
        ("unparsable statement: CANNOT_CHECK never VALID", _atom("t11", "a*x**2 + b*x +", "2", "C"), q, CANNOT_CHECK),
        ("unparsable root: CANNOT_CHECK", _atom("t12", e, "sqrt(", "C"), q, CANNOT_CHECK),
        ("missing binding: CANNOT_CHECK", _atom("t13", e, "2", "C"), {"instance_id": "m", "bindings": {"a": "1"}}, CANNOT_CHECK),
        ("non-checkable kind: CANNOT_CHECK", _atom("t14", e, "2", "C", kind="worked_example"), q, CANNOT_CHECK),
        ("unknown domain: CANNOT_CHECK", _atom("t15", e, "2", "Z"), q, CANNOT_CHECK),
        ("symbolic coefficients, formula root, over C: VALID", _atom("t16", e, formula_plus, "C"), sym, VALID),
        ("symbolic coefficients, wrong root: INVALID", _atom("t17", e, "-p", "C"), sym, INVALID),
        ("symbolic coefficients over R: membership undecidable -> CANNOT_CHECK", _atom("t18", e, formula_plus, "R"), sym, CANNOT_CHECK),
        ("root mentioning x: CANNOT_CHECK", _atom("t19", e, "x", "C"), q, CANNOT_CHECK),
        ("produced_by carried through", _atom("t20", e, "1", "Q", produced_by="proc:factoring"), q, VALID),
    ]


def self_test() -> int:
    sp = _sympy()
    print(f"kso_exact_checker_sympy self-test (python {sys.version.split()[0]}; {assumption()})")
    if sp is None:
        print("  CANNOT CHECK: SymPy is not importable; the plant table cannot run")
        return EXIT_CANNOT_CHECK
    bad = 0
    for name, atom, inst, want in plant_table():
        got = check(atom, inst)
        ok = got["status"] == want
        bad += not ok
        print(f"  {'ok ' if ok else 'BAD'} {name}: {got['status']} (expected {want}){'' if ok else ' -- ' + str(got['witness'])}")
    # channel exclusivity: an INSTRUCTION-labelled claim never becomes warranted by its label
    wrong = check(_atom("w", "a*x**2 + b*x + c", "3", "C", label="INSTRUCTION"), {"bindings": {"a": "1", "b": "-3", "c": "2"}})
    excl = not is_warranted(wrong) and warrant_label(wrong, 0) == () and wrong["producer_label_ignored"] == "INSTRUCTION"
    right = check(_atom("r", "a*x**2 + b*x + c", "1", "C", label="INSTRUCTION", produced_by="proc:factoring"), {"bindings": {"a": "1", "b": "-3", "c": "2"}})
    lbl = warrant_label(right, 7, (frozenset({3}),)) == (frozenset({3, 7}),)
    for name, ok in (("only this checker warrants (INSTRUCTION label ignored)", excl), ("warrant label = {{verdict}} ⊗ procedure label", lbl)):
        bad += not ok
        print(f"  {'ok ' if ok else 'BAD'} {name}")
    if bad:
        print(f"SELF-TEST FAILED: {bad} row(s)")
        return EXIT_CANNOT_CHECK
    print("self-test passed: every rule can fail on its plant; CANNOT_CHECK is never VALID")
    return EXIT_VALID


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--atoms", type=Path, help="JSON list of ROOT_CLAIM atoms (or an object with an 'atoms' list)")
    ap.add_argument("--instance", type=Path, help="JSON instance with 'bindings'")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.atoms or not a.instance:
        print("COULD NOT CHECK: --atoms and --instance are required (or --self-test)", file=sys.stderr)
        return EXIT_CANNOT_CHECK
    try:
        atoms = json.loads(a.atoms.read_text())
        inst = json.loads(a.instance.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"COULD NOT CHECK: input unreadable ({exc})", file=sys.stderr)
        return EXIT_CANNOT_CHECK
    if isinstance(atoms, dict):
        atoms = atoms.get("atoms", [])
    if not isinstance(atoms, list) or not atoms:
        print("COULD NOT CHECK: no atoms to check (an empty list is not a pass)", file=sys.stderr)
        return EXIT_CANNOT_CHECK
    results = [check(at, inst) for at in atoms]
    counts = {s: sum(1 for r in results if r["status"] == s) for s in (VALID, INVALID, CANNOT_CHECK)}
    print(f"kso_exact_checker_sympy: python {sys.version.split()[0]}; {assumption()}")
    if a.json:
        print(json.dumps({"instance_id": inst.get("instance_id"), "counts": counts, "results": results}, indent=1))
    else:
        for r in results:
            print(f"  [{r['status']}] {r['atom_id']} -- {r['witness'].get('reason', 'root ' + str(r['witness'].get('root_evaluated', '')))}")
        print(f"  {counts}")
    if counts[CANNOT_CHECK] or _sympy() is None:
        print("COULD NOT CHECK: at least one atom undecided", file=sys.stderr)
        return EXIT_CANNOT_CHECK
    return EXIT_INVALID if counts[INVALID] else EXIT_VALID


if __name__ == "__main__":
    sys.exit(main())
