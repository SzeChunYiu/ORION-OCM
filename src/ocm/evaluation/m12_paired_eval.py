"""M12 V3: eight paired lifetimes (OCM vs whole-system parent) on per-lifetime protected streams.

The unit of inference is the lifetime (theory batch 6 F2).  For every family the per-lifetime
score is the success rate inside that lifetime; the primary test is the exact sign test over the
eight lifetime differences (ties dropped), the secondary statistic is the exact paired test inside
each lifetime (reported per lifetime, never pooled).  Kill gates: the V2 gates plus the ledger-chain
identity gate (F5) at every phase boundary.  `--manifest-only` writes the stream manifest (no
outcome is read) so the pre-registration can bind its hash before the run.
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import time
from fractions import Fraction
from pathlib import Path
from typing import Any

from ocm.evaluation import stats as ST
from ocm.evaluation.m12_lifetime_eval import ORDERINGS, WORK, family_vectors, paired_family, vec
from ocm.evaluation.output import new_output_path, write_result
from ocm.lifetime import machine as MC
from ocm.lifetime import phases as PH
from ocm.lifetime import streams as SR

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "research" / "ocm-m12" / "M12_PAIRED_LIFETIMES_EVAL_V1.json"
MANIFEST = ROOT / "research" / "ocm-m12" / "M12_V3_STREAM_MANIFEST_V1.json"
PREREG = ROOT / "research" / "ocm-m12" / "M12_LIFETIME_PREREGISTRATION_V3.md"
N_LIFETIMES = 8

# V4 (theory batch 7 G8): fresh streams, a pre-registered PRIMARY family, ≤ 6 secondary families with
# Bonferroni, the one-sided ≥ 7/8 sign rule (size 9/256, power 0.81 at p = 0.9), a collapsed-one-coin
# flag, and the world-true out-of-scope half (G7).
V4 = {"seed": "OCM-M12-V4", "out": ROOT / "research" / "ocm-m12" / "M12_PAIRED_LIFETIMES_EVAL_V4.json", "manifest": ROOT / "research" / "ocm-m12" / "M12_V4_STREAM_MANIFEST_V1.json", "prereg": ROOT / "research" / "ocm-m12" / "M12_LIFETIME_PREREGISTRATION_V4.md",
      "primary": "A_conversations", "secondary": ("A_post_deployment", "A_honest_unknown", "D_causal", "E_transfer", "F_integrity", "G_self_repair"), "alpha": 0.05}

# V5 (issue #38 M12 gates; ledger S37/S38; V4 one-coin finding): fresh never-exposed streams on the CURRENT
# runtime, prospectively matched transfer cells (phase_E matched_cells), the world-true out-of-scope half,
# the same primary family and one-sided ≥ 7/8 rule, THREE inferential secondary families at α/3 (the
# families whose per-lifetime differences are not a deterministic function of the planted design), and the
# three categorical families (transfer, revision integrity, self-repair) pre-registered as CATEGORICAL:
# reported per lifetime as win/tie/loss, never tested.  A V5 run is a protected pre-registered study only
# when the pre-registration file is present, the stream manifest is regenerated identically and no gate
# hits; the decision is then NOT relabelled (unlike replays of exposed streams).
V5 = {"seed": "OCM-M12-V5", "out": ROOT / "research" / "ocm-m12" / "M12_PAIRED_LIFETIMES_EVAL_V5.json", "manifest": ROOT / "research" / "ocm-m12" / "M12_V5_STREAM_MANIFEST_V1.json", "prereg": ROOT / "research" / "ocm-m12" / "M12_LIFETIME_PREREGISTRATION_V5.md",
      "primary": "A_conversations", "secondary": ("A_post_deployment", "A_honest_unknown", "D_causal"), "categorical": ("E_transfer", "F_integrity", "G_self_repair"), "alpha": 0.05}


def run_lifetime(arm_name: str, stream: dict[str, Any], root: Path, *, matched_cells: bool = False) -> dict[str, Any]:
    k = stream["lifetime"]
    arm = MC.ARMS[arm_name](root / arm_name / f"L{k}")
    order = ORDERINGS[stream["ordering"]]
    phases: dict[str, Any] = {}
    chain = [("start", MC.identity_chain(arm.s.runtime) if isinstance(arm, MC.PersistentOCM) else None)]
    continuous = True
    t0 = time.perf_counter()
    for ph in order:
        if ph == "A":
            phases["A"] = PH.phase_A_stream(arm, stream)
        elif ph in WORK:
            phases[ph] = PH.phase_work(arm, WORK[ph], task_ids=stream["work_task_ids"], withheld_ids=stream["work_withheld_ids"])
        elif ph == "D":
            phases["D"] = PH.phase_D(arm, dataset_ids=stream["science_dataset_ids"])
        elif ph == "E":
            phases["E"] = PH.phase_E(arm, matched_cells=matched_cells) if matched_cells else PH.phase_E(arm)
        elif ph == "F":
            phases["F"] = PH.phase_F(arm)
        elif ph == "G":
            phases["G"] = PH.phase_G(arm, k)
        if isinstance(arm, MC.PersistentOCM):
            prev = chain[-1][1]
            continuous = continuous and MC.chain_continuous(prev, arm.s.runtime)
            chain.append((ph, MC.identity_chain(arm.s.runtime)))
    phases["unknown"] = PH.phase_unknown(arm)
    info = arm.info() if hasattr(arm, "info") else {}
    res = arm.resources() if hasattr(arm, "resources") else {}
    return {"arm": arm_name, "lifetime": k, "ordering": "→".join(order), "stream_sha256": stream["sha256"], "phases": phases, "chain_continuous": continuous, "chain": chain, "no_reset": continuous, "information": info, "resources": {**res, "wall_s": round(time.perf_counter() - t0, 3)}}


def lifetime_scores(run: dict) -> dict[str, float | None]:
    out = {}
    for fam, v in family_vectors(run).items():
        out[fam] = (sum(v) / len(v)) if v else None
    f = run["phases"]["F"]
    out["F_integrity"] = 1.0 if f["stale_behaviours"] == 0 and f["dependents_reopened"] == 3 and f["unrelated_intact"] == 2 else 0.0
    g = run["phases"]["G"]
    out["G_self_repair"] = 1.0 if g.get("repaired") and g.get("preserved") and g.get("rollback_exact", True) else 0.0
    out["unknown_no_action"] = 1.0 if run["phases"]["unknown"]["unregistered_domain_no_action"] else 0.0
    return out


def sign_test(diffs: list[float]) -> dict[str, Any]:
    nz = [d for d in diffs if d != 0]
    pos = sum(1 for d in nz if d > 0)
    if not nz:
        return {"n_nonzero": 0, "positive": 0, "p_two_sided": 1.0, "verdict": "TIES_ONLY"}
    p = float(ST.exact_binomial_two_sided(pos, len(nz), Fraction(1, 2)))
    return {"n_nonzero": len(nz), "positive": pos, "p_two_sided": round(p, 5), "verdict": ("OCM_RESIDUAL" if pos == len(nz) and p <= 0.05 else "PARENT_RESIDUAL" if pos == 0 and p <= 0.05 else "INCONCLUSIVE")}


def sign_test_one_sided(diffs: list[float], alpha: float) -> dict[str, Any]:
    """Batch 7 G8: one-sided exact sign test (H1: OCM > parent) at level alpha; ties dropped; the
    collapsed-one-coin flag marks families whose eight differences are identical (shared variation
    may reduce them to one coin: reported, never counted as independent evidence on its own)."""
    nz = [d for d in diffs if d != 0]
    pos = sum(1 for d in nz if d > 0)
    collapsed = len(set(round(d, 6) for d in diffs)) == 1 and len(diffs) > 1
    if not nz:
        return {"n_nonzero": 0, "positive": 0, "p_one_sided": 1.0, "collapsed_one_coin": collapsed, "verdict": "TIES_ONLY"}
    n = len(nz)
    p = float(1 - ST.binom_cdf(pos - 1, n, Fraction(1, 2))) if pos > 0 else 1.0
    return {"n_nonzero": n, "positive": pos, "p_one_sided": round(p, 5), "collapsed_one_coin": collapsed, "verdict": ("OCM_RESIDUAL" if p <= alpha else "INCONCLUSIVE")}


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    v5 = "--v5" in argv
    v4 = "--v4" in argv or v5          # V5 inherits the V4 rule shape (primary + Bonferroni secondaries + one-coin flag)
    cfg = V5 if v5 else V4
    manifest_only = "--manifest-only" in argv
    out_path = new_output_path([a for a in argv if a not in ("--v4", "--v5", "--manifest-only")],
        "Current engineering replay on historically exposed streams; new output required" if not v5 else "V5 protected study: the result path is written once; a second run needs a new output path")
    seed = cfg["seed"] if v4 else "OCM-M12-V3"
    manifest_path, prereg_path, out_default = (cfg["manifest"], cfg["prereg"], cfg["out"]) if v4 else (MANIFEST, PREREG, OUT)
    man_name = "M12_V5_STREAM_MANIFEST_V1" if v5 else ("M12_V4_STREAM_MANIFEST_V1" if v4 else "M12_V3_STREAM_MANIFEST_V1")
    build = lambda k: SR.build_stream(k, seed=seed, world_true_half=v4)  # noqa: E731
    if manifest_only:
        man = SR.stream_manifest(N_LIFETIMES, seed=seed, world_true_half=v4, name=man_name)
        leaks = [SR.leak_check(build(k)) for k in range(N_LIFETIMES)]
        man["leak_checks"] = leaks
        write_result(out_path, man)
        print(json.dumps({"manifest_sha256": man["sha256"], "leaks_ok": all(l["ok"] for l in leaks)}))
        return 0
    man = SR.stream_manifest(N_LIFETIMES, seed=seed, world_true_half=v4, name=man_name)
    frozen_manifest_ok = manifest_path.exists() and json.loads(manifest_path.read_text(encoding="utf-8")).get("sha256") == man["sha256"]
    if v5 and not (frozen_manifest_ok and prereg_path.exists()):
        raise SystemExit("V5 requires the frozen stream manifest and the pre-registration file before any outcome is read")
    runs: dict[str, list[dict]] = {"ocm": [], "whole_system_parent": []}
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for k in range(N_LIFETIMES):
            stream = build(k)
            if stream["sha256"] != man["streams"][k]["sha256"]:
                raise ValueError("stream identity mismatch")
            for arm in runs:
                runs[arm].append(run_lifetime(arm, stream, root, matched_cells=v5))
    scores = {arm: [lifetime_scores(r) for r in rs] for arm, rs in runs.items()}
    fams = list(scores["ocm"][0])
    tests = {}
    for fam in fams:
        diffs = [(a[fam] or 0) - (b[fam] or 0) for a, b in zip(scores["ocm"], scores["whole_system_parent"]) if a[fam] is not None and b[fam] is not None]
        base = {"ocm_mean": round(sum((a[fam] or 0) for a in scores["ocm"]) / N_LIFETIMES, 4), "parent_mean": round(sum((b[fam] or 0) for b in scores["whole_system_parent"]) / N_LIFETIMES, 4), "diffs": [round(d, 4) for d in diffs]}
        if v4:
            role = "primary" if fam == cfg["primary"] else ("secondary" if fam in cfg["secondary"] else ("categorical" if fam in cfg.get("categorical", ()) else "descriptive"))
            alpha = cfg["alpha"] if role == "primary" else (cfg["alpha"] / len(cfg["secondary"]) if role == "secondary" else None)
            st = sign_test_one_sided(diffs, alpha if alpha is not None else cfg["alpha"])
            if role == "descriptive":
                st["verdict"] = "DESCRIPTIVE (not pre-registered)"
            if role == "categorical":
                wins = sum(1 for d in diffs if d > 0); losses = sum(1 for d in diffs if d < 0)
                st = {"n_nonzero": len([d for d in diffs if d != 0]), "positive": wins, "p_one_sided": None, "collapsed_one_coin": st["collapsed_one_coin"],
                      "verdict": "CATEGORICAL (pre-registered descriptive)", "wins": wins, "ties": len(diffs) - wins - losses, "losses": losses}
            tests[fam] = {**base, "role": role, "alpha": alpha, **st}
        else:
            tests[fam] = {**base, **sign_test(diffs)}
    within = {}
    for fam in family_vectors(runs["ocm"][0]):
        within[fam] = []
        for k in range(N_LIFETIMES):
            try:
                pair = paired_family(runs["ocm"][k], runs["whole_system_parent"][k], fam)
                row = {kk: vv for kk, vv in ST.tost_equivalence(pair, 0.05).items() if kk in ("verdict", "p_mcnemar", "n")}
            except ValueError as exc:
                row = {"verdict": "CANNOT_CHECK", "reason": str(exc)}
            within[fam].append({"lifetime": k, **row})
        if any(row["verdict"] == "CANNOT_CHECK" for row in within[fam]):
            tests[fam]["verdict"] = "CANNOT_CHECK_MATCHED_CASES"
    gates = {"identity_chain_broken": sum(1 for r in runs["ocm"] if not r["chain_continuous"]), "protected_exposure": sum(int(r["information"].get("protected_exposure", 0) or 0) for rs in runs.values() for r in rs), "external_io": sum(int(r["resources"].get("external_io", 0) or 0) for rs in runs.values() for r in rs),
             "live_on_revoked_after_F": sum(1 for r in runs["ocm"] if r["phases"]["F"].get("work", {}).get("ran_dead_skill")), "missing_phase_outcomes": sum(1 for rs in runs.values() for r in rs if len(r["phases"]) != 8), "stream_leaks": sum(1 for k in range(N_LIFETIMES) if not SR.leak_check(build(k))["ok"])}
    if v5:
        gates["adoption_predecessors_unbound"] = sum(1 for r in runs["ocm"] if r["information"].get("adoption_predecessors_bound") is False)
        gates["frozen_manifest_mismatch"] = 0 if frozen_manifest_ok else 1
    gates["hits"] = sum(gates.values())
    if v4:
        primary = tests[cfg["primary"]]
        secondaries = [f for f in cfg["secondary"] if tests[f]["verdict"] == "OCM_RESIDUAL"]
        decision = "CANNOT_CHECK" if gates["hits"] else ("OCM_LIFETIME_RESIDUAL_SUPPORTED" if primary["verdict"] == "OCM_RESIDUAL" else ("PARENT_SUFFICIENT" if primary["verdict"] == "TIES_ONLY" and not secondaries else "INCONCLUSIVE"))
        rule = ("V5: primary family A_conversations, one-sided exact sign test over 8 lifetime differences at α = 0.05 (rejects iff ≥ 7/8 positive, size 9/256); three pre-registered inferential secondary families (post-deployment lessons, honest unknown incl. the world-true half, causal identification) at α/3 (reject iff 8/8); transfer (prospectively matched cells), revision integrity and self-repair are CATEGORICAL, reported per lifetime and never tested; every other family descriptive; collapsed-one-coin flagged; kill gates include the identity chain and adoption predecessor binding; the reference arm never enters the decision (F8)" if v5 else
                "V4: primary family A_conversations, one-sided exact sign test over 8 lifetime differences at α = 0.05 (rejects iff ≥ 7/8 positive, size 9/256); six pre-registered secondary families at α/6 (reject iff 8/8); every other family descriptive; collapsed-one-coin flagged; the reference arm never enters the decision (F8)")
    else:
        residual = [f for f, t_ in tests.items() if t_["verdict"] == "OCM_RESIDUAL"]
        parent_wins = [f for f, t_ in tests.items() if t_["verdict"] == "PARENT_RESIDUAL"]
        decision = "CANNOT_CHECK" if gates["hits"] else ("OCM_LIFETIME_RESIDUAL_SUPPORTED" if residual and not parent_wins else ("PARENT_SUFFICIENT" if not residual else "MIXED"))
        rule = "primary: exact sign test over 8 lifetime differences per family (α = 0.05, ties dropped); OCM_LIFETIME_RESIDUAL_SUPPORTED iff ≥ 1 family rejects in OCM's favour, none in the parent's, and kill gates are 0; PARENT_SUFFICIENT iff no family rejects; the reference arm is reported separately and never enters this decision (F8)"
    deterministic = {"tests": tests, "within_lifetime": within, "gates": gates, "decision": decision, "scores": scores, "orderings": [r["ordering"] for r in runs["ocm"]], "G": [r["phases"]["G"] for r in runs["ocm"]], "F": [{k: v for k, v in r["phases"]["F"].items() if k != "knowledge"} for r in runs["ocm"]]}
    if v4:
        deterministic["secondary_rejections"] = secondaries
        deterministic["collapsed_one_coin_families"] = [f for f, t_ in tests.items() if t_.get("collapsed_one_coin")]
    if v5:
        deterministic["categorical_families"] = {f: {k_: tests[f][k_] for k_ in ("wins", "ties", "losses", "collapsed_one_coin")} for f in cfg["categorical"]}
        receipt_name, study_status = "M12_PAIRED_LIFETIMES_V5", "PROTECTED_PREREGISTERED_V5__FRESH_STREAMS_CURRENT_RUNTIME"
    else:
        deterministic["historical_rule_diagnostic"] = deterministic["decision"]
        deterministic["decision"] = "CANNOT_CHECK_CURRENT_SCIENTIFIC_PROMOTION"
        receipt_name, study_status = "M12_PAIRED_LIFETIMES_ENGINEERING_REPLAY", "ENGINEERING_REGRESSION_ONLY__AFTER_OUTCOME_ACCESS"
    out = {"receipt": receipt_name, "study_status": study_status, "preregistration_sha256": hashlib.sha256(prereg_path.read_bytes()).hexdigest() if prereg_path.exists() else None, "stream_manifest_sha256": man["sha256"], "lifetimes": N_LIFETIMES,
           "deterministic": deterministic, "phases": {arm: [r["phases"] for r in rs] for arm, rs in runs.items()}, "chains": [r["chain"] for r in runs["ocm"]], "information": {arm: [r["information"] for r in rs] for arm, rs in runs.items()}, "resources": {arm: [r["resources"] for r in rs] for arm, rs in runs.items()},
           "rule": rule, "authority": "eight paired lifetimes on OCM-authored per-lifetime protected streams inside the bounded world; matched whole-system parent; no novelty claim"}
    write_result(out_path, out)
    print(json.dumps({"decision": deterministic["decision"], "study_status": study_status, "gates": gates, "tests": {f: (t_["ocm_mean"], t_["parent_mean"], t_["positive"], t_["n_nonzero"], t_.get("p_one_sided", t_.get("p_two_sided")), t_["verdict"]) for f, t_ in tests.items()}}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
