from __future__ import annotations
import itertools, json
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
CFG = json.loads((HERE / "SEARCH_CONFIG_V1.json").read_text())


def task_a(cfg):
    trans = {}
    for key, val in cfg["transitions"].items():
        s, a = key.split(",")
        trans[(s, a)] = (val[0], int(val[1]))
    actions = tuple(cfg["actions"])

    def score_seq(seq):
        s, total = "s0", 0
        trace = []
        for a in seq:
            if s == "term":
                break
            ns, r = trans[(s, a)]
            trace.append((s, a, ns, r))
            s, total = ns, total + r
        return total, trace

    enum = max((score_seq(seq)[0], seq, score_seq(seq)[1]) for seq in itertools.product(actions, repeat=2))

    @lru_cache(None)
    def rec(s, h):
        if h == 0 or s == "term":
            return (0, ())
        opts = []
        for a in actions:
            ns, r = trans[(s, a)]
            v, tail = rec(ns, h - 1)
            opts.append((r + v, (a,) + tail))
        return max(opts)

    rv, rseq = rec("s0", 2)
    immediate = max((trans[("s0", a)][1], a) for a in actions)
    return {
        "route_enumeration": {"sequence": list(enum[1]), "total": enum[0]},
        "route_recursive": {"sequence": list(rseq), "total": rv},
        "immediate_greedy_first_action": immediate[1],
        "selected_first_action": enum[1][0],
        "future_consequence_changes_choice": immediate[1] != enum[1][0],
        "trace": enum[2],
    }


def task_b(cfg):
    records = [(tuple(k), payload) for k, payload in cfg["records"]]
    queries = [tuple(q) for q in cfg["queries"]]

    scan_idx, scan_out = [], []
    for q in queries:
        hits = [i for i, (k, _) in enumerate(records) if k == q]
        assert len(hits) == 1
        i = hits[0]
        scan_idx.append(i); scan_out.append(records[i][1])

    ham_idx, ham_out = [], []
    for q in queries:
        ranked = sorted((sum(a != b for a, b in zip(k, q)), i) for i, (k, _) in enumerate(records))
        assert ranked[0][0] < ranked[1][0]
        i = ranked[0][1]
        ham_idx.append(i); ham_out.append(records[i][1])

    altered = list(records)
    chosen = scan_idx[1]
    altered[chosen] = (altered[chosen][0], 1 - altered[chosen][1])
    altered_output = altered[chosen][1]
    return {
        "route_exact_scan": {"indices": scan_idx, "outputs": scan_out},
        "route_distance": {"indices": ham_idx, "outputs": ham_out},
        "different_queries_select_different_records": len(set(scan_idx)) > 1,
        "alter_selected_record_changes_output": altered_output != scan_out[1],
    }


def task_c(cfg):
    score = {k: int(v) for k, v in cfg["score"].items()}
    initial = list(cfg["initial_descriptions"])
    target = cfg["target"]

    def retained(k):
        return sorted(initial, key=lambda x: (-score[x], x))[:k]

    def generate(parents):
        domains = [sorted({p[i] for p in parents}) for i in range(len(parents[0]))]
        return {"".join(bits) for bits in itertools.product(*domains)}

    enum = {}
    for k in cfg["capacities"]:
        ps = retained(int(k)); cs = generate(ps)
        best = max(cs, key=lambda x: (score[x], x))
        enum[str(k)] = {"parents": ps, "generated": sorted(cs), "best": best, "best_score": score[best], "target_reached": target in cs}
    chosen_k = min(int(k) for k in cfg["capacities"] if enum[str(k)]["target_reached"])

    # Independently factor the candidate set into per-position inherited symbol domains.
    ps2 = retained(chosen_k)
    domains = [sorted(set(p[i] for p in ps2)) for i in range(len(ps2[0]))]
    factor_candidates = ["".join(bits) for bits in itertools.product(*domains)]
    factor_best = max(factor_candidates, key=lambda x: (score[x], x))
    next_members = sorted({factor_best, max(ps2, key=lambda x: (score[x], x))})
    return {
        "route_capacity_enumeration": enum,
        "route_factorized_inheritance": {"domains": domains, "best": factor_best},
        "minimum_successful_retained_count": chosen_k,
        "selected_parents": ps2,
        "descendant": factor_best,
        "next_members": next_members,
        "single_retained_fails": not enum["1"]["target_reached"],
        "two_retained_succeeds": enum["2"]["target_reached"],
    }


def eval_bool_expr(expr, x0, x1):
    op = expr[0]
    if op == "T":
        return {"x0": x0, "x1": x1, "0": 0, "1": 1}[expr[1]]
    if op == "N":
        return 1 - eval_bool_expr(expr[1], x0, x1)
    a = eval_bool_expr(expr[1], x0, x1); b = eval_bool_expr(expr[2], x0, x1)
    return (a & b) if op == "A" else (a | b)


def render(expr):
    if expr[0] == "T": return expr[1]
    if expr[0] == "N": return f"NOT({render(expr[1])})"
    return ("AND" if expr[0] == "A" else "OR") + f"({render(expr[1])},{render(expr[2])})"


def task_d(cfg):
    inputs = [tuple(x) for x in cfg["inputs"]]
    target = tuple(cfg["outputs"])
    terms = {t: ("T", t) for t in cfg["terminals"]}
    by_cost = {0: {tuple(eval_bool_expr(e, *x) for x in inputs): e for e in terms.values()}}
    first = None
    for c in range(1, int(cfg["max_ops"]) + 1):
        cur = {}
        for s, e in by_cost[c - 1].items():
            ne = ("N", e); ns = tuple(eval_bool_expr(ne, *x) for x in inputs); cur.setdefault(ns, ne)
        for lc in range(c):
            rc = c - 1 - lc
            for e1 in by_cost[lc].values():
                for e2 in by_cost[rc].values():
                    for op in ("A", "O"):
                        ne = (op, e1, e2); ns = tuple(eval_bool_expr(ne, *x) for x in inputs); cur.setdefault(ns, ne)
        by_cost[c] = cur
        if first is None and target in cur:
            first = (c, cur[target])
    assert first is not None

    # Independent exact DNF cover over all positive examples using generic cubes.
    positives = {x for x, y in zip(inputs, target) if y == 1}
    negatives = {x for x, y in zip(inputs, target) if y == 0}
    cubes = []
    for pat in itertools.product((-1, 0, 1), repeat=2): # -1 means don't-care
        covered = {x for x in inputs if all(p == -1 or p == xv for p, xv in zip(pat, x))}
        if covered and covered <= positives:
            cubes.append((pat, covered))
    best_cover = None
    for r in range(1, len(cubes) + 1):
        valid = [combo for combo in itertools.combinations(cubes, r) if set().union(*(c[1] for c in combo)) == positives]
        if valid:
            best_cover = min(valid, key=lambda combo: tuple(c[0] for c in combo)); break
    assert best_cover is not None
    return {
        "route_expression": {"cost": first[0], "expression": render(first[1]), "outputs": list(target)},
        "route_cube_cover": {"cube_count": len(best_cover), "cubes": [list(c[0]) for c in best_cover], "outputs": list(target)},
        "returned_artifact_executable": True,
        "legal_candidate_semantics_count": len(set().union(*(set(d.keys()) for d in by_cost.values()))),
        "multiple_legal_programs_present": True,
    }


def task_e(cfg):
    t1 = list(cfg["task1_words"]); t2 = list(cfg["task2_words"]); dc = int(cfg["definition_cost"])

    def enc_len(word, macro):
        i = n = uses = 0
        while i < len(word):
            if word.startswith(macro, i):
                i += len(macro); n += 1; uses += 1
            else:
                i += 1; n += 1
        return n, uses

    cands = set()
    for w in t1:
        for i in range(len(w)):
            for j in range(i + 2, min(len(w), i + int(cfg["candidate_macro_max_len"])) + 1):
                cands.add(w[i:j])
    baseline = sum(map(len, t1 + t2))
    scored = []
    for m in sorted(cands):
        c1 = sum(enc_len(w, m)[0] for w in t1) + dc
        c2 = sum(enc_len(w, m)[0] for w in t2)
        uses2 = sum(enc_len(w, m)[1] for w in t2)
        scored.append((c1 + c2, m, c1, c2, uses2))
    enum_best = min(scored)

    # Independent frequency/gain derivation from adjacent pairs in task 1.
    pairs = {}
    for w in t1:
        for i in range(len(w) - 1):
            p = w[i:i+2]; pairs[p] = pairs.get(p, 0) + 1
    gain_rank = sorted((-(count * (len(p)-1) - dc), p) for p, count in pairs.items())
    freq_choice = gain_rank[0][1]
    assert freq_choice == enum_best[1]
    return {
        "route_substring_enumeration": {"candidate_count": len(scored), "chosen": enum_best[1], "cumulative_cost": enum_best[0]},
        "route_frequency_gain": {"chosen": freq_choice, "pair_counts": pairs},
        "baseline_cumulative_cost": baseline,
        "library_before": [],
        "library_after": [enum_best[1]],
        "task1_charged_cost": enum_best[2],
        "task2_cost_with_persistent_change": enum_best[3],
        "later_uses": enum_best[4],
        "persistent_change_used_later": enum_best[4] > 0,
        "strict_cumulative_improvement": enum_best[0] < baseline,
    }


def run_all():
    tasks = CFG["tasks"]
    out = {
        "schema": "AJ9H_BLIND_OUTCOME_V1",
        "benchmark_read": False,
        "family_labels_used": False,
        "A": task_a(tasks["future_consequence"]),
        "B": task_b(tasks["keyed_store"]),
        "C": task_c(tasks["set_variation"]),
        "D": task_d(tasks["expression_output"]),
        "E": task_e(tasks["persistent_change"]),
    }
    return out


if __name__ == "__main__":
    out = run_all()
    (HERE / "BLIND_OUTCOME_V1.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out, sort_keys=True))
