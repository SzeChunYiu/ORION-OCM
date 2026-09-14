"""I7 remainder: belief vs goal, action prediction, regime, deception.

Four boxes left open by social_cognition_witness.py. Each is settled by exact
enumeration over Fractions -- no sampling, no floating point in any claim.

  D1  hidden BELIEF inference as something other than hidden-goal inference
  D2  intention / action prediction
  D3  cooperation-versus-competition regimes
  D4  strategic deception and its detection

Every part carries a non-vacuity gate: a region where the machinery pays and a
region where it does not. A part that fires everywhere proves nothing.
"""

from fractions import Fraction as F
import itertools, json, sys

OUT = {}


def hdr(t):
    print("\n" + "=" * 70)
    print(t)
    print("=" * 70)


# ----------------------------------------------------------------------------
# D1. Belief is not a relabelling of goal.
#
# Partner has a goal and an observation channel. It acts on where it BELIEVES
# the object is. We must predict its action (to meet it, intercept it, help it).
# Question: can a goal-only model -- any function from goals to actions -- fit?
# ----------------------------------------------------------------------------

LOCS = ["L1", "L2"]


def partner_action(goal, saw_move):
    """Goal 'fetch' -> go to believed location. Goal 'avoid' -> the other one.

    The object STARTS at L1 and MOVES to L2. A partner that missed the move
    still believes L1. Belief is a function of the observation channel;
    the goal is not.
    """
    believed = "L2" if saw_move else "L1"
    if goal == "fetch":
        return believed
    return "L1" if believed == "L2" else "L2"


def d1_goal_only_fits(channel_varies):
    """Is there ANY function goals->actions consistent with the observations?

    Enumerate every candidate goal-only model and test it against the data.
    This is an exclusion by exhaustion, not an appeal to a definition.
    """
    goals = ["fetch", "avoid"]
    obs_settings = [True, False] if channel_varies else [True]
    data = [((g, o), partner_action(g, o)) for g in goals for o in obs_settings]
    for assign in itertools.product(LOCS, repeat=len(goals)):
        phi = dict(zip(goals, assign))
        if all(phi[g] == act for (g, _o), act in data):
            return True, phi, data
    return False, None, data


hdr("D1  hidden belief is not hidden goal")

print("\n  (a) partner's information CAN differ from ours (channel varies)")
fits_var, phi_var, data_var = d1_goal_only_fits(True)
for (g, o), a in data_var:
    print("      goal=%-6s saw_move=%-5s -> acts %s" % (g, o, a))
print("      a goal-only model fits: %s" % fits_var)

print("\n  (b) partner always sees what we see (channel constant)")
fits_con, phi_con, data_con = d1_goal_only_fits(False)
for (g, o), a in data_con:
    print("      goal=%-6s saw_move=%-5s -> acts %s" % (g, o, a))
print("      a goal-only model fits: %s   (witness %s)" % (fits_con, phi_con))

assert fits_var is False, "D1 vacuous: goal-only model was never excluded"
assert fits_con is True, "D1 vacuous: goal-only model never sufficed"

# Now price it. Stake S paid for a correct prediction of the partner's action.
STAKE = F(1)
BELIEF_MODEL_COST = F(1, 5)


def d1_value(p_saw):
    """Exact expected score of each model when the partner saw the move with
    probability p_saw. Goal is known; only the belief varies."""
    goal = "fetch"
    # goal-only model must commit to ONE location for this goal.
    best_goal_only = max(
        LOCS,
        key=lambda guess: sum(
            (p_saw if o else 1 - p_saw) * (STAKE if partner_action(goal, o) == guess else 0)
            for o in (True, False)
        ),
    )
    v_goal_only = sum(
        (p_saw if o else 1 - p_saw) * (STAKE if partner_action(goal, o) == best_goal_only else 0)
        for o in (True, False)
    )
    # belief model tracks the channel, so it is right every time.
    v_belief = STAKE - BELIEF_MODEL_COST
    return v_goal_only, v_belief


print("\n  pricing (stake %s, belief model costs %s)" % (STAKE, BELIEF_MODEL_COST))
print("      %-14s %-14s %-14s %s" % ("P(partner saw)", "goal-only", "belief model", "belief pays?"))
d1_rows = []
pays = 0
for num in (0, 1, 2, 3, 4):
    p = F(num, 4)
    vg, vb = d1_value(p)
    ok = vb > vg
    pays += ok
    d1_rows.append({"p_saw": str(p), "goal_only": str(vg), "belief": str(vb), "pays": ok})
    print("      %-14s %-14s %-14s %s" % (p, vg, vb, ok))

assert 0 < pays < len(d1_rows), "D1 pricing vacuous: belief model pays everywhere or nowhere"
print("\n      belief model pays on %d of %d channel settings (non-vacuous)" % (pays, len(d1_rows)))
OUT["D1"] = {
    "goal_only_fits_when_channel_varies": fits_var,
    "goal_only_fits_when_channel_constant": fits_con,
    "pricing": d1_rows,
}


# ----------------------------------------------------------------------------
# D2. Action prediction pays only when we must commit before revelation.
# ----------------------------------------------------------------------------

hdr("D2  intention and action prediction")

P_ACTS = ["left", "right"]
U_ACTS = ["left", "right"]
# coordination payoff: matching is worth 2, mismatching 0; plus a safe action.
MATRIX = {("left", "left"): F(2), ("left", "right"): F(0),
          ("right", "right"): F(2), ("right", "left"): F(0)}
PREDICTOR_COST = F(1, 5)


def d2_sequential(p_left):
    """We observe the partner's action, then act. Perfect play, no predictor."""
    return sum((p_left if pa == "left" else 1 - p_left) *
               max(MATRIX[(pa, ua)] for ua in U_ACTS)
               for pa in P_ACTS)


def d2_simultaneous_fixed(p_left):
    """We must commit first, with only the prior."""
    return max(sum((p_left if pa == "left" else 1 - p_left) * MATRIX[(pa, ua)] for pa in P_ACTS)
               for ua in U_ACTS)


def d2_simultaneous_predictor(p_left, q):
    """We must commit first, but a predictor of accuracy q calls the action."""
    tot = F(0)
    for pa in P_ACTS:
        pr_pa = p_left if pa == "left" else 1 - p_left
        for call in P_ACTS:
            pr_call = q if call == pa else 1 - q
            # posterior over the true action given the call
            post = {}
            for t in P_ACTS:
                prior_t = p_left if t == "left" else 1 - p_left
                post[t] = prior_t * (q if call == t else 1 - q)
            z = sum(post.values())
            best = max(U_ACTS, key=lambda ua: sum(post[t] / z * MATRIX[(t, ua)] for t in P_ACTS))
            tot += pr_pa * pr_call * MATRIX[(pa, best)]
    return tot - PREDICTOR_COST


print("\n  (a) SEQUENTIAL protocol -- we act after seeing the partner act")
p = F(1, 2)
seq = d2_sequential(p)
seq_pred = seq - PREDICTOR_COST
print("      observe-then-act          %s" % seq)
print("      predictor added to it     %s   (loses exactly its price %s)"
      % (seq_pred, PREDICTOR_COST))
assert seq - seq_pred == PREDICTOR_COST

print("\n  (b) SIMULTANEOUS protocol -- we must commit before revelation")
print("      %-12s %-14s %-16s %s" % ("accuracy q", "no predictor", "with predictor", "pays?"))
d2_rows = []
pays = 0
for num in (10, 11, 12, 13, 14, 15, 16):
    q = F(num, 20)
    base = d2_simultaneous_fixed(p)
    with_p = d2_simultaneous_predictor(p, q)
    ok = with_p > base
    pays += ok
    d2_rows.append({"q": str(q), "fixed": str(base), "predictor": str(with_p), "pays": ok})
    print("      %-12s %-14s %-16s %s" % (q, base, with_p, ok))

assert 0 < pays < len(d2_rows), "D2 vacuous: predictor pays at every accuracy or none"
thresh = min((F(r["q"]) for r in d2_rows if r["pays"]), default=None)
print("\n      predictor pays on %d of %d accuracies; threshold at q = %s"
      % (pays, len(d2_rows), thresh))
OUT["D2"] = {"sequential_loss": str(PREDICTOR_COST), "simultaneous": d2_rows,
             "threshold_q": str(thresh)}


# ----------------------------------------------------------------------------
# D3. Signal informativeness is set by incentive alignment, not by the channel.
#
# The partner KNOWS its type and chooses a signal. We have a known response
# rule. The partner picks the signal maximising ITS payoff. We then ask what
# the signal carries.
# ----------------------------------------------------------------------------

hdr("D3  cooperation and competition regimes")

TYPES = ["coop", "comp"]
SIGNALS = ["says_coop", "says_comp"]
ACTS3 = ["share", "guard"]
# our payoff for (their type, our action)
OUR = {("coop", "share"): F(3), ("coop", "guard"): F(1),
       ("comp", "share"): F(-2), ("comp", "guard"): F(1)}
ALIGNED = dict(OUR)
OPPOSED = {k: -v for k, v in OUR.items()}

# every deterministic response rule: signal -> action
RULES = [dict(zip(SIGNALS, combo)) for combo in itertools.product(ACTS3, repeat=2)]


def sender_best(their_payoff, rule):
    """Given our rule, each type picks the signal inducing its preferred action.
    Ties are recorded, because a tie means the signal is not forced."""
    out = {}
    for t in TYPES:
        vals = {s: their_payoff[(t, rule[s])] for s in SIGNALS}
        best = max(vals.values())
        out[t] = sorted(s for s in SIGNALS if vals[s] == best)
    return out


def separating(chosen):
    """Informative iff the two types cannot send a common signal."""
    return not (set(chosen["coop"]) & set(chosen["comp"]))


def our_best_rules(chosen, prior_coop):
    """Best deterministic rules against the sender's signalling behaviour.
    A type with ties is taken to split uniformly over its tied signals."""
    def joint(s, t):
        pr = prior_coop if t == "coop" else 1 - prior_coop
        opts = chosen[t]
        return pr * F(1, len(opts)) if s in opts else F(0)
    scored = []
    for rule in RULES:
        v = sum(joint(s, t) * OUR[(t, rule[s])] for s in SIGNALS for t in TYPES)
        scored.append((v, rule))
    best = max(v for v, _ in scored)
    return [r for v, r in scored if v == best], best


def fixed_points(their_payoff, prior_coop):
    """A rule is an equilibrium iff it is a best response to the signalling
    behaviour it itself induces."""
    fps = []
    for rule in RULES:
        chosen = sender_best(their_payoff, rule)
        best_rules, val = our_best_rules(chosen, prior_coop)
        if rule in best_rules:
            fps.append({"rule": dict(rule), "signals": {k: v for k, v in chosen.items()},
                        "informative": separating(chosen), "value": str(val)})
    return fps


prior = F(1, 2)
OUT["D3"] = {}
for name, pay in (("ALIGNED", ALIGNED), ("OPPOSED", OPPOSED)):
    fps = fixed_points(pay, prior)
    print("\n  %s regime -- equilibrium response rules (prior on coop = 1/2)" % name)
    for fp in fps:
        print("      rule %-42s informative=%-6s value=%s"
              % (str(fp["rule"]), fp["informative"], fp["value"]))
    any_inf = any(fp["informative"] for fp in fps)
    print("      an INFORMATIVE equilibrium exists: %s" % any_inf)
    OUT["D3"][name] = {"fixed_points": fps, "informative_equilibrium": any_inf}

al = OUT["D3"]["ALIGNED"]["informative_equilibrium"]
op = OUT["D3"]["OPPOSED"]["informative_equilibrium"]
assert al is True and op is False, "D3 vacuous: the two regimes behaved alike"

print("\n  why opposition is NOT simply 'the partner lies':")
trust = {"says_coop": "share", "says_comp": "guard"}
invert = {"says_coop": "guard", "says_comp": "share"}
ch = sender_best(OPPOSED, trust)
ch2 = sender_best(OPPOSED, invert)
print("      against a TRUSTING reader an opposed sender sends:  %s" % ch)
print("      against an INVERTING reader it sends:               %s" % ch2)
print("      BOTH are separating -- a deterministic liar leaks everything,")
print("      because a lie told every time is invertible.")
print("      but each reading re-aims the sender at the OTHER reading, so the")
print("      best-response cycle never closes. Only the uninformative rules")
print("      are fixed points, and that is why the opposed signal is worthless.")
assert separating(ch) and separating(ch2), "expected both readings to separate"
assert ch != ch2, "expected the sender to re-aim when the reading changes"
OUT["D3"]["invertibility_note"] = {"vs_trusting": {k: v for k, v in ch.items()},
                                   "vs_inverting": {k: v for k, v in ch2.items()}}


# ----------------------------------------------------------------------------
# D4. Deception, detection, and the substitution of commitment for detection.
# ----------------------------------------------------------------------------

hdr("D4  strategic deception and detection")

GAIN = F(3)        # deceiver's gain from a successful lie
DAMAGE = F(3)      # our loss from being deceived
VERIFY_COST = F(1, 2)


def d4_deceive(penalty, rho):
    """Deceive iff expected gain exceeds expected punishment."""
    return GAIN > rho * penalty


def d4_verify(p_deceive):
    """Verify iff the expected damage prevented exceeds the verification cost."""
    return p_deceive * DAMAGE > VERIFY_COST


print("\n  (a) when does the sender lie?  (gain %s)" % GAIN)
print("      %-12s %-14s %s" % ("penalty", "P(detect)", "lies?"))
d4_lie = []
for penalty in (F(0), F(2), F(6), F(12)):
    for rho in (F(1, 4), F(1, 2)):
        lies = d4_deceive(penalty, rho)
        d4_lie.append({"penalty": str(penalty), "rho": str(rho), "lies": lies})
        print("      %-12s %-14s %s" % (penalty, rho, lies))
n_lie = sum(r["lies"] for r in d4_lie)
assert 0 < n_lie < len(d4_lie), "D4 vacuous: sender always lies or never lies"

print("\n  (b) when do we pay to verify?  (cost %s, damage %s)" % (VERIFY_COST, DAMAGE))
print("      %-16s %s" % ("P(deception)", "verify?"))
d4_ver = []
for num in (0, 1, 2, 3, 4):
    pd = F(num, 8)
    v = d4_verify(pd)
    d4_ver.append({"p_deceive": str(pd), "verify": v})
    print("      %-16s %s" % (pd, v))
n_ver = sum(r["verify"] for r in d4_ver)
assert 0 < n_ver < len(d4_ver), "D4 vacuous: verification always or never pays"

print("\n  (c) commitment and detection are SUBSTITUTES")
deterring = GAIN / F(1, 2)          # penalty that deters at rho = 1/2
print("      a penalty above %s deters entirely at P(detect)=1/2" % deterring)
lies_after = d4_deceive(deterring + 1, F(1, 2))
print("      sender lies at that penalty: %s" % lies_after)
print("      P(deception) is then 0, so verification is worth: %s"
      % ("pay" if d4_verify(F(0)) else "nothing"))
assert lies_after is False and d4_verify(F(0)) is False
OUT["D4"] = {"lying": d4_lie, "verification": d4_ver,
             "deterring_penalty": str(deterring),
             "detector_needed_after_commitment": d4_verify(F(0))}

print("\n" + "=" * 70)
print("all four parts non-vacuous; every number exact over Fractions")
print("=" * 70)

with open(sys.argv[1] if len(sys.argv) > 1 else "STAGE_SOCIAL_STRATEGIC_V1.json", "w") as fh:
    json.dump(OUT, fh, indent=2, sort_keys=True)
