"""Centre: run the CANONICAL serial generation cycle through the real M11
cell (vendored #149 EvolutionCell over ``ocm``), consuming the frozen MODEL
PROXY decision, and emit GenerationSnapshotV1 + DEVELOPMENT_TRANSITION receipt.

One cycle = one attempted generation transition.  Outcomes (all honest):

* DEVELOPMENT_CHANGE_ADOPTED   generation g+1 installed by M11 adoption;
* EXTERNAL_ADOPTION_REJECTED   assurance passed but the proxy said no;
* SELF_EVOLUTION_REGRESSES      M11 assurance failed on shadow suites;
* SELF_DIAGNOSIS_NOT_IDENTIFIABLE  candidate did not dominate on re-measure.

Also emits the PDEV-9 receipts: cold restart (identity), rollback
counterfactual (clone), determinism re-measurement of the incumbent, and
(paven at --freeze) the PDEV-13 protected freeze identity.

Usage:
  centre_cycle.py --run-root R --generation G
  centre_cycle.py --run-root R --generation G --freeze
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
for entry in (HERE, HERE.parent):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

import pdev_io as IO  # noqa: E402
import pdev_grammar as G  # noqa: E402
import pdev_runner as R  # noqa: E402
import pdev_machine as M  # noqa: E402

BUDGETS = dict(M.DEFAULT_BUDGETS)


def determinism_check(run_root, generation):
    """Re-measure the incumbent on its own dev suite; vector must reproduce
    exactly (deterministic meter) -- the regression/replay control."""
    gdir = IO.gen_dir(run_root, generation)
    suites = IO.load_suites(run_root, generation)
    incumbent = IO.read_json(gdir / "incumbent.json")
    dev = incumbent["suites"]["dev"]
    again = R.runner(incumbent["config"], suites["dev"])
    return {
        "schema": "pdev217.determinism.v1", "generation": generation,
        "first": {"n": dev["n"], "success": dev["success"],
                  "work": dev["work"],
                  "persistent_bytes": dev["persistent_bytes"]},
        "second": {"n": again["n"], "success": again["success"],
                   "work": again["resources"]["work"],
                   "persistent_bytes": again["resources"]["persistent_bytes"]},
        "exact": (dev["n"] == again["n"] and dev["success"] == again["success"]
                  and dev["work"] == again["resources"]["work"]
                  and dev["persistent_bytes"]
                  == again["resources"]["persistent_bytes"])}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-root", required=True)
    ap.add_argument("--generation", type=int, required=True)
    ap.add_argument("--freeze", action="store_true")
    args = ap.parse_args()

    paths = IO.run_paths(args.run_root)
    state = IO.read_json(paths["state"])
    if state["generation"] != args.generation:
        raise SystemExit("state generation %d != requested %d"
                         % (state["generation"], args.generation))
    gdir = IO.gen_dir(args.run_root, args.generation)
    packet = IO.read_json(gdir / "ADOPTION_PACKET.json")
    suites = IO.load_suites(args.run_root, args.generation)
    decision_path = gdir / "decision.json"
    if not decision_path.exists():
        raise SystemExit("no frozen decision file; the external gate is closed")

    lineage = M.PDEVLineage(str(paths["lineage"] / "CONTINUED"), BUDGETS,
                            mode="CONTINUED")
    before = lineage.snapshot("g%d" % args.generation, 0,
                              {"event": "cycle-start"})
    entry = lineage.develop(packet["winner"], suites["dev"],
                            {"target": suites["target"],
                             "preservation": suites["preservation"]},
                            str(decision_path),
                            obstruction=packet.get("obstruction"))
    cold = lineage.cold_restart_check()
    rollback = lineage.rollback_counterfactual()
    det = determinism_check(args.run_root, args.generation)
    after = lineage.snapshot("g%d" % args.generation, 1, {
        "event": "cycle-end", "terminal": entry.get("terminal"),
        "determinism_exact": det["exact"], "cold_restart_exact": cold["exact"]})

    adopted = entry.get("terminal") == "DEVELOPMENT_CHANGE_ADOPTED"
    charged_work = int(entry["incumbent_development"]["resources"]["work"])
    charged_work += sum(int(p["measurement"]["resources"]["work"])
                        for p in entry.get("probes", []))
    shadow = entry.get("shadow") or {}
    for side in ("challenger", "incumbent"):
        for suite_row in shadow.get(side, {}).values():
            charged_work += int(suite_row["resources"]["work"])
    state["attempted_cycles"] = state.get("attempted_cycles", 0) + 1
    if adopted:
        state["generation"] = args.generation + 1
        state["incumbent"] = {"config": after["config"],
                              "digest": after["config_digest"]}
        state["adoptions"] = state.get("adoptions", 0) + 1
    row = {
        "schema": "pdev217.generation_ledger.v1",
        "generation_attempted": args.generation,
        "generation_after": state["generation"],
        "terminal": entry.get("terminal"),
        "winner": packet["winner"]["candidate_id"],
        "winner_arm": packet["winner"]["arm"],
        "decision_gate": "HUMAN_GATE_BYPASSED__MODEL_PROXY",
        "m11_cycle_index": entry.get("cycle"),
        "m11_prediction": entry.get("prediction"),
        "m11_assurance": entry.get("assurance"),
        "m11_shadow": {"challenger": shadow.get("challenger"),
                       "incumbent": shadow.get("incumbent"),
                       "non_interference": shadow.get("non_interference")}
        if shadow else None,
        "cold_restart": cold, "rollback_counterfactual": rollback,
        "determinism": det, "snapshot_before": before["snapshot_sha256"],
        "snapshot_after": after["snapshot_sha256"],
        "resources_charged": {"work": charged_work},
        "written_unix": time.time(),
    }
    IO.write_json(gdir / "cycle_receipt.json", row)
    IO.append_jsonl(paths["generation_ledger"], row)
    IO.write_json(paths["state"], state)

    if args.freeze:
        frozen = lineage.cell.freeze_for_protected(
            comparator={"vector": list(R.RESOURCE_KEYS),
                        "rule": "failures, work, persistent_bytes Pareto; "
                                "assured via M11 shadow suites"},
            budgets=BUDGETS,
            protected_protocol_hash=G.digest(
                {"protocol": "pdev217.freeze.v1",
                 "vendor": after["vendor_manifest_sha256"]}))
        IO.write_json(paths["lineage"] / "CONTINUED" / "freeze.json", frozen)
        print("frozen_identity=%s" % frozen["freeze_hash"])
    print("terminal=%s generation_after=%d" % (entry.get("terminal"),
                                               state["generation"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
