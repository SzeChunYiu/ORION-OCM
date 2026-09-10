#!/usr/bin/env python3
"""TTAC-D2 builder: READINESS_MATRIX_V1 + DECISIVE_CLAIM_REGISTRY_V1.

Scores every ATOM_REGISTRY_V1 atom on R(a)=(T,P,M,C,G,S,R,A,E) per
READINESS_SCHEMA_V1. Honest scoring only: unspecified applicable coordinates
default to 1 (SPECIFIED), never inflated; non-load-bearing coordinates are
null and never block. Downward amendments only via cause.
"""
import json, re, sys
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
ATOMS = json.loads((BASE / "ATOM_REGISTRY_V1.json").read_text())
OV = {}
for _fname in ("d2_overrides_a.json", "d2_overrides_b.json", "d2_overrides_c.json", "d2_overrides_d.json", "d2_overrides_e.json"):
    for _aid, _o in json.loads((BASE / _fname).read_text()).items():
        _cur = OV.setdefault(_aid, {})
        _cur["R"] = {**_cur.get("R", {}), **_o.get("R", {})}  # coordinate-wise; later files refine, never clobber
        if _o.get("cls"):
            _cur["cls"] = _o["cls"]
        if _o.get("note"):
            _cur["note"] = (_cur.get("note", "") + " | " + _o["note"]).strip(" |")

LOAD_BEARING = {
    "THEOREM": ["T", "P", "R", "A"],
    "ENGINEERING_MECHANISM": ["M", "C", "R", "A", "S", "P"],
    "EMPIRICAL_REGULARITY": ["M", "C", "R", "S"],
    "SELF_EVOLUTION": ["M", "C", "A"],
    "GOVERNANCE_META": ["M"],
}
PROFILES = {
    ("THEOREM", "PROVED"): {"T": 5, "P": 3, "R": 4, "A": 2},
    ("THEOREM", "FINITE_CERTIFIED"): {"T": 3, "P": 3, "A": 2},
    ("THEOREM", "PARENT_SUFFICIENT"): {"P": 5, "T": 3},
    ("ENGINEERING_MECHANISM", "EMPIRICALLY_SUPPORTED_AT_SCOPE"): {"M": 3, "C": 3, "R": 3, "A": 2, "S": 2},
    ("ENGINEERING_MECHANISM", "PARENT_SUFFICIENT"): {"P": 4, "M": 2},
    ("EMPIRICAL_REGULARITY", "EMPIRICALLY_SUPPORTED_AT_SCOPE"): {"M": 3, "C": 3, "R": 4, "S": 2},
    ("EMPIRICAL_REGULARITY", "PARENT_SUFFICIENT"): {"P": 4, "M": 2},  # analogy with ENGINEERING profile, noted
    ("SELF_EVOLUTION", "any"): {"M": 3, "C": 3, "A": 4},
    ("GOVERNANCE_META", "audit_complete"): {"M": 3},
}
PR_FOR = [
    (r"hsg-semantic-execution-v1.*D17", "PR #275"), (r"hsg-semantic-execution-v1.*D18", "PR #275"),
    (r"D19_RESULTS", "PR #282"), (r"D20_RESULTS", "PR #283"), (r"D21_RESULTS", "PR #285"),
    (r"GS_R2_AGGREGATE|GS_R2_FREEZE", "PR #279"),
    (r"parallel-developmental-evolution-v1", "PR #217-lane"),
    (r"PARENT_FIRST_REFUSAL", "PR #286"), (r"EXTERNAL_COGNITIVE_INPUT_LEDGER", "PR #280"),
    (r"IN_FLIGHT_COORDINATE_MAP", "PR #281"),
]

def ref_for(atom, cls):
    ev = atom.get("current_evidence", "")
    m = re.search(r"research/[A-Za-z0-9_./-]+", ev)
    art = m.group(0).rstrip(".") if m else "see ATOM_REGISTRY_V1 row"
    pr = next((p for pat, p in PR_FOR if re.search(pat, ev)), None)
    return {"sha_or_pr": f"{art} ({pr})" if pr else art,
            "evidence_class": cls,
            "registered_question": f"{atom['atom_id']} exact_claim per ATOM_REGISTRY_V1"}

rows, gaps = [], []
for a in ATOMS["atoms"]:
    cls, term = a["class"], a["terminal"]
    o = OV.get(a["atom_id"], {})
    vec, refs = {}, {}
    for c in "TPMCGRSRAE" if False else ["T", "P", "M", "C", "G", "S", "R", "A", "E"]:
        # B6-PROFILE-FINAL (D10): P is load-bearing for every PARENT_SUFFICIENT terminal
        # regardless of class -- the claim IS a parent-subtraction claim; a scheme that
        # does not score P for such atoms cannot see its own weakest evidence.
        lbset = set(LOAD_BEARING[cls]) | ({"P"} if term == "PARENT_SUFFICIENT" else set())
        if c not in lbset:
            vec[c] = None
            continue
        vec[c] = o.get("R", {}).get(c, 1)
        if vec[c] >= 2:
            refs[c] = ref_for(a, o.get("cls", "E2"))
    lb = {c: vec[c] for c in lbset}
    prof_key = (cls, term) if (cls, term) in PROFILES else None
    gap = None
    if prof_key:
        need = PROFILES[prof_key]
        short = {c: {"have": lb.get(c), "need": n} for c, n in need.items() if (lb.get(c) or 0) < n}
        gap = short or None
        if short:
            gaps.append({"atom_id": a["atom_id"], "class": cls, "terminal": term, "short_vs_profile": short})
    rows.append({"atom_id": a["atom_id"], "class": cls, "terminal": term, "owner_issue": a["owner_issue"],
                 "R": vec, "load_bearing_min": min(v for v in lb.values() if v is not None),
                 "evidence_refs": refs, "gap_vs_closure_profile": gap,
                 "scoring_notes": o.get("note", "no shipped evidence beyond specification; defaults applied"),
                 "scored_utc": "2026-09-10"})

lb_dist = Counter(r["load_bearing_min"] for r in rows)
weakest = sorted(rows, key=lambda r: (r["load_bearing_min"], -len(r["evidence_refs"])))[:12]
matrix = {
    "schema": "TTAC_READINESS_MATRIX", "version": "V1", "d_step": "TTAC-D2", "owner_issue": 277,
    "built_utc": "2026-09-10", "bound_at_sha": ATOMS.get("bound_at_sha"),
    "registry_ref": "ATOM_REGISTRY_V1.json", "schema_ref": "READINESS_SCHEMA_V1.json",
    "scoring_policy": {
        "defaults": "unspecified applicable coordinate = 1 (SPECIFIED); non-load-bearing = null (never blocks); internal replay caps R at 2; adaptive-exploratory caps at 2 permanently",
        "profile_gap_rule": "gap_vs_closure_profile lists coordinates below the closure-profile minimum for the atom's (class, terminal); it is the D3 blocker-DAG seed",
        "empirical_parent_sufficient_note": "FINAL per B6-PROFILE-FINAL (D10, amendment with cause): EMPIRICAL_REGULARITY/PARENT_SUFFICIENT profile (P4,M2). P4 = parent artifacts disjointly verified (E4-class empirical-parent bar; P5 reserved for formally verifiable parents per THEOREM/PARENT_SUFFICIENT). M2 = measurement at exploratory grade with hostiles registered. Was by-analogy/non-final; finalized because for a parent-sufficiency claim P is load-bearing by the meaning of the claim itself",
        "amendments": "value decreases via amendment with cause; increases require sha+class per schema",
    },
    "rows": rows,
    "census": {"atoms": len(rows), "by_class": dict(Counter(r["class"] for r in rows)),
               "by_terminal": dict(Counter(r["terminal"] for r in rows)),
               "load_bearing_min_distribution": dict(sorted(lb_dist.items())),
               "atoms_with_closure_gap": len(gaps),
               "weakest_12": [{"atom_id": w["atom_id"], "lb_min": w["load_bearing_min"], "terminal": w["terminal"]} for w in weakest]},
    "top_rule_reading": "programme strength = min over load-bearing coordinates of load-bearing atoms; current global structure is dominated by A (autonomy audit, historical chains unaudited) and P/R on theorem atoms",
    "non_final": "EXPLICITLY_NON_FINAL",
}
(BASE / "READINESS_MATRIX_V1.json").write_text(json.dumps(matrix, indent=1) + "\n")

CLAIMS = [
    ("DC-01", 233, "Inherited structure with retained legal strategies cannot worsen optimal burden", ["ATOM-HST-01"]),
    ("DC-02", 233, "Macro admission multiplies Levin allocation exactly by 2^Delta", ["ATOM-HST-04", "ATOM-HST-08"]),
    ("DC-03", 233, "No free lunch out of ecology: learned bias can lose to flat prior", ["ATOM-HST-19", "ATOM-HST-09"]),
    ("DC-04", 233, "Semantic/obligation execution is exact on frozen tiny worlds", ["ATOM-SEM-01", "ATOM-SEM-02", "ATOM-SEM-04", "ATOM-SEM-05", "ATOM-SEM-06", "ATOM-SEM-08", "ATOM-SEM-10"]),
    ("DC-05", 233, "Provenance/revocation exact at scope; adaptive refinement loses to direct search", ["ATOM-PRV-01", "ATOM-PRV-02", "ATOM-SEM-07"]),
    ("DC-06", 62, "Causal macro/lemma reuse supported at registered polynomial scope only", ["ATOM-MAQ-01", "ATOM-MAQ-02"]),
    ("DC-07", 165, "H1 amortized acquisition: LIBRARY_ACQUISITION_EXCEEDS_LATER_SAVINGS (capital negative)", ["ATOM-MAQ-02", "ATOM-MAQ-05"]),
    ("DC-08", 93, "One physical persistent epistemic field", ["ATOM-GEF-01", "ATOM-GEF-02", "ATOM-GEF-03"]),
    ("DC-09", 149, "Governed multi-generation self-evolution", ["ATOM-SEV-01", "ATOM-SEV-02", "ATOM-SEV-03"]),
    ("DC-10", 151, "Developmental-lineage amortization across generations", ["ATOM-DEV-01", "ATOM-DEV-02"]),
    ("DC-11", 50, "Heterogeneous lifetime Pareto signature", ["ATOM-LIF-02", "ATOM-LIF-03"]),
    ("DC-12", 165, "Sparse relevant cognition k/N", ["ATOM-SPX-01", "ATOM-HSG-05"]),
    ("DC-13", 144, "Publication-constitution readiness", ["ATOM-REP-03", "ATOM-REP-04"]),
    ("DC-14", 277, "Replication + autonomy infrastructure exists and is negative-honest", ["ATOM-REP-01", "ATOM-REP-02", "ATOM-PAR-01"]),
    ("DC-15", 165, "Programme closure: every required lane has a bounded disposition", [r["atom_id"] for r in rows]),
]
by_id = {r["atom_id"]: r for r in rows}
claims = []
for cid, iss, sent, atoms in CLAIMS:
    mem = [by_id[a] for a in atoms]
    weakest_links = []
    for m in mem:
        for c, v in m["R"].items():
            if v is not None and v <= 1:
                weakest_links.append({"atom": m["atom_id"], "coord": c, "value": v})
    cur_min = min(m["load_bearing_min"] for m in mem)
    claims.append({"claim_id": cid, "owner_issue": iss, "sentence": sent, "atoms": atoms,
                   "composition_rule": "min over load-bearing coordinates of member atoms",
                   "current_min": cur_min,
                   "weakest_links": weakest_links[:8],
                   "ceiling_note": "claim ceiling = strongest sentence compatible with member vectors; see ATOM_REGISTRY claim_ceiling fields"})
dcr = {"schema": "TTAC_DECISIVE_CLAIM_REGISTRY", "version": "V1", "d_step": "TTAC-D2", "owner_issue": 277,
       "built_utc": "2026-09-10", "bound_at_sha": ATOMS.get("bound_at_sha"),
       "matrix_ref": "READINESS_MATRIX_V1.json", "claims": claims,
       "census": {"claims": len(claims), "current_min_distribution": dict(Counter(c["current_min"] for c in claims))},
       "non_final": "EXPLICITLY_NON_FINAL"}
(BASE / "DECISIVE_CLAIM_REGISTRY_V1.json").write_text(json.dumps(dcr, indent=1) + "\n")

print(f"rows={len(rows)} gaps={len(gaps)} claims={len(claims)}")
print("lb_min dist:", dict(sorted(lb_dist.items())))
print("claim min dist:", dict(Counter(c['current_min'] for c in claims)))
missing = [a["atom_id"] for a in ATOMS["atoms"] if a["atom_id"] not in {r['atom_id'] for r in rows}]
assert not missing, missing
assert all(set(["atom_id", "R", "evidence_refs", "scoring_notes", "scored_utc"]) <= set(r) for r in rows)
print("VALIDATION OK")
