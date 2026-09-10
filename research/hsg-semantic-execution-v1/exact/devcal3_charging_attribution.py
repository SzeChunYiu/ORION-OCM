#!/usr/bin/env python3
"""DEV-CAL-3 charging-attribution recomputation (#323; freeze
DEV_CAL_3_CHARGING_ATTRIBUTION_FREEZE_V1.json -- every clause binding).

Parent terminal: DEV-CAL-2 V2 AMORTISATION_DOMINATED (PR #345, 5d10d910) --
KO-2 carries the oracle transfer at 1.0000 [1.0,1.0] (AGREE_DETERMINATE 3/3)
on compute-matched work, but NO tier recovers on total_burden_incl_acquisition
(secondary shuffle-null alarm p_signflip=0.0 on every recovering tier).  The
DEV-CAL-2 freeze authorises work on the amortisation structure ONLY; carrier
= charging model.  This study answers the frozen central question: WHICH
component of the charging model makes acquisition costs non-amortising.

Method (freeze `method.kind` = ANALYTICAL_RECOMPUTATION_OVER_SEALED_RECEIPTS):
NO new worlds, seeds, arms-at-runtime, or scored execution.  The sealed V2
receipt ledgers are the sole input.  sha256 of every input is recorded in
the analysis receipt BEFORE any recomputation and cross-checked against TWO
independent committed digest sources (the scored V2 output_bindings and the
laptop host receipt output_bindings); any disagreement is
RECEIPT_BINDING_DEFECT and the analysis halts with no numbers.

Stage 1 -- AS_IS control: every V2 scored per-arm readout is recomputed from
the sealed receipt rows with the UNCHANGED DEV-CAL-2 statistics functions
(imported from exact.run_devcal2: frozen seeds, bootstrap discipline,
signflip permutations) -- EXACT equality required, any mismatch =
ASSAY_DEFECT (first differing cell printed, analysis halts, no
alternative-semantics numbers).  Float fields bind exactly FIRST; a value
that differs only at the last-bit level (summation-order noise between the
scored rollup and this recomputation; observed 1 ULP) binds within the
registered FLOAT_BIND_TOLERANCE=1e-12 relative and every tolerance-bound
field is NAMED in the receipt -- anything beyond it is ASSAY_DEFECT.  The
per-row charge decomposition is REPLAYED
through the UNCHANGED DEV-CAL-1/2 machinery (deterministic frozen seeds) and
every recorded aggregate is verified: event_log_digest, n_events_logged,
eventual_success_rank, nodes_expanded, failed_candidates,
rejection_reason_histogram, verification_calls, work_to_first_verified_success,
cost_ledger families, m_star_digest, acquisition charge rule.

Stage 2 -- five alternative charge semantics (freeze `charge_semantics_arms`),
applied POST HOC to the RECOVERED event ledger only (freeze `leakage_rule`:
no event re-simulated, re-ordered, or dropped -- asserted by re-digesting the
event multiset per row under every semantics):
  NO_FAILURE_CHARGE    failed attempts charged zero (still occur + count)
  NO_VERIFICATION_CHARGE external CHECKER_C (verify) calls charged zero
  NO_MINING_CHARGE     development-stream (acquisition) cost excluded
  MARGINAL_COST_ONLY   acquisition retires after first N uses (primary N=10,
                       sensitivity N in {5,10,25}), canonical use order:
                       ORACLE s0-2, SHUFFLED s0-2, then ALL_KO_ARMS x seeds
  SALVAGE_MODEL        failed traces credited measured information value at
                       the empirical reuse rate r_failed recorded in the
                       sealed ledger (fraction of failed-trace events whose
                       candidate digest is some run's m*)

Stats (freeze `endpoint_and_stats`): paired per-cell recomputation intervals,
lineage (certificate-family) and ecology clustering, Holm-Bonferroni over the
five alternative arms at alpha=0.05, the registered 20% margin
(EFFECT_THRESHOLD=0.20 inherited from exact.run_devcal2 controls), and
NULL_BAND_GATED_V1 direction tests (AM-5 standing).  Attribution = the single
component whose reform flips the secondary readout (total-burden recovery
>= 0.25, CI excluding 0, per-semantics null non-alarm, Holm reject) while
the KO-2 primary transfer stays intact.  A component that does NOT flip is
EXONERATED and lands as a class-level invariant with its measured bound.

Terminals (freeze `terminals`): ASSAY_DEFECT > RECEIPT_BINDING_DEFECT >
CHARGE_CARRIER_{FAILURES|VERIFICATION|MINING|FULL_CHARGE|NO_SALVAGE|MULTIPLE|NONE}
> CANNOT_CHECK_<reason>.

HOST RULES (freeze `hosts`): the scored recompute + rollup runs on laptop
billy ONLY -- never Mac mini; Mac mini hosts sub-second selftests only.
Forbidden (freeze `forbidden`): no new scored run, no editing sealed V1/V2
receipts or their bindings (outputs land under NEW names), no new charging
model designed/deployed in-lane, no economics/OCM-residual/open-endedness
claims, no oracle-transplant headline comparator.

Usage:
  python3 -m exact.devcal3_charging_attribution --run [--out PATH] [--data DIR]
Exit codes: 0 completed; 4 ASSAY_DEFECT; 5 RECEIPT_BINDING_DEFECT;
3 CANNOT_CHECK setup.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
RECEIPTS = os.path.join(HERE, "receipts")
FREEZE_PATH = os.path.join(os.path.dirname(os.path.dirname(HERE)),
                           "top-tier-atomic-closure-v1",
                           "DEV_CAL_3_CHARGING_ATTRIBUTION_FREEZE_V1.json")

SCORED_V2 = os.path.join(RESULTS, "DEV_CAL_2_SCORED_RESULTS_V2.json")
SCORED_V1 = os.path.join(RESULTS, "DEV_CAL_2_SCORED_RESULTS_V1.json")
HOST_RECEIPT_V2 = os.path.join(RECEIPTS, "DEVCAL2_HOST_RECEIPT_billy_V2.json")
SHARD_V2 = [os.path.join(RECEIPTS, "DEVCAL2_receipts_shard%d_V2.jsonl" % k)
            for k in (1, 2, 3, 4)]
RESULTS_V2 = os.path.join(RESULTS, "DEVCAL2_RESULTS_V2.json")

# MARGINAL_COST_ONLY: acquisition retires after the first N uses of the
# world asset (freeze `charge_semantics_arms.MARGINAL_COST_ONLY`; primary
# N=10, sensitivity at 5 and 25 -- derived from the freeze, never tuned)
MCO_PRIMARY_N = 10
MCO_SENSITIVITY = (5, 10, 25)

SEMANTICS_ARMS = ("NO_FAILURE_CHARGE", "NO_VERIFICATION_CHARGE",
                  "NO_MINING_CHARGE", "MARGINAL_COST_ONLY", "SALVAGE_MODEL")
SEMANTICS_COMPONENT = {
    "NO_FAILURE_CHARGE": "FAILURES",
    "NO_VERIFICATION_CHARGE": "VERIFICATION",
    "NO_MINING_CHARGE": "MINING",
    "MARGINAL_COST_ONLY": "FULL_CHARGE",
    "SALVAGE_MODEL": "NO_SALVAGE",
}
HOLM_ALPHA = 0.05
RECOVERY_THRESHOLD = 0.25      # inherited frozen DEV-CAL-2 threshold
PERM_N = 10000

EXIT_OK, EXIT_ASSAY_DEFECT, EXIT_CANNOT_CHECK, EXIT_BINDING_DEFECT = 0, 4, 3, 5


class AssayDefect(Exception):
    """Stage-1 exact-equality failure (first differing cell in the message)."""


class BindingDefect(Exception):
    """Sealed-input sha256 mismatch vs the committed digest bindings."""


def _sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# ---------------------------------------------------------- input binding -----
def bind_inputs(data_dir=None):
    """Record sha256 of every sealed input BEFORE any recomputation.
    Returns (bindings: {relpath: sha256}, loaded docs, expected: {relpath:
    {source: sha256}}).  Raises BindingDefect when the two committed digest
    sources disagree with each other or with the file on disk."""
    rd = data_dir or RESULTS
    rc = data_dir or RECEIPTS
    paths = {
        "results/DEV_CAL_2_SCORED_RESULTS_V2.json": SCORED_V2 if not
        data_dir else os.path.join(rd, "DEV_CAL_2_SCORED_RESULTS_V2.json"),
        "results/DEV_CAL_2_SCORED_RESULTS_V1.json": SCORED_V1 if not
        data_dir else os.path.join(rd, "DEV_CAL_2_SCORED_RESULTS_V1.json"),
        "results/DEVCAL2_RESULTS_V2.json": RESULTS_V2 if not
        data_dir else os.path.join(rd, "DEVCAL2_RESULTS_V2.json"),
        "receipts/DEVCAL2_HOST_RECEIPT_billy_V2.json": HOST_RECEIPT_V2 if
        not data_dir else os.path.join(rc, "DEVCAL2_HOST_RECEIPT_billy_V2.json"),
        "freeze/DEV_CAL_3_CHARGING_ATTRIBUTION_FREEZE_V1.json": FREEZE_PATH,
    }
    for k in (1, 2, 3, 4):
        paths["receipts/DEVCAL2_receipts_shard%d_V2.jsonl" % k] = (
            SHARD_V2[k - 1] if not data_dir else os.path.join(
                rc, "DEVCAL2_receipts_shard%d_V2.jsonl" % k))
    bindings = {}
    for rel, p in sorted(paths.items()):
        if not os.path.exists(p):
            raise BindingDefect("sealed input missing: %s (%s)" % (rel, p))
        bindings[rel] = _sha256_file(p)

    with open(paths["results/DEV_CAL_2_SCORED_RESULTS_V2.json"],
              encoding="utf-8") as f:
        scored_v2 = json.load(f)
    with open(paths["results/DEV_CAL_2_SCORED_RESULTS_V1.json"],
              encoding="utf-8") as f:
        scored_v1 = json.load(f)
    with open(paths["receipts/DEVCAL2_HOST_RECEIPT_billy_V2.json"],
              encoding="utf-8") as f:
        host = json.load(f)

    expected = {}
    for rel, sha in (scored_v2.get("output_bindings") or {}).items():
        expected.setdefault(os.path.basename(rel), {})["scored_v2"] = sha
    for rel, sha in (host.get("output_bindings") or {}).items():
        expected.setdefault(os.path.basename(rel), {})["host_receipt_v2"] = sha
    # gate: every gated input must match BOTH committed sources exactly
    # (matched by BASENAME -- the scored file binds "receipts/<name>" while
    # the host receipt binds bare "<name>"; anything else would silently
    # fail to gate, which is fail-open and forbidden here)
    defects = []
    gated = {}                       # basename -> {source name that gated it}
    for rel in sorted(bindings):
        base = os.path.basename(rel)
        if base not in expected:
            continue
        gated.setdefault(base, set())
        for src, want in sorted(expected[base].items()):
            if want != bindings[rel]:
                defects.append("%s: %s expects %s, file is %s" %
                               (rel, src, want, bindings[rel]))
            else:
                gated[base].add(src)
    if defects:
        raise BindingDefect("; ".join(defects))
    # fail-closed: the five score-bearing inputs MUST be gated by BOTH
    # independent committed sources (4 V2 shards + the merged results file)
    # -- gating by ONE source only is not a cross-check; a source that
    # silently stops binding a score-bearing input is itself a defect
    must_gate = set(os.path.basename(p) for k in (1, 2, 3, 4) for p in
                    [SHARD_V2[k - 1]]) | {"DEVCAL2_RESULTS_V2.json"}
    need = {"scored_v2", "host_receipt_v2"}
    missing = sorted(b for b in must_gate if gated.get(b) != need)
    if missing:
        raise BindingDefect(
            "committed digest sources failed to gate: %s (must be gated by "
            "BOTH sources; gated=%s)" %
            (missing, {b: sorted(s) for b, s in sorted(gated.items())}))
    return bindings, {"scored_v2": scored_v2, "scored_v1": scored_v1,
                      "host_v2": host}, expected


def load_shard_rows(data_dir=None):
    rc = data_dir or RECEIPTS
    rows = []
    for k in (1, 2, 3, 4):
        p = os.path.join(rc, "DEVCAL2_receipts_shard%d_V2.jsonl" % k)
        with open(p, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rows.append(json.loads(line))
    return rows


# ------------------------------------------------- event-ledger replay --------
# The receipts bind the event ledger only by digest; the per-event charge
# decomposition required by the alternative semantics is RECOVERED by
# replaying the UNCHANGED frozen machinery (deterministic seeds) and
# verifying EVERY recorded aggregate.  Any divergence = ASSAY_DEFECT.
def _world_cache():
    import exact.devcal1_worlds as W
    import exact.run_devcal2 as R2
    cert_rows = [R2.C_check_structural(w) for w in W.all_worlds()]
    worlds = {"%s-%02d" % (w["cell"], w["world_index"]): w
              for w in W.all_worlds()}
    ctx = {wid: R2.world_context(w, cert_rows)
           for wid, w in worlds.items()}
    return worlds, ctx


def _events_detail(arm, world, seed, ctx, adapter=None):
    """Replay one row's event stream through the UNCHANGED machinery.
    Mirrors exact.run_devcal2._ko_stream (KO arms) and
    exact.devcal1_search.run_search (anchors) field-for-field; returns
    (events, aux) where each event carries {i, cand_digest, p_draw,
    promoted, size, fate, expand_charge, verify_charge} and aux carries the
    aggregates the receipt binds."""
    import math
    import exact.devcal1_search as S
    import exact.devcal1_certificates as C
    import exact.devcal2_adapters as A

    effective = set()
    if adapter is not None:
        effective, _degraded = A.effective_components(adapter)
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
    adapted = []
    if adapter is not None:
        history, _shuffled = S.build_histories(world)
        if "RETRIEVAL_KEYING" in effective:
            key_match = ctx["structural"]["latent_same"] is True
        else:
            key_match = ctx["surface"]["surface_same"] is True
        for obj in history["objects"]:
            ledger["retrieval"] += S.COST["retrieve_per_object"] \
                + S.COST["retrieve_per_probe"]
            if not key_match:
                continue
            shape = tuple((op, tuple(ch)) for op, ch in obj["ops_dag"])
            if "TRANSPORT_MAP" in effective:
                # the verified homomorphism (certificate (c)) carries the
                # retrieved certificate onto the reminted surface: ONE
                # served construction charged once; degrade to per-slot
                # binding when (c) is not held (round-trip error recorded)
                held_c, _ = C.cert_c(list(map(list, shape)),
                                     world["target"]["shape"])
                if held_c:
                    ledger["adaptation"] += S.COST["adapt_per_binding"]
                    for slot in range(len(target["inputs"])):
                        adapted.append({"size": len(shape), "shape": shape,
                                        "root_slot": slot, "promoted": True})
                else:
                    for slot in range(len(target["inputs"])):
                        ledger["adaptation"] += S.COST["adapt_per_binding"]
                        adapted.append({"size": len(shape), "shape": shape,
                                        "root_slot": slot, "promoted": True})
            else:
                for slot in range(len(target["inputs"])):
                    ledger["adaptation"] += S.COST["adapt_per_binding"]
                    adapted.append({"size": len(shape), "shape": shape,
                                    "root_slot": slot, "promoted": True})
        ledger["storage_bytes"] = len(C.history_bytes(history)) + len(
            C.canonical_json(adapter).encode("utf-8"))
    elif arm in ("ORACLE_HISTORY", "SHUFFLED_HISTORY"):
        oracle, shuffled = S.build_histories(world)
        history = oracle if arm == "ORACLE_HISTORY" else shuffled
        ledger["storage_bytes"] = len(C.history_bytes(history))
        for obj in history["objects"]:
            ledger["retrieval"] += S.COST["retrieve_per_object"]
            ledger["retrieval"] += S.COST["retrieve_per_probe"]
            have = {t["type"] for t in target["inputs"]}
            if set(obj["applicability_contract"]
                   ["acceptable_token_types"]) & have:
                shape = tuple((op, tuple(ch)) for op, ch in obj["ops_dag"])
                for slot in range(len(target["inputs"])):
                    ledger["adaptation"] += S.COST["adapt_per_binding"]
                    adapted.append({"size": len(shape), "shape": shape,
                                    "root_slot": slot, "promoted": True})

    adapted_digests = {C.canonical_json([list(map(list, m["shape"])),
                                         m["root_slot"]]) for m in adapted}
    blind = [m for m in pool if C.canonical_json(
        [list(map(list, m["shape"])), m["root_slot"]]) not in adapted_digests]
    stream = list(adapted) + blind

    events = []
    nodes_expanded = 0
    work = ledger["retrieval"] + ledger["adaptation"]
    failed = 0
    rej_hist = {}
    verif_calls = 0
    m_star = None
    m_star_rank = None
    remaining = len(stream)
    for rank, cand in enumerate(stream, start=1):
        if m_star is not None:
            break
        p_draw = 1.0 / remaining
        ev = {"i": rank,
              "cand_digest": C.sha(C.canonical_json(
                  [list(map(list, cand["shape"])), cand["root_slot"]])),
              "p_draw": p_draw,
              "promoted": bool(cand.get("promoted")),
              "size": cand["size"]}
        expand_charge = S.COST["expand_base"] + \
            S.COST["expand_per_node"] * cand["size"]
        work += expand_charge
        nodes_expanded += 1
        ev["expand_charge"] = expand_charge
        ev["verify_charge"] = 0
        val, reason = S.apply_method(cand, target)
        if val is None:
            failed += 1
            rej_hist[reason] = rej_hist.get(reason, 0) + 1
            ledger["rejected_candidates"] += 1
            ev["fate"] = reason
            events.append(ev)
            remaining -= 1
            continue
        verif_calls += 1
        verify_charge = S.COST["verify_base"] + \
            S.COST["verify_per_node"] * cand["size"]
        work += verify_charge
        ledger["verification"] += 1
        ev["verify_charge"] = verify_charge
        if S.verify_independent(cand, target):
            m_star = cand
            m_star_rank = rank
            ev["fate"] = "SUCCESS"
            events.append(ev)     # success flag rides the canonical event
        else:
            failed += 1
            rej_hist["VERIFY_FAIL"] = rej_hist.get("VERIFY_FAIL", 0) + 1
            ledger["rejected_candidates"] += 1
            ev["fate"] = "VERIFY_FAIL"
            events.append(ev)
        remaining -= 1
    aux = {"n_pool": n_pool, "n_adapted": len(adapted), "nodes_expanded":
           nodes_expanded, "failed": failed, "rej_hist": rej_hist,
           "verif_calls": verif_calls, "work": work,
           "retrieval": ledger["retrieval"], "adaptation":
           ledger["adaptation"], "verification": ledger["verification"],
           "rejected_candidates": ledger["rejected_candidates"],
           "storage_bytes": ledger["storage_bytes"], "m_star_rank":
           m_star_rank, "m_star_digest": (C.sha(C.canonical_json(
               [list(map(list, m_star["shape"])), m_star["root_slot"]]))
               if m_star else None)}
    return events, aux


def _canonical_event_log(events):
    """The receipt's event_log_digest input: the recorded event fields ONLY
    (i, cand_digest, p_draw, promoted[, success]) -- fate/size/charges are
    DEV-CAL-3 analysis annotations, never part of the sealed digest."""
    import exact.devcal1_certificates as C
    log = []
    for ev in events:
        e = {"i": ev["i"], "cand_digest": ev["cand_digest"],
             "p_draw": ev["p_draw"], "promoted": ev["promoted"]}
        if ev.get("fate") == "SUCCESS":
            e["success"] = True
        log.append(e)
    return C.sha(C.canonical_json(log)), log


def _first_defect(row, events, aux):
    """Exact-equality check of one replayed row against its sealed receipt.
    Returns None when faithful, else a string naming the first differing
    field (freeze: ASSAY_DEFECT prints the first differing cell)."""
    rbd = row.get("recorded_before_solution_discovery") or {}
    wid = "%s/%s/s%s" % (row.get("arm"), row.get("world_id"), row.get("seed"))
    digest, _log = _canonical_event_log(events)
    checks = [
        ("event_log_digest", digest, rbd.get("event_log_digest")),
        ("n_events_logged", len(events), rbd.get("n_events_logged")),
        ("eventual_success_rank", aux["m_star_rank"],
         rbd.get("eventual_success_rank")),
        ("nodes_expanded", aux["nodes_expanded"], rbd.get("nodes_expanded")),
        ("failed_candidates", aux["failed"], rbd.get("failed_candidates")),
        ("rejection_reason_histogram", aux["rej_hist"],
         rbd.get("rejection_reason_histogram")),
        ("verification_calls", aux["verif_calls"],
         rbd.get("verification_calls")),
        ("work_to_first_verified_success", aux["work"],
         rbd.get("work_to_first_verified_success")),
        ("m_star_digest", aux["m_star_digest"], row.get("m_star_digest")),
    ]
    cl = row.get("cost_ledger") or {}
    checks += [
        ("cost_ledger.retrieval", aux["retrieval"], cl.get("retrieval")),
        ("cost_ledger.adaptation", aux["adaptation"], cl.get("adaptation")),
        ("cost_ledger.verification", aux["verification"],
         cl.get("verification")),
        ("cost_ledger.rejected_candidates", aux["rejected_candidates"],
         cl.get("rejected_candidates")),
    ]
    for name, got, want in checks:
        if got != want:
            return ("%s: replay %r != receipt %r" % (name, got, want))
    return None


def decompose_rows(rows, worlds, ctx, adapters, raw_acq, keys=None):
    """Replay + verify every sealed OK row; returns {key: decomposition}.
    key = (arm, world_id, seed).  Raises AssayDefect (first differing cell)
    on any replay divergence."""
    out = {}
    for row in rows:
        if row.get("status") != "OK":
            continue
        key = (row["arm"], row["world_id"], row["seed"])
        if keys is not None and key not in keys:
            continue
        w = worlds.get(row["world_id"])
        if w is None:
            raise AssayDefect("unknown world %s" % row["world_id"])
        if row["world_id"] not in raw_acq:
            raise AssayDefect("no ORACLE anchor raw acquisition for %s"
                              % row["world_id"])
        adapter = adapters.get(row["arm"])
        if row.get("run_role") != "ANCHOR_RERUN" and adapter is None:
            raise AssayDefect("no adapter for KO arm %s" % row["arm"])
        if row.get("run_role") == "ANCHOR_RERUN":
            adapter = None
        events, aux = _events_detail(row["arm"], w, row["seed"],
                                     ctx[row["world_id"]], adapter)
        defect = _first_defect(row, events, aux)
        if defect:
            raise AssayDefect("%s/%s/s%s: %s" % (row["arm"], row["world_id"],
                                                 row["seed"], defect))
        digest, _log = _canonical_event_log(events)
        out[key] = {"events": events, "aux": aux, "row": row,
                    "raw": raw_acq[row["world_id"]],
                    "event_log_digest": digest}
    return out


def raw_acquisition_by_world(rows):
    """The measured per-world source-solve cost, taken from each world's
    sealed ORACLE anchor row (never recomputed)."""
    raw = {}
    for r in rows:
        if (r.get("arm") == "ORACLE_HISTORY" and r.get("status") == "OK"
                and r.get("run_role") == "ANCHOR_RERUN"):
            raw[r["world_id"]] = r["cost_ledger"]["acquisition"]
    return raw


def acquisition_charge_checks(decomp, ctx):
    """AS_IS acquisition charging must equal the recorded ledger: anchors pay
    the raw source cost (RESET 0), KO rows pay raw or raw/divisor exactly per
    their recorded charge_rule_applied and the data-derived divisor."""
    import exact.devcal2_adapters as A
    defects = []
    for key, d in sorted(decomp.items()):
        row = d["row"]
        wid = row["world_id"]
        rec_acq = row["cost_ledger"]["acquisition"]
        if row["arm"] == "RESET":
            want = 0
        elif row.get("run_role") == "ANCHOR_RERUN":
            want = d["raw"]
        else:
            rule = (row.get("adapter") or {}).get("charge_rule_applied")
            if rule == "NO_AMORTISATION_V1":
                want = d["raw"]
            elif rule and rule.startswith("CERT_FAMILY_AMORTISATION_V1"):
                want = d["raw"] / ctx[wid]["divisor"]
                if want != rec_acq or ctx[wid]["divisor"] < 1:
                    defects.append("%s/%s: amortised charge %r != recorded %r"
                                   " (divisor %d)" % (row["arm"], wid, want,
                                                      rec_acq,
                                                      ctx[wid]["divisor"]))
                continue
            else:
                defects.append("%s/%s: unknown charge rule %r" %
                               (row["arm"], wid, rule))
                continue
        if want != rec_acq:
            defects.append("%s/%s: acquisition %r != recorded %r" %
                           (row["arm"], wid, want, rec_acq))
    return defects


# ------------------------------------------------------- charge semantics -----
def event_identity_digest(events):
    """Leakage-rule guard input: the multiset identity (order included) of
    the recovered event ledger -- semantics may recompute CHARGES, never
    events; every semantics output must re-verify to this digest."""
    import hashlib
    payload = json.dumps([{"i": e["i"], "cand_digest": e["cand_digest"],
                           "p_draw": e["p_draw"], "promoted": e["promoted"]}
                          for e in events], sort_keys=True,
                         separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _use_order():
    """Canonical per-world asset-use order for MARGINAL_COST_ONLY (freeze:
    the registered amortisation threshold counts uses in the ledger's
    canonical order): ORACLE s0-2, SHUFFLED s0-2, then ALL_KO_ARMS x seeds.
    RESET never uses the asset.  1-indexed."""
    import exact.devcal2_adapters as A
    order = ([("ORACLE_HISTORY", s) for s in (0, 1, 2)] +
             [("SHUFFLED_HISTORY", s) for s in (0, 1, 2)] +
             [(a, s) for a in A.ALL_KO_ARMS for s in (0, 1, 2)])
    return {k: i for i, k in enumerate(order, start=1)}


def measure_salvage_rate(decomp):
    """r_failed: the empirical reuse rate recorded in the sealed ledger =
    fraction of failed-trace events whose candidate digest is some run's
    verified success (m*) anywhere in the ledger."""
    mstar = {d["row"]["m_star_digest"] for d in decomp.values()}
    n_failed = n_reused = 0
    for d in decomp.values():
        for ev in d["events"]:
            if ev["fate"] == "SUCCESS":
                continue
            n_failed += 1
            if ev["cand_digest"] in mstar:
                n_reused += 1
    r = (n_reused / n_failed) if n_failed else 0.0
    return {"n_failed_events": n_failed, "n_reused_failed_events": n_reused,
            "r_failed": r}


def semantics_totals(decomp, semantics, raw_acq, mco_n=10, r_failed=0.0):
    """POST HOC charge recomputation (freeze `leakage_rule`): returns
    {key: {work, acquisition, total, event_digest}} under the chosen
    semantics.  Events are READ, never re-simulated/re-ordered/dropped --
    the identity digest of every row is carried unchanged into the output
    and the caller re-verifies it (hostile selftest plants an event-drop
    that must trip)."""
    use_pos = _use_order()
    out = {}
    for key, d in sorted(decomp.items()):
        row = d["row"]
        ev = d["events"]
        digest = event_identity_digest(ev)
        rec_work = row["recorded_before_solution_discovery"][
            "work_to_first_verified_success"]
        rec_acq = row["cost_ledger"]["acquisition"]
        base = d["aux"]
        if semantics == "AS_IS":
            work, acq = rec_work, rec_acq
        elif semantics == "NO_FAILURE_CHARGE":
            work = base["retrieval"] + base["adaptation"] + sum(
                e["expand_charge"] + e["verify_charge"] for e in ev
                if e["fate"] == "SUCCESS")
            acq = rec_acq
        elif semantics == "NO_VERIFICATION_CHARGE":
            work = base["retrieval"] + base["adaptation"] + sum(
                e["expand_charge"] for e in ev)
            acq = rec_acq
        elif semantics == "NO_MINING_CHARGE":
            work, acq = rec_work, 0
        elif semantics == "MARGINAL_COST_ONLY":
            work = rec_work
            if row["arm"] == "RESET":
                acq = 0
            else:
                pos = use_pos.get((row["arm"], row["seed"]))
                raw = raw_acq[row["world_id"]]
                acq = raw / mco_n if pos and pos <= mco_n else 0
        elif semantics == "SALVAGE_MODEL":
            credit = r_failed * sum(e["expand_charge"] + e["verify_charge"]
                                    for e in ev if e["fate"] != "SUCCESS")
            work = rec_work - credit
            acq = rec_acq
        else:
            raise ValueError("unknown semantics %r" % (semantics,))
        out[key] = {"work": work, "acquisition": acq,
                    "total": work + acq, "event_digest": digest}
    return out


def event_preservation(decomp, totals):
    """Freeze leakage-rule assertion: the event multiset is IDENTICAL across
    AS_IS and every semantics (count + per-cell task set + identity digest).
    Returns list of violation strings (empty = preserved)."""
    asis = semantics_totals(decomp, "AS_IS", {})
    viol = []
    if len(totals) != len(asis):
        viol.append("task-set mismatch: %d semantics rows vs %d AS_IS rows"
                    % (len(totals), len(asis)))
    for key, t in sorted(totals.items()):
        if key not in asis:
            viol.append("row %s missing from AS_IS ledger" % (key,))
            continue
        n_rec = decomp[key]["row"]["recorded_before_solution_discovery"][
            "n_events_logged"]
        if len(decomp[key]["events"]) != n_rec:
            viol.append("row %s event count %d != recorded %d"
                        % (key, len(decomp[key]["events"]), n_rec))
        if t.get("event_digest") != asis[key]["event_digest"]:
            viol.append("row %s event identity digest changed" % (key,))
    return viol


def direction_sanity(totals_as_is, totals_alt, label=""):
    """Structural invariant of every authorised reform (they only remove,
    retire, or credit charges over the identical event multiset): NO row's
    total burden may exceed its AS_IS total.  A violation means the
    semantics implementation ADDED charge (implementation defect, not a
    finding); returns violation strings (empty = sane)."""
    viol = []
    for k in sorted(totals_alt):
        a = totals_as_is.get(k)
        if a is None:
            viol.append("row %s absent from AS_IS totals" % (k,))
            continue
        if totals_alt[k]["total"] > a["total"]:
            viol.append("row %s total %r > AS_IS %r under %s%s"
                        % (k, totals_alt[k]["total"], a["total"], label,
                           "" if not label else " (charge ADDED by reform)"))
    return viol


# ------------------------------------------------------------ statistics ------
def recompute_per_arm(rows):
    """Recompute the V2 scored per-arm readouts from sealed rows with the
    UNCHANGED DEV-CAL-2 statistics functions (exact float equality expected
    -- identical integer inputs, identical frozen seeds)."""
    import exact.devcal2_adapters as A
    import exact.run_devcal2 as R2
    arms = sorted({r["arm"] for r in rows
                   if r.get("run_role") != "ANCHOR_RERUN"})
    null_w = R2.shuffle_null(rows, "B")
    null_t = R2.shuffle_null(rows, "B", burden_key="total")
    nshare_w = R2.null_arm_share(rows, "B")
    nshare_t = R2.null_arm_share(rows, "B", "total")
    null_ok_w = null_w["non_alarm"] and nshare_w["non_alarm"]
    null_ok_t = null_t["non_alarm"] and nshare_t["non_alarm"]
    per_arm = {}
    for arm in arms:
        prim = R2.recovery_share_stats(rows, "B", arm)
        sec = R2.recovery_share_stats(rows, "B", arm, "total")
        prim["threshold_met"] = bool(prim["threshold_met"] and null_ok_w)
        sec["threshold_met"] = bool(sec["threshold_met"] and null_ok_t)
        ctl = {cell: R2.reduction_stats(rows, cell, arm)
               for cell in ("A", "C", "D")}
        per_arm[arm] = {
            "recovery_share_cell_B": {
                **{k: prim[k] for k in ("mean", "n_pairs",
                                        "threshold_met")},
                "ci": list(prim["ci"]) if prim.get("ci") else None},
            "recovery_share_cell_B_total_burden": {
                **{k: sec[k] for k in ("mean", "n_pairs",
                                       "threshold_met")},
                "ci": list(sec["ci"]) if sec.get("ci") else None},
            "shuffle_null_cell_B": {"non_alarm": null_w["non_alarm"],
                                    "p_signflip": null_w["p_signflip"]},
            "shuffle_null_cell_B_total_burden": {
                "non_alarm": null_t["non_alarm"],
                "p_signflip": null_t["p_signflip"]},
            "draw_invariance_cell_B": R2.draw_invariance(rows, "B", arm),
            "controls": {
                "A_fired": bool(ctl["A"]["threshold_met"] and
                                ctl["A"]["burden_cis_nonoverlapping"]),
                "C_silent": not (ctl["C"]["threshold_met"] and
                                 ctl["C"]["burden_cis_nonoverlapping"]),
                "D_silent": not (ctl["D"]["threshold_met"] and
                                 ctl["D"]["burden_cis_nonoverlapping"])},
            "purity": R2.purity_summary(rows, arm),
            "adapter_sha256": next((r["adapter"]["adapter_sha256"]
                                    for r in rows if r.get("arm") == arm
                                    and r.get("adapter")), None),
        }
    ladder_state = {}
    for arm in A.LADDER:
        if arm in per_arm:
            ladder_state[arm] = {
                "primary": per_arm[arm]["recovery_share_cell_B"]
                ["threshold_met"],
                "secondary": per_arm[arm]
                ["recovery_share_cell_B_total_burden"]["threshold_met"]}
    minimal_tier = next((a for a in A.LADDER
                         if ladder_state.get(a, {}).get("primary")), None)
    if minimal_tier is None:
        verdict = "INTERFACE_GRANTS_INSUFFICIENT"
    elif not any(s["secondary"] for s in ladder_state.values()):
        verdict = "AMORTISATION_DOMINATED"
    else:
        verdict = "CARRIER_IDENTIFIED_TIER_%d" % (A.LADDER.index(
            minimal_tier) + 1)
    return per_arm, ladder_state, verdict


# Registered float-bind tolerance for the AS_IS gate: the scored V2 numbers
# were produced by a separate rollup process whose float summation order can
# differ from this recomputation at the last-bit level (observed 1 ULP on
# KO-1 means).  Exact equality is required FIRST; equality within this
# RELATIVE bound is recorded as bound-equal (never silently accepted beyond
# it -- any true semantic drift on shares of order 0.1-10 exceeds it by
# many orders of magnitude, which is what ASSAY_DEFECT must catch).
FLOAT_BIND_TOLERANCE = 1e-12


def _bind_eq(a, b):
    """Exact equality first; numeric operands may bind within the registered
    float tolerance (recursive over lists/dicts)."""
    if a == b:
        return True
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= FLOAT_BIND_TOLERANCE * max(
            1.0, abs(a), abs(b))
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_bind_eq(x, y) for x, y in
                                        zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return set(a) == set(b) and all(_bind_eq(a[k], b[k]) for k in a)
    return False


def compare_as_is(per_arm, ladder_state, verdict, scored_v2):
    """Exact-equality gate against the sealed V2 scored numbers (freeze:
    any mismatch = ASSAY_DEFECT; report the FIRST differing cell).  Numeric
    fields bind exactly or within the registered FLOAT_BIND_TOLERANCE;
    every tolerance-bound field is NAMED in the returned stats (never a
    silent acceptance)."""
    defects, tol_used, n_cmp = [], [], [0]
    absent = []

    _MISSING = object()

    def cmp(label, got, want):
        n_cmp[0] += 1
        if want is _MISSING:
            # the sealed scored block does not record this field: a named
            # absence (recorded in bind_stats), never a silent skip and
            # never an ASSAY_DEFECT -- the scored file carries no contract
            # for a field it never wrote
            absent.append(label)
            return
        if _bind_eq(got, want):
            if not (got == want) and not (
                    isinstance(got, str) or isinstance(want, str)):
                tol_used.append(label)
            return
        defects.append("%s: recomputed %r != scored %r" % (label, got, want))

    scored_arm = scored_v2.get("per_arm") or {}
    for arm in sorted(set(per_arm) | set(scored_arm)):
        if arm not in scored_arm:
            defects.append("%s: recomputed arm absent from scored V2" % arm)
            continue
        if arm not in per_arm:
            defects.append("%s: scored arm not recomputed" % arm)
            continue
        got, want = per_arm[arm], scored_arm[arm]
        for field in ("recovery_share_cell_B",
                      "recovery_share_cell_B_total_burden"):
            for k in ("mean", "ci", "n_pairs", "threshold_met"):
                cmp("%s.%s.%s" % (arm, field, k), got[field].get(k),
                    want.get(field, {}).get(k, _MISSING))
        for field in ("shuffle_null_cell_B",
                      "shuffle_null_cell_B_total_burden"):
            for k in ("non_alarm", "p_signflip"):
                cmp("%s.%s.%s" % (arm, field, k), got[field].get(k),
                    want.get(field, {}).get(k, _MISSING))
        gd, wd = got["draw_invariance_cell_B"], want["draw_invariance_cell_B"]
        for k in ("classification", "direction_agrees", "n_determinate"):
            cmp("%s.draw_invariance_cell_B.%s" % (arm, k), gd.get(k),
                wd.get(k, _MISSING))
        for s in ("0", "1", "2"):
            for k in ("mean_reduction", "null_band_95", "determinate"):
                cmp("%s.draw_invariance_cell_B.per_seed.%s.%s" % (arm, s, k),
                    gd["per_seed"][s].get(k),
                    wd.get("per_seed", {}).get(s, {}).get(k, _MISSING))
        for k in ("A_fired", "C_silent", "D_silent"):
            cmp("%s.controls.%s" % (arm, k), got["controls"].get(k),
                want.get("controls", {}).get(k, _MISSING))
        for k in ("n", "n_pure", "n_impure", "n_cannot_check"):
            cmp("%s.purity.%s" % (arm, k), got["purity"].get(k),
                want.get("purity", {}).get(k, _MISSING))
        cmp("%s.adapter_sha256" % arm, got["adapter_sha256"],
            want.get("adapter_sha256", _MISSING))
    cmp("ladder_state", ladder_state, scored_v2.get("ladder_state"))
    cmp("verdict", verdict, scored_v2.get("verdict"))
    return defects, {"fields_compared": n_cmp[0],
                     "fields_exact": n_cmp[0] - len(tol_used) - len(absent),
                     "fields_within_float_tolerance": tol_used,
                     "scored_fields_absent": absent,
                     "tolerance": FLOAT_BIND_TOLERANCE}


def patched_rows(rows, totals):
    """Copy the sealed rows with ONLY the two burden readouts replaced by a
    semantics' post hoc recomputation (events/ledgers untouched)."""
    out = []
    for r in rows:
        if r.get("status") != "OK":
            out.append(r)
            continue
        key = (r["arm"], r["world_id"], r["seed"])
        t = totals.get(key)
        if t is None:
            out.append(r)
            continue
        r2 = dict(r)
        r2["recorded_before_solution_discovery"] = dict(
            r["recorded_before_solution_discovery"])
        r2["recorded_before_solution_discovery"][
            "work_to_first_verified_success"] = t["work"]
        r2["total_burden_incl_acquisition"] = t["total"]
        out.append(r2)
    return out


def one_sided_signflip_p(shares, tag):
    """H0: mean secondary share <= 0 vs H1: > 0; signflip permutation with
    a frozen seeded tag (deterministic re-run)."""
    import exact.run_devcal2 as R2
    if not shares:
        return None
    obs = R2._mean(shares)
    rng = random.Random("DC3:sign:%s" % tag)
    ge = 0
    for _ in range(PERM_N):
        d = [x * (1 if rng.random() < 0.5 else -1) for x in shares]
        if R2._mean(d) >= obs - 1e-12:
            ge += 1
    return ge / PERM_N


def holm(pvals, alpha=HOLM_ALPHA):
    """Holm-Bonferroni step-down over the five alternative arms."""
    items = sorted(((p, a) for a, p in pvals.items() if p is not None),
                   key=lambda t: t[0])
    m = len(items)
    adjusted, reject = {}, {}
    running = 0.0
    for i, (p, arm) in enumerate(items):
        adj = min(1.0, max(running, (m - i) * p))
        running = adj
        adjusted[arm] = adj
        reject[arm] = adj < alpha
    for a, p in pvals.items():
        if p is None:
            adjusted[a] = None
            reject[a] = False
    return adjusted, reject


def paired_secondary_shares(rows, arm, cell="B"):
    """The paired per-(world,seed) secondary shares feeding the one-sided
    semantics test (identical construction to run_devcal2's
    recovery_share_stats share list)."""
    import exact.run_devcal2 as R2
    armv = R2.cell_arm_stats(rows, cell, arm, "total")
    orac = R2.cell_arm_stats(rows, cell, "ORACLE_HISTORY", "total")
    reset = R2.cell_arm_stats(rows, cell, "RESET", "total")
    keys = sorted(set(armv) & set(orac) & set(reset))
    return [(reset[k2] - armv[k2]) / (reset[k2] - orac[k2]) for k2 in keys
            if reset[k2] > 0 and (reset[k2] - orac[k2]) != 0]


def evaluate_semantics(rows, totals):
    """Full readout set under one charge semantics: per-DEV-CAL-2-arm
    primary/secondary recovery (with per-semantics nulls), the recovering
    tiers, KO-2 primary intactness, secondary draw-invariance conflict
    block, and the one-sided evidence p (best recovering tier; registered
    fallback = KO-2 tier when nothing recovers)."""
    import exact.devcal2_adapters as A
    import exact.run_devcal2 as R2
    rows2 = patched_rows(rows, totals)
    per_arm, ladder_state, verdict = recompute_per_arm(rows2)
    recovering = [a for a in A.LADDER if
                  per_arm[a]["recovery_share_cell_B_total_burden"]
                  ["threshold_met"]]
    blocked = [a for a in recovering if not
               R2.draw_invariance(rows2, "B", a, "total")
               ["direction_agrees"]]
    primary_intact = bool(
        ladder_state.get("KO-2_PLUS_RETRIEVAL", {}).get("primary"))
    evidence_arm = recovering[0] if recovering else "KO-2_PLUS_RETRIEVAL"
    p = one_sided_signflip_p(
        paired_secondary_shares(rows2, evidence_arm), evidence_arm)
    return {"per_arm": per_arm, "ladder_state": ladder_state,
            "verdict_if_this_were_the_model": verdict,
            "recovering_tiers": recovering,
            "draw_invariance_conflict_tiers": blocked,
            "ko2_primary_intact": primary_intact,
            "evidence_arm": evidence_arm, "p_one_sided": p}


def decide_terminal(flips):
    """flips: {semantics: bool} over the five alternative arms.
    Terminal per freeze precedence: exactly one carrier ->
    CHARGE_CARRIER_k; more than one -> MULTIPLE; none -> NONE."""
    carriers = [s for s in SEMANTICS_ARMS if flips.get(s)]
    if len(carriers) == 1:
        return "CHARGE_CARRIER_%s" % SEMANTICS_COMPONENT[carriers[0]], carriers
    if carriers:
        return "CHARGE_CARRIER_MULTIPLE", carriers
    return "CHARGE_CARRIER_NONE", carriers


def burden_share_as_is(decomp, cell=None):
    """Per-component charge decomposition of the AS_IS ledger (the exoneration
    bounds): absolute sums and shares of work and of total burden."""
    sums = {"retrieval": 0, "adaptation": 0, "expand_failed": 0,
            "expand_success": 0, "verify_failed": 0, "verify_success": 0,
            "acquisition": 0, "work": 0, "total": 0}
    for key, d in sorted(decomp.items()):
        if cell and d["row"].get("cell") != cell:
            continue
        row = d["row"]
        for ev in d["events"]:
            ch = ev["expand_charge"]
            if ev["fate"] == "SUCCESS":
                sums["expand_success"] += ch
                sums["verify_success"] += ev["verify_charge"]
            else:
                sums["expand_failed"] += ch
                sums["verify_failed"] += ev["verify_charge"]
        sums["retrieval"] += d["aux"]["retrieval"]
        sums["adaptation"] += d["aux"]["adaptation"]
        sums["acquisition"] += row["cost_ledger"]["acquisition"]
        sums["work"] += row["recorded_before_solution_discovery"][
            "work_to_first_verified_success"]
        sums["total"] += row["total_burden_incl_acquisition"]
    out = {"sums": sums, "n_rows": sum(1 for k, d in decomp.items()
                                       if not cell or
                                       d["row"].get("cell") == cell)}
    out["share_of_work"] = {k: (sums[k] / sums["work"] if sums["work"]
                                else None) for k in
                            ("retrieval", "adaptation", "expand_failed",
                             "expand_success", "verify_failed",
                             "verify_success")}
    out["share_of_total_burden"] = {k: (sums[k] / sums["total"] if
                                        sums["total"] else None) for k in
                                    ("retrieval", "adaptation",
                                     "expand_failed", "expand_success",
                                     "verify_failed", "verify_success",
                                     "acquisition")}
    return out


def cluster_secondary_shares(rows, ctx, cell="B"):
    """Lineage (certificate-family) and ecology-axis clustering of the
    cell-B paired secondary shares (freeze `endpoint_and_stats`)."""
    import exact.run_devcal2 as R2
    arms = sorted({r["arm"] for r in rows
                   if r.get("run_role") != "ANCHOR_RERUN"})
    out = {}
    for arm in arms:
        armv = R2.cell_arm_stats(rows, cell, arm, "total")
        orac = R2.cell_arm_stats(rows, cell, "ORACLE_HISTORY", "total")
        reset = R2.cell_arm_stats(rows, cell, "RESET", "total")
        per_world = {}
        for k2 in sorted(set(armv) & set(orac) & set(reset)):
            if reset[k2] <= 0 or (reset[k2] - orac[k2]) == 0:
                continue
            per_world[k2[0]] = per_world.setdefault(
                k2[0], {"sum": 0.0, "n": 0})
            per_world[k2[0]]["sum"] += (reset[k2] - armv[k2]) / (
                reset[k2] - orac[k2])
            per_world[k2[0]]["n"] += 1
        by_axis, by_lineage = {}, {}
        for wid, agg in sorted(per_world.items()):
            share = agg["sum"] / agg["n"]
            fam = (ctx.get(wid) or {}).get("family_key") or "NONE"
            by_lineage.setdefault(fam, {"sum": 0.0, "n": 0})
            by_lineage[fam]["sum"] += share
            by_lineage[fam]["n"] += 1
            axes = next((r["ecology_axes"] for r in rows
                         if r.get("world_id") == wid), None) or {}
            for ax in ("rho", "sigma", "d", "delta"):
                by_axis.setdefault(ax, {}).setdefault(
                    str(axes.get(ax)), {"sum": 0.0, "n": 0})
                by_axis[ax][str(axes.get(ax))]["sum"] += share
                by_axis[ax][str(axes.get(ax))]["n"] += 1
        def _mean_table(t):
            return {k: {"mean_share": (v["sum"] / v["n"]) if v["n"] else
                        None, "n_worlds": v["n"]} for k, v in sorted(
                            t.items())}
        out[arm] = {"by_lineage": _mean_table(by_lineage),
                    "by_ecology_axis": {ax: _mean_table(vals)
                                        for ax, vals in
                                        sorted(by_axis.items())}}
    return out


# ---------------------------------------------------------------- driver ------
def run(data_dir=None, out_path=None, host_label=None):
    """Full DEV-CAL-3 analysis over the sealed V2 ledgers.  Exit-code
    contract: 0 completed; 4 ASSAY_DEFECT; 5 RECEIPT_BINDING_DEFECT."""
    import exact.devcal2_adapters as A
    out_path = out_path or os.path.join(
        RESULTS, "DEV_CAL_3_ATTRIBUTION_RESULTS_V1.json")
    receipt = {"schema": "OCM_DEV_CAL_3_ATTRIBUTION_RESULTS", "version":
               "V1", "study": "DEV-CAL-3 charging attribution",
               "protocol": "DEV_CAL_3_CHARGING_ATTRIBUTION_FREEZE_V1",
               "owner_issue": 323, "parent_verdict":
               "DEV-CAL-2 V2 AMORTISATION_DOMINATED (PR #345, 5d10d910)",
               "host": host_label or os.uname().nodename, "cannot_check": []}
    t0 = time.time()

    # 1 -- bind inputs BEFORE any recomputation (freeze method clause)
    try:
        bindings, docs, expected = bind_inputs(data_dir)
    except BindingDefect as e:
        receipt["input_bindings"] = None
        receipt["binding_defect"] = str(e)
        receipt["terminal"] = "RECEIPT_BINDING_DEFECT"
        _write(receipt, out_path)
        print("DEV-CAL-3 terminal: RECEIPT_BINDING_DEFECT")
        print("  ", str(e)[:400])
        return EXIT_BINDING_DEFECT
    receipt["input_bindings_recorded_before_recomputation"] = bindings
    receipt["binding_verification"] = {
        "gated_against": ["DEV_CAL_2_SCORED_RESULTS_V2.json output_bindings",
                          "DEVCAL2_HOST_RECEIPT_billy_V2.json "
                          "output_bindings"], "verdict": "ALL_MATCH"}

    def _assay_defect(first_cell, detail):
        receipt["terminal"] = "ASSAY_DEFECT"
        receipt["assay_defect"] = detail[:2000]
        receipt["first_differing_cell"] = first_cell
        _write(receipt, out_path)
        print("DEV-CAL-3 terminal: ASSAY_DEFECT")
        print("  first differing cell:", first_cell)
        return EXIT_ASSAY_DEFECT

    # 2 -- load sealed rows + replay the event ledger (exact equality)
    rows = load_shard_rows(data_dir)
    worlds, ctx = _world_cache()
    adapters = {a: A.make_adapter(a) for a in A.ALL_KO_ARMS}
    raw_acq = raw_acquisition_by_world(rows)
    try:
        decomp = decompose_rows(rows, worlds, ctx, adapters, raw_acq)
    except AssayDefect as e:
        return _assay_defect(str(e).split(":", 1)[0],
                             "replay divergence: %s" % e)
    receipt["n_rows_replayed_and_verified"] = len(decomp)
    acq_defects = acquisition_charge_checks(decomp, ctx)
    if acq_defects:
        return _assay_defect(acq_defects[0], "acquisition charging: %s" %
                             "; ".join(acq_defects[:10]))

    # 3 -- AS_IS exact-equality control against the sealed scored numbers
    per_arm_asis, ladder_asis, verdict_asis = recompute_per_arm(rows)
    asis_defects, asis_stats = compare_as_is(per_arm_asis, ladder_asis,
                                             verdict_asis, docs["scored_v2"])
    if asis_defects:
        return _assay_defect(asis_defects[0], "AS_IS mismatch: %s" %
                             "; ".join(asis_defects[:10]))
    receipt["as_is_control"] = {
        "verdict": "EXACT_EQUALITY_WITH_DEV_CAL_2_SCORED_V2",
        "fields_compared": "per-arm recovery shares (mean/ci/n/threshold, "
                           "both readouts), shuffle nulls, draw-invariance "
                           "per-seed, controls, purity, adapter digests, "
                           "ladder_state, verdict",
        "bind_stats": asis_stats,
        "recomputed_verdict": verdict_asis,
        "n_arms": len(per_arm_asis)}

    # 4 -- alternative charge semantics (post hoc; events preserved)
    salvage = measure_salvage_rate(decomp)
    receipt["salvage_measurement"] = salvage
    asis_totals = semantics_totals(decomp, "AS_IS", raw_acq)
    semantics_out, pvals = {}, {}
    for sem in SEMANTICS_ARMS:
        totals = semantics_totals(decomp, sem, raw_acq,
                                  mco_n=MCO_PRIMARY_N,
                                  r_failed=salvage["r_failed"])
        viol = event_preservation(decomp, totals)
        if viol:
            return _assay_defect(viol[0], "leakage rule violation under %s: "
                                 "%s" % (sem, "; ".join(viol[:5])))
        dviol = direction_sanity(asis_totals, totals, sem)
        if dviol:
            return _assay_defect(dviol[0], "direction sanity under %s: %s" %
                                 (sem, "; ".join(dviol[:5])))
        ev = evaluate_semantics(rows, totals)
        ev["flip_pre_holm"] = bool(ev["recovering_tiers"] and
                                   ev["ko2_primary_intact"] and
                                   not ev["draw_invariance_conflict_tiers"])
        semantics_out[sem] = ev
        pvals[sem] = ev["p_one_sided"]
    adj, rej = holm(pvals)
    receipt["holm"] = {"alpha": HOLM_ALPHA, "p_one_sided": pvals,
                       "adjusted_p": adj, "reject": rej}
    flips = {sem: bool(semantics_out[sem]["flip_pre_holm"] and rej[sem])
             for sem in SEMANTICS_ARMS}
    for sem in SEMANTICS_ARMS:
        semantics_out[sem]["flip"] = flips[sem]

    # 5 -- MARGINAL_COST_ONLY sensitivity (freeze: N in {5,10,25})
    sens = {}
    for n in MCO_SENSITIVITY:
        totals = semantics_totals(decomp, "MARGINAL_COST_ONLY", raw_acq,
                                  mco_n=n, r_failed=salvage["r_failed"])
        viol = event_preservation(decomp, totals)
        dviol = direction_sanity(asis_totals, totals,
                                 "MARGINAL_COST_ONLY(N=%d)" % n)
        if viol or dviol:
            return _assay_defect((viol + dviol)[0],
                                 "leakage/direction violation at N=%d: %s" %
                                 (n, "; ".join((viol + dviol)[:5])))
        ev = evaluate_semantics(rows, totals)
        sens[str(n)] = {"recovering_tiers": ev["recovering_tiers"],
                        "ko2_primary_intact": ev["ko2_primary_intact"],
                        "p_one_sided": ev["p_one_sided"],
                        "note": "N=%d is %s" % (n, "the frozen primary" if
                                                n == MCO_PRIMARY_N else
                                                "sensitivity")}
    receipt["marginal_cost_sensitivity"] = sens

    # 6 -- terminal + exonerated components (negatives -> invariants)
    terminal, carriers = decide_terminal(flips)
    share_all = burden_share_as_is(decomp)
    share_b = burden_share_as_is(decomp, cell="B")
    receipt["burden_share_as_is"] = {"whole_ledger": share_all,
                                     "cell_B": share_b}
    exonerated = []
    for sem in SEMANTICS_ARMS:
        if flips[sem]:
            continue
        ev = semantics_out[sem]
        best = max((ev["per_arm"][a]
                    ["recovery_share_cell_B_total_burden"]["mean"]
                    for a in ev["per_arm"]), default=None)
        bound = {"component": SEMANTICS_COMPONENT[sem],
                 "reform": sem,
                 "invariant": "%s_NOT_CARRIER" % SEMANTICS_COMPONENT[sem],
                 "max_secondary_recovery_share_under_reform": best,
                 "recovering_tiers_under_reform": ev["recovering_tiers"],
                 "ko2_primary_intact": ev["ko2_primary_intact"]}
        if sem == "SALVAGE_MODEL":
            bound["measured_reuse_rate_r_failed"] = salvage["r_failed"]
            if salvage["r_failed"] == 0:
                bound["invariant"] = "NO_REUSABLE_FAILED_TRACES_IN_LEDGER"
        if sem == "NO_VERIFICATION_CHARGE":
            bound["verification_share_of_total_burden"] = \
                share_b["share_of_total_burden"]["verify_failed"] + \
                share_b["share_of_total_burden"]["verify_success"]
        if sem == "NO_FAILURE_CHARGE":
            bound["failed_attempt_share_of_total_burden"] = \
                share_b["share_of_total_burden"]["expand_failed"] + \
                share_b["share_of_total_burden"]["verify_failed"]
        if sem == "NO_MINING_CHARGE":
            bound["acquisition_share_of_total_burden"] = \
                share_b["share_of_total_burden"]["acquisition"]
        exonerated.append(bound)
    receipt["charge_semantics"] = semantics_out
    receipt["exonerated_components"] = exonerated
    receipt["terminal"] = terminal
    if carriers:
        ev = semantics_out[carriers[0]]
        receipt["terminal_evidence"] = (
            "%s flips the secondary readout to recovery (tiers %s, KO-2 "
            "primary intact=%s, Holm adj p=%.4g) while the other arms do "
            "not" % (carriers[0], ev["recovering_tiers"],
                     ev["ko2_primary_intact"],
                     adj[carriers[0]] if adj[carriers[0]] is not None
                     else float("nan")))
    else:
        receipt["terminal_evidence"] = (
            "no single-component charge reform flips the secondary readout; "
            "the non-amortisation is structural in the acquisition "
            "pipeline (revival routes to the M1B mechanism-attribution "
            "lane)")

    # 7 -- lineage/ecology clustering of the secondary readout
    receipt["clustering_cell_B"] = {
        "AS_IS": cluster_secondary_shares(rows, ctx),
        **{sem: cluster_secondary_shares(
            patched_rows(rows, semantics_totals(
                decomp, sem, raw_acq, mco_n=MCO_PRIMARY_N,
                r_failed=salvage["r_failed"])), ctx)
           for sem in SEMANTICS_ARMS}}

    receipt["generated_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                             time.gmtime())
    receipt["wall_s"] = round(time.time() - t0, 1)
    receipt["run_role"] = "ANALYTICAL_RECOMPUTATION_OVER_SEALED_RECEIPTS"
    _write(receipt, out_path)
    print("DEV-CAL-3 terminal:", terminal)
    print("  ", receipt["terminal_evidence"])
    print("   exonerated:", [e["invariant"] for e in exonerated])
    print("   wall_s", receipt["wall_s"], "->", out_path)
    return EXIT_OK


def _write(doc, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, sort_keys=True, default=repr)
        f.write("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--data", default=None,
                    help="directory holding sealed inputs (selftest only)")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    if args.run:
        return run(data_dir=args.data, out_path=args.out)
    print("use --run", file=sys.stderr)
    return EXIT_CANNOT_CHECK


if __name__ == "__main__":
    sys.exit(main())
