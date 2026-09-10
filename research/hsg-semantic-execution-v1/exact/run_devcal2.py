#!/usr/bin/env python3
"""DEV-CAL-2 carrier-attribution knockout runner (#323; freeze
DEV_CAL_2_KNOCKOUT_PROTOCOL_FREEZE_V1.json -- every clause binding).

Executes the parent terminal TRANSFERABLE_HEADROOM_OCM_MISSES: the benchmark
provably carries structural transferable headroom (cell-B oracle +97.0%
[96.5, 97.4] vs RESET, DEVCAL1 PR #328 cc3af86d) that an OCM-side history
cannot reach.  This study grants the OCM side EXACTLY ONE interface component
per arm -- AS DATA (adapter records), never as a code change -- and
identifies the carrier.

World matrix: IDENTICAL to frozen DEV-CAL-1 (results/DEVCAL1_world_freeze_
table.json verbatim; same worlds, cells, seeds, ecology axes).  No DEV-CAL-1
file is modified; devcal1_worlds / devcal1_certificates / devcal1_search are
imported unchanged.  Anchors (ORACLE_HISTORY / RESET / SHUFFLED_HISTORY) are
re-run through the UNCHANGED DEV-CAL-1 code path; every anchor must reproduce
the committed DEVCAL1 cell values within the frozen tolerance (bootstrap CI
overlap) or the run is ASSAY_DEFECT.

Knockout arms (adapter records name exactly the granted components):
  ladder PRIMARY      KO-1_REPRESENTATION, KO-2_PLUS_RETRIEVAL,
                      KO-3_PLUS_TRANSPORT, KO-4_PLUS_CHARGING (cumulative)
  leave_one_out SEC.  LOO_MINUS_{REPRESENTATION,RETRIEVAL,TRANSPORT,CHARGING}
The unchanged serve path: retrieval key = SURFACE_SIGNATURE_V1 (the frozen
surface checker) and per-slot blind adaptation, exactly as DEV-CAL-1's
history arm consumed objects.  Grants swap in: certificate storage
(REPRESENTATION), certificate-keyed retrieval (RETRIEVAL_KEYING -- the
UNCHANGED fail-closed structural checker becomes the retrieval key), the
verified homomorphism carrying the retrieved certificate onto the reminted
surface (TRANSPORT_MAP, certificate (c)), and acquisition amortised across
the certificate-sharing world family (CHARGING_MODEL, divisor derived from
the committed world freeze table, never tuned).  A granted component whose
prerequisite is absent degrades to unchanged behaviour, RECORDED in the
receipt (never silent).  Blind discipline is preserved: promotion only ever
fronts candidates; every candidate is still executed + independently
verified; the search never reads declared labels; the purity checker still
guards history bytes both directions.

Endpoints: primary recovery_share (cell B, per arm) =
  (burden_RESET - burden_arm) / (burden_RESET - burden_ORACLE_HISTORY)
on work_to_first_verified_success (compute- and information-matched, all
HDI-14 families charged incl. adapter storage/serve); secondary = the same
share on total_burden_incl_acquisition (amortisation-sensitive).  Material
recovery = share >= 0.25 (frozen) with non-overlapping bootstrap CIs AND
shuffle-equal-n null non-alarm.  Controls A/C/D re-run PER ARM.

HOST RULES (freeze `host_rules`): SCORED runs execute on laptop billy /
billy-old / LUNARC only -- NEVER Mac mini; fresh worktree; receipts
sha-bound.  Sanity selftests (sub-second, toy fixtures) may run anywhere.

Usage:
  python3 -m exact.run_devcal2 --shard k/n [--arms ladder|loo|all|CSV]
  python3 -m exact.run_devcal2 --merge N
Exit codes: 0 completed; 4 terminal ASSAY_DEFECT; 3 CANNOT_CHECK setup.

PROTOCOL_APPENDIX -- 13-family receipt coverage (RECEIPT_COVERAGE_V1.json
rule_for_new_studies) for DEV-CAL-2 receipt rows.  EMITTED (top-level row
keys): "negative/CANNOT_CHECK status" (cannot_check map), "wall/CPU/GPU/IO/
storage" (wall_s), "active k / total N" (k promoted products, n candidate
pool), "ambiguity size/entropy" (ambiguity_size_n = pool remaining at m*),
"protected round-trip errors" (round_trip_errors; transport-verified serve,
cannot_check on arms without TRANSPORT_MAP), "operator/library reuse
identities" (reuse_identities = history-template digests promoted into m*),
"provenance supports/alternatives" (provenance_source = adapter/object that
served the promotion), "abstraction/refinement count" (refinement_count,
honest 0 -- the frozen search never refines representations mid-run).
CANNOT_CHECK-marked (applicable, unmeasurable at row level): none beyond the
round_trip_errors case above.  INAPPLICABLE-BY-DESIGN (omitted from the DC2
receipt schema): "raw terminal" (per-row terminal is undefined before merge;
the terminal is emitted in results/DEVCAL2_RESULTS.json), "B_exec vector"
(no behavioural-execution machinery in DEV-CAL-2), "obligation nodes/
hyperedges/derivations/SCCs" (no obligation-graph machinery), "counterexample
+ version-space shrinkage" (no version-space machinery), "reduction/proof/
rewrite path" (no proof/rewrite machinery).
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
RECEIPTS = os.path.join(HERE, "receipts")
DEVCAL1_RESULTS = os.path.join(RESULTS, "DEVCAL1_RESULTS.json")
WORLD_FREEZE_TABLE = os.path.join(RECEIPTS, "DEVCAL1_world_freeze_table.json")

SEEDS = (0, 1, 2)
BOOT_N = 10000
PERM_N = 10000
EFFECT_THRESHOLD = 0.20          # DEV-CAL-1 control threshold (A fires / D silent)
RECOVERY_THRESHOLD = 0.25        # frozen DC2 material-recovery share
ANCHOR_ARMS = ("ORACLE_HISTORY", "RESET", "SHUFFLED_HISTORY")


def _mean(xs):
    return sum(xs) / len(xs) if xs else None


def _bootstrap_ci(values, stat_fn, n=BOOT_N, seed=20260910):
    """Identical discipline to DEV-CAL-1 (frozen seed, percentile CI)."""
    rng = random.Random(seed)
    stats = []
    vals = list(values)
    if not vals:
        return None
    for _ in range(n):
        sample = [vals[rng.randrange(len(vals))] for _ in range(len(vals))]
        stats.append(stat_fn(sample))
    stats.sort()
    return (stats[int(0.025 * n)], stats[int(0.975 * n)])


# ---------------------------------------------------- world-pair context ------
def world_context(world, cert_rows=None):
    """Per-world-pair context consumed by the serve path: the UNCHANGED
    frozen checkers (surface + structural), the amortisation divisor (data
    derived), and the world id.  cert_rows = the recomputed structural
    checks of the whole frozen matrix (for the divisor); may be None when
    the arm grants no CHARGING_MODEL."""
    import exact.devcal1_certificates as C
    import exact.devcal2_adapters as A
    sur = C.check_surface_relation(world)
    rel = C.check_structural_relation(world)
    wid = "%s-%02d" % (world["cell"], world["world_index"])
    divisor, family_key = (1, None)
    if cert_rows is not None:
        divisor, family_key = A.amortisation_divisor(rel, cert_rows)
    return {"world_id": wid, "surface": sur, "structural": rel,
            "divisor": divisor, "family_key": family_key}


def C_check_structural(world):
    """Thin wrapper so shard/merge share one import point; the checker
    itself is the UNCHANGED devcal1_certificates.check_structural_relation."""
    import exact.devcal1_certificates as C
    return C.check_structural_relation(world)


def committed_sha256():
    import hashlib
    with open(WORLD_FREEZE_TABLE, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# ---------------------------------------------------- knockout serve path -----
def run_ko_arm(adapter, world, seed, acquisition, ctx):
    """One KO arm on one world/seed through the UNCHANGED search machinery.

    Unchanged (imported, never modified): candidate pool + frozen jitter
    ordering + COST table + ALPHA_PROMOTE promotion distribution +
    apply_method + verify_independent + template_object + build_histories +
    both frozen checkers.  Adapter-declared (data, not code): what history
    stores (REPRESENTATION), the retrieval key (RETRIEVAL_KEYING), the serve
    construction (TRANSPORT_MAP), the acquisition charge (CHARGING_MODEL).
    """
    import math
    import exact.devcal1_search as S
    import exact.devcal1_certificates as C
    import exact.devcal2_adapters as A

    effective, degraded = A.effective_components(adapter)
    arm = adapter["arm"]
    target = world["target"]
    rng = random.Random("DC1:stream:%s:%s:%02d:%d" % (
        arm, world["cell"], world["world_index"], seed))
    pool = S.enumerate_methods(world)
    for m in pool:
        m["jitter"] = rng.random()
    pool.sort(key=lambda m: (m["size"], m["jitter"],
                             C.canonical_json(m["shape"]), m["root_slot"]))
    n_pool = len(pool)

    ledger = {"acquisition": 0, "storage_bytes": 0, "retrieval": 0,
              "rejected_candidates": 0, "verification": 0, "adaptation": 0}
    # history CONTENT is the natural source-solved history (unchanged
    # builder); the INTERFACE components are what the adapter grants
    history, _shuffled = S.build_histories(world)
    if "REPRESENTATION" in effective:
        rel = ctx["structural"]
        for obj in history["objects"]:
            obj["structural_certificate"] = {
                "certificate_type": rel["certificate_type"],
                "certificate_digest": rel["certificate_digest"],
                "certificate_format": "DEV_CAL_1(cert_a|cert_b|cert_c)",
                "world_id": ctx["world_id"],
            }
    # adapter record bytes are STORED with the history (cost completeness)
    adapter_bytes = len(C.canonical_json(adapter).encode("utf-8"))
    ledger["storage_bytes"] = len(C.history_bytes(history)) + adapter_bytes
    return _ko_stream(adapter, arm, effective, degraded, world, seed, ctx,
                      history, pool, n_pool, ledger, acquisition, target)


def _ko_stream(adapter, arm, effective, degraded, world, seed, ctx,
               history, pool, n_pool, ledger, acquisition, target):
    import math
    import exact.devcal1_search as S
    import exact.devcal1_certificates as C

    # ---- retrieval: the adapter's keying rule over the UNCHANGED checkers
    if "RETRIEVAL_KEYING" in effective:
        key_match = ctx["structural"]["latent_same"] is True
        keying_rule = "STRUCTURAL_CERTIFICATE_V1"
    else:
        key_match = ctx["surface"]["surface_same"] is True
        keying_rule = "SURFACE_SIGNATURE_V1"
    adapted = []
    round_trip_errors = 0
    transport_used = False
    for obj in history["objects"]:
        ledger["retrieval"] += S.COST["retrieve_per_object"] \
            + S.COST["retrieve_per_probe"]
        if not key_match:
            continue
        shape = tuple((op, tuple(ch)) for op, ch in obj["ops_dag"])
        if "TRANSPORT_MAP" in effective:
            # the verified homomorphism (certificate (c)) carries the
            # retrieved certificate onto the reminted surface: ONE served
            # construction; degrade to per-slot binding if (c) is not held
            held_c, _ = C.cert_c(list(map(list, shape)),
                                 world["target"]["shape"])
            if held_c:
                ledger["adaptation"] += S.COST["adapt_per_binding"]
                transport_used = True
                for slot in range(len(target["inputs"])):
                    adapted.append({"size": len(shape), "shape": shape,
                                    "root_slot": slot, "promoted": True})
            else:
                round_trip_errors += 1
                for slot in range(len(target["inputs"])):
                    ledger["adaptation"] += S.COST["adapt_per_binding"]
                    adapted.append({"size": len(shape), "shape": shape,
                                    "root_slot": slot, "promoted": True})
        else:
            for slot in range(len(target["inputs"])):
                ledger["adaptation"] += S.COST["adapt_per_binding"]
                adapted.append({"size": len(shape), "shape": shape,
                                "root_slot": slot, "promoted": True})

    adapted_digests = {C.canonical_json([list(map(list, m["shape"])),
                                         m["root_slot"]]) for m in adapted}
    blind = [m for m in pool if C.canonical_json(
        [list(map(list, m["shape"])), m["root_slot"]]) not in adapted_digests]
    stream = list(adapted) + blind
    n_adapted = len(adapted)

    def p_first(m):
        p = (1.0 - S.ALPHA_PROMOTE) / n_pool
        if n_adapted and C.canonical_json(
                [list(map(list, m["shape"])), m["root_slot"]]) \
                in adapted_digests:
            p += S.ALPHA_PROMOTE / n_adapted
        return p

    # ---- the search loop: IDENTICAL discipline to devcal1_search.run_search
    events = []
    nodes_expanded = 0
    work = ledger["retrieval"] + ledger["adaptation"]
    failed = 0
    rej_hist = {}
    verif_calls = 0
    entropy_sum = 0.0
    entropy_n = 0
    branch_sum = 0
    branch_n = 0
    m_star = None
    m_star_rank = None
    m_star_surprisal = None
    remaining = len(stream)
    for rank, cand in enumerate(stream, start=1):
        if m_star is not None:
            break
        p_draw = 1.0 / remaining
        events.append({"i": rank,
                       "cand_digest": C.sha(C.canonical_json(
                           [list(map(list, cand["shape"])),
                            cand["root_slot"]])),
                       "p_draw": p_draw,
                       "promoted": bool(cand.get("promoted"))})
        entropy_sum += -math.log2(p_draw)
        entropy_n += 1
        branch_sum += len(cand["shape"])
        branch_n += 1
        remaining -= 1
        nodes_expanded += 1
        work += S.COST["expand_base"] + S.COST["expand_per_node"] * cand["size"]
        val, reason = S.apply_method(cand, target)
        if val is None:
            failed += 1
            rej_hist[reason] = rej_hist.get(reason, 0) + 1
            ledger["rejected_candidates"] += 1
            continue
        verif_calls += 1
        work += S.COST["verify_base"] + S.COST["verify_per_node"] * cand["size"]
        ledger["verification"] += 1
        if S.verify_independent(cand, target):
            m_star = cand
            m_star_rank = rank
            m_star_surprisal = -math.log2(p_first(cand))
            events[-1]["success"] = True
        else:
            failed += 1
            rej_hist["VERIFY_FAIL"] = rej_hist.get("VERIFY_FAIL", 0) + 1
            ledger["rejected_candidates"] += 1
    if m_star is None:
        return {"status": "NO_VERIFIED_SUCCESS", "arm": arm,
                "world_id": ctx["world_id"], "cell": world["cell"],
                "seed": seed, "work": work, "nodes_expanded": nodes_expanded,
                "ledger": ledger}
    return _ko_receipt(adapter, arm, effective, degraded, world, seed, ctx,
                       history, m_star, m_star_rank, m_star_surprisal,
                       events, nodes_expanded, failed, rej_hist, verif_calls,
                       entropy_sum, entropy_n, branch_sum, branch_n, work,
                       ledger, acquisition, n_pool, n_adapted,
                       round_trip_errors, transport_used, keying_rule,
                       key_match)


def _ko_receipt(adapter, arm, effective, degraded, world, seed, ctx,
                history, m_star, m_star_rank, m_star_surprisal, events,
                nodes_expanded, failed, rej_hist, verif_calls, entropy_sum,
                entropy_n, branch_sum, branch_n, work, ledger, acquisition,
                n_pool, n_adapted, round_trip_errors, transport_used,
                keying_rule, key_match):
    import exact.devcal1_certificates as C

    # charging model (adapter-declared): amortise acquisition across the
    # certificate-sharing world family; identical serve path, only the
    # acquisition accounting changes (freeze: KO-4 == KO-3 serve path)
    if "CHARGING_MODEL" in effective:
        ledger["acquisition"] = acquisition / ctx["divisor"]
        charge_rule = "CERT_FAMILY_AMORTISATION_V1(divisor=%d)" % ctx["divisor"]
    else:
        ledger["acquisition"] = acquisition
        charge_rule = "NO_AMORTISATION_V1"
    # purity (unchanged checker, both directions, checker-computed m*)
    target = world["target"]
    solution_obj = {"method": [list(map(list, m_star["shape"])),
                               m_star["root_slot"]],
                    "value": target["goal"]}
    pure, detail = C.purity_check(history, world, solution_obj)
    m_star_in_history = (False if pure is True else
                         True if pure is False else None)
    if pure is not True:
        # KO histories carry the natural source history; a hit is leakage
        # and reclassifies the row, exactly as DEV-CAL-1
        classification = "SOLUTION_EPISODIC"
    else:
        classification = "SEARCH_DEVELOPMENT_CANDIDATE"
    receipt = {
        "study": "DEV-CAL-2",
        "status": "OK",
        "arm": arm,
        "world_id": ctx["world_id"],
        "cell": world["cell"],
        "seed": seed,
        "m_star_digest": C.sha(C.canonical_json(
            [list(map(list, m_star["shape"])), m_star["root_slot"]])),
        "m_star_identity_class": "typed_operator_dag_binding",
        "m_star_derived_from_history_template": bool(m_star.get("promoted")),
        "m_star_in_history": m_star_in_history,
        "purity": {"pure": pure, **detail},
        "classification": classification,
        "adapter": {
            "adapter_id": adapter["adapter_id"],
            "adapter_sha256": adapter["adapter_sha256"],
            "components_granted": list(adapter["components_granted"]),
            "components_effective": sorted(effective),
            "component_degradations": degraded,
            "keying_rule_applied": keying_rule,
            "retrieval_key_match": bool(key_match),
            "transport_map_used": bool(transport_used),
            "charge_rule_applied": charge_rule,
            "certificate_digest": (ctx["structural"]["certificate_digest"]
                                   if "REPRESENTATION" in effective else None),
        },
        "recorded_before_solution_discovery": {
            "RECONSTRUCTED": False,
            "event_log_digest": C.sha(C.canonical_json(events)),
            "n_events_logged": len(events),
            "eventual_success_rank": m_star_rank,
            "proposal_surprisal_bits": round(m_star_surprisal, 6),
            "proposal_entropy_bits": round(entropy_sum / entropy_n, 6)
            if entropy_n else None,
            "branch_factor": round(branch_sum / branch_n, 6) if branch_n
            else None,
            "nodes_expanded": nodes_expanded,
            "failed_candidates": failed,
            "rejection_reason_histogram": rej_hist,
            "decomposition_structure_digest": C.sha(C.canonical_json(
                [list(map(list, m_star["shape"])), m_star["root_slot"]])),
            "information_queries": {"count": 0, "cost": 0,
                                    "note": "no external hints; identical "
                                            "evidence stream across arms"},
            "retrieval_attempts": len(history["objects"]),
            "successful_mappings": 1 if m_star.get("promoted") else 0,
            "representation_refinements": {"count": 0, "digests": []},
            "verification_calls": verif_calls,
            "target_evidence_consumed": {
                "bytes": len(C.canonical_json(target)), "queries": 1},
            "work_to_first_verified_success": work,
        },
        "cost_ledger": ledger,
        "ecology_axes": {
            "rho": float(world["ecology_axes"]["rho"]),
            "sigma": float(world["ecology_axes"]["sigma"]),
            "d": world["ecology_axes"]["d"],
            "delta": world["ecology_axes"]["delta"],
        },
        "total_burden_incl_acquisition": work + ledger["acquisition"],
        # ---- 13-family receipt projections (see PROTOCOL_APPENDIX) ----
        "k": n_adapted,
        "n": n_pool,
        "wall_s": None,        # filled by shard writer (wall measurable)
        "ambiguity_size_n": n_pool - m_star_rank + 1,
        "round_trip_errors": round_trip_errors if "TRANSPORT_MAP" in \
            effective else None,
        "reuse_identities": ([C.sha(C.canonical_json(
            [list(map(list, m_star["shape"])), m_star["root_slot"]]))]
            if m_star.get("promoted") else []),
        "provenance_source": adapter["adapter_sha256"] if
        m_star.get("promoted") else None,
        "refinement_count": 0,
        "cannot_check": {},
    }
    if "TRANSPORT_MAP" not in effective:
        receipt["cannot_check"]["round_trip_errors"] = (
            "TRANSPORT_MAP not granted; transport round-trip not measurable")
    return receipt


# ------------------------------------------------------------ shard runner ---
def arm_selection(spec):
    import exact.devcal2_adapters as A
    if spec in (None, "all"):
        return list(A.ALL_KO_ARMS)
    if spec == "ladder":
        return list(A.LADDER)
    if spec == "loo":
        return list(A.LEAVE_ONE_OUT)
    arms = [a.strip() for a in spec.split(",") if a.strip()]
    bad = [a for a in arms if a not in A.ALL_KO_ARMS]
    if bad:
        raise SystemExit("unknown KO arms: %s" % bad)
    return arms


def shard_main(k, n, arm_spec):
    import exact.devcal1_worlds as W
    import exact.devcal1_search as S
    import exact.devcal2_adapters as A
    os.makedirs(RESULTS, exist_ok=True)
    os.makedirs(RECEIPTS, exist_ok=True)
    arms = arm_selection(arm_spec)
    adapters = [A.make_adapter(a) for a in arms]
    ok, errs = A.verify_adapter_suite(adapters, arms)
    if not ok:
        raise SystemExit("adapter suite failed closed: %s" % errs)
    t0 = time.time()
    worlds = W.all_worlds()
    # world-matrix anchor: recomputed certificate digests must match the
    # committed freeze table (same matrix, else ASSAY_DEFECT at merge)
    with open(WORLD_FREEZE_TABLE, encoding="utf-8") as f:
        committed_table = {r["world"]: r["certificate_digest"]
                           for r in json.load(f)["table"]}
    cert_rows = []
    table_defects = []
    for w in worlds:
        rel = C_check_structural(w)
        wid = "%s-%02d" % (w["cell"], w["world_index"])
        if committed_table.get(wid) != rel["certificate_digest"]:
            table_defects.append(wid)
        cert_rows.append(rel)
    if table_defects:
        raise SystemExit("world matrix drift vs committed freeze table: %s"
                         % table_defects[:5])
    receipts = []
    partial = {"shard": "%d/%d" % (k, n), "worlds": {}}
    acquisition = {}
    for w in worlds:
        wid = "%s-%02d" % (w["cell"], w["world_index"])
        src = S.source_acquisition_cost(w, 0)
        if src.get("status") != "OK":
            raise SystemExit("DC2 source search failed for %s: %s"
                             % (wid, src.get("status")))
        acquisition[wid] = src["work"]
    for wi, w in enumerate(worlds):
        if (wi % n) + 1 != k:
            continue
        wid = "%s-%02d" % (w["cell"], w["world_index"])
        ctx = world_context(w, cert_rows)
        for arm in ANCHOR_ARMS:  # anchors: UNCHANGED DEV-CAL-1 code path
            for seed in SEEDS:
                import exact.run_devcal1 as R1
                rec = R1.run_world(arm, w, seed, acquisition[wid])
                rec.pop("_m_star_shape", None)
                rec.pop("_m_star_slot", None)
                rec["study"] = "DEV-CAL-2"
                rec["run_role"] = "ANCHOR_RERUN"
                receipts.append(rec)
        for adapter in adapters:
            for seed in SEEDS:
                tw = time.time()
                rec = run_ko_arm(adapter, w, seed, acquisition[wid], ctx)
                if rec.get("status") == "OK":
                    rec["wall_s"] = round(time.time() - tw, 4)
                receipts.append(rec)
        partial["worlds"][wid] = {"acquisition": acquisition[wid],
                                  "n_receipts": len(receipts)}
    with open(os.path.join(RECEIPTS,
                           "DEVCAL2_receipts_shard%d.jsonl" % k), "w",
              encoding="utf-8") as f:
        for row in receipts:
            f.write(json.dumps(row, sort_keys=True, default=repr) + "\n")
    with open(os.path.join(RECEIPTS, "DEVCAL2_adapters.json"), "w",
              encoding="utf-8") as f:
        json.dump({"schema": "OCM_DC2_ADAPTER_SUITE",
                   "adapters": adapters,
                   "world_freeze_table_sha256": committed_sha256()}, f,
                  indent=1, sort_keys=True, default=repr)
        f.write("\n")
    with open(os.path.join(RESULTS,
                           "DEVCAL2_partial_shard%d.json" % k), "w",
              encoding="utf-8") as f:
        json.dump(partial, f, indent=1, sort_keys=True, default=repr)
        f.write("\n")
    print("DC2 shard %d/%d done: %d receipts, arms=%s, %.1fs" %
          (k, n, len(receipts), arms, time.time() - t0))
    return 0


# ------------------------------------------------------- anchor reproduction --
# checker_requirements[2]: ORACLE_HISTORY/RESET/SHUFFLED_HISTORY re-runs must
# match the committed DEVCAL1 cell values within the frozen tolerance
# (bootstrap CI overlap) or the run is ASSAY_DEFECT.  The tolerance is CI
# OVERLAP, justified by the committed DEVCAL1 CIs themselves: the cell-B
# anchor CI [0.9654, 0.9739] has half-width 0.0043 (A: 0.0044, C: 0.181,
# D: 0.155); a re-run of the same frozen machinery reproduces those CIs to
# within their own width, so requiring strictly positive overlap accepts a
# faithful re-run and rejects any drift larger than the CI gap.  Touching
# intervals (overlap exactly 0) FAIL CLOSED.
ANCHOR_CI_OVERLAP_MIN = 0.0


def ci_overlap(ci_a, ci_b):
    if not ci_a or not ci_b:
        return None
    return min(ci_a[1], ci_b[1]) - max(ci_a[0], ci_b[0])


def anchor_reproduction(committed, rerun, label):
    """Compare re-run reduction stats against the committed DEVCAL1 anchors.
    Returns list of defect strings (empty = anchors reproduce)."""
    defects = []
    for cell in ("A", "B", "C", "D"):
        for key, name in (("oracle_vs_reset_reduction", "ORACLE"),
                          ("shuffled_vs_reset_reduction", "SHUFFLED")):
            com = committed["per_cell"][cell][key]
            rer = rerun.get(cell, {}).get(key)
            if rer is None or rer.get("ci") is None:
                defects.append("%s %s anchor: re-run value missing (%s)"
                               % (cell, name, label))
                continue
            ov = ci_overlap(com["ci"], rer["ci"])
            if ov is None or ov <= ANCHOR_CI_OVERLAP_MIN:
                defects.append(
                    "%s %s anchor drift: committed mean %.4f ci %s vs re-run "
                    "mean %.4f ci %s (overlap %s <= %s)" %
                    (cell, name, com["mean"], com["ci"], rer["mean"],
                     rer["ci"], ov, ANCHOR_CI_OVERLAP_MIN))
    return defects


def cell_arm_stats(rows, cell, arm, burden_key):
    """world-seed -> burden for one arm/cell on the chosen readout."""
    out = {}
    for r in rows:
        if r.get("arm") != arm or r.get("cell") != cell:
            continue
        if r.get("status") != "OK":
            continue
        if burden_key == "work":
            v = r["recorded_before_solution_discovery"][
                "work_to_first_verified_success"]
        else:
            v = r["total_burden_incl_acquisition"]
        out[("%s" % r["world_id"], r["seed"])] = v
    return out


def reduction_stats(rows, cell, arm, burden_key="work"):
    """arm-vs-RESET mean reduction + CI + nonoverlap, DEV-CAL-1 discipline."""
    armv = cell_arm_stats(rows, cell, arm, burden_key)
    reset = cell_arm_stats(rows, cell, "RESET", burden_key)
    keys = sorted(set(armv) & set(reset))
    red = [(reset[k2] - armv[k2]) / reset[k2]
           for k2 in keys if reset[k2] > 0]
    out = {"mean": _mean(red), "ci": _bootstrap_ci(red, _mean),
           "n_pairs": len(red)}
    out["threshold_met"] = bool(
        red and _mean(red) >= EFFECT_THRESHOLD and
        _bootstrap_ci(red, _mean)[0] > 0)
    out["burden_cis_nonoverlapping"] = bool(
        armv and reset and
        _bootstrap_ci(list(armv.values()), _mean)[1] <
        _bootstrap_ci(list(reset.values()), _mean)[0])
    return out


def recovery_share_stats(rows, cell, arm, burden_key="work"):
    """PRIMARY endpoint: share of the oracle's cell-B reduction recovered.
    (burden_RESET - burden_arm) / (burden_RESET - burden_ORACLE_HISTORY),
    paired per world-seed."""
    armv = cell_arm_stats(rows, cell, arm, burden_key)
    orac = cell_arm_stats(rows, cell, "ORACLE_HISTORY", burden_key)
    reset = cell_arm_stats(rows, cell, "RESET", burden_key)
    keys = sorted(set(armv) & set(orac) & set(reset))
    shares = []
    for k2 in keys:
        denom = reset[k2] - orac[k2]
        if reset[k2] > 0 and denom != 0:
            shares.append((reset[k2] - armv[k2]) / denom)
    ci = _bootstrap_ci(shares, _mean)
    out = {"mean": _mean(shares), "ci": ci, "n_pairs": len(shares)}
    # non-overlap vs the share-0 null (RESET itself): material recovery
    # needs the CI strictly above 0 AND mean >= RECOVERY_THRESHOLD
    out["ci_excludes_zero"] = bool(ci and ci[0] > 0)
    out["threshold_met"] = bool(
        shares and out["mean"] is not None and
        out["mean"] >= RECOVERY_THRESHOLD and out["ci_excludes_zero"])
    return out


def shuffle_null(rows, cell, arm="SHUFFLED_HISTORY", burden_key="work"):
    """shuffle-equal-n null, DEV-CAL-1 construction VERBATIM: the signflip
    permutation runs on the SHUFFLED_HISTORY control (same object kind and
    count, class randomly reassigned) vs RESET -- never on the recovering arm
    itself, whose true effect would trivially 'alarm' a signflip null (this
    is exactly why DC1 ran its null at p=0.79 on the shuffled arm)."""
    armv = cell_arm_stats(rows, cell, arm, burden_key)
    reset = cell_arm_stats(rows, cell, "RESET", burden_key)
    keys = sorted(set(armv) & set(reset))
    diffs = [armv[k2] - reset[k2] for k2 in keys]
    obs = abs(_mean(diffs) or 0.0)
    rng = random.Random(20260910)
    ge = 0
    for _ in range(PERM_N):
        d = [x * (1 if rng.random() < 0.5 else -1) for x in diffs]
        if abs(_mean(d)) >= obs - 1e-12:
            ge += 1
    return {"null_arm": arm, "observed_mean_excess": _mean(diffs),
            "p_signflip": ge / PERM_N,
            "non_alarm": ge / PERM_N >= 0.05}


def null_arm_share(rows, cell, burden_key="work"):
    """Recovery share of the SHUFFLED_HISTORY anchor itself: the null arm must
    NOT show material recovery (a recovering shuffle = class-blind leak)."""
    s = recovery_share_stats(rows, cell, "SHUFFLED_HISTORY", burden_key)
    material = bool(s["mean"] is not None and
                    s["mean"] >= RECOVERY_THRESHOLD and
                    s["ci_excludes_zero"])
    return {"mean": s["mean"], "ci": s["ci"], "n_pairs": s["n_pairs"],
            "material_recovery": material,
            "non_alarm": not material}


def draw_invariance(rows, cell, arm, burden_key="work"):
    """Per-seed direction agreement of the arm-vs-RESET reduction."""
    armv = cell_arm_stats(rows, cell, arm, burden_key)
    reset = cell_arm_stats(rows, cell, "RESET", burden_key)
    per_seed = {}
    for seed in SEEDS:
        reds = [(reset[k2] - armv[k2]) / reset[k2]
                for k2 in sorted(set(armv) & set(reset))
                if k2[1] == seed and reset[k2] > 0]
        per_seed[str(seed)] = {"mean_reduction": _mean(reds)}
    dirs = [v["mean_reduction"] for v in per_seed.values()
            if v["mean_reduction"] is not None]
    return {"per_seed": per_seed,
            "direction_agrees": bool(dirs) and
            all((d > 0) == (dirs[0] > 0) for d in dirs)}


def arm_control_defects(rows, arm):
    """controls_per_arm: A must fire, C and D must stay silent
    (DEV-CAL-1 assay-validity rule applied PER ARM)."""
    defects = []
    a = reduction_stats(rows, "A", arm)
    if not (a["threshold_met"] and a["burden_cis_nonoverlapping"]):
        defects.append("arm %s cell-A positive control did not fire "
                       "(mean=%.4f)" % (arm, a["mean"] or float("nan")))
    for cell in ("C", "D"):
        s = reduction_stats(rows, cell, arm)
        if s["threshold_met"] and s["burden_cis_nonoverlapping"]:
            defects.append("arm %s cell-%s control ALARMED (leak): mean=%.4f"
                           % (arm, cell, s["mean"]))
    return defects


def ledger_defects(rows):
    """cost completeness incl. adapter storage/serve: every family on every
    arm row; adapter digest bound in every KO row."""
    fams = ("acquisition", "storage_bytes", "retrieval", "rejected_candidates",
            "verification", "adaptation")
    defects = []
    for r in rows:
        if r.get("status") != "OK":
            continue
        if r.get("run_role") == "ANCHOR_RERUN":
            continue
        cl = r.get("cost_ledger") or {}
        for fam in fams:
            if fam not in cl or cl[fam] is None:
                defects.append("cost family %s missing on %s/%s/%s" %
                               (fam, r.get("arm"), r.get("world_id"),
                                r.get("seed")))
        if not r.get("adapter", {}).get("adapter_sha256"):
            defects.append("adapter digest not bound on %s/%s" %
                           (r.get("arm"), r.get("world_id")))
    return defects


def purity_summary(rows, arm):
    pur = [r.get("m_star_in_history") for r in rows
           if r.get("arm") == arm and r.get("status") == "OK"]
    return {"n": len(pur),
            "n_pure": sum(1 for p in pur if p is False),
            "n_impure": sum(1 for p in pur if p is True),
            "n_cannot_check": sum(1 for p in pur
                                  if p is not False and p is not True)}


def merge_main(nshards):
    import exact.devcal2_adapters as A
    import exact.devcal1_certificates as C
    t0 = time.time()
    rows = []
    for k in range(1, nshards + 1):
        p = os.path.join(RECEIPTS, "DEVCAL2_receipts_shard%d.jsonl" % k)
        with open(p, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rows.append(json.loads(line))
    with open(DEVCAL1_RESULTS, encoding="utf-8") as f:
        committed = json.load(f)
    with open(os.path.join(RECEIPTS, "DEVCAL2_adapters.json"),
              encoding="utf-8") as f:
        adapters = json.load(f)["adapters"]
    arms = sorted({r["arm"] for r in rows
                   if r.get("run_role") != "ANCHOR_RERUN"})
    ok, aerrs = A.verify_adapter_suite(adapters, arms)
    defects = [] if ok else ["adapter suite: %s" % e for e in aerrs]
    suite_digest = {rec["arm"]: rec["adapter_sha256"] for rec in adapters
                    if isinstance(rec, dict) and "arm" in rec}
    for r in rows:  # checker_requirements[1]: row digest == suite digest
        ad = r.get("adapter") or {}
        if ad and suite_digest.get(r.get("arm")) != ad.get("adapter_sha256"):
            defects.append("adapter digest mismatch on %s/%s (row %s vs "
                           "suite %s)" % (r.get("arm"), r.get("world_id"),
                                          ad.get("adapter_sha256"),
                                          suite_digest.get(r.get("arm"))))

    # ---- anchors re-run through the unchanged DEV-CAL-1 path --------------
    rerun = {cell: {"oracle_vs_reset_reduction":
                    reduction_stats(rows, cell, "ORACLE_HISTORY"),
                    "shuffled_vs_reset_reduction":
                    reduction_stats(rows, cell, "SHUFFLED_HISTORY")}
             for cell in ("A", "B", "C", "D")}
    defects.extend(anchor_reproduction(committed, rerun, "DC2 rerun"))
    controls = C.hostile_and_clean_controls()
    for name, ctl in controls.items():
        key = "fired" if "fired" in ctl else "silent"
        if not ctl[key]:
            defects.append("checker control %s failed to %s" % (name, key))

    # ---- per-arm readouts --------------------------------------------------
    # material recovery (frozen effect_threshold) = share >= 0.25 AND
    # non-overlapping CIs AND shuffle-equal-n null non-alarm; the null gates
    # threshold_met, it is NOT an ASSAY_DEFECT (frozen terminals list).
    per_arm = {}
    null_w = shuffle_null(rows, "B")                      # DC1 construction
    null_t = shuffle_null(rows, "B", burden_key="total")
    nshare_w = null_arm_share(rows, "B")
    nshare_t = null_arm_share(rows, "B", "total")
    null_ok_w = null_w["non_alarm"] and nshare_w["non_alarm"]
    null_ok_t = null_t["non_alarm"] and nshare_t["non_alarm"]
    for arm in arms:
        prim = recovery_share_stats(rows, "B", arm)
        sec = recovery_share_stats(rows, "B", arm, "total")
        prim["shuffle_null_non_alarm"] = null_ok_w
        sec["shuffle_null_non_alarm"] = null_ok_t
        prim["threshold_met"] = bool(prim["threshold_met"] and null_ok_w)
        sec["threshold_met"] = bool(sec["threshold_met"] and null_ok_t)
        per_arm[arm] = {
            "recovery_share_cell_B": prim,
            "recovery_share_cell_B_total_burden": sec,
            "controls": {cell: reduction_stats(rows, cell, arm)
                         for cell in ("A", "C", "D")},
            "shuffle_null_cell_B": {**null_w, "null_arm_share": nshare_w},
            "shuffle_null_cell_B_total_burden": {**null_t,
                                                 "null_arm_share": nshare_t},
            "draw_invariance_cell_B": draw_invariance(rows, "B", arm),
            "purity": purity_summary(rows, arm),
            "adapter_sha256": next((r["adapter"]["adapter_sha256"]
                                    for r in rows if r.get("arm") == arm
                                    and r.get("adapter")), None),
        }
        defects.extend(arm_control_defects(rows, arm))
        if not per_arm[arm]["draw_invariance_cell_B"]["direction_agrees"]:
            defects.append("arm %s draw-invariance failure on primary "
                           "endpoint" % arm)
    defects.extend(ledger_defects(rows))

    # ---- terminal decision (frozen rules) ----------------------------------
    ladder_state = {}
    for arm in A.LADDER:
        if arm not in per_arm:
            continue
        ladder_state[arm] = {
            "primary": per_arm[arm]["recovery_share_cell_B"]["threshold_met"],
            "secondary": per_arm[arm]["recovery_share_cell_B_total_burden"]
            ["threshold_met"]}
    minimal_tier = None
    for arm in A.LADDER:
        st = ladder_state.get(arm)
        if st and st["primary"]:
            minimal_tier = arm
            break
    if defects:
        terminal = "ASSAY_DEFECT"
    elif minimal_tier is None:
        terminal = "INTERFACE_GRANTS_INSUFFICIENT"
    elif not any(st["secondary"] for st in ladder_state.values()):
        terminal = "AMORTISATION_DOMINATED"
    else:
        terminal = "CARRIER_IDENTIFIED_TIER_%d" % (
            A.LADDER.index(minimal_tier) + 1)
    results = {
        "study": "DEV-CAL-2",
        "protocol": "DEV_CAL_2_KNOCKOUT_PROTOCOL_FREEZE_V1",
        "parent_protocol": "DEV_CAL_1_PROTOCOL_FREEZE_V1",
        "receipt_schema": "SEARCH_GEOMETRY_RECEIPT_SCHEMA_V1 + 13-family "
                          "projections (see run_devcal2 PROTOCOL_APPENDIX)",
        "owner_issue": 323,
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "host": os.uname().nodename,
        "wall_s": round(time.time() - t0, 3),
        "n_receipts": len(rows),
        "arms_run": arms,
        "adapters": adapters,
        "anchor_rerun": rerun,
        "anchor_reproduction_defects": anchor_reproduction(
            committed, rerun, "DC2 rerun"),
        "checker_controls": controls,
        "per_arm": per_arm,
        "ladder_state": ladder_state,
        "leave_one_out_secondary": {
            a: {"primary": per_arm[a]["recovery_share_cell_B"],
                "secondary": per_arm[a]
                ["recovery_share_cell_B_total_burden"]}
            for a in A.LEAVE_ONE_OUT if a in per_arm},
        "effect_threshold": EFFECT_THRESHOLD,
        "recovery_threshold": RECOVERY_THRESHOLD,
        "solution_episodic_classification": {
            a: per_arm[a]["purity"] for a in arms},
        "terminal": terminal,
        "terminal_defects": defects,
    }
    with open(os.path.join(RESULTS, "DEVCAL2_RESULTS.json"), "w",
              encoding="utf-8") as f:
        json.dump(results, f, indent=1, sort_keys=True, default=repr)
        f.write("\n")
    print("DEV-CAL-2 terminal:", terminal)
    for arm in arms:
        s = per_arm[arm]["recovery_share_cell_B"]
        print("  %s: cell-B recovery_share mean=%.4f ci=%s met=%s" %
              (arm, s["mean"] or float("nan"), s["ci"], s["threshold_met"]))
    for dd in defects[:20]:
        print("  defect:", dd)
    return 0 if terminal != "ASSAY_DEFECT" else 4


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", default=None, help="k/n where k in 1..n")
    ap.add_argument("--merge", type=int, default=None)
    ap.add_argument("--arms", default="all",
                    help="ladder | loo | all | comma-separated KO arm ids")
    args = ap.parse_args()
    if args.shard:
        k, n = (int(x) for x in args.shard.split("/"))
        return shard_main(k, n, args.arms)
    if args.merge:
        return merge_main(args.merge)
    print("use --shard k/n [--arms ...] or --merge N", file=sys.stderr)
    return 3


if __name__ == "__main__":
    sys.exit(main())

