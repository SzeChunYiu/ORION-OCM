# -*- coding: utf-8 -*-
"""AG2 route B -- materially independent oracle.

Route A generates terms by depth-indexed recursion over a Term class and runs a
structural interpreter.  Route B instead:

  * represents terms as flat strings and builds them by CLOSURE ITERATION to a
    fixed point (repeatedly apply every rule to everything already generated
    until the set stops growing), with no depth index and no Term class;
  * decides well-sortedness by a separately written string parser;
  * runs programs from an explicit transition TABLE keyed by opcode, with the
    configuration held as a 4-tuple of ints, written without reference to the
    route-A interpreter.

It imports nothing from signature_free_syntax_v1.py.  Stdlib only.

    python3 -I -B independent_oracle_v1.py
"""

import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))

RULES = [
    ("r0", [], "Reg"),
    ("l0", [], "Label"),
    ("l1", [], "Label"),
    ("halt", [], "Instr"),
    ("read", ["Reg", "Label"], "Instr"),
    ("inc", ["Reg", "Label"], "Instr"),
    ("emit", ["Reg", "Label"], "Instr"),
    ("decjz", ["Reg", "Label", "Label"], "Instr"),
    ("prog", ["Instr", "Instr"], "Prog"),
]
SORTS = ["Reg", "Label", "Instr", "Prog"]


def close_to_fixed_point():
    pool = dict((s, []) for s in SORTS)
    seen = set()
    grew = True
    rounds = 0
    while grew:
        grew = False
        rounds += 1
        for name, args, res in RULES:
            if not args:
                cands = [name]
            else:
                cands = []
                stack = [(0, [])]
                while stack:
                    i, acc = stack.pop()
                    if i == len(args):
                        cands.append("%s(%s)" % (name, ",".join(acc)))
                        continue
                    for t in pool[args[i]]:
                        stack.append((i + 1, acc + [t]))
            for c in cands:
                if c not in seen:
                    seen.add(c)
                    pool[res].append(c)
                    grew = True
    for s in SORTS:
        pool[s].sort()
    return pool, rounds


def split_args(body):
    out, depth, cur = [], 0, ""
    for ch in body:
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
            continue
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        cur += ch
    if cur:
        out.append(cur)
    return out


RULE_BY_NAME = dict((n, (a, r)) for n, a, r in RULES)


def parse_sort(text):
    """Independent well-sortedness decision on the flat string form."""
    if "(" not in text:
        if text not in RULE_BY_NAME:
            return (None, "UNKNOWN_SYMBOL:%s" % text)
        args, res = RULE_BY_NAME[text]
        if args:
            return (None, "ARITY_MISMATCH:%s" % text)
        return (res, "OK")
    if not text.endswith(")"):
        return (None, "MALFORMED")
    name, body = text[:-1].split("(", 1)
    if name not in RULE_BY_NAME:
        return (None, "UNKNOWN_SYMBOL:%s" % name)
    args, res = RULE_BY_NAME[name]
    parts = split_args(body)
    if len(parts) != len(args):
        return (None, "ARITY_MISMATCH:%s:%d!=%d" % (name, len(parts), len(args)))
    for i, p in enumerate(parts):
        s, why = parse_sort(p)
        if s is None:
            return (None, why)
        if s != args[i]:
            return (None, "SORT_MISMATCH:%s:arg%d" % (name, i))
    return (res, "OK")


def opcode_and_targets(instr_text):
    if "(" not in instr_text:
        return (instr_text, [])
    name, body = instr_text[:-1].split("(", 1)
    parts = split_args(body)
    return (name, [p for p in parts if p in ("l0", "l1")])


BUDGET = 8
WORDS = [[], [0], [1], [2]]


def execute(prog_text, word, inc_delta, decjz_swap):
    """Table-driven transition relation over a 4-tuple configuration."""
    body = prog_text[len("prog("):-1]
    i0, i1 = split_args(body)
    table = {"l0": opcode_and_targets(i0), "l1": opcode_and_targets(i1)}
    pc, reg, pos, steps = "l0", 0, 0, 0
    out = []
    while True:
        if steps >= BUDGET:
            return ("STEP_BUDGET_EXHAUSTED", tuple(out), reg, steps)
        op, tgt = table[pc]
        steps += 1
        if op == "halt":
            return ("HALTED", tuple(out), reg, steps)
        if op == "read":
            if pos >= len(word):
                return ("INPUT_UNDERFLOW", tuple(out), reg, steps)
            reg = word[pos]
            pos += 1
            pc = tgt[0]
        elif op == "inc":
            reg += inc_delta
            pc = tgt[0]
        elif op == "emit":
            out.append(reg)
            pc = tgt[0]
        elif op == "decjz":
            nz, zz = (tgt[1], tgt[0]) if decjz_swap else (tgt[0], tgt[1])
            if reg > 0:
                reg -= 1
                pc = nz
            else:
                pc = zz
        else:
            raise AssertionError("unknown opcode %s" % op)


def main():
    pool, rounds = close_to_fixed_point()
    counts = dict((s, len(pool[s])) for s in SORTS)
    progs = pool["Prog"]

    sortcheck_failures = 0
    for s in SORTS:
        for t in pool[s]:
            got, _ = parse_sort(t)
            if got != s:
                sortcheck_failures += 1

    std = dict((p, tuple(execute(p, w, 1, False) for w in WORDS)) for p in progs)
    var = dict((p, tuple(execute(p, w, 2, True) for w in WORDS)) for p in progs)
    divergent = sorted(p for p in progs if std[p] != var[p])

    no_succ = sorted(p for p in progs
                     if opcode_and_targets(split_args(p[len("prog("):-1])[0])[0] == "halt")

    bag = {}
    for p in progs:
        key = tuple(sorted(_symbols(p).items()))
        bag.setdefault(key, []).append(p)
    same_shape_diff = 0
    for key in bag:
        g = sorted(bag[key])
        for i in range(len(g)):
            for j in range(i + 1, len(g)):
                if std[g[i]] != std[g[j]]:
                    same_shape_diff += 1

    classes = {}
    for p in progs:
        classes.setdefault(std[p], []).append(p)
    terminal = {}
    for p in progs:
        for st, _o, _r, _s in std[p]:
            terminal[st] = terminal.get(st, 0) + 1

    oracle = {
        "schema": "AG2_ORACLE_RESULT_V1",
        "route": "CLOSURE_FIXED_POINT_PLUS_TABLE_DRIVEN_TRANSITION",
        "fixed_point_rounds": rounds,
        "free_syntax_term_counts": counts,
        "sortcheck_failures": sortcheck_failures,
        "divergent_program_count": len(divergent),
        "initial_configs_with_no_successor": len(no_succ),
        "identical_symbol_multiset_different_behaviour_pairs": same_shape_diff,
        "syntactic_class_count": len(progs),
        "semantic_class_count": len(classes),
        "semantic_collapse_ratio": str(Fraction(len(progs) - len(classes), len(progs))),
        "terminal_histogram": terminal,
        "executions": len(progs) * len(WORDS),
    }
    with open(os.path.join(HERE, "ORACLE_RESULT_V1.json"), "w") as fh:
        json.dump(oracle, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps(oracle, sort_keys=True))
    return 0


def _symbols(text):
    bag = {}
    buf = ""
    for ch in text:
        if ch.isalnum():
            buf += ch
        else:
            if buf:
                bag[buf] = bag.get(buf, 0) + 1
                buf = ""
    if buf:
        bag[buf] = bag.get(buf, 0) + 1
    return bag


if __name__ == "__main__":
    sys.exit(main())
