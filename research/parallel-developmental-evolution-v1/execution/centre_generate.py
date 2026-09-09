"""Centre: build one wave batch (+ generation suites, incumbent measurement,
parent batch), register the frozen denominator BEFORE submission.

Centre is the ONLY writer of state: task ledger, suites, serial states, batch
files, archive.  Workers only measure.

Usage:
  centre_generate.py --run-root R --generation G --wave W --salt S --quota Q
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
import pdev_search  # noqa: E402
import pdev_tasks as T  # noqa: E402
import pdev_machine as M  # noqa: E402


def mix_tasks(recipes: dict, name: str, ledger: T.TaskLedger, phase: str):
    recipe = recipes[name]
    mix = str(recipe["mix"])          # e.g. "s4d2" -> 4 s tasks + 2 d tasks
    s_spec, d_spec = mix.split("d")
    s_count, d_count = int(s_spec[1:]), int(d_spec)
    out = []
    if s_count:
        out.extend(ledger.take(s_count, domain="s", phase=phase, label=name))
    if d_count:
        out.extend(ledger.take(d_count, domain="d", phase=phase, label=name))
    return out


def ensure_generation_suites(run_root: str, generation: int, incumbent: dict,
                             recipes=None) -> None:
    gdir = IO.gen_dir(run_root, generation)
    if (gdir / "suites.json").exists():
        return
    recipes = recipes or dict(T.SUITE_RECIPES)
    paths = IO.run_paths(run_root)
    ledger = T.TaskLedger(str(paths["task_ledger"]))
    suites = {name: mix_tasks(recipes, name, ledger, "%s.g%d" % (name, generation))
              for name in recipes}
    ledger.save()

    # Incumbent measured on EVERY suite of this generation (control + hostile
    # baseline), synchronously here and recorded before any candidate runs.
    measured = {}
    for name, tasks in suites.items():
        result = R.runner(incumbent["config"], tasks)
        measured[name] = result
    incumbent_row = {
        "schema": "pdev217.incumbent.v1",
        "generation": generation,
        "config": incumbent["config"],
        "digest": G.digest(incumbent["config"]),
        "suites": {name: {"n": res["n"], "success": res["success"],
                          "violations": res["preservation_violations"],
                          "work": res["resources"]["work"],
                          "persistent_bytes": res["resources"]["persistent_bytes"]}
                   for name, res in measured.items()},
    }
    IO.write_json(gdir / "suites.json",
                  {"schema": "pdev217.suites.v1", "generation": generation,
                   "recipes": {k: dict(v) for k, v in recipes.items()},
                   "suites": suites})
    IO.write_json(gdir / "incumbent.json", incumbent_row)
    incumbent["raw"] = incumbent_row


def ensure_parent_batch(run_root: str, generation: int) -> int:
    gdir = IO.gen_dir(run_root, generation)
    path = gdir / ("parent_batch_g%d.json" % generation)
    if path.exists():
        return len(IO.read_json(path)["entries"])
    parents = IO.run_paths(run_root)["parents"]

    def serial_state(arm: str, initial: dict) -> dict:
        state_path = parents / arm / "serial_state.json"
        if state_path.exists():
            return IO.read_json(state_path)
        state = {"schema": "pdev217.serial_state.v1", "arm": arm,
                 "generation": 0, "config": dict(initial),
                 "digest": G.digest(initial), "adoptions": 0, "history": []}
        IO.write_json(state_path, state)
        return state

    entries = [{"entry_id": "PARENT.g2.g%d" % generation, "kind": "baseline",
                "arm": "PARENT", "config": dict(M.G2_MORPHOLOGY)}]
    for arm, initial in (("CONTINUED", M.G2_MORPHOLOGY),
                         ("RESET", M.RESET_MORPHOLOGY)):
        state = serial_state(arm, initial)
        entries.append({"entry_id": "%s.baseline.g%d" % (arm, generation),
                        "kind": "baseline", "arm": arm,
                        "config": dict(state["config"])})
        seen = {G.digest(state["config"])}
        for child in G.enumerate_neighbourhood(state["config"],
                                               structural_only=True):
            if G.validate(child) or G.is_noop(child, state["config"]):
                continue
            dg = G.digest(child)
            if dg in seen:
                continue
            seen.add(dg)
            entries.append({"entry_id": "%s.n%d.g%d" % (arm, len(entries),
                                                        generation),
                            "kind": "neighbour", "arm": arm, "config": child})
        for child in G.enumerate_neighbourhood(state["config"],
                                               structural_only=False)[:96]:
            if G.validate(child) or G.is_noop(child, state["config"]):
                continue
            dg = G.digest(child)
            if dg in seen:
                continue
            seen.add(dg)
            entries.append({"entry_id": "%s.n%d.g%d" % (arm, len(entries),
                                                        generation),
                            "kind": "neighbour", "arm": arm, "config": child})
    payload = {"schema": "pdev217.parent_batch.v1", "generation": generation,
               "entries": entries, "denominator": len(entries)}
    IO.write_json(path, payload)
    return len(entries)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-root", required=True)
    ap.add_argument("--generation", type=int, required=True)
    ap.add_argument("--wave", type=int, required=True)
    ap.add_argument("--salt", required=True)
    ap.add_argument("--quota", type=int, default=12)
    args = ap.parse_args()

    paths = IO.run_paths(args.run_root)
    state = IO.read_json(paths["state"])
    if state["generation"] != args.generation:
        raise SystemExit("state generation %d != requested %d"
                         % (state["generation"], args.generation))

    ensure_generation_suites(args.run_root, args.generation, state["incumbent"])
    incumbent_row = IO.read_json(IO.gen_dir(args.run_root, args.generation)
                                 / "incumbent.json")
    parent_den = ensure_parent_batch(args.run_root, args.generation)

    wdir = IO.wave_dir(args.run_root, args.generation, args.wave)
    if (wdir / "batch.json").exists():
        batch = IO.read_json(wdir / "batch.json")
    else:
        candidates = pdev_search.propose_wave(
            args.salt, args.generation, args.wave, state["incumbent"]["config"],
            str(paths["history"]) if paths["history"].exists() else None,
            str(paths["archive"]) if paths["archive"].exists() else None,
            args.quota,
            int(incumbent_row["suites"]["dev"]["persistent_bytes"]))
        batch = {"schema": "pdev217.wave_batch.v1",
                 "generation": args.generation, "wave": args.wave,
                 "salt": args.salt, "quota_per_arm": args.quota,
                 "parent": state["incumbent"]["config"],
                 "candidates": candidates,
                 "denominator": len(candidates)}
        IO.write_json(wdir / "batch.json", batch)

    manifest_path = paths["manifests"] / "BATCH.json"
    manifest = IO.read_json(manifest_path) if manifest_path.exists() else \
        {"schema": "pdev217.batch_manifest.v1", "waves": []}
    manifest["waves"].append({
        "generation": args.generation, "wave": args.wave,
        "evaluate_denominator": batch["denominator"],
        "parent_denominator": parent_den
        if not [w for w in manifest["waves"]
                if w["generation"] == args.generation] else 0,
        "registered_unix": time.time(), "submitted": False})
    IO.write_json(manifest_path, manifest)
    print("evaluate_denominator=%d parent_denominator=%d"
          % (batch["denominator"], parent_den))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
