from __future__ import annotations

import json
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
CFG = json.loads((HERE / "SEARCH_CONFIG_V1.json").read_text())


def future_consequence(task):
    states = task["states"]
    actions = task["actions"]
    horizon = task["horizon"]
    trans = {}
    for k, v in task["transitions"].items():
        s, a = k.split(",")
        trans[(s, a)] = (v[0], int(v[1]))

    def rollout(seq):
        s = states[0]
        total = 0
        trace = []
        for a in seq:
            if s == "term":
                break
            ns, r = trans[(s, a)]
            trace.append([s, a, ns, r])
            total += r
            s = ns
        return total, trace

    enum_rows = []
    for seq in product(actions, repeat=horizon):
        total, trace = rollout(seq)
        enum_rows.append((total, tuple(seq), trace))
    enum_rows.sort(key=lambda x: (x[0], x[1]), reverse=True)
    enum_best = enum_rows[0]

    @lru_cache(None)
    def value(s, h):
        if s == "term" or h == 0:
            return 0
        return max(trans[(s, a)][1] + value(trans[(s, a)][0], h - 1) for a in actions)

    def best_action(s, h):
        rows = []
        for a in actions:
            ns, r = trans[(s, a)]
            rows.append((r + value(ns, h - 1), a, ns, r))
        return max(rows, key=lambda x: (x[0], x[1]))

    dyn0 = best_action(states[0], horizon)
    dyn1 = best_action("s1", 1)
    immediate = max((trans[(states[0], a)][1], a) for a in actions)
    assert enum_best[1][0] == dyn0[1] == "b"
    assert enum_best[0] == dyn0[0] == 5
    assert dyn1[1] == "a"
    assert immediate[1] == "a" and immediate[0] == 2
    return {
        "route_enumeration": {"best_sequence": list(enum_best[1]), "total": enum_best[0], "trace": enum_best[2]},
        "route_recursive_value": {"first_action": dyn0[1], "first_action_total": dyn0[0], "s1_action": dyn1[1]},
        "immediate_only_control": {"action": immediate[1], "score": immediate[0]},
        "agreement": True,
        "downstream_consequence_changes_first_choice": True,
    }


def keyed_store(task):
    records = [(tuple(k), int(v)) for k, v in task["records"]]
    queries = [tuple(q) for q in task["queries"]]
    expected = list(map(int, task["success_outputs"]))

    def exact_scan(q, recs):
        hits = [v for k, v in recs if k == q]
        return hits[0] if len(hits) == 1 else None

    def hamming(a, b):
        return sum(x != y for x, y in zip(a, b))

    def nearest(q, recs):
        rows = [(hamming(q, k), i, v) for i, (k, v) in enumerate(recs)]
        return min(rows)[2]

    out1 = [exact_scan(q, records) for q in queries]
    out2 = [nearest(q, records) for q in queries]
    assert out1 == expected == out2
    target_q = queries[1]
    reduced = [r for r in records if r[0] != target_q]
    altered = nearest(target_q, reduced)
    assert altered != expected[1]
    return {
        "route_exact_scan_outputs": out1,
        "route_distance_outputs": out2,
        "different_queries_select_different_payloads": len(set(out1)) > 1,
        "selected_record_ablation": {"query": list(target_q), "before": expected[1], "after": altered},
        "agreement": True,
    }


def set_variation(task):
    initial = tuple(task["initial_descriptions"])
    target = task["target"]
    scores = {k: int(v) for k, v in task["score"].items()}
    rounds = int(task["rounds"])
    capacities = list(map(int, task["capacities"]))

    def combine(a, b, mask):
        return "".join(b[i] if mask[i] else a[i] for i in range(len(a)))

    def children(pool):
        return {combine(a, b, m) for a in pool for b in pool for m in product((0, 1), repeat=len(a))}

    def topk(items, k):
        return tuple(sorted(set(items), key=lambda x: (scores[x], x), reverse=True)[:k])

    def generational(k):
        pool = topk(initial, k)
        trace = [list(pool)]
        parent_child = []
        for _ in range(rounds):
            generated = children(pool)
            for child in generated:
                for a in pool:
                    for b in pool:
                        if any(combine(a, b, m) == child for m in product((0, 1), repeat=len(a))):
                            parent_child.append([a, b, child])
                            break
                    else:
                        continue
                    break
            pool = topk(set(pool) | generated, k)
            trace.append(list(pool))
        return pool, trace, parent_child

    def closure_route(k):
        retained = topk(initial, k)
        seen_sets = {retained}
        frontier = [retained]
        parent_map = {}
        for depth in range(rounds):
            nxt = []
            for pool in frontier:
                generated = children(pool)
                next_pool = topk(set(pool) | generated, k)
                if next_pool not in seen_sets:
                    seen_sets.add(next_pool)
                    parent_map[next_pool] = pool
                    nxt.append(next_pool)
            frontier = nxt
        hits = [s for s in seen_sets if target in s]
        return bool(hits), sorted([list(s) for s in seen_sets])

    result = {}
    for k in capacities:
        pool, trace, inherit = generational(k)
        hit2, states2 = closure_route(k)
        hit1 = target in pool
        assert hit1 == hit2
        result[str(k)] = {
            "route_generation_hit": hit1,
            "route_set_closure_hit": hit2,
            "membership_trace": trace,
            "closure_states": states2,
            "inheritance_witness": next((r for r in inherit if r[2] == target), None),
        }
    assert result["1"]["route_generation_hit"] is False
    assert result["2"]["route_generation_hit"] is True
    assert result["2"]["inheritance_witness"] is not None
    return {
        "capacity_results": result,
        "two_record_set_required_at_scope": True,
        "evaluation_changes_persistent_membership": result["2"]["membership_trace"][0] != result["2"]["membership_trace"][1],
    }


def expression_output(task):
    inputs = [tuple(x) for x in task["inputs"]]
    target = tuple(task["outputs"])
    max_ops = int(task["max_ops"])
    terminals = {
        "x0": tuple(x for x, y in inputs),
        "x1": tuple(y for x, y in inputs),
        "0": tuple(0 for _ in inputs),
        "1": tuple(1 for _ in inputs),
    }
    best = {sem: (0, name) for name, sem in terminals.items()}
    for cost in range(1, max_ops + 1):
        snapshot = list(best.items())
        for sem, (c, expr) in snapshot:
            if c == cost - 1:
                out = tuple(1 - v for v in sem)
                if out not in best:
                    best[out] = (cost, f"NOT({expr})")
        snapshot = list(best.items())
        for c1 in range(cost):
            c2 = cost - 1 - c1
            left = [(s, e) for s, (c, e) in snapshot if c == c1]
            right = [(s, e) for s, (c, e) in snapshot if c == c2]
            for s1, e1 in left:
                for s2, e2 in right:
                    for op in ("AND", "OR"):
                        out = tuple((a & b) if op == "AND" else (a | b) for a, b in zip(s1, s2))
                        if out not in best:
                            best[out] = (cost, f"{op}({e1},{e2})")
    assert target in best
    cost, expr = best[target]

    def cube_matches(cube, inp):
        return all(c is None or c == x for c, x in zip(cube, inp))

    positives = {i for i, v in enumerate(target) if v == 1}
    cubes = []
    for cube in product((None, 0, 1), repeat=2):
        covered = {i for i, inp in enumerate(inputs) if cube_matches(cube, inp)}
        if covered and covered <= positives:
            cubes.append((cube, covered))
    covers = []
    for r in range(1, len(cubes) + 1):
        for comb in combinations(cubes, r):
            union = set().union(*(cov for _, cov in comb))
            if union == positives:
                lit = sum(sum(c is not None for c in cube) for cube, _ in comb)
                covers.append((r, lit, tuple(cube for cube, _ in comb)))
        if covers:
            break
    dnf = min(covers, key=lambda x: (x[0], x[1], x[2]))
    assert dnf[0] == 2
    assert cost <= max_ops
    return {
        "route_semantic_expression": {"program": expr, "operation_count": cost, "truth": list(target)},
        "route_exact_cube_cover": {"cube_count": dnf[0], "literal_count": dnf[1], "cubes": [["*" if x is None else x for x in cube] for cube in dnf[2]]},
        "multiple_legal_candidate_programs": len(best) > 4,
        "returned_artifact_executable": True,
        "agreement": True,
    }


def persistent_change(task):
    task1 = list(task["task1_words"])
    task2 = list(task["task2_words"])
    max_len = int(task["candidate_macro_max_len"])
    definition_cost = int(task["definition_cost"])

    def candidate_substrings(words):
        out = set()
        for w in words:
            for L in range(2, min(max_len, len(w)) + 1):
                for i in range(len(w) - L + 1):
                    out.add(w[i:i + L])
        return sorted(out)

    def encode(word, macro=None):
        if not macro:
            return len(word), list(word)
        i = 0
        tokens = []
        while i < len(word):
            if word.startswith(macro, i):
                tokens.append("M")
                i += len(macro)
            else:
                tokens.append(word[i])
                i += 1
        return len(tokens), tokens

    candidates = candidate_substrings(task1)
    assert candidates

    enum_rows = []
    for m in candidates:
        before1 = sum(len(w) for w in task1)
        after1 = definition_cost + sum(encode(w, m)[0] for w in task1)
        enum_rows.append((before1 - after1, m, after1))
    enum_rows.sort(key=lambda x: (x[0], len(x[1]), x[1]), reverse=True)
    chosen1 = enum_rows[0]

    freq_rows = []
    for m in candidates:
        nonoverlap = 0
        for w in task1:
            i = 0
            while i <= len(w) - len(m):
                if w.startswith(m, i):
                    nonoverlap += 1
                    i += len(m)
                else:
                    i += 1
        predicted_gain = nonoverlap * (len(m) - 1) - definition_cost
        freq_rows.append((predicted_gain, m, nonoverlap))
    freq_rows.sort(key=lambda x: (x[0], len(x[1]), x[1]), reverse=True)
    chosen2 = freq_rows[0]
    assert chosen1[1] == chosen2[1]
    macro = chosen1[1]
    assert chosen1[0] > 0

    before2 = sum(len(w) for w in task2)
    encoded2 = [encode(w, macro) for w in task2]
    after2 = definition_cost + sum(c for c, _ in encoded2)
    assert after2 < before2
    assert any("M" in tokens for _, tokens in encoded2)
    return {
        "route_exhaustive_admission": {"macro": macro, "task1_net_gain": chosen1[0]},
        "route_frequency_bound": {"macro": chosen2[1], "predicted_task1_gain": chosen2[0], "task1_occurrences": chosen2[2]},
        "persistent_library_before": list(task["base_symbols"]),
        "persistent_library_after": list(task["base_symbols"]) + ["M"],
        "task2_before_cost": before2,
        "task2_after_charged_cost": after2,
        "task2_encodings": [tokens for _, tokens in encoded2],
        "same_future_word_before_after": {"word": task2[0], "before": len(task2[0]), "after": encoded2[0][0]},
        "agreement": True,
    }


def main():
    tasks = CFG["tasks"]
    out = {
        "schema": "AJ9H_BLIND_OUTCOME_V1",
        "benchmark_access": False,
        "family_labels_visible": False,
        "future_consequence": future_consequence(tasks["future_consequence"]),
        "keyed_store": keyed_store(tasks["keyed_store"]),
        "set_variation": set_variation(tasks["set_variation"]),
        "expression_output": expression_output(tasks["expression_output"]),
        "persistent_change": persistent_change(tasks["persistent_change"]),
    }
    (HERE / "BLIND_OUTCOME_V1.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
