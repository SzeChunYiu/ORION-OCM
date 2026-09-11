#!/usr/bin/env python3
"""Extended-grammar analogue of the registered solver, for testing d>=2 generalisation.

M2_SUBSTRATE_REQ established that d>=2 arrangement generalisation is infeasible in the
registered grammar (P=4) by a window of -1.87 motifs, and feasible from P=5. The
registered grammar cannot be changed -- src/ocm/learning/methods.py is bound AS-IS -- so
the mechanism is tested in a LARGER grammar to separate two hypotheses:

    H_substrate  the mechanism generalises to novel arrangements, and P=4 is what blocks
                 the TEST
    H_mechanism  the mechanism only interpolates, and would fail at d>=2 anywhere

This module re-implements methods.solve's semantics parameterised by the primitive set:
same ascending-length enumeration, same guided/baseline interleave on slot parity, same
duplicate skip, same counterexample pruning, same slot accounting, same success condition.

CONTROL (the thing that makes this usable): with the registered primitives it must
reproduce M.solve EXACTLY -- identical status, slots, candidates_checked and program on
every probe task. A single mismatch invalidates every extended-grammar result, so the
control runs first and hard-fails.

This is a RESEARCH ANALOGUE, never presented as an OCM result. Any finding here is a
statement about the mechanism's behaviour in a larger substrate, explicitly outside the
registered grammar.
"""
from __future__ import annotations
import argparse, json, random, sys
from fractions import Fraction
from itertools import product
from pathlib import Path

# polynomial-safe unary ops: each maps a coefficient vector to a coefficient vector
OPS = {
    "inc":    lambda c: [c[0] + 1] + list(c[1:]),
    "dec":    lambda c: [c[0] - 1] + list(c[1:]),
    "double": lambda c: [2 * x for x in c],
    "square": None,        # handled specially (polynomial multiply)
    "triple": lambda c: [3 * x for x in c],
    "neg":    lambda c: [-x for x in c],
}


def normal_form(program, ops):
    c = [Fraction(0), Fraction(1)]
    for op in program:
        if op == "square":
            sq = [Fraction(0)] * (2 * len(c) - 1)
            for i, x in enumerate(c):
                for j, y in enumerate(c):
                    sq[i + j] += x * y
            c = sq
        else:
            c = [Fraction(v) for v in OPS[op](c)]
    return tuple(c)


def evaluate(coeffs, x):
    v = Fraction(0)
    for a in reversed(coeffs):
        v = v * x + a
    return v


def primitive_programs(prims, max_length):
    for L in range(max_length + 1):
        yield from product(prims, repeat=L)


def guided_programs(fragments, prims, max_length):
    tokens = tuple(fragments) + tuple((p,) for p in prims)
    for L in range(1, max_length + 1):
        for word in product(tokens, repeat=L):
            yield tuple(op for tok in word for op in tok)


def solve(target, prims, max_length=8, slots=200000, fragments=()):
    """Mirrors methods.solve exactly, parameterised by the primitive set."""
    baseline = iter(primitive_programs(prims, max_length))
    guided = iter(guided_programs(fragments, prims, max_length)) if fragments else None
    seen, counterexamples = set(), [0]
    checked = slot = 0
    for slot in range(1, slots + 1):
        stream = guided if guided is not None and slot % 2 == 1 else baseline
        try:
            program = next(stream)
        except StopIteration:
            if stream is baseline:
                return {"status": "EXHAUSTED", "program": None, "slots": slot - 1,
                        "checked": checked}
            guided = None
            continue
        if len(program) > max_length or program in seen:
            continue
        seen.add(program)
        checked += 1
        if any(evaluate(normal_form(program, prims), x) != evaluate(target, x)
               for x in counterexamples):
            continue
        nf = normal_form(program, prims)
        if nf == target:
            return {"status": "VERIFIED", "program": program, "slots": slot,
                    "checked": checked}
        for x in range(max(len(nf), len(target))):
            if evaluate(nf, x) != evaluate(target, x):
                counterexamples.append(x)
                break
    return {"status": "BUDGET_EXHAUSTED", "program": None, "slots": slot, "checked": checked}


def control(repo, n=60, seed=7):
    """Must reproduce M.solve exactly on the registered grammar, or everything is void."""
    sys.path.insert(0, str(Path(repo) / "src"))
    import ocm.learning.methods as M
    prims = tuple(M.PRIMITIVES)
    rng = random.Random(seed)
    targets, mismatches = [], []
    allp = list(primitive_programs(prims, 6))
    rng.shuffle(allp)
    for prog in allp[:n]:
        nf = normal_form(prog, prims)
        while len(nf) > 1 and nf[-1] == 0:
            nf = nf[:-1]
        targets.append(nf)
    for nf in targets:
        mine = solve(nf, prims, max_length=8, slots=200000)
        task = M.PolynomialTask("ctl", nf)
        theirs = M.solve(task, M.SearchBudget(slots=200000, max_length=8))
        same = (mine["slots"] == theirs.slots
                and mine["checked"] == theirs.candidates_checked
                and (mine["program"] or ()) == (theirs.program or ()))
        if not same:
            mismatches.append({"target": [str(x) for x in nf],
                               "mine": {k: (list(v) if isinstance(v, tuple) else v)
                                        for k, v in mine.items()},
                               "registered": {"slots": theirs.slots,
                                              "checked": theirs.candidates_checked,
                                              "program": list(theirs.program or ())}})
    return {"probes": len(targets), "mismatches": len(mismatches),
            "detail": mismatches[:3],
            "verdict": "EXACT_MATCH" if not mismatches else "MISMATCH_ANALOGUE_INVALID"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--probes", type=int, default=60)
    a = ap.parse_args()
    ctl = control(a.repo, n=a.probes)
    out = {"schema": "OCM_M2_EXTGRAMMAR_CONTROL_V1",
           "lane": "LANE_M2_TRAVERSAL_CAPITAL_OPUS",
           "purpose": ("faithful re-implementation of methods.solve parameterised by the "
                       "primitive set, so d>=2 generalisation can be tested in a substrate "
                       "that permits it (P>=5). Research analogue, never an OCM result."),
           "control": ctl,
           "registered_primitives": ["inc", "dec", "double", "square"],
           "extended_primitives_available": sorted(OPS)}
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps(ctl, indent=1)[:900])
    return 0 if ctl["verdict"] == "EXACT_MATCH" else 1


if __name__ == "__main__":
    raise SystemExit(main())
