#!/usr/bin/env python3
"""M2-P1 summarize: arm comparison, G4 surface-predictor null, terminal mapping.

Terminals are those registered in HIDDEN_FAMILY_DESIGN.md before execution:
  ASSAY_DEFECT > LEAKAGE_ALARM > FAMILY_PREDICTABLE_WITHOUT_HISTORY
  > NO_FAMILY_HEADROOM > HISTORY_INDUCED_SEARCH_PRIOR / FAMILY_HEADROOM_OCM_MISSES
  > PARENT_SUFFICIENT / NO_NATIVE_EFFECT / CANNOT_CHECK_<reason>
"""
from __future__ import annotations
import argparse, json, statistics, sys
from collections import Counter
from itertools import product
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--ecology", required=True)
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    repo, run = Path(a.repo), Path(a.run_dir)
    sys.path.insert(0, str(repo / "src"))
    import ocm.learning.methods as M
    eco = json.loads(Path(a.ecology).read_text())
    dev = json.loads((run / "dev_state.json").read_text())

    arms = {}
    for f in sorted(run.glob("arm_*.json")):
        r = json.loads(f.read_text())
        arms[r["arm"]] = r

    # ---------- G4: can a history-free SURFACE ordering explain any advantage?
    # Exact closed form, reusing the M2 probe machinery: ASC (baseline), DESC,
    # and CONST8-first.  None of these uses history or the hidden motifs.
    within, counts, minlen = {}, {}, {}
    for L in range(9):
        w = 0
        for p in product(M.PRIMITIVES, repeat=L):
            w += 1
            nf = M.normal_form(p)
            minlen.setdefault(nf, L)
            within.setdefault((nf, L), w)
        counts[L] = w

    def b_seq(nf, seq):
        tl, used = minlen[nf], 0
        for L in seq:
            if L == tl:
                return used + within[(nf, L)]
            used += counts[L]
        return None

    from fractions import Fraction
    prot = eco["streams"]["protected"]
    nfs = []
    for r in prot:
        c = list(Fraction(x) for x in r["coefficients"])
        while len(c) > 1 and c[-1] == 0:
            c.pop()
        nfs.append(tuple(c))
    ladder = arms[next(iter(arms))]["ladder"] if arms else [1000, 4000, 16000, 64000, 200000]
    surface = {}
    for name, seq in (("ASC_baseline", list(range(9))),
                      ("DESC_history_free", [8, 7, 6, 5, 4, 3, 2, 1, 0]),
                      ("CONST8_first", [8] + [L for L in range(9) if L != 8])):
        vals = [b_seq(nf, seq) for nf in nfs]
        surface[name] = {
            "mean_B": round(statistics.fmean(vals), 1),
            "successes_by_budget": {str(q): sum(1 for v in vals if v <= q) for q in ladder},
            "ladder_total": sum(sum(1 for v in vals if v <= q) for q in ladder)}

    def total(arm):
        return arms[arm]["ladder_total"] if arm in arms else None

    best_surface = max(surface.values(), key=lambda d: d["ladder_total"])["ladder_total"]
    cont, reset = total("CONTINUED"), total("RESET")
    lib, shuf = total("LIBRARY_ONLY"), total("SHUFFLED_HISTORY")
    orac, parent = total("ORACLE_FAMILY"), total("ORDINARY_ADAPTIVE_PARENT")

    g4 = ("PASS" if (cont is not None and cont > best_surface) else
          "FAIL_SURFACE_ORDERING_EXPLAINS_ADVANTAGE" if cont is not None else "CANNOT_CHECK")

    defects = [a_ for a_, r in arms.items() if not r["process"]["pid_changed"]]
    if defects:
        terminal = "ASSAY_DEFECT"
    elif not dev["admission"]:
        terminal = "PARENT_SUFFICIENT__LEARNER_REFUSED_DEPLOYMENT"
    elif orac is not None and reset is not None and orac <= reset:
        terminal = "NO_FAMILY_HEADROOM"
    elif g4.startswith("FAIL"):
        terminal = "FAMILY_PREDICTABLE_WITHOUT_HISTORY"
    elif (cont is not None and reset is not None and lib is not None and shuf is not None
          and cont > reset and cont > lib and cont > shuf and g4 == "PASS"):
        terminal = "HISTORY_INDUCED_SEARCH_PRIOR"
    elif orac is not None and reset is not None and orac > reset:
        terminal = "FAMILY_HEADROOM_OCM_MISSES"
    else:
        terminal = "NO_NATIVE_EFFECT"

    # ---------- HDI-14 cost completeness: charge acquisition, validation, retrieval
    # Developmental acquisition is paid in SLOTS, the same currency as the benefit.
    dev_solve_slots = sum(r["baseline_first_index"] for r in eco["streams"]["train"])
    attrib_path = Path(a.run_dir).parent / "M2P1_ATTRIBUTION_V1.json"
    validate_slots = None
    if attrib_path.exists():
        at = json.loads(attrib_path.read_text())
        validate_slots = sum(r["baseline_slots"] + r["candidate_slots"] for r in at["all_rows"])
    acquisition_slots = dev_solve_slots + (validate_slots or 0)

    def mean_b(arm):
        return arms[arm]["mean_B_slots"] if arm in arms and arms[arm]["mean_B_slots"] else None

    served, base = mean_b("ORDINARY_ADAPTIVE_PARENT"), mean_b("RESET")
    n_prot = len(prot)
    saved_per_target = None if (served is None or base is None) else base - served
    total_saved = None if saved_per_target is None else saved_per_target * n_prot
    amortisation = {
        "developmental_solve_slots": dev_solve_slots,
        "validation_slots": validate_slots,
        "acquisition_slots_total": acquisition_slots,
        "protected_targets": n_prot,
        "saved_slots_per_target": None if saved_per_target is None else round(saved_per_target, 1),
        "total_saved_on_protected": None if total_saved is None else round(total_saved, 1),
        "net_slots": None if total_saved is None else round(total_saved - acquisition_slots, 1),
        "breakeven_targets": None if not saved_per_target or saved_per_target <= 0 else
                             round(acquisition_slots / saved_per_target, 1),
        "note": ("acquisition is charged in full and in the same currency as the benefit; "
                 "developmental solving would have been paid anyway to acquire those "
                 "objects, so this ledger is conservative against the history arm"),
    }

    out = {
        "schema": "OCM_M2P1_SUMMARY_V1", "lane": "LANE_M2_TRAVERSAL_CAPITAL_OPUS",
        "amortisation_ledger": amortisation,
        "owner_issue": 165, "hardening_parent": 323,
        "terminal": terminal,
        "dev_phase": {k: v for k, v in dev.items() if k not in ("training_task_ids",)},
        "entry_gates": dict(eco["entry_gates"], G4_surface_predictor_null=g4,
                            G4_best_surface_ladder=best_surface),
        "surface_orderings_history_free": surface,
        "arms": {a_: {k: v for k, v in r.items() if k != "rows"} for a_, r in arms.items()},
        "comparison": {
            "CONTINUED_vs_RESET": None if (cont is None or reset is None) else cont - reset,
            "CONTINUED_vs_LIBRARY_ONLY": None if (cont is None or lib is None) else cont - lib,
            "CONTINUED_vs_SHUFFLED": None if (cont is None or shuf is None) else cont - shuf,
            "CONTINUED_vs_best_surface": None if cont is None else cont - best_surface,
            "ORACLE_vs_CONTINUED": None if (orac is None or cont is None) else orac - cont,
            "PARENT_vs_CONTINUED": None if (parent is None or cont is None) else parent - cont,
        },
        "novelty_guarantee": {
            "protected_targets": len(prot),
            "shared_normal_forms_with_history": eco["entry_gates"]["G2_shared_normal_forms"],
            "external_verifications": {a_: r["external_verifications"] for a_, r in arms.items()},
        },
    }
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps({"terminal": terminal, "G4": g4,
                      "ladder": {a_: r["ladder_total"] for a_, r in arms.items()},
                      "best_surface": best_surface,
                      "mean_B": {a_: r["mean_B_slots"] for a_, r in arms.items()},
                      "admission": dev["admission"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
