"""I4: replanning under model error/drift.

The stopping rule said: stop searching when no deeper search can change the committed
action. The conjecture here is that RESUMING search obeys the same criterion applied to a
different source of change:

  replan exactly when accumulated model error makes the committed action no longer the one
  the corrected model would choose.

If that holds, one criterion -- action-invariance -- governs both when to stop searching
and when to start again, differing only in whether the threat to invariance is search depth
or model drift.

Tested against the two obvious policies it must beat: replan every step (always correct,
maximally expensive) and never replan (free, increasingly wrong).
"""
import json, random

C_REPLAN = 2          # charged cost of one replanning episode
N_STEPS = 40
TRIALS = 200

def run(policy, drift, seed):
    """world cost of the committed action drifts; planner holds a model that goes stale."""
    rng = random.Random(seed)
    true_cost = {"A": 3.0, "B": 4.0}          # true costs, drift over time
    model = dict(true_cost)                    # planner's model, correct at t=0
    committed = min(model, key=model.get)
    total, replans = 0.0, 0
    for t in range(N_STEPS):
        # the world drifts
        for k in true_cost:
            true_cost[k] += rng.uniform(-drift, drift)
            true_cost[k] = max(0.5, true_cost[k])
        if policy == "always":
            model = dict(true_cost); replans += 1; total += C_REPLAN
            committed = min(model, key=model.get)
        elif policy == "never":
            pass
        elif policy == "on_action_change":
            # the agent observes the true costs (free) but only PAYS to replan when the
            # corrected model would pick a different action -- action-invariance violated
            would = min(true_cost, key=true_cost.get)
            if would != committed:
                model = dict(true_cost); replans += 1; total += C_REPLAN
                committed = would
        total += true_cost[committed]          # execute the committed action
    return total, replans

print("%-8s %-22s %-10s %-10s %s" % ("drift", "policy", "mean cost", "replans", "vs best"))
rows = []
for drift in (0.05, 0.2, 0.5, 1.0):
    res = {}
    for pol in ("never", "on_action_change", "always"):
        costs, reps = zip(*[run(pol, drift, s) for s in range(TRIALS)])
        res[pol] = (sum(costs) / TRIALS, sum(reps) / TRIALS)
    best = min(res, key=lambda p: res[p][0])
    for pol in ("never", "on_action_change", "always"):
        c, r = res[pol]
        print("%-8s %-22s %-10.2f %-10.1f %s" % (drift, pol, c, r, "BEST" if pol == best else ""))
    rows.append({"drift": drift, "results": {k: {"cost": round(v[0], 3), "replans": round(v[1], 2)}
                                             for k, v in res.items()}, "best": best})
    print()

wins = sum(1 for r in rows if r["best"] == "on_action_change")
print("action-change triggering is cheapest on %d of %d drift regimes" % (wins, len(rows)))
json.dump({"schema": "ReplanningPolicyWitnessV1", "C_replan": C_REPLAN, "steps": N_STEPS,
           "trials": TRIALS, "rows": rows, "action_change_wins": wins},
          open("microscopes/results/STAGE_REPLANNING_V1.json", "w"), indent=1, sort_keys=True)
print("written")
