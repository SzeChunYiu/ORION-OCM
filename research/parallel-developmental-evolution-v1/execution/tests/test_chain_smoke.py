#!/usr/bin/env python3
"""End-to-end harness self-test for the PDEV-217 capsule (HPC issue #217).

Runs the ENTIRE frozen chain in a scratch run root, exactly as the slurm
layout will run it (same CLIs, same order), at smoke scale:

  centre_init -> centre_generate(quota=1) -> worker_evaluate(all indices)
  -> aggregate collect -> worker_verify(all survivors) -> aggregate finalize
  -> centre_cycle (frozen proxy decision; fail-closed refusal first)
  -> [forced-adoption harness leg if nothing adopted]
  -> a second wave (same generation if no adoption, else the new generation)

This is HARNESS VALIDATION, not a campaign measurement: it uses the frozen
master salt and the real suites, but its run root is separate and is never
aggregated into campaign ledgers.  Packets it synthesizes are labelled
``harness_validation``; the M11 cell still re-measures everything itself.

Usage: python3 test_chain_smoke.py SCRATCH_DIR
Exit code 0 = every stage passed.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent          # execution/
CAPSULE = HERE.parent                                   # capsule root
for p in (str(HERE), str(CAPSULE)):
    if p not in sys.path:
        sys.path.insert(0, p)

MASTER_SALT = "pdev217-20260909-uniform-ignorance"      # frozen, PROTOCOL.json

PY = sys.executable or "python3"
ENV = dict(os.environ)
ENV["PYTHONPATH"] = os.pathsep.join(
    p for p in (str(HERE), str(CAPSULE),
                ENV.get("PDEV217_OCM", ""), ENV.get("PYTHONPATH", "")) if p)


def run(args, expect=0, label=""):
    proc = subprocess.run([PY] + [str(a) for a in args], env=ENV,
                          cwd=str(HERE), capture_output=True, text=True)
    lines = (proc.stdout or "").strip().splitlines()
    print("[test] %-30s rc=%d %s" % (label, proc.returncode,
                                     lines[-1] if lines else ""))
    if proc.returncode != expect:
        print("  STDOUT:", proc.stdout[-4000:])
        print("  STDERR:", proc.stderr[-4000:])
        raise SystemExit("stage failed: %s (rc=%d, expected %d)"
                         % (label, proc.returncode, expect))
    return proc.stdout


def read(path):
    return json.loads(Path(path).read_text())


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines()
            if line.strip()]


def vec(row):
    return (int(row["n"]) - int(row["success"]), int(row["work"]),
            int(row["persistent_bytes"]))


def dominates(a, b):
    return (a[0] <= b[0] and a[1] <= b[1] and a[2] <= b[2]
            and a != b)


def measure(config, tasks):
    import pdev_runner as R
    return R.runner(config, tasks)


def main() -> int:
    scratch = Path(sys.argv[1]).resolve()
    if scratch.exists():
        shutil.rmtree(scratch)
    scratch.mkdir(parents=True)
    run_root = scratch / "run"
    state_path = run_root / "generations" / "state.json"

    # -- init ---------------------------------------------------------------
    run([HERE / "centre_init.py", "--run-root", run_root], label="centre_init")
    state = read(state_path)
    assert state["generation"] == 2 and state["adoptions"] == 0
    print("[test] init ok: generation=%d incumbent digest=%s"
          % (state["generation"], state["incumbent"]["digest"][:12]))

    # -- generate (smoke quota=1) ------------------------------------------
    t0 = time.time()
    out = run([HERE / "centre_generate.py", "--run-root", run_root,
               "--generation", 2, "--wave", 1, "--salt", MASTER_SALT,
               "--quota", 1], label="centre_generate")
    print("[test] generate wall=%.1fs %s" % (time.time() - t0, out.strip()))
    wdir = run_root / "generations" / "g2" / "waves" / "w1"
    batch = read(wdir / "batch.json")
    denom = batch["denominator"]
    assert denom == len(batch["candidates"]) and denom >= 1
    manifest = read(run_root / "manifests" / "BATCH.json")
    assert manifest["waves"][-1]["evaluate_denominator"] == denom
    assert manifest["waves"][-1]["parent_denominator"] > 0
    suites = read(run_root / "generations" / "g2" / "suites.json")
    incumbent = read(run_root / "generations" / "g2" / "incumbent.json")
    inc_dev = incumbent["suites"]["dev"]
    assert inc_dev["n"] == len(suites["suites"]["dev"]) and inc_dev["n"] > 0
    for name in ("dev", "target", "preservation", "harmful", "fresh",
                 "relabel", "audit"):
        assert name in suites["suites"], "missing suite %s" % name
    print("[test] suites ok: dev n=%d incumbent work=%s bytes=%s"
          % (inc_dev["n"], inc_dev["work"], inc_dev["persistent_bytes"]))

    # -- evaluate every candidate -------------------------------------------
    t0 = time.time()
    for index in range(denom):
        run([HERE / "worker_evaluate.py", "--run-root", run_root,
             "--generation", 2, "--wave", 1, "--index", index],
            label="worker_evaluate[%d]" % index)
    print("[test] evaluate wall=%.1fs (%d candidates)" % (time.time() - t0, denom))
    rows = [read(wdir / "eval" / (c["candidate_id"] + ".json"))
            for c in batch["candidates"]]
    measured = [r for r in rows if r["status"] == "MEASURED"]
    assert all(r["status"] in ("MEASURED", "CRASHED") for r in rows)
    if len(measured) != len(rows):
        print("[test] NOTE crashed eval rows: %d" % (len(rows) - len(measured)))
    ledger = read_jsonl(run_root / "CANDIDATE_LEDGER.jsonl")
    assert len(ledger) == len(measured)
    for cand in batch["candidates"]:
        assert cand["change_class"] in ("C3", "C4", "C5"), cand
    print("[test] eval ok: %d measured / %d" % (len(measured), len(rows)))

    # -- aggregate collect ---------------------------------------------------
    out = run([HERE / "centre_aggregate.py", "--run-root", run_root,
               "--generation", 2, "--wave", 1, "--stage", "collect"],
              label="aggregate_collect")
    print("[test] collect: %s" % out.strip())
    vbatch = read(wdir / "verify_batch.json")
    vden = vbatch["denominator"]
    assert vden == len(vbatch["candidates"]) and vden <= 40

    # -- verify every survivor ----------------------------------------------
    t0 = time.time()
    for index in range(vden):
        run([HERE / "worker_verify.py", "--run-root", run_root,
             "--generation", 2, "--wave", 1, "--index", index],
            label="worker_verify[%d]" % index)
    print("[test] verify wall=%.1fs (%d survivors)" % (time.time() - t0, vden))
    for cand in vbatch["candidates"]:
        vrow = read(wdir / "verify" / (cand["candidate_id"] + ".json"))
        assert vrow["status"] in ("VERIFIED", "CRASHED")
        assert isinstance(vrow["hostiles"], list) and len(vrow["hostiles"]) == 11
        assert set(vrow["shadow"]) <= {"target", "preservation", "harmful",
                                       "fresh", "relabel"}

    # -- aggregate finalize ---------------------------------------------------
    out = run([HERE / "centre_aggregate.py", "--run-root", run_root,
               "--generation", 2, "--wave", 1, "--stage", "finalize"],
              label="aggregate_finalize")
    print("[test] finalize: %s" % out.strip())
    agg = read(wdir / "aggregate.json")
    assert agg["stage"] == "finalize" and "failure_stage" in agg
    history = read_jsonl(run_root / "search_history.jsonl")
    assert len(history) == len(measured), (len(history), len(measured))
    state = read(state_path)
    assert state["waves_run"] == 1
    pbatch = read(run_root / "generations" / "g2" / "parent_batch_g2.json")
    print("[test] finalize ok: failure_stage=%s archive=%s parent_batch=%d"
          % (agg["failure_stage"], agg["archive_occupancy"]["cells_occupied"],
             pbatch["denominator"]))

    # -- parent array (small slice) ------------------------------------------
    entries = pbatch["entries"]
    sample = [i for i, e in enumerate(entries) if e["kind"] == "baseline"]
    sample += [i for i, e in enumerate(entries)
               if e["kind"] == "neighbour"][:8]
    t0 = time.time()
    for index in sample:
        run([HERE / "worker_parent.py", "--run-root", run_root,
             "--generation", 2, "--index", index],
            label="worker_parent[%d]" % index)
    print("[test] parent slice wall=%.1fs (%d of %d entries)"
          % (time.time() - t0, len(sample), len(entries)))

    # -- the canonical cycle (M11) -------------------------------------------
    packet_path = run_root / "generations" / "g2" / "ADOPTION_PACKET.json"
    if not packet_path.exists():
        pool = [r for r in rows if r["status"] == "MEASURED"]
        best = min(pool, key=vec) if pool else None
        packet = {
            "schema": "pdev217.adoption_packet.v1", "generation": 2,
            "wave": 1, "harness_validation": True,
            "winner": {"candidate_id": best["candidate_id"],
                       "digest": best["digest"], "config": best["config"],
                       "arm": best["arm"], "origin": best["origin"],
                       "change_class": best["change_class"],
                       "size": best["size"], "vector": dict(
                           zip(("failures", "work", "persistent_bytes"),
                               vec(best)))},
            "incumbent": {"digest": incumbent["digest"],
                          "config": incumbent["config"],
                          "vector": dict(zip(
                              ("failures", "work", "persistent_bytes"),
                              (inc_dev["n"] - inc_dev["success"],
                               inc_dev["work"], inc_dev["persistent_bytes"])))},
            "hostile_summary": {}, "shadow": {},
            "decision_question": "HARNESS VALIDATION packet (synthesized "
                                 "from the wave's best measured row); M11 "
                                 "re-measures independently.",
            "decision_file_schema": "pdev217.proxy_decision.v1"}
        packet_path.write_text(json.dumps(packet, indent=1, sort_keys=True))
        print("[test] synthesized harness packet from %s" % best["candidate_id"])
    # fail-closed first: no decision file -> cycle refuses
    run([HERE / "centre_cycle.py", "--run-root", run_root, "--generation", 2],
        expect=1, label="cycle_refuses_without_decision")
    decision = {"schema": "pdev217.proxy_decision.v1",
                "gate": "HUMAN_GATE_BYPASSED__MODEL_PROXY",
                "approved": True,
                "reason": "HARNESS VALIDATION: exercise the M11 path "
                          "end-to-end; not a campaign adoption decision.",
                "decided_by": "self-test",
                "decided_unix": int(time.time())}
    (run_root / "generations" / "g2" / "decision.json").write_text(
        json.dumps(decision, indent=1, sort_keys=True))
    t0 = time.time()
    out = run([HERE / "centre_cycle.py", "--run-root", run_root,
               "--generation", 2, "--freeze"], label="centre_cycle")
    print("[test] cycle wall=%.1fs %s" % (time.time() - t0, out.strip()))
    receipt = read(run_root / "generations" / "g2" / "cycle_receipt.json")
    assert receipt["terminal"] in ("DEVELOPMENT_CHANGE_ADOPTED",
                                   "EXTERNAL_ADOPTION_REJECTED",
                                   "SELF_EVOLUTION_REGRESSES",
                                   "SELF_DIAGNOSIS_NOT_IDENTIFIABLE"), receipt
    assert receipt["decision_gate"] == "HUMAN_GATE_BYPASSED__MODEL_PROXY"
    assert receipt["cold_restart"]["exact"] is True, receipt["cold_restart"]
    assert receipt["determinism"]["exact"] is True, receipt["determinism"]
    gen_ledger = read_jsonl(run_root / "GENERATION_LEDGER.jsonl")
    assert len(gen_ledger) == 1 and gen_ledger[0]["terminal"] == receipt["terminal"]
    state = read(state_path)
    assert state["attempted_cycles"] == 1
    lin = run_root / "lineage" / "CONTINUED"
    assert len(sorted((lin / "snapshots").glob("*.json"))) == 2
    assert (lin / "machine.json").exists() and (lin / "freeze.json").exists()
    print("[test] cycle A ok: terminal=%s generation_after=%d rollback=%s"
          % (receipt["terminal"], state["generation"],
             receipt["rollback_counterfactual"].get("exercised")))

    # -- forced-adoption harness leg (only if nothing was adopted) -----------
    if state["generation"] == 2:
        state = forced_adoption_leg(run_root, scratch)
    else:
        print("[test] cycle A already adopted; skipping forced leg")

    # -- one more wave at the CURRENT generation ------------------------------
    gen2 = state["generation"]
    wave2 = 2 if gen2 == 2 else 1     # wave numbering restarts per generation
    out = run([HERE / "centre_generate.py", "--run-root", run_root,
               "--generation", gen2, "--wave", wave2, "--salt", MASTER_SALT,
               "--quota", 1], label="centre_generate(next wave)")
    manifest = read(run_root / "manifests" / "BATCH.json")
    last = manifest["waves"][-1]
    assert last["generation"] == gen2 and last["wave"] == wave2
    if wave2 == 2:
        assert last["parent_denominator"] == 0, \
            "second wave of a generation must register parent_denominator=0"
    else:
        assert last["parent_denominator"] > 0
    w2dir = run_root / "generations" / ("g%d" % gen2) / "waves" / ("w%d" % wave2)
    batch2 = read(w2dir / "batch.json")
    for index in range(batch2["denominator"]):
        run([HERE / "worker_evaluate.py", "--run-root", run_root,
             "--generation", gen2, "--wave", wave2, "--index", index],
            label="next.eval[%d]" % index)
    run([HERE / "centre_aggregate.py", "--run-root", run_root,
         "--generation", gen2, "--wave", wave2, "--stage", "collect"],
        label="next.collect")
    vb2 = read(w2dir / "verify_batch.json")
    for index in range(vb2["denominator"]):
        run([HERE / "worker_verify.py", "--run-root", run_root,
             "--generation", gen2, "--wave", wave2, "--index", index],
            label="next.verify[%d]" % index)
    run([HERE / "centre_aggregate.py", "--run-root", run_root,
         "--generation", gen2, "--wave", wave2, "--stage", "finalize"],
        label="next.finalize")
    agg2 = read(w2dir / "aggregate.json")
    if wave2 == 2:
        suites_now = read(run_root / "generations" / "g2" / "suites.json")
        assert suites_now["suites"] == suites["suites"], \
            "suites are frozen per generation"
    else:
        s_old = {json.dumps(t, sort_keys=True) for t in suites["suites"]["dev"]}
        s_new = {json.dumps(t, sort_keys=True)
                 for t in read(run_root / "generations" / "g3"
                               / "suites.json")["suites"]["dev"]}
        assert not (s_old & s_new), "generation 3 must use fresh tasks"
    print("[test] next wave ok: g%d w%d failure_stage=%s archive=%s"
          % (gen2, wave2, agg2["failure_stage"],
             agg2["archive_occupancy"]["cells_occupied"]))
    print("[test] PASS")
    return 0


def forced_adoption_leg(run_root, scratch) -> dict:
    """Exercise the ADOPTED branch honestly: fresh suite from the ledger,
    directed neighbourhood measurement (scratch compute, harness-labelled),
    then the real M11 cycle on a dominating candidate."""
    import pdev_grammar as G
    import pdev_tasks as T
    from centre_generate import mix_tasks

    print("[test] forced-adoption leg: allocating fresh harness suites")
    ledger = T.TaskLedger(str(run_root / "task_ledger.json"))
    recipes = dict(T.SUITE_RECIPES)
    fresh = {name: mix_tasks(recipes, name, ledger,
                             "harness.cycleB.g2")
             for name in ("dev", "target", "preservation")}
    ledger.save()
    incumbent = read(run_root / "generations" / "g2" / "incumbent.json")
    config = incumbent["config"]
    base = measure(config, fresh["dev"])
    base_vec = (base["n"] - base["success"], base["resources"]["work"],
                base["resources"]["persistent_bytes"])
    best = None
    tried = 0
    for child in G.enumerate_neighbourhood(config, structural_only=True):
        if G.validate(child) or G.is_noop(child, config):
            continue
        tried += 1
        if tried > 24:
            break
        row = measure(child, fresh["dev"])
        if row["preservation_violations"]:
            continue
        v = (row["n"] - row["success"], row["resources"]["work"],
             row["resources"]["persistent_bytes"])
        if dominates(v, base_vec) and row["success"] >= base["success"]:
            best = (child, row, v)
            break
    if best is None:
        print("[test] SKIP forced-adoption leg: no dominating neighbour in "
              "24 structural tries (recorded, not a failure of the harness)")
        return read(state_path)

    child, row, v = best
    suites_payload = {"schema": "pdev217.suites.v1", "generation": 2,
                      "harness_validation": True,
                      "recipes": {"dev": recipes["dev"],
                                  "target": recipes["target"],
                                  "preservation": recipes["preservation"]},
                      "suites": fresh}
    gdir = run_root / "generations" / "g2"
    (gdir / "suites.json").write_text(json.dumps(suites_payload, indent=1,
                                                 sort_keys=True))
    inc_row = {"schema": "pdev217.incumbent.v1", "generation": 2,
               "config": config, "digest": G.digest(config),
               "suites": {"dev": {"n": base["n"], "success": base["success"],
                                  "violations": base["preservation_violations"],
                                  "work": base["resources"]["work"],
                                  "persistent_bytes":
                                      base["resources"]["persistent_bytes"]}}}
    (gdir / "incumbent.json").write_text(json.dumps(inc_row, indent=1,
                                                    sort_keys=True))
    packet = {"schema": "pdev217.adoption_packet.v1", "generation": 2,
              "wave": 1, "harness_validation": "forced-adoption-leg",
              "winner": {"candidate_id": "harness.forced.1",
                         "digest": G.digest(child), "config": child,
                         "arm": "harness", "origin": "human",
                         "change_class": G.infer_change_class(child, config),
                         "size": G.size_accounting(child, config),
                         "vector": dict(zip(("failures", "work",
                                             "persistent_bytes"), v))},
              "incumbent": {"digest": G.digest(config), "config": config,
                            "vector": dict(zip(("failures", "work",
                                                "persistent_bytes"),
                                               base_vec))},
              "hostile_summary": {}, "shadow": {},
              "decision_question": "HARNESS VALIDATION (forced-adoption "
                                   "leg): a measured-dominating neighbour; "
                                   "M11 re-measures independently.",
              "decision_file_schema": "pdev217.proxy_decision.v1"}
    (gdir / "ADOPTION_PACKET.json").write_text(json.dumps(packet, indent=1,
                                                          sort_keys=True))
    decision = {"schema": "pdev217.proxy_decision.v1",
                "gate": "HUMAN_GATE_BYPASSED__MODEL_PROXY", "approved": True,
                "reason": "HARNESS VALIDATION: exercise the ADOPTED branch.",
                "decided_by": "self-test", "decided_unix": int(time.time())}
    (gdir / "decision.json").write_text(json.dumps(decision, indent=1,
                                                   sort_keys=True))
    out = run([HERE / "centre_cycle.py", "--run-root", run_root,
               "--generation", 2, "--freeze"], label="centre_cycle(forced)")
    print("[test] forced cycle: %s" % out.strip())
    receipt = read(gdir / "cycle_receipt.json")
    assert receipt["terminal"] == "DEVELOPMENT_CHANGE_ADOPTED", receipt
    assert receipt["rollback_counterfactual"]["exercised"] is True, \
        "an adopted lineage must exercise the M11 rollback"
    assert receipt["rollback_counterfactual"]["m11_exact"] is True
    state = read(state_path)
    assert state["generation"] == 3 and state["adoptions"] == 1
    assert len(read_jsonl(run_root / "GENERATION_LEDGER.jsonl")) == 2
    return state


if __name__ == "__main__":
    raise SystemExit(main())
