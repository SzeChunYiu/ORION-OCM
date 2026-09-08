"""Generate the support-pilot figure directly from immutable arm receipts."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    summary = json.loads((args.results / "summary.json").read_text())
    rows = summary["arms"]
    labels = {"active_monotone": "Explicit version\nspace",
              "antichain_parent": "Antichain\nparent",
              "eager_table": "Eager\ntable",
              "lazy_cache": "Lazy\ncache",
              "loo_ablation": "LOO\nablation"}
    colors = ["#176B95", "#5C478F", "#8A969D", "#8A969D", "#B44D3C"]
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.3))
    for ax, key, title in zip(axes, ["queries", "work"],
                             ["Paid queries (correct / total below count)", "Counted operations (log scale)"]):
        values = [r["cost"]["query_calls"] if key == "queries" else
                  r["counted_operations"] for r in rows]
        ax.bar(range(len(rows)), values, color=colors, width=0.68)
        if key == "work":
            ax.set_yscale("log")
            ax.set_ylim(max(1, min(values) / 2), max(values) * 3)
        else:
            ax.set_ylim(0, max(values) * 1.28)
        for i, (r, value) in enumerate(zip(rows, values)):
            annotation = f"{value:,}"
            if key == "queries":
                annotation += f"\n{r['correct']}/{r['n']}"
            ax.annotate(annotation, (i, value), xytext=(0, 5),
                        textcoords="offset points", ha="center", fontsize=9)
        ax.set_xticks(range(len(rows)), [labels[r["arm"]] for r in rows], fontsize=9)
        ax.set_title(title, loc="left", fontsize=12, weight="bold")
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=.2)
        ax.set_axisbelow(True)
    fig.suptitle("Learning when a fixed rule remains supported", x=.08, ha="left",
                 fontsize=16, weight="bold")
    fig.text(.08, .89, "Actual-source development census; candidate evidence groups supplied", fontsize=10)
    fig.text(.08, .04, "Counts include baseline queries and acquisition. Operation proxy excludes catalogue construction.\n"
             "LOO is an intentionally unsound ablation. These are retention classifications, not universal rule correctness.",
             fontsize=9)
    fig.subplots_adjust(top=.79, bottom=.23, left=.08, right=.98, wspace=.28)
    args.out.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "svg"):
        destination = args.out / f"support_learning.{ext}"
        if destination.exists():
            raise FileExistsError(destination)
        fig.savefig(destination, dpi=180, facecolor="white")
    (args.out / "figure_source.json").write_text(json.dumps({
        "registration_sha256": summary["registration_sha256"],
        "source": str(args.results.name) + "/summary.json",
        "rows": [{"arm": r["arm"], "queries": r["cost"]["query_calls"],
                  "counted_operations": r["counted_operations"],
                  "correct": r["correct"], "n": r["n"]} for r in rows]}, indent=2) + "\n")


if __name__ == "__main__":
    main()
