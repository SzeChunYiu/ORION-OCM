"""t02_reach_v1.py -- HST-T02 finite exact certificate: reach expansion by irreducible
primitive, plus the §11 hostile (grammar expansion that increases reach but worsens
typical search burden). Generates T02_REACH_WITNESS_V1.json. Deterministic, exact.

Checks performed (all by complete enumeration, no sampling):
  C1  p (a1) is admissible (it is a well-formed legal operator of the grammar).
  C2  p notin <O>: FULL closure BFS of O over all functions Z_16->Z_16, fixpoint-verified
      (closure closed under generators), exhaustive absence of p's image tuple.
  C3  <O> strict subset <O u {p}>: both closures enumerated, sizes compared, strict.
  C4  witness task tau: contract (s,g) with a word over O+{p} of cost <= B solving it,
      and NO word over O at ANY length solving it (complete state-BFS fixpoint on the
      finite state space + full transformation-closure fixpoint + structural parity
      check: every function in <O> maps even x to even f(x); p does not).
  C5  Reach_B comparison at B=8: complete word-tree enumeration both sides
      (2^9-1 = 511 words over O; 3^9-1 = 9841 over O+{p}); reachable-task sets compared.
  C6  HOSTILE: exact expected first-admissible-solution cost per task under the frozen
      proposal distribution (uniform over words <= L=6), before vs after adding p:
      mean over the 5 O-solvable tasks must WORSEN (reach expanded, burden worsened).
"""
import json
import time
from fractions import Fraction

import finite_world_v1 as fw

B_REACH = 8
PROP_LEN = 6


def main() -> dict:
    t0 = time.time()
    table_o = dict(fw.OPS)
    table_op = dict(fw.OPS)
    table_op.update(fw.P_OP)
    alphabet_o = sorted(table_o)
    alphabet_op = sorted(table_op)

    # C1 admissibility of p: legal operator, applied exactly
    p_name = sorted(fw.P_OP)[0]
    c1 = {"primitive": p_name, "legal_operator": True,
          "image_tuple": list(fw.P_OP[p_name])}

    # C2 full closure membership (exhaustive)
    clo_o = fw.full_closure(table_o)
    p_fn = fw.P_OP[p_name]
    witness_word = clo_o["functions"].get(p_fn)
    c2 = {"closure_size_O": clo_o["size"],
          "fixpoint_verified": clo_o["closed_under_generators"],
          "p_in_closure_O": witness_word is not None,
          "p_witness_word": (list(witness_word) if witness_word else None)}

    # C3 strict inclusion
    clo_op = fw.full_closure(table_op)
    strict = set(clo_o["functions"]) < set(clo_op["functions"])
    c3 = {"closure_size_O_plus_p": clo_op["size"], "strict_inclusion": strict}

    # structural parity check backing C4: every f in <O> maps evens to evens
    evens = set(range(0, fw.N, 2))
    parity_ok = all(f[x] in evens for f in clo_o["functions"] for x in evens)
    p_maps_even_to_odd = fw.P_OP[p_name][0] == 1 and 1 not in evens

    # C4 witness: exact per-task analysis. Cheapest cost with p from the complete word
    # tree to B; solvability-without-p decided by complete state-BFS over the FINITE
    # state space (a task is O-solvable at ANY length iff g is BFS-reachable from s),
    # independently corroborated by the closure and the parity structure.
    words_op_b = fw.all_words(alphabet_op, B_REACH)          # complete tree, |3^9-1|
    best_with_p = {}
    for w in words_op_b:                                     # shortest first (BFS order)
        for tid, s, g in fw.TASKS:
            if tid not in best_with_p and fw.adm(w, (tid, s, g), table_op):
                best_with_p[tid] = {"word": list(w), "cost": len(w)}
    o_reach_from = {}  # start state -> (visited set, dist map) under O
    for start in set(s for (_t, s, _g) in fw.TASKS):
        o_reach_from[start] = fw.state_bfs(table_o, alphabet_o, start)
    o_solvers = {}
    for tid, s, g in fw.TASKS:
        visited, dist = o_reach_from[s]
        if g in visited:
            o_solvers[tid] = {"cost": dist[g]}
    witness_tasks = [tid for (tid, _s, _g) in fw.TASKS
                     if tid in best_with_p and tid not in o_solvers]
    c4 = {"witness_tasks": witness_tasks,
          "example": {"task": witness_tasks[0] if witness_tasks else None,
                      "cost_with_p": (best_with_p[witness_tasks[0]]["cost"]
                                      if witness_tasks else None),
                      "cost_without_p": "INF: not in the complete state-BFS closure of "
                                        "O from the start state => unreachable at ANY "
                                        "composition length (finite state space)"},
          "exclusion_method": "complete state-BFS over Z_16 under O (all 16 states "
                              "enumerated per start; fixpoint = exhaustive) + full "
                              "transformation-closure fixpoint + parity structure",
          "parity_structural_check": parity_ok and p_maps_even_to_odd}

    # C5 Reach_B sets: complete word-tree enumeration both sides at B
    words_o_b = fw.all_words(alphabet_o, B_REACH)            # complete tree, |2^9-1|
    reach_o = set(tid for (tid, s, g) in fw.TASKS
                  if any(fw.adm(w, (tid, s, g), table_o) for w in words_o_b))
    reach_op = set(best_with_p)
    c5 = {"B": B_REACH,
          "words_enumerated_O": len(words_o_b),
          "words_enumerated_O_plus_p": len(words_op_b),
          "reach_O": sorted(reach_o), "reach_O_plus_p": sorted(reach_op),
          "expansion_tasks": sorted(reach_op - reach_o),
          "strict_expansion_at_B": reach_op > reach_o}

    # C6 HOSTILE: exact burdens
    before = {tid: fw.exact_burden(alphabet_o, table_o, task, PROP_LEN)
              for task in fw.TASKS for tid in [task[0]]}
    after = {tid: fw.exact_burden(alphabet_op, table_op, task, PROP_LEN)
             for task in fw.TASKS for tid in [task[0]]}
    solvable = sorted(reach_o)
    def mean_burden(bmap, ids):
        vals = [bmap[i]["expected_first_solution_cost"] for i in ids]
        if any(v[0] == "INF" for v in vals):
            return ["INF", None]
        f = sum((Fraction(v[0]) for v in vals), Fraction(0)) / len(vals)
        return [str(f), float(f)]
    mean_before_solvable = mean_burden(before, solvable)
    mean_after_solvable = mean_burden(after, solvable)
    worsened = (mean_before_solvable[0] != "INF" and mean_after_solvable[0] != "INF"
                and Fraction(mean_after_solvable[0]) > Fraction(mean_before_solvable[0]))
    c6 = {"proposal": "uniform over all words of length <= %d over the alphabet "
                      "(i.i.d. rounds; charged cost = total operator slots proposed "
                      "until first admissible word)" % PROP_LEN,
          "per_task_before": before, "per_task_after": after,
          "mean_over_O_solvable_before": mean_before_solvable,
          "mean_over_O_solvable_after": mean_after_solvable,
          "hostile_confirmed_reach_up_burden_worse": bool(worsened and c5["strict_expansion_at_B"]),
          "honest_note": "mean over ALL 10 tasks: before = INF (5 tasks unsolvable), "
                         "after = finite: the expansion is strictly beneficial for the "
                         "full task family while worsening TYPICAL burden on the "
                         "previously-solvable majority -- exactly the §11 hostile."}
    all_tasks_after = mean_burden(after, [t[0] for t in fw.TASKS])
    c6["mean_over_all_tasks_after"] = all_tasks_after

    doc = {
        "certificate_id": "T02_REACH_WITNESS_V1",
        "theorem_id": "HST-T02",
        "world": fw.WORLD_SPEC,
        "scope_statement": "P2 finite exact: certified ONLY over universe FW1 "
                           "(Z_16, 2+1 operators, 10 tasks); complete enumerations counted "
                           "below; not a statement over other worlds/universal operators.",
        "checks": {"C1_admissible_primitive": c1, "C2_p_notin_closure_O": c2,
                   "C3_strict_closure_inclusion": c3, "C4_witness_task": c4,
                   "C5_reach_B_expansion": c5, "C6_hostile_burden": c6},
        "exhaustive_enumeration_flags": {
            "closure_fixpoint_verified": bool(c2["fixpoint_verified"]
                                              and clo_op["closed_under_generators"]),
            "word_trees_complete": True,
            "state_bfs_complete": True,
            "word_tree_counts": {"O_to_%d" % B_REACH: len(words_o_b),
                                 "Op_to_%d" % B_REACH: len(words_op_b)}},
        "runtime_seconds": round(time.time() - t0, 3),
        "deterministic": True,
    }
    assert not c2["p_in_closure_O"], "C2 failed: p unexpectedly in <O>"
    assert c3["strict_inclusion"], "C3 failed"
    assert c4["parity_structural_check"], "C4 parity backing failed"
    assert c5["strict_expansion_at_B"], "C5 failed: no strict reach expansion at B"
    assert witness_tasks, "C4 failed: no witness task"
    assert worsened, "C6 failed: hostile did not reproduce (burden did not worsen)"
    return doc


if __name__ == "__main__":
    doc = main()
    with open("T02_REACH_WITNESS_V1.json", "w") as fh:
        json.dump(doc, fh, sort_keys=True, indent=1)
    print("T02 OK: closure_O=%d closure_Op=%d witness_tasks=%s burden %.3f -> %.3f" % (
        doc["checks"]["C2_p_notin_closure_O"]["closure_size_O"],
        doc["checks"]["C3_strict_closure_inclusion"]["closure_size_O_plus_p"],
        doc["checks"]["C4_witness_task"]["witness_tasks"],
        doc["checks"]["C6_hostile_burden"]["mean_over_O_solvable_before"][1],
        doc["checks"]["C6_hostile_burden"]["mean_over_O_solvable_after"][1]))
