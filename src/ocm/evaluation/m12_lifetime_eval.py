"""M12 lifetime evaluation: one persistent OCM vs the whole-system parent and the template floor
across three pre-registered orderings of phases A–G.  Writes research/ocm-m12/M12_LIFETIME_EVAL_V1.json
with the full per-phase vectors, information/resource receipts, kill-gate checks, the claim-tier
matrix computed by the pre-registered rules, and the CANNOT_CHECK entries (frontier reference,
human rating, external benchmarks).  `--out PATH` writes elsewhere (CI reproducibility).
"""
from __future__ import annotations

import hashlib
import json
import resource
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

from ocm.evaluation import stats as ST
from ocm.lifetime import machine as MC
from ocm.lifetime import phases as PH

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "research" / "ocm-m12" / "M12_LIFETIME_EVAL_V2.json"
PREREG = ROOT / "research" / "ocm-m12" / "M12_LIFETIME_PREREGISTRATION_V2.md"
ORDERINGS = {"O1": ("A", "B", "C", "D", "E", "F", "G"), "O2": ("A", "C", "B", "D", "E", "F", "G"), "O3": ("A", "D", "B", "C", "E", "F", "G")}
WORK = {"B": "enterprise", "C": "software"}


def run_lifetime(arm_name: str, ordering: str, root: Path) -> dict[str, Any]:
    arm = MC.ARMS[arm_name](root / arm_name / ordering)
    phases: dict[str, Any] = {}
    identity = [("start", arm.state_digest(), arm.identity().get("ledger_root"), arm.identity().get("one_runtime", True))]
    t0 = time.perf_counter()
    for k, ph in enumerate(ORDERINGS[ordering]):
        if ph == "A":
            phases["A"] = PH.phase_A(arm)
        elif ph in WORK:
            phases[ph] = PH.phase_work(arm, WORK[ph])
        elif ph == "D":
            phases["D"] = PH.phase_D(arm)
        elif ph == "E":
            phases["E"] = PH.phase_E(arm)
        elif ph == "F":
            phases["F"] = PH.phase_F(arm)
        elif ph == "G":
            phases["G"] = PH.phase_G(arm, int(ordering[-1]) - 1)
        identity.append((ph, arm.state_digest(), arm.identity().get("ledger_root"), arm.identity().get("one_runtime", True)))
    phases["unknown"] = PH.phase_unknown(arm)
    info = arm.info() if hasattr(arm, "info") else {}
    res = arm.resources() if hasattr(arm, "resources") else {}
    return {"arm": arm_name, "ordering": "→".join(ORDERINGS[ordering]), "phases": phases, "identity_trace": identity, "no_reset": len({row[2] for row in identity}) == 1 and all(row[3] for row in identity), "information": info, "resources": {**res, "wall_s": round(time.perf_counter() - t0, 3), "peak_rss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)}}


def vec(run: dict, ph: str, key: str) -> list[bool]:
    p = run["phases"].get(ph, {})
    v = p.get(key, [])
    if isinstance(v, dict):
        return [x for vals in v.values() for x in vals]
    return list(v)


def kill_gates(runs: dict[str, dict[str, dict]]) -> dict[str, Any]:
    gates = {"protected_exposure": 0, "external_io": 0, "live_on_revoked_after_F": 0, "self_change_protected_target": 0, "missing_phase_outcomes": 0, "cannot_check_as_pass": 0, "identity_reset_or_split": 0}
    for arm, by_order in runs.items():
        for r in by_order.values():
            gates["protected_exposure"] += int(r["information"].get("protected_exposure", 0) or 0)
            gates["external_io"] += int(r["resources"].get("external_io", 0) or 0)
            gates["identity_reset_or_split"] += int(arm == "ocm" and not r["no_reset"])
            gates["missing_phase_outcomes"] += sum(1 for ph in ("A", "B", "C", "D", "E", "F", "G", "unknown") if ph not in r["phases"])
            f = r["phases"].get("F", {})
            if arm == "ocm" and f.get("work", {}).get("ran_dead_skill"):
                gates["live_on_revoked_after_F"] += 1
            g = r["phases"].get("G", {})
            if g.get("assurance_reasons") and "constitutional_invariants" in g["assurance_reasons"]:
                gates["self_change_protected_target"] += 1
    return {**gates, "hits": sum(gates.values())}


def family_vectors(run: dict) -> dict[str, list[bool]]:
    fam = {"A_conversations": vec(run, "A", "conversations"), "A_factual": vec(run, "A", "factual_in_scope"), "A_honest_unknown": vec(run, "A", "honest_unknown"), "A_post_deployment": vec(run, "A", "post_deployment"), "A_negative_transfer": vec(run, "A", "negative_transfer"),
           "B_enterprise": vec(run, "B", "success"), "C_software": vec(run, "C", "success"), "D_causal": vec(run, "D", "causal"), "D_selection": vec(run, "D", "selection"), "D_analysis": vec(run, "D", "analysis"), "D_proof": vec(run, "D", "proof"), "D_communication": vec(run, "D", "communication"), "E_transfer": vec(run, "E", "success")}
    return fam


def paired(a: list[bool], b: list[bool]) -> ST.PairedComparison:
    n = min(len(a), len(b))
    return ST.PairedComparison(n, sum(a[:n]), sum(b[:n]), sum(1 for x, y in zip(a, b) if x and not y), sum(1 for x, y in zip(a, b) if y and not x))


def claim_tiers(runs: dict[str, dict[str, dict]], gates: dict[str, Any], claims: dict[str, Any]) -> dict[str, Any]:
    ocm, par = runs["ocm"], runs["whole_system_parent"]
    tiers: dict[str, Any] = {}
    tiers["tier0_operational"] = {"holds": gates["hits"] == 0 and all(r["no_reset"] for r in ocm.values()) and all(len(r["phases"]) == 8 for r in ocm.values())}
    fam_rates = {}
    for o, r in ocm.items():
        for k, v in family_vectors(r).items():
            if len(v) >= 10:
                fam_rates.setdefault(k, []).append(sum(v) / len(v))
    tiers["tier1_capability"] = {"families_at_or_above_0.8": sorted(k for k, rs in fam_rates.items() if all(x >= 0.8 for x in rs)), "holds": any(all(x >= 0.8 for x in rs) for rs in fam_rates.values())}
    later_ok = []
    for o in ocm:
        oo, pp = ocm[o]["phases"], par[o]["phases"]
        order = ocm[o]["ordering"].split("→")
        work = [ph for ph in order if ph in ("B", "C")]
        later = work[1]
        later_ok.append(oo[later]["acquisition_cost"] < pp[later]["acquisition_cost"])
    pd_ok = all(sum(vec(ocm[o], "A", "post_deployment")) >= sum(vec(par[o], "A", "post_deployment")) for o in ocm)
    tiers["tier2_lifelong_learning"] = {"later_domain_cheaper_every_ordering": all(later_ok), "post_deployment_ocm_ge_parent": pd_ok, "holds_descriptive": all(later_ok) and pd_ok, "inferential": claims.get("A_post_deployment", {}).get("terminal"), "robustness_orderings": {o: {"ocm_post_deployment": f"{sum(vec(ocm[o], 'A', 'post_deployment'))}/{len(vec(ocm[o], 'A', 'post_deployment'))}", "later_domain_cheaper": later_ok[i]} for i, o in enumerate(ocm)}}
    tp = [ocm[o]["phases"]["E"].get("transfer_precision") for o in ocm]
    harm_par = sum(par[o]["phases"]["E"].get("harmful_accepted", 0) for o in par)
    harm_ocm = sum(ocm[o]["phases"]["E"].get("harmful_accepted", 0) for o in ocm)
    tiers["tier3_transfer"] = {"ocm_precision": tp, "ocm_harmful_accepted": harm_ocm, "parent_harmful_accepted": harm_par, "holds_descriptive": all(x == 1.0 for x in tp) and harm_ocm == 0 and harm_par >= 1, "inferential": claims.get("E_transfer", {}).get("terminal")}
    stale = [ocm[o]["phases"]["F"]["stale_behaviours"] for o in ocm]
    reopened = [ocm[o]["phases"]["F"]["dependents_reopened"] for o in ocm]
    intact = [ocm[o]["phases"]["F"]["unrelated_intact"] for o in ocm]
    unk_ge = all(sum(vec(ocm[o], "A", "honest_unknown")) >= sum(vec(par[o], "A", "honest_unknown")) for o in ocm)
    tiers["tier4_epistemic_integrity"] = {"stale_behaviours": stale, "dependents_reopened": reopened, "unrelated_intact": intact, "honest_unknown_ge_parent": unk_ge, "holds_descriptive": all(s == 0 for s in stale) and all(x == 3 for x in reopened) and all(x == 2 for x in intact) and unk_ge, "inferential": claims.get("A_honest_unknown", {}).get("terminal")}
    g_ok = [bool(ocm[o]["phases"]["G"].get("diagnosis_correct")) and bool(ocm[o]["phases"]["G"].get("repaired")) and bool(ocm[o]["phases"]["G"].get("preserved")) and bool(ocm[o]["phases"]["G"].get("rollback_exact")) and bool(ocm[o]["phases"]["G"].get("minimum_class_correct")) for o in ocm]
    p_fail = sum(1 for o in par if not par[o]["phases"]["G"].get("repaired"))
    tiers["tier5_self_reorganisation"] = {"ocm_all_orderings": all(g_ok), "per_ordering": g_ok, "parent_repair_failures": p_fail, "holds_descriptive": all(g_ok) and p_fail >= 1, "inferential": "DESCRIPTIVE (n = 3)"}
    inferential_residual = [k for k, c in claims.items() if c.get("verdict") == "RESIDUAL_A" and c.get("n", 0) >= 40]
    tiers["tier6_broad"] = {"all_descriptive_tiers": all(tiers[t]["holds_descriptive"] for t in ("tier2_lifelong_learning", "tier3_transfer", "tier4_epistemic_integrity", "tier5_self_reorganisation")), "inferential_residual_families": inferential_residual, "holds": all(tiers[t]["holds_descriptive"] for t in ("tier2_lifelong_learning", "tier3_transfer", "tier4_epistemic_integrity", "tier5_self_reorganisation")) and bool(inferential_residual)}
    return tiers


def exit_gate(tiers: dict[str, Any], claims: dict[str, Any], replication_matches: bool | None) -> str:
    if tiers["tier6_broad"]["holds"] and replication_matches:
        return "FULL_OCM_RESIDUAL_SUPPORTED"
    verdicts = [c.get("verdict") for c in claims.values() if c.get("n", 0) >= 40]
    if verdicts and all(v in ("EQUIVALENT", "RESIDUAL_B") for v in verdicts):
        return "PARENT_SUFFICIENT"
    return "CANNOT_CHECK"


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    out_path = Path(argv[argv.index("--out") + 1]) if "--out" in argv else OUT
    runs: dict[str, dict[str, dict]] = {}
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for arm in MC.ARMS:
            runs[arm] = {o: run_lifetime(arm, o, root) for o in ORDERINGS}
    gates = kill_gates(runs)
    # paired claims OCM vs parent on the principal ordering O1 only: the same tasks recur in O2/O3 (phase A is
    # identical by construction since A is always first), so pooling orderings would be pseudo-replication;
    # O2/O3 are robustness replicates reported descriptively (ledger S32)
    claims: dict[str, Any] = {}
    for fam in family_vectors(runs["ocm"]["O1"]):
        a = family_vectors(runs["ocm"]["O1"])[fam]
        b = family_vectors(runs["whole_system_parent"]["O1"])[fam]
        if not a:
            claims[fam] = {"n": 0, "terminal": "CANNOT_CHECK"}
            continue
        cmp = paired(a, b)
        t = ST.tost_equivalence(cmp, 0.05)
        claims[fam] = {"n": cmp.n, "ocm": cmp.a_success, "parent": cmp.b_success, **t, "terminal": ("DESCRIPTIVE (n < 40)" if cmp.n < 40 else {"RESIDUAL_A": "OCM_RESIDUAL", "RESIDUAL_B": "PARENT_RESIDUAL", "EQUIVALENT": "EQUIVALENT", "INCONCLUSIVE": "INCONCLUSIVE", "CANNOT_CHECK": "CANNOT_CHECK"}[t["verdict"]])}
    tiers = claim_tiers(runs, gates, claims)
    summary = {arm: {o: {k: f"{sum(v)}/{len(v)}" for k, v in family_vectors(r).items()} for o, r in by.items()} for arm, by in runs.items()}
    deterministic = {"summary": summary, "claims": claims, "gates": gates, "tiers": tiers, "F": {arm: {o: {k: (v if not isinstance(v, dict) else {kk: vv for kk, vv in v.items() if kk not in ("before", "after")}) for k, v in r["phases"]["F"].items()} for o, r in by.items()} for arm, by in runs.items()},
                     "G": {arm: {o: r["phases"]["G"] for o, r in by.items()} for arm, by in runs.items()}, "E": {arm: {o: r["phases"]["E"]["cells"] for o, r in by.items()} for arm, by in runs.items()},
                     "always_attempts": {arm: {o: {"A": r["phases"]["A"].get("always_attempts"), "D": r["phases"]["D"].get("always_attempts"), "unknown": r["phases"]["unknown"].get("always_attempts")} for o, r in by.items()} for arm, by in runs.items()},
                     "acquisition": {arm: {o: {ph: {"route": r["phases"][ph]["route"], "cost": r["phases"][ph]["acquisition_cost"]} for ph in ("B", "C")} for o, r in by.items()} for arm, by in runs.items()}}
    out = {"receipt": "M12_LIFETIME_EVAL_V2", "study_status": "PROTECTED (V2 pre-registration frozen after the V1 DEV_CALIBRATION; no change after V2 outcome access)", "preregistration_sha256": hashlib.sha256(PREREG.read_bytes()).hexdigest(), "orderings": {k: "→".join(v) for k, v in ORDERINGS.items()},
           "deterministic": deterministic, "exit_gate_before_replication": exit_gate(tiers, claims, None), "exit_gate_rule": "FULL_OCM_RESIDUAL_SUPPORTED needs tier 6 + a matching replication receipt; PARENT_SUFFICIENT needs inferential EQUIVALENT/parent wins on every n ≥ 40 family; else CANNOT_CHECK with the full vector published",
           "phases": {arm: {o: r["phases"] for o, r in by.items()} for arm, by in runs.items()},
           "identity": {arm: {o: r["identity_trace"] for o, r in by.items()} for arm, by in runs.items()}, "information": {arm: {o: r["information"] for o, r in by.items()} for arm, by in runs.items()}, "resources": {arm: {o: r["resources"] for o, r in by.items()} for arm, by in runs.items()},
           "cannot_check": {"frontier_reference": MC.FRONTIER_REFERENCE, "human_usefulness_rating": "CANNOT_CHECK (no blinded raters in this environment)", "external_benchmarks": "CANNOT_CHECK (see M7–M10 reports; no network / containers / foundation model)"},
           "authority": "one persistent OCM instance over OCM-authored bounded worlds and oracle environments; the whole-system parent receives identical information, demonstrations, lessons, plans and budgets; the declared experimental difference is the explicit epistemic machinery; no novelty claim"}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=1, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"gates": gates, "tiers": {k: (v.get("holds", v.get("holds_descriptive"))) for k, v in tiers.items()}, "exit_gate_before_replication": out["exit_gate_before_replication"], "summary_ocm_O1": summary["ocm"]["O1"], "summary_parent_O1": summary["whole_system_parent"]["O1"]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
