"""Route B -- materially independent oracle.

This module imports NOTHING from this package and nothing from the parent
package.  It re-declares the three held-out populations, the registered grids
and the predictor semantics from the frozen specification, and it differs from
route A in representation and algorithm at every step:

* survivor sets are ``frozenset``s of realization records, never integer
  bitmasks;
* the contract image is a set comprehension over those records, not a union of
  precomputed value masks;
* ceilings are ``max`` over a generator, not a cached bitmask scan;
* every machine's solved-set is obtained by its own independently written
  simulator, and the closed-form capability law is re-derived here rather than
  imported;
* the ten failure-mode predicates are written out longhand.

It reproduces, byte for byte, the same prediction-stream format as the freeze,
so agreement is checked by sha256 equality rather than by field-by-field
comparison.

Run:  python3 -I -B oracle_route_b_v1.py   (writes/prints ROUTE_B_RESULT_V1.json)
"""

from fractions import Fraction
import hashlib
import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

WORD_LEN = 4
BETA_B = {"beta_B": Fraction(1, 500), "beta_D": Fraction(1, 200),
          "beta_H": Fraction(1, 50), "beta_M": Fraction(1, 100)}
BETA_TOTAL = sum(BETA_B.values())
RHO_N = 14
UNSAT = "UNSATISFIED"
CUTS_B = ("Expr", "Res", "Reach", "Seen", "Epis")
CUT_MODE_B = {"Expr": "FM_EXPRESSIVITY", "Res": "FM_RESOURCE",
              "Reach": "FM_REACHABILITY", "Seen": "FM_SEARCH_BUDGET",
              "Epis": "FM_OBSERVED_SHORTFALL"}
MODES_B = ("FM_CANNOT_CHECK", "FM_INCONSISTENT", "FM_INFORMATION_CEILING",
           "FM_EXPRESSIVITY", "FM_RESOURCE", "FM_REACHABILITY",
           "FM_SEARCH_BUDGET", "FM_OBSERVED_SHORTFALL", "FM_ALIASING", "FM_NONE")


def all_words():
    acc = [()]
    cur = [()]
    for _ in range(WORD_LEN):
        nxt = []
        for word in cur:
            nxt.append(word + (0,))
            nxt.append(word + (1,))
        acc.extend(nxt)
        cur = nxt
    return acc


WORDS_B = all_words()


def task_target(index, word):
    if index == 0:
        return word[-1] if word else 0
    if index == 1:
        return sum(word) % 2
    return 1 if sum(word) % 3 == 0 else 0


VERIFIED_B = {"E_full": (0, 1, 2), "E_v0": (1, 2)}


# --------------------------------------------------------------------------
# Independently written simulators
# --------------------------------------------------------------------------


def sim_syn(machine, index, word):
    m, w, h = machine
    if ((h >> index) & 1) == 0:
        return 0
    if index == 0:
        if w != 1:
            return 0
        return word[-1] if word else 0
    total = 0
    for sym in word:
        total += sym
    state = total % m
    if index == 1:
        return state - 2 * (state // 2)
    return 1 if state - 3 * (state // 3) == 0 else 0


def sim_arch(machine, index, word):
    mech, param, w, h = machine
    if ((h >> index) & 1) == 0:
        return 0
    if index == 0:
        if w != 1:
            return 0
        return word[-1] if word else 0
    if mech == "FF":
        state = sum(word[len(word) - param:]) if word else 0
    elif mech == "REC":
        state = sum(word) % param
    elif mech == "CTR":
        total = sum(word)
        state = param if total > param else total
    else:
        state = 0
        for sym in word:
            if sym:
                state = state + 1 if state < param else state
            else:
                state = state - 1 if state > 0 else 0
    if index == 1:
        return state - 2 * (state // 2)
    return 1 if state - 3 * (state // 3) == 0 else 0


def solved_by_simulation(sim, machine):
    bits = 0
    for index in range(3):
        good = True
        for word in WORDS_B:
            if sim(machine, index, word) != task_target(index, word):
                good = False
                break
        if good:
            bits += 1 << index
    return bits


# --------------------------------------------------------------------------
# Populations, re-declared
# --------------------------------------------------------------------------


def bitcount(value):
    out = 0
    while value:
        out += value & 1
        value >>= 1
    return out


def rho_vec(entries):
    vec = [0] * RHO_N
    for pos, val in entries:
        vec[pos] = val
    return tuple(vec)


def population_syn():
    out = []
    for m in (1, 2, 3, 6):
        for w in (0, 1):
            for h in range(8):
                k = 0 if m == 1 else (1 if m in (2, 3) else 2)
                rho = rho_vec(((0, m), (1, 1 + w), (2, 1 + bitcount(h)),
                               (3, 1 + (1 if h else 0))))
                out.append({"machine": (m, w, h), "sort": (rho[0], m, w, h),
                            "k": k, "rho": rho, "dev": m + bitcount(h) + w,
                            "obs": (1 + w, m % 2), "sim": sim_syn})
    return out


def population_arch():
    params = {"FF": (1, 2), "REC": (2, 3), "CTR": (2, 4), "STK": (1, 2)}
    kmap = {"FF": 0, "REC": 1, "CTR": 1, "STK": 2}
    out = []
    for mech in ("FF", "REC", "CTR", "STK"):
        for param in params[mech]:
            for w in (0, 1):
                for h in range(8):
                    extra = 1 if mech in ("CTR", "STK") else 0
                    rho = rho_vec(((0, param + extra), (1, 1 + w),
                                   (2, 1 + bitcount(h)),
                                   (3, 3 + (1 if mech in ("REC", "CTR") else 0))))
                    out.append({"machine": (mech, param, w, h),
                                "sort": (rho[0], param, w, h),
                                "k": kmap[mech], "rho": rho,
                                "dev": param + bitcount(h) + w + kmap[mech],
                                "obs": (1 + w, param % 2), "sim": sim_arch})
    return out


def population_real(measured):
    out = []
    for mech in ("MLP", "GRU"):
        for size in (2, 8):
            for w in (0, 1):
                for h in (1, 3, 5, 7):
                    k = 0 if mech == "MLP" else (1 if size < 8 else 2)
                    rho = rho_vec(((0, size), (1, 1 + w), (2, 1 + bitcount(h)),
                                   (3, 5 + (1 if mech == "GRU" else 0))))
                    key = "%s|%d|%d|%d" % (mech, size, w, h)
                    out.append({"machine": (mech, size, w, h),
                                "sort": (rho[0], rho[3], size, w, h),
                                "k": k, "rho": rho,
                                "dev": size + bitcount(h) + w + (2 if mech == "GRU" else 0),
                                "obs": (1 + w, 1 if mech == "GRU" else 0),
                                "sim": None,
                                "measured_bits": measured[key] if measured else None})
    return out


GRIDS = {
    "SIGMA_SYN": {
        "mu": (Fraction(5, 11), Fraction(4, 11), Fraction(2, 11)),
        "budgets": ((2, 1, 2, 1), (3, 2, 3, 2), (6, 2, 4, 2)),
        "charges": ((0, 0, 0, 0), (1, 0, 0, 0)),
        "d": (3, 6, 99), "b": (0, 12, 24, 40, 64),
        "h": ("NO_OBSERVATION", (1, 0), (2, 1)),
        "tau": (Fraction(2, 11), Fraction(5, 11), Fraction(7, 11), Fraction(9, 11)),
    },
    "SIGMA_ARCH": {
        "mu": (Fraction(7, 13), Fraction(4, 13), Fraction(2, 13)),
        "budgets": ((2, 1, 2, 3), (3, 2, 3, 4), (5, 2, 4, 4)),
        "charges": ((0, 0, 0, 0), (1, 0, 0, 0)),
        "d": (4, 7, 99), "b": (0, 24, 48, 80, 128),
        "h": ("NO_OBSERVATION", (1, 0), (2, 1)),
        "tau": (Fraction(2, 13), Fraction(6, 13), Fraction(11, 13), Fraction(1)),
    },
    "SIGMA_REAL": {
        "mu": (Fraction(8, 17), Fraction(6, 17), Fraction(3, 17)),
        "budgets": ((2, 1, 2, 5), (8, 2, 3, 6), (8, 2, 4, 6)),
        "charges": ((0, 0, 0, 0), (1, 0, 0, 0)),
        "d": (6, 10, 99), "b": (0, 8, 16, 24, 32),
        "h": ("NO_OBSERVATION", (1, 0), (2, 1)),
        "tau": (Fraction(3, 17), Fraction(8, 17), Fraction(11, 17), Fraction(1)),
    },
}


def law_syn(machine):
    m, w, h = machine
    bits = 0
    if (h & 1) and w == 1:
        bits += 1
    if (h & 2) and m % 2 == 0:
        bits += 2
    if (h & 4) and m % 3 == 0:
        bits += 4
    return bits


def law_arch(machine):
    mech, param, w, h = machine
    exact_counter = (mech == "CTR" and param >= WORD_LEN)
    bits = 0
    if (h & 1) and w == 1:
        bits += 1
    if (h & 2) and ((mech == "REC" and param % 2 == 0) or exact_counter):
        bits += 2
    if (h & 4) and ((mech == "REC" and param % 3 == 0) or exact_counter):
        bits += 4
    return bits


def law_real(machine):
    mech, size, w, h = machine
    bits = 0
    if h & 1:
        bits += 1
    if (h & 2) and (mech == "GRU" or size >= 8):
        bits += 2
    if (h & 4) and size >= 8:
        bits += 4
    return bits


LAWS = {"SIGMA_SYN": law_syn, "SIGMA_ARCH": law_arch, "SIGMA_REAL": law_real}


def cap_of(bits, mu, contract):
    total = Fraction(0)
    for j in VERIFIED_B[contract]:
        if (bits >> j) & 1:
            total += mu[j]
    return total


def fits(rho, budget, charge):
    for j in range(RHO_N):
        left = budget[j] if j < len(budget) else 0
        used = charge[j] if j < len(charge) else 0
        if rho[j] > left - used:
            return False
    return True


def key_of(value):
    if isinstance(value, str):
        return (1, Fraction(0))
    return (0, value)


def ceiling_of(records, contract):
    best = None
    for rec in records:
        val = rec["cap"][contract]
        if best is None or val > best:
            best = val
    return best


def run_universe(name, population, measured_table=None):
    grid = GRIDS[name]
    mu = grid["mu"]
    law = LAWS[name]
    for rec in population:
        if name == "SIGMA_REAL":
            rec["bits"] = law(rec["machine"])
            rec["measured"] = rec.get("measured_bits")
        else:
            rec["bits"] = law(rec["machine"])
            rec["measured"] = solved_by_simulation(rec["sim"], rec["machine"])
        rec["cap"] = dict((c, cap_of(rec["bits"], mu, c)) for c in ("E_full", "E_v0"))
    ordered = sorted(range(len(population)), key=lambda i: population[i]["sort"])
    for rank, idx0 in enumerate(ordered):
        population[idx0]["rank"] = rank
    for i, rec in enumerate(population):
        rec["index"] = i
    universe = frozenset(range(len(population)))
    by_index = dict((rec["index"], rec) for rec in population)

    k_sets = tuple(frozenset(j for j in range(3) if (bits >> j) & 1) for bits in range(8))
    r_values = tuple((b, c) for b in grid["budgets"] for c in grid["charges"])
    u_full = universe
    u_sub = frozenset(i for i, rec in enumerate(population) if rec["rho"][1] == 1)
    u_values = (("U0", "FEASIBLE_SET", u_full, None),
                ("U1", "CONFIDENCE_SET", u_sub, Fraction(1, 20)),
                ("U2", "CONFIDENCE_SET", u_full, Fraction(1, 10)))

    expr_sets = dict((i, frozenset(j for j in universe if by_index[j]["k"] in k_sets[i]))
                     for i in range(8))
    res_sets = dict((r, frozenset(j for j in universe if fits(by_index[j]["rho"], r[0], r[1])))
                    for r in r_values)
    reach_sets = dict((d, frozenset(j for j in universe if by_index[j]["dev"] <= d))
                      for d in grid["d"])
    seen_sets = dict((b, frozenset(j for j in universe if by_index[j]["rank"] < b))
                     for b in grid["b"])
    obs_sets = dict((h, universe if h == "NO_OBSERVATION" else
                     frozenset(j for j in universe if by_index[j]["obs"] == h))
                    for h in grid["h"])

    rows = []
    dispositions = {}
    modes = {}
    soundness_violations = 0
    point_pairs = 0
    point_hits = 0
    coverage_pairs = 0
    coverage_hits = 0
    law_vs_sim = 0
    for rec in population:
        if rec["measured"] is not None and rec["measured"] == rec["bits"]:
            law_vs_sim += 1
    idx = 0
    for k_index in range(8):
        for r_value in r_values:
            for d_value in grid["d"]:
                for b_value in grid["b"]:
                    for h_value in grid["h"]:
                        for u_id, u_kind, u_set, alpha in u_values:
                            for contract in ("E_full", "E_v0"):
                                cuts = {"Expr": expr_sets[k_index],
                                        "Res": res_sets[r_value],
                                        "Reach": reach_sets[d_value],
                                        "Seen": seen_sets[b_value],
                                        "Epis": obs_sets[h_value] & u_set}
                                ladder = [universe]
                                cur = universe
                                for cname in CUTS_B:
                                    cur = cur & cuts[cname]
                                    ladder.append(cur)
                                ceilings = [ceiling_of((by_index[j] for j in step), contract)
                                            for step in ladder]
                                subset_ceiling = {}
                                for size in range(6):
                                    for combo in itertools.combinations(range(5), size):
                                        cur2 = universe
                                        for j in combo:
                                            cur2 = cur2 & cuts[CUTS_B[j]]
                                        subset_ceiling[combo] = ceiling_of(
                                            (by_index[j] for j in cur2), contract)
                                survivors = (expr_sets[k_index] & reach_sets[d_value]
                                             & seen_sets[b_value] & obs_sets[h_value] & u_set)
                                res_set = res_sets[r_value]
                                image = set()
                                for j in survivors:
                                    image.add(by_index[j]["cap"][contract] if j in res_set
                                              else UNSAT)
                                ordered_image = tuple(sorted(image, key=key_of))
                                if u_kind == "FEASIBLE_SET":
                                    alpha_s = ""
                                    cov_s = ""
                                else:
                                    low = Fraction(1) - alpha - BETA_TOTAL
                                    if low < 0:
                                        low = Fraction(0)
                                    alpha_s = str(alpha)
                                    cov_s = str(low)
                                for tau in grid["tau"]:
                                    if not survivors:
                                        disp = "INCONSISTENT_REGISTERED_ASSUMPTIONS"
                                        value_s = ""
                                        ident_s = ""
                                        mode = "FM_INCONSISTENT"
                                    else:
                                        if len(ordered_image) == 1:
                                            disp = "IDENTIFIED"
                                            value_s = _show(ordered_image[0])
                                            ident_s = value_s
                                        else:
                                            disp = "CANNOT_IDENTIFY"
                                            value_s = ""
                                            ident_s = ";".join(_show(v) for v in ordered_image)
                                        mode = _mode_of(ceilings, tau, survivors, res_set,
                                                        by_index, contract)
                                    order_class = _order_class(subset_ceiling, tau)
                                    dispositions[disp] = dispositions.get(disp, 0) + 1
                                    modes[mode] = modes.get(mode, 0) + 1
                                    if survivors:
                                        hitset = set(ordered_image)
                                        for j in survivors:
                                            true_val = (_measured_cap(by_index[j], mu, contract)
                                                        if j in res_set else UNSAT)
                                            coverage_pairs += 1
                                            if true_val in hitset:
                                                coverage_hits += 1
                                            if disp == "IDENTIFIED":
                                                point_pairs += 1
                                                if true_val == ordered_image[0]:
                                                    point_hits += 1
                                                else:
                                                    soundness_violations += 1
                                    rows.append("\t".join((
                                        str(idx), str(k_index), str(r_values.index(r_value)),
                                        str(d_value), str(b_value),
                                        str(grid["h"].index(h_value)), u_id, contract,
                                        str(tau), disp, value_s, ident_s, mode, order_class,
                                        str(len(survivors)), u_kind, alpha_s, cov_s)))
                                    idx += 1
    stream = "\n".join(rows) + "\n"
    return {
        "universe": name,
        "population": len(population),
        "predictions_sha256": hashlib.sha256(stream.encode("utf-8")).hexdigest(),
        "grid_size": idx,
        "dispositions": dict(sorted(dispositions.items())),
        "modes": dict(sorted(modes.items())),
        "law_matches_measurement": law_vs_sim,
        "point_world_pairs": point_pairs,
        "point_hits": point_hits,
        "soundness_violations": soundness_violations,
        "coverage_pairs": coverage_pairs,
        "coverage_hits": coverage_hits,
    }


def _show(value):
    if isinstance(value, str):
        return value
    return str(value)


def _measured_cap(rec, mu, contract):
    bits = rec["measured"]
    total = Fraction(0)
    for j in VERIFIED_B[contract]:
        if (bits >> j) & 1:
            total += mu[j]
    return total


def _mode_of(ceilings, tau, survivors, res_set, by_index, contract):
    def low(value):
        return value is None or value < tau

    def high(value):
        return value is not None and value >= tau

    flags = {
        "FM_INFORMATION_CEILING": low(ceilings[0]),
        "FM_EXPRESSIVITY": low(ceilings[1]) and high(ceilings[0]),
        "FM_RESOURCE": low(ceilings[2]) and high(ceilings[1]),
        "FM_REACHABILITY": low(ceilings[3]) and high(ceilings[2]),
        "FM_SEARCH_BUDGET": low(ceilings[4]) and high(ceilings[3]),
        "FM_OBSERVED_SHORTFALL": low(ceilings[5]) and high(ceilings[4]),
    }
    met = set()
    for j in survivors:
        if j in res_set:
            met.add(1 if by_index[j]["cap"][contract] >= tau else 0)
        else:
            met.add(0)
    flags["FM_NONE"] = high(ceilings[5]) and met == set((1,))
    flags["FM_ALIASING"] = high(ceilings[5]) and met != set((1,))
    live = [name for name in MODES_B if flags.get(name)]
    if len(live) == 1:
        return live[0]
    return "MULTI:" + "|".join(live)


def _order_class(subset_ceiling, tau):
    labels = set()
    for order in itertools.permutations(range(5)):
        label = None
        acc = ()
        for position in range(6):
            value = subset_ceiling[tuple(sorted(acc))]
            if value is None or value < tau:
                label = ("FM_INFORMATION_CEILING" if position == 0
                         else CUT_MODE_B[CUTS_B[order[position - 1]]])
                break
            if position < 5:
                acc = acc + (order[position],)
        labels.add(label)
    if labels == set((None,)):
        return "NO_CROSSING"
    return "ORDER_FREE" if len(labels) == 1 else "CONJUNCTIVE"


def main():
    measured = None
    path = os.path.join(HERE, "REAL_RUNS", "REAL_MEASURED_V1.json")
    if os.path.exists(path):
        with open(path) as handle:
            measured = json.load(handle)["measured_solved_bits"]
    out = {"schema": "GMI_833_K_EVAL_ROUTE_B_V1", "universes": []}
    out["universes"].append(run_universe("SIGMA_SYN", population_syn()))
    out["universes"].append(run_universe("SIGMA_ARCH", population_arch()))
    real_pop = population_real(measured)
    if measured is None:
        out["universes"].append({"universe": "SIGMA_REAL",
                                 "status": "OUTCOMES_UNAVAILABLE"})
    else:
        out["universes"].append(run_universe("SIGMA_REAL", real_pop))
    body = json.dumps(out, indent=2, sort_keys=True)
    with open(os.path.join(HERE, "ROUTE_B_RESULT_V1.json"), "w") as handle:
        handle.write(body)
        handle.write("\n")
    sys.stdout.write(body)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
