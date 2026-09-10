#!/usr/bin/env python3
"""Build the machine-usable donor/atom banks + term vocab for the executable router.

Sources (all on main, no external fetches):
  - d13/MECHANISM_CROSSINDEX_V1.json  -> term vocab (keywords per mechanism term,
    probe disciplines per term)
  - d12/arms/*/  receipts + logs      -> donor cards (donor_id, discipline,
    structural motifs from the receipts, depth marker)
  - HSG_ATOM_TABLE_V1.json            -> atom bank (statements + motifs)
Writes DONOR_BANK_V1.jsonl, ATOM_BANK_V1.jsonl, TERM_VOCAB_V1.json next to itself.

Run from research/heritable-search-geometry-v1/: python3 continuous/donor_bank.py
"""
import json, re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent   # .../heritable-search-geometry-v1
CONT = BASE / "continuous"

# ---- term vocab: mechanism term -> retrieval keywords + probe disciplines ----
KW = {
  "M01_saturation_capacity_limit": ["saturation", "capacity limit", "congestion",
      "queueing", "dose-response", "server saturation"],
  "M02_channeling_localized_flow": ["channeling", "localization", "dedicated lane",
      "compartment", "jit", "supply chain placement"],
  "M03_threshold_economics": ["amortization", "build vs", "per-use", "fixed cost",
      "tooling", "warehouse", "facility location", "cache warming", "promotion"],
  "M04_renewal_regenerative": ["renewal", "regenerative", "turnover",
      "garbage collection", "planned replacement", "reward theorem"],
  "M05_depletion_nonrenewable": ["depletion", "non-renewable", "extraction",
      "fisheries", "heap exhaustion", "hotelling", "option value", "irreversible"],
  "M06_ratchet_monotone_accumulation": ["ratchet", "monotone", "hypervolume",
      "archive", "kelly", "irreversibility", "hysteresis", "accumulation"],
  "M07_allocation_under_capacity": ["allocation", "budget allocation", "halving",
      "kidney exchange", "spectrum auction", "flux allocation"],
  "M08_contraction_coupling": ["contraction", "coupling", "dobrushin",
      "coefficient", "lockstep", "coupling of chains"],
  "M09_neutral_sets_degeneracy": ["neutral", "degeneracy", "null-space",
      "redundancy", "aliasing", "billiards"],
  "M10_sufficiency_compression": ["sufficiency", "sufficient statistic", "blackwell",
      "rate-distortion", "compression", "bisimulation", "information"],
  "M11_local_to_global_consistency": ["gluing", "consistency", "lumpability",
      "coarse-graining", "renormalization", "sheaf", "local-to-global"],
  "M12_exploration_necessity": ["exploration", "best-arm", "lower bound",
      "pac-bayes", "novelty search", "speedup"],
}

def load_json(p):
    return json.loads((BASE / p).read_text())

def terms_from_text(s):
    """Mechanism terms present in text, by keyword hit (router-compatible)."""
    t = s.lower()
    return [tid for tid, kws in KW.items() if any(k in t for k in kws)]

def donors_from_d13():
    """One donor card per (term, owning discipline) row of the cross-index."""
    ci = load_json("d13/MECHANISM_CROSSINDEX_V1.json")
    out = []
    for t in ci["terms"]:
        for d in t["owner_disciplines"]:
            out.append({
                "donor_id": "D13-" + t["id"] + "-" + re.sub(r"\W+", "", d)[:24],
                "name": d,
                "discipline": d.split("(")[0].split(";")[0].strip().lower(),
                "mechanism_terms": [t["id"]],
                "structural_motifs": [t["id"]],
                "depth": 3,
                "source": "d13_crossindex",
            })
    return out

def donors_from_d12_receipts():
    """Donor cards from every transport receipt the five arms actually emitted.
    Mechanism terms / motifs extracted by keyword hit over the receipt's own
    structural text (donor_structure + mapping + preserved_relations)."""
    out = []
    rdir = BASE / "d12" / "arms"
    for rf in sorted(rdir.glob("A*_receipts/*.json")):
        try:
            j = json.loads(rf.read_text())
        except Exception:
            continue
        donor = j.get("donor_source_ids") or j.get("strongest_parent") or rf.stem
        disc = j.get("donor_domain") or "unattributed"
        def flat(v):
            if isinstance(v, list):
                return [str(x) for x in v]
            return [str(v)] if v else []
        text = " ".join(
            flat(j.get("donor_structure")) + flat(j.get("mapping")) +
            flat(j.get("preserved_relations")) + flat(j.get("candidate_theorem")))
        motifs = terms_from_text(text)
        total = (j.get("mapping_search_cost", {}) or {}).get("total", 110)
        out.append({
            "donor_id": "D12-" + rf.parent.name + "-" + re.sub(r"\W+", "", str(donor))[:32],
            "name": str(donor),
            "discipline": str(disc).split("/")[0].strip().lower(),
            "mechanism_terms": motifs,
            "structural_motifs": motifs,
            "depth": 3 if total >= 100 else 2,
            "source": f"d12:{rf.parent.name}/{rf.name}",
            "status": j.get("status"),
        })
    return out

def atom_bank(vocab):
    """Synthesize a searchable statement per atom from the table's own fields,
    then extract mechanism-term motifs with the same keyword hit the router uses."""
    at = load_json("HSG_ATOM_TABLE_V1.json")
    rows = []
    for c in at.get("concepts", []):
        stmt = " ".join(filter(None, [c.get("atom", ""), str(c.get("object", "")),
                                      str(c.get("ladder", "")),
                                      str(c.get("parents_hint", ""))]))
        rows.append({"atom": c["atom"], "statement": stmt,
                     "structural_motifs": terms_from_text(stmt), "kind": "concept"})
    for t in at.get("theorems", []):
        stmt = " ".join(filter(None, [t.get("atom", ""), str(t.get("ladder_question", "")),
                                      str(t.get("assumption_removals", "")),
                                      str(t.get("verdicts", ""))]))
        rows.append({"atom": t["atom"], "statement": stmt,
                     "structural_motifs": terms_from_text(stmt), "kind": "theorem"})
    return rows

def main():
    ci = load_json("d13/MECHANISM_CROSSINDEX_V1.json")
    vocab = {t["id"]: {"keywords": KW[t["id"]],
                        "probe_disciplines": [d.split("(")[0].split(";")[0].strip().lower()
                                              for d in t["owner_disciplines"]]}
             for t in ci["terms"]}
    donors = donors_from_d13() + donors_from_d12_receipts()
    # dedup by (name, discipline), merging mechanism terms
    seen, bank = {}, []
    for d in donors:
        k = (d["name"], d["discipline"])
        if k in seen:
            e = bank[seen[k]]
            for f in ("mechanism_terms", "structural_motifs"):
                m = e[f] + [x for x in d[f] if x not in e[f]]
                e[f] = m
            continue
        seen[k] = len(bank); bank.append(d)
    atoms = atom_bank(vocab)
    CONT.mkdir(exist_ok=True)
    (CONT / "DONOR_BANK_V1.jsonl").write_text(
        "\n".join(json.dumps(d, ensure_ascii=False) for d in bank) + "\n")
    (CONT / "ATOM_BANK_V1.jsonl").write_text(
        "\n".join(json.dumps(a, ensure_ascii=False) for a in atoms) + "\n")
    (CONT / "TERM_VOCAB_V1.json").write_text(json.dumps(vocab, indent=1) + "\n")
    print(f"bank={len(bank)} donors, atoms={len(atoms)}, vocab={len(vocab)} terms")

if __name__ == "__main__":
    main()
