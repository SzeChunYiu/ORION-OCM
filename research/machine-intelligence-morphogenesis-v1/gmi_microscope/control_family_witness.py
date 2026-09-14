"""B18: the control / reinforcement-learning families, derived and priced.

B18 sits between two results this corpus already has. B16 derived explicit
search and priced it against a compiled policy; B13 derived the belief state as
the quotient on a partially observed world. Control is what stands between
them: a POLICY is a compiled table, a VALUE FUNCTION is retained state, and
PLANNING is search. Nothing below re-derives the compile-versus-search
crossover or belief-state maintenance. What is derived here is what is specific
to CONTROL.

Two corpus laws do the work:

  PVR-3  retain beats recompute iff  S < (r-1)(C-U)
  CSR-1  one state per distinction that must still be made

Derived here, none of it assumed:

  1  the policy's memory, as the CSR-1 quotient on a sequential obligation --
     enumerated over machines, with a matched twin where one state suffices
  2  value as retained state: when future consequences matter, and the exact
     sense in which the value function is NOT the minimal retained state
  3  when a scalar reward signal is sufficient to specify the task at all
  4  the policy / value / model trichotomy, and the model-based versus
     model-free crossover in queries-per-goal
  5  on-policy versus off-policy as a reuse question, gated by coverage
  6  exploration pressure, by exhaustive enumeration of adaptive machines
  7  hierarchical options: recurrence of subtrajectories earns the option
  8  neutral recovery: machines enumerated with no control vocabulary at all

Exhaustive enumeration over small finite worlds. Exact integers and
fractions.Fraction throughout. No sampling, no floating point.

PVR-3 CONVENTION. PVR-3's (r-1) charges the retained machine for doing the
work ONCE to build what it keeps, then U per later use, against C per use for
the recomputing machine. Sections 4 and 5 instantiate that literally. Section 7
does not: there the stored object IS the one construction (S == C), so its
ledger is S + rU < rC, i.e. S < r(C-U). Both break-evens are printed side by
side where they appear so they stay comparable.
"""

from fractions import Fraction as F
import itertools
import json

OUT = {}
BAR = "=" * 78


# ===========================================================================
print(BAR)
print("1  THE POLICY'S MEMORY IS THE CSR-1 QUOTIENT ON A SEQUENTIAL OBLIGATION")
print(BAR)
print("  A cue is shown, then a corridor, then a junction. The correct turn at")
print("  the junction is the one the cue named. Machines are enumerated: m")
print("  memory classes, a class-update table and an action table, both over")
print("  (class, observation). No machine is told that the cue matters.")
print()

ACT = (0, 1)                      # 0 = left, 1 = right


def run_machine(m, upd, act, episodes, obs_index):
    """Total reward over the episode set. The action emitted at the FINAL
    observation of an episode is the one that is scored."""
    total = 0
    no = len(obs_index)
    for obs_seq, correct in episodes:
        c = 0
        for i, o in enumerate(obs_seq):
            oi = obs_index[o]
            a = act[c * no + oi]
            if i == len(obs_seq) - 1 and a == correct:
                total += 1
            c = upd[c * no + oi]
    return total


def minimal_memory(episodes, obs_alphabet, m_max=2):
    """Enumerate every (m, upd, act) machine up to m_max classes. Return the
    smallest m that attains the optimal return, and the machines that do."""
    obs_index = dict((o, i) for i, o in enumerate(obs_alphabet))
    no = len(obs_alphabet)
    optimal = len(episodes)
    for m in range(1, m_max + 1):
        winners = []
        n = m * no
        for act in itertools.product(ACT, repeat=n):
            for upd in itertools.product(range(m), repeat=n):
                if run_machine(m, upd, act, episodes, obs_index) == optimal:
                    winners.append((m, upd, act))
        if winners:
            return m, winners, optimal
    return None, [], optimal


CORR = 3
BASE_OBS = ("cueL", "cueR", "corr", "junc")
BASE_EP = ((("cueL",) + ("corr",) * CORR + ("junc",), 0),
           (("cueR",) + ("corr",) * CORR + ("junc",), 1))

TWIN_OBS = ("cueL", "cueR", "corr", "juncL", "juncR")
TWIN_EP = ((("cueL",) + ("corr",) * CORR + ("juncL",), 0),
           (("cueR",) + ("corr",) * CORR + ("juncR",), 1))

# the twin must differ in exactly one respect: whether the decision-time
# observation carries the cue. Everything else is asserted equal.
assert len(BASE_EP) == len(TWIN_EP), "different number of episodes"
assert [len(e[0]) for e in BASE_EP] == [len(e[0]) for e in TWIN_EP], \
    "different episode lengths"
assert [e[1] for e in BASE_EP] == [e[1] for e in TWIN_EP], \
    "different correct actions"
assert [e[0][:-1] for e in BASE_EP] == [e[0][:-1] for e in TWIN_EP], \
    "the twin changes more than the decision-time observation"

m_base, win_base, opt_base = minimal_memory(BASE_EP, BASE_OBS)
m_twin, win_twin, opt_twin = minimal_memory(TWIN_EP, TWIN_OBS)

# how many machines were actually searched, so the enumeration is visible
n_base = sum(len(ACT) ** (m * len(BASE_OBS)) * m ** (m * len(BASE_OBS))
             for m in range(1, m_base + 1))
n_twin = sum(len(ACT) ** (m * len(TWIN_OBS)) * m ** (m * len(TWIN_OBS))
             for m in range(1, m_twin + 1))

print("  %-30s %-10s %-14s %-12s %s"
      % ("world", "optimal", "machines seen", "minimal m", "machines that attain it"))
print("  %-30s %-10d %-14d %-12d %d"
      % ("cue hidden at the junction", opt_base, n_base, m_base, len(win_base)))
print("  %-30s %-10d %-14d %-12d %d"
      % ("cue visible at the junction", opt_twin, n_twin, m_twin, len(win_twin)))

assert m_base == 2, "the aliased world should force two memory classes, got %r" % (m_base,)
assert m_twin == 1, "the disambiguated twin should need none, got %r" % (m_twin,)
assert 0 < len(win_base) < n_base, (
    "either no machine or every machine attains the optimum, so the "
    "enumeration decides nothing: %d of %d" % (len(win_base), n_base))
assert 0 < len(win_twin) < n_twin, (
    "the twin enumeration does not discriminate: %d of %d" % (len(win_twin), n_twin))

# the B13 quotient on the same world, for comparison: beliefs over the cue
beliefs = set()
for obs_seq, _c in BASE_EP:
    for k in range(len(obs_seq) + 1):
        pre = obs_seq[:k]
        if not pre:
            beliefs.add((F(1, 2), F(1, 2)))
        elif pre[0] == "cueL":
            beliefs.add((F(1), F(0)))
        else:
            beliefs.add((F(0), F(1)))
n_belief = len(beliefs)

OUT["policy_memory"] = {
    "optimal_return": opt_base, "machines_enumerated_base": n_base,
    "minimal_m_base": m_base, "optimal_machines_base": len(win_base),
    "machines_enumerated_twin": n_twin, "minimal_m_twin": m_twin,
    "optimal_machines_twin": len(win_twin),
    "belief_classes": n_belief, "action_classes": m_base,
}

assert n_belief > m_base, (
    "the control quotient is not coarser than the belief quotient (%d vs %d), "
    "so there is nothing control-specific here" % (n_belief, m_base))

print()
print("  The same world carries %d distinct beliefs about the cue but only %d"
      % (n_belief, m_base))
print("  memory classes are needed to ACT. The pre-cue history, whose belief is")
print("  (1/2, 1/2), merges with one of the post-cue classes because before the")
print("  cue no distinction is yet due. CSR-1 counts distinctions that must")
print("  STILL be made -- and for a controller the distinction is the action.")
print()
print("  > A policy's memory is not a summary of the past. It is exactly the")
print("  > partition of histories that different future actions force, which")
print("  > can be strictly coarser than knowing where you are.")


# ===========================================================================
print()
print(BAR)
print("2  VALUE AS RETAINED STATE, AND WHY IT IS NOT THE MINIMAL ONE")
print(BAR)
print("  A corridor. Walking on costs 1 a step; leaving at state i pays EXIT[i];")
print("  reaching the end pays 10. Two worlds with the SAME graph and the SAME")
print("  multiset of rewards -- only the placement of the exits differs.")
print()

N_ST = 5           # states 0..4; 4 is the end
END_PAY = 10
STEP = -1


def solve(exits):
    """Backward induction. V[i] is the exact optimal return from state i."""
    V = [None] * N_ST
    V[N_ST - 1] = END_PAY
    greedy = {}
    for i in range(N_ST - 2, -1, -1):
        walk = STEP + V[i + 1]
        leave = exits[i]
        if leave > walk:
            V[i], greedy[i] = leave, "g"
        else:
            V[i], greedy[i] = walk, "w"
    return V, greedy


def myopic_return(exits):
    """Act on immediate reward alone, then live with where that lands you."""
    i, total = 0, 0
    while i < N_ST - 1:
        if exits[i] > STEP:
            return total + exits[i]
        total += STEP
        i += 1
    return total + END_PAY


EX_A = (0, 1, 2, 12)          # the big exit is late: patience required
EX_B = (12, 1, 2, 0)          # the same exits, permuted: patience not required
assert sorted(EX_A) == sorted(EX_B), "the twin changes the reward multiset"
assert len(EX_A) == len(EX_B), "the twin changes the number of exits"

rows = []
for name, ex in (("big exit late", EX_A), ("big exit first", EX_B)):
    V, greedy = solve(ex)
    myo = myopic_return(ex)
    regret = V[0] - myo
    rows.append({"world": name, "exits": list(ex), "V": list(V),
                 "optimal": V[0], "myopic": myo, "regret": regret,
                 "distinct_V": len(set(V)),
                 "distinct_actions": len(set(greedy.values())),
                 "greedy": "".join(greedy[i] for i in sorted(greedy))})
print("  %-16s %-18s %-10s %-10s %-8s %s"
      % ("world", "V(0..4)", "optimal", "myopic", "regret", "greedy"))
for r in rows:
    print("  %-16s %-18s %-10d %-10d %-8d %s"
          % (r["world"], ",".join(str(v) for v in r["V"]), r["optimal"],
             r["myopic"], r["regret"], r["greedy"]))
OUT["value"] = rows

a, b = rows[0], rows[1]
assert a["regret"] > 0, "the myopic machine must actually lose somewhere"
assert b["regret"] == 0, (
    "the twin must be a world where immediate reward already decides, or the "
    "claim is untested against its own negative")
assert a["distinct_actions"] > 1, (
    "the greedy policy is constant, so its quotient is trivially coarse")
assert a["distinct_actions"] < a["distinct_V"], (
    "the action quotient is not strictly coarser than the value quotient "
    "(%d vs %d)" % (a["distinct_actions"], a["distinct_V"]))

print()
print("  The two worlds are the same graph with the same rewards permuted. In")
print("  one, acting on immediate reward loses %d; in the other it loses"
      % a["regret"])
print("  nothing. So a value function is not a modelling preference: it is")
print("  what is required exactly when the ordering of immediate rewards is")
print("  not the ordering of returns.")
print()
print("  But the value function is NOT the minimal retained state. V takes %d"
      % a["distinct_V"])
print("  distinct values across the corridor while the greedy policy takes %d."
      % a["distinct_actions"])
print("  CSR-1 counts distinctions that must still be made; for acting, that")
print("  is the action. The extra distinctions V carries are real -- they are")
print("  what lets it be RE-optimized -- but they are not paid for by acting.")
print()
print("  > Value is retained state under PVR-3, and a strictly finer state")
print("  > than the policy it induces. That gap is the whole reason compiling")
print("  > a policy is a separate machine and not a change of notation.")


# ===========================================================================
print()
print(BAR)
print("3  WHEN A SCALAR REWARD SIGNAL IS SUFFICIENT TO SPECIFY THE TASK")
print(BAR)
print("  One state, two actions, two steps. Four trajectories. A reward on")
print("  (state, action) is searched exhaustively over a rational grid, at")
print("  three discounts, for one that makes the TARGET uniquely optimal.")
print()

TRAJ = tuple(itertools.product(("a", "b"), repeat=2))
GRID = tuple(F(v) for v in range(-2, 3))
GAMMAS = (F(1), F(1, 2), F(1, 4))


def counts_stateless(t):
    return (sum(1 for x in t if x == "a"), sum(1 for x in t if x == "b"))


def ret_stateless(t, ra, rb, g):
    r = {"a": ra, "b": rb}
    return sum((g ** i) * r[x] for i, x in enumerate(t))


def ret_timed(t, r0a, r0b, r1a, r1b, g):
    tab = {(0, "a"): r0a, (0, "b"): r0b, (1, "a"): r1a, (1, "b"): r1b}
    return sum((g ** i) * tab[(i, x)] for i, x in enumerate(t))


def search_stateless(target):
    hits, total = 0, 0
    for ra in GRID:
        for rb in GRID:
            for g in GAMMAS:
                total += 1
                vals = dict((t, ret_stateless(t, ra, rb, g)) for t in TRAJ)
                best = max(vals.values())
                arg = [t for t in TRAJ if vals[t] == best]
                if arg == [target]:
                    hits += 1
    return hits, total


def search_timed(target):
    hits, total = 0, 0
    small = tuple(F(v) for v in range(-1, 2))
    for r0a in small:
        for r0b in small:
            for r1a in small:
                for r1b in small:
                    for g in GAMMAS:
                        total += 1
                        vals = dict((t, ret_timed(t, r0a, r0b, r1a, r1b, g))
                                    for t in TRAJ)
                        best = max(vals.values())
                        arg = [t for t in TRAJ if vals[t] == best]
                        if arg == [target]:
                            hits += 1
    return hits, total


T_ORDER = ("a", "b")        # "do a then b" -- an ordering requirement
T_PLAIN = ("a", "a")        # "do a twice"  -- a count requirement

cv = dict((t, counts_stateless(t)) for t in TRAJ)
assert cv[("a", "b")] == cv[("b", "a")], (
    "ab and ba do not share a visitation count vector, so the impossibility "
    "argument does not apply to this world")
assert cv[("a", "a")] != cv[("b", "b")], (
    "every trajectory has the same counts; the count vector distinguishes "
    "nothing and the test is vacuous")

rew = []
for label, target in (("do a then b", T_ORDER), ("do a twice", T_PLAIN)):
    h1, n1 = search_stateless(target)
    h2, n2 = search_timed(target)
    rew.append({"target": label, "trajectory": list(target),
                "state_only_hits": h1, "state_only_grid": n1,
                "time_indexed_hits": h2, "time_indexed_grid": n2,
                "counts": list(cv[target])})
    print("  %-16s %-14s %-24s %s"
          % (label, "counts=%s" % (cv[target],),
             "state-only: %d / %d" % (h1, n1),
             "state+step: %d / %d" % (h2, n2)))
OUT["reward_sufficiency"] = rew

order_row = rew[0]
plain_row = rew[1]
assert order_row["state_only_hits"] == 0, (
    "an ordering requirement was expressible over state-only reward, which "
    "contradicts the count-vector argument")
assert order_row["time_indexed_hits"] > 0, (
    "enlarging the state did not make the ordering expressible, so the repair "
    "claim is unsupported")
assert plain_row["state_only_hits"] > 0, (
    "the matched twin is not expressible either, so nothing is being "
    "discriminated")
assert plain_row["state_only_hits"] < plain_row["state_only_grid"], (
    "every reward in the grid makes the twin uniquely optimal; the search is "
    "not selective")

print()
print("  ab and ba visit the same (state, action) pairs the same number of")
print("  times, so EVERY additive reward on the state gives them the same")
print("  return -- at every discount. The grid search finds %d of %d. That is"
      % (order_row["state_only_hits"], order_row["state_only_grid"]))
print("  not a gap in the grid: it is a proof. With one state, the optimal")
print("  action sequence is constant, so no reward at any discount can demand")
print("  a change of action.")
print()
print("  Indexing the state by the step repairs it exactly: %d of %d reward"
      % (order_row["time_indexed_hits"], order_row["time_indexed_grid"]))
print("  tables then make 'a then b' the unique optimum, while the matched")
print("  twin 'a twice' was expressible in both.")
print()
print("  > A scalar reward is sufficient exactly when the task is a function of")
print("  > the visitation counts of the state the machine actually has. A task")
print("  > that is not is not badly specified -- the STATE is too small. That")
print("  > is CSR-1 again, arriving from the objective rather than the policy.")


# ===========================================================================
print()
print(BAR)
print("4  POLICY / VALUE / MODEL, AND THE CROSSOVER IN QUERIES-PER-GOAL")
print(BAR)

N_S, ACTS, HORIZON = 25, (0, 1), 2


def step(s, a):
    return (s * 2 + 1) % N_S if a == 0 else (s + 7) % N_S


def make_reward(seed):
    return dict(((s, a), (s * 3 + a * 5 + seed * 7) % 11)
                for s in range(N_S) for a in ACTS)


def plan(s, R):
    """Exhaustive depth-HORIZON lookahead. Returns (action, expansions)."""
    exp = [0]

    def rec(s, h):
        if h == 0:
            return 0
        best = None
        for a in ACTS:
            exp[0] += 1
            v = R[(s, a)] + rec(step(s, a), h - 1)
            if best is None or v > best:
                best = v
        return best

    best_a, best_v = None, None
    for a in ACTS:
        exp[0] += 1
        v = R[(s, a)] + rec(step(s, a), HORIZON - 1)
        if best_v is None or v > best_v:
            best_v, best_a = v, a
    return best_a, exp[0]


R0 = make_reward(0)
_, C = plan(0, R0)
P_ROWS = N_S                        # one action per state
Q_ROWS = N_S * len(ACTS)            # one number per state-action
M_ROWS = 2 * N_S * len(ACTS)        # transitions and rewards
U = 1
E_EXP = N_S * len(ACTS) * HORIZON   # environment steps to rebuild without a model

# the planner must actually be right, or none of the prices mean anything
bruteV = {}
for s in range(N_S):
    best = None
    for seq in itertools.product(ACTS, repeat=HORIZON):
        t, v = s, 0
        for a in seq:
            v += R0[(t, a)]
            t = step(t, a)
        if best is None or v > best[0]:
            best = (v, seq[0])
    bruteV[s] = best
for s in range(N_S):
    a, _ = plan(s, R0)
    assert R0[(s, a)] + max(R0[(step(s, a), a2)] for a2 in ACTS) == bruteV[s][0], \
        "the planner is not optimal at state %d, so its price is meaningless" % s

print("  world: %d states, %d actions, horizon %d. One planning query expands"
      % (N_S, len(ACTS), HORIZON))
print("  %d nodes; a policy is %d rows; a model is %d rows; rebuilding without"
      % (C, P_ROWS, M_ROWS))
print("  a model costs %d environment steps." % E_EXP)
print()
print("  Three machines, all model-based, over r queries spread round-robin")
print("  across the states:")
print()
print("    plan always   r*C")
print("    compile all   |S|*C + P + r*U")
print("    cache         (first visit) C+1, (later) U")
print()
print("  %-8s %-14s %-14s %-14s %s"
      % ("r", "plan always", "compile all", "cache", "cheapest"))
tri = []
for r in (1, 4, 10, 25, 31, 50, 100, 200):
    plan_c = r * C
    comp_c = N_S * C + P_ROWS + r * U
    cache_c = min(r, N_S) * (C + 1) + max(0, r - N_S) * U
    d = {"plan always": plan_c, "compile all": comp_c, "cache": cache_c}
    best = min(d, key=lambda k: d[k])
    tri.append({"r": r, "plan": plan_c, "compile": comp_c, "cache": cache_c,
                "cheapest": best})
    print("  %-8d %-14d %-14d %-14d %s" % (r, plan_c, comp_c, cache_c, best))
OUT["trichotomy"] = tri

kinds = set(t["cheapest"] for t in tri)
assert "plan always" in kinds and "cache" in kinds, (
    "no crossover between planning and caching: %s" % sorted(kinds))
assert "compile all" not in kinds, (
    "compiling the whole table won somewhere; the dominance claim is false")
assert all(t["cache"] <= t["compile"] for t in tri), "cache does not dominate"
assert any(t["cache"] < t["compile"] for t in tri), (
    "cache and compile are identical everywhere, so the comparison is empty")

# the two crossovers are different numbers and were conflated in a first
# version: r=31 is where caching overtakes planning, r=36 is where the
# all-or-nothing compiled table does.
def _first_r(better):
    for r in range(1, 500):
        plan_c = r * C
        comp_c = N_S * C + P_ROWS + r * U
        cache_c = min(r, N_S) * (C + 1) + max(0, r - N_S) * U
        if better(plan_c, comp_c, cache_c):
            return r
    return None


X_CACHE = _first_r(lambda p, k, c: c < p)
X_COMPILE = _first_r(lambda p, k, c: k < p)
assert X_CACHE is not None and X_COMPILE is not None, "no crossover found"
assert X_CACHE < X_COMPILE, (
    "caching does not bring the crossover forward (%r against %r), so it is "
    "not buying anything over all-or-nothing compilation" % (X_CACHE, X_COMPILE))
OUT["crossovers"] = {"plan_vs_cache": X_CACHE, "plan_vs_compile": X_COMPILE}

print()
print("  Compiling the whole table never wins. It pays for %d rows and %d"
      % (P_ROWS, N_S * C))
print("  expansions before knowing which states will be asked, while caching")
print("  builds exactly the rows it is asked for. PVR-3 applied PER KEY says a")
print("  row is worth keeping as soon as it is asked twice -- 1 < (r-1)(%d-%d)"
      % (C, U))
print("  holds from r=2 -- and caching is the machine that obeys that rule key")
print("  by key.")
print()
print("  Two different crossovers, which a first version of this section ran")
print("  together: planning gives way to CACHING at r=%d, and to the" % X_CACHE)
print("  all-or-nothing COMPILED TABLE only at r=%d. That %d-query gap is the"
      % (X_COMPILE, X_COMPILE - X_CACHE))
print("  cost of forbidding the intermediate shape B16 left unevaluated.")
print()
print("  Now the model-free arm: it holds no model, so on a goal change it")
print("  cannot re-plan and must re-acquire from the environment.")
print()
print("    model-based  M + g*cache(r)")
print("    model-free   P + g*(E + r*U)")
print()
print("  %-8s %-16s %-16s %-16s %s"
      % ("goals g", "flip at r =", "model-based", "model-free", "at the flip"))
mf = []
for g in (1, 64, 256):
    flip = None
    for r in range(1, 61):
        mb = M_ROWS + g * (min(r, N_S) * (C + 1) + max(0, r - N_S) * U)
        fr = P_ROWS + g * (E_EXP + r * U)
        if fr < mb:
            flip = r
            break
    r = flip
    mb = M_ROWS + g * (min(r, N_S) * (C + 1) + max(0, r - N_S) * U)
    fr = P_ROWS + g * (E_EXP + r * U)
    mf.append({"g": g, "flip_r": flip, "model_based": mb, "model_free": fr})
    print("  %-8d %-16d %-16d %-16d %s" % (g, flip, mb, fr, "model-free wins"))
OUT["model_based_vs_free"] = mf

by_g = dict((x["g"], x["flip_r"]) for x in mf)
assert by_g[64] == by_g[256], (
    "the crossover is not stable in the number of goals (%r vs %r), so it is "
    "not a queries-per-goal law" % (by_g[64], by_g[256]))
assert by_g[1] != by_g[64], (
    "the crossover is identical at g=1 and g=64, so the model's fixed charge "
    "is doing no work and it was effectively given away free")
assert all(x["flip_r"] is not None for x in mf), "no flip found in range"

print()
print("  The flip sits at r=%d for both g=%d and g=%d, and at r=%d for a single"
      % (by_g[64], 64, 256, by_g[1]))
print("  goal. The model's %d rows are a fixed charge: they wash out as M/g, so"
      % M_ROWS)
print("  the asymptotic crossover is a statement about QUERIES PER GOAL and not")
print("  about the length of the machine's life.")
print()
print("  > Model-based is correct when the ecology changes what it wants faster")
print("  > than it repeats what it asks. Model-free is correct when it repeats")
print("  > what it asks faster than it changes what it wants. That is the same")
print("  > break-even as B16 with the reuse count read per goal.")
print()
print("  The third arm of the trichotomy separates on the kind of query, not")
print("  the count. A policy cannot answer 'how good would b have been?'; it")
print("  must re-plan. A value table answers in one read but costs %d rows."
      % Q_ROWS)
print()
print("  %-14s %-16s %-16s %s" % ("eval queries", "policy", "value table", "cheaper"))
qm = []
N_ACT_Q = 64
for ne in (0, 4, 17, 18, 40):
    pol = P_ROWS + N_ACT_Q * U + ne * C
    val = Q_ROWS + N_ACT_Q * len(ACTS) + ne * U
    ch = "policy" if pol < val else ("value" if val < pol else "tie")
    qm.append({"eval_queries": ne, "policy": pol, "value": val, "cheaper": ch})
    print("  %-14d %-16d %-16d %s" % (ne, pol, val, ch))
OUT["policy_vs_value"] = qm
qk = set(x["cheaper"] for x in qm)
assert "policy" in qk and "value" in qk, (
    "one of policy/value wins at every evaluative-query count, so the "
    "trichotomy's third arm is not separated: %s" % sorted(qk))


# ===========================================================================
print()
print(BAR)
print("5  ON-POLICY VERSUS OFF-POLICY IS A REUSE QUESTION, GATED BY COVERAGE")
print(BAR)
print("  Two start states, two actions, deterministic payoffs. A batch of four")
print("  logged transitions is reused to evaluate a target policy. Two batches")
print("  of the SAME size differ only in which pair they happened to log.")
print()

RW = {("x", "a"): F(3), ("x", "b"): F(1), ("y", "a"): F(0), ("y", "b"): F(4)}
PI = {"x": "a", "y": "b"}
TRUE_V = sum(RW[(s, PI[s])] for s in ("x", "y")) / 2

BATCH_COV = (("x", "a"), ("x", "b"), ("y", "a"), ("y", "b"))
BATCH_GAP = (("x", "a"), ("x", "b"), ("y", "a"), ("y", "a"))
BATCH_FIX = (("x", "a"), ("x", "b"), ("y", "a"), ("y", "b"))
assert len(BATCH_COV) == len(BATCH_GAP), "the twin batches differ in size"
assert sorted(set(BATCH_COV)) != sorted(set(BATCH_GAP)), "the batches cover the same pairs"


def off_policy_value(batch):
    seen = dict((k, RW[k]) for k in batch)
    return sum(seen.get((s, PI[s]), F(0)) for s in ("x", "y")) / 2


print("  %-22s %-14s %-14s %-14s %s"
      % ("batch", "size", "covers pi", "estimate", "error"))
cov = []
for name, b in (("covering", BATCH_COV), ("one pair missing", BATCH_GAP),
                ("missing pair added", BATCH_FIX)):
    covers = all((s, PI[s]) in set(b) for s in ("x", "y"))
    est = off_policy_value(b)
    cov.append({"batch": name, "size": len(b), "covers": covers,
                "estimate": str(est), "error": str(TRUE_V - est)})
    print("  %-22s %-14d %-14s %-14s %s"
          % (name, len(b), covers, est, TRUE_V - est))
OUT["coverage"] = {"true_value": str(TRUE_V), "rows": cov}

assert cov[0]["error"] == "0", "the covering batch does not reproduce the truth"
assert cov[1]["error"] != "0", "the gapped batch is somehow exact"
assert cov[2]["error"] == "0", (
    "adding the missing pair does not repair the estimate, so the error was "
    "not caused by coverage")
assert cov[0]["covers"] and not cov[1]["covers"], "coverage flag is not tracking"

print()
print("  The gapped batch is wrong by exactly %s, and adding the single missing"
      % cov[1]["error"])
print("  pair repairs it to zero. Off-policy reuse is not an approximation with")
print("  a variance: on the support it is EXACT, and off the support it is")
print("  uninformed. Coverage is the whole of the legality condition.")
print()
print("  Where reuse is legal it is priced by PVR-3. Storing the batch costs S")
print("  transitions; a fresh on-policy evaluation costs %d rollouts at W"
      % 2)
print("  environment steps each; a read costs %d." % 2)
print()
print("  break-even is the smallest r with  S + C + (r-1)U < r*C,  PVR-3's own")
print("  form, scanned rather than solved.")
print()
print("  %-14s %-14s %-14s %-16s %s"
      % ("W (env step)", "C", "U", "break-even r", "reuse ever pays"))
pr = []
S_BATCH = len(BATCH_COV)
for w in (1, 2, 5, 10):
    C5, U5 = 2 * w, 2
    # scanned, not solved in closed form: a first version used an arithmetic
    # expression for the smallest r and printed 3 where the ledger says 4.
    be = None
    for r in range(1, 400):
        if S_BATCH + C5 + (r - 1) * U5 < r * C5:
            be = r
            break
    if be is not None:
        assert S_BATCH < (be - 1) * (C5 - U5), "break-even fails PVR-3 at r"
        assert not (S_BATCH < (be - 2) * (C5 - U5)), "break-even is not the smallest r"
    pr.append({"w": w, "C": C5, "U": U5, "break_even_r": be,
               "pays": be is not None})
    print("  %-14d %-14d %-14d %-16s %s"
          % (w, C5, U5, "never" if be is None else be, be is not None))
OUT["reuse_price"] = pr
ps = set(x["pays"] for x in pr)
assert True in ps and False in ps, (
    "off-policy reuse either always pays or never pays across the sweep, so "
    "the price is not being tested: %s" % sorted(ps))

print()
print("  > On-policy is not a safer method. It is the machine that regenerates")
print("  > because regeneration is cheap or because the batch does not cover")
print("  > what it now needs to know. Both are PVR-3 conditions, one on price")
print("  > and one on legality.")


# ===========================================================================
print()
print(BAR)
print("6  EXPLORATION PRESSURE, BY ENUMERATION OF ADAPTIVE MACHINES")
print(BAR)
print("  Two arms with fixed unknown payoffs, four possible worlds, four pulls.")
print("  A machine is a decision tree over the payoffs it has observed: 15")
print("  nodes, 2 arms each, 32768 machines. Every one is run in every world.")
print()

H6 = 4
WORLDS6 = ((1, 1), (1, 3), (3, 1), (3, 3))
N_NODES = 2 ** H6 - 1
N_MACH = 2 ** N_NODES


def run_tree(mach, world):
    """Total payoff, and the arm sequence, for one machine in one world."""
    pos, total, seq = 0, 0, []
    for d in range(H6):
        idx = (2 ** d - 1) + pos
        arm = (mach >> idx) & 1
        pay = world[arm]
        total += pay
        seq.append(arm)
        pos = pos * 2 + (0 if pay == 1 else 1)
    return total, tuple(seq)


OPT6 = dict((w, H6 * max(w)) for w in WORLDS6)
best_total, minimizers = None, []
for mach in range(N_MACH):
    tot = 0
    for w in WORLDS6:
        got, _ = run_tree(mach, w)
        tot += OPT6[w] - got
    if best_total is None or tot < best_total:
        best_total, minimizers = tot, [mach]
    elif tot == best_total:
        minimizers.append(mach)

CONST = (0, N_MACH - 1)
const_scores = []
for mach in CONST:
    tot = sum(OPT6[w] - run_tree(mach, w)[0] for w in WORLDS6)
    const_scores.append(tot)
best_const = min(const_scores)

# Does every minimizer actually change arm where it MATTERS? Switching inside a
# world whose two arms pay the same is free and proves nothing, so the test is
# restricted to the worlds where the arms differ. (A first version allowed any
# world; it passed on machines that only ever switched inside (1,1) and (3,3).)
SPLIT6 = tuple(w for w in WORLDS6 if w[0] != w[1])
TIED6 = tuple(w for w in WORLDS6 if w[0] == w[1])
assert SPLIT6 and TIED6, "the world set must contain both tied and split arms"

adaptive, adaptive_tied_only = [], []
for mach in minimizers:
    split = any(len(set(run_tree(mach, w)[1])) > 1 for w in SPLIT6)
    tied = any(len(set(run_tree(mach, w)[1])) > 1 for w in TIED6)
    adaptive.append(split)
    adaptive_tied_only.append(tied and not split)

print("  %-26s %s" % ("machines enumerated", N_MACH))
print("  %-26s %s" % ("minimum total regret", best_total))
print("  %-26s %s" % ("machines attaining it", len(minimizers)))
print("  %-26s %s" % ("best constant-arm machine", best_const))
print()
ex = minimizers[0]
print("  %-14s %-12s %-12s %-12s %s"
      % ("world", "optimal", "machine", "regret", "arms pulled"))
ex_rows = []
for w in WORLDS6:
    got, seq = run_tree(ex, w)
    ex_rows.append({"world": list(w), "optimal": OPT6[w], "got": got,
                    "regret": OPT6[w] - got, "arms": list(seq)})
    print("  %-14s %-12d %-12d %-12d %s"
          % ("(%d,%d)" % w, OPT6[w], got, OPT6[w] - got, "".join(str(x) for x in seq)))

OUT["exploration"] = {
    "machines": N_MACH, "min_total_regret": best_total,
    "n_minimizers": len(minimizers), "best_constant": best_const,
    "all_minimizers_adaptive": all(adaptive),
    "minimizers_switching_only_where_free": sum(adaptive_tied_only),
    "split_worlds": [list(w) for w in SPLIT6],
    "example": ex_rows,
}

assert best_total > 0, (
    "a machine achieves zero regret in every world, so nothing was ever "
    "unknown and there is no exploration pressure to derive")
assert 0 < len(minimizers) < N_MACH, (
    "either no machine or every machine is optimal: %d of %d"
    % (len(minimizers), N_MACH))
assert best_const > best_total, (
    "a constant-arm machine matches the optimum (%d vs %d), so adaptivity "
    "buys nothing here" % (best_const, best_total))
assert all(adaptive), (
    "some minimizing machine never changes arm in a world where the arms "
    "differ, so the minimum is not evidence of exploration")
assert sum(adaptive_tied_only) == 0, (
    "%d minimizers switch arm only inside the tied worlds, where switching is "
    "free; the adaptivity gate is being satisfied for nothing"
    % sum(adaptive_tied_only))

# where does the optimum actually pin behaviour down?
split_profiles = set(tuple(run_tree(m, w)[1] for w in SPLIT6) for m in minimizers)
tied_profiles = set(tuple(run_tree(m, w)[1] for w in TIED6) for m in minimizers)
OUT["exploration"]["distinct_behaviour_split_worlds"] = len(split_profiles)
OUT["exploration"]["distinct_behaviour_tied_worlds"] = len(tied_profiles)
assert len(split_profiles) < len(tied_profiles), (
    "the minimum constrains behaviour no more tightly where the arms differ "
    "(%d profiles) than where they tie (%d), so it is not the payoff gap doing "
    "the constraining" % (len(split_profiles), len(tied_profiles)))

print()
print("  No machine reaches zero: the first pull is taken blind, so a world")
print("  whose better arm is the other one has already lost %d before anything"
      % best_total)
print("  is known. The best constant-arm machine loses %d. Every one of the %d"
      % (best_const, len(minimizers)))
print("  minimizers changes arm in a world where the arms DIFFER, and none of")
print("  them gets there by switching only where switching is free.")
print()
print("  The %d minimizers show only %d distinct behaviours across the two"
      % (len(minimizers), len(split_profiles)))
print("  worlds whose arms differ, against %d across the two where they tie."
      % len(tied_profiles))
print("  The optimum pins the machine down exactly where the choice is paid")
print("  for and leaves it free everywhere else -- CSR-1 read off an objective.")
print()
print("  The matched twin: same worlds, same horizon, same four decisions, same")
print("  payoffs -- the arms are announced BEFORE the first pull instead of")
print("  after. Machines are maps from the announced world to an arm sequence.")
print()

N_MACH_T = (2 ** H6) ** len(WORLDS6)
best_twin, best_split, best_tied = None, None, None
for mach in range(N_MACH_T):
    tot, ex_split, ex_tied = 0, False, False
    for wi, w in enumerate(WORLDS6):
        seq = [(mach >> (wi * H6 + k)) & 1 for k in range(H6)]
        tot += OPT6[w] - sum(w[a] for a in seq)
        if len(set(seq)) > 1:
            if w[0] != w[1]:
                ex_split = True
            else:
                ex_tied = True
    if best_twin is None or tot < best_twin:
        best_twin = tot
    if ex_split and (best_split is None or tot < best_split):
        best_split = tot
    if ex_tied and not ex_split and (best_tied is None or tot < best_tied):
        best_tied = tot

print("  %-40s %s" % ("machines enumerated (twin)", N_MACH_T))
print("  %-40s %s" % ("minimum total regret (twin)", best_twin))
print("  %-40s %s" % ("best that pulls both where arms DIFFER", best_split))
print("  %-40s %s" % ("best that pulls both only where arms TIE", best_tied))
OUT["exploration_twin"] = {
    "machines": N_MACH_T, "min_total_regret": best_twin,
    "min_regret_if_explores_split": best_split,
    "min_regret_if_explores_tied_only": best_tied,
}
assert best_twin == 0, (
    "even with the payoffs announced the twin cannot reach zero regret, so it "
    "is not a matched negative: got %r" % (best_twin,))
assert best_split > best_twin, (
    "spending a pull on the other arm costs nothing when the answer is "
    "already known, so exploration is not being shown to have a price")
assert best_tied == best_twin, (
    "switching between two arms that pay the same is not free (%r against "
    "%r), which would mean the price is not coming from the payoff gap"
    % (best_tied, best_twin))

print()
print("  With the answer announced, zero regret is reachable and any machine")
print("  that still pulls both arms where they DIFFER loses %d. But switching"
      % best_split)
print("  between two arms that pay the same costs %d -- exploration's price is"
      % best_tied)
print("  exactly the payoff gap it gives up, and is zero where there is none.")
print("  (A first version of this gate counted any switch as exploring; it")
print("  passed on machines that only ever switched inside the tied worlds.)")
print()
print("  > Exploration pressure is exactly the residual uncertainty about which")
print("  > action is best, valued at what acting on the wrong one costs. It")
print("  > vanishes -- and becomes strictly harmful -- the moment observation")
print("  > already identifies the optimum.")


# ===========================================================================
print()
print(BAR)
print("7  HIERARCHY: AN OPTION IS EARNED WHEN A SUBTRAJECTORY RECURS")
print(BAR)
print("  Four tasks as primitive action strings. Flat cost is one unit per")
print("  stored symbol. An option stores its body once and each use becomes a")
print("  single symbol. The best option is SEARCHED for, not declared.")
print()

TASKS_REC = ("ABXYZC", "DXYZEF", "GHXYZ", "XYZIJ")
TASKS_TWIN = ("ABCDEF", "GHIJKL", "MNOPQ", "RSTUV")


def best_option(tasks):
    """Every contiguous substring of length >= 2 that occurs at least twice,
    priced. Returns (body, occurrences, flat, hier) for the cheapest."""
    flat = sum(len(t) for t in tasks)
    cands = set()
    for t in tasks:
        for i in range(len(t)):
            for j in range(i + 2, len(t) + 1):
                cands.add(t[i:j])
    best = None
    for body in sorted(cands):
        occ = sum(t.count(body) for t in tasks)
        if occ < 1:
            continue
        hier = len(body) + sum(len(t) - occ_t * (len(body) - 1)
                               for t, occ_t in ((t, t.count(body)) for t in tasks))
        if best is None or hier < best[3] or (hier == best[3] and body < best[0]):
            best = (body, occ, flat, hier)
    return best


def repeats_exist(tasks):
    for t in tasks:
        for i in range(len(t)):
            for j in range(i + 2, len(t) + 1):
                sub = t[i:j]
                if sum(x.count(sub) for x in tasks) > 1:
                    return True
    return False


assert [len(t) for t in TASKS_REC] == [len(t) for t in TASKS_TWIN], \
    "the twin task set has different task lengths"
assert sum(len(t) for t in TASKS_REC) == sum(len(t) for t in TASKS_TWIN), \
    "the twin task set has a different flat cost"
assert repeats_exist(TASKS_REC), "the recurring task set has no repeated substring"
assert not repeats_exist(TASKS_TWIN), (
    "the twin task set contains a repeated substring of length >= 2, so it is "
    "not a matched non-recurring negative")

print("  %-14s %-10s %-12s %-10s %-10s %s"
      % ("task set", "option", "occurrences", "flat", "hier", "margin"))
opt = []
for name, tasks in (("recurring", TASKS_REC), ("no recurrence", TASKS_TWIN)):
    body, occ, flat, hier = best_option(tasks)
    opt.append({"tasks": name, "option": body, "occurrences": occ,
                "flat": flat, "hier": hier, "margin": flat - hier})
    print("  %-14s %-10s %-12d %-10d %-10d %+d"
          % (name, body, occ, flat, hier, flat - hier))
OUT["options"] = opt

assert opt[0]["margin"] > 0, "the option does not pay even where it recurs"
assert opt[1]["margin"] < 0, (
    "the best option found in the non-recurring twin still pays, so recurrence "
    "is not what is buying the hierarchy")
assert opt[1]["margin"] == -1, (
    "the non-recurring margin is %d, not the -1 that a single use of a body of "
    "length L predicts" % opt[1]["margin"])

L_OPT = len(opt[0]["option"])
L_TWIN = len(opt[1]["option"])
print()
print("  The option is found by enumeration, and in the non-recurring twin the")
print("  best one found still LOSES, by exactly 1. A body of length L used ONCE")
print("  costs L to store and saves L-1 write-outs, so it loses one symbol")
print("  whatever L is -- here the winner has L=%d against the recurring set's"
      % L_TWIN)
print("  L=%d, and the margin is -1 either way." % L_OPT)
print()
print("  The break-even as a function of how often the body recurs. The stored")
print("  body IS the one construction here, so the ledger is S + rU < rC with")
print("  S = C = %d and U = 1, i.e. S < r(C-U) -- not PVR-3's (r-1) form, which"
      % L_OPT)
print("  would charge a second write-out that is never made.")
print()
print("  %-10s %-14s %-14s %s" % ("uses r", "write out r*L", "store + r refs", "saving"))
br = []
for r in (1, 2, 3, 4):
    out_c, keep_c = r * L_OPT, L_OPT + r
    br.append({"r": r, "writeout": out_c, "keep": keep_c, "saving": out_c - keep_c})
    print("  %-10d %-14d %-14d %+d" % (r, out_c, keep_c, out_c - keep_c))
OUT["option_break_even"] = {"L": L_OPT, "rows": br,
                            "break_even_r": next(x["r"] for x in br if x["saving"] > 0)}
sv = [x["saving"] > 0 for x in br]
assert any(sv) and not all(sv), (
    "the option pays at every reuse count or at none, so no break-even is "
    "being derived")

print()
print("  > A skill is not an abstraction the designer supplies. It is retained")
print("  > structure under PVR-3 whose keep is earned by the recurrence of a")
print("  > subtrajectory, and a task set whose subtrajectories do not recur")
print("  > makes hierarchy strictly more expensive than being flat.")


# ===========================================================================
print()
print(BAR)
print("8  NEUTRAL RECOVERY: MACHINES ENUMERATED WITH NO CONTROL VOCABULARY")
print(BAR)
print("  Nothing below names a policy, a value, a model, a plan or an option. A")
print("  candidate is: m memory classes, a class-update table, an action table,")
print("  and a SUBSET K of its own (class, observation) keys that it holds as")
print("  rows. A key not held is recomputed on every visit at cost W.")
print()
print("    cost(K) = ROW*|K| + r * W * (visits to keys not in K)")
print()


def machine_signatures(episodes, obs_alphabet, m_max=2):
    """Every optimal machine, reduced to what pricing can see: its reachable
    (class, observation) keys and how often each is visited."""
    obs_index = dict((o, i) for i, o in enumerate(obs_alphabet))
    no = len(obs_alphabet)
    optimal = len(episodes)
    sigs = set()
    for m in range(1, m_max + 1):
        n = m * no
        for act in itertools.product(ACT, repeat=n):
            for upd in itertools.product(range(m), repeat=n):
                if run_machine(m, upd, act, episodes, obs_index) != optimal:
                    continue
                visits = {}
                for obs_seq, _c in episodes:
                    c = 0
                    for o in obs_seq:
                        oi = obs_index[o]
                        visits[(c, oi)] = visits.get((c, oi), 0) + 1
                        c = upd[c * no + oi]
                sigs.add(tuple(sorted(visits.items())))
        if sigs:
            break
    return sigs


def cheapest_shape(sigs, row_price, r, w=1):
    """Enumerate every subset of every optimal machine's keys. Return the
    cheapest, its size, and how many keys that machine had."""
    best = None
    for sig in sigs:
        keys = [k for k, _v in sig]
        vis = dict(sig)
        n = len(keys)
        for mask in range(2 ** n):
            held = [keys[i] for i in range(n) if (mask >> i) & 1]
            hs = set(held)
            cost = row_price * len(held) + r * w * sum(
                vis[k] for k in keys if k not in hs)
            cand = (cost, len(held), n)
            if best is None or cand < best:
                best = cand
    return best


ALIASED_OBS = ("cueL", "cueR", "corr", "junc")
ALIASED_EP = BASE_EP
UNIFORM_OBS = ("cueL", "cueR", "c1", "c2", "c3", "junc")
UNIFORM_EP = ((("cueL", "c1", "c2", "c3", "junc"), 0),
              (("cueR", "c1", "c2", "c3", "junc"), 1))

assert [len(e[0]) for e in ALIASED_EP] == [len(e[0]) for e in UNIFORM_EP], \
    "the uniform-visit twin has different episode lengths"
assert [e[1] for e in ALIASED_EP] == [e[1] for e in UNIFORM_EP], \
    "the uniform-visit twin has different correct actions"

SIG_A = machine_signatures(ALIASED_EP, ALIASED_OBS)
SIG_U = machine_signatures(UNIFORM_EP, UNIFORM_OBS)
vis_a = sorted(set(v for sig in SIG_A for _k, v in sig))
vis_u = sorted(set(v for sig in SIG_U for _k, v in sig))
assert len(vis_a) > 1, "the aliased world does not have varying visit counts"
assert len(vis_u) == 1, (
    "the twin's visit counts are not uniform (%r), so it is not a matched "
    "negative for the partial-holding claim" % (vis_u,))

print("  aliased corridor:  optimal-machine key profiles %d, visit counts %s"
      % (len(SIG_A), vis_a))
print("  distinct corridor: optimal-machine key profiles %d, visit counts %s"
      % (len(SIG_U), vis_u))
print()
print("  %-10s %-8s %-16s %-16s %s"
      % ("ROW", "r", "cheapest cost", "keys held", "reads as"))
rec = []
for row_price in (1, 2, 4, 8):
    for r in (1, 2, 3, 5, 8, 16):
        cost, held, n = cheapest_shape(SIG_A, row_price, r)
        if held == 0:
            reads = "holds nothing, recomputes"
        elif held == n:
            reads = "holds every decision"
        else:
            reads = "holds %d of %d decisions" % (held, n)
        rec.append({"row": row_price, "r": r, "cost": cost, "held": held,
                    "keys": n, "reads_as": reads})
        if row_price == 4:
            print("  %-10d %-8d %-16d %-16s %s" % (row_price, r, cost, "%d/%d" % (held, n), reads))
OUT["recovery"] = rec

shapes = set()
for x in rec:
    shapes.add("none" if x["held"] == 0 else
               ("all" if x["held"] == x["keys"] else "partial"))
assert shapes == set(["none", "partial", "all"]), (
    "the enumeration recovers only %s; if one shape wins everywhere nothing "
    "has been recovered" % sorted(shapes))

low = [x for x in rec if x["r"] == 1 and x["row"] == 4][0]
high = [x for x in rec if x["r"] == 16 and x["row"] == 4][0]
assert low["held"] == 0, (
    "the full table wins at the lowest reuse; the obvious answer is winning "
    "everywhere and the search is rigged")
assert high["held"] == high["keys"], (
    "holding nothing still wins at the highest reuse, so the crossover is not "
    "being found")

partial_rows = [x for x in rec if 0 < x["held"] < x["keys"]]
assert partial_rows, "no strictly intermediate machine ever wins"
rows_with_partial = sorted(set(x["row"] for x in partial_rows))
assert len(rows_with_partial) == 4, (
    "the intermediate regime exists only at some row prices (%r), so it is an "
    "artifact of one number rather than of the visit profile" % rows_with_partial)

twin_partial = []
for row_price in (1, 2, 4, 8):
    for r in (1, 2, 3, 5, 8, 16):
        cost, held, n = cheapest_shape(SIG_U, row_price, r)
        if 0 < held < n:
            twin_partial.append((row_price, r, held, n))
OUT["recovery_twin"] = {"partial_wins": len(twin_partial),
                        "visit_counts": vis_u}
assert not twin_partial, (
    "an intermediate machine wins in the uniform-visit twin (%r), so partial "
    "holding is not caused by uneven visits" % (twin_partial[:3],))

print()
n_subsets = sum(2 ** len(sig) for sig in SIG_A)
print()
print("  holdings that win strictly between the two extremes (ROW, r, held/keys):")
print("    %s" % ", ".join("(%d, %d, %d/%d)" % (x["row"], x["r"], x["held"], x["keys"])
                           for x in partial_rows))
print()
print("  The %d optimal machines of section 1 reduce to %d distinct visit"
      % (len(win_base), len(SIG_A)))
print("  profile(s) -- everything pricing can see about them -- and over those,")
print("  %d holdings were enumerated. Three shapes come out of it, and none of"
      % n_subsets)
print("  them was named. At low reuse the cheapest machine holds")
print("  nothing and recomputes -- that reads as a planner. At high reuse it")
print("  holds every decision -- that reads as a compiled policy. In between it")
print("  holds the keys it visits OFTEN and recomputes the rest, which is the")
print("  partial-compilation shape B16 listed as legal and did not evaluate.")
print()
print("  The intermediate regime appears at every row price tested, and NEVER")
print("  appears in the matched twin where the corridor observations are")
print("  distinct and every key is visited exactly once. Partial holding is not")
print("  a tuning artifact: it is what uneven visitation buys.")
print()
print("  > A controller is not chosen from a menu of families. Hold a decision")
print("  > when PVR-3 says its own visit count earns the row, recompute it")
print("  > otherwise, and the three families are what the resulting machine")
print("  > looks like from outside in three different ecologies.")


# ===========================================================================
print()
print(BAR)
print("SCOPE AND FALSIFIERS")
print(BAR)
print("  - Section 1 enumerates machines only up to m=2, which is enough to")
print("    show 1 fails and 2 suffices. A world needing 3 was not searched.")
print("  - Section 2's action/value quotient gap is a row count on one")
print("    corridor, not a theorem about all MDPs.")
print("  - Section 3's impossibility is a proof (equal count vectors, and a")
print("    constant optimal sequence under one state); the grid only confirms")
print("    it. The repair is exhibited on a grid and is existential.")
print("  - Section 4 charges a planning query at exhaustive depth-2 expansion")
print("    and a row at 1. Other prices move the crossovers; the SHAPE, and")
print("    the dominance of caching over whole-table compilation, do not.")
print("  - Section 5's off-policy estimator substitutes 0 off support. Any")
print("    other default changes the size of the error, not its existence.")
print("  - Section 6 has deterministic payoffs, so one pull identifies an arm")
print("    exactly. Noisy payoffs would add a statistical term the exact")
print("    method here cannot carry.")
print("  - Section 7 prices one option. Nested options and overlapping bodies")
print("    are legal in the ledger and were not searched.")
print("  - Section 8 conditions its subset enumeration on machines that are")
print("    already optimal, so it prices WHAT TO HOLD, not what to do.")
print()
print("  Falsifier. Exhibit a control world where holding every decision is")
print("  cheaper than holding the frequently-visited ones at every reuse count")
print("  with uneven visitation; or a task that is not a function of the")
print("  machine's state visitation counts and is still the unique optimum of")
print("  some additive reward on that state.")

print()
print(BAR)
print("all assertions held")
print(BAR)

with open("microscopes/results/STAGE_CONTROL_FAMILY_V1.json", "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
