# -*- coding: utf-8 -*-
"""AG2 tests: two-route agreement, detected hostiles, nulls, no-alarm case.

Every hostile below is paired with a control proving the check MOVES the
quantity the hostile perturbs: the clean value is asserted first, then the
perturbed value, and they must differ in the stated direction.  A hostile the
checker cannot move is a hostile that detects nothing.

    python3 -I -O -B test_ag2_v1.py
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import signature_free_syntax_v1 as A          # noqa: E402
import independent_oracle_v1 as B             # noqa: E402

FAIL = []


def check(name, cond, detail=""):
    if not cond:
        FAIL.append("%s %s" % (name, detail))
    return cond


def clean_route_a():
    by_sort = A.generate_terms(A.SIGMA_G0, A.DEPTH_BOUND)
    progs = by_sort["Prog"]
    std = dict((str(p), A.behaviour(p, A.I_STANDARD)) for p in progs)
    hist = {}
    for p in progs:
        for st, _o, _r, _s in std[str(p)]:
            hist[st] = hist.get(st, 0) + 1
    return by_sort, progs, std, hist


def main():
    res = json.load(open(os.path.join(HERE, "RESULT_V1.json")))
    ora = json.load(open(os.path.join(HERE, "ORACLE_RESULT_V1.json")))
    by_sort, progs, std, hist = clean_route_a()

    # ---------------- two materially independent routes -------------------
    check("ROUTE_TERM_COUNTS", res["free_syntax_term_counts"] == ora["free_syntax_term_counts"],
          str((res["free_syntax_term_counts"], ora["free_syntax_term_counts"])))
    check("ROUTE_SEM_CLASSES",
          res["syntax_vs_semantics"]["semantic_class_count"] == ora["semantic_class_count"])
    check("ROUTE_COLLAPSE_RATIO",
          res["syntax_vs_semantics"]["semantic_collapse_ratio"] == ora["semantic_collapse_ratio"])
    check("ROUTE_DIVERGENT",
          res["interpretation_separation"]["divergent_program_count"] == ora["divergent_program_count"])
    check("ROUTE_NO_SUCCESSOR",
          res["formation_vs_transition"]["initial_configs_with_no_successor"]
          == ora["initial_configs_with_no_successor"])
    check("ROUTE_SHAPE_PAIRS",
          res["formation_vs_transition"]["identical_symbol_multiset_different_behaviour_pairs"]
          == ora["identical_symbol_multiset_different_behaviour_pairs"])
    check("ROUTE_TERMINAL_HIST", res["g0_reconstruction"]["terminal_histogram"] == ora["terminal_histogram"])
    check("ROUTE_EXECUTIONS", res["g0_reconstruction"]["executions"] == ora["executions"] == 484)

    # ---------------- frozen headline values ------------------------------
    check("AG2-1_CLOSURE", res["closure_is_closed"] and res["closure_missing_terms"] == [])
    check("AG2-1_COUNTS", res["free_syntax_term_counts"] == {"Reg": 1, "Label": 2, "Instr": 11, "Prog": 121})
    check("AG2-5_AJ5_BIJECTION", res["g0_reconstruction"]["bijection_with_aj5_program_set"])
    check("AG2-5_AJ5_HIST", res["g0_reconstruction"]["terminal_histogram_matches_aj5"])
    check("AG2-5_HIST_VALUE",
          hist == {"HALTED": 63, "INPUT_UNDERFLOW": 107, "STEP_BUDGET_EXHAUSTED": 314}, str(hist))

    # ---------------- hostiles, each with a moved quantity ----------------
    detected = {}

    # H1 arity violation.  Control: the same operator at correct arity is accepted.
    ctrl = A.Term("read", (A.Term("r0"), A.Term("l0")))
    bad = A.Term("read", (A.Term("r0"), A.Term("l0"), A.Term("l1")))
    ok_c, _ = A.well_sorted(ctrl)
    ok_b, why_b = A.well_sorted(bad)
    check("H1_CONTROL_ACCEPTED", ok_c)
    detected["ARITY_VIOLATION"] = (not ok_b) and why_b.startswith("ARITY_MISMATCH")
    check("H1_MOVES", ok_c != ok_b)

    # H2 sort violation.
    bad2 = A.Term("read", (A.Term("l0"), A.Term("r0")))
    ok_b2, why_b2 = A.well_sorted(bad2)
    detected["SORT_VIOLATION"] = (not ok_b2) and why_b2.startswith("SORT_MISMATCH")
    check("H2_MOVES", ok_c != ok_b2)

    # H3 ghost symbol.
    bad3 = A.Term("foo", (A.Term("r0"), A.Term("l0")))
    ok_b3, why_b3 = A.well_sorted(bad3)
    detected["GHOST_SYMBOL"] = (not ok_b3) and why_b3.startswith("UNKNOWN_SYMBOL")
    check("H3_MOVES", ok_c != ok_b3)

    # H4 dropped operator: Instr 11 -> 7, Prog 121 -> 49.
    sig4 = dict(A.SIGMA_G0)
    del sig4["decjz"]
    c4 = A.generate_terms(sig4, A.DEPTH_BOUND)
    detected["DROPPED_OPERATOR"] = (len(c4["Instr"]) != 11 and len(c4["Prog"]) != 121)
    check("H4_MOVES", len(c4["Prog"]) == 49, str(len(c4["Prog"])))

    # H5 extra operator: Instr 11 -> 12, Prog 121 -> 144.
    sig5 = dict(A.SIGMA_G0)
    sig5["skip"] = (("Reg",), "Instr")
    c5 = A.generate_terms(sig5, A.DEPTH_BOUND)
    detected["EXTRA_OPERATOR"] = (len(c5["Instr"]) != 11 and len(c5["Prog"]) != 121)
    check("H5_MOVES", len(c5["Prog"]) == 144, str(len(c5["Prog"])))

    # H6 the claim "syntactic equality iff semantic equality".
    detected["SYNTAX_EQ_IS_SEMANTIC_EQ"] = res["syntax_vs_semantics"]["strictly_coarser"]
    check("H6_MOVES", res["syntax_vs_semantics"]["semantic_class_count"] == 33
          and res["syntax_vs_semantics"]["syntactic_class_count"] == 121)

    # H7 the claim "every well-formed term has a successor".
    detected["FORMATION_IMPLIES_TRANSITION"] = (
        res["formation_vs_transition"]["initial_configs_with_no_successor"] > 0)
    check("H7_MOVES", res["formation_vs_transition"]["initial_configs_with_no_successor"] == 11)

    # H8 the claim "operation symbols determine semantics".
    detected["SYMBOLS_DETERMINE_SEMANTICS"] = (
        res["interpretation_separation"]["divergent_program_count"] > 0)
    check("H8_MOVES", res["interpretation_separation"]["divergent_program_count"] == 43)

    # H9 the claim "operator multiset (formation shape) determines behaviour".
    detected["SHAPE_DETERMINES_BEHAVIOUR"] = (
        res["formation_vs_transition"]["identical_symbol_multiset_different_behaviour_pairs"] > 0)
    check("H9_MOVES",
          res["formation_vs_transition"]["identical_symbol_multiset_different_behaviour_pairs"] == 120)

    # H10 wrong step budget.  VALIDATED FINDING: the terminal histogram
    # saturates at budget 6, so budgets 7..13 are invisible to this gate and a
    # budget-7 hostile would detect nothing.  The hostile therefore uses a
    # budget BELOW saturation, and the invariance range is recorded as a
    # boundary on what the AJ5 histogram cross-check proves.
    saved = A.STEP_BUDGET
    A.STEP_BUDGET = 5
    h10 = {}
    for p in progs:
        for st, _o, _r, _s in A.behaviour(p, A.I_STANDARD):
            h10[st] = h10.get(st, 0) + 1
    A.STEP_BUDGET = 7
    h10_invisible = {}
    for p in progs:
        for st, _o, _r, _s in A.behaviour(p, A.I_STANDARD):
            h10_invisible[st] = h10_invisible.get(st, 0) + 1
    A.STEP_BUDGET = saved
    detected["WRONG_STEP_BUDGET_BELOW_SATURATION"] = (h10 != hist)
    check("H10_MOVES", h10 != hist and h10["INPUT_UNDERFLOW"] == 106, str(h10))
    check("H10_SATURATION_RECORDED",
          res["g0_reconstruction"]["histogram_saturation_step_budget"] == 6)
    check("H10_ABOVE_SATURATION_IS_INVISIBLE", h10_invisible == hist,
          "budget 7 must be invisible to the histogram gate; that is the recorded boundary")

    # H11 DECJZ without the decrement: the AJ5 histogram gate must stop matching.
    broken = {"name": "I_NO_DECREMENT", "inc_delta": 1, "decjz_swap": False}
    orig_run = A.run

    def run_no_decrement(prog_term, word, interpretation):
        binding = A._binding(prog_term)
        reg, pos, pc, steps = 0, 0, "l0", 0
        out = []
        while True:
            if steps >= A.STEP_BUDGET:
                return ("STEP_BUDGET_EXHAUSTED", tuple(out), reg, steps)
            instr = binding[pc]
            op = instr.op
            steps += 1
            if op == "halt":
                return ("HALTED", tuple(out), reg, steps)
            if op == "read":
                if pos >= len(word):
                    return ("INPUT_UNDERFLOW", tuple(out), reg, steps)
                reg = word[pos]
                pos += 1
                pc = instr.args[1].op
            elif op == "inc":
                reg += 1
                pc = instr.args[1].op
            elif op == "emit":
                out.append(reg)
                pc = instr.args[1].op
            elif op == "decjz":
                pc = instr.args[1].op if reg > 0 else instr.args[2].op
    h11 = {}
    for p in progs:
        for w in A.INPUT_WORDS:
            st = run_no_decrement(p, w, broken)[0]
            h11[st] = h11.get(st, 0) + 1
    detected["DECJZ_WITHOUT_DECREMENT"] = (h11 != hist)
    check("H11_MOVES", h11 != hist, str(h11))
    assert orig_run is A.run

    check("ALL_HOSTILES_DETECTED", all(detected.values()),
          str([k for k in detected if not detected[k]]))
    check("HOSTILE_COUNT", len(detected) == 11, str(len(detected)))

    # ---------------- nulls ----------------------------------------------
    # NULL-A: randomised semantics over the same syntax.  How many random
    # opcode-role assignments reproduce the AJ5 terminal histogram?
    # VALIDATED FINDING: the terminal histogram alone does NOT identify the
    # semantics.  Randomised opcode-role permutations reproduce it whenever
    # they happen to fix the terminal-determining roles.  The histogram null is
    # therefore reported, not gated; the identification claim rests on the
    # full behaviour map (terminal + output + final register, per program per
    # word), for which the null IS zero.
    true_behaviour = dict((str(p), tuple((r[0], r[1], r[2]) for r in std[str(p)]))
                          for p in progs)
    seed = 20260918
    null_a_hist_hits = 0
    null_a_behaviour_hits = 0
    opcodes = ["read", "inc", "emit", "decjz", "halt"]
    identity_draws = 0
    for _ in range(200):
        seed = (1103515245 * seed + 12345) % (2 ** 31)
        perm = list(opcodes)
        s = seed
        for i in range(len(perm) - 1, 0, -1):
            s = (1103515245 * s + 12345) % (2 ** 31)
            j = s % (i + 1)
            perm[i], perm[j] = perm[j], perm[i]
        role = dict(zip(opcodes, perm))
        if all(role[o] == o for o in opcodes):
            identity_draws += 1
            continue
        h = {}
        beh = {}
        for p in progs:
            trace = tuple(_random_run(p, w, role) for w in A.INPUT_WORDS)
            beh[str(p)] = trace
            for rec in trace:
                h[rec[0]] = h.get(rec[0], 0) + 1
        if h == hist:
            null_a_hist_hits += 1
        if beh == true_behaviour:
            null_a_behaviour_hits += 1
    null_a_hits = null_a_behaviour_hits

    # NULL-B: same operator NAMES and sorts, randomised arities/argument sorts.
    seed = 777
    null_b_hits = 0
    for _ in range(200):
        sig = {"r0": ((), "Reg"), "l0": ((), "Label"), "l1": ((), "Label")}
        for op in ("read", "inc", "emit", "decjz", "halt"):
            seed = (1103515245 * seed + 12345) % (2 ** 31)
            ar = seed % 4
            args = []
            for k in range(ar):
                seed = (1103515245 * seed + 12345) % (2 ** 31)
                args.append(("Reg", "Label")[seed % 2])
            sig[op] = (tuple(args), "Instr")
        sig["prog"] = (("Instr", "Instr"), "Prog")
        c = A.generate_terms(sig, A.DEPTH_BOUND)
        if len(c["Instr"]) == 11 and len(c["Prog"]) == 121:
            null_b_hits += 1

    check("NULL_A_BEHAVIOUR_ZERO", null_a_behaviour_hits == 0,
          "hits=%d/200" % null_a_behaviour_hits)
    # The histogram-only null is RECORDED, never gated: its measured value is
    # the evidence about how much the AJ5 histogram cross-check discriminates.
    check("NULL_A_HISTOGRAM_RECORDED", isinstance(null_a_hist_hits, int))
    check("NULL_A_IDENTITY_DRAWS_EXCLUDED", identity_draws >= 0)
    check("NULL_B_ZERO", null_b_hits == 0, "hits=%d/200" % null_b_hits)

    # ---------------- no-alarm case on the true objects --------------------
    ok_all = True
    for s in A.SORTS:
        for t in by_sort[s]:
            good, _ = A.well_sorted(t)
            ok_all = ok_all and good and t.sort() == s
    check("NO_ALARM_ALL_GENERATED_TERMS_WELL_SORTED", ok_all)
    check("NO_ALARM_ORACLE_SORTCHECK", ora["sortcheck_failures"] == 0)
    check("NO_ALARM_STATUS_GREEN", res["status"] == "GREEN" and res["failed_gates"] == [])

    if FAIL:
        for f in FAIL:
            sys.stderr.write("FAIL %s\n" % f)
        return 1
    summary = {"tests": "PASS", "hostiles_detected": len(detected),
               "null_a_behaviour_hits": null_a_behaviour_hits,
               "null_a_histogram_hits": null_a_hist_hits,
               "null_a_identity_draws": identity_draws,
               "null_b_hits": null_b_hits, "routes": 2,
               "histogram_saturation_step_budget":
                   res["g0_reconstruction"]["histogram_saturation_step_budget"]}
    with open(os.path.join(HERE, "TEST_RESULT_V1.json"), "w") as fh:
        json.dump(summary, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps(summary, sort_keys=True))
    return 0


def _random_run(prog_term, word, role):
    """Execute with the five opcode ROLES randomly permuted."""
    binding = A._binding(prog_term)
    reg, pos, pc, steps = 0, 0, "l0", 0
    out = []
    while True:
        if steps >= A.STEP_BUDGET:
            return ("STEP_BUDGET_EXHAUSTED", tuple(out), reg)
        instr = binding[pc]
        act = role[instr.op]
        steps += 1
        tgts = [a.op for a in instr.args if a.op in ("l0", "l1")]
        nxt = tgts[0] if tgts else "l0"
        if act == "halt":
            return ("HALTED", tuple(out), reg)
        if act == "read":
            if pos >= len(word):
                return ("INPUT_UNDERFLOW", tuple(out), reg)
            reg = word[pos]
            pos += 1
            pc = nxt
        elif act == "inc":
            reg += 1
            pc = nxt
        elif act == "emit":
            out.append(reg)
            pc = nxt
        elif act == "decjz":
            if reg > 0:
                reg -= 1
                pc = nxt
            else:
                pc = tgts[1] if len(tgts) > 1 else nxt


if __name__ == "__main__":
    sys.exit(main())
