"""FNA-1c: charge the metapath policy for its own preparation, then find break-even.

FNA-1b and its v2 hostile bounded the policy's capability on both sides. Both left the
same accounting gap open, and both said so in their own receipts:

    "The metapath score is computed by a scan over all edges and is NOT charged against
     the query budget in any arm here."

#214 section 6 names this risk exactly -- "explicit retrieval may move, not remove,
information/storage cost" -- and Phase A found main already solves it structurally:
``ExtractionIndex`` records ``build_work`` SEPARATELY from query work, with object-bound
validity, so preparation is never free and never double-charged.

This study adopts that same discipline rather than inventing an accounting scheme.

    COLD  a single query pays the whole scan: charge = |E| + expansions
    WARM  the score is prepared once per immutable space and reused: the scan is a build
          cost amortised over Q queries, charge_per_query = |E|/Q + expansions

The registered question is not "does metapath win" -- FNA-1b already bounded that. It is:

    at what number of queries does a metapath-ordered search repay the scan that
    produces its ordering, against a naive order that prepares nothing?

A policy that never repays it is NO_LIFETIME_PAYBACK regardless of how well it orders.

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

import experiment as E     # noqa: E402
import fna1b as B          # noqa: E402

SCHEMA = "ocm.fna.fna1c-charged-metapath.v1"

#: One edge read during the scoring scan. Same unit as one expansion, so the two are
#: commensurable without a conversion factor that could be tuned.
SCAN_COST_PER_EDGE = 1


def prepare_cost(ks) -> int:
    """Exactly what metapath_order reads: every edge once, plus its heads."""
    return SCAN_COST_PER_EDGE * len(ks.hyperedges)


def expansions_to_find(ks, order, target=E.DECISIVE, cap=None) -> int | None:
    """Smallest expansion count at which this order reaches the decisive atom."""
    cap = cap if cap is not None else 4 * len(ks.hyperedges)
    for b in range(1, cap + 1):
        reached, _ = E.bounded_closure(ks, ["seed"], b, channel_order=order)
        if target in reached:
            return b
    return None


def run(queries=(1, 2, 4, 8, 16, 32, 64, 128, 256)) -> dict:
    out = {}
    for kind in B.WORLDS:
        ks = B.world(kind)
        meta, _score = B.metapath_order(ks, B.TARGET_TYPE)
        rarity, _counts = E.channel_rarity(ks)
        prep = prepare_cost(ks)
        e_naive = expansions_to_find(ks, None)
        e_meta = expansions_to_find(ks, meta)
        e_rar = expansions_to_find(ks, rarity)
        saved = None if (e_naive is None or e_meta is None) else e_naive - e_meta
        break_even = None
        if saved and saved > 0:
            # Q * saved > prep  =>  Q > prep / saved
            break_even = -(-prep // saved)          # ceiling division
        per_query = {}
        for q in queries:
            cold_or_warm = prep / q
            per_query[str(q)] = {
                "metapath_charge_per_query": (e_meta + cold_or_warm) if e_meta else None,
                "naive_charge_per_query": e_naive,
                "metapath_pays": bool(e_meta is not None and e_naive is not None
                                      and (e_meta + cold_or_warm) < e_naive),
            }
        out[kind] = {
            "edges": len(ks.hyperedges), "preparation_cost": prep,
            "expansions_to_find": {"NAIVE": e_naive, "RARITY_FIRST": e_rar,
                                   "METAPATH_TYPE_YIELD": e_meta},
            "expansions_saved_vs_naive": saved,
            "break_even_queries": break_even,
            "per_query": per_query,
        }
    return {"schema": SCHEMA,
            "analysis_status": "CHARGED_ACCOUNTING_FOR_FNA1B_POLICY",
            "authority": ("Research-only. Adopts main's ExtractionIndex discipline -- build "
                          "work separated from query work -- rather than inventing an "
                          "accounting scheme. No production source modified."),
            "evidence_class": "E1 / L1",
            "charges": {"scan_cost_per_edge": SCAN_COST_PER_EDGE,
                        "note": ("One edge read is charged the same as one expansion, so the "
                                 "two are commensurable without a conversion factor that "
                                 "could be tuned to produce a payback.")},
            "worlds": out}


def verdict(doc: dict) -> dict:
    w = doc["worlds"]
    pays_cold = sorted(k for k in B.WORLDS if w[k]["per_query"]["1"]["metapath_pays"])
    ever_pays = sorted(k for k in B.WORLDS if w[k]["break_even_queries"] is not None)
    never = sorted(k for k in B.WORLDS if w[k]["break_even_queries"] is None)
    out = {
        "worlds_where_metapath_pays_on_a_SINGLE_query": pays_cold,
        "worlds_with_a_finite_break_even": ever_pays,
        "worlds_that_never_repay_the_scan": never,
        "break_even_queries": {k: w[k]["break_even_queries"] for k in B.WORLDS},
        "expansions_saved": {k: w[k]["expansions_saved_vs_naive"] for k in B.WORLDS},
        "preparation_cost": {k: w[k]["preparation_cost"] for k in B.WORLDS},
    }
    if not pays_cold and ever_pays:
        out["terminal"] = "NON_NEURAL_RESOURCE_ADVANTAGE_AT_REGISTERED_SCOPE"
        out["terminal_reason"] = (
            "Charged honestly, the policy NEVER pays on a single query in any world: the "
            "scan that produces the ordering costs more than the ordering saves, which is "
            "exactly the 'explicit retrieval moves rather than removes cost' risk #214 "
            "section 6 names. It pays only as an AMORTISED preparation, and the break-even "
            f"is now a number rather than a hope: {out['break_even_queries']}. That is the "
            "same shape main already uses -- ExtractionIndex charges build_work separately "
            "from query work with object-bound validity -- so the mechanism inherits an "
            "existing discipline instead of needing a new one. Where the break-even is "
            "None the scan is never repaid at any horizon and the honest reading for that "
            "world is NO_LIFETIME_PAYBACK.")
    elif pays_cold:
        out["terminal"] = "CANNOT_CHECK_SINGLE_QUERY_PAYBACK_IMPLIES_UNCHARGED_PREPARATION"
        out["terminal_reason"] = (
            "A policy that repays a full-edge scan within one query has almost certainly "
            "not been charged for it correctly. This is flagged as an accounting defect "
            "rather than reported as a strong result.")
    else:
        out["terminal"] = "NO_LIFETIME_PAYBACK"
        out["terminal_reason"] = (
            "No world produced a finite break-even: the metapath scan is never repaid by "
            "the expansions its ordering saves, at any number of queries. The ordering is "
            "real (FNA-1b) and worthless once its own preparation is charged.")
    out["what_this_does_not_establish"] = (
        "A break-even in QUERIES is not a lifetime result. Nothing here charges score "
        "maintenance under revocation or structural edit, and main's own rule is that a "
        "structurally replaced space needs fresh preparation -- so a space that changes "
        "often would re-pay the scan repeatedly and the break-even above would be optimistic. "
        "That is the next term to charge, and it is not charged here. E1/L1: four planted "
        "worlds, one author.")
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
        "terminal", "worlds_where_metapath_pays_on_a_SINGLE_query",
        "break_even_queries", "expansions_saved", "preparation_cost")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
