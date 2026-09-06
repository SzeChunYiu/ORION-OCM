"""Plot recorded chunk CPU, without benchmarking or importing the actors.

Run with an existing matplotlib environment: python3 plot_cpu.py
Reads only sibling sealed receipts/rows/grades; writes the figure and source data.
"""
import hashlib
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_run(label):
    folder = ROOT / label
    receipt = json.loads((folder / "receipt.json").read_text())
    grade = json.loads((folder / "grade.json").read_text())
    assert receipt["status"] == "EXECUTED_NOT_GRADED"
    assert grade["status"] == "GRADED_DEVELOPMENT"
    assert grade["receipt_sha256"] == sha(folder / "receipt.json")
    assert grade["syntax_agreement"] == {"assigned": 100, "both_valid": 100, "equal_trees": 100}
    series = {}
    for arm in ("native", "ocm"):
        chunks = sorted((c for c in receipt["chunks"] if c["arm"] == arm), key=lambda c: c["chunk"])
        assert [c["chunk"] for c in chunks] == list(range(5))
        items, cpu = 0, 0.0
        points = [{"items_completed": 0, "cumulative_cpu_s": 0.0}]
        for chunk in chunks:
            path = folder / ("%02d-%s.rows.jsonl" % (chunk["chunk"], arm))
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            assert len(rows) == chunk["rows_written"] == chunk["worker"]["rows"] == 21
            assert sha(path) == chunk["worker"]["rows_sha256"]
            assert chunk["complete_cpu_custody"] and chunk["exit_code"] == 0
            assert not chunk["outer_timeout"]
            observed = chunk["reaped_process_tree_cpu_s"]
            assert math.isfinite(observed) and observed >= 0
            items += len(rows)
            cpu += observed
            points.append({"chunk": chunk["chunk"], "items_completed": items,
                           "chunk_cpu_s": observed, "cumulative_cpu_s": cpu,
                           "rows_path": str(path.relative_to(ROOT)), "rows_sha256": sha(path)})
        assert items == 105
        assert math.isclose(cpu, grade["resources"][arm]["observed_reaped_cpu_s"], rel_tol=1e-12)
        summary = grade["summaries"][arm]
        assert summary["syntax"]["accepted"] == 100 and summary["clia"]["accepted"] == 5
        assert summary["clia"]["verified_programs"]["correct"] == 5
        series[arm] = {"points": points, "resources": grade["resources"][arm]}
    return {"receipt_sha256": sha(folder / "receipt.json"),
            "grade_sha256": sha(folder / "grade.json"),
            "source_identity": receipt["source_identity"],
            "model_sha256": receipt["model_sha256"],
            "public_items_sha256": receipt["plan"]["public_items_sha256"], "arms": series}


def main():
    runs = {label: read_run(label) for label in ("original", "revised")}
    for key in ("model_sha256", "public_items_sha256"):
        assert runs["original"][key] == runs["revised"][key]
    data = {"scope": "Single frozen public development stream on shared laptop; descriptive chunk endpoints.",
            "cpu_scope": "Reaped worker process-tree CPU: imports, replay, archive, checking, persistence. Training, installation, external grading and energy excluded.",
            "native_curve": "Revised-run native; original native retained separately, never pooled.",
            "matplotlib_version": matplotlib.__version__, "plot_script_sha256": sha(Path(__file__)), "runs": runs}
    (ROOT / "cpu-series.json").write_text(json.dumps(data, indent=2) + "\n")
    plt.rcParams.update({"font.size": 10, "svg.hashsalt": "g1-admission-support-20260906"})
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    styles = [("original", "ocm", "Original OCM", "#bb6c16", "o"),
              ("revised", "ocm", "OCM with existing exact-support admission", "#176eaa", "s"),
              ("revised", "native", "Native donor (revised run)", "#444444", "^")]
    for run, arm, label, color, marker in styles:
        points = runs[run]["arms"][arm]["points"]
        x = [p["items_completed"] for p in points]
        y = [p["cumulative_cpu_s"] for p in points]
        ax.plot(x, y, color=color, marker=marker, linewidth=1.8, markersize=5,
                label="%s: %.3f s" % (label, y[-1]))
    ax.set(xlabel="Items completed (100 syntax + 5 synthesis)",
           ylabel="Cumulative observed process-tree CPU (seconds)",
           xlim=(-1, 107), ylim=(-3, 136), xticks=[0, 21, 42, 63, 84, 105])
    ax.grid(axis="y", color="#dddddd", linewidth=0.7)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="upper left", frameon=False, fontsize=9)
    fig.suptitle("Observed CPU before and after exact-support adoption", x=0.12, ha="left", fontsize=12)
    fig.text(0.12, 0.905, "Single frozen development stream; shared laptop; no statistical generalization", fontsize=9)
    fig.text(0.12, 0.025, "Markers are completed 21-item chunks; connecting lines guide the eye. Training and grading excluded.", fontsize=8)
    fig.subplots_adjust(left=0.12, right=0.975, bottom=0.16, top=0.86)
    for extension in ("png", "svg", "pdf"):
        fig.savefig(ROOT / ("cpu-cumulative." + extension), dpi=180,
                    metadata={"Creator": "plot_cpu.py"})
    plt.close(fig)
    print(json.dumps({r: {a: runs[r]["arms"][a]["points"][-1] for a in ("native", "ocm")} for r in runs}, indent=2))


if __name__ == "__main__":
    main()
