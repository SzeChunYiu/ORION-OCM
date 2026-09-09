"""t10_ev_v1.py -- HST-T10 finite exact certificate: evolvability as useful-descendant
mass. Ev_t(x; U, D) computed EXACTLY for EVERY candidate by enumeration (no sampling).
Generates T10_EV_ORACLE_V1.json. Deterministic; the only RNG is a SEEDED demo of the
finite-sample estimator (P3 seed for lane D) and it is recorded as such.

Finite specialization of the frozen definition (HST_DEFINITIONS_V1.md §4):
  candidate set X      = all operator words of length <= K=3 over {a1,a2,m2} (|X|=40)
  kernel Q(.|x)        = uniform over N(x), the distinct one-edit neighbours of x
                         (single substitution / insertion / deletion, result length <= 4,
                         x itself excluded) -- exactly computable
  ecologies            D_fut = {tau06..tau10} (future), D_cur = {tau01..tau05} (current)
  Useful(x'; D_fut)    := [# future tasks solved by x' >= U_MIN=1]   (frozen predicate)
  fitness(x)           := # current tasks solved (for the hostile contrast only)
  Ev(x; U, D_fut)      = |{x' in N(x): Useful(x';D_fut)}| / |N(x)|   (exact Fraction)
"""
import json
import math
import random
import time
from fractions import Fraction
from typing import Dict, List, Tuple

import finite_world_v1 as fw

K = 3
MAX_NBR_LEN = 4
U_MIN = 1
FUTURE_TASKS = ["tau06", "tau07", "tau08", "tau09", "tau10"]
CURRENT_TASKS = ["tau01", "tau02", "tau03", "tau04", "tau05"]
SEED = 20260910
M_EST = 200
DELTA = Fraction(5, 100)  # delta = 0.05 for the Hoeffding demo


def neighbourhood(x: Tuple[str, ...], alphabet: List[str]) -> List[Tuple[str, ...]]:
    """Distinct one-edit neighbours (sub/ins/del), length <= MAX_NBR_LEN, x excluded."""
    nb = set()
    for i in range(len(x)):  # substitutions
        for op in alphabet:
            if op != x[i]:
                nb.add(x[:i] + (op,) + x[i + 1:])
    for i in range(len(x) + 1):  # insertions
        for op in alphabet:
            w = x[:i] + (op,) + x[i:]
            if len(w) <= MAX_NBR_LEN:
                nb.add(w)
    for i in range(len(x)):  # deletions
        nb.add(x[:i] + x[i + 1:])
    nb.discard(x)
    return sorted(nb)


def tasks_by_id(ids: List[str]) -> List[Tuple[str, int, int]]:
    want = set(ids)
    return [t for t in fw.TASKS if t[0] in want]


def main() -> dict:
    t0 = time.time()
    table = dict(fw.OPS)
    table.update(fw.P_OP)
    alphabet = sorted(table)
    cur_tasks = tasks_by_id(CURRENT_TASKS)
    fut_tasks = tasks_by_id(FUTURE_TASKS)
    assert len(cur_tasks) == 5 and len(fut_tasks) == 5

    cands = fw.all_words(alphabet, K)   # complete tree: 1+3+9+27 = 40 candidates
    rows = []
    for x in cands:
        nb = neighbourhood(x, alphabet)
        cur = sum(1 for t in cur_tasks if fw.adm(x, t, table))
        fut = sum(1 for t in fut_tasks if fw.adm(x, t, table))
        useful = [n for n in nb
                  if sum(1 for t in fut_tasks if fw.adm(n, t, table)) >= U_MIN]
        ev = Fraction(len(useful), len(nb)) if nb else Fraction(0)
        rows.append({"x": list(x), "fitness_current": cur, "future_tasks_solved": fut,
                     "n_neighbours": len(nb), "n_useful": len(useful),
                     "ev_exact": [str(ev), float(ev)]})
    assert len(rows) == len(cands)

    def evf(r):
        return Fraction(r["ev_exact"][0])

    ev_max = max(rows, key=evf)
    ev_min_rows = [r for r in rows if evf(r) == min(evf(r2) for r2 in rows)]
    max_fit = max(r["fitness_current"] for r in rows)
    high_fit = [r for r in rows if r["fitness_current"] == max_fit]
    hi_fit_lo_ev = min(high_fit, key=evf)
    zero_fit = [r for r in rows if r["fitness_current"] == 0]
    lo_fit_hi_ev = max(zero_fit, key=evf) if zero_fit else None
    separation = (lo_fit_hi_ev is not None
                  and evf(lo_fit_hi_ev) > evf(hi_fit_lo_ev))

    # P3 seed: finite-sample estimator with exact Hoeffding radius, vs oracle.
    rng = random.Random(SEED)
    eps = Fraction(math.sqrt(math.log(2.0 / float(DELTA)) / (2.0 * M_EST))).limit_denominator(10 ** 9)
    estimator = {"form": "hatEv_m(x) = (1/m) * sum_{i=1..m} Useful(x'_i), x'_i iid ~ Q(.|x); "
                         "Hoeffding: P(|hatEv_m - Ev| >= eps) <= 2 exp(-2 m eps^2); "
                         "eps_delta = sqrt(ln(2/delta)/(2m))",
                 "m": M_EST, "delta": [str(DELTA), float(DELTA)],
                 "eps_delta": [str(eps), float(eps)],
                 "rng_seed": SEED, "note": "estimator is for lane D / P3; the oracle "
                                           "above is exact and needs no confidence "
                                           "interval"}
    demos = {}
    for label, r in [("argmax_ev", ev_max), ("argmin_ev", ev_min_rows[0]),
                     ("high_fitness_low_ev", hi_fit_lo_ev)] + \
                    ([("low_fitness_high_ev", lo_fit_hi_ev)] if lo_fit_hi_ev else []):
        x = tuple(r["x"])
        nb = neighbourhood(x, alphabet)
        oracle = evf(r)
        hits = 0
        for _ in range(M_EST):
            n = rng.choice(nb)
            if sum(1 for t in fut_tasks if fw.adm(n, t, table)) >= U_MIN:
                hits += 1
        hat = Fraction(hits, M_EST)
        covered = abs(hat - oracle) <= eps
        demos[label] = {"x": list(x), "oracle_ev": [str(oracle), float(oracle)],
                        "hatEv_m": [str(hat), float(hat)],
                        "oracle_within_hoeffding_interval": covered,
                        "note_if_uncovered": "a single realization may miss the interval "
                                             "with prob <= delta; the guarantee is "
                                             "probabilistic, the oracle is exact"}
    estimator["demos"] = demos

    doc = {
        "certificate_id": "T10_EV_ORACLE_V1",
        "theorem_id": "HST-T10",
        "world": fw.WORLD_SPEC,
        "scope_statement": "P2 finite exact over universe FW1 restricted to words of "
                           "length <= %d over {a1,a2,m2}: |X| = %d candidates, every Ev "
                           "value is an exact rational over a fully enumerated "
                           "neighbourhood; NOT an estimate; says nothing about other "
                           "ecologies/kernels (that is P3, lane D)." % (K, len(cands)),
        "specialization": {"candidate_set": "all words length <= %d over %s" % (K, alphabet),
                           "kernel_Q": "uniform over distinct one-edit neighbours "
                                       "(sub/ins/del), result length <= %d, self excluded"
                                       % MAX_NBR_LEN,
                           "ecology_D_future": FUTURE_TASKS,
                           "ecology_D_current": CURRENT_TASKS,
                           "Useful": "future_tasks_solved >= %d" % U_MIN,
                           "fitness": "# current-ecology tasks solved (display only)"},
        "ev_table": rows,
        "summary": {"argmax_ev": {"x": ev_max["x"], "ev": ev_max["ev_exact"],
                                  "fitness": ev_max["fitness_current"]},
                    "argmin_ev": {"x": ev_min_rows[0]["x"], "ev": ev_min_rows[0]["ev_exact"],
                                  "count_tied_at_min": len(ev_min_rows)},
                    "max_fitness": max_fit,
                    "high_fitness_low_ev_hostile": {
                        "x": hi_fit_lo_ev["x"], "fitness": hi_fit_lo_ev["fitness_current"],
                        "ev": hi_fit_lo_ev["ev_exact"],
                        "reading": "max-current-fitness morphology with the lowest "
                                   "useful-descendant mass: current fitness does not "
                                   "certify evolvability (§11 hostile)"},
                    "low_fitness_high_ev": (
                        {"x": lo_fit_hi_ev["x"], "fitness": 0,
                         "ev": lo_fit_hi_ev["ev_exact"],
                         "reading": "zero current fitness, high useful-descendant mass: "
                                    "a stepping stone invisible to current-fitness "
                                    "selection"}
                        if lo_fit_hi_ev else None),
                    "separation_confirmed": separation},
        "p3_estimator_seed": estimator,
        "oracle_not_estimate": True,
        "runtime_seconds": round(time.time() - t0, 3),
        "deterministic": True,
    }
    assert separation, "hostile separation failed: no (low fitness, high Ev) > (high fitness, low Ev) pair"
    # internal consistency: every showcased oracle value equals its ev_table row
    by_word = {tuple(r["x"]): Fraction(r["ev_exact"][0]) for r in rows}
    for d in demos.values():
        assert by_word[tuple(d["x"])] == Fraction(d["oracle_ev"][0]), "oracle/table mismatch"
    n_uncovered = sum(1 for d in demos.values() if not d["oracle_within_hoeffding_interval"])
    doc["p3_estimator_seed"]["uncovered_demos"] = n_uncovered
    return doc


if __name__ == "__main__":
    doc = main()
    with open("T10_EV_ORACLE_V1.json", "w") as fh:
        json.dump(doc, fh, sort_keys=True, indent=1)
    s = doc["summary"]
    print("T10 OK: |X|=%d argmax_ev=%s hiFit/loEv=%s(fit=%d,ev=%.4f) loFit/hiEv=%s(ev=%.4f)" % (
        len(doc["ev_table"]), s["argmax_ev"]["x"], s["high_fitness_low_ev_hostile"]["x"],
        s["high_fitness_low_ev_hostile"]["fitness"],
        s["high_fitness_low_ev_hostile"]["ev"][1],
        s["low_fitness_high_ev"]["x"], s["low_fitness_high_ev"]["ev"][1]))
