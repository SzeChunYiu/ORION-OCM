"""I4: when is model-based future simulation worth its cost?

Simulation is not free: the model must be retained (CSR-1 charges that) and each simulated
future costs compute. The alternative is to act and observe, which costs real mistakes.

Derived comparison, no new principle:
  act-and-observe : expected wrong tries x mistake cost   (+ termination penalty if irreversible)
  simulate        : model retention + sim cost per option evaluated, then one correct act

Predicted: simulation pays exactly when mistakes are expensive or irreversible relative to
model cost; with cheap reversible mistakes, trial-and-error dominates.

Every cell exact -- expectations computed in closed form, not sampled. Non-vacuity is
CHECKED: the winning strategy must actually change across the sweep, or the test says
nothing.
"""
import json

def act_observe(n, mistake, irreversible, ruin):
    """uniformly random correct option; try until found"""
    if irreversible:
        # one shot: 1/n chance of success, else ruin
        return (1.0 / n) * 0.0 + (1 - 1.0 / n) * ruin
    # expected number of wrong tries before success = (n-1)/2
    return ((n - 1) / 2.0) * mistake

def simulate(n, model_cost, sim_cost):
    """retain a model, evaluate every option in simulation, then act correctly"""
    return model_cost + n * sim_cost

N = 6
rows = []
print("%-9s %-7s %-7s %-7s %-11s %-11s %s" % ("mistake", "irrev", "model", "sim", "act&obs", "simulate", "winner"))
for irreversible in (False, True):
    for mistake in (0.5, 2, 8, 32):
        for model_cost, sim_cost in ((4, 0.5), (12, 2)):
            a = act_observe(N, mistake, irreversible, ruin=50)
            s = simulate(N, model_cost, sim_cost)
            w = "simulate" if s < a else "act&observe"
            rows.append({"mistake": mistake, "irreversible": irreversible,
                         "model_cost": model_cost, "sim_cost": sim_cost,
                         "act_observe": a, "simulate": s, "winner": w})
            print("%-9s %-7s %-7s %-7s %-11.2f %-11.2f %s"
                  % (mistake, irreversible, model_cost, sim_cost, a, s, w))

winners = {r["winner"] for r in rows}
n_sim = sum(1 for r in rows if r["winner"] == "simulate")
print("\ndistinct winners across the sweep: %s  (non-vacuous: %s)" % (sorted(winners), len(winners) > 1))
print("simulation wins %d of %d cells" % (n_sim, len(rows)))

# the two structural claims, checked separately
rev = [r for r in rows if not r["irreversible"]]
irr = [r for r in rows if r["irreversible"]]
claim1 = all(r["winner"] == "simulate" for r in rev if r["mistake"] >= 8) and \
         any(r["winner"] == "act&observe" for r in rev if r["mistake"] <= 2)
claim2 = sum(1 for r in irr if r["winner"] == "simulate") > sum(1 for r in rev if r["winner"] == "simulate")
print("\nclaim 1 -- with reversible mistakes, expensive mistakes flip it to simulation:", claim1)
print("claim 2 -- irreversibility favours simulation more than reversibility does :", claim2)
json.dump({"schema": "SimulationWorthWitnessV1", "n_options": N, "rows": rows,
           "non_vacuous": len(winners) > 1, "claim_expensive_mistakes": claim1,
           "claim_irreversibility": claim2},
          open("microscopes/results/STAGE_SIMULATION_WORTH_V1.json", "w"), indent=1, sort_keys=True)
print("written")
