#!/usr/bin/env python3
"""Sweep runner for frozen CONT-CAL specs (HSG continuous calibration).

Handlers:
  CONT-CAL-01  eps_sensitivity_curve — router sweep over eps x theorem atoms x
               seeds; measures final_cost / receipts / donors_found per eps.
  CONT-CAL-02  halving_two_rung_rule — replays the 5 merged D12 arm logs under
               both cut rules (two-rung frozen vs single-rung counterfactual),
               counterfactual arithmetic on the logged (pair, rung, score)
               sequences. promotion_bar_assumed=7 (A5 header: score 0-10).
  CONT-CAL-03  inspection_cap_boundary — extracts (atom, donor) pairs accepted
               at L3 from the D12 logs; L4 verdict-flip purchase itself needs
               model-in-the-loop inspection -> emits PAIRS_READY, not MEASURED.

Each run writes results/<EXP>.results.jsonl (+ .summary.json) and, with
--update-ledger, flips the matching UNCERTAINTY_LEDGER_V1.json entry with
evidence (file + sha + measured value).

Usage: python3 calibrate.py --spec specs/CONT-CAL-01.json --bank DONOR_BANK_V1.jsonl \
                             --atoms ATOM_BANK_V1.jsonl --term-vocab TERM_VOCAB_V1.json \
                             [--update-ledger]
"""
import argparse, hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path

CONT = Path(__file__).resolve().parent
sys.path.insert(0, str(CONT))
import router as R  # noqa: E402

EPS_GRID = [0.02, 0.05, 0.10, 0.15, 0.18]     # inside admissible (0.0, 0.2)
PROMOTION_BAR = 7                              # A5 header: score = judgment 0-10
ARMS = ["A1", "A2", "A3", "A4", "A5"]

def sha256f(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def verify_spec(spec):
    body = dict(spec); body["frozen_sha"] = None
    want = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
    if want != spec["frozen_sha"]:
        sys.exit(f"spec frozen_sha mismatch: {spec['experiment']}")

def write_results(exp, rows, summary):
    out = CONT / "results" / f"{exp}.results.jsonl"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n")
    s = CONT / "results" / f"{exp}.summary.json"
    s.write_text(json.dumps(summary, indent=1) + "\n")
    return out, s

def update_ledger(entry_id, status, value, evidence):
    lp = CONT / "UNCERTAINTY_LEDGER_V1.json"
    led = json.loads(lp.read_text())
    for e in led["entries"]:
        if e["id"] == entry_id:
            e["status"] = status
            e["measured_value"] = value
            e["evidence"] = evidence
            e["measured_utc"] = datetime.now(timezone.utc).isoformat()
            break
    else:
        sys.exit(f"ledger entry not found: {entry_id}")
    lp.write_text(json.dumps(led, indent=1) + "\n")

# ---------------- handlers ----------------

def run_eps_curve(spec, args):
    bank = R.load_bank(args.bank)
    atoms = [a for a in R.load_bank(args.atoms) if a.get("kind") == "theorem"]
    tv = R.load_vocab(args.term_vocab)
    motif_index = R.build_motif_index(atoms, bank, tv)
    import random
    rows = []
    for eps in EPS_GRID:
        for a in atoms:
            for seed in spec.get("seeds", [0, 1, 2]):
                rng = random.Random(seed)
                log = []
                cost, receipts, found = R.route(
                    a, bank, tv, motif_index, eps,
                    spec.get("probe_share", 0.05), spec.get("budget", 1000), rng, log)
                rows.append({"experiment": "CONT-CAL-01", "eps": eps, "atom": a["atom"],
                             "seed": seed, "final_cost": cost,
                             "receipts": len(receipts), "donors_found": len(found),
                             "probe_share_used": round(R.probe_share_used(log, spec.get("budget", 1000)), 4),
                             "eps_share_used": round(R.eps_share_used(log, spec.get("budget", 1000)), 4)})
    curve = {}
    for eps in EPS_GRID:
        rs = [r for r in rows if r["eps"] == eps]
        curve[str(eps)] = {
            "mean_final_cost": round(sum(r["final_cost"] for r in rs) / len(rs), 1),
            "total_receipts": sum(r["receipts"] for r in rs),
            "total_donors_found": sum(r["donors_found"] for r in rs)}
    summary = {"experiment": "CONT-CAL-01", "quantity": spec["quantity"],
               "eps_grid": EPS_GRID, "atoms": len(atoms),
               "seeds": spec.get("seeds", [0, 1, 2]), "curve": curve}
    return rows, summary, ("MEASURED", curve)

def load_arm_log(arm):
    p = CONT.parent / "d12" / "arms" / f"{arm}_LOG.jsonl"
    lines = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    return [l for l in lines if l.get("type") == "action" and l.get("level")]

def run_halving_replay(spec, args):
    """Counterfactual replay: walk each (arm, atom, donor) rung sequence; a rung
    with score >= bar is a success. single = cut the pair after 1 failed rung;
    two_rung = cut after 2 consecutive. A pair's terminal synth/validate count
    as receipts only if the rule never cut before its deepest logged rung."""
    rows = []
    for arm in ARMS:
        acts = load_arm_log(arm)
        pairs = {}
        for l in acts:
            pairs.setdefault((l["atom"], l["donor"]), []).append(l)
        for rule, max_fail in (("two_rung", 2), ("single", 1)):
            cost, receipts = 0, 0
            for seq in pairs.values():
                fails = 0
                for i, l in enumerate(seq):
                    if i > 0 and l["level"] not in ("synth", "validate"):
                        fails = fails + 1 if l.get("score", 10) < PROMOTION_BAR else 0
                        if fails >= max_fail:
                            break
                    cost += l.get("cost", 0)
                    if l["level"] == "validate":
                        receipts += 1
            rows.append({"experiment": "CONT-CAL-02", "arm": arm, "rule": rule,
                         "replay_cost": cost, "replay_validations": receipts,
                         "promotion_bar_assumed": PROMOTION_BAR})
    deltas = {}
    for arm in ARMS:
        t = next(r for r in rows if r["arm"] == arm and r["rule"] == "two_rung")
        s = next(r for r in rows if r["arm"] == arm and r["rule"] == "single")
        deltas[arm] = {"cost_two_rung_minus_single": t["replay_cost"] - s["replay_cost"],
                       "validations_two_rung": t["replay_validations"],
                       "validations_single": s["replay_validations"]}
    summary = {"experiment": "CONT-CAL-02", "quantity": spec["quantity"],
               "per_arm_delta": deltas,
               "honest_scope": "counterfactual arithmetic on logged sequences; "
                               "does not re-run retrieval"}
    return rows, summary, ("MEASURED", deltas)

def run_inspection_pairs(spec, args):
    pairs = {}
    for arm in ARMS:
        for l in load_arm_log(arm):
            k = (arm, l["atom"], l["donor"])
            sc = l.get("score")
            sc = -1 if sc is None else sc
            if k not in pairs or sc > pairs[k]["score"]:
                pairs[k] = {"arm": arm, "atom": l["atom"], "donor": l["donor"],
                            "deepest_level": l["level"], "score": sc}
    rows = [p for p in pairs.values() if p["score"] >= PROMOTION_BAR]
    rows.sort(key=lambda p: -p["score"])
    rows = rows[:spec.get("n_pairs", 20)]
    for i, p in enumerate(rows):
        p["experiment"] = "CONT-CAL-03"
        p["pair_id"] = f"L3-{i:02d}"
        p["l4_verdict"] = None
    summary = {"experiment": "CONT-CAL-03", "quantity": spec["quantity"],
               "n_pairs": len(rows),
               "status": "PAIRS_READY_INSPECTION_PENDING",
               "honest_scope": "L4 purchase requires model-in-the-loop "
                               "inspection; not mechanizable in this runner"}
    return rows, summary, ("PAIRS_READY", {"n_pairs": len(rows)})

HANDLERS = {"CONT-CAL-01": run_eps_curve,
            "CONT-CAL-02": run_halving_replay,
            "CONT-CAL-03": run_inspection_pairs}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--bank", required=True)
    ap.add_argument("--atoms", required=True)
    ap.add_argument("--term-vocab", required=True)
    ap.add_argument("--update-ledger", action="store_true")
    a = ap.parse_args()
    spec = json.loads(Path(a.spec).read_text())
    verify_spec(spec)
    exp = spec["experiment"]
    rows, summary, (status, value) = HANDLERS[exp](spec, a)
    rf, sf = write_results(exp, rows, summary)
    if a.update_ledger:
        update_ledger(spec["entry_id"], status, value,
                      {"results": str(rf.relative_to(CONT)), "sha256": sha256f(rf),
                       "summary": str(sf.relative_to(CONT))})
    print(json.dumps({"experiment": exp, "rows": len(rows), "status": status,
                      "summary_file": str(sf)}, indent=1))

if __name__ == "__main__":
    main()
