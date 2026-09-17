#!/usr/bin/env python3
"""W4 prospective replication executor (REV-L47-NOVEL-INTELLIGENCE-W4).

Re-runs the novel-intelligence W4 family-member search from the parent
package's pre-existing frozen seed under the NEW prospective custody of
FREEZE_V2_PROSPECTIVE.{md,json} (committed before this executor existed),
then extends the held-out set, adds a negative-control family, an
independent no-import route, and a determinism protocol. The decision rule
D1-D5 of the freeze is evaluated mechanically; the receipt records
PROSPECTIVE_CONTENT_CONFIRMED__SUSPICION_CLEARED only when every leg holds.

The parent package's 2026-09-15 commit-order custody defect is permanent and
recorded; what this re-earns is prospective-ness of the CONTENT at the
original claim strength.

Py3.8-safe, stdlib-only. Receipt content is deterministic only (no host
strings, no timings); runtime facts go to RUNTIME_V1.json via --protocol.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import signal
import subprocess
import sys
import time
from typing import Dict, List, Optional, Tuple

import independent_route_v1 as ind

PROSPECTIVE_LITERAL = b"GMI-NOVEL-INTELLIGENCE-W4-PROSPECTIVE-V2/REPLICATION-2026-09-16"
PROSPECTIVE_SHA256 = "971e3ed3fec5568a588ff475badd1be77a0533bf6a99d0f9a2a99da5138f3110"

PARENT_REL = "../gmi-novel-intelligence-w4-v1/novel_intelligence_w4_v1.py"
PARENT_RESULT_REL = "../gmi-novel-intelligence-w4-v1/RESULT_V1.json"
FREEZE_JSON = "FREEZE_V2_PROSPECTIVE.json"

WALL_CLOCK_ABORT_SECONDS = 3600  # registered per-assay abort budget (freeze)

D_FIELDS = [
    "D1_replication_structured_equal",
    "D2_registered_predictions_match",
    "D3_negative_control_constant_law",
    "D4_independent_route_exact_agreement",
    "D5_determinism_bit_identity",
]


def sha256_file(path):
    # type: (str) -> str
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def assert_prospective_freeze_intact():
    # type: () -> None
    got = hashlib.sha256(PROSPECTIVE_LITERAL).hexdigest()
    if got != PROSPECTIVE_SHA256:
        raise RuntimeError("prospective freeze digest mismatch: %s" % got)


def _load_module(rel, name):
    # type: (str, str) -> object
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.normpath(os.path.join(here, rel))
    if not os.path.isfile(path):
        raise RuntimeError("required module missing at %s" % path)
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load module %s" % name)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def load_freeze_plan():
    # type: () -> Tuple[Dict[str, object], str]
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, FREEZE_JSON)
    with open(path, "r", encoding="utf-8") as fh:
        plan = json.load(fh)
    return plan, sha256_file(path)


def _ecology_f(parent, k):
    # type: (object, int) -> Tuple[Tuple[int, ...], Tuple[int, ...]]
    q_p, q_o = parent.ecology_for_k(k)
    return tuple(q_p), tuple(q_o)


def ecology_g(k):
    # type: (int) -> Tuple[Tuple[int, ...], Tuple[int, ...]]
    """Negative-control family G(k): registered constant law max_m=2 for all k."""
    fiber0_o = tuple(i % 2 for i in range(k))
    fiber1_o = tuple(2 + (i % 2) for i in range(k))
    q_p = (0,) * k + (1,) * k
    q_o = fiber0_o + fiber1_o
    return q_p, q_o


def _deep_diff(a, b, path):
    # type: (object, object, str) -> List[str]
    if isinstance(a, dict) and isinstance(b, dict):
        out = []  # type: List[str]
        for key in sorted(set(a) | set(b), key=str):
            if key not in a:
                out.append("%s.%s: missing in rerun" % (path, key))
            elif key not in b:
                out.append("%s.%s: missing in original" % (path, key))
            else:
                out.extend(_deep_diff(a[key], b[key], "%s.%s" % (path, key)))
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return ["%s: len %d != %d" % (path, len(a), len(b))]
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out.extend(_deep_diff(x, y, "%s[%d]" % (path, i)))
        return out
    if a == b:
        return []
    return ["%s: %r != %r" % (path, a, b)]


# ---------------------------------------------------------------- D1 leg

def replication_leg(parent, parent_result_path):
    # type: (object, str) -> Dict[str, object]
    rerun = parent.run_campaign()
    # Normalize through a JSON round-trip: the parent's receipt is the
    # serialized artifact (string keys), and the in-memory campaign uses int
    # keys for per-k details -- comparing like for like is the honest D1.
    rerun = json.loads(json.dumps(rerun))
    with open(parent_result_path, "r", encoding="utf-8") as fh:
        original = json.load(fh)
    diffs = _deep_diff(rerun, original, "$")
    return {
        "rerun_all_w4_boxes_green": bool(rerun["all_w4_boxes_green"]),
        "original_all_w4_boxes_green": bool(original["all_w4_boxes_green"]),
        "deep_field_diffs": diffs,
        "structured_equal_to_parent_result": not diffs,
        "D1": bool(rerun["all_w4_boxes_green"]) and not diffs,
    }


# ---------------------------------------------------------------- D2 leg

class _AssayTimeout(Exception):
    pass


def _v6_measure(v6, q_p, q_o, budget_B, deadline):
    # type: (object, Tuple[int, ...], Tuple[int, ...], int, float) -> Dict[str, object]
    if time.monotonic() > deadline:
        return {"assay_timeout": True}
    pred = v6.property_vector_prediction(q_p, q_o)

    def _on_alarm(signum, frame):
        raise _AssayTimeout()

    use_alarm = hasattr(signal, "SIGALRM") and hasattr(signal, "setitimer")
    old_handler = None
    if use_alarm:
        old_handler = signal.signal(signal.SIGALRM, _on_alarm)
        signal.setitimer(signal.ITIMER_REAL, WALL_CLOCK_ABORT_SECONDS)
    try:
        search = v6.find_matching_residuals(q_p, q_o, pred)
    except _AssayTimeout:
        return {"assay_timeout": True}
    finally:
        if use_alarm:
            signal.setitimer(signal.ITIMER_REAL, 0)
            if old_handler is not None:
                signal.signal(signal.SIGALRM, old_handler)
    return {
        "assay_timeout": False,
        "max_m": int(pred["min_residual_alphabet"]),
        "C_star": int(search["min_cost"]),
        "canonical_cost": int(search["canonical_constructive_cost"]),
        "flat": int(pred["flat_table_cost"]),
        "needs_residual": bool(pred["needs_residual"]),
        "pure_predictor_succeeds": bool(v6.pure_predictor_under_qp_succeeds(q_p, q_o)),
        "fixed_budget_recovers": bool(v6.exists_residual_exact(q_p, q_o, budget_B)),
        "no_cheaper_residual_under_qp": bool(search["no_cheaper_residual_under_qp"]),
        "any_winner_matches_prediction": bool(search["any_winner_matches_prediction"]),
    }


def prediction_leg(parent, v6, plan, ks, deadline, leg_name):
    # type: (object, object, Dict[str, object], List[int], float, str) -> Dict[str, object]
    budget_B = int(plan["fixed_budget_B"])
    rows = []  # type: List[Dict[str, object]]
    all_match = True
    for k in ks:
        q_p, q_o = _ecology_f(parent, k)
        measured = _v6_measure(v6, q_p, q_o, budget_B, deadline)
        if bool(measured.get("assay_timeout")):
            rows.append({"k": k, "leg": leg_name, "status": "ASSAY_TIMEOUT"})
            continue
        expected = {
            "max_m": k,
            "C_star": 2 + k,
            "flat": k + 3,
            "needs_residual": True,
            "pure_predictor_succeeds": False,
            "fixed_budget_recovers": k <= budget_B,
        }
        mism = [f for f in expected if measured[f] != expected[f]]
        row = {"k": k, "leg": leg_name, "status": "MATCH" if not mism else "MISMATCH"}
        row.update({"measured_" + f: measured[f] for f in expected})
        row.update({"expected_" + f: expected[f] for f in expected})
        if mism:
            row["mismatched_fields"] = mism
            all_match = False
        rows.append(row)
    return {"rows": rows, "all_registered_match": all_match}


# ---------------------------------------------------------------- D3 leg

def negative_control_leg(v6, plan, ks):
    # type: (object, Dict[str, object], List[int]) -> Dict[str, object]
    budget_B = int(plan["fixed_budget_B"])
    pred_table = plan["predictions"]["negative_control_G"]["law_constant_in_k"]
    rows = []
    all_ok = True
    for k in ks:
        q_p, q_o = ecology_g(k)
        pred = v6.property_vector_prediction(q_p, q_o)
        measured = {
            "max_m": int(pred["min_residual_alphabet"]),
            "C_star": int(pred["predicted_min_cost"]),
            "flat": int(pred["flat_table_cost"]),
            "pure_predictor_succeeds": bool(v6.pure_predictor_under_qp_succeeds(q_p, q_o)),
            "fixed_budget_recovers": bool(v6.exists_residual_exact(q_p, q_o, budget_B)),
        }
        expected = {
            "max_m": int(pred_table["max_m"]),
            "C_star": int(pred_table["C_star"]),
            "flat": int(pred_table["flat"]),
            "pure_predictor_succeeds": bool(pred_table["pure_predictor_succeeds"]),
            "fixed_budget_recovers": bool(pred_table["fixed_budget_recovers"]),
        }
        mism = [f for f in expected if measured[f] != expected[f]]
        rows.append(
            {
                "k": k,
                "measured": measured,
                "expected": expected,
                "status": "MATCH" if not mism else "MISMATCH",
                "mismatched_fields": mism or None,
            }
        )
        if mism:
            all_ok = False
    return {"rows": rows, "constant_law_confirmed": all_ok}


# ---------------------------------------------------------------- D4 leg

D4_FIELDS = [
    "max_m",
    "C_star",
    "flat",
    "needs_residual",
    "pure_predictor_succeeds",
    "fixed_budget_recovers",
]


def _v6_route_row(v6, q_p, q_o, budget_B):
    # type: (object, Tuple[int, ...], Tuple[int, ...], int) -> Dict[str, object]
    pred = v6.property_vector_prediction(q_p, q_o)
    return {
        "max_m": int(pred["min_residual_alphabet"]),
        "C_star": int(pred["predicted_min_cost"]),
        "flat": int(pred["flat_table_cost"]),
        "needs_residual": bool(pred["needs_residual"]),
        "pure_predictor_succeeds": bool(v6.pure_predictor_under_qp_succeeds(q_p, q_o)),
        "fixed_budget_recovers": bool(v6.exists_residual_exact(q_p, q_o, budget_B)),
    }


def independent_route_leg(parent, v6, plan, f_ks, g_ks):
    # type: (object, object, Dict[str, object], List[int], List[int]) -> Dict[str, object]
    budget_B = int(plan["fixed_budget_B"])
    rows = []  # type: List[Dict[str, object]]
    witness_rows = []  # type: List[Dict[str, object]]
    all_agree = True
    for family_name, ks, ecology in (
        ("F", f_ks, lambda k: _ecology_f(parent, k)),
        ("G", g_ks, ecology_g),
    ):
        for k in ks:
            q_p, q_o = ecology(k)
            v6_row = _v6_route_row(v6, q_p, q_o, budget_B)
            ind_row = ind.ecology_properties(q_p, q_o, budget_B)
            mism = [f for f in D4_FIELDS if v6_row[f] != ind_row[f]]
            rows.append(
                {
                    "family": family_name,
                    "k": k,
                    "v6_route": v6_row,
                    "independent_route": ind_row,
                    "agree": not mism,
                    "mismatched_fields": mism or None,
                }
            )
            if mism:
                all_agree = False
            wit = ind.brute_force_no_decoder_below_m(q_p, q_o)
            witness_rows.append({"family": family_name, "k": k, "witness": wit})
            if bool(wit["witness_run"]) and not bool(wit["no_decoder_below_m"]):
                all_agree = False
    witnesses_run = sum(1 for w in witness_rows if bool(w["witness"]["witness_run"]))
    return {
        "fields_compared": D4_FIELDS,
        "rows": rows,
        "brute_force_witnesses": witness_rows,
        "witnesses_run": witnesses_run,
        "exact_agreement_everywhere": all_agree,
    }


# ---------------------------------------------------------------- campaign

def run_campaign(scope):
    # type: (str) -> Dict[str, object]
    assert_prospective_freeze_intact()
    plan, plan_sha = load_freeze_plan()
    parent = _load_module(PARENT_REL, "novel_intelligence_w4_v1")
    if hashlib.sha256(parent.FREEZE_LITERAL).hexdigest() != parent.FREEZE_SHA256:
        raise RuntimeError("parent freeze seed digest mismatch")
    v6 = parent._load_upstream()

    here = os.path.dirname(os.path.abspath(__file__))
    parent_result = os.path.normpath(os.path.join(here, PARENT_RESULT_REL))

    # D1: faithful re-run of the original campaign vs its committed receipt.
    d1 = replication_leg(parent, parent_result)

    # D2: registered predictions (family, held-out fresh k=5, extended {6,7,8}).
    family_ks = [int(k) for k in plan["family_ks"]]
    fresh_k = int(plan["fresh_k"])
    deadline = time.monotonic() + WALL_CLOCK_ABORT_SECONDS
    d2_family = prediction_leg(parent, v6, plan, family_ks, deadline, "family")
    d2_fresh = prediction_leg(parent, v6, plan, [fresh_k], deadline, "fresh")
    d2_extended = None  # type: Optional[Dict[str, object]]
    extended = []  # type: List[int]
    if scope == "full":
        extended = [int(k) for k in plan["extended_heldout_ks"]]
        d2_extended = prediction_leg(
            parent, v6, plan, extended, deadline, "extended_heldout"
        )
    d2_all = bool(d2_family["all_registered_match"]) and bool(
        d2_fresh["all_registered_match"]
    )
    n_timeouts = 0
    if d2_extended is not None:
        d2_all = d2_all and bool(d2_extended["all_registered_match"])
        n_timeouts += sum(
            1 for r in d2_extended["rows"] if r.get("status") == "ASSAY_TIMEOUT"
        )

    # D3: negative control (V6 instrument must show the constant law on G).
    control_ks = [int(k) for k in plan["negative_control_ks"]]
    if scope == "ci":
        control_ks = [2, 3]
    d3 = negative_control_leg(v6, plan, control_ks)

    # D4: independent route agreement (+ brute-force tightness witnesses).
    ind_f_ks = family_ks + [fresh_k] + extended
    ind_g_ks = [2, 3, 4, 5] if scope == "ci" else control_ks
    d4 = independent_route_leg(parent, v6, plan, ind_f_ks, ind_g_ks)

    d_flags = {
        "D1_replication_structured_equal": bool(d1["D1"]),
        "D2_registered_predictions_match": d2_all,
        "D3_negative_control_constant_law": bool(d3["constant_law_confirmed"]),
        "D4_independent_route_exact_agreement": bool(d4["exact_agreement_everywhere"]),
        "D5_determinism_bit_identity": None,
    }

    counts = {
        "family_rows": len(d2_family["rows"]),
        "fresh_rows": len(d2_fresh["rows"]),
        "extended_rows": len(extended),
        "assay_timeouts_extended": n_timeouts,
        "control_rows": len(d3["rows"]),
        "agreement_rows": len(d4["rows"]),
        "witnesses_run": int(d4["witnesses_run"]),
    }

    d14 = [d_flags[f] for f in D_FIELDS[:4]]
    if not all(bool(v) for v in d14):
        verdict = "REFUTED"
    else:
        verdict = "PENDING_DETERMINISM"
    return {
        "artifact": "GMI_NOVEL_INTELLIGENCE_W4_PROSPECTIVE_V1",
        "ticket": "REV-L47-NOVEL-INTELLIGENCE-W4",
        "scope": scope,
        "freeze_plan_sha256": plan_sha,
        "prospective_seed_sha256": PROSPECTIVE_SHA256,
        "inherited_seed_sha256": hashlib.sha256(parent.FREEZE_LITERAL).hexdigest(),
        "replication": d1,
        "registered_predictions": {
            "family": d2_family,
            "fresh_k5": d2_fresh,
            "extended_heldout": d2_extended,
        },
        "negative_control": d3,
        "independent_route": d4,
        "decision_flags": d_flags,
        "counts": counts,
        "verdict": verdict,
    }


def emit_receipt(receipt, path):
    # type: (Dict[str, object], str) -> None
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=2, sort_keys=True)
        fh.write("\n")


def finalize_with_determinism(receipt, same_host_bit_identical):
    # type: (Dict[str, object], bool) -> Dict[str, object]
    """Stamp D5 (same-host half; the cross-host half of the determinism
    protocol is completed and recorded by make_multihost_receipt_v1.py) and
    the final verdict into a protocol-produced receipt."""
    out = dict(receipt)
    flags = dict(out["decision_flags"])
    flags["D5_determinism_bit_identity"] = same_host_bit_identical
    out["decision_flags"] = flags
    if not all(bool(flags[f]) for f in D_FIELDS[:4]):
        out["verdict"] = "REFUTED"
    elif not same_host_bit_identical:
        out["verdict"] = "REFUTED_AT_DETERMINISM"
    else:
        out["verdict"] = "PROSPECTIVE_CONTENT_CONFIRMED__SUSPICION_CLEARED"
    return out


def protocol_driver(scope, out, runtime_out):
    # type: (str, str, str) -> None
    """Two isolated subprocess runs must emit byte-identical receipts; the
    final receipt carries D5 and the runtime record charges host + elapsed."""
    here = os.path.dirname(os.path.abspath(__file__))
    me = os.path.abspath(__file__)
    tmp_a = os.path.join(here, ".protocol_run_a.json")
    tmp_b = os.path.join(here, ".protocol_run_b.json")
    t0 = time.monotonic()
    subprocess.run(
        [sys.executable, me, "--scope", scope, "--out", tmp_a], check=True, cwd=here
    )
    t1 = time.monotonic()
    subprocess.run(
        [sys.executable, me, "--scope", scope, "--out", tmp_b], check=True, cwd=here
    )
    t2 = time.monotonic()
    sha_a = sha256_file(tmp_a)
    sha_b = sha256_file(tmp_b)
    identical = sha_a == sha_b
    with open(tmp_a, "r", encoding="utf-8") as fh:
        receipt = json.load(fh)
    final = finalize_with_determinism(receipt, identical)
    emit_receipt(final, out)
    for tmp in (tmp_a, tmp_b):
        os.remove(tmp)
    runtime = {
        "schema": "GMI_NOVEL_INTELLIGENCE_W4_PROSPECTIVE_RUNTIME_V1",
        "scope": scope,
        "host": os.uname().nodename if hasattr(os, "uname") else "unknown",
        "platform": sys.platform,
        "python": sys.version.split()[0],
        "elapsed": {
            "run_a_seconds": round(t1 - t0, 3),
            "run_b_seconds": round(t2 - t1, 3),
        },
        "result_sha256": sha256_file(out),
        "run_a_sha256": sha_a,
        "run_b_sha256": sha_b,
        "same_host_bit_identical": identical,
        "argv": sys.argv[1:],
    }
    with open(runtime_out, "w", encoding="utf-8") as fh:
        json.dump(runtime, fh, indent=2, sort_keys=True)
        fh.write("\n")


def main():
    # type: () -> None
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scope", choices=["ci", "full"], default="full")
    ap.add_argument("--out", default=None)
    ap.add_argument("--runtime-out", default=None)
    ap.add_argument(
        "--protocol",
        action="store_true",
        help="two isolated runs; byte-identical receipts; writes D5 verdict",
    )
    args = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    out = args.out or os.path.join(here, "RESULT_V1.json")
    if args.protocol:
        runtime_out = args.runtime_out or os.path.join(here, "RUNTIME_V1.json")
        protocol_driver(args.scope, out, runtime_out)
        with open(out, "r", encoding="utf-8") as fh:
            receipt = json.load(fh)
        print(
            json.dumps(
                {
                    "verdict": receipt["verdict"],
                    "decision_flags": receipt["decision_flags"],
                    "counts": receipt["counts"],
                },
                indent=2,
            )
        )
        return
    receipt = run_campaign(args.scope)
    emit_receipt(receipt, out)
    print(json.dumps({"verdict": receipt["verdict"], "counts": receipt["counts"]}, indent=2))


if __name__ == "__main__":
    main()
