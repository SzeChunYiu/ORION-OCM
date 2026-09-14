"""B20: obtaining an answer versus absorbing the capability, and what checking costs.

B10 priced one machine split into blocks under a context tag. B7 priced where to
look inside one input. Neither ever faced an ALTERNATIVE THAT IS NOT PART OF THE
MACHINE: an outside holder with its own competence set and its own posted price,
which may be wrong without saying so.

Three things follow only from that, and are derived here:

  1  the break-even between absorbing a capability and obtaining it, when the
     outside prices are heterogeneous -- and whether B10's finite expiry of a
     storage advantage survives heterogeneity (it does not, above a toll)
  2  the price of not being able to check an answer: a caller must hold either a
     competence map or a checker, and CHECKING IS CHEAPER THAN COMPUTING EXACTLY
     WHEN THE OBLIGATION IS RELATIONAL -- for a functional obligation, verifying
     an answer costs exactly what producing it costs
  3  what a mixture costs when competence sets overlap versus partition, and the
     failure mode of the selection rule when competence is misjudged

Everything is exhaustive enumeration over a finite world in exact integers. No
sampling, no floating point in any reported number.

THE COST PRIMITIVE is B10's -- minimal branching structure, node count held and
tests traversed, by dynamic programming over every subcube with no tree shape
assumed. B10 brute-force verified it on all 256 total three-variable functions.
This file introduces a code path B10 did not have -- DON'T-CARE cells, for
queries a machine is never asked -- so section 1 re-verifies the primitive
against exhaustive tree enumeration over every partial function on two and three
variables. The primitive is borrowed; the questions are not.

TWO CONVENTIONS, both load-bearing and both stated where they are used:

  - A caller knows WHICH task it is running and WHAT answer it was handed; it
    does not know the payload. So held cost counts every node of the machine,
    including the nodes that tell tasks apart, while traversal cost counts only
    tests on PAYLOAD variables. Knowing costs storage; probing costs time.
  - A holder posts ONE price, so its price is its worst-case traversal plus a
    toll. The toll is the only free parameter and it is swept exhaustively.
"""

import itertools
import json
import time

OUT = {}
T0 = time.time()

NIDX = 3                                  # bits naming the task
NPAY = 4                                  # bits of payload
NCLAIM = 2                                # bits of a handed-over answer
NTASK = 1 << NIDX                         # 8 tasks
NP = 1 << NPAY                            # 16 payloads


# ---------------------------------------------------------------------------
# THE COST PRIMITIVE
#
# A machine is charged for what it HOLDS -- every node of the smallest branching
# tree consistent with its obligations -- and for what it TRAVERSES on one query,
# counted over a designated set of PROBED variables. Cells the machine is never
# asked are don't-cares and constrain nothing.
# ---------------------------------------------------------------------------
_CELLS = {}


def assign_cells(nv):
    """Every subcube of the nv-cube, as a map from partial assignment to cells.

    Built once per arity and shared by every call, so the DP never rescans the
    whole cube to find out which cells a subcube contains.
    """
    if nv in _CELLS:
        return _CELLS[nv]
    table = {}

    def walk(assign, cells):
        table[assign] = cells
        for k in range(nv):
            if assign[k] is not None:
                continue
            for b in (0, 1):
                a = assign[:k] + (b,) + assign[k + 1:]
                if a not in table:
                    walk(a, tuple(i for i in cells if ((i >> k) & 1) == b))

    walk((None,) * nv, tuple(range(1 << nv)))
    _CELLS[nv] = table
    return table


def min_tree(cared, nv):
    """Smallest tree consistent with `cared` (None = never asked).

    Returns (nodes, depth, memo). Minimised lexicographically on (nodes, depth),
    exactly as B10. Every split is tried; no shape is assumed.
    """
    table = assign_cells(nv)
    memo = {}

    def rec(assign):
        got = memo.get(assign)
        if got is not None:
            return got
        seen = set()
        for i in table[assign]:
            v = cared[i]
            if v is not None:
                seen.add(v)
                if len(seen) > 1:
                    break
        if len(seen) <= 1:
            res = (1, 0, -1)                       # a leaf: held, never tested
        else:
            best = None
            for k in range(nv):
                if assign[k] is not None:
                    continue
                s0, d0, _ = rec(assign[:k] + (0,) + assign[k + 1:])
                s1, d1, _ = rec(assign[:k] + (1,) + assign[k + 1:])
                cand = (1 + s0 + s1, 1 + max(d0, d1), k)
                if best is None or cand[:2] < best[:2]:
                    best = cand
            res = best
        memo[assign] = res
        return res

    nodes, depth, _ = rec((None,) * nv)
    return nodes, depth, memo


def probe_cost(memo, cell, nv, probed):
    """Tests on PROBED variables along the path this cell takes."""
    assign = (None,) * nv
    n = 0
    while True:
        _, _, k = memo[assign]
        if k == -1:
            return n
        if k in probed:
            n += 1
        b = (cell >> k) & 1
        assign = assign[:k] + (b,) + assign[k + 1:]


# ---------------------------------------------------------------------------
print("=" * 78)
print("1  THE PRIMITIVE, RE-VERIFIED ON THE PATH B10 DID NOT HAVE")
print("=" * 78)
print("  B10 brute-force verified this DP on all 256 TOTAL three-variable")
print("  functions. Don't-cares are a new code path. Exhaustive enumeration of")
print("  EVERY decision tree is an independent implementation; it must agree")
print("  with the DP on every PARTIAL function of two and three variables.")
print()


def brute_min_tree(cared, nv):
    """Every tree over the nv-cube, by construction rather than by DP."""
    table = assign_cells(nv)

    def rec(assign):
        out = []
        seen = set()
        for i in table[assign]:
            v = cared[i]
            if v is not None:
                seen.add(v)
        if len(seen) <= 1:
            out.append((1, 0))
        for k in range(nv):
            if assign[k] is not None:
                continue
            for s0, d0 in rec(assign[:k] + (0,) + assign[k + 1:]):
                for s1, d1 in rec(assign[:k] + (1,) + assign[k + 1:]):
                    out.append((1 + s0 + s1, 1 + max(d0, d1)))
        return out

    return min(rec((None,) * nv))


prim = []
for nv in (2, 3):
    cells = 1 << nv
    n_checked = 0
    n_with_dc = 0
    for pattern in itertools.product((None, 0, 1), repeat=cells):
        dp = min_tree(list(pattern), nv)[:2]
        bf = brute_min_tree(list(pattern), nv)
        assert dp == bf, (
            "the don't-care DP disagrees with exhaustive tree enumeration on "
            "%r at arity %d: DP %r, brute force %r" % (pattern, nv, dp, bf))
        n_checked += 1
        if any(v is None for v in pattern):
            n_with_dc += 1
    prim.append({"arity": nv, "partial_functions": n_checked,
                 "with_dont_cares": n_with_dc, "mismatches": 0})
    print("  arity %d: %5d partial functions checked (%d carry don't-cares), "
          "0 mismatches" % (nv, n_checked, n_with_dc))
OUT["primitive_validation"] = prim
assert prim[0]["with_dont_cares"] > 0 and prim[1]["with_dont_cares"] > 0, (
    "the validation swept no don't-care patterns at all, so it did not "
    "exercise the code path it exists to check")

# The gate itself must be capable of failing. Corrupt the DP's answer and
# require the comparison to notice.
_mutant_caught = False
try:
    _bad = list(brute_min_tree([0, 1, None, 1], 2))
    _bad[0] += 1
    assert tuple(_bad) == min_tree([0, 1, None, 1], 2)[:2]
except AssertionError:
    _mutant_caught = True
assert _mutant_caught, (
    "a deliberately wrong node count passed the comparison, so the "
    "validation in this section proves nothing")
print("  mutation test: a node count off by one is rejected by the comparison.")


# ---------------------------------------------------------------------------
# THE WORLD
#
# Eight tasks over a four-bit payload, answers two bits wide. Two of them are
# RELATIONAL -- more than one answer is acceptable -- and six are FUNCTIONAL.
# That distinction is not decoration; section 4 turns on it.
# ---------------------------------------------------------------------------
def bits(p):
    return [(p >> j) & 1 for j in range(NPAY)]


def t_witness_one(p):
    b = bits(p)
    if p == 0:
        return None                                  # never asked
    return min(j for j in range(NPAY) if b[j])


def t_parity(p):
    b = bits(p)
    return b[0] ^ b[1] ^ b[2] ^ b[3]


def t_majority(p):
    return 1 if sum(bits(p)) >= 3 else 0


def t_project(p):
    b = bits(p)
    return (b[1] << 1) | b[0]


def t_const(p):
    return 0


def t_popcount(p):
    return sum(bits(p)) & 3


def t_witness_zero(p):
    b = bits(p)
    if p == NP - 1:
        return None                                  # never asked
    return min(j for j in range(NPAY) if not b[j])


def t_andor(p):
    b = bits(p)
    return ((b[0] & b[1]) << 1) | (b[2] | b[3])


TASKS = [
    ("witness-one", t_witness_one, "relational"),
    ("parity", t_parity, "functional"),
    ("majority", t_majority, "functional"),
    ("project", t_project, "functional"),
    ("constant", t_const, "functional"),
    ("popcount", t_popcount, "functional"),
    ("witness-zero", t_witness_zero, "relational"),
    ("and-or", t_andor, "functional"),
]
assert len(TASKS) == NTASK

ANS = [[TASKS[t][1](p) for p in range(NP)] for t in range(NTASK)]


def accepts(t, p, c):
    """Does the obligation for task t accept answer c on payload p?

    Functional: only the canonical answer. Relational: any index that is a
    genuine witness. This is the obligation a checker checks, and for a
    relational obligation it is weaker than reproducing the canonical answer.
    """
    kind = TASKS[t][2]
    if ANS[t][p] is None:
        return None                                  # never asked
    if kind == "functional":
        return 1 if c == ANS[t][p] else 0
    b = bits(p)
    if TASKS[t][0] == "witness-one":
        return 1 if b[c] == 1 else 0
    return 1 if b[c] == 0 else 0


# --- held machines over (task index, payload); index known at query time -----
IDX_VARS = set(range(NIDX))
PAY_VARS = set(range(NIDX, NIDX + NPAY))
NV_CAP = NIDX + NPAY


def cap_cared(mask):
    out = []
    for cell in range(1 << NV_CAP):
        t = cell & (NTASK - 1)
        p = cell >> NIDX
        out.append(ANS[t][p] if (mask >> t) & 1 else None)
    return out


HOLD = {}
DEPTH = {}
for mask in range(1 << NTASK):
    if mask == 0:
        HOLD[0] = 0
        DEPTH[0] = tuple([0] * NTASK)
        continue
    nodes, _, memo = min_tree(cap_cared(mask), NV_CAP)
    per = []
    for t in range(NTASK):
        if not (mask >> t) & 1:
            per.append(0)
            continue
        worst = 0
        for p in range(NP):
            if ANS[t][p] is None:
                continue
            worst = max(worst, probe_cost(memo, t | (p << NIDX), NV_CAP, PAY_VARS))
        per.append(worst)
    HOLD[mask] = nodes
    DEPTH[mask] = tuple(per)
ALL = (1 << NTASK) - 1

print()
print("=" * 78)
print("2  THE WORLD, AND THE PRICES NOBODY CHOSE")
print("=" * 78)
print("  Eight tasks over %d payloads. Held cost counts every node; traversal"
      % NP)
print("  counts only payload probes, because a caller knows which task it ran.")
print()
print("  %-14s %-12s %6s %7s %7s" % ("task", "obligation", "solve", "check", "hold"))
task_rows = []
SOLVE = []
CHECK = []
for t in range(NTASK):
    cared = [ANS[t][p] for p in range(NP)]
    s_nodes, s_depth, _ = min_tree(cared, NPAY)
    worst_check = 0
    check_nodes = 0
    for c in range(1 << NCLAIM):
        cc = [accepts(t, p, c) for p in range(NP)]
        n, d, _ = min_tree(cc, NPAY)
        worst_check = max(worst_check, d)
        check_nodes += n
    SOLVE.append(s_depth)
    CHECK.append(worst_check)
    task_rows.append({"task": TASKS[t][0], "obligation": TASKS[t][2],
                      "solve_probes": s_depth, "check_probes": worst_check,
                      "solve_nodes": s_nodes, "check_nodes": check_nodes})
    print("  %-14s %-12s %6d %7d %7d"
          % (TASKS[t][0], TASKS[t][2], s_depth, worst_check, s_nodes))
OUT["tasks"] = task_rows

# Non-vacuity: the held cost must actually share structure, or the whole
# assignment question decomposes per task and there is nothing combinatorial.
assert all(HOLD[m] <= HOLD[m | (1 << t)]
           for m in range(1 << NTASK) for t in range(NTASK)), (
    "held cost is not monotone under adding a task, so the primitive is wrong")
shared = []
for a in range(1 << NTASK):
    for b in range(1 << NTASK):
        if a & b or not a or not b:
            continue
        if HOLD[a | b] < HOLD[a] + HOLD[b]:
            shared.append((a, b, HOLD[a] + HOLD[b] - HOLD[a | b]))
assert shared, (
    "held cost is additive over every disjoint pair, so holding several "
    "capabilities shares nothing and the assignment problem is not a problem")
best_share = max(shared, key=lambda x: x[2])
OUT["sharing"] = {"pairs_with_sharing": len(shared),
                  "max_saving": best_share[2],
                  "hold_all": HOLD[ALL],
                  "hold_sum_of_singletons": sum(HOLD[1 << t] for t in range(NTASK))}
print()
print("  hold(all eight) = %d nodes; the eight held separately = %d nodes."
      % (HOLD[ALL], sum(HOLD[1 << t] for t in range(NTASK))))
print("  %d disjoint pairs share structure; the largest saving is %d nodes."
      % (len(shared), best_share[2]))


# --- outside holders; prices derived, not chosen -----------------------------
LAYOUTS = [
    ("partition", [(0, 1, 2), (3, 4), (5, 6, 7)]),
    ("overlap-2", [(0, 1, 2, 3), (2, 3, 4, 5), (5, 6, 7, 0)]),
    ("nested", [(0, 1), (0, 1, 2, 3), (0, 1, 2, 3, 4, 5, 6, 7)]),
    ("gap", [(0, 1), (2, 3), (4, 5)]),
    ("specialists", [(0,), (6,), (1, 2, 3, 4, 5, 6, 7)]),
    ("ladder", [(4,), (3, 4), (0, 3, 4)]),
    ("everyone", [(0, 1, 2, 3, 4, 5, 6, 7)] * 3),
]
TOLLS = [0, 1, 2, 3, 4]
WEIGHTS = [
    ("flat", tuple([1] * NTASK)),
    ("witness-heavy", (8, 1, 1, 1, 1, 1, 1, 8)),
]


def maskof(ts):
    m = 0
    for t in ts:
        m |= 1 << t
    return m


def price(ts, toll):
    """A holder posts ONE price: its own worst-case probing, plus the toll."""
    m = maskof(ts)
    return max(DEPTH[m]) + toll


print()
print("  %-13s %-34s %s" % ("layout", "competence sets", "posted prices, toll 0..4"))
holder_rows = []
for name, sets in LAYOUTS:
    ps = [[price(s, toll) for s in sets] for toll in TOLLS]
    holder_rows.append({"layout": name, "sets": [list(s) for s in sets],
                        "prices_by_toll": ps})
    print("  %-13s %-34s %s"
          % (name, " ".join("{%s}" % ",".join(str(x) for x in s) for s in sets),
             ps[0]))
OUT["holders"] = holder_rows
assert len({tuple(r["prices_by_toll"][0]) for r in holder_rows}) > 1, (
    "every layout posts the same prices, so heterogeneity of price -- the "
    "one thing distinguishing this from B10 -- is not present")
print()
print("  > Nobody chose these prices. A holder's price is what its own machine")
print("  > must probe, so BROAD COMPETENCE IS EXPENSIVE PER CALL: the holder")
print("  > that can do everything charges everyone for the depth it needs.")


# ---------------------------------------------------------------------------
# WORLDS, and the exhaustive assignment search
#
# A candidate is an assignment of every task to a SOURCE. Source 0 means the
# answer is computed from structure held here, and is charged the held cost once
# plus its probes on every query. Source i > 0 means the answer is obtained from
# outside holder i at its posted price, and is legal only where that holder is
# competent. Cost over r rounds, each round running the weight vector once:
#
#     total(a, r) = hold(held set) + r * sum_t n_t * c_t(a)
#
# Given the held set, each obtained task independently takes its cheapest legal
# source, so the search decomposes. That is a theorem, not an assumption, and
# section 5 brute-forces all 4^8 assignments in one world to confirm it.
# ---------------------------------------------------------------------------
WORLDS = []
for lname, sets in LAYOUTS:
    for toll in TOLLS:
        for wname, w in WEIGHTS:
            WORLDS.append({"layout": lname, "sets": sets, "toll": toll,
                           "weights": wname, "n": w})


ISO_DEPTH = tuple(DEPTH[1 << t][t] for t in range(NTASK))


def own_probes(held_mask, t, dmode):
    """What the caller probes for a task it holds.

    "interfering" is the real regime: the held machine is one tree, so holding
    more can push a task deeper. "isolated" is the counterfactual in which a
    task's probing ignores everything else held -- the ONLY thing it changes.
    """
    return DEPTH[held_mask][t] if dmode == "interfering" else ISO_DEPTH[t]


def derived_prices(sets, toll, dmode):
    if dmode == "interfering":
        return [max(DEPTH[maskof(s)]) + toll for s in sets]
    return [max(ISO_DEPTH[t] for t in s) + toll for s in sets]


def flat_price(dmode, toll):
    """What a holder of ALL eight tasks would charge, in the given regime."""
    return (max(DEPTH[ALL]) if dmode == "interfering" else max(ISO_DEPTH)) + toll


def plan(world, held_mask, prices, dmode="interfering"):
    """Cost line (A, B) for a held set, with each obtained task at its cheapest
    legal source. Returns None if some task has no legal source."""
    n = world["n"]
    sets = world["sets"]
    A = HOLD[held_mask]
    B = 0
    src = []
    for t in range(NTASK):
        if (held_mask >> t) & 1:
            B += n[t] * own_probes(held_mask, t, dmode)
            src.append(0)
            continue
        best = None
        for i, s in enumerate(sets):
            if t in s and (best is None or prices[i] < prices[best]):
                best = i
        if best is None:
            return None
        B += n[t] * prices[best]
        src.append(best + 1)
    return (A, B, tuple(src))


def envelope(world, prices, rmax, dmode="interfering"):
    """Cost-minimal held set at every round count from 0 to rmax."""
    lines = []
    for m in range(1 << NTASK):
        pl = plan(world, m, prices, dmode)
        if pl is not None:
            lines.append((m, pl[0], pl[1], pl[2]))
    out = []
    for r in range(rmax + 1):
        best = min(lines, key=lambda L: (L[1] + r * L[2], L[1], L[0]))
        out.append(best)
    return lines, out


RMAX = 255
print()
print("=" * 78)
print("3  ABSORBING VERSUS OBTAINING, AND WHETHER THE ADVANTAGE EXPIRES")
print("=" * 78)
print("  B10 found that a storage bargain paid in per-query work has a finite")
print("  life. Here the per-query price is set by someone else, so the question")
print("  is whether heterogeneity changes that. Sweep r = 0 .. %d rounds." % RMAX)
print()
print('  "Expires" = the monolith is asymptotically optimal, ties included: a')
print("  tie is not an advantage.")
print()
print("  %-13s %-5s %-14s %9s %9s %s"
      % ("layout", "toll", "weights", "r->inf held", "monolith", "expires"))

expiry_rows = []
for world in WORLDS:
    prices = [price(s, world["toll"]) for s in world["sets"]]
    lines, env = envelope(world, prices, RMAX)
    mono = plan(world, ALL, prices)
    tail = env[-1]
    asym = min(lines, key=lambda L: (L[2], L[1], L[0]))
    assert tail[0] == asym[0], (
        "the r = %d minimiser is not the asymptotic minimiser, so the sweep "
        "stopped before the last crossover" % RMAX)
    # "Expires" means obtaining keeps no STRICT per-query advantage: the
    # monolith is asymptotically optimal, ties included. A tie is not an
    # advantage, and at toll 0 obtaining carries no premium at all.
    expires = mono[1] <= min(L[2] for L in lines)
    steps = []
    for r in range(RMAX + 1):
        if not steps or env[r][0] != steps[-1][1]:
            steps.append((r, env[r][0]))
    nested = all((steps[i][1] & steps[i + 1][1]) == steps[i][1]
                 for i in range(len(steps) - 1))
    expiry_rows.append({"layout": world["layout"], "toll": world["toll"],
                        "weights": world["weights"],
                        "asymptotic_held": asym[0], "monolith_B": mono[1],
                        "asymptotic_B": asym[2], "expires": expires,
                        "n_steps": len(steps), "nested": nested,
                        "steps": [[r, m] for r, m in steps]})
    print("  %-13s %-5d %-14s %9s %9s %s"
          % (world["layout"], world["toll"], world["weights"],
             bin(asym[0])[2:].zfill(8), bin(ALL)[2:].zfill(8),
             "yes" if expires else "NEVER"))
OUT["expiry"] = expiry_rows

n_exp = sum(1 for r in expiry_rows if r["expires"])
n_nev = len(expiry_rows) - n_exp
print()
print("  expires (the monolith eventually wins): %d of %d worlds" % (n_exp, len(expiry_rows)))
print("  never expires (obtaining stays cheaper forever): %d of %d"
      % (n_nev, len(expiry_rows)))
assert n_exp > 0 and n_nev > 0, (
    "every world falls on the same side, so nothing has been derived about "
    "when the advantage expires -- one side or the other is a positive control "
    "that did not fire")

# The toll threshold: the smallest toll at which expiry is restored.
print()
print("  %-13s %-14s %s" % ("layout", "weights", "expires at toll"))
thresh = []
for lname, sets in LAYOUTS:
    for wname, w in WEIGHTS:
        row = []
        for toll in TOLLS:
            r = next(x for x in expiry_rows if x["layout"] == lname
                     and x["toll"] == toll and x["weights"] == wname)
            row.append(1 if r["expires"] else 0)
        first = next((TOLLS[i] for i, v in enumerate(row) if v), None)
        monotone = all(row[i] <= row[i + 1] for i in range(len(row) - 1))
        thresh.append({"layout": lname, "weights": wname, "by_toll": row,
                       "first_expiring_toll": first, "monotone": monotone})
        print("  %-13s %-14s %s   first: %s"
              % (lname, wname, row, "never" if first is None else first))
OUT["toll_threshold"] = thresh
assert all(x["monotone"] for x in thresh), (
    "raising the toll un-expires some world, which cannot happen if the toll "
    "only ever makes obtaining dearer -- the cost model is inconsistent")
assert any(x["first_expiring_toll"] not in (None, TOLLS[0]) for x in thresh), (
    "expiry is never switched ON by the toll, so the threshold is vacuous")

# Matched negative twins. Two independent things could break expiry: prices
# that track competence, and the fact that holding more deepens your own
# probing. Vary ONE dimension at a time -- the full 2x2.
print()
print("  TWO TWINS, one dimension each:")
print("    price     derived      a holder's price is its own worst-case probing")
print("              flat         every holder charges what a generalist charges")
print("    own cost  interfering  holding more deepens your OWN probing")
print("              isolated     your probing for a task ignores what else you hold")
print()
print("  %-10s %-13s %15s %6s   %s"
      % ("price", "own cost", "never expires", "of", "regime"))
fact = []
for pmode in ("derived", "flat"):
    for dmode in ("interfering", "isolated"):
        never = []
        for world in WORLDS:
            if pmode == "derived":
                prices = derived_prices(world["sets"], world["toll"], dmode)
            else:
                prices = [flat_price(dmode, world["toll"])] * len(world["sets"])
            lines, _ = envelope(world, prices, 1, dmode)
            mono = plan(world, ALL, prices, dmode)
            if mono[1] > min(L[2] for L in lines):
                never.append([world["layout"], world["toll"], world["weights"]])
        tag = ("B10's regime" if (pmode, dmode) == ("flat", "isolated")
               else ("this world" if (pmode, dmode) == ("derived", "interfering")
                     else ""))
        fact.append({"price": pmode, "own_cost": dmode,
                     "never_expiring": len(never), "of": len(WORLDS),
                     "worlds": never})
        print("  %-10s %-13s %15d %6d   %s"
              % (pmode, dmode, len(never), len(WORLDS), tag))
OUT["expiry_factorial"] = fact
cell = dict(((f["price"], f["own_cost"]), f["never_expiring"]) for f in fact)
wsets = dict(((f["price"], f["own_cost"]), set(tuple(x) for x in f["worlds"]))
             for f in fact)

assert cell[("flat", "isolated")] == 0, (
    "with flat prices AND no interference -- exactly B10's regime -- some "
    "storage advantage still never expires, so this ledger does not contain "
    "B10's law as a special case and something is wrong with the cost model")
assert cell[("derived", "isolated")] == 0, (
    "heterogeneous prices alone break expiry even without interference, so "
    "interference is NOT necessary and the attribution below is wrong")
assert max(cell.values()) > 0, (
    "no cell of the 2x2 ever survives, so expiry is universal here and there "
    "is nothing to attribute -- positive control did not fire")
assert len(set(cell.values())) > 1, (
    "all four cells agree, so neither dimension explains anything")

price_effect = (cell[("derived", "interfering")] - cell[("flat", "interfering")],
                cell[("derived", "isolated")] - cell[("flat", "isolated")])
depth_effect = (cell[("derived", "interfering")] - cell[("derived", "isolated")],
                cell[("flat", "interfering")] - cell[("flat", "isolated")])
same = wsets[("derived", "interfering")] == wsets[("flat", "interfering")]
OUT["expiry_attribution"] = {"price_effect": list(price_effect),
                             "depth_effect": list(depth_effect),
                             "heterogeneous_and_flat_agree_on_worlds": same}
print()
print("  effect of price heterogeneity (derived - flat): %s" % (price_effect,))
print("  effect of interference (interfering - isolated): %s" % (depth_effect,))
print("  the two price regimes name the SAME never-expiring worlds: %s" % same)
assert min(depth_effect) > 0, (
    "removing interference leaves some price regime unchanged, so it is not "
    "necessary and the attribution below is wrong")
assert max(price_effect) < min(depth_effect), (
    "price heterogeneity moves at least as many worlds as interference does, "
    "so calling one the mechanism and the other a modifier is not supported")
print()
print("  > INTERFERENCE IS NECESSARY: with a task's probing independent of what")
print("  > else is held, every storage advantage expires under BOTH price")
print("  > regimes (0 and 0). Restore interference and %d worlds survive."
      % cell[("derived", "interfering")])
print("  > Holding one more capability deepens the probing of everything")
print("  > already held, so a caller that absorbs everything pays for that on")
print("  > every query forever. This is B10's own finding -- conditioning costs")
print("  > computation rather than saving it -- read from outside the machine,")
print("  > where it becomes the reason an outside holder stays worth calling.")
print()
print("  > HETEROGENEOUS PRICES ARE NEITHER NECESSARY NOR SUFFICIENT: they")
print("  > carry %d worlds on their own (%d against %d) and none at all without"
      % (price_effect[0], cell[("derived", "interfering")],
         cell[("flat", "interfering")]))
print("  > interference. They move WHICH capability is given up first, not")
print("  > whether any is. So the answer to whether heterogeneity overturns")
print("  > B10's verdict is NO -- something else does.")

nest_bad = [r for r in expiry_rows if not r["nested"]]
print()
print("  Absorption is a staircase, not a switch: %d worlds have more than one"
      % sum(1 for r in expiry_rows if r["n_steps"] > 1))
print("  step. The staircase is NOT nested in %d of them -- a task absorbed at a"
      % len(nest_bad))
print("  low round count is handed back at a higher one.")
OUT["staircase"] = {"multi_step_worlds": sum(1 for r in expiry_rows if r["n_steps"] > 1),
                    "non_nested_worlds": len(nest_bad),
                    "max_steps": max(r["n_steps"] for r in expiry_rows)}
assert max(r["n_steps"] for r in expiry_rows) > 1, (
    "every world switches once, so there is no staircase and the claim that "
    "absorption is incremental is unsupported")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("4  WHAT IT COSTS NOT TO BE ABLE TO CHECK")
print("=" * 78)
print("  A holder asked outside its competence returns a WRONG ANSWER, not an")
print("  error. To stay correct a caller must hold one of two things: a map of")
print("  who is competent, or a checker. Both are held structure. B10 and B7")
print("  never had to buy either.")
print()
print("  %-14s %-12s %6s %7s %s" % ("task", "obligation", "solve", "check", "checking is"))
verif = []
for t in range(NTASK):
    rel = CHECK[t] < SOLVE[t]
    verif.append({"task": TASKS[t][0], "obligation": TASKS[t][2],
                  "solve_probes": SOLVE[t], "check_probes": CHECK[t],
                  "cheaper": rel})
    print("  %-14s %-12s %6d %7d %s"
          % (TASKS[t][0], TASKS[t][2], SOLVE[t], CHECK[t],
             "CHEAPER" if rel else ("equal" if CHECK[t] == SOLVE[t] else "dearer")))
OUT["verification"] = verif

rel_tasks = [v for v in verif if v["obligation"] == "relational"]
fun_tasks = [v for v in verif if v["obligation"] == "functional"]
assert rel_tasks and fun_tasks, "one of the two obligation kinds is missing"
assert all(v["cheaper"] for v in rel_tasks), (
    "a relational obligation is not cheaper to check than to solve, so the "
    "asymmetry this section claims does not exist in this world")
assert not any(v["cheaper"] for v in fun_tasks), (
    "POSITIVE CONTROL INVERTED: a functional obligation is cheaper to check "
    "than to solve, which would make the dichotomy below false")
assert all(v["check_probes"] == v["solve_probes"] for v in fun_tasks), (
    "checking a functional obligation is not EXACTLY as dear as solving it, "
    "so the sharp form of the claim is wrong and must be weakened")
print()
print("  > Checking is cheaper than computing EXACTLY when the obligation is")
print("  > relational. For a functional obligation the checker must pin down")
print("  > the same answer the solver would have produced, so it probes exactly")
print("  > as much: verification buys nothing at all. The verifier-gated")
print("  > lifecycle is licensed by MULTIPLE ACCEPTABLE ANSWERS, not by")
print("  > outsourcing.")

# The competence map: held over the task index, which the caller already knows,
# so it costs storage and no probing at all.
print()
print("  The other posture: hold a map from task to a competent holder. The")
print("  index is known at query time, so a map costs storage and ZERO probes.")
print()
print("  %-13s %-5s %-14s %8s %8s %8s %s"
      % ("layout", "toll", "weights", "obtained", "saving", "map", "worth it"))
posture = []
for world in WORLDS:
    prices = [price(s, world["toll"]) for s in world["sets"]]
    lines, env = envelope(world, prices, RMAX)
    held = env[RMAX // 2][0]
    obtained = ALL & ~held
    if obtained == 0:
        posture.append({"layout": world["layout"], "toll": world["toll"],
                        "weights": world["weights"], "obtained": 0,
                        "saving": 0, "map_nodes": 0, "worth": False,
                        "check_nodes": 0})
        continue
    src = next(L[3] for L in lines if L[0] == held)
    sel = [src[t] for t in range(NTASK)]
    map_nodes = min_tree(sel, NIDX)[0]
    saving = HOLD[ALL] - HOLD[held]
    ch = 0
    for t in range(NTASK):
        if (obtained >> t) & 1:
            ch += next(r["check_nodes"] for r in task_rows
                       if r["task"] == TASKS[t][0])
    posture.append({"layout": world["layout"], "toll": world["toll"],
                    "weights": world["weights"], "obtained": obtained,
                    "saving": saving, "map_nodes": map_nodes,
                    "check_nodes": ch, "worth": map_nodes < saving})
OUT["postures"] = posture
shown = 0
for pr in posture:
    if pr["obtained"] and shown < 12:
        print("  %-13s %-5d %-14s %8s %8d %8d %s"
              % (pr["layout"], pr["toll"], pr["weights"],
                 bin(pr["obtained"])[2:].zfill(8), pr["saving"],
                 pr["map_nodes"], "yes" if pr["worth"] else "NO"))
        shown += 1
live = [p for p in posture if p["obtained"]]
assert live, "no world ever obtained anything, so there is nothing to govern"
n_worth = sum(1 for p in live if p["worth"])
print()
print("  the map is cheaper than the capability it replaces: %d of %d worlds"
      % (n_worth, len(live)))
print("  the map costs at least as much as it saves:         %d of %d"
      % (len(live) - n_worth, len(live)))
assert n_worth > 0, (
    "the competence map never pays, so obtaining answers is never correct-able "
    "and the whole posture is dead -- positive control did not fire")
assert n_worth == len(live), (
    "with competence declared per TASK the map is a function of three bits the "
    "caller already knows, so it must be cheap in every world; if it is not, "
    "the map cost is being computed over the wrong variables")
print()
print("  > While competence respects task boundaries, knowing who to ask is")
print("  > nearly free: the map is a function of bits the caller already holds.")
print("  > Every world pays for it and no world collapses. That is the whole")
print("  > case for obtaining answers -- and it rests on an assumption nobody")
print("  > checked, which the twin below removes.")


# --- the twin: competence that does not respect task boundaries -------------
print()
print("  TWIN -- competence is not declared, it is EARNED. Give each holder a")
print("  probe budget: it reads b payload bits (holder i starting at bit i) and")
print("  answers with the commonest value in each class it can tell apart. Its")
print("  competence is the set of instances it actually gets right, which has")
print("  no reason to line up with task boundaries.")
print()


def bounded_competence(offset, b):
    """Instances a machine probing b payload bits from `offset` answers right."""
    reads = [(offset + j) % NPAY for j in range(b)]

    def key(t, p):
        return (t, tuple((p >> r) & 1 for r in reads))

    classes = {}
    for t in range(NTASK):
        for p in range(NP):
            if ANS[t][p] is not None:
                classes.setdefault(key(t, p), []).append(ANS[t][p])
    guess = {}
    for k, vals in classes.items():
        guess[k] = min(set(vals), key=lambda v: (-vals.count(v), v))
    ok = set()
    for t in range(NTASK):
        for p in range(NP):
            if ANS[t][p] is not None and guess[key(t, p)] == ANS[t][p]:
                ok.add((t, p))
    return ok


def hold_cells(cells, ans=None):
    """Held cost of answering exactly this set of instances and no others."""
    ans = ANS if ans is None else ans
    cared = []
    for cell in range(1 << NV_CAP):
        t = cell & (NTASK - 1)
        p = cell >> NIDX
        cared.append(ans[t][p] if (t, p) in cells else None)
    return min_tree(cared, NV_CAP)[0]


def fine_map(comps, ans=None):
    """Held cost and probing of a map from INSTANCE to a holder that is right.

    Don't-care where no holder is right: those instances cannot be obtained at
    all and must be held, so the map owes nothing for them. Naming ANY correct
    holder suffices -- the map is itself a relational obligation.
    """
    ans = ANS if ans is None else ans
    cared = []
    covered = set()
    for cell in range(1 << NV_CAP):
        t = cell & (NTASK - 1)
        p = cell >> NIDX
        if ans[t][p] is None:
            cared.append(None)
            continue
        who = [i for i, c in enumerate(comps) if (t, p) in c]
        if who:
            covered.add((t, p))
        cared.append(who[0] if who else None)
    nodes, _, memo = min_tree(cared, NV_CAP)
    probes = 0
    for cell in range(1 << NV_CAP):
        if cared[cell] is not None:
            probes = max(probes, probe_cost(memo, cell, NV_CAP, PAY_VARS))
    return nodes, probes, covered


print("  Compared like with like: the map against holding EXACTLY the instances")
print("  the map lets you obtain -- not against holding everything.")
print()
print("  %-8s %10s %10s %11s %14s %s"
      % ("budget", "covered", "map nodes", "map probes", "hold(covered)",
         "knowing costs"))
fine = []
for b in range(NPAY + 1):
    comps = [bounded_competence(i, b) for i in range(3)]
    nodes, probes, cov = fine_map(comps)
    hc = hold_cells(cov)
    verdict = "less than being right" if nodes < hc else "MORE THAN BEING RIGHT"
    fine.append({"budget": b, "covered_cells": len(cov), "map_nodes": nodes,
                 "map_probes": probes, "hold_covered": hc,
                 "map_cheaper_than_capability": nodes < hc})
    print("  %-8d %10d %10d %11d %14d %s"
          % (b, len(cov), nodes, probes, hc, verdict))
OUT["fine_competence"] = fine
assert any(x["map_probes"] > 0 for x in fine), (
    "an instance-level map never probes the payload, so it is really a "
    "task-level map and this twin changes nothing")
n_collapse = sum(1 for x in fine if not x["map_cheaper_than_capability"])
print()
print("  earned competence: the map collapses in %d of %d budgets."
      % (n_collapse, len(fine)))
print()
print("  > Naming a correct holder is itself a RELATIONAL obligation -- any")
print("  > correct one will do -- and that slack is why routing stays cheap")
print("  > even when competence stops respecting task boundaries. The same")
print("  > property that makes checking cheap makes knowing-who cheap.")


# --- is collapse possible at all? a genuine search, with a control -----------
print()
print("  Earned competence never collapsed. That is a negative, so search for a")
print("  positive: enumerate competence REGIONS from a catalogue of predicates")
print("  over instances, two holders at a time, and ask the same question.")
print()


def region(name):
    out = set()
    for t in range(NTASK):
        for p in range(NP):
            if ANS[t][p] is None:
                continue
            b = bits(p)
            if name == "parity-even":
                keep = (b[0] ^ b[1] ^ b[2] ^ b[3]) == 0
            elif name == "parity-odd":
                keep = (b[0] ^ b[1] ^ b[2] ^ b[3]) == 1
            elif name.startswith("bit"):
                keep = b[int(name[3])] == 1
            elif name == "dense":
                keep = sum(b) >= 2
            elif name == "sparse":
                keep = sum(b) < 2
            elif name == "low-tasks":
                keep = t < 4
            elif name == "high-tasks":
                keep = t >= 4
            else:
                keep = True
            if keep:
                out.add((t, p))
    return out


CATALOGUE = ["parity-even", "parity-odd", "bit0", "bit1", "bit2", "bit3",
             "dense", "sparse", "low-tasks", "high-tasks", "all"]
REG = dict((n, region(n)) for n in CATALOGUE)
search = []
for i in range(len(CATALOGUE)):
    for j in range(i, len(CATALOGUE)):
        a, c = CATALOGUE[i], CATALOGUE[j]
        nodes, probes, cov = fine_map([REG[a], REG[c]])
        hc = hold_cells(cov)
        search.append({"regions": [a, c], "covered": len(cov),
                       "map_nodes": nodes, "hold_covered": hc,
                       "collapses": nodes >= hc})
OUT["collapse_search"] = search
coll = [x for x in search if x["collapses"]]
print("  %-26s %9s %11s %14s %s"
      % ("competence regions", "covered", "map nodes", "hold(covered)", "verdict"))
for x in search[:4]:
    print("  %-26s %9d %11d %14d %s"
          % (" + ".join(x["regions"]), x["covered"], x["map_nodes"],
             x["hold_covered"], "COLLAPSES" if x["collapses"] else "routing pays"))
worst = max(search, key=lambda x: (x["map_nodes"], -x["hold_covered"]))
print("  %-26s %9d %11d %14d %s   <- dearest map"
      % (" + ".join(worst["regions"]), worst["covered"], worst["map_nodes"],
         worst["hold_covered"], "COLLAPSES" if worst["collapses"] else "routing pays"))
print()
print("  %d of %d region pairs collapse. The dearest map anywhere costs %d nodes"
      % (len(coll), len(search), worst["map_nodes"]))
print("  against a capability of %d." % worst["hold_covered"])

# A negative needs a control: prove the comparison CAN come out the other way,
# or "never collapses" is a statement about this code rather than this world.
FLAT_ANS = [[0 for _ in range(NP)] for _ in range(NTASK)]
ctrl_regions = []
for want in (0, 1):
    r = set()
    for t in range(NTASK):
        for pp in range(NP):
            b = bits(pp)
            if (b[0] ^ b[1] ^ b[2] ^ b[3]) == want:
                r.add((t, pp))
    ctrl_regions.append(r)
c_nodes, _, c_cov = fine_map(ctrl_regions, FLAT_ANS)
c_hold = hold_cells(c_cov, FLAT_ANS)
OUT["collapse_control"] = {"map_nodes": c_nodes, "hold_covered": c_hold,
                           "collapses": c_nodes >= c_hold}
print()
print("  CONTROL -- keep the competence boundary, make the capability trivial:")
print("  every answer constant, competence split by payload parity.")
print("  map %d nodes against a capability of %d: %s"
      % (c_nodes, c_hold, "COLLAPSES" if c_nodes >= c_hold else "routing pays"))
assert c_nodes >= c_hold, (
    "the control does not collapse either, so this comparison cannot detect a "
    "collapse at all and the negative below would be a statement about the "
    "code rather than about the world")
assert not coll, (
    "the search found a collapse after all -- the negative stated below is "
    "false and the condition must be characterised instead")
print()
print("  > The collapse is REAL -- the control exhibits it -- but it needs a")
print("  > capability SIMPLER than the competence boundary, and %d region pairs"
      % len(search))
print("  > over these eight tasks never produce one. So the competence map is")
print("  > NOT what kills obtaining answers from outside.")
print()
print("  > Naming a correct holder is itself a RELATIONAL obligation -- any")
print("  > correct one will do -- and that slack is exactly the slack that made")
print("  > checking cheap in the table above. One property buys both.")
print()
print("  > What survives is sharper than what was expected: a caller is never")
print("  > priced out of KNOWING who to ask. It is priced out of CHECKING, and")
print("  > only for functional obligations, where a checker probes exactly as")
print("  > much as a solver. Verification, not selection, is the cost B10 and")
print("  > B7 never had to pay.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("5  OVERLAP VERSUS PARTITION: WHAT A MIXTURE BUYS AND WHAT IT COSTS")
print("=" * 78)
print("  Coverage held equal where it can be. Overlap gives a task a second")
print("  competent holder; partition gives it exactly one.")
print()
print("  %-13s %8s %10s %12s %12s"
      % ("layout", "covered", "fallbacks", "cheapest sum", "broadest price"))
ov = []
for lname, sets in LAYOUTS:
    covered = 0
    for s in sets:
        covered |= maskof(s)
    fallback = sum(1 for t in range(NTASK)
                   if sum(1 for s in sets if t in s) >= 2)
    prices = [price(s, 0) for s in sets]
    cheap_sum = 0
    for t in range(NTASK):
        opts = [prices[i] for i, s in enumerate(sets) if t in s]
        if opts:
            cheap_sum += min(opts)
    ov.append({"layout": lname, "covered": bin(covered).count("1"),
               "fallbacks": fallback, "cheapest_sum": cheap_sum,
               "prices": prices, "broadest_price": max(prices),
               "overlap_cells": sum(max(0, sum(1 for s in sets if t in s) - 1)
                                    for t in range(NTASK))})
    print("  %-13s %8d %10d %12d %12d"
          % (lname, bin(covered).count("1"), fallback, cheap_sum, max(prices)))
OUT["overlap"] = ov

part = next(x for x in ov if x["layout"] == "partition")
over = next(x for x in ov if x["layout"] == "overlap-2")
everyone = next(x for x in ov if x["layout"] == "everyone")
assert part["fallbacks"] == 0, (
    "the partition layout has a fallback, so it is not a partition and the "
    "contrast in this section is not the contrast claimed")
assert over["fallbacks"] > 0, (
    "the overlapping layout has no fallback, so the positive control for this "
    "section did not fire")
assert over["covered"] == part["covered"], (
    "the two layouts do not cover the same tasks, so their prices are not "
    "comparable and the margin below means nothing")
assert over["cheapest_sum"] > part["cheapest_sum"], (
    "overlap is not dearer than partition at equal coverage, so redundancy is "
    "free and the cost claimed below does not exist")

# Why: a holder's price is its own worst-case probing, so competence is
# monotone in price. Check it across every holder that appears anywhere.
pairs = []
for _, sets_a in LAYOUTS:
    for sa in sets_a:
        for _, sets_b in LAYOUTS:
            for sb in sets_b:
                if set(sa) < set(sb):
                    pairs.append((price(sa, 0), price(sb, 0)))
assert pairs, "no competence set is contained in another, so nothing to check"
assert all(a <= b for a, b in pairs), (
    "a strictly broader holder posts a CHEAPER price, which the cost primitive "
    "cannot produce -- the price function is wrong")
strict = [1 for a, b in pairs if a < b]
OUT["price_monotone"] = {"nested_pairs": len(pairs), "strictly_dearer": len(strict)}
print()
print("  Price is monotone in competence: of %d strictly nested holder pairs,"
      % len(pairs))
print("  %d have the broader holder strictly dearer, and none is cheaper."
      % len(strict))
assert strict, (
    "no broader holder is ever strictly dearer, so breadth is free and the "
    "mechanism named below does not operate")
print()
print("  > A fallback exists only where two holders can do the same task, and")
print("  > that duplication is what makes a holder broad -- which its own")
print("  > probing then charges for, on EVERY call, not only the calls that")
print("  > fail. At equal coverage overlap costs %d a round against partition's"
      % over["cheapest_sum"])
print("  > %d, and buys %d fallbacks for the difference. Under a partition a"
      % (part["cheapest_sum"], over["fallbacks"]))
print("  > misjudged competence has nowhere to go at all: %d fallbacks."
      % part["fallbacks"])

# B20 item 6: composition, or a distinct domain?
sep = sum(HOLD[1 << t] for t in range(NTASK))
print()
print("  Composition or a distinct domain? The OBTAINED side is composition --")
print("  cost is a plain sum over tasks, each at one posted price. The HELD side")
print("  is not: holding all eight costs %d nodes, holding them separately %d."
      % (HOLD[ALL], sep))
OUT["composition"] = {"hold_all": HOLD[ALL], "hold_separately": sep,
                      "is_composition_outside": True,
                      "is_composition_inside": HOLD[ALL] == sep}
assert HOLD[ALL] < sep, (
    "holding eight capabilities together costs exactly what holding them apart "
    "costs, so there is no interior and the composition question is empty")
print("  > A mixture is a composition on the outside and not one on the inside.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("6  NEUTRAL RECOVERY: NOTHING IN THE CANDIDATE SPACE IS NAMED")
print("=" * 78)
FORBIDDEN = ("tool", "solver", "router", "routing", "route", "hybrid",
             "dispatch", "expert", "gate")
SOURCE_LABELS = ["computed from structure held here"] + [
    "obtained from outside holder %d at its posted price" % i for i in range(3)]
bad = [(lab, v) for lab in SOURCE_LABELS for v in FORBIDDEN if v in lab.lower()]
print("  A candidate is an assignment of each task to a source. The sources are:")
for lab in SOURCE_LABELS:
    print("    - %s" % lab)
print()
print("  forbidden words in the candidate descriptors: %d" % len(bad))
assert not bad, "a family name leaked into the candidate space: %r" % bad
# The gate must be able to fail.
assert [(l, v) for l in SOURCE_LABELS + ["the dispatch table"]
        for v in FORBIDDEN if v in l.lower()], (
    "the vocabulary gate does not fire on a deliberately named candidate, so "
    "it proves nothing about the candidates that passed")
print("  mutation test: adding one mislabelled source makes the gate fire.")

# Brute force, to confirm the decomposition used everywhere above is exact.
# Brute force in an OVERLAPPING world: under a partition every task has
# exactly one legal holder, so the decomposition could not possibly fail and
# checking it there would prove nothing.
bw = next(w for w in WORLDS if w["layout"] == "overlap-2" and w["toll"] == 1)
bprices = [price(s, bw["toll"]) for s in bw["sets"]]
R_BF = 8
best_bf = None
n_assign = 0
for a in itertools.product(range(len(bw["sets"]) + 1), repeat=NTASK):
    held = 0
    ok = True
    for t in range(NTASK):
        if a[t] == 0:
            held |= 1 << t
        elif t not in bw["sets"][a[t] - 1]:
            ok = False
            break
    if not ok:
        continue
    n_assign += 1
    cost = HOLD[held] + R_BF * sum(
        bw["n"][t] * (DEPTH[held][t] if a[t] == 0 else bprices[a[t] - 1])
        for t in range(NTASK))
    if best_bf is None or cost < best_bf[0]:
        best_bf = (cost, held, a)
_, env_bf = envelope(bw, bprices, R_BF)
dec = env_bf[R_BF]
dec_cost = dec[1] + R_BF * dec[2]
print()
print("  brute force over all %d legal assignments at r = %d: cost %d"
      % (n_assign, R_BF, best_bf[0]))
print("  decomposed search (cheapest legal source per obtained task): cost %d"
      % dec_cost)
OUT["brute_force"] = {"legal_assignments": n_assign, "rounds": R_BF,
                      "brute_cost": best_bf[0], "decomposed_cost": dec_cost}
assert best_bf[0] == dec_cost, (
    "the decomposition is not exact: brute force finds a cheaper assignment "
    "than taking the cheapest legal source per task")
assert n_assign > (1 << NTASK), (
    "at most one holder was ever legal per task, so the decomposition was "
    "never asked to choose and this check is vacuous")

# Anti-rig: no single shape may win everywhere.
print()
print("  %-13s %-5s %-14s %-10s %s"
      % ("layout", "toll", "weights", "winner", "reads as"))
rec = []
for world in WORLDS:
    prices = [price(s, world["toll"]) for s in world["sets"]]
    lines, env = envelope(world, prices, 16)
    w = env[16]
    held = w[0]
    if held == ALL:
        shape = "all held"
    elif held == 0:
        shape = "none held"
    else:
        shape = "mixed"
    # the naive candidate: obtain everything the single cheapest holder covers
    cheapest = min(range(len(prices)), key=lambda i: prices[i])
    naive_held = ALL & ~maskof(world["sets"][cheapest])
    naive = plan(world, naive_held, prices)
    naive_cost = None if naive is None else naive[0] + 16 * naive[1]
    best_cost = w[1] + 16 * w[2]
    rec.append({"layout": world["layout"], "toll": world["toll"],
                "weights": world["weights"], "held": held, "shape": shape,
                "best_cost": best_cost, "naive_cost": naive_cost,
                "naive_optimal": naive_cost == best_cost})
OUT["recovery"] = rec
shapes = {}
for r in rec:
    shapes[r["shape"]] = shapes.get(r["shape"], 0) + 1
for r in rec[:10]:
    print("  %-13s %-5d %-14s %-10s %s"
          % (r["layout"], r["toll"], r["weights"], bin(r["held"])[2:].zfill(8),
             r["shape"]))
print("  ...")
print()
print("  winning shapes over %d worlds: %s" % (len(rec), shapes))
assert len(shapes) > 1, (
    "one shape wins in every world, so the candidate space is not "
    "discriminating and nothing has been recovered")
assert shapes.get("all held", 0) > 0, (
    "a single held machine never wins, so the search is rigged against it")
assert shapes.get("mixed", 0) > 0, (
    "a mixture never wins, so this family has not been recovered at all")
n_naive_bad = sum(1 for r in rec if not r["naive_optimal"])
print("  the obvious answer -- obtain everything the cheapest holder covers --")
print("  is SUBOPTIMAL in %d of %d worlds." % (n_naive_bad, len(rec)))
assert n_naive_bad > 0, (
    "the obvious answer is optimal everywhere, so the search recovers nothing "
    "that could not have been written down without it")
# Mutation test on the recovery gate itself.
_collapsed = [{"shape": "mixed"} for _ in rec]
_caught = False
try:
    assert len({x["shape"] for x in _collapsed}) > 1
except AssertionError:
    _caught = True
assert _caught, (
    "collapsing the candidate space to one shape still passes the diversity "
    "gate, so that gate does not police anything")
print("  mutation test: a candidate space collapsed to one shape fails the gate.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("7  THE SELECTION RULE, AND WHERE IT BREAKS")
print("=" * 78)
print("  The rule is: send each obtained task to the cheapest holder BELIEVED")
print("  competent. Overstate one holder's competence by one task and see")
print("  whether the rule changes its mind -- a misjudgement nobody acts on is")
print("  not a failure. Control: the same sweep under a rule that ignores price")
print("  and takes the first believed-competent holder.")
print()


def select(sets, prices, t, by_price):
    opts = [i for i, s in enumerate(sets) if t in s]
    if not opts:
        return None
    if by_price:
        return min(opts, key=lambda i: (prices[i], i))
    return opts[0]


mis = []
for world in WORLDS:
    sets = world["sets"]
    prices = [price(s, world["toll"]) for s in world["sets"]]
    # Where two holders post the same lowest price the tie is broken by index,
    # so the price-minimising rule and the price-blind control often pick the
    # SAME holder. Those worlds cannot separate the two rules and are marked.
    untied = sorted(prices)[0] < sorted(prices)[1]
    for by_price, rule in ((True, "cheapest"), (False, "first")):
        consequential = 0
        total = 0
        onto_cheapest = 0
        cheapest = min(range(len(prices)), key=lambda i: (prices[i], i))
        for i in range(len(sets)):
            for t in range(NTASK):
                if t in sets[i]:
                    continue
                total += 1
                belief = [set(s) for s in sets]
                belief[i].add(t)
                before = select(sets, prices, t, by_price)
                after = select(belief, prices, t, by_price)
                if after != before:
                    consequential += 1
                    if after == cheapest:
                        onto_cheapest += 1
        mis.append({"layout": world["layout"], "toll": world["toll"],
                    "weights": world["weights"], "rule": rule,
                    "overstatements": total, "consequential": consequential,
                    "onto_cheapest": onto_cheapest, "untied": untied})
OUT["misjudgement"] = mis

def totals(rows):
    out = {}
    for m in rows:
        a = out.setdefault(m["rule"], {"total": 0, "cons": 0, "onto": 0})
        a["total"] += m["overstatements"]
        a["cons"] += m["consequential"]
        a["onto"] += m["onto_cheapest"]
    return out


agg = totals(mis)
untied = totals([m for m in mis if m["untied"]])
OUT["misjudgement_totals"] = agg
OUT["misjudgement_totals_untied"] = untied
print("  %-10s %-9s %14s %13s %s"
      % ("prices", "rule", "overstatements", "consequential",
         "onto the cheapest"))
for label, a in (("all", agg), ("no tie", untied)):
    for k in ("cheapest", "first"):
        if k in a:
            print("  %-10s %-9s %14d %13d %17d"
                  % (label, k, a[k]["total"], a[k]["cons"], a[k]["onto"]))
assert agg["cheapest"]["total"] > 0, (
    "no overstatement was even possible, so this section swept nothing")
assert agg["cheapest"]["cons"] > 0, (
    "no misjudgement ever changes the selection, so the rule has no failure "
    "mode in this world and the section is vacuous")
assert agg["first"]["cons"] > 0, (
    "the control rule has no failure mode, so there is nothing to compare "
    "against -- the negative has no positive control")
assert untied and untied["cheapest"]["cons"] > 0, (
    "every world posts a tied lowest price, so the price-minimising rule is "
    "never distinguishable from the control and no comparison is possible")


def separates(a):
    """Does the price-minimising rule concentrate error on its preferred
    holder more than the price-blind control? Exact integer comparison."""
    return (a["cheapest"]["onto"] * a["first"]["cons"],
            a["first"]["onto"] * a["cheapest"]["cons"])


l_all, r_all = separates(agg)
l_un, r_un = separates(untied)
verdict = ("concentrates more than the control" if l_un > r_un else
           ("concentrates less than the control" if l_un < r_un else
            "does not separate from the control"))
OUT["misjudgement_verdict"] = verdict
OUT["misjudgement_separation"] = {"all_worlds": [l_all, r_all],
                                  "untied_worlds": [l_un, r_un]}
print()
print("  Tied lowest prices make the two rules pick the same holder, so the")
print("  comparison is read only on worlds with a STRICTLY cheapest holder:")
print("  %d of %d consequential misjudgements land on it under the price-"
      % (untied["cheapest"]["onto"], untied["cheapest"]["cons"]))
print("  minimising rule, against %d of %d under the control."
      % (untied["first"]["onto"], untied["first"]["cons"]))
assert 0 < untied["cheapest"]["onto"] < untied["cheapest"]["cons"], (
    "every consequential misjudgement lands on the cheapest holder, or none "
    "does, so the concentration statistic is degenerate and says nothing")
assert 0 < untied["first"]["onto"] < untied["first"]["cons"], (
    "the control's concentration statistic is degenerate, so there is nothing "
    "to compare the price-minimising rule against")
print()
print("  > On the untied worlds the price-minimising rule")
print("  > %s." % verdict)
if verdict == "does not separate from the control":
    print("  > So error does NOT demonstrably follow the preference of the rule.")
    print("  > What the sweep does establish is that misjudgement BITES at all:")
    print("  > %d of %d overstatements change where a task is sent, under both"
          % (untied["cheapest"]["cons"], untied["cheapest"]["total"]))
    print("  > rules alike. A caller is exposed to every one of those, and by")
    print("  > section 5 it has somewhere to fall back to only where competence")
    print("  > overlaps -- never under a partition.")
else:
    print("  > Errors follow the selection rule, so the holder a rule prefers")
    print("  > is the holder whose competence must be judged most carefully.")
print("  > Either way the exposure is priced by section 4: the caller can")
print("  > detect a wrong answer cheaply only where the obligation is")
print("  > relational.")

print()
print("=" * 78)
print("all assertions held   (%.1f s)" % (time.time() - T0))
print("=" * 78)

with open("microscopes/results/STAGE_TOOL_ROUTING_V1.json", "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
