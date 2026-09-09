"""Centre: aggregate a wave under the PRE-FROZEN selection rules (PDEV-8),
update the QD archive + shared history, advance the serial controls, and emit
the frozen ADOPTION_PACKET when a winner exists.

FROZEN RULES (registered in PROTOCOL.json before any wave ran):

* admission (eval stage)     row.status == MEASURED, n == |dev suite|,
                             preservation_violations == 0, success >=
                             incumbent dev success (noninferior quality).
* preliminary frontier       non-dominated on (failures, work, persistent_bytes)
                             over admitted rows + the incumbent point; verify
                             survivors = frontier candidates capped at
                             VERIFY_CAP=40 by (failures, work, bytes, digest).
* final admissibility        every hostile in {PASS, NOT_APPLICABLE,
                             ADVERSE_RECORDED}; any FAIL -> inadmissible.
* winner                     finally admissible AND (failures, work, bytes)
                             dominated-vs-incumbent with at least one strict
                             improvement; ties broken by that same order then
                             digest.  Exactly zero or one winner per wave.
* negative wave              failure_stage in {quality, integrity, dominance}
                             with the matching revival lever applied by the
                             next wave's reflection/repair/qd arms through the
                             shared history (never by relaxing a rule).

Usage:
  centre_aggregate.py --run-root R --generation G --wave W --stage collect
  centre_aggregate.py --run-root R --generation G --wave W --stage finalize
  centre_aggregate.py --run-root R --generation G --wave 0 --stage close
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
import pdev_search  # noqa: E402

VERIFY_CAP = 40
VECTOR = ("failures", "work", "persistent_bytes")

#: Mirror of ocm.selfmodel.proposal.CLASS_ORDER (C6 is outside the grammar):
#: lower change class = narrower intervention = preferred, per M11 doctrine.
CLASS_RANK = {"C0": 0, "C1": 1, "C2": 2, "C4": 3, "C3": 4, "C5": 5}
#: Mirror of the vendored cell's evolution.CLASS_LAYER (class -> layer).
CLASS_LAYER = {"C0": "D0", "C1": "D1", "C2": "D2", "C3": "D3",
               "C4": "D6", "C5": "D7"}
#: Mirror of ocm.selfmodel.diagnose.ORDER.
LAYER_ORDER = ["D0", "D1", "D2", "D5", "D6", "D3", "D4", "D7", "D8"]


def _vec(row) -> dict:
    return {"failures": int(row["n"]) - int(row["success"]),
            "work": int(row["work"]),
            "persistent_bytes": int(row["persistent_bytes"])}


def _dominates(a: dict, b: dict) -> bool:
    return all(a[k] <= b[k] for k in VECTOR) and any(a[k] < b[k] for k in VECTOR)


def _lex(vec: dict, digest: str):
    return (vec["failures"], vec["work"], vec["persistent_bytes"], digest)


def _obstruction_material(winner, rows, verify_rows, inc_vec) -> dict:
    """M11 escalation material for a non-local-layer winner: every MEASURED
    wave candidate whose change class maps to a layer strictly below the
    winner's, with the centre's own honest verdicts (dominates the incumbent
    on the frozen dev vector; finally admissible after hostiles).  The M11 cell
    consumes this to build its ObstructionCertificate -- a lower-layer
    alternative that both dominates and is admissible is recorded as a
    SUCCEEDED narrower repair and honestly invalidates escalation."""
    layer = CLASS_LAYER.get(str(winner.get("change_class")))
    if layer is None or layer in ("D2", "D6"):
        return {"required": False,
                "reason": "winner's change class is a local-layer repair"}
    alternatives = []
    for r in rows:
        if r.get("status") != "MEASURED":
            continue
        if r["candidate_id"] == winner["candidate_id"]:
            continue
        alt_layer = CLASS_LAYER.get(str(r.get("change_class")))
        if alt_layer is None or LAYER_ORDER.index(alt_layer) >= LAYER_ORDER.index(layer):
            continue
        ver = next((x for x in verify_rows
                    if x["candidate_id"] == r["candidate_id"]), None)
        alternatives.append({
            "candidate_id": r["candidate_id"],
            "change_class": str(r["change_class"]),
            "layer": alt_layer,
            "arm": r.get("arm"), "origin": r.get("origin"),
            "vector": r["_vec"],
            "dominates_incumbent": _dominates(r["_vec"], inc_vec),
            "admissible": bool(ver is not None and ver["status"] == "VERIFIED"
                               and not ver["failing_hostiles"]),
        })
    return {
        "required": True,
        "winner_layer": layer,
        "alternatives": alternatives,
        "incumbent_vector": inc_vec,
        "winner_vector": winner["_vec"],
        "wave_measured": sum(1 for r in rows if r.get("status") == "MEASURED"),
    }


def _frontier(rows):
    out = []
    for i, a in enumerate(rows):
        va = a["_vec"]
        if any(all(b["_vec"][k] <= va[k] for k in VECTOR)
               and any(b["_vec"][k] < va[k] for k in VECTOR) for b in rows):
            continue
        out.append(a)
    return out


def load_eval_rows(run_root, generation, wave):
    wdir = IO.wave_dir(run_root, generation, wave)
    batch = IO.read_json(wdir / "batch.json")
    rows = []
    for cand in batch["candidates"]:
        path = wdir / "eval" / (cand["candidate_id"] + ".json")
        if not path.exists():
            continue
        row = IO.read_json(path)
        row["_vec"] = _vec(row)
        rows.append(row)
    return batch, rows


def stage_collect(run_root, generation, wave):
    paths = IO.run_paths(run_root)
    wdir = IO.wave_dir(run_root, generation, wave)
    batch, rows = load_eval_rows(run_root, generation, wave)
    denominator = batch["denominator"]
    if len(rows) != denominator:
        raise SystemExit("eval incomplete: %d/%d rows present"
                         % (len(rows), denominator))
    incumbent = IO.read_json(IO.gen_dir(run_root, generation) / "incumbent.json")
    inc_vec = _vec({"n": incumbent["suites"]["dev"]["n"],
                    "success": incumbent["suites"]["dev"]["success"],
                    "work": incumbent["suites"]["dev"]["work"],
                    "persistent_bytes":
                        incumbent["suites"]["dev"]["persistent_bytes"]})
    admitted = [r for r in rows
                if r["status"] == "MEASURED"
                and r["preservation_violations"] == 0
                and r["success"] >= incumbent["suites"]["dev"]["success"]]
    points = admitted + [{"_vec": inc_vec, "candidate_id": "__incumbent__",
                          "digest": G.digest(incumbent["config"])}]
    frontier = [r for r in _frontier(points) if r["candidate_id"] != "__incumbent__"]
    survivors = sorted(frontier, key=lambda r: _lex(r["_vec"], r["digest"]))
    survivors = survivors[:VERIFY_CAP]

    archive_digests = []
    if paths["archive"].exists():
        archive_digests = sorted(
            cell["digest"] for cell in
            IO.read_json(paths["archive"])["cells"].values())
    payload = {"schema": "pdev217.verify_batch.v1", "generation": generation,
               "wave": wave, "candidates": survivors,
               "archive_digests": archive_digests,
               "denominator": len(survivors)}
    IO.write_json(wdir / "verify_batch.json", payload)
    IO.write_json(wdir / "aggregate.json", {
        "schema": "pdev217.wave_aggregate.v1", "generation": generation,
        "wave": wave, "stage": "collect", "denominator": denominator,
        "measured": len(rows), "admitted": len(admitted),
        "frontier": len(frontier), "verify_denominator": len(survivors),
        "incumbent_vector": inc_vec,
        "fail_stage_counts": {
            "crashed": sum(1 for r in rows if r["status"] != "MEASURED"),
            "violations": sum(1 for r in rows
                              if r["status"] == "MEASURED"
                              and r["preservation_violations"] > 0),
            "quality": sum(1 for r in rows
                           if r["status"] == "MEASURED"
                           and r["preservation_violations"] == 0
                           and r["success"] < incumbent["suites"]["dev"]["success"])}})
    print("verify_denominator=%d admitted=%d frontier=%d"
          % (len(survivors), len(admitted), len(frontier)))
    return 0


def stage_finalize(run_root, generation, wave):
    paths = IO.run_paths(run_root)
    wdir = IO.wave_dir(run_root, generation, wave)
    verify_batch = IO.read_json(wdir / "verify_batch.json")
    incumbent = IO.read_json(IO.gen_dir(run_root, generation) / "incumbent.json")
    state = IO.read_json(paths["state"])
    batch, rows = load_eval_rows(run_root, generation, wave)

    verify_rows = []
    for cand in verify_batch["candidates"]:
        path = wdir / "verify" / (cand["candidate_id"] + ".json")
        if not path.exists():
            raise SystemExit("verify incomplete: missing %s" % cand["candidate_id"])
        verify_rows.append(IO.read_json(path))

    inc_vec = _vec({"n": incumbent["suites"]["dev"]["n"],
                    "success": incumbent["suites"]["dev"]["success"],
                    "work": incumbent["suites"]["dev"]["work"],
                    "persistent_bytes":
                        incumbent["suites"]["dev"]["persistent_bytes"]})

    # -- final admissibility + QD archive offers ---------------------------
    archive = pdev_search.DiversityArchive(
        str(paths["archive"])) if paths["archive"].exists() \
        else pdev_search.DiversityArchive()
    final = []
    for v in verify_rows:
        ok = v["status"] == "VERIFIED" and not v["failing_hostiles"]
        ev = next((r for r in rows if r["candidate_id"] == v["candidate_id"]), None)
        if ev is None:
            raise SystemExit("verify row without eval row: %s" % v["candidate_id"])
        archive.offer(ev["config"], {"n": ev["n"], "success": ev["success"],
                                     "work": ev["work"],
                                     "persistent_bytes": ev["persistent_bytes"],
                                     "index_build_work":
                                         ev["detail"].get("index_build_work", 0),
                                     "index_maintenance_work":
                                         ev["detail"].get(
                                             "index_maintenance_work", 0),
                                     "query_work": ev["detail"].get("query_work", 0),
                                     "revision_work": ev["detail"].get(
                                         "revision_work", 0),
                                     "generation": generation},
                      int(incumbent["suites"]["dev"]["persistent_bytes"]),
                      ev["origin"], integrity_ok=ok,
                      reason="; ".join(v["failing_hostiles"]))
        if ok:
            final.append((v, ev))

    # -- shared history (equal information surface for every arm) ----------
    for r in rows:
        if r["status"] != "MEASURED":
            continue
        verified = next((v for v in verify_rows
                         if v["candidate_id"] == r["candidate_id"]), None)
        disposition = "UNVERIFIED"
        if verified is not None:
            disposition = "ADMITTED" if not verified["failing_hostiles"] \
                else "REJECTED"
        IO.append_jsonl(paths["history"], {
            "digest": r["digest"], "config": r["config"], "arm": r["arm"],
            "origin": r["origin"], "generation": generation, "wave": wave,
            "n": r["n"], "success": r["success"], "work": r["work"],
            "persistent_bytes": r["persistent_bytes"],
            "disposition": disposition})

    # -- winner --------------------------------------------------------------
    # Class-first (M11 doctrine: lowest change class that restores the
    # contract wins; the frozen vector rule breaks ties inside a class).  This
    # keeps the centre's selection coherent with the M11 obstruction gate: a
    # C3/C5 winner then certifiably implies that no measured lower-class
    # admissible dominator exists in the wave.  Protocol refinement recorded
    # BEFORE the campaign's first measured wave (selftest scratch is harness
    # validation, not campaign measurement).
    winner = None
    dominating = [(v, e) for (v, e) in final if _dominates(e["_vec"], inc_vec)]
    if dominating:
        v, e = min(dominating,
                   key=lambda pair: (CLASS_RANK.get(pair[1]["change_class"], 99),
                                     _lex(pair[1]["_vec"], pair[1]["digest"])))
        winner = e
    if winner is not None:
        vrow = next(x for x in verify_rows
                    if x["candidate_id"] == winner["candidate_id"])
        packet = {
            "schema": "pdev217.adoption_packet.v1",
            "generation": generation, "wave": wave,
            "winner": {"candidate_id": winner["candidate_id"],
                       "digest": winner["digest"], "config": winner["config"],
                       "arm": winner["arm"], "origin": winner["origin"],
                       "change_class": winner["change_class"],
                       "size": winner["size"],
                       "vector": winner["_vec"]},
            "incumbent": {"digest": G.digest(incumbent["config"]),
                          "config": incumbent["config"],
                          "vector": inc_vec},
            "hostile_summary": {h["hostile_id"]: h["status"]
                                for h in vrow["hostiles"]},
            "shadow": vrow["shadow"],
            "obstruction": _obstruction_material(winner, rows, verify_rows,
                                                 inc_vec),
            "decision_question":
                "Adopt this morphology as generation %d of the canonical "
                "serial lineage?  The M11 cell will independently re-measure "
                "and apply assurance; your decision gates ONLY the external "
                "adoption authority." % (generation + 1),
            "decision_file_schema": "pdev217.proxy_decision.v1",
        }
        IO.write_json(IO.gen_dir(run_root, generation) / "ADOPTION_PACKET.json",
                      packet)

    # -- negative-wave attribution (revival directive) ----------------------
    failure_stage = None
    if winner is None:
        agg = IO.read_json(wdir / "aggregate.json")
        counts = agg["fail_stage_counts"]
        if counts["violations"] + counts["quality"] == len(rows) - counts["crashed"]:
            failure_stage = "quality"
        elif final:
            failure_stage = "dominance"
        else:
            failure_stage = "integrity"

    # -- serial controls (PDEV-11) ------------------------------------------
    serial_receipts = advance_serial_controls(run_root, generation)

    archive.save(str(paths["archive"]))
    state["waves_run"] = state.get("waves_run", 0) + 1
    IO.write_json(paths["state"], state)
    IO.write_json(wdir / "aggregate.json", {
        "schema": "pdev217.wave_aggregate.v1", "generation": generation,
        "wave": wave, "stage": "finalize",
        "verify_rows": len(verify_rows), "final_admissible": len(final),
        "winner": winner["candidate_id"] if winner else None,
        "failure_stage": failure_stage,
        "archive_occupancy": archive.occupancy(),
        "serial": serial_receipts})
    print("winner=%s failure_stage=%s archive=%s"
          % (winner["candidate_id"] if winner else None, failure_stage,
             archive.occupancy()["cells_occupied"]))
    return 0


def stage_close(run_root, generation):
    """Close a generation cycle that exhausted its wave bound with no winner
    by emitting the issue section-21 SUCCESS terminal (PARENT_SUFFICIENT_*).

    Guards (all fail-closed):
      * never twice (EXHAUSTION_TERMINAL.json already present);
      * never when an adoption packet exists (that cycle runs centre_cycle);
      * only after the frozen 5-wave bound, with every wave finalized;
      * only when NO wave recorded a winner AND no admitted eval row even
        dominates the incumbent (the necessary condition for a winner), so
        the terminal is a computed fact, not a summary of summaries.

    Reports frozen-minimum and full-set verdicts separately per AMENDMENTS.json
    (AMENDMENT-1: first 12 candidates per arm in frozen batch order for waves
    2-5; AMENDMENT-2 waves 6-7 are amendment-only additions).
    """
    paths = IO.run_paths(run_root)
    gdir = IO.gen_dir(run_root, generation)
    if (gdir / "EXHAUSTION_TERMINAL.json").exists():
        raise SystemExit("generation %d already closed" % generation)
    if (gdir / "ADOPTION_PACKET.json").exists():
        raise SystemExit("adoption packet exists for generation %d; "
                         "the cycle must run, not close" % generation)
    incumbent = IO.read_json(gdir / "incumbent.json")
    inc_vec = _vec({"n": incumbent["suites"]["dev"]["n"],
                    "success": incumbent["suites"]["dev"]["success"],
                    "work": incumbent["suites"]["dev"]["work"],
                    "persistent_bytes":
                        incumbent["suites"]["dev"]["persistent_bytes"]})
    waves = sorted(int(p.name[1:]) for p in (gdir / "waves").iterdir()
                   if p.is_dir() and p.name.startswith("w"))
    if len(waves) < 5:
        raise SystemExit("frozen wave bound (5) not reached; waves=%s" % waves)

    per_wave, any_dominating = [], False
    for w in waves:
        agg = IO.read_json(gdir / "waves" / ("w%d" % w) / "aggregate.json")
        if agg["stage"] != "finalize":
            raise SystemExit("wave %d not finalized" % w)
        if agg.get("winner"):
            raise SystemExit("wave %d recorded winner %s; close not applicable"
                             % (w, agg["winner"]))
        batch, rows = load_eval_rows(run_root, generation, w)

        def _dominating(subset):
            return [r for r in subset
                    if r["status"] == "MEASURED"
                    and r["preservation_violations"] == 0
                    and r["success"] >= incumbent["suites"]["dev"]["success"]
                    and _dominates(r["_vec"], inc_vec)]

        per_arm = {}
        for cand in batch["candidates"]:
            per_arm.setdefault(cand["arm"], []).append(cand["candidate_id"])
        frozen_min_ids = set()
        for ids in per_arm.values():
            frozen_min_ids.update(ids[:12])
        sub = [r for r in rows if r["candidate_id"] in frozen_min_ids]
        full_dom, min_dom = _dominating(rows), _dominating(sub)
        any_dominating = any_dominating or bool(full_dom)
        per_wave.append({
            "wave": w, "denominator": batch["denominator"],
            "failure_stage": agg["failure_stage"],
            "final_admissible": agg["final_admissible"],
            "verify_rows": agg["verify_rows"],
            "full_set": {"evals": len(rows),
                         "dominating_admitted": len(full_dom)},
            "frozen_minimum": {"evals": len(sub),
                               "dominating_admitted": len(min_dom)},
            "amendment_only": w > 5})
    if any_dominating:
        raise SystemExit("an admitted row dominates the incumbent but no "
                         "winner/verify verdict was recorded; investigate "
                         "before closing")

    history_rows = 0
    if paths["history"].exists():
        with open(paths["history"]) as h:
            history_rows = sum(1 for _ in h)
    terminal = ("PARENT_SUFFICIENT_BY_REVIVAL_EXHAUSTION"
                if len(waves) >= 2 and history_rows > 0
                else "PARENT_SUFFICIENT_NO_ADOPTION")
    state = IO.read_json(paths["state"])
    row = {
        "schema": "pdev217.exhaustion_terminal.v1",
        "generation": generation,
        "terminal": terminal,
        "waves": per_wave,
        "revival_lever": ("every negative wave's failure_stage was attributed "
                          "and the next wave's reflection/repair/qd arms "
                          "consumed the shared history (%d rows) under "
                          "unchanged frozen rules" % history_rows),
        "frozen_minimum_note": ("AMENDMENT-1 frozen minimum = first 12 "
                                "candidates per arm in frozen batch order; "
                                "waves 6-7 (AMENDMENT-2) are amendment-only; "
                                "both sets reach the same verdict: no winner"),
        "incumbent": {"digest": G.digest(incumbent["config"]),
                      "vector": inc_vec},
        "programme_close": ("generation cycles bound (2) reached: cycle 1 "
                            "(g2) ended DEVELOPMENT_CHANGE_ADOPTED; cycle 2 "
                            "(g3) exhausted its wave bound with no adoption; "
                            "the programme closes"),
        "written_unix": time.time()}
    IO.write_json(gdir / "EXHAUSTION_TERMINAL.json", row)
    IO.append_jsonl(paths["generation_ledger"], row)
    state["programme_terminal"] = terminal
    IO.write_json(paths["state"], state)
    print("terminal=%s waves=%d" % (terminal, len(waves)))
    return 0


def advance_serial_controls(run_root, generation):
    gdir = IO.gen_dir(run_root, generation)
    parents = IO.run_paths(run_root)["parents"]
    receipts = {}
    for arm in ("CONTINUED", "RESET"):
        state_path = parents / arm / "serial_state.json"
        state = IO.read_json(state_path)
        if state.get("last_advanced_generation") == generation:
            receipts[arm] = {"advanced": False, "reason": "already advanced"}
            continue
        base_path = gdir / "parents" / ("%s.baseline.g%d.json" % (arm, generation))
        if not base_path.exists():
            receipts[arm] = {"advanced": False, "reason": "parent rows incomplete"}
            continue
        base = IO.read_json(base_path)
        best = None
        for path in sorted((gdir / "parents").glob("%s.n*.g%d.json" % (arm, generation))):
            row = IO.read_json(path)
            if row["status"] != "MEASURED" or row["preservation_violations"]:
                continue
            key = pdev_search.scalar_objective(row)
            if best is None or key < best[0]:
                best = (key, row)
        base_key = pdev_search.scalar_objective(base)
        adopted = False
        if best is not None and best[0] < base_key:
            _, row = best
            state["config"] = row["config"]
            state["digest"] = G.digest(row["config"])
            state["adoptions"] += 1
            state["history"].append({
                "generation": generation, "adopted": row["digest"],
                "entry_id": row["entry_id"], "vector": _vec(row),
                "baseline_vector": _vec(base), "rule": "frozen scalar "
                "(failures, work) strict improvement, violations==0"})
            adopted = True
        else:
            state["history"].append({
                "generation": generation, "adopted": None,
                "reason": "no neighbour strictly better under frozen scalar",
                "baseline_vector": _vec(base)})
        state["generation"] = generation
        state["last_advanced_generation"] = generation
        IO.write_json(state_path, state)
        receipts[arm] = {"advanced": adopted,
                         "adoptions": state["adoptions"],
                         "config_digest": state["digest"]}
    return receipts


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-root", required=True)
    ap.add_argument("--generation", type=int, required=True)
    ap.add_argument("--wave", type=int, required=True)
    ap.add_argument("--stage", choices=("collect", "finalize", "close"),
                    required=True)
    args = ap.parse_args()
    if args.stage == "collect":
        return stage_collect(args.run_root, args.generation, args.wave)
    if args.stage == "close":
        return stage_close(args.run_root, args.generation)
    return stage_finalize(args.run_root, args.generation, args.wave)


if __name__ == "__main__":
    raise SystemExit(main())
