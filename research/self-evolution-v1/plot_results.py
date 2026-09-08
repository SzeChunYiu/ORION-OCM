"""Standalone figures from retained measured results; no fitted capability score."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
pilot = ROOT / "results/run-v1"
payback = json.loads((ROOT / "results/payback-v1/result.json").read_text())
spent, x, g = 0, [0], [0]
for i in range(3):
    cycle = json.loads((pilot / f"cycle-{i}.json").read_text())
    fresh = json.loads((pilot / f"fresh-{i}.json").read_text())
    spent += cycle["measured_runner_cost"]["work"]
    spent += sum(fresh[a]["resources"]["work"] for a in ("current", "compensated_previous"))
    x.append(spent / 1000)
    g.append(cycle["generation_after"])

plt.rcParams.update({"font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "svg.fonttype": "none"})
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), constrained_layout=True)
axes[0].plot(x, g, "o-", color="#28699d", linewidth=2)
axes[0].axhline(3, color="#999999", linestyle="--", linewidth=1)
axes[0].annotate("Required g3 not reached", (x[-1], 3), xytext=(-3, 6),
                 textcoords="offset points", ha="right", fontsize=9)
axes[0].set(xlabel="Cumulative measured development work (thousands)",
            ylabel="Earned configuration generation", ylim=(-.1, 3.5),
            title="A  Two adopted changes; third attempt stopped")
axes[0].set_yticks([0, 1, 2, 3])

rows = payback["rows"]
episodes = [0] + [r["episode"] for r in rows]
old = [0] + [r["cumulative_initial_work"] / 1e6 for r in rows]
new = [payback["self_improvement_work_fully_charged"] / 1e6] + [r["cumulative_evolved_work"] / 1e6 for r in rows]
axes[1].plot(episodes, old, color="#777777", label="Initial dispatcher", linewidth=2)
axes[1].plot(episodes, new, color="#28699d", label="Evolved + counted development work", linewidth=2)
axes[1].axvline(payback["first_counted_work_payback_episode"], color="#999999", linestyle=":")
axes[1].set(xlabel="Further development revision episodes", ylabel="Cumulative counted work (millions)",
            title="B  Counted-work payback at episode 12")
axes[1].legend(frameon=False, loc="upper left", fontsize=9)
fig.suptitle("M11 self-evolution pilot — existing-library selection, E2 evidence", fontsize=13)
for ax in axes:
    ax.grid(axis="y", alpha=.15)
dest = ROOT / "figures"
dest.mkdir(exist_ok=True)
fig.savefig(dest / "self_evolution_results.svg")
fig.savefig(dest / "self_evolution_results.png", dpi=180)
