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
from ocm.evaluation.m12_lifetime_eval import ORDERINGS, WORK, family_vectors, paired, vec
from ocm.lifetime import machine as MC
from ocm.lifetime import phases as PH
from ocm.lifetime import streams as SR

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "research" / "ocm-m12" / "M12_PAIRED_LIFETIMES_EVAL_V1.json"
MANIFEST = ROOT / "research" / "ocm-m12" / "M12_V3_STREAM_MANIFEST_V1.json"
PREREG = ROOT / "research" / "ocm-m12" / "M12_LIFETIME_PREREGISTRATION_V3.md"
N_LIFETIMES = 8


def run_lifetime(arm_name: str, stream: dict[str, Any], root: Path) -> dict[str, Any]:
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
            phases["E"] = PH.phase_E(arm)
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


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--manifest-only" in argv:
        man = SR.stream_manifest(N_LIFETIMES)
        leaks = [SR.leak_check(SR.build_stream(k)) for k in range(N_LIFETIMES)]
        man["leak_checks"] = leaks
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps(man, indent=1, default=str) + "\n", encoding="utf-8")
        print(json.dumps({"manifest_sha256": man["sha256"], "leaks_ok": all(l["ok"] for l in leaks)}))
        return 0
    out_path = Path(argv[argv.index("--out") + 1]) if "--out" in argv else OUT
    man = SR.stream_manifest(N_LIFETIMES)
    runs: dict[str, list[dict]] = {"ocm": [], "whole_system_parent": []}
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for k in range(N_LIFETIMES):
            stream = SR.build_stream(k)
            assert stream["sha256"] == man["streams"][k]["sha256"]
            for arm in runs:
                runs[arm].append(run_lifetime(arm, stream, root))
    scores = {arm: [lifetime_scores(r) for r in rs] for arm, rs in runs.items()}
    fams = list(scores["ocm"][0])
    tests = {}
    for fam in fams:
        diffs = [(a[fam] or 0) - (b[fam] or 0) for a, b in zip(scores["ocm"], scores["whole_system_parent"]) if a[fam] is not None and b[fam] is not None]
        tests[fam] = {"ocm_mean": round(sum((a[fam] or 0) for a in scores["ocm"]) / N_LIFETIMES, 4), "parent_mean": round(sum((b[fam] or 0) for b in scores["whole_system_parent"]) / N_LIFETIMES, 4), "diffs": [round(d, 4) for d in diffs], **sign_test(diffs)}
    within = {fam: [{"lifetime": k, **{kk: vv for kk, vv in ST.tost_equivalence(paired(family_vectors(runs["ocm"][k])[fam], family_vectors(runs["whole_system_parent"][k])[fam]), 0.05).items() if kk in ("verdict", "p_mcnemar", "n")}} for k in range(N_LIFETIMES) if family_vectors(runs["ocm"][k])[fam]] for fam in family_vectors(runs["ocm"][0])}
    gates = {"identity_chain_broken": sum(1 for r in runs["ocm"] if not r["chain_continuous"]), "protected_exposure": sum(int(r["information"].get("protected_exposure", 0) or 0) for rs in runs.values() for r in rs), "external_io": sum(int(r["resources"].get("external_io", 0) or 0) for rs in runs.values() for r in rs),
             "live_on_revoked_after_F": sum(1 for r in runs["ocm"] if r["phases"]["F"].get("work", {}).get("ran_dead_skill")), "missing_phase_outcomes": sum(1 for rs in runs.values() for r in rs if len(r["phases"]) != 8), "stream_leaks": sum(1 for k in range(N_LIFETIMES) if not SR.leak_check(SR.build_stream(k))["ok"])}
    gates["hits"] = sum(gates.values())
    residual = [f for f, t in tests.items() if t["verdict"] == "OCM_RESIDUAL"]
    parent_wins = [f for f, t in tests.items() if t["verdict"] == "PARENT_RESIDUAL"]
    decision = "CANNOT_CHECK" if gates["hits"] else ("OCM_LIFETIME_RESIDUAL_SUPPORTED" if residual and not parent_wins else ("PARENT_SUFFICIENT" if not residual else "MIXED"))
    deterministic = {"tests": tests, "within_lifetime": within, "gates": gates, "decision": decision, "scores": scores, "orderings": [r["ordering"] for r in runs["ocm"]], "G": [r["phases"]["G"] for r in runs["ocm"]], "F": [{k: v for k, v in r["phases"]["F"].items() if k != "knowledge"} for r in runs["ocm"]]}
    out = {"receipt": "M12_PAIRED_LIFETIMES_EVAL_V1", "study_status": "PROTECTED (V3 pre-registration frozen with the stream-manifest hash before this run)", "preregistration_sha256": hashlib.sha256(PREREG.read_bytes()).hexdigest() if PREREG.exists() else None, "stream_manifest_sha256": man["sha256"], "lifetimes": N_LIFETIMES,
           "deterministic": deterministic, "phases": {arm: [r["phases"] for r in rs] for arm, rs in runs.items()}, "chains": [r["chain"] for r in runs["ocm"]], "information": {arm: [r["information"] for r in rs] for arm, rs in runs.items()}, "resources": {arm: [r["resources"] for r in rs] for arm, rs in runs.items()},
           "rule": "primary: exact sign test over 8 lifetime differences per family (α = 0.05, ties dropped); OCM_LIFETIME_RESIDUAL_SUPPORTED iff ≥ 1 family rejects in OCM's favour, none in the parent's, and kill gates are 0; PARENT_SUFFICIENT iff no family rejects; the reference arm is reported separately and never enters this decision (F8)",
           "authority": "eight paired lifetimes on OCM-authored per-lifetime protected streams inside the bounded world; matched whole-system parent; no novelty claim"}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=1, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"decision": decision, "gates": gates, "tests": {f: (t["ocm_mean"], t["parent_mean"], t["positive"], t["n_nonzero"], t["p_two_sided"], t["verdict"]) for f, t in tests.items()}}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
