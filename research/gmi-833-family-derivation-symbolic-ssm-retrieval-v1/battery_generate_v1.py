"""Battery generator v1 — known-family derivation tranche (GMI #833).

Generates NEUTRAL_BATTERY_FREEZE_V1.json deterministically from the frozen
generation rules declared in PRIOR_DISCLOSURE_V1.md. Reads no benchmark, no
family data, no fingerprints: the three batteries are complete enumerations of
standard mathematical objects at derived sizes.

  B_CONTR — all (t0, rs, g) contraction-reachability decision tasks over the
            free term universe U (leaves {0,1}, ordered binary constructor,
            <= 3 leaves; 22 terms) x all 36 nonempty rule subsets of size <= 2
            of the 8 constant contractions x all goals g in U. 17424 tasks.
            Cell layout: t0 tokens (5, pad -1), lhs1 (3, pad -1), rhs1 (1),
            lhs2 (3, pad -1), rhs2 (1), g tokens (5, pad -1) = 18 cells.
  B_W2    — all 7^4 = 2401 total functions {0,1}^2 -> D on the canonical de
            Bruijn stream of order 3, two periods, zero-prefix history.
  B_EP    — all 4 assignments f:{1,2}->{0,1} x 2 presentation orders x 7
            query tokens. 56 episodes, output required at the final position.

Run: python3 -B battery_generate_v1.py   (writes NEUTRAL_BATTERY_FREEZE_V1.json
next to this file; byte-identical on regeneration).
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "NEUTRAL_BATTERY_FREEZE_V1.json"

GUARD = 3
DOMAIN = list(range(-GUARD, GUARD + 1))
PAD = -1  # non-token padding marker (a constant, never a token)

# ---------------------------------------------------------------------------
# B_CONTR: term universe, contraction rules, reachability
# ---------------------------------------------------------------------------
# Term ADT: int leaf (0 or 1) | ("N", left, right)


def term_tokens(t):
    """Canonical prefix token encoding; constructor -> 2, leaves -> 0/1."""
    if isinstance(t, int):
        return [t]
    return [2] + term_tokens(t[1]) + term_tokens(t[2])


def term_leaves(t):
    if isinstance(t, int):
        return 1
    return term_leaves(t[1]) + term_leaves(t[2])


def all_terms(max_leaves):
    """All ordered binary terms over leaves {0,1} with <= max_leaves leaves,
    in canonical order (leaf count, then prefix token sequence lexicographic)."""
    by_n = {1: [0, 1]}
    for n in range(2, max_leaves + 1):
        ts = []
        for ln in range(1, n):  # left leaves: all smaller sizes
            rn = n - ln
            if rn not in by_n:
                continue
            for l in by_n[ln]:
                for r in by_n[rn]:
                    ts.append(("N", l, r))
        by_n[n] = sorted(ts, key=term_tokens)
    all_t = []
    for n in sorted(by_n):
        all_t.extend(by_n[n])
    return all_t


def subterms(t):
    """All (path, subtree) pairs; path = tuple of child indices from root."""
    out = [((), t)]
    if not isinstance(t, int):
        for p, s in subterms(t[1]):
            out.append(((0,) + p, s))
        for p, s in subterms(t[2]):
            out.append(((1,) + p, s))
    return out


def replace_at(t, path, new):
    if not path:
        return new
    side = path[0]
    assert not isinstance(t, int)
    if side == 0:
        return ("N", replace_at(t[1], path[1:], new), t[2])
    return ("N", t[1], replace_at(t[2], path[1:], new))


def one_step(t, lhs, rhs):
    """All terms obtained by applying the contraction rule once (any position)."""
    outs = []
    for path, s in subterms(t):
        if s == lhs:
            outs.append(replace_at(t, path, rhs))
    return outs


def reachable_set(t0, lhs, rhs):
    seen = {t0}
    frontier = [t0]
    while frontier:
        nxt = []
        for t in frontier:
            for u in one_step(t, lhs, rhs):
                if u not in seen:
                    seen.add(u)
                    nxt.append(u)
        frontier = nxt
    return seen


def contr_battery():
    U = all_terms(3)
    assert len(U) == 22, len(U)
    assert max(term_leaves(t) for t in U) == 3
    two_leaf = [t for t in U if term_leaves(t) == 2]
    assert len(two_leaf) == 4
    rules = []
    for lhs in two_leaf:            # 4 two-leaf terms
        for rhs in (0, 1):          # 2 constant leaves
            rules.append((lhs, rhs))
    assert len(rules) == 8
    # rule-set class: ALL nonempty subsets of size <= 2 (36: 8 singles + 28
    # pairs), canonical order singles-then-pairs, pairs sorted by (lhs, rhs).
    rulesets = [[r] for r in rules]
    for i in range(len(rules)):
        for j in range(i + 1, len(rules)):
            rulesets.append([rules[i], rules[j]])
    assert len(rulesets) == 36
    idx = {t: i for i, t in enumerate(U)}

    def enc5(t):
        toks = term_tokens(t)
        assert len(toks) <= 5
        return toks + [PAD] * (5 - len(toks))

    rows = []
    layouts = []
    succ_pairs = []  # per (t0, ruleset): number of distinct one-step successors
    for t0 in U:
        for rs in rulesets:
            reach = set()
            for lhs, rhs in rs:
                reach |= reachable_set(t0, lhs, rhs)
            succ = set()
            for lhs, rhs in rs:
                for u in one_step(t0, lhs, rhs):
                    succ.add(u)
            succ_pairs.append([idx[t0], len(succ)])
            base = enc5(t0)
            slot1 = term_tokens(rs[0][0]) + [rs[0][1]]
            slot2 = (term_tokens(rs[1][0]) + [rs[1][1]]) if len(rs) == 2 \
                else [PAD] * 4
            pre = base + slot1 + slot2
            for g in U:
                rows.append([idx[t0], len(rs) - 1, idx[g],
                             1 if g in reach else 0])
                layouts.append(pre + enc5(g))
    # per-task machine cell layout (fixed slots, pad -1):
    # 0..4 t0 | 5..7 lhs1 | 8 rhs1 | 9..11 lhs2 | 12 rhs2 | 13..17 g
    return {
        "schema": "FDT_BATTERY_B_CONTR_V1",
        "class": "all (t0, rule-set, goal) pairs; rule-set class = all 36 nonempty subsets of size <= 2 of the 8 constant contractions",
        "universe_tokens": [term_tokens(t) for t in U],
        "universe_leaf_counts": [term_leaves(t) for t in U],
        "rule_table": [[idx[lhs], rhs] for lhs, rhs in rules],
        "rule_set_table": [[[idx[l], r] for (l, r) in rs] for rs in rulesets],
        "task_rows": rows,                # [t0_idx, set_flag, g_idx, y]
        "task_cell_layouts": layouts,     # 18 cells per task, order = rows
        "successor_census": {"pairs_total": len(succ_pairs),
                             "pairs_with_two_plus_distinct_successors":
                                 sum(1 for _, n in succ_pairs if n >= 2)},
        "output_required_at": "final step, designated output cell",
        "step_cap": 16,
        "cell_cap": 24,
        "n_tasks": len(rows),
    }


# ---------------------------------------------------------------------------
# B_W2: sliding two-slot window maps on a de Bruijn stream
# ---------------------------------------------------------------------------


def de_bruijn(k, n):
    """Canonical de Bruijn sequence of order n over alphabet size k (Lyndon)."""
    a = [0] * k * n
    seq = []

    def db(t, p):
        if t > n:
            if n % p == 0:
                seq.extend(a[1:p + 1])
        else:
            a[t] = a[t - p]
            db(t + 1, p)
            for j in range(a[t - p] + 1, k):
                a[t] = j
                db(t + 1, t)

    db(1, 1)
    return seq


def w2_battery():
    stream = de_bruijn(2, 3)            # order 3 = memory span 2 + 1
    assert len(stream) == 8 and len(set(tuple(stream[i:i + 3]) for i in range(8))) == 8
    periods = stream + stream           # 2 periods: stationarity pressure
    # zero-prefix history: window at t = (x_{t-1}, x_t) with x_{-1} = 0
    windows = []
    for t in range(len(periods)):
        prev = periods[t - 1] if t >= 1 else 0
        windows.append([prev, periods[t]])
    n_win = len(set(map(tuple, windows)))
    assert n_win == 4
    rows = []
    for a in DOMAIN:                    # f(0,0)
        for b in DOMAIN:                # f(0,1)
            for c in DOMAIN:            # f(1,0)
                for d in DOMAIN:        # f(1,1)
                    tt = [a, b, c, d]
                    out = [tt[2 * w[0] + w[1]] for w in windows]
                    rows.append({"truth_table": tt, "required_outputs": out})
    return {
        "schema": "FDT_BATTERY_B_W2_V1",
        "class": "all total functions {0,1}^2 -> D on the canonical de Bruijn stream (order 3, two periods, zero-prefix)",
        "stream": periods,
        "windows": windows,
        "task_rows": rows,
        "output_required_at": "every stream position",
        "cell_cap": 3,
        "n_tasks": len(rows),
    }


# ---------------------------------------------------------------------------
# B_EP: two-slot episode tasks
# ---------------------------------------------------------------------------


def ep_battery():
    rows = []
    for v1 in (0, 1):
        for v2 in (0, 1):
            for order in ((1, 2), (2, 1)):
                # stream slot i shows (k_i, v_i); v_i is the value bound to key k_i
                fa = {order[0]: v1, order[1]: v2}
                for q in DOMAIN:
                    y = fa[q] if q in fa else 0
                    rows.append({"order": list(order),
                                 "values": [v1, v2],
                                 "stream": [order[0], v1, order[1], v2, q],
                                 "required_final_output": y})
    assert len(rows) == 56, len(rows)
    return {
        "schema": "FDT_BATTERY_B_EP_V1",
        "class": "all assignments f:{1,2}->{0,1} x both presentation orders x all query tokens in D",
        "task_rows": rows,
        "output_required_at": "final position only",
        "cell_cap": 8,
        "n_tasks": len(rows),
    }


def main():
    bat = {
        "schema": "FDT_NEUTRAL_BATTERY_V1",
        "guard": GUARD,
        "domain": DOMAIN,
        "pad": PAD,
        "batteries": {
            "B_CONTR": contr_battery(),
            "B_W2": w2_battery(),
            "B_EP": ep_battery(),
        },
    }
    OUT.write_text(json.dumps(bat, indent=1, sort_keys=True))
    print("wrote", OUT.name,
          "B_CONTR", bat["batteries"]["B_CONTR"]["n_tasks"],
          "B_W2", bat["batteries"]["B_W2"]["n_tasks"],
          "B_EP", bat["batteries"]["B_EP"]["n_tasks"])


if __name__ == "__main__":
    main()
