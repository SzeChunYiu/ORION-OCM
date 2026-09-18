"""Route B for gmi-833-h-real-scale-revival-v1: a source-separated oracle.

This file imports NOTHING from grammar_s_v1, run_real_scale_revival_v1 or
real_scale_revival_v1. It re-implements, from FREEZE_V1.md alone, the parts of
the derivation whose result is claimed: expression semantics, the structural
classifier, the charged cost model, the exact replay of every committed
partial, and an independent re-ranking of the committed survivors on the
committed search sample with its own fitting routine.

Non-import is enforced structurally by test_real_scale_revival_v1.py via an
`ast` scan of this file and a `sys.modules` assertion, not by this comment.

    python3 -I -B  independent_oracle_v1.py
"""
from fractions import Fraction as F
import itertools
import json
import os
import sys

WHERE = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS = os.path.join(WHERE, "REAL_RUNS")

KEYS = ("R02", "R03", "R04")
EXPECT_SIGMA = {"R02": "SIGMA_R02", "R03": "SIGMA_R03", "R04": "SIGMA_R04"}
GRID = (F(-2), F(-1), F(-1, 2), F(0), F(1, 2), F(1), F(2))
LINE = (F(-2), F(-1), F(0), F(1), F(2))


def fetch(fname):
    full = os.path.join(ARTIFACTS, fname)
    if not os.path.isfile(full):
        raise SystemExit("MISSING REAL_RUN ARTIFACT: " + full)
    with open(full) as handle:
        return json.load(handle)


# ------------------------------------------------- expression semantics -----

def read_expr(text, at=0):
    stop = at
    while stop < len(text) and (text[stop].isalnum() or text[stop] == "_"):
        stop += 1
    tag = text[at:stop]
    if stop < len(text) and text[stop] == "(":
        kids = []
        cursor = stop + 1
        while True:
            kid, cursor = read_expr(text, cursor)
            kids.append(kid)
            if text[cursor] == ",":
                cursor += 1
                continue
            cursor += 1
            break
        return (tag, tuple(kids)), cursor
    return (tag, None), stop


def parse(text):
    tree, _ = read_expr(text, 0)
    return tree


def count_nodes(tree):
    tag, kids = tree
    if kids is None:
        return 1
    return 1 + sum(count_nodes(k) for k in kids)


CONSTANTS = {"C0": F(0), "C1": F(1)}


def evaluate(tree, binding):
    tag, kids = tree
    if kids is None:
        if tag in CONSTANTS:
            return CONSTANTS[tag]
        return binding[tag]
    if tag == "NEG":
        return F(0) - evaluate(kids[0], binding)
    if tag == "ABS":
        got = evaluate(kids[0], binding)
        return got if got >= 0 else F(0) - got
    if tag == "STEP":
        return F(1) if evaluate(kids[0], binding) > 0 else F(0)
    if tag == "RECIP":
        got = evaluate(kids[0], binding)
        return F(0) if got == 0 else F(1) / got
    if tag == "ADD":
        return evaluate(kids[0], binding) + evaluate(kids[1], binding)
    if tag == "MUL":
        return evaluate(kids[0], binding) * evaluate(kids[1], binding)
    raise ValueError("operation outside the frozen grammar: " + tag)


def float_eval(tree, binding):
    tag, kids = tree
    if kids is None:
        if tag == "C0":
            return 0.0
        if tag == "C1":
            return 1.0
        return binding[tag]
    if tag == "NEG":
        return -float_eval(kids[0], binding)
    if tag == "ABS":
        return abs(float_eval(kids[0], binding))
    if tag == "STEP":
        return 1.0 if float_eval(kids[0], binding) > 0.0 else 0.0
    if tag == "RECIP":
        got = float_eval(kids[0], binding)
        return 0.0 if got == 0.0 else 1.0 / got
    if tag == "ADD":
        return float_eval(kids[0], binding) + float_eval(kids[1], binding)
    if tag == "MUL":
        return float_eval(kids[0], binding) * float_eval(kids[1], binding)
    raise ValueError(tag)


def varies_with(tree, moving, fixed):
    for assignment in itertools.product(GRID, repeat=len(fixed)):
        binding = dict(zip(fixed, assignment))
        got = set()
        for value in GRID:
            binding[moving] = value
            got.add(evaluate(tree, binding))
        if len(got) > 1:
            return True
    return False


def straight_in(tree, moving, every):
    fixed = [name for name in every if name != moving]
    for assignment in itertools.product(GRID, repeat=len(fixed)):
        binding = dict(zip(fixed, assignment))
        seq = []
        for value in LINE:
            binding[moving] = value
            seq.append(evaluate(tree, binding))
        for k in range(len(seq) - 2):
            if seq[k] - seq[k + 1] - seq[k + 1] + seq[k + 2] != 0:
                return False
    return True


def structural_class(body_text, head_text):
    """The priority of FREEZE_V1.md section 5, re-implemented independently."""
    body = parse(body_text)
    head = parse(head_text)
    if varies_with(head, "STATE", ["S", "BIAS"]):
        return "PERSISTENT_STATE"
    if not straight_in(body, "ARG", ["ARG", "PARAM"]):
        return "LIFTED_BASIS"
    if not straight_in(head, "S", ["S", "BIAS", "STATE"]):
        return "NONLINEAR_LINK"
    return "AFFINE_SCORE"


# ------------------------------------------------------------ cost model ----

def charged_program(body_text, head_text, m, stateful):
    b = count_nodes(parse(body_text))
    h = count_nodes(parse(head_text))
    return m * b + m + h + m + 1 + (1 if stateful else 0)


def charged_table(m):
    return m + 2 ** m


def charged_landmark(q, d):
    return q * (2 * d + 1) + q + q * d + q


# --------------------------------------------------------- exact replay -----

def replay(rec):
    body = parse(rec["chosen"]["body"])
    head = parse(rec["chosen"]["head"])
    stateful = bool(rec["chosen"]["attributes"]["reads_state"])
    params = [F(v) for v in rec["chosen"]["params"]]
    bias = F(rec["chosen"]["bias"])
    xden = rec["xden"]
    yden = rec["yden"]
    block = rec["replay"]
    total = F(0)
    wrong = 0
    carried = F(0)
    for raw, yraw in zip(block["X"], block["y"]):
        fold = F(0)
        for j, cell in enumerate(raw):
            fold = fold + evaluate(body, {"ARG": F(int(cell), xden[j]),
                                          "PARAM": params[j]})
        got = evaluate(head, {"S": fold, "BIAS": bias, "STATE": carried})
        if stateful:
            carried = got
        want = F(int(yraw), yden)
        gap = got - want
        total = total + gap * gap
        if (1 if got > 0 else 0) != (1 if want > 0 else 0):
            wrong += 1
    return total, wrong


# ------------------------------------------- independent survivor ranking ----

def sample_design(block):
    xden = block["xden"]
    rows = [[float(cell) / float(xden[j]) for j, cell in enumerate(raw)]
            for raw in block["X"]]
    ys = [float(v) / float(block["yden"]) for v in block["y"]]
    return rows, ys


def fold_values(body, rows, params):
    out = []
    for raw in rows:
        acc = 0.0
        for j, cell in enumerate(raw):
            acc += float_eval(body, {"ARG": cell, "PARAM": params[j]})
        out.append(acc)
    return out


def head_values(head, folds, bias, stateful):
    out = []
    carried = 0.0
    for fold in folds:
        got = float_eval(head, {"S": fold, "BIAS": bias, "STATE": carried})
        if stateful:
            carried = got
        out.append(got)
    return out


def squared(pred, ys):
    total = 0.0
    for a, b in zip(pred, ys):
        total += (a - b) * (a - b)
    return total


def solve_normal(A, rhs):
    """Gaussian elimination with partial pivoting, written here, not imported."""
    n = len(rhs)
    M = [row[:] + [rhs[i]] for i, row in enumerate(A)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[piv][col]) < 1e-14:
            return None
        M[col], M[piv] = M[piv], M[col]
        inv = 1.0 / M[col][col]
        for r in range(n):
            if r == col:
                continue
            factor = M[r][col] * inv
            if factor == 0.0:
                continue
            for c in range(col, n + 1):
                M[r][c] -= factor * M[col][c]
    return [M[i][n] / M[i][i] for i in range(n)]


def fit_candidate(body_text, head_text, stateful, rows, ys, d):
    body = parse(body_text)
    head = parse(head_text)

    def predict(params, bias):
        return head_values(head, fold_values(body, rows, params), bias, stateful)

    zero = [0.0] * d
    base = predict(zero, 0.0)
    cols = []
    for j in range(d):
        p = [0.0] * d
        p[j] = 1.0
        cols.append([a - b for a, b in zip(predict(p, 0.0), base)])
    cols.append([a - b for a, b in zip(predict(zero, 1.0), base)])
    probe = [1.0 if (j % 3) == 0 else -1.0 for j in range(d + 1)]
    got = predict(probe[:d], probe[d])
    want = [base[i] + sum(cols[j][i] * probe[j] for j in range(d + 1))
            for i in range(len(rows))]
    jointly_affine = all(abs(a - b) <= 1e-7 * (1.0 + abs(a))
                         for a, b in zip(got, want))
    if jointly_affine:
        A = [[sum(cols[a][i] * cols[b][i] for i in range(len(rows)))
              + (1e-8 if a == b else 0.0) for b in range(d + 1)]
             for a in range(d + 1)]
        rhs = [sum(cols[a][i] * (ys[i] - base[i]) for i in range(len(rows)))
               for a in range(d + 1)]
        sol = solve_normal(A, rhs)
        if sol is None:
            return None
        return squared(predict(sol[:d], sol[d]), ys)
    params = [0.0] * d
    bias = 0.0
    best = squared(predict(params, bias), ys)
    step = 1.0
    for _ in range(2):
        for j in range(d + 1):
            cur = params[j] if j < d else bias
            for k in (-4, -2, -1, 1, 2, 4):
                trial = cur + k * step
                if j < d:
                    params[j] = trial
                else:
                    bias = trial
                got = squared(predict(params, bias), ys)
                if got < best - 1e-15:
                    best = got
                    cur = trial
                else:
                    if j < d:
                        params[j] = cur
                    else:
                        bias = cur
            if j < d:
                params[j] = cur
            else:
                bias = cur
        step *= 0.5
    return best


def rerank(rec):
    block = rec["search_sample"]
    rows, ys = sample_design(block)
    d = block["d"]
    table = []
    for entry in block["survivors"]:
        stateful = varies_with(parse(entry["head"]), "STATE", ["S", "BIAS"])
        got = fit_candidate(entry["body"], entry["head"], stateful, rows, ys, d)
        if got is None:
            continue
        table.append((got, count_nodes(parse(entry["body"]))
                      + count_nodes(parse(entry["head"])),
                      entry["body"], entry["head"]))
    table.sort()
    return table


# ------------------------------------------------------------------ main ----

def main():
    scopes = {}
    for key in KEYS:
        rec = fetch("scope_%s.json" % key)
        got_sse, got_errors = replay(rec)
        sse_ok = (got_sse == F(rec["replay"]["partial_sse"]))
        err_ok = True
        if "partial_decision_errors" in rec["replay"]:
            err_ok = (got_errors == rec["replay"]["partial_decision_errors"])
        klass = structural_class(rec["chosen"]["body"], rec["chosen"]["head"])
        class_ok = (klass == rec["chosen"]["class"])
        table = rerank(rec)
        top_ok = bool(table and table[0][2] == rec["chosen"]["body"]
                      and table[0][3] == rec["chosen"]["head"])
        stateful = bool(rec["chosen"]["attributes"]["reads_state"])
        m_star = rec["crossover"]["m_star"]
        cross_ok = True
        if m_star is not None:
            here = charged_program(rec["chosen"]["body"], rec["chosen"]["head"],
                                   m_star, stateful)
            before = charged_program(rec["chosen"]["body"], rec["chosen"]["head"],
                                     m_star - 1, stateful) if m_star > 1 else None
            cross_ok = (charged_table(m_star) > here
                        and (before is None or charged_table(m_star - 1) <= before))
        sigma_ok = (rec["sigma"] == EXPECT_SIGMA[key])
        scale_ok = (rec["n_fit"] >= 100000 and rec["n_held"] >= 20000)
        scopes[key] = {
            "exact_replay_sse_matches": bool(sse_ok),
            "exact_replay_decisions_match": bool(err_ok),
            "recomputed_partial_sse": str(got_sse),
            "recomputed_partial_decision_errors": got_errors,
            "class_rederived": klass,
            "class_matches": bool(class_ok),
            "independent_top1": (list(table[0][2:]) if table else None),
            "independent_top1_matches": top_ok,
            "survivors_reranked": len(table),
            "crossover_arithmetic_ok": bool(cross_ok),
            "sigma_matches": bool(sigma_ok),
            "real_scale_thresholds_met": bool(scale_ok),
            "agrees": bool(sse_ok and err_ok and class_ok and top_ok
                           and cross_ok and sigma_ok and scale_ok)}
        print("[%s] replay=%s class=%s top1=%s agrees=%s"
              % (key, sse_ok, klass, top_ok, scopes[key]["agrees"]))

    extra = {}
    rec3 = fetch("scope_R03.json")
    rp = rec3["arms"]["replay"]
    win_log = win_id = tied = neg_log = neg_id = 0
    for a, b, y in zip(rp["mu_log"], rp["mu_identity"], rp["y"]):
        qa, qb, qy = F(a), F(b), F(int(y))
        da = qa - qy
        db = qb - qy
        da = da if da >= 0 else F(0) - da
        db = db if db >= 0 else F(0) - db
        if da < db:
            win_log += 1
        elif db < da:
            win_id += 1
        else:
            tied += 1
        if qa < 0:
            neg_log += 1
        if qb < 0:
            neg_id += 1
    extra["R03_partial_counts"] = {
        "log_strict_wins": win_log, "identity_strict_wins": win_id,
        "ties": tied, "log_negative_means": neg_log,
        "identity_negative_means": neg_id,
        "matches_committed": bool(
            win_log == rp["partial_log_strict_wins"]
            and win_id == rp["partial_identity_strict_wins"]
            and tied == rp["partial_ties"]
            and neg_log == rp["partial_log_negative_means"]
            and neg_id == rp["partial_identity_negative_means"])}
    scopes["R03"]["agrees"] = bool(scopes["R03"]["agrees"]
                                   and extra["R03_partial_counts"]["matches_committed"])

    control_path = os.path.join(ARTIFACTS, "controls.json")
    if os.path.isfile(control_path):
        with open(control_path) as handle:
            ctl = json.load(handle)
        const = F(ctl["constant_sse"])
        extra["control_band"] = {
            "band_low_matches": bool(F(ctl["band_low"]) == F(9, 10) * const),
            "band_high_matches": bool(F(ctl["band_high"]) == F(11, 10) * const),
            "chosen_below_band": bool(F(ctl["chosen_arm_held_sse"]) < F(ctl["band_low"])),
            "all_controls_in_band": bool(ctl["in_band"] == ctl["controls"]),
            "controls_beating_the_chosen_arm": ctl["controls_beating_the_chosen_arm"]}

    out = {"schema": "GMI833HRealScaleRevivalOracleV1",
           "route": "B", "imports_primary_executor": False,
           "scopes": scopes, "extra": extra}
    with open(os.path.join(WHERE, "ORACLE_RESULT_V1.json"), "w") as handle:
        json.dump(out, handle, indent=1, sort_keys=True)
        handle.write("\n")
    bad = [k for k in KEYS if not scopes[k]["agrees"]]
    print("route B agreement: %s" % ("all three scopes" if not bad
                                     else "DISAGREES on " + ",".join(bad)))


if __name__ == "__main__":
    main()
