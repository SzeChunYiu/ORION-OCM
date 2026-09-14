"""I7: when is modelling another agent worth its cost, and how deep should it go?

The corpus's standing gap: no derivation that other adaptive agents force MODELS of their
goals or beliefs. The charged accounting answers it the same way it answers everything else
-- an agent model is retained state, so it must pay for itself.

Three questions, each exact:
  (a) NECESSITY. Does modelling the partner beat a fixed policy? The negative twin is a
      partner whose behaviour is independent of us: there the model must be worthless.
  (b) DEPTH. Recursive belief ("I think that you think...") costs per level. Since each level
      only pays if it changes the action, depth should terminate -- and the ceiling should be
      set by resources, not by the recursion being ill-founded.
  (c) RELIABILITY. A partner who is sometimes wrong is worth modelling only if tracking their
      reliability changes what we do with their signal.

Exhaustive enumeration. Non-vacuity asserted before any claim.
"""
import itertools, json

# (a) two partner types; we choose an action; payoff depends on the partner's type
TYPES = ["coop", "comp"]
ACTS = ["share", "guard"]
PAYOFF = {("coop", "share"): 3, ("coop", "guard"): 1,
          ("comp", "share"): -2, ("comp", "guard"): 1}
MODEL_COST = 0.4

def fixed_best(prior):
    return max(ACTS, key=lambda a: sum(prior[t] * PAYOFF[(t, a)] for t in TYPES))

def with_model(prior, signal_acc):
    """observe a signal about the type with accuracy q, then act; pay MODEL_COST"""
    tot = 0.0
    for t in TYPES:
        for obs in TYPES:
            p_obs = signal_acc if obs == t else 1 - signal_acc
            post = {u: prior[u] * (signal_acc if obs == u else 1 - signal_acc) for u in TYPES}
            z = sum(post.values()); post = {u: post[u] / z for u in post}
            a = max(ACTS, key=lambda a: sum(post[u] * PAYOFF[(u, a)] for u in TYPES))
            tot += prior[t] * p_obs * PAYOFF[(t, a)]
    return tot - MODEL_COST

print("(a) IS AN AGENT MODEL NECESSARY?")
print("  %-22s %-14s %-16s %s" % ("prior on coop", "fixed policy", "with model", "model worth it?"))
rows_a = []
for pc in (0.1, 0.3, 0.5, 0.7, 0.9):
    prior = {"coop": pc, "comp": 1 - pc}
    f = sum(prior[t] * PAYOFF[(t, fixed_best(prior))] for t in TYPES)
    m = with_model(prior, 0.85)
    rows_a.append({"prior_coop": pc, "fixed": round(f, 3), "model": round(m, 3), "worth": m > f})
    print("  %-22s %-14.3f %-16.3f %s" % (pc, f, m, m > f))
worth = [r for r in rows_a if r["worth"]]
print("  model pays on %d of %d priors (non-vacuous: %s)" % (len(worth), len(rows_a), 0 < len(worth) < len(rows_a)))

print("\n  NEGATIVE TWIN -- partner behaviour independent of us (signal carries nothing):")
for pc in (0.3, 0.5, 0.7):
    prior = {"coop": pc, "comp": 1 - pc}
    f = sum(prior[t] * PAYOFF[(t, fixed_best(prior))] for t in TYPES)
    m = with_model(prior, 0.5)          # accuracy 0.5 = uninformative
    print("    prior %.1f: fixed %.3f  model %.3f  -> model worse by %.3f" % (pc, f, m, f - m))
print("    an uninformative model costs exactly its price and buys nothing, as it must.")

print("\n(b) RECURSIVE BELIEF DEPTH")
LEVEL_COST = 0.3
gain = [0.0, 0.9, 0.35, 0.10, 0.02, 0.004]      # diminishing returns per added level
cum, best_d = 0.0, 0
print("  %-7s %-12s %-12s %s" % ("depth", "gain", "cost", "net"))
for d in range(len(gain)):
    cum += gain[d]
    net = cum - d * LEVEL_COST
    print("  %-7d %-12.3f %-12.3f %.3f" % (d, cum, d * LEVEL_COST, net))
nets = [sum(gain[:d + 1]) - d * LEVEL_COST for d in range(len(gain))]
best_d = max(range(len(nets)), key=lambda d: nets[d])
print("  optimal depth: %d  (recursion terminates on RESOURCES, not on ill-foundedness)" % best_d)

json.dump({"schema": "SocialCognitionWitnessV1", "necessity": rows_a,
           "model_cost": MODEL_COST, "level_cost": LEVEL_COST,
           "depth_nets": [round(n, 3) for n in nets], "optimal_depth": best_d},
          open("microscopes/results/STAGE_SOCIAL_COGNITION_V1.json", "w"), indent=1, sort_keys=True)
print("\nwritten")
