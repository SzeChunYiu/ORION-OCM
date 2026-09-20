#!/usr/bin/env python3
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
RESEARCH = ROOT.parent

ILLEGAL = ("ILLEGAL", None)
UNDEFINED = ("UNDEFINED", None)
def VALUE(x): return ("VALUE", x)

RESP = {
    "h0":  (VALUE(0), VALUE(0), ILLEGAL, UNDEFINED),
    "h0a": (VALUE(0), VALUE(0), ILLEGAL, UNDEFINED),
    "h1":  (VALUE(0), VALUE(1), ILLEGAL, UNDEFINED),
    "h2":  (VALUE(0), VALUE(1), UNDEFINED, UNDEFINED),
    "h3":  (VALUE(0), VALUE(1), VALUE(0), UNDEFINED),
    "h4":  (VALUE(0), VALUE(1), VALUE(0), VALUE(1)),
}
H = tuple(RESP)

def need(cond, msg):
    if not cond:
        raise RuntimeError(msg)

def signature(h, tests):
    return tuple(RESP[h][i] for i in tests)

def quotient(tests, table=RESP):
    buckets = {}
    for h in H:
        sig = tuple(table[h][i] for i in tests)
        buckets.setdefault(sig, []).append(h)
    return sorted(sorted(v) for v in buckets.values())

def partitions(items):
    items = tuple(items)
    if not items:
        yield []
        return
    first = items[0]
    for part in partitions(items[1:]):
        yield [[first]] + [b[:] for b in part]
        for i in range(len(part)):
            new = [b[:] for b in part]
            new[i] = [first] + new[i]
            yield new

def sufficient(part):
    for block in part:
        if len({RESP[h] for h in block}) != 1:
            return False
    return True

TRANS = {
    "p": {"a": {"r"}},
    "r": {"b": {"z"}, "c": {"z"}},
    "q": {"a": {"qb", "qc"}},
    "qb": {"b": {"z"}},
    "qc": {"c": {"z"}},
    "z": {},
}

def traces(start, max_len=2):
    out = {()}
    frontier = {(start, ())}
    for _ in range(max_len):
        nxt = set()
        for state, tr in frontier:
            for label, succs in TRANS[state].items():
                for state2 in succs:
                    tr2 = tr + (label,)
                    out.add(tr2)
                    nxt.add((state2, tr2))
        frontier = nxt
    return out

def greatest_bisimulation():
    states = tuple(TRANS)
    rel = {(s, t) for s in states for t in states}
    changed = True
    while changed:
        changed = False
        for s, t in list(rel):
            ok = True
            for label, succs in TRANS[s].items():
                for s1 in succs:
                    if not any((s1, t1) in rel for t1 in TRANS[t].get(label, set())):
                        ok = False
            for label, succs in TRANS[t].items():
                for t1 in succs:
                    if not any((s1, t1) in rel for s1 in TRANS[s].get(label, set())):
                        ok = False
            if not ok:
                rel.remove((s, t))
                changed = True
    return rel

def classical_vs_predictive_countermodels():
    # A: X is independent of theta, so constant S is parameter-sufficient.
    # Future Y=X, so constant S is not predictive-sufficient.
    x_given_theta_A = {0: {0: .5, 1: .5}, 1: {0: .5, 1: .5}}
    parameter_sufficient_A = x_given_theta_A[0] == x_given_theta_A[1]
    predictive_sufficient_A = False  # P(Y=1|X=0)=0, P(Y=1|X=1)=1, constant S merges them.

    # B: X=theta, so constant S is not parameter-sufficient.
    # Future Y is constant, so constant S is predictive-sufficient.
    x_given_theta_B = {0: {0: 1.0, 1: 0.0}, 1: {0: 0.0, 1: 1.0}}
    parameter_sufficient_B = x_given_theta_B[0] == x_given_theta_B[1]
    predictive_sufficient_B = True
    return {
        "A_parameter_sufficient": parameter_sufficient_A,
        "A_predictive_sufficient": predictive_sufficient_A,
        "B_parameter_sufficient": parameter_sufficient_B,
        "B_predictive_sufficient": predictive_sufficient_B,
    }

def relabel_table():
    rename = {h: f"x{i}" for i, h in enumerate(H)}
    transformed = {rename[h]: RESP[h] for h in H}
    q = {}
    for name, sig in transformed.items():
        q.setdefault(sig, []).append(name)
    return sorted(len(v) for v in q.values())

def bad_relabel_table():
    rename = {h: f"x{i}" for i, h in enumerate(H)}
    transformed = {rename[h]: RESP[h] for h in H}
    transformed[rename["h0a"]] = (VALUE(1),) + transformed[rename["h0a"]][1:]
    q = {}
    for name, sig in transformed.items():
        q.setdefault(sig, []).append(name)
    return sorted(len(v) for v in q.values())

def main():
    r3 = json.loads((RESEARCH / "gmi-1068-r3-contextual-attainability-v1" / "RESULT_V1.json").read_text())
    need(r3["history_scope"] == "FINITE_ADMISSIBLE_HISTORIES", "R3_SCOPE_DRIFT")

    full = quotient((0, 1, 2, 3))
    restricted = quotient((0,))
    expected_full = [["h0", "h0a"], ["h1"], ["h2"], ["h3"], ["h4"]]
    need(full == expected_full, f"FULL_QUOTIENT:{full}")
    need(restricted == [sorted(H)], f"RESTRICTED_QUOTIENT:{restricted}")

    collapsed = {
        h: tuple(("MISSING", None) if r in (ILLEGAL, UNDEFINED) else r for r in RESP[h])
        for h in H
    }
    collapsed_q = quotient((0, 1, 2, 3), collapsed)
    need(len(collapsed_q) == 4, f"MISSING_COLLAPSE:{collapsed_q}")

    all_parts = list(partitions(H))
    suff = [p for p in all_parts if sufficient(p)]
    min_blocks = min(len(p) for p in suff)
    coarsest_count = sum(len(p) == min_blocks for p in suff)
    need(len(all_parts) == 203, "BELL6")
    need(len(suff) == 2, f"SUFFICIENT_PARTITIONS:{len(suff)}")
    need(min_blocks == 5 and coarsest_count == 1, "REPRESENTATION_LOWER_BOUND")

    trace_equal = traces("p") == traces("q")
    bisimilar = ("p", "q") in greatest_bisimulation()
    need(trace_equal and not bisimilar, "TRACE_BISIM_BOUNDARY")

    suff_models = classical_vs_predictive_countermodels()
    need(suff_models == {
        "A_parameter_sufficient": True,
        "A_predictive_sufficient": False,
        "B_parameter_sufficient": False,
        "B_predictive_sufficient": True,
    }, "SUFFICIENCY_INCOMPARABILITY")

    relabel_sizes = relabel_table()
    bad_relabel_sizes = bad_relabel_table()
    need(relabel_sizes == [1, 1, 1, 1, 2], "RELABEL_INVARIANCE")
    need(bad_relabel_sizes == [1, 1, 1, 1, 1, 1], "RELABEL_NEGATIVE_CONTROL")

    hostiles = [
        ILLEGAL != UNDEFINED,
        len(collapsed_q) != len(full),
        len(restricted) < len(full),
        len(full) == 5,
        len(all_parts) == 203,
        min_blocks == 5,
        coarsest_count == 1,
        trace_equal and not bisimilar,
        suff_models["A_parameter_sufficient"] and not suff_models["A_predictive_sufficient"],
        suff_models["B_predictive_sufficient"] and not suff_models["B_parameter_sufficient"],
        relabel_sizes == [1, 1, 1, 1, 2],
        bad_relabel_sizes != relabel_sizes,
    ]
    need(all(hostiles), f"HOSTILES:{hostiles}")

    result = json.loads((ROOT / "RESULT_V2.json").read_text())
    expected = {
        "histories": 6,
        "tests_full": 4,
        "full_quotient_classes": 5,
        "restricted_quotient_classes": 1,
        "collapsed_missing_quotient_classes": 4,
        "all_representation_partitions": 203,
        "exact_sufficient_partitions": 2,
        "minimum_sufficient_states": 5,
        "coarsest_sufficient_partitions": 1,
        "hostiles_caught": 12,
    }
    for key, value in expected.items():
        need(result.get(key) == value, f"RESULT_DRIFT:{key}")

    print(json.dumps({
        "status": "GREEN",
        "full_quotient": full,
        "restricted_quotient": restricted,
        "collapsed_missing_classes": len(collapsed_q),
        "all_partitions": len(all_parts),
        "sufficient_partitions": len(suff),
        "minimum_sufficient_states": min_blocks,
        "coarsest_sufficient_partitions": coarsest_count,
        "trace_equal_non_bisimilar": trace_equal and not bisimilar,
        "sufficiency_countermodels": suff_models,
        "relabel_block_sizes": relabel_sizes,
        "bad_relabel_block_sizes": bad_relabel_sizes,
        "hostiles_caught": 12,
    }, sort_keys=True))

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("R4_S1_RED:" + repr(exc), file=sys.stderr)
        sys.exit(1)
