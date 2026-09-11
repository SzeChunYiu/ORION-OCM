#!/usr/bin/env python3
"""Compute the mdl_response probe honestly for each natural-failure case.

mdl_response = (held-out strictly-better count with the MDL-selected library)
             - (same count with the registered frequency-selected library)

Both libraries are scored by the SAME registered validate_generator on the SAME
validation stream. Training programs are the canonical programs of the train rows (the
solver returns the first-in-enumeration program, which is what canonical_program records).
No evaluator-side facts: the organism can run this by re-mining and re-validating.
"""
from __future__ import annotations
import argparse, json, sys
from fractions import Fraction
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--cases", required=True)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    sys.path.insert(0, str(Path(a.repo) / "src"))
    sys.path.insert(0, str(Path(__file__).parent))
    import ocm.learning.methods as M
    from m2_mdl_selection import mdl_select

    spec = {s["name"]: s for s in json.loads(Path(a.spec).read_text())}
    cases = json.loads(Path(a.cases).read_text())
    budget = M.SearchBudget(slots=200000, max_length=8)
    for c in cases["cases"]:
        s = spec.get(c["name"])
        if not s or not Path(s["ecology"]).exists() or not Path(s["dev"]).exists():
            c["mdl_response"] = None
            print("%-16s unknown (no ecology)" % c["name"], flush=True)
            continue
        eco = json.loads(Path(s["ecology"]).read_text())
        dev = json.loads(Path(s["dev"]).read_text())
        progs = [tuple(r["canonical_program"]) for r in eco["streams"]["train"]]
        mdl = tuple(f for f in mdl_select(progs, cap=16) if 2 <= len(f) <= 8)[:16]
        freq = tuple(tuple(f) for f in dev["fragments"])
        held = []
        for i, r in enumerate(eco["streams"]["validation"]):
            nf = tuple(Fraction(x) for x in r["coefficients"])
            while len(nf) > 1 and nf[-1] == 0:
                nf = nf[:-1]
            held.append(M.PolynomialTask(f"mr:{i}", nf))
        ids = tuple(dev["training_task_ids"])

        def better(lib):
            if not lib:
                return 0
            rep = M.validate_generator(M.GeneratorMethod(lib, ids), held, budget)
            return sum(1 for r in rep["held_out"] if r["candidate"]["slots"] < r["baseline"]["slots"])

        mb, fb = better(mdl), better(freq)
        c["mdl_response"] = mb - fb
        c["mdl_better"], c["freq_better"] = mb, fb
        print("%-16s mdl=%2d freq=%2d response=%+d" % (c["name"], mb, fb, mb - fb), flush=True)
    Path(a.out).write_text(json.dumps(cases, indent=1))
    print("written", a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
