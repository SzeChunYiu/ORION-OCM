"""FNA-6 scored runner.

Sequence (frozen by FREEZE_FNA6_V1.json):
  1. build population + stream once from the frozen salts;
  2. harness validation: (a) static-world no-alarm for every arm, (b) instrumented
     incumbent closure == production gated_closure on the scored stream, (c) mutant
     detection on the scored stream;
  3. scored replay per arm with the exact checker (judge-side oracle + impact cones,
     never charged);
  4. locality vs LOC_RANDOM_NULL, persistent bytes, sufficiency + terminals;
  5. write RESULTS_FNA6_V1.json / RESULTS_FNA6_V1.md.

Usage: python3 research/fna6-working-state-v1/run_fna6.py   (from the repo root)
"""
from __future__ import annotations

import datetime
import json
import platform
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
for p in (str(REPO / "src"), str(HERE)):
    if p not in sys.path:
        sys.path.insert(0, p)

import world  # noqa: E402
from actr import ActrArm  # noqa: E402
from arms import IncumbentArm, RescanArm  # noqa: E402
from blackboard import BlackboardArm  # noqa: E402
from contract import ExactChecker  # noqa: E402
from ocm.kso.navigation import gated_closure  # noqa: E402
from ocm.kso.revocation import impact_cone  # noqa: E402
from soar_wm import SoarArm  # noqa: E402

PARENT_LINE = ("P1A_BLACKBOARD_APPEND", "P1B_BLACKBOARD_VERSIONED", "P2_SOAR_WM",
               "P3_ACTR_STRICT_BUFFERS", "P3R_ACTR_REVALIDATE", "P4_FULL_RESCAN")


def build_arms():
    return [
        IncumbentArm(),
        BlackboardArm("P1A_BLACKBOARD_APPEND", versioned=False),
        BlackboardArm("P1B_BLACKBOARD_VERSIONED", versioned=True),
        SoarArm("P2_SOAR_WM", goal_scoped=True),
        SoarArm("P2_MUTANT_NO_GOAL_BINDING", goal_scoped=False),
        ActrArm("P3_ACTR_STRICT_BUFFERS", revalidate=False),
        ActrArm("P3R_ACTR_REVALIDATE", revalidate=True),
        RescanArm(),
    ]


def _serve_one(arm, ev, ks, revoked, checker, serve_idx):
    ob, seed, target = ev["ob"], ev["seed"], ev["target"]
    answer, consulted = arm.serve(ob, seed, target, ks, revoked)
    truth = world.oracle(ks, seed, target, revoked)
    v = checker.check(serve_idx, ob, target, answer, truth,
                      consulted, arm.resident(1 - ob))
    arm.res.verdicts.append(v)
    return v, consulted


def _changed_set(prev_ks, prev_revoked, ev, ks, revoked):
    """Judge-side set of atoms whose reachability status the event can change."""
    if ev["kind"] == "admission":
        out = set()
        for e in ev["_edges"]:
            out |= set(e.tails) | set(e.heads)
        return out
    if ev["kind"] == "revocation":
        rb, ra = frozenset(prev_revoked), frozenset(revoked)
        return {a.atom_id for a in ks.atoms
                if a.is_live(rb) and not a.is_live(ra)}
    e = ev.get("_edge_before")
    return set([ev["atom_id"]]) | (set(e.tails) | set(e.heads) if e is not None else set())


def score_arm(arm, field, stream):
    """Scored replay. Returns (per-event locality rows, harness agreement rows)."""
    arm.open(field, stream["seeds"])
    checker = ExactChecker()
    serve_idx = 0
    rows = []
    agree = []
    prev_ks, prev_revoked = field, frozenset()
    for kind, ev, ks, revoked in world.replay(field, stream):
        if kind == "serve":
            v, consulted = _serve_one(arm, ev, ks, revoked, checker, serve_idx)
            serve_idx += 1
            if arm.code in ("P0_INCUMBENT_ACTIVE_KSO", "P4_FULL_RESCAN"):
                prod = set(gated_closure(ks, [ev["seed"]], revoked))
                agree.append(set(consulted) == prod)
            rows.append({"kind": "serve", "verdict": v.as_dict()})
        else:
            if ev["kind"] == "drift":
                ev["_edge_before"] = prev_ks.edge_view.get(ev["edge_id"])
            changed = _changed_set(prev_ks, prev_revoked, ev, ks, revoked)
            cone = set(impact_cone(ks, changed))
            if ev["kind"] == "admission":
                arm.apply_admission(ev, ks, revoked)
            elif ev["kind"] == "revocation":
                arm.apply_revocation(ev, ks, revoked)
            else:
                arm.apply_drift(ev, ks, revoked)
            checker.note_update(ev["kind"])
            key = "%s:%d" % (ev["kind"], ev["after"])
            rows.append({"kind": "update", "event_key": key,
                         "changed": sorted(changed), "cone_size": len(cone),
                         "cone": sorted(cone)})
        prev_ks, prev_revoked = ks, frozenset(revoked)
    return rows, agree


def static_no_alarm(field, seeds):
    """Validation (a): update-free stream, every arm exact, zero checker events."""
    stream = world.static_stream(field, seeds)
    out = {}
    for arm in build_arms():
        if "MUTANT" in arm.code:
            continue  # labelled probe, not an arm; teeth proven by the fixture test
        arm.open(field, seeds)
        checker = ExactChecker()
        wrong = 0
        idx = 0
        for ev in stream["events"]:
            v, _ = _serve_one(arm, ev, field, frozenset(), checker, idx)
            idx += 1
            if not v.exact:
                wrong += 1
        events = sum(1 for r in arm.res.verdicts
                     if (not r.exact) or r.interference
                     or r.stale_revocation or r.merge_failure)
        out[arm.code] = {"exact": idx - wrong, "total": idx, "checker_events": events}
    return out


def locality_rows(arm, update_rows):
    touched = dict(arm.c.touched)
    vals = []
    for row in update_rows:
        t = touched.get(row["event_key"], set())
        if not t:
            vals.append(None)
            continue
        cone = set(row["cone"])
        vals.append(len(t & cone) / len(t))
    counted = [v for v in vals if v is not None]
    return vals, (sum(counted) / len(counted) if counted else None)


def locality_null(arm, update_rows, field_ids):
    """LOC_RANDOM_NULL: 20 random same-cardinality draws per update event."""
    touched = dict(arm.c.touched)
    means = []
    for row in update_rows:
        t = touched.get(row["event_key"], set())
        if not t:
            continue
        rng = random.Random(world.stable_seed(
            world.SALT_LOCNULL + "/" + arm.code + "/" + row["event_key"]))
        cone = set(row["cone"])
        draws = []
        for _ in range(20):
            s = set(rng.sample(field_ids, min(len(t), len(field_ids))))
            draws.append(len(s & cone) / len(s))
        means.append(sum(draws) / len(draws))
    return (sum(means) / len(means)) if means else None


def evaluate(summ: list, cost0: int) -> dict:
    p0 = next(s for s in summ if s["arm"] == "P0_INCUMBENT_ACTIVE_KSO")
    for s in summ:
        s["cost_vs_p0"] = (round(s["total_ops"] / cost0, 3) if cost0 else None)
        s["flags"] = []
        if s["sufficient"] and cost0 and s["total_ops"] > 10.0 * cost0:
            s["flags"].append("STATE_SEARCH_COST_DOMINATES")
        if s["locality_in_cone_fraction"] is not None and s["locality_null_mean"] is not None:
            if (s["locality_in_cone_fraction"] >= 0.90
                    and s["locality_in_cone_fraction"] >= 2.0 * s["locality_null_mean"]):
                s["flags"].append("LOCALITY_SUPPORTED")
    winners = [s["arm"] for s in summ
               if s["arm"] in PARENT_LINE and s["sufficient"]
               and cost0 and s["total_ops"] <= 2.0 * cost0]
    if winners:
        overall = "PARENT_SUFFICIENT_FOR_working_state"
    elif p0["sufficient"]:
        overall = "NON_NEURAL_FUNCTIONAL_RECONSTRUCTION_SUPPORTED_working_state"
        winners = ["P0_INCUMBENT_ACTIVE_KSO"]
    else:
        overall = "NO_FUNCTIONAL_PARITY_working_state"
        winners = []
    return {"overall": overall, "winning_arms": winners}


def main() -> int:
    field, meta = world.build_field()
    stream = world.build_stream(field)
    seeds = stream["seeds"]
    field_ids = list(field.ids)

    serves = [e for e in stream["events"] if e["kind"] == "serve"]
    updates = [e for e in stream["events"] if e["kind"] != "serve"]
    stream_stats = {
        "n_serves": len(serves),
        "n_updates": len(updates),
        "n_admissions": sum(1 for e in updates if e["kind"] == "admission"),
        "n_revocations": sum(1 for e in updates if e["kind"] == "revocation"),
        "n_drift": sum(1 for e in updates if e["kind"] == "drift"),
        "polarity_supported": sum(1 for e in serves if e["truth"]),
        "polarity_not_supported": sum(1 for e in serves if not e["truth"]),
        "world_meta": meta,
        "admission_edges_total": sum(len(e["edges"]) for e in updates
                                     if e["kind"] == "admission"),
    }

    validation = {"static_no_alarm": static_no_alarm(field, seeds)}
    static_ok = all(v["exact"] == v["total"] and v["checker_events"] == 0
                    for v in validation["static_no_alarm"].values())
    validation["static_no_alarm_pass"] = bool(static_ok)

    arms = build_arms()
    rows_by_arm = {}
    agree_by_arm = {}
    for arm in arms:
        rows, agree = score_arm(arm, field, stream)
        rows_by_arm[arm.code] = rows
        if agree:
            agree_by_arm[arm.code] = all(agree)
    validation["incumbent_closure_agrees_production"] = agree_by_arm.get(
        "P0_INCUMBENT_ACTIVE_KSO", False)
    validation["rescan_closure_agrees_production"] = agree_by_arm.get(
        "P4_FULL_RESCAN")
    validation["mutant_detected"] = bool(any(
        r["verdict"]["interference"] for r in rows_by_arm["P2_MUTANT_NO_GOAL_BINDING"]
        if r["kind"] == "serve"))
    validation["mutant_note"] = (
        "P2_MUTANT_NO_GOAL_BINDING is a labelled probe, never a result"
        if validation["mutant_detected"]
        else "MUTANT_NOT_EXPRESSED_ON_STREAM: detector teeth rest on the "
             "forced-crosstalk fixture in test_fna6.py")

    if not validation["incumbent_closure_agrees_production"]:
        results = {"schema": "ocm.fna6.working-state.results.v1",
                   "terminal": "CANNOT_CHECK_HARNESS_DISAGREES",
                   "validation": validation}
        (HERE / "RESULTS_FNA6_V1.json").write_text(
            json.dumps(results, indent=2, sort_keys=True) + "\n")
        print("HARNESS DISAGREES — scored run aborted")
        return 2

    summ = []
    verdict_log = {}
    for arm in arms:
        rows = rows_by_arm[arm.code]
        update_rows = [r for r in rows if r["kind"] == "update"]
        _, loc = locality_rows(arm, update_rows)
        nullm = locality_null(arm, update_rows, field_ids)
        s = arm.res.summary()
        s["sufficient"] = arm.res.sufficient()
        s["locality_in_cone_fraction"] = (round(loc, 4) if loc is not None else None)
        s["locality_null_mean"] = (round(nullm, 4) if nullm is not None else None)
        s["persistent_bytes"] = world.measure_bytes(arm.persistent_state())
        summ.append(s)
        verdict_log[arm.code] = [r for r in rows if r["kind"] == "serve"]
    cost0 = next(s["total_ops"] for s in summ if s["arm"] == "P0_INCUMBENT_ACTIVE_KSO")
    terminals = evaluate(summ, cost0)

    by = lambda c: next(s for s in summ if s["arm"] == c)
    chain = [
        {"lever": "L1_blackboard_versioning",
         "from": "P1A_BLACKBOARD_APPEND", "to": "P1B_BLACKBOARD_VERSIONED",
         "before_sufficient": by("P1A_BLACKBOARD_APPEND")["sufficient"],
         "after_sufficient": by("P1B_BLACKBOARD_VERSIONED")["sufficient"]},
        {"lever": "L2_actr_retrieval_revalidation",
         "from": "P3_ACTR_STRICT_BUFFERS", "to": "P3R_ACTR_REVALIDATE",
         "before_sufficient": by("P3_ACTR_STRICT_BUFFERS")["sufficient"],
         "after_sufficient": by("P3R_ACTR_REVALIDATE")["sufficient"]},
    ]

    results = {
        "schema": "ocm.fna6.working-state.results.v1",
        "freeze_file": "FREEZE_FNA6_V1.json",
        "freeze_sha256": __import__("hashlib").sha256(
            (HERE / "FREEZE_FNA6_V1.json").read_bytes()).hexdigest(),
        "run_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "python": platform.python_version(),
        "stream_stats": stream_stats,
        "validation": validation,
        "arms": {s["arm"]: s for s in summ},
        "terminals": terminals,
        "engineering_chain": chain,
        "superseded_defect_runs": [{
            "run": 1,
            "date_utc": "2026-09-09",
            "status": "SUPERSEDED_DEFECT_RUN",
            "symptom": "static no-alarm control failed: P2_SOAR_WM 45/48 on the scored "
                       "stream; P3R_ACTR_REVALIDATE 46/48 and P3_ACTR_STRICT_BUFFERS "
                       "40/48 on the static control",
            "root_causes": [
                "P2 soar_wm._retract_unsupported omitted the atom-live enabling "
                "condition declared in the arm's own production spec, so nodes whose "
                "atom warrant died (drift/revocation liveness flip) survived "
                "structurally -> 3 stale positives at ob1 serves 33/43/45",
                "P3R actr._node_valid validated by recursion with an in-progress "
                "pessimistic memo over a cyclic graph; memo entries written while an "
                "ancestor was still in progress poisoned later reads -> false "
                "negatives (stream serves 9/25/29/37 and 2 static wrongs). Replaced "
                "by an exact iterative pending-counter closure pass",
                "P3 actr DM encoding omitted build-time warrant liveness entirely (no "
                "head-atom live gate, no dead-edge filter): on the static world the "
                "arm over-derived through the population's 76 zero-warrant atoms -> 8 "
                "stale positives",
            ],
            "remedy": "arm implementation fixes only (soar_wm.py, actr.py); freeze, "
                      "salts, stream, targets and thresholds untouched — MSC #216 "
                      "defect-run supersession precedent",
        }, {
            "run": 2,
            "date_utc": "2026-09-09",
            "status": "SUPERSEDED_DEFECT_RUN",
            "symptom": "all decisions, costs, bytes, locality and terminals valid, but "
                       "the working-set-occupancy instrument was dead: no arm ever "
                       "called the resident hooks, so working_set_peak read 0 for "
                       "every arm in the printed table",
            "root_causes": [
                "contract.Counters exposed resident_add/resident_remove hooks that no "
                "arm wired; the declared working-set-occupancy metric was never "
                "measured",
            ],
            "remedy": "instrument wiring only (contract.resident_sync declared at each "
                      "serve boundary by every arm; bookkeeping, never charged as ops); "
                      "decisions, thresholds, salts, stream untouched — this run was "
                      "repeated so the shipped artifact carries a live occupancy "
                      "column",
        }],
        "notes": [
            "oracle and impact cones are judge-side and never charged to arms",
            "P2_MUTANT_NO_GOAL_BINDING is a labelled interference probe, never a result",
            "locality null = LOC_RANDOM_NULL, 20 salt-seeded draws per update event",
        ],
        "verdict_log": verdict_log,
    }
    (HERE / "RESULTS_FNA6_V1.json").write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n")
    write_md(results)
    print("terminal:", terminals["overall"], terminals["winning_arms"])
    for s in summ:
        print("  %-28s exact %2d/%d suff=%-5s ops=%7d xP0=%6.2f bytes=%7d loc=%s" % (
            s["arm"], s["decisions_exact"], s["decisions_total"], s["sufficient"],
            s["total_ops"], s["total_ops"] / cost0, s["persistent_bytes"],
            s["locality_in_cone_fraction"]))
    return 0


def write_md(results: dict) -> None:
    lines = ["# FNA-6 working-state results (v1)", ""]
    lines.append("Freeze: FREEZE_FNA6_V1.json (sha256 %s)" % results["freeze_sha256"][:16])
    lines.append("")
    lines.append("## Terminal")
    lines.append("")
    lines.append("- **%s** — %s" % (results["terminals"]["overall"],
                                    ", ".join(results["terminals"]["winning_arms"])))
    lines.append("")
    lines.append("## Harness validation")
    lines.append("")
    v = results["validation"]
    lines.append("- static no-alarm pass: %s" % v["static_no_alarm_pass"])
    lines.append("- incumbent closure == production gated_closure: %s"
                 % v["incumbent_closure_agrees_production"])
    lines.append("- mutant detected on stream: %s" % v["mutant_detected"])
    lines.append("")
    lines.append("## Arms (48 decisions each; ops whole-lifecycle; loc = in-cone fraction, null in parentheses)")
    lines.append("")
    lines.append("| arm | exact | wrong | stale-rev | merge-fail | interfer | ops | xP0 | peak-WS | bytes | loc (null) | flags |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    cost0 = results["arms"]["P0_INCUMBENT_ACTIVE_KSO"]["total_ops"]
    for s in results["arms"].values():
        lines.append("| %s | %d | %d | %d | %d | %d | %d | %.2f | %d | %d | %s (%s) | %s |" % (
            s["arm"], s["decisions_exact"], s["wrong_total"],
            s["stale_revocation_decisions"], s["merge_failures"],
            s["interference_events"], s["total_ops"], s["total_ops"] / cost0,
            s["working_set_peak"], s["persistent_bytes"],
            s["locality_in_cone_fraction"], s["locality_null_mean"],
            ",".join(s["flags"]) or "-"))
    lines.append("")
    lines.append("## Engineering chain (pre-registered levers)")
    lines.append("")
    for c in results["engineering_chain"]:
        lines.append("- %s: %s (sufficient=%s) -> %s (sufficient=%s)" % (
            c["lever"], c["from"], c["before_sufficient"], c["to"], c["after_sufficient"]))
    lines.append("")
    lines.append("## Superseded defect runs")
    lines.append("")
    for d in results.get("superseded_defect_runs", []):
        lines.append("- run %d (%s) %s — %s Root causes and remedy recorded in "
                     "RESULTS_FNA6_V1.json; freeze, salts, stream and thresholds "
                     "untouched." % (d["run"], d["date_utc"], d["status"],
                                     d["symptom"] + "."))
    lines.append("")
    st = results["stream_stats"]
    lines.append("## Stream")
    lines.append("")
    lines.append("- %d serves (%d supported / %d not), %d updates (%d admissions / %d revocations / %d drift), %d admitted edges"
                 % (st["n_serves"], st["polarity_supported"], st["polarity_not_supported"],
                    st["n_updates"], st["n_admissions"], st["n_revocations"], st["n_drift"],
                    st["admission_edges_total"]))
    lines.append("")
    (HERE / "RESULTS_FNA6_V1.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    sys.exit(main())
