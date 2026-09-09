"""FNA-1b: engineer past FNA-1's negative -- a channel policy that carries RELEVANCE.

FNA-1 measured a real but narrow advantage and then killed most of it. Rarity-first
beats a naive expansion order only when the rare channel happens to carry the answer;
it is neutral when a common channel does, and strictly WORSE against a rare-channel
decoy. The diagnosis was that rarity is a SELECTIVITY signal: it predicts where few
edges are, never where the answer is.

This study engineers the fix rather than recording the negative and stopping. The
mechanism is the parent Phase B already named for typed channels -- METAPATH RETRIEVAL
over heterogeneous information networks -- not a new OCM invention.

## The policy, and why it is not an oracle

A query states what KIND of object it wants. ``METAPATH_TYPE_YIELD`` scores each
relation channel by the fraction of its edges whose head atom carries that target type,
and expands high-scoring channels first:

    score(c) = |{e : relation_type(e)=c, atom_type(head(e))=target}| / |{e : relation_type(e)=c}|

It reads the query's TARGET TYPE and the space's own edge/atom types. It never reads
which atom is the answer. The line between legitimate and oracle is exactly there, and
every world below contains SEVERAL atoms of the target type, so knowing the type
NARROWS the search and cannot identify the answer. A world with a unique target-type
atom would make this policy an oracle in disguise, which is why none is used.

## Registered prediction, before execution

1. METAPATH beats RARITY on COMMON_DECISIVE and RARE_DECOY, because it follows type
   rather than scarcity and those are the two worlds where scarcity misleads.
2. METAPATH is BEATEN on TYPE_DECOY, where a channel is deliberately enriched with
   target-type atoms that are not the answer. A policy that wins there too is reading
   something it should not, and that outcome is registered as a DEFECT rather than a
   triumph -- see ``verdict``.

Prediction 2 is the load-bearing one. Engineering a fix to a measured negative is only
legitimate if the fix is frozen and run against worlds built to kill it.

Research-only. No production source modified, no model trained, no router implemented.
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

SCHEMA = "ocm.fna.fna1b-metapath-channel-policy.v1"

TARGET_TYPE = "counterexample"
DECOY_CHANNEL = "EMBEDDING"
WORLDS = ("RARE_DECISIVE", "COMMON_DECISIVE", "RARE_DECOY", "TYPE_DECOY")


def world(kind: str, n_distractors: int = 60, decoys: int = 40, siblings: int = 6):
    """Every world holds several TARGET_TYPE atoms, so type narrows but never identifies."""
    atoms = [Atom(atom_id="seed", atom_type="query_seed"),
             Atom(atom_id=E.DECISIVE, atom_type=TARGET_TYPE)]
    atoms += [Atom(atom_id=f"d{i}", atom_type="claim") for i in range(n_distractors)]
    # Sibling target-type atoms, reachable on common channels. These are the reason
    # target type cannot single out the answer.
    atoms += [Atom(atom_id=f"s{i}", atom_type=TARGET_TYPE) for i in range(siblings)]

    edges = [Hyperedge(edge_id=f"e_d{i}", tails=("seed",), heads=(f"d{i}",),
                       relation_type=E.COMMON_CHANNELS[i % 2]) for i in range(n_distractors)]
    for i in range(0, n_distractors, 3):
        for j in (1, 2):
            if i + j < n_distractors:
                edges.append(Hyperedge(edge_id=f"e_c{i}_{j}", tails=(f"d{i}",),
                                       heads=(f"d{i + j}",),
                                       relation_type=E.COMMON_CHANNELS[j % 2]))
    for i in range(siblings):
        edges.append(Hyperedge(edge_id=f"e_s{i}", tails=("seed",), heads=(f"s{i}",),
                               relation_type=E.COMMON_CHANNELS[i % 2]))

    if kind == "RARE_DECISIVE":
        edges.append(Hyperedge(edge_id="e_decisive", tails=("seed",), heads=(E.DECISIVE,),
                               relation_type=E.RARE_CHANNEL))
    else:
        edges.append(Hyperedge(edge_id="e_decisive", tails=("seed",), heads=(E.DECISIVE,),
                               relation_type=E.COMMON_CHANNELS[0]))

    if kind == "RARE_DECOY":
        # Bulk on a scarce channel: what beat rarity-first in FNA-1's hostile.
        atoms += [Atom(atom_id=f"k{i}", atom_type="claim") for i in range(decoys)]
        edges += [Hyperedge(edge_id=f"e_k{i}", tails=("seed",), heads=(f"k{i}",),
                            relation_type=DECOY_CHANNEL) for i in range(decoys)]
    if kind == "TYPE_DECOY":
        # Bulk of TARGET-TYPE atoms on a channel that does NOT carry the answer. This is
        # built specifically to defeat METAPATH_TYPE_YIELD.
        atoms += [Atom(atom_id=f"t{i}", atom_type=TARGET_TYPE) for i in range(decoys)]
        edges += [Hyperedge(edge_id=f"e_t{i}", tails=("seed",), heads=(f"t{i}",),
                            relation_type=DECOY_CHANNEL) for i in range(decoys)]
    return KnowledgeSpace(atoms=tuple(atoms), hyperedges=tuple(edges))


def metapath_order(ks: KnowledgeSpace, target_type: str):
    """Channels ordered by the fraction of their edges landing on the target type.

    Reads: the query's target type, and the space's edge and atom types.
    Never reads: which atom is the answer.
    """
    amap = ks.atom_view
    hits: dict[str, int] = {}
    total: dict[str, int] = {}
    for e in ks.hyperedges:
        total[e.relation_type] = total.get(e.relation_type, 0) + 1
        if any(amap[h].atom_type == target_type for h in e.heads):
            hits[e.relation_type] = hits.get(e.relation_type, 0) + 1
    score = {c: hits.get(c, 0) / total[c] for c in total}
    return tuple(sorted(score, key=lambda c: (-score[c], c))), score


def run(budgets=(4, 8, 16, 32, 64, 128)) -> dict:
    out = {}
    for kind in WORLDS:
        ks = world(kind)
        rarity, counts = E.channel_rarity(ks)
        meta, score = metapath_order(ks, TARGET_TYPE)
        oracle_channel = next(e.relation_type for e in ks.hyperedges
                              if e.edge_id == "e_decisive")
        rows = {}
        for b in budgets:
            arms = {
                "NAIVE": E.bounded_closure(ks, ["seed"], b, channel_order=None),
                "RARITY_FIRST": E.bounded_closure(ks, ["seed"], b, channel_order=rarity),
                "METAPATH_TYPE_YIELD": E.bounded_closure(ks, ["seed"], b, channel_order=meta),
                "ORACLE": E.bounded_closure(
                    ks, ["seed"], b,
                    channel_order=(oracle_channel,) + tuple(c for c in counts if c != oracle_channel)),
            }
            rows[str(b)] = {"budget_binds": arms["NAIVE"][1]["truncated"],
                            **{k: {"found": E.DECISIVE in r, "reached": len(r)}
                               for k, (r, _w) in arms.items()}}
        binding = {b: r for b, r in rows.items() if r["budget_binds"]}
        out[kind] = {
            "channel_counts": counts, "rarity_order": list(rarity),
            "metapath_score": score, "metapath_order": list(meta),
            "decisive_channel": oracle_channel,
            "target_type_atom_count": sum(1 for a in ks.atoms if a.atom_type == TARGET_TYPE),
            "rows": rows,
            "metapath_beats_rarity": sorted(
                b for b, r in binding.items()
                if r["METAPATH_TYPE_YIELD"]["found"] and not r["RARITY_FIRST"]["found"]),
            "metapath_beats_naive": sorted(
                b for b, r in binding.items()
                if r["METAPATH_TYPE_YIELD"]["found"] and not r["NAIVE"]["found"]),
            "metapath_WORSE_than_naive": sorted(
                b for b, r in binding.items()
                if r["NAIVE"]["found"] and not r["METAPATH_TYPE_YIELD"]["found"]),
        }
    return {"schema": SCHEMA,
            "analysis_status": "ENGINEERED_RESPONSE_TO_FNA1_NEGATIVE",
            "authority": ("Research-only. Runs main's gated closure through the FNA-1 bounded "
                          "harness. No production source modified, no model trained, no router. "
                          "#71 remains LEARNED_ROUTER_NOT_YET_AUTHORIZED."),
            "evidence_class": "E1 / L1",
            "target_type": TARGET_TYPE,
            "policy_information_surface": (
                "METAPATH_TYPE_YIELD reads the query's target atom type plus the space's own "
                "edge and atom types. It never reads which atom is the answer. Every world "
                "contains several target-type atoms so that type NARROWS and cannot IDENTIFY."),
            "worlds": out}


def verdict(doc: dict) -> dict:
    w = doc["worlds"]
    fixed = sorted(k for k in WORLDS if w[k]["metapath_beats_rarity"])
    survives = sorted(k for k in WORLDS if not w[k]["metapath_WORSE_than_naive"])
    broken = sorted(k for k in WORLDS if w[k]["metapath_WORSE_than_naive"])
    out = {
        "worlds_where_metapath_beats_rarity": fixed,
        "worlds_where_metapath_is_worse_than_naive": broken,
        "worlds_survived": survives,
        "type_decoy_defeated_the_policy": bool(w["TYPE_DECOY"]["metapath_WORSE_than_naive"]),
        "target_type_atom_counts": {k: w[k]["target_type_atom_count"] for k in WORLDS},
    }
    # Prediction 2: a policy that wins the TYPE_DECOY world is reading too much.
    if not out["type_decoy_defeated_the_policy"] and \
            not w["TYPE_DECOY"]["metapath_beats_naive"]:
        out["type_decoy_note"] = (
            "TYPE_DECOY neither defeated nor was beaten by the policy: it did not "
            "discriminate. That is a weak test, not a passed one.")
    if out["type_decoy_defeated_the_policy"]:
        out["terminal"] = "NON_NEURAL_RESOURCE_ADVANTAGE_AT_REGISTERED_SCOPE"
        out["terminal_reason"] = (
            "The engineered policy fixes the FNA-1 negative where FNA-1 said it was broken "
            f"and FAILS where it was predicted to fail. It beats rarity-first on {fixed} -- "
            "the worlds where scarcity misleads -- because it orders channels by where the "
            "query's target TYPE lands rather than by where edges are few. And it is "
            "strictly worse than a naive order on TYPE_DECOY, where a channel is enriched "
            "with target-type atoms that are not the answer. That failure is the evidence "
            "the policy is not an oracle: it can be misled by exactly the information it "
            "reads. A policy that won every world would be reading the answer.")
    else:
        out["terminal"] = "CANNOT_CHECK_TYPE_DECOY_DID_NOT_DISCRIMINATE"
        out["terminal_reason"] = (
            "The hostile world built to defeat METAPATH_TYPE_YIELD did not defeat it, and "
            "did not clearly fail to either. Without a world that can kill the policy, a "
            "positive on the other three is not evidence the mechanism is sound rather "
            "than over-informed. The honest disposition is that this pass did not check it.")
    out["what_this_does_not_establish"] = (
        "Not a general retrieval policy: it is measured on four planted worlds, one author, "
        "one population (E1/L1). Not a claim about attention -- no neural arm was run, and "
        "R3/R6/R7 remain absent. Not a lifetime result: computing the metapath score is "
        "itself a scan over edges and is NOT charged against the query budget here, which "
        "is a real accounting gap and the next thing to close.")
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    doc = run()
    doc["verdict"] = verdict(doc)
    a.out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    v = doc["verdict"]
    print(json.dumps({k: v[k] for k in (
        "terminal", "worlds_where_metapath_beats_rarity",
        "worlds_where_metapath_is_worse_than_naive",
        "type_decoy_defeated_the_policy")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
