"""FNA-8/D9 driver: instrumented micro-execution of the privilege ladder.

Executes the rungs current-main artifacts support on the frozen world WL1:

- Rung 6 (bounded domain, no frontier model as central cognition): fully
  executable — pure OCM arms (incumbent first-PASS policy, analytic GUARDED
  parent per #219's guard-first conclusion, labelled ORACLE bound) over the
  whole frozen stream including the drift and revocation windows.
- Rung 1 (LLM controls + OCM records): shadow micro-execution. The frontier
  model (gpt-5.5 via the pinned local codex CLI) is the CONTROLLER — it
  chooses the operator and delivers its own computed answer; the OCM side
  records every call/decision/check/commit and never selects.
- Rung 2 (LLM proposes, OCM selects/commits): the model proposes a ranked
  candidate list; the INCUMBENT exact machinery executes the proposals in
  order and commits the first checker-correct result. The model never
  supplies the committed answer.
- Rungs 3-5: NOT executed. Their activation gate (causal functional
  replacements from FNA-7/#208 transplants, see PROTOCOL.md) is unmet on
  current main; recorded as pending with the explicit gate, claiming nothing.

NEVER fabricates model output: parse failures, illegal operator ids and call
failures are recorded as control failures; mock mode is stamped MOCK and never
scored into terminals.
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))                        # capsule modules
sys.path.insert(0, str(HERE.parents[1] / "src"))     # incumbent ocm package

import fna8_world as W                               # noqa: E402
from fna8_ledger import CostLedger, Recorder         # noqa: E402
from fna8_model import (MODEL_CONFIG, make_model,    # noqa: E402
                        mock_controller_reply, mock_proposal_reply)

SCHEMA = "ocm.fna.fna8-privilege-ladder.run.v1"
EPS = 0.05                       # frozen capability-preservation margin
EVAL_CAP_MODEL = 24              # frozen: model arms see at most 24 EVAL queries
REV_CAP_MODEL = 8                # frozen: model arms re-ask at most 8 REV queries
GUARD_EXACT_TOL = 2.0            # frozen guard rule: exact if <= 2x cheapest approx
FORBIDDEN_TOKENS = ("TRANSFORMER_REPLACED", "LLM_EQUIVALENT",
                    "GENERAL_SUPERIORITY", "AGI")


def _now() -> str:
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


# ------------------------------------------------------------------------------------------------
# frozen windows
# ------------------------------------------------------------------------------------------------


def splits(queries):
    out = {"DEV": [], "EVAL": [], "DRIFT": []}
    for q in queries:
        out[W.split_of(q.qid)].append(q)
    for k in out:
        out[k] = sorted(out[k], key=lambda q: q.qid)
    return out


def rev_atom(world, eval_queries) -> str:
    """Frozen rule: first atom (sorted) appearing in >= 3 EVAL slices."""
    counts = {}
    for q in eval_queries:
        for aid in q.slice_ids:
            counts[aid] = counts.get(aid, 0) + 1
    for aid in sorted(counts):
        if counts[aid] >= 3:
            return aid
    raise AssertionError("frozen world has no atom with >=3 EVAL membership")


def dev_example(world, dev_queries):
    """Frozen one-shot worked example: first DEV query + its exact answer."""
    if not dev_queries:
        return None
    q = dev_queries[0]
    return q, q.exact_answer(world["atoms"])


# ------------------------------------------------------------------------------------------------
# OCM-side attempt loop (rungs 6 and 2)
# ------------------------------------------------------------------------------------------------


def run_attempts(world, q, order, ledger, rung, arm, extra_select_work=0):
    """Execute attempts in `order`; commit first checker-correct; else scan.

    Returns (delivered, first_pass, fallback, source, exec_work, check_work).
    """
    atoms = world["atoms"]
    insts = {i.op_id: i for i in world["catalogue"]}
    _, sel_work = W.applicable(world, q)
    exec_work, check_work = extra_select_work + sum(sel_work.values()), 0
    first_pass, fallback, source = False, False, None
    for attempt_idx, op_id in enumerate(order):
        inst = insts.get(op_id)
        if inst is None:
            continue
        _law, w, ans = W.execute_instance(inst, q, atoms, world["state"])
        ok, cw = W.check(q, atoms, ans)
        exec_work += w
        check_work += cw
        if ok:
            first_pass = attempt_idx == 0
            source = "exact_%s" % inst.family if inst.family in W.EXACT_FAMILIES \
                else "approx_%s" % inst.family
            return True, first_pass, fallback, source, exec_work, check_work
    # portfolio recovery: safe scan (always applicable, always correct)
    scan = [i for i in world["catalogue"] if i.family == "scan"][0]
    _law, w, ans = W.execute_instance(scan, q, atoms, world["state"])
    ok, cw = W.check(q, atoms, ans)
    exec_work += w
    check_work += cw
    assert ok
    return True, first_pass, True, "exact_scan", exec_work, check_work


def arm_order(world, q, arm) -> List[str]:
    """Frozen per-arm attempt order over the applicable set."""
    insts, _ = W.applicable(world, q)
    ids = [i.op_id for i in insts]
    if arm == "A0_ORACLE":
        return ids  # executes all; commit cheapest correct is applied by caller
    if arm == "A1_INCUMBENT":
        return [i.op_id for i in world["catalogue"] if i.op_id in ids]
    if arm == "A2_GUARDED":
        exact = [i for i in insts if i.family in W.EXACT_FAMILIES]
        approx = [i for i in insts if i.family not in W.EXACT_FAMILIES]
        exact.sort(key=lambda i: i.declared_cost_estimate(q, world["state"]))
        approx.sort(key=lambda i: i.declared_cost_estimate(q, world["state"]))
        if exact and (not approx or
                      exact[0].declared_cost_estimate(q, world["state"]) <=
                      GUARD_EXACT_TOL * approx[0].declared_cost_estimate(q, world["state"])):
            return [exact[0].op_id]
        if approx:
            return [approx[0].op_id]
        return [i.op_id for i in insts if i.family == "scan"]
    raise ValueError(arm)


def run_oracle(world, q, ledger):
    """Labelled ORACLE bound: execute ALL applicable, commit cheapest correct."""
    insts, sel_work = W.applicable(world, q)
    atoms = world["atoms"]
    exec_work, check_work = sum(sel_work.values()), 0
    best = None
    for inst in sorted(insts, key=lambda i: i.op_id):
        _law, w, ans = W.execute_instance(inst, q, atoms, world["state"])
        ok, cw = W.check(q, atoms, ans)
        exec_work += w
        check_work += cw
        if ok and (best is None or w < best[0]):
            best = (w, inst)
    source = "oracle"
    return True, bool(best), False, source, exec_work, check_work


# ------------------------------------------------------------------------------------------------
# rung 6 — bounded domain, no frontier model anywhere in the loop
# ------------------------------------------------------------------------------------------------


def run_rung6(world, sp, params) -> Dict:
    ledgers = {}
    for arm in ("A0_ORACLE", "A1_INCUMBENT", "A2_GUARDED"):
        ledgers[arm] = CostLedger("R6", arm)
    ledgers["A1_INCUMBENT"].state_growth["index_entries"] = len(world["index"])
    ledgers["A2_GUARDED"].state_growth["index_entries"] = len(world["index"])
    for arm, ledger in ledgers.items():
        ledger.acquisition_work["index_build_work"] = world["index_build_work"]
        if arm == "A2_GUARDED":
            ledger.acquisition_work["guard_derivation_work"] = 3  # re-derived from spec
        ledger.acquisition_work["authored_prior_bytes"] = 0      # no authored policy text
    # EVAL window
    for q in sp["EVAL"]:
        for arm, ledger in ledgers.items():
            if arm == "A0_ORACLE":
                d, fp, fb, src, ew, cw = run_oracle(world, q, ledger)
            else:
                d, fp, fb, src, ew, cw = run_attempts(world, q, arm_order(world, q, arm),
                                                      ledger, "R6", arm)
            ledger.record_query(q.qid, fp, d, fb, ew, 0, cw, src)
    # DRIFT window: frozen catalogue mutation, index rebuild charged to everyone
    world["state"] = {"scan_version_mult": 1.6, "drift": True}
    rebuild = W.rebuild_index(world)
    for arm, ledger in ledgers.items():
        ledger.maintenance_and_revision["drift_index_rebuild_work"] = \
            world["index_build_work"]
    for q in sp["DRIFT"]:
        for arm, ledger in ledgers.items():
            if arm == "A0_ORACLE":
                d, fp, fb, src, ew, cw = run_oracle(world, q, ledger)
            else:
                d, fp, fb, src, ew, cw = run_attempts(world, q, arm_order(world, q, arm),
                                                      ledger, "R6", arm)
            ledger.maintenance_and_revision["drift_recompute_work"] += ew + cw
            ledger.capability["n"] += 1
            ledger.capability["first_pass"] += int(fp)
            ledger.capability["delivered_correct"] += int(d)
            ledger.capability["fallbacks"] += int(fb)
            ledger.reasoning_work["queries"] += 1
            ledger.record_source(src)
    # REV window: frozen evidence revocation, affected EVAL queries re-answered
    world["state"] = {"scan_version_mult": 1.0, "drift": False}
    W.rebuild_index(world)
    ratom = rev_atom(world, sp["EVAL"])
    world["atoms"][ratom].revoked = True
    affected = [q for q in sp["EVAL"] if ratom in q.slice_ids]
    for arm, ledger in ledgers.items():
        ledger.maintenance_and_revision["revoked_atoms"] = 1
    for q in affected:
        for arm, ledger in ledgers.items():
            if arm == "A0_ORACLE":
                d, fp, fb, src, ew, cw = run_oracle(world, q, ledger)
            else:
                d, fp, fb, src, ew, cw = run_attempts(world, q, arm_order(world, q, arm),
                                                      ledger, "R6", arm)
            ledger.maintenance_and_revision["revision_recompute_work"] += ew + cw
    world["atoms"][ratom].revoked = False
    return {"ledgers": {a: ledgers[a].to_dict() for a in ledgers},
            "rev_atom": ratom, "n_affected_eval": len(affected)}


# ------------------------------------------------------------------------------------------------
# rung 1 — LLM controls, OCM records (shadow micro-execution)
# ------------------------------------------------------------------------------------------------


def _model_reply(model, prompt, q, world, propose):
    """One controller interaction. Mock mode uses the declared stub reply."""
    if model.mode == "mock":
        text = mock_proposal_reply(q, world) if propose else mock_controller_reply(q, world)
        return {"ok": True, "returncode": 0, "wall_s": 0.0, "tokens": 0,
                "message": text, "parse_failure": None, "mock": True}
    return model.call(prompt)


def run_rung1(world, sp, params, model, recorder, eval_cap, rev_cap) -> Dict:
    ledger = CostLedger("R1", "MODEL_CONTROLLER")
    ledger.acquisition_work["index_build_work"] = world["index_build_work"]
    ledger.acquisition_work["authored_prior_bytes"] = 3800  # frozen controller spec bytes
    example = dev_example(world, sp["DEV"])
    eval_qs = sp["EVAL"][:eval_cap]
    applicable_ids = lambda q: [i.op_id for i in W.applicable(world, q)[0]]  # noqa: E731
    for q in eval_qs:
        prompt = W.render_prompt(q, world, example=example, propose=False)
        call = _model_reply(model, prompt, q, world, propose=False)
        recorder.add("model_call", rung="R1", qid=q.qid, prompt_chars=len(prompt),
                     ok=call.get("ok"), parse_failure=call.get("parse_failure"))
        delivered, first_pass, fallback, source = False, False, False, None
        exec_work, check_work = 0, 0
        ctrl_failure = None
        if call.get("ok") and call.get("message") is not None:
            try:
                op_id, model_answer = W.parse_controller_line(q, call["message"])
                if op_id not in applicable_ids(q):
                    ctrl_failure = "illegal_or_inapplicable_operator"
                else:
                    inst = {i.op_id: i for i in world["catalogue"]}[op_id]
                    _law, w, _ans = W.execute_instance(inst, q, world["atoms"],
                                                       world["state"])
                    ok, cw = W.check(q, world["atoms"], model_answer)
                    exec_work = w + sum(W.applicable(world, q)[1].values())
                    check_work = cw
                    if ok:
                        delivered, first_pass, source = True, True, "model"
                    else:
                        ctrl_failure = "model_answer_failed_exact_check"
            except (ValueError, ZeroDivisionError) as exc:
                ctrl_failure = "parse_failure:%s" % exc
        else:
            ctrl_failure = "call_failed:%s" % call.get("parse_failure")
        if not delivered:
            d2, fp2, fb2, src2, ew2, cw2 = run_attempts(
                world, q, [i.op_id for i in W.applicable(world, q)[0] if i.family == "scan"],
                ledger, "R1", "MODEL_CONTROLLER")
            delivered, fallback, source = True, True, src2
            exec_work += ew2
            check_work += cw2
        ledger.record_query(q.qid, first_pass, delivered, fallback, exec_work,
                            0, check_work, source, model_call=call)
        ledger.per_query[-1]["ctrl_failure"] = ctrl_failure
        recorder.add("commit", rung="R1", qid=q.qid, source=source,
                     first_pass=first_pass, fallback=fallback)
    ledger.state_growth.update(recorder.state_growth())
    # REV window: revocation -> the controller must be re-asked (measured, not derived)
    ratom = rev_atom(world, sp["EVAL"])
    world["atoms"][ratom].revoked = True
    affected = [q for q in eval_qs if ratom in q.slice_ids][:rev_cap]
    for q in affected:
        prompt = W.render_prompt(q, world, example=example, propose=False)
        call = _model_reply(model, prompt, q, world, propose=False)
        ledger.maintenance_and_revision["revision_model_reasks"] += 1
        ledger.maintenance_and_revision["revision_recompute_work"] += 1
        ledger.model_usage["calls"] += 1
        if call.get("ok"):
            ledger.model_usage["calls_ok"] += 1
        else:
            ledger.model_usage["parse_failures"] += 1
        ledger.model_usage["tokens"] += int(call.get("tokens") or 0)
        ledger.model_usage["wall_s"] += float(call.get("wall_s") or 0.0)
        recorder.add("model_call", rung="R1", qid=q.qid, window="REV",
                     ok=call.get("ok"), parse_failure=call.get("parse_failure"))
    world["atoms"][ratom].revoked = False
    ledger.maintenance_and_revision["revoked_atoms"] = 1
    ledger.state_growth.update(recorder.state_growth())
    return {"ledger": ledger.to_dict(), "rev_atom": ratom,
            "n_rev_reasks": len(affected), "eval_n": len(eval_qs)}


# ------------------------------------------------------------------------------------------------
# rung 2 — LLM proposes, OCM selects/commits (incumbent machinery)
# ------------------------------------------------------------------------------------------------


def run_rung2(world, sp, params, model, recorder, eval_cap, rev_cap) -> Dict:
    ledger = CostLedger("R2", "MODEL_PROPOSER")
    ledger.acquisition_work["index_build_work"] = world["index_build_work"]
    ledger.acquisition_work["authored_prior_bytes"] = 3600  # frozen proposer spec bytes
    example = dev_example(world, sp["DEV"])
    eval_qs = sp["EVAL"][:eval_cap]
    legal_ids = [i.op_id for i in world["catalogue"]]
    for q in eval_qs:
        prompt = W.render_prompt(q, world, example=example, propose=True)
        call = _model_reply(model, prompt, q, world, propose=True)
        recorder.add("model_call", rung="R2", qid=q.qid, ok=call.get("ok"),
                     parse_failure=call.get("parse_failure"))
        proposal = []
        ctrl_failure = None
        if call.get("ok") and call.get("message") is not None:
            try:
                proposal = W.parse_proposal(call["message"], legal_ids)
                # incumbent selection: proposed order INTERSECT structural applicability
                applic = set(i.op_id for i in W.applicable(world, q)[0])
                order = [op for op in proposal if op in applic]
            except ValueError as exc:
                ctrl_failure = "parse_failure:%s" % exc
                order = []
        else:
            ctrl_failure = "call_failed:%s" % call.get("parse_failure")
            order = []
        d, fp, fb, src, ew, cw = run_attempts(world, q, order, ledger, "R2",
                                              "MODEL_PROPOSER")
        proposal_consumed = bool(order) and src in ("exact_probe", "exact_scan",
                                                    "approx_window", "approx_sample") \
            and not fb
        ledger.record_query(q.qid, fp, d, fb, ew, 0, cw, src, model_call=call)
        ledger.per_query[-1]["ctrl_failure"] = ctrl_failure
        ledger.per_query[-1]["proposal"] = proposal
        ledger.per_query[-1]["proposal_consumed"] = proposal_consumed
        recorder.add("commit", rung="R2", qid=q.qid, source=src, fallback=fb,
                     proposal=proposal)
    ledger.state_growth.update(recorder.state_growth())
    ratom = rev_atom(world, sp["EVAL"])
    world["atoms"][ratom].revoked = True
    affected = [q for q in eval_qs if ratom in q.slice_ids][:rev_cap]
    for q in affected:
        prompt = W.render_prompt(q, world, example=example, propose=True)
        call = _model_reply(model, prompt, q, world, propose=True)
        ledger.maintenance_and_revision["revision_model_reasks"] += 1
        ledger.maintenance_and_revision["revision_recompute_work"] += 1
        ledger.model_usage["calls"] += 1
        if call.get("ok"):
            ledger.model_usage["calls_ok"] += 1
        else:
            ledger.model_usage["parse_failures"] += 1
        ledger.model_usage["tokens"] += int(call.get("tokens") or 0)
        ledger.model_usage["wall_s"] += float(call.get("wall_s") or 0.0)
        recorder.add("model_call", rung="R2", qid=q.qid, window="REV",
                     ok=call.get("ok"), parse_failure=call.get("parse_failure"))
    world["atoms"][ratom].revoked = False
    ledger.maintenance_and_revision["revoked_atoms"] = 1
    ledger.state_growth.update(recorder.state_growth())
    return {"ledger": ledger.to_dict(), "rev_atom": ratom,
            "n_rev_reasks": len(affected), "eval_n": len(eval_qs)}


# ------------------------------------------------------------------------------------------------
# rungs 3-5 — activation gate unmet on current main; protocol-only records
# ------------------------------------------------------------------------------------------------


def pending_rungs() -> Dict:
    return {
        "R3": {"status": "RUNG_PENDING_ACTIVATION_GATE",
               "gate": "G2->3: FNA-7/#208 transplant T1 repository_semantic_retrieval "
                       "and T2 failure_classification each at "
                       "PARENT_SUFFICIENT_FOR_<capability> or "
                       "NON_NEURAL_NONINFERIOR_AT_REGISTERED_SCOPE, plus a "
                       "candidate-supply surface (code/text) the incumbent "
                       "planner can consume. Neither exists on current main."},
        "R4": {"status": "RUNG_PENDING_ACTIVATION_GATE",
               "gate": "G3->4: FNA-4/D6 library/synthesis parent suite (open) "
                       "sufficient for learned-operator supply; FNA-7 T4/T5 "
                       "transplants non-inferior; donor gate conceding policy "
                       "frozen. Not met."},
        "R5": {"status": "RUNG_PENDING_ACTIVATION_GATE",
               "gate": "G4->5: FNA-7 T3 API/interface_induction and T6 "
                       "verification_interpretation transplants non-inferior; "
                       "FNA-3/D5 sequence/grammar parents (open) bound the "
                       "language-proposal surface. Not met."},
    }


# ------------------------------------------------------------------------------------------------
# terminal evaluation (frozen; mock mode never scores)
# ------------------------------------------------------------------------------------------------


def _interface_refused(ledger_dict) -> bool:
    """Model arm never received a usable interface: calls were placed, none
    completed ok, and every query was rescued by the scan fallback. Pre-declared
    in PROTOCOL.md limitations as CANNOT_CHECK_NO_MODEL_ACCESS — an interface
    refusal is never scored as a model-capability result."""
    mu = ledger_dict["model_usage"]
    cap = ledger_dict["capability"]
    return mu["calls"] > 0 and mu["calls_ok"] == 0 and cap["n"] > 0 \
        and cap["fallbacks"] == cap["n"]


def evaluate_terminals(r6, r1, r2, model_mode) -> Dict:
    out = {"model_mode": model_mode, "rungs": {}}
    if model_mode == "MOCK":
        out["note"] = "MOCK mode: no terminals evaluated (mock is never scored)."
        return out
    inc = r6["ledgers"]["A1_INCUMBENT"]
    guard = r6["ledgers"]["A2_GUARDED"]
    inc_rate = inc["delivered_correct_rate"]
    guard_rate = guard["delivered_correct_rate"]
    if guard_rate is not None and guard_rate >= 1.0 - EPS and \
            guard["lifetime_logical_work"] <= (1 + EPS) * inc["lifetime_logical_work"]:
        out["rungs"]["R6"] = "PARENT_SUFFICIENT_FOR_obligation_control"
    elif inc_rate is not None and inc_rate >= 1.0 - EPS:
        out["rungs"]["R6"] = "NON_NEURAL_NONINFERIOR_AT_REGISTERED_SCOPE"
    else:
        out["rungs"]["R6"] = "CANNOT_CHECK_HARNESS_FAILED_BASELINE"
    if r1 is not None:
        if _interface_refused(r1["ledger"]):
            out["rungs"]["R1"] = "CANNOT_CHECK_NO_MODEL_ACCESS"
            out["r1_side_note"] = ("model surface refused every call at run time "
                                   "(interface failure, pre-declared); re-execute "
                                   "when the surface is live — receipts kept")
        else:
            m = r1["ledger"]["delivered_correct_rate"]
            best_ocm = max(x for x in (inc_rate, guard_rate) if x is not None)
            if m is not None and m < 1.0 - EPS:
                out["rungs"]["R1"] = "NO_FUNCTIONAL_PARITY_control_at_scope"
                out["r1_side_note"] = ("model controller below the frozen margin at "
                                       "scope: stepping R1->R6 is capability-preserving here")
            elif m is not None and m > best_ocm:
                out["rungs"]["R1"] = "NEURAL_DONOR_DOMINATES_AT_SCOPE"
            else:
                out["rungs"]["R1"] = "NON_NEURAL_NONINFERIOR_AT_REGISTERED_SCOPE"
    if r2 is not None:
        if _interface_refused(r2["ledger"]):
            out["rungs"]["R2"] = "CANNOT_CHECK_NO_MODEL_ACCESS"
            out["r2_side_note"] = ("model surface refused every call at run time "
                                   "(interface failure, pre-declared); re-execute "
                                   "when the surface is live — receipts kept")
        else:
            r = r2["ledger"]["delivered_correct_rate"]
            consumed = sum(1 for row in r2["ledger"]["per_query"]
                           if row.get("proposal_consumed"))
            if r is not None and r >= 1.0 - EPS:
                out["rungs"]["R2"] = "R2_CAPABILITY_PRESERVED_AT_SCOPE"
                out["r2_proposal_consumed_n"] = consumed
            else:
                out["rungs"]["R2"] = "NO_FUNCTIONAL_PARITY_proposal_at_scope"
    return out


# ------------------------------------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------------------------------------


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="FNA-8/D9 privilege-ladder micro-execution")
    ap.add_argument("--rung", choices=["6", "1", "2", "all"], required=True)
    ap.add_argument("--model", choices=["codex", "mock"], default="mock")
    ap.add_argument("--workdir", default="/tmp/fna8-codex-workdir")
    ap.add_argument("--tiny", action="store_true")
    ap.add_argument("--eval-cap", type=int, default=None)
    ap.add_argument("--rev-cap", type=int, default=None)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    params = W.WorldParams.tiny_params() if args.tiny else W.WorldParams()
    world = W.build_world(params)
    sp = splits(world["queries"])
    eval_cap = args.eval_cap if args.eval_cap is not None else \
        (min(8, len(sp["EVAL"])) if args.tiny else EVAL_CAP_MODEL)
    rev_cap = args.rev_cap if args.rev_cap is not None else \
        (min(3, len(sp["EVAL"])) if args.tiny else REV_CAP_MODEL)

    receipt = {
        "schema": SCHEMA, "generated_at_utc": _now(),
        "salt": W.SALT, "params": {"n_queries": params.n_queries, "n_atoms": params.n_atoms,
                                   "tiny": params.tiny},
        "splits": {k: len(v) for k, v in sp.items()},
        "model_mode": args.model.upper(),
        "model_config": dict(MODEL_CONFIG),
        "eps": EPS, "eval_cap_model": eval_cap, "rev_cap_model": rev_cap,
        "guard_exact_tol": GUARD_EXACT_TOL,
    }
    model = None
    if args.rung in ("1", "2", "all"):
        model = make_model(args.model, args.workdir)
        receipt["codex_version"] = getattr(model, "version", None)

    r6 = run_rung6(world, sp, params)
    receipt["rung6"] = r6
    world = W.build_world(params)  # fresh main-state world for model rungs
    r1 = r2 = None
    if args.rung in ("1", "all"):
        recorder = Recorder()
        r1 = run_rung1(world, sp, params, model, recorder, eval_cap, rev_cap)
        receipt["rung1"] = r1
    if args.rung in ("2", "all"):
        world = W.build_world(params)
        recorder2 = Recorder()
        r2 = run_rung2(world, sp, params, model, recorder2, eval_cap, rev_cap)
        receipt["rung2"] = r2
    receipt["pending_rungs"] = pending_rungs()
    receipt["terminals"] = evaluate_terminals(r6, r1, r2, args.model.upper())
    receipt["forbidden_token_scan"] = not any(
        t in json.dumps(receipt) for t in FORBIDDEN_TOKENS)

    Path(args.out).write_text(json.dumps(receipt, indent=1, default=str))
    summary = {
        "rung6_incumbent_rate": r6["ledgers"]["A1_INCUMBENT"]["delivered_correct_rate"],
        "rung6_guarded_rate": r6["ledgers"]["A2_GUARDED"]["delivered_correct_rate"],
        "terminals": receipt["terminals"].get("rungs"),
    }
    if r1 is not None:
        summary["rung1_model_rate"] = r1["ledger"]["delivered_correct_rate"]
        summary["rung1_tokens"] = r1["ledger"]["model_usage"]["tokens"]
    if r2 is not None:
        summary["rung2_rate"] = r2["ledger"]["delivered_correct_rate"]
        summary["rung2_tokens"] = r2["ledger"]["model_usage"]["tokens"]
    print(json.dumps(summary, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
