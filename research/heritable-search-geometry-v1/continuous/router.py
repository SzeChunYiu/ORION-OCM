#!/usr/bin/env python3
"""HSG continuous calibration — executable router (D11 constants + D13 cross-index).

The executable twin of the D12/D15 arm protocol: motif routing + eps-exploration
+ cross-index probes over a donor bank, priced under the frozen D12 price model.
Deterministic given --seed. Emits a D12-schema-compatible action log so the same
scorer extends to compute-calibration runs.

Usage:
  python3 router.py --atom <ATOM_ID> --bank DONOR_BANK_V1.jsonl --atoms ATOM_BANK_V1.jsonl
                    --term-vocab TERM_VOCAB_V1.json [--eps 0.1] [--probe-share 0.05]
                    [--budget 1000] [--seed 0] [--out LOG.jsonl]

Frozen constants (D12_SCORING_V1.json): eps_default=0.1 in (0.0,0.2) exclusive (T63);
validation_reserve=50; inspection cap L3; prices map=15, L0=1, L1=3, L2=10, L3=40,
L4=100, L5=250, synth=30, validate=50. Stop: per-partition only.

Documented deviation: overlap() is the CONTAINMENT coefficient |A&B|/min(|A|,|B|),
not Jaccard — the bank's donor cards carry singleton motif lists, so Jaccard is
capped at 1/|atom motifs| and cannot reach the 0.34 operating point. Threshold
value unchanged (0.34, D12 A4 operating point).
"""
import argparse, json, random
from pathlib import Path

PRICES = {"map": 15, "L0": 1, "L1": 3, "L2": 10, "L3": 40, "L4": 100, "L5": 250,
          "synth": 30, "validate": 50}
EPS_DEFAULT, EPS_RANGE = 0.1, (0.0, 0.2)
PROBE_SHARE_DEFAULT = 0.05
VALIDATION_RESERVE = 50
INSPECTION_CAP = 3          # L3
OVERLAP_ACCEPT = 0.34       # containment on structural motifs; D12 A4 operating point

def load_bank(path):
    return [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]

def mechanism_terms(text, term_vocab):
    """Mechanism terms present in a text, by keyword hit on non-discipline keys."""
    s = text.lower()
    return [tid for tid, kws in term_vocab.items()
            if not tid.endswith("_disciplines") and any(k in s for k in kws)]

def overlap(a, b):
    return len(a & b) / min(len(a), len(b)) if (a and b) else 0.0

def probe_share_used(log, budget):
    s = sum(l["cost"] for l in log if l.get("channel") == "cross_index")
    return s / budget

def eps_share_used(log, budget):
    s = sum(l["cost"] for l in log if l.get("channel") == "eps")
    return s / budget

def donor_gets_deeper(donor, rung):
    """Ladder continuation rule: donor survives rung r if its depth marker >= r."""
    return donor.get("depth", 3) >= rung

def route(atom, bank, term_vocab, motif_index, eps, probe_share, budget, rng, log):
    """One atom's search. Returns (cost, receipts, donors_found)."""
    spent = 0
    def pay(action, kind, **fields):
        nonlocal spent
        price = PRICES[kind]
        assert spent + price <= budget, f"hard stop: {action} would exceed budget"
        spent += price
        log.append({"type": "action", "action": action, "kind": kind, "cost": price,
                    "cum": spent, "atom": atom["atom"], **fields})
    def stop():
        return spent + PRICES["L3"] > budget - VALIDATION_RESERVE

    pay("map", "map", query=atom["atom"])
    terms = mechanism_terms(atom["statement"], term_vocab)
    log.append({"type": "route", "atom": atom["atom"], "mechanism_terms": terms})
    # 1. motif routing: donors sharing a mechanism term with the atom
    routed = motif_index.get(atom["atom"], [])
    # 2. cross-index probes: owning disciplines of the atom's mechanism terms,
    #    INCLUDING non-adjacent ones; one L2 probe each, within the probe share
    probe_budget = probe_share * budget
    cand_disciplines = []
    for tid in terms:
        for d in term_vocab.get(tid + "_disciplines", []):
            if d not in cand_disciplines:
                cand_disciplines.append(d)
    rng.shuffle(cand_disciplines)
    probed = []
    for d in cand_disciplines:
        if spent + PRICES["L2"] > budget - VALIDATION_RESERVE: break
        if probe_share_used(log, budget) + PRICES["L2"] / budget > probe_share + 1e-9: break
        pool = [x for x in bank if x["discipline"] == d and x not in probed]
        if not pool: continue
        pick = rng.choice(pool)
        pay("probe", "L2", donor=pick["donor_id"], discipline=d, channel="cross_index")
        probed.append(pick)
    # 3. eps-exploration: random non-adjacent discipline probes
    all_disciplines = sorted({x["discipline"] for x in bank})
    while eps_share_used(log, budget) < eps and not stop():
        avail = [d for d in all_disciplines if d not in cand_disciplines
                 and any(x["discipline"] == d and x not in probed for x in bank)]
        if not avail:
            avail = [d for d in all_disciplines
                     if any(x["discipline"] == d and x not in probed for x in bank)]
        if not avail: break
        d = rng.choice(avail)
        pick = rng.choice([x for x in bank
                           if x["discipline"] == d and x not in probed])
        pay("probe", "L2", donor=pick["donor_id"], discipline=d, channel="eps")
        probed.append(pick)
    # 4. deep inspection on structural overlap (rung ladder up to L3)
    receipts, found = [], []
    seen = set()
    for donor in probed + [bank[i] for i in routed]:
        if donor["donor_id"] in seen or stop(): break
        seen.add(donor["donor_id"])
        ov = overlap(set(donor.get("structural_motifs", [])),
                     set(atom.get("structural_motifs", [])))
        if ov < OVERLAP_ACCEPT:
            log.append({"type": "action", "action": "reject", "atom": atom["atom"],
                        "donor": donor["donor_id"], "overlap": round(ov, 3),
                        "reason": "structural_overlap_below_threshold"})
            continue
        for rung in (1, 2, 3):
            pay(f"inspect_L{rung}", f"L{rung}", donor=donor["donor_id"],
                overlap=round(ov, 3))
            if not donor_gets_deeper(donor, rung):
                break
        found.append(donor["donor_id"])
        if spent + PRICES["synth"] + PRICES["validate"] <= budget:
            pay("synth", "synth", donor=donor["donor_id"])
            pay("validate", "validate", donor=donor["donor_id"])
            receipts.append({"receipt_id": f"{atom['atom']}-{donor['donor_id']}",
                             "status": "SUPPORTED"})
    log.append({"type": "arm_end", "atom": atom["atom"], "final_cost": spent,
                "receipts": receipts, "hard_stop_reading": spent})
    return spent, receipts, found

def build_motif_index(atoms, bank, term_vocab):
    """atom_id -> bank indices of donors sharing >=1 mechanism term."""
    idx = {}
    for a in atoms:
        terms = set(mechanism_terms(a["statement"], term_vocab))
        idx[a["atom"]] = [i for i, d in enumerate(bank)
                          if terms & set(d.get("mechanism_terms", []))]
    return idx

def load_vocab(path):
    tv = json.loads(Path(path).read_text())
    out = {k: v["keywords"] for k, v in tv.items()}
    for k, v in tv.items():
        out[k + "_disciplines"] = v["probe_disciplines"]
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--atom", required=True)
    ap.add_argument("--bank", required=True)
    ap.add_argument("--atoms", help="atoms jsonl with statements+motifs")
    ap.add_argument("--term-vocab", help="json: term_id -> keywords + disciplines")
    ap.add_argument("--eps", type=float, default=EPS_DEFAULT)
    ap.add_argument("--probe-share", type=float, default=PROBE_SHARE_DEFAULT)
    ap.add_argument("--budget", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="/dev/stdout")
    a = ap.parse_args()
    assert EPS_RANGE[0] < a.eps < EPS_RANGE[1], "eps outside admissible range (T63)"
    bank = load_bank(a.bank)
    atoms = {x["atom"]: x for x in load_bank(a.atoms)} if a.atoms else {}
    term_vocab = load_vocab(a.term_vocab) if a.term_vocab else {}
    atom = atoms.get(a.atom) or {"atom": a.atom, "statement": a.atom,
                                 "structural_motifs": []}
    motif_index = build_motif_index(list(atoms.values()), bank, term_vocab)
    rng = random.Random(a.seed)
    log = []
    cost, receipts, found = route(atom, bank, term_vocab, motif_index,
                                  a.eps, a.probe_share, a.budget, rng, log)
    Path(a.out).write_text(
        "\n".join(json.dumps(l, ensure_ascii=False) for l in log) + "\n")
    print(json.dumps({"atom": a.atom, "final_cost": cost, "receipts": len(receipts),
                      "donors_found": found, "eps": a.eps,
                      "probe_share": a.probe_share, "seed": a.seed}))

if __name__ == "__main__":
    main()
