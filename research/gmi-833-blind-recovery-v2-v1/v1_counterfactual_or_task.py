"""Motivation receipt: v1 mechanics on the OR-task counterfactual.

Reproduces the science-audit finding on PR #932: the merged AJ9b K01 pipeline
recovered the K01 fingerprint for the XOR task, but the XOR CHOICE is the
family information. Running the same v1 basis/mechanics on the OR task
(required_outputs [0,1,1,1]) yields a minimal single-threshold-site solution
that FAILS the actual v1 adjudicator's own checks — the v1 adjudicator is the
REAL one, imported unmodified from the merged package (no copy drift). Only
the v1 search is re-implemented, faithfully parameterized by the required
output vector (v1's blind_search_v1.py hardcodes XOR).
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
V1 = HERE.parent / "gmi-833-aj9b-k01-blind-recovery-v1"

CASES = ((0, 0), (0, 1), (1, 0), (1, 1))
OR_REQUIRED = (0, 1, 1, 1)   # the auditor's counterfactual task
XOR_REQUIRED = (0, 1, 1, 0)  # v1's actual task, for the contrast column
MAX_OPS = 7


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- faithful parameterization of v1's size_layered_search ------------------
def v1_search(required):
    ATOMS = (("x", 0), ("x", 1), ("c", -1), ("c", 0), ("c", 1))

    def eval_ast(e):
        op = e[0]
        if op == "x":
            return tuple(row[e[1]] for row in CASES)
        if op == "c":
            return (e[1],) * len(CASES)
        if op == "add":
            a, b = eval_ast(e[1]), eval_ast(e[2])
            return tuple(x + y for x, y in zip(a, b))
        if op == "neg":
            a = eval_ast(e[1])
            return tuple(-x for x in a)
        if op == "pos":
            a = eval_ast(e[1])
            return tuple(1 if x > 0 else 0 for x in a)
        raise ValueError(op)

    def valid_values(v):
        return all(-3 <= x <= 3 for x in v)

    by = [{} for _ in range(MAX_OPS + 1)]
    for e in ATOMS:
        by[0].setdefault(eval_ast(e), e)
    seen = set(by[0])
    for size in range(1, MAX_OPS + 1):
        cand = {}
        for e in by[size - 1].values():
            for ne in (("neg", e), ("pos", e)):
                v = eval_ast(ne)
                if valid_values(v):
                    old = cand.get(v)
                    if old is None or repr(ne) < repr(old):
                        cand[v] = ne
        for left_size in range(size):
            right_size = size - 1 - left_size
            for a in by[left_size].values():
                for b in by[right_size].values():
                    if repr(a) > repr(b):
                        continue
                    ne = ("add", a, b)
                    v = eval_ast(ne)
                    if valid_values(v):
                        old = cand.get(v)
                        if old is None or repr(ne) < repr(old):
                            cand[v] = ne
        cand = {v: e for v, e in cand.items() if v not in seen}
        by[size] = cand
        seen |= set(cand)
        if required in cand:
            return {"first_exact_cost": size, "expression": cand[required]}
    return None


def main():
    post = load_module("v1_posthoc", V1 / "posthoc_adjudicate_v1.py")
    rows = {}
    for label, req in (("OR_COUNTERFACTUAL", OR_REQUIRED), ("XOR_V1_ACTUAL", XOR_REQUIRED)):
        hit = v1_search(req)
        insp = post.inspect_candidate(post.tup(hit["expression"]), list(req))
        rows[label] = {
            "task_required_outputs": list(req),
            "first_exact_cost": hit["first_exact_cost"],
            "minimal_expression": json.loads(json.dumps(hit["expression"])),
            "v1_adjudicator_checks": insp["checks"],
            "v1_adjudicator_pass": insp["pass"],
            "v1_terminal_would_be":
                "RECOVERED" if insp["pass"] else "NOT_RECOVERED_AT_SCOPE",
        }
    receipt = {
        "schema": "V2_MOTIVATION_RECEIPT_V1",
        "claim": "Under v1 mechanics, changing only the task from XOR to OR "
                 "flips the v1 adjudicator verdict from RECOVERED to "
                 "NOT_RECOVERED: the v1 recovery rode on the XOR task choice "
                 "(open task-authorship channel), not on a family-blind "
                 "protocol.",
        "v1_adjudicator_source":
            "gmi-833-aj9b-k01-blind-recovery-v1/posthoc_adjudicate_v1.py "
            "(imported unmodified)",
        "v1_search_basis": "{atoms x0,x1, consts -1/0/1; unary NEG, POS; "
                           "binary ADD; guard [-3,3]; max 7 ops} — v1's frozen "
                           "SEARCH_CONFIG_V1.json, unchanged",
        "rows": rows,
    }
    (HERE / "MOTIVATION_RECEIPT_V1.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: {"cost": v["first_exact_cost"],
                          "checks": v["v1_adjudicator_checks"],
                          "terminal": v["v1_terminal_would_be"]}
                      for k, v in rows.items()}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
