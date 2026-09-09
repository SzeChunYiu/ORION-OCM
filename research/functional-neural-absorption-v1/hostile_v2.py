"""FNA-1b hostile v2: a TYPE_DECOY world that can actually defeat METAPATH_TYPE_YIELD.

``fna1b.py`` registered two predictions. The first held: METAPATH beats RARITY on
COMMON_DECISIVE and RARE_DECOY. The second -- that a target-type decoy would defeat the
policy -- DID NOT RESOLVE. ``fna1b.py``'s own rule fired and returned
CANNOT_CHECK_TYPE_DECOY_DID_NOT_DISCRIMINATE rather than banking the two wins.

Why v1 failed to discriminate, diagnosed from the receipt: at budget 64 every non-oracle
arm failed and at 128 every arm succeeded, so no budget existed at which NAIVE found the
answer and METAPATH did not. The decisive edge sat roughly 67th in the seed's insertion
order, so a naive scan had no head start it could lose.

v2 fixes the hostile, not the policy. Three changes, all of which make the world HARDER
for METAPATH_TYPE_YIELD:

    1. the decisive atom sits on a TYPE-POOR channel, so the policy deprioritises it;
    2. its edge is inserted FIRST from the seed, so a naive order finds it immediately;
    3. the decoy channel is enriched to 60 target-type atoms and scores 1.0, so the
       policy must exhaust it before reaching the answer.

Sharpening a falsifier is legitimate; weakening one is not. ``fna1b.py`` and its receipt
are left untouched as the record that v1 did not discriminate.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "src"))

from ocm.kso.space import KnowledgeSpace, Atom, Hyperedge      # noqa: E402
import experiment as E                                          # noqa: E402
import fna1b as B                                               # noqa: E402

SCHEMA = "ocm.fna.fna1b-hostile-v2.v1"


def type_decoy_sharp(n_distractors: int = 40, decoys: int = 60, siblings: int = 6):
    """Decisive on a type-poor channel and FIRST in insertion order; bulk decoys on a
    type-rich channel. Built to make METAPATH_TYPE_YIELD strictly worse than naive."""
    atoms = [Atom(atom_id="seed", atom_type="query_seed"),
             Atom(atom_id=E.DECISIVE, atom_type=B.TARGET_TYPE)]
    atoms += [Atom(atom_id=f"d{i}", atom_type="claim") for i in range(n_distractors)]
    atoms += [Atom(atom_id=f"s{i}", atom_type=B.TARGET_TYPE) for i in range(siblings)]
    atoms += [Atom(atom_id=f"t{i}", atom_type=B.TARGET_TYPE) for i in range(decoys)]

    # (2) decisive edge FIRST, on DEPENDENCE -- which will score poorly on type yield.
    edges = [Hyperedge(edge_id="e_decisive", tails=("seed",), heads=(E.DECISIVE,),
                       relation_type="DEPENDENCE")]
    # Siblings on SUPPORT only, so DEPENDENCE stays type-poor.
    edges += [Hyperedge(edge_id=f"e_s{i}", tails=("seed",), heads=(f"s{i}",),
                        relation_type="SUPPORT") for i in range(siblings)]
    edges += [Hyperedge(edge_id=f"e_d{i}", tails=("seed",), heads=(f"d{i}",),
                        relation_type="DEPENDENCE" if i % 2 else "SUPPORT")
              for i in range(n_distractors)]
    # (3) a type-rich decoy channel scoring 1.0.
    edges += [Hyperedge(edge_id=f"e_t{i}", tails=("seed",), heads=(f"t{i}",),
                        relation_type=B.DECOY_CHANNEL) for i in range(decoys)]
    return KnowledgeSpace(atoms=tuple(atoms), hyperedges=tuple(edges))


def run(budgets=(2, 4, 8, 16, 32, 64, 96, 128, 160)) -> dict:
    ks = type_decoy_sharp()
    rarity, counts = E.channel_rarity(ks)
    meta, score = B.metapath_order(ks, B.TARGET_TYPE)
    rows = {}
    for b in budgets:
        naive, wn = E.bounded_closure(ks, ["seed"], b, channel_order=None)
        rar, _ = E.bounded_closure(ks, ["seed"], b, channel_order=rarity)
        met, _ = E.bounded_closure(ks, ["seed"], b, channel_order=meta)
        rows[str(b)] = {
            "budget_binds": wn["truncated"],
            "NAIVE": {"found": E.DECISIVE in naive, "reached": len(naive)},
            "RARITY_FIRST": {"found": E.DECISIVE in rar, "reached": len(rar)},
            "METAPATH_TYPE_YIELD": {"found": E.DECISIVE in met, "reached": len(met)},
        }
    binding = {b: r for b, r in rows.items() if r["budget_binds"]}
    worse = sorted(b for b, r in binding.items()
                   if r["NAIVE"]["found"] and not r["METAPATH_TYPE_YIELD"]["found"])
    return {"schema": SCHEMA,
            "analysis_status": "SHARPENED_FALSIFIER_AFTER_V1_DID_NOT_DISCRIMINATE",
            "authority": ("Research-only. Sharpens a hostile so it can kill the policy; it "
                          "cannot strengthen the policy. fna1b.py is untouched."),
            "supersedes_note": ("fna1b.py returned CANNOT_CHECK_TYPE_DECOY_DID_NOT_DISCRIMINATE. "
                                "That receipt is retained; this does not overwrite it."),
            "world": {"atoms": len(ks.atoms), "edges": len(ks.hyperedges),
                      "channel_counts": counts, "metapath_score": score,
                      "metapath_order": list(meta), "rarity_order": list(rarity),
                      "decisive_channel": "DEPENDENCE",
                      "decisive_edge_insertion_index": 0,
                      "target_type_atom_count": sum(
                          1 for a in ks.atoms if a.atom_type == B.TARGET_TYPE)},
            "rows": rows,
            "metapath_WORSE_than_naive": worse}


def verdict(doc: dict) -> dict:
    worse = doc["metapath_WORSE_than_naive"]
    out = {"metapath_worse_than_naive_at": worse,
           "falsifier_discriminates": bool(worse),
           "metapath_score": doc["world"]["metapath_score"],
           "metapath_order": doc["world"]["metapath_order"]}
    if worse:
        out["terminal"] = "NON_NEURAL_RESOURCE_ADVANTAGE_AT_REGISTERED_SCOPE"
        out["terminal_reason"] = (
            "The falsifier now bites, and the policy fails it. METAPATH_TYPE_YIELD is "
            f"strictly worse than a naive order at budgets {worse}, because a channel "
            "enriched with target-type atoms that are not the answer draws the whole budget "
            "before a type-poor channel carrying the answer is touched. Combined with "
            "fna1b's confirmed first prediction -- METAPATH beats RARITY on COMMON_DECISIVE "
            "and RARE_DECOY -- the mechanism's scope is now bounded on BOTH sides. It "
            "carries relevance where rarity carried only scarcity, and it is misled by "
            "exactly the signal it reads. That failure is what shows it is not an oracle. "
            "The engineered fix is therefore real and bounded, not a rescue: FNA-1's "
            "negative is solved for the two worlds that motivated it and a third world is "
            "now known to break it.")
    else:
        out["terminal"] = "CANNOT_CHECK_SHARPENED_FALSIFIER_STILL_DID_NOT_DISCRIMINATE"
        out["terminal_reason"] = (
            "Even the sharpened world produced no budget at which a naive order found the "
            "answer and the policy did not. Two failed attempts to kill the policy are not "
            "evidence it is sound; they are evidence this world family cannot test it. No "
            "positive is banked.")
    out["what_this_does_not_establish"] = (
        "The metapath score is computed by a scan over all edges and is NOT charged against "
        "the query budget in any arm here. That is a real accounting gap -- #214 section 6 "
        "names exactly this ('explicit retrieval may move, not remove, cost') -- and it is "
        "the next thing to close, not something these numbers already handle.")
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    doc = run()
    doc["verdict"] = verdict(doc)
    a.out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: doc["verdict"][k] for k in (
        "terminal", "falsifier_discriminates", "metapath_worse_than_naive_at",
        "metapath_order")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
