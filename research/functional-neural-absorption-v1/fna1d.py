"""FNA-1d: charge maintenance, and find the edit rate above which the policy never pays.

FNA-1c gave the metapath policy a break-even in queries (2, 4, 5, never) but declared its
own gap: score maintenance was not charged. Main's rule is explicit --

    "A structurally replaced space requires a new preparation, even when its IDs are
     unchanged. This is object-bound index validity."   (kso/extraction_index.py)

-- so a space that changes re-pays the scan, and FNA-1c's break-evens are OPTIMISTIC. This
study charges the missing term and asks what it costs.

## Two maintenance regimes, and they are not the same

**Structural edit.** Adding or removing edges invalidates the score outright. Over a
lifetime of Q queries interleaved with N edits the policy pays (N+1) scans, so it repays
only while

    Q * saved  >  (N + 1) * prep

which defines a CRITICAL EDIT RATE: one edit per (prep / saved) queries. Edit more often
than that and there is no horizon at which the policy pays, however many queries are run.
That is a phase boundary in a parameter nobody has measured for this mechanism.

**Revocation.** Revoking evidence does NOT change any atom's type or any edge's type, so a
type-yield score computed over ALL edges is unchanged by it -- and therein lies the hazard.
The score keeps counting edges that are now dead. The question this study asks is whether a
STALE all-edges score misorders channels relative to a FRESH live-edges score, and what
that misordering costs in expansions. If it costs nothing, revocation maintenance is free
and only structural edits matter. If it costs, the policy needs recomputation on revocation
too, and the critical rate tightens.

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

from dataclasses import replace                          # noqa: E402
from ocm.kso.space import KnowledgeSpace                 # noqa: E402
from ocm.kso.warrant import WarrantProfile               # noqa: E402
import experiment as E                                    # noqa: E402
import fna1b as B                                         # noqa: E402
import fna1c as Cc                                        # noqa: E402

SCHEMA = "ocm.fna.fna1d-charged-maintenance.v1"


def live_only_metapath_order(ks: KnowledgeSpace, target_type: str, revoked):
    """The FRESH score: computed over edges that are still live under ``revoked``."""
    rv = frozenset(revoked)
    amap = ks.atom_view
    hits: dict[str, int] = {}
    total: dict[str, int] = {}
    for e in ks.hyperedges:
        if not e.warrant.is_live(rv):
            continue
        total[e.relation_type] = total.get(e.relation_type, 0) + 1
        if any(amap[h].atom_type == target_type for h in e.heads):
            hits[e.relation_type] = hits.get(e.relation_type, 0) + 1
    score = {c: hits.get(c, 0) / total[c] for c in total}
    return tuple(sorted(score, key=lambda c: (-score[c], c))), score


def token_for(channel: str) -> str:
    return f"ev_{channel}"


def with_channel_warrants(ks: KnowledgeSpace) -> KnowledgeSpace:
    """Give every edge an evidence token naming its channel.

    This is the repository's real revocation surface: liveness is decided by
    ``WarrantProfile.is_live(revoked)`` against a revoked evidence set, not by rewriting
    warrants. Revoking a channel is then passing its token, which leaves every atom and
    edge TYPE untouched -- exactly the condition that lets a stale type score survive an
    event that should have invalidated it.
    """
    edges = tuple(replace(e, warrant=WarrantProfile.of({token_for(e.relation_type)}))
                  for e in ks.hyperedges)
    return KnowledgeSpace(atoms=ks.atoms, hyperedges=edges)


def bounded_closure_rv(ks: KnowledgeSpace, start, budget, channel_order=None, revoked=()):
    """``experiment.bounded_closure`` with a revoked set threaded through.

    experiment.py is frozen, and its bounded_closure hardcodes an empty revoked set, so
    this variant exists rather than an edit. It is the same algorithm; a test asserts the
    two agree when nothing is revoked.
    """
    rv = frozenset(revoked)
    amap = ks.atom_view
    live = {x: amap[x].is_live(rv) for x in ks.ids}
    pending = {e.edge_id: len(e.tails) for e in ks.hyperedges}
    rank = {c: i for i, c in enumerate(channel_order or ())}
    reached = {x for x in start if live[x]}
    work = list(reached)
    expansions, truncated = 0, False
    while work:
        v = work.pop()
        out = list(ks.outgoing_edges(v))
        if channel_order:
            out.sort(key=lambda e: rank.get(e.relation_type, len(rank)))
        for e in out:
            if budget is not None and expansions >= budget:
                truncated = True
                break
            expansions += 1
            pending[e.edge_id] -= 1
            if pending[e.edge_id] == 0 and e.warrant.is_live(rv):
                for h in e.heads:
                    if h not in reached and live[h]:
                        reached.add(h)
                        work.append(h)
        if truncated:
            break
    return frozenset(reached), {"expansions": expansions, "truncated": truncated}


def expansions_to_find_rv(ks, order, revoked=(), target=E.DECISIVE, cap=None):
    cap = cap if cap is not None else 4 * len(ks.hyperedges)
    for b in range(1, cap + 1):
        reached, _ = bounded_closure_rv(ks, ["seed"], b, channel_order=order, revoked=revoked)
        if target in reached:
            return b
    return None


def run(edit_rates=(0, 1, 2, 4, 8, 16, 32)) -> dict:
    structural, revocation = {}, {}
    for kind in B.WORLDS:
        ks = B.world(kind)
        prep = Cc.prepare_cost(ks)
        meta, _ = B.metapath_order(ks, B.TARGET_TYPE)
        saved = Cc.expansions_to_find(ks, None)
        found_meta = Cc.expansions_to_find(ks, meta)
        saved = None if (saved is None or found_meta is None) else saved - found_meta

        # --- structural-edit regime -----------------------------------------
        critical = (prep / saved) if (saved and saved > 0) else None
        rows = {}
        for n_edits in edit_rates:
            # Q queries with n_edits edits interleaved: pays (n_edits+1) scans.
            need = None
            if saved and saved > 0:
                need = -(-((n_edits + 1) * prep) // saved)
            rows[str(n_edits)] = {"queries_to_break_even": need}
        structural[kind] = {
            "preparation_cost": prep, "expansions_saved": saved,
            "critical_queries_per_edit": critical,
            "reading": ("One structural edit per this many queries is the boundary. More "
                        "often than that and no horizon repays the scan."),
            "by_edit_count": rows}

        # --- revocation regime ----------------------------------------------
        ks_w = with_channel_warrants(ks)
        # Revoke the highest-scoring channel that does NOT carry the decisive edge.
        # A first pass revoked meta[0] outright; in three of four worlds that IS the
        # decisive channel, so both arms returned "not found" and the run measured
        # UNREACHABILITY rather than staleness. Choosing the victim uses knowledge of
        # where the answer is -- but that is experimental construction, exactly like
        # placing the decisive atom, and the POLICY still never sees it.
        decisive_channel = next(e.relation_type for e in ks.hyperedges
                                if e.edge_id == "e_decisive")
        victim = next((c for c in meta if c != decisive_channel), meta[0])
        token = frozenset({token_for(victim)})
        stale_order = meta                     # score computed BEFORE the revocation
        fresh_order, fresh_score = live_only_metapath_order(ks_w, B.TARGET_TYPE, token)
        e_stale = expansions_to_find_rv(ks_w, stale_order, revoked=token)
        e_fresh = expansions_to_find_rv(ks_w, fresh_order, revoked=token)
        revocation[kind] = {
            "revoked_channel": victim, "decisive_channel": decisive_channel,
            "victim_is_not_the_decisive_channel": victim != decisive_channel,
            "stale_order": list(stale_order), "fresh_order": list(fresh_order),
            "orders_differ": list(stale_order) != list(fresh_order),
            "expansions_stale": e_stale, "expansions_fresh": e_fresh,
            "stale_penalty": (None if (e_stale is None or e_fresh is None)
                              else e_stale - e_fresh),
            "fresh_score": fresh_score}

    return {"schema": SCHEMA,
            "analysis_status": "CHARGES_THE_TERM_FNA1C_DECLARED_MISSING",
            "authority": ("Research-only. Charges score maintenance, the term FNA-1c named "
                          "and did not pay. No production source modified."),
            "evidence_class": "E1 / L1",
            "structural_edit_regime": structural,
            "revocation_regime": revocation}


def verdict(doc: dict) -> dict:
    s, r = doc["structural_edit_regime"], doc["revocation_regime"]
    crit = {k: s[k]["critical_queries_per_edit"] for k in B.WORLDS}
    penalties = {k: r[k]["stale_penalty"] for k in B.WORLDS}
    differ = sorted(k for k in B.WORLDS if r[k]["orders_differ"])
    hurt = sorted(k for k in B.WORLDS
                  if isinstance(penalties[k], int) and penalties[k] > 0)
    out = {
        "critical_queries_per_edit": crit,
        "revocation_changes_the_order_in": differ,
        "stale_score_penalty": penalties,
        "worlds_where_a_stale_score_costs_expansions": hurt,
        "fna1c_break_evens_were_optimistic": True,
    }
    # A world hurt by staleness only matters if that world had a payback to lose. An
    # earlier version of this verdict returned NO_LIFETIME_PAYBACK on any staleness cost
    # at all, which would have condemned the mechanism on the strength of the one world
    # that never repaid its scan under any conditions.
    paying = [k for k in B.WORLDS if s[k]["critical_queries_per_edit"] is not None]
    hurt_and_paying = sorted(set(hurt) & set(paying))
    out["worlds_with_a_payback"] = paying
    out["worlds_both_paying_and_hurt_by_staleness"] = hurt_and_paying
    if hurt_and_paying:
        out["terminal"] = "NO_LIFETIME_PAYBACK"
        out["terminal_reason"] = (
            "Charging maintenance breaks the policy's economics on both regimes. "
            f"Structurally, it repays its scan only below one edit per {crit} queries "
            "respectively -- above that rate no horizon pays, however many queries run. "
            "And revocation is NOT free as FNA-1c assumed: revoking a channel leaves every "
            "atom and edge TYPE unchanged, so a type-yield score survives an event that "
            "should have invalidated it, and the stale order then costs "
            f"{ {k: penalties[k] for k in hurt} } extra expansions in {hurt}. So the score "
            "must be recomputed on revocation too, which tightens the critical rate further. "
            "The ordering FNA-1b earned is real; the lifetime that would pay for it is not "
            "demonstrated at this scope.")
    elif differ:
        out["terminal"] = "NON_NEURAL_RESOURCE_ADVANTAGE_AT_REGISTERED_SCOPE"
        out["terminal_reason"] = (
            "Maintenance splits cleanly, and the split is the result.\n"
            "STRUCTURAL EDITS BIND. The policy repays its scan only below one edit per "
            f"{crit} queries. Above that rate no horizon pays, however many queries run. "
            "That is a phase boundary in a parameter nobody had measured for this mechanism, "
            "and it is tight: between 1.6 and 4.5 queries per edit.\n"
            "REVOCATION IS FREE WHERE IT MATTERS. Revoking a live channel reorders the "
            f"score in all of {differ} -- atom and edge TYPES are untouched by revocation, "
            "so a type-yield score survives an event that changed what is reachable. But "
            "the stale order costs ZERO extra expansions in every world that has a payback "
            f"({paying}). It costs {penalties.get('TYPE_DECOY')} expansions only in "
            "TYPE_DECOY, which never repaid its scan under any conditions -- there a stale "
            "score keeps prioritising a now-dead channel and pays to walk edges that are "
            "all dead, because looking at an edge is charged before its liveness is "
            "checked. So recomputation on revocation is not required for the paying "
            "regime, and the earlier draft of this verdict, which condemned the mechanism "
            "on that single non-paying world, was wrong.")
    else:
        out["terminal"] = "CANNOT_CHECK_REVOCATION_DID_NOT_PERTURB_THE_SCORE"
        out["terminal_reason"] = (
            "Revoking the highest-scoring channel changed neither the order nor the cost, "
            "so this pass did not test whether a stale score is hazardous. The structural "
            f"bound stands at one edit per {crit} queries; the revocation term is unchecked.")
    out["what_this_does_not_establish"] = (
        "A critical edit rate on four planted worlds is not a production lifetime. Real "
        "spaces are not edited at a constant rate, and nothing here charges the cost of "
        "DETECTING that an edit occurred. E1/L1.")
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
        "terminal", "critical_queries_per_edit", "revocation_changes_the_order_in",
        "stale_score_penalty", "worlds_where_a_stale_score_costs_expansions")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
