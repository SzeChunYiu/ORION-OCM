"""FNA-1: does typed multi-channel retrieval add anything the exact closure lacks?

#214 gives non-neural mechanisms first refusal against attention. Phase A found that
main already implements R0 (dense scan), R1 (exact indexed retrieval), R2 (warm sparse
support) and R4 (sparse diffusion), with a 17-coordinate resource vector that charges
index build separately from query work. Phase B found that #214 section 3 mis-attributes
the typed-channel idea to multi-head attention: the literature reads multi-head as an
ENSEMBLE OF KERNEL ESTIMATORS whose function is variance reduction (2605.20271), and an
exact closure has no estimator variance to reduce. Typed channels belong instead to
heterogeneous information networks and metapath retrieval.

So this study does NOT rebuild the exact ladder and does NOT implement attention. It runs
main's own closure, restricted to relation-type channels, and asks two questions.

Q1 (unbounded). Can channel-restricted retrieval reach task-decisive state that the
    undifferentiated exact closure misses?

Q2 (bounded). Under a truncation budget, does channel ORDER change what is found -- and
    can a NON-ORACLE, parent-owned ordering policy recover a decisive item that a naive
    order misses?

Q1 is expected to be structurally impossible to win; Proposition 3 below states why, and
the run checks the proposition rather than assuming it. Q2 is where the mechanism can
earn something, and the ordering policy under test is rarity-first -- the same selectivity
heuristic ``runtime/operator_index.py`` already applies to operator inputs. Any positive
is therefore attributable to the classical IR parent, not to a bespoke OCM mechanism.

An ORACLE arm is included as an upper bound and is labelled ORACLE everywhere. It is not
achievable and is never reported as a result.

Research-only. No production source is modified, no model is trained, no router exists.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "src"))

from ocm.kso.space import KnowledgeSpace, Atom, Hyperedge          # noqa: E402
from ocm.kso.navigation import gated_closure                        # noqa: E402
from ocm.kso.extraction import reacting_subgraph_from_surprise      # noqa: E402
from ocm.kso.extraction_index import ExtractionIndex                # noqa: E402
from ocm.kso.extraction_indexed import (                            # noqa: E402
    reacting_subgraph_from_support_indexed)

SCHEMA = "ocm.fna.fna1-typed-channel-retrieval.v1"

PROPOSITION_3 = """Proposition 3 (typed channels cannot add reach to an exact closure).

Let E be the edge set of a space and E_T = {e in E : relation_type(e) in T} for a channel
subset T. Let C(E, s) be the gated closure from seed s over edge set E.

(1) MONOTONICITY. gated_closure's worklist admits a head only via an edge all of whose
    tails are reached and whose warrant is live. Removing edges can only remove admissions;
    it never creates one. So E_T subset-of E implies C(E_T, s) subset-of C(E, s), by
    induction on the worklist order.

(2) Hence for ANY channel subset T, and any channel-selection policy however clever,
    the reached set is a SUBSET of the undifferentiated closure. A multi-channel retrieval
    mechanism cannot recover task-decisive state that the exact closure misses, because
    the exact closure misses nothing that any subset reaches.

(3) Therefore the only advantage available to typed channels over an UNBOUNDED exact
    closure is WORK, never REACH. A study reporting a capability gain there has a defect.

The escape, and it is the interesting half: (2) assumes the closure runs to completion.
Under a truncation budget B, the closure is cut off, and then which edges are expanded
FIRST determines what is inside the budget. Channel order becomes capability-relevant
exactly when B is binding. So the registered claim of this study is conditional: typed
channels are worthless for reach when the budget is slack, and can matter when it binds.
Q2 measures where that boundary is, using a non-oracle rarity-first policy.
"""

# ---------------------------------------------------------------------------
# Planted world. Frozen construction; see PROTOCOL.md for the freeze.
# ---------------------------------------------------------------------------

#: The decisive item hangs off a RARE channel; distractors hang off common ones. This is
#: the shape #214 section 4 asks for -- "one rare decisive item" and "misleading similar
#: items" -- and it is adversarial to a naive expansion order rather than to the parent.
COMMON_CHANNELS = ("SUPPORT", "DEPENDENCE")
RARE_CHANNEL = "SCALE_CHANGE"
DECISIVE = "decisive"


def planted_world(n_distractors: int = 60, fanout: int = 3):
    """A seed, many distractors on common channels, one decisive atom on a rare channel."""
    atoms = [Atom(atom_id="seed", atom_type="query_seed"),
             Atom(atom_id=DECISIVE, atom_type="claim")]
    edges = []
    for i in range(n_distractors):
        atoms.append(Atom(atom_id=f"d{i}", atom_type="claim"))
    # Distractor fan-out from the seed on common channels only.
    for i in range(n_distractors):
        edges.append(Hyperedge(edge_id=f"e_d{i}", tails=("seed",), heads=(f"d{i}",),
                               relation_type=COMMON_CHANNELS[i % len(COMMON_CHANNELS)]))
    # Second-hop distractor chains, still on common channels: these consume budget.
    for i in range(0, n_distractors, fanout):
        for j in range(1, fanout):
            if i + j < n_distractors:
                edges.append(Hyperedge(edge_id=f"e_c{i}_{j}", tails=(f"d{i}",),
                                       heads=(f"d{i + j}",),
                                       relation_type=COMMON_CHANNELS[j % len(COMMON_CHANNELS)]))
    # The single decisive edge, on the rare channel.
    edges.append(Hyperedge(edge_id="e_decisive", tails=("seed",), heads=(DECISIVE,),
                           relation_type=RARE_CHANNEL))
    return KnowledgeSpace(atoms=tuple(atoms), hyperedges=tuple(edges))


def restrict(ks: KnowledgeSpace, channels) -> KnowledgeSpace:
    """The same space with only the named relation channels. Production closure is reused."""
    keep = frozenset(channels)
    return KnowledgeSpace(atoms=ks.atoms,
                          hyperedges=tuple(e for e in ks.hyperedges if e.relation_type in keep))


# ---------------------------------------------------------------------------
# Bounded closure. Research-side, and validated against production at slack budget.
# ---------------------------------------------------------------------------

def bounded_closure(ks: KnowledgeSpace, start, budget: int | None, channel_order=None):
    """gated_closure with an expansion budget and a channel priority.

    Mirrors ``ocm.kso.navigation.gated_closure`` exactly -- live atoms, live edges,
    conjunctive pending-tail counters -- and adds two things: expansions are capped at
    ``budget``, and the outgoing edges of a node are visited in ``channel_order``.

    With ``budget=None`` and no ordering this MUST equal the production closure, and the
    study asserts that rather than trusting it. Without that check a bounded arm could
    differ from the parent for reasons unrelated to the budget.
    """
    amap = ks.atom_view
    live = {x: amap[x].is_live(frozenset()) for x in ks.ids}
    pending = {e.edge_id: len(e.tails) for e in ks.hyperedges}
    rank = {c: i for i, c in enumerate(channel_order or ())}
    reached = {x for x in start if live[x]}
    work = list(reached)
    expansions = 0
    truncated = False
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
            if pending[e.edge_id] == 0 and e.warrant.is_live(frozenset()):
                for h in e.heads:
                    if h not in reached and live[h]:
                        reached.add(h)
                        work.append(h)
        if truncated:
            break
    return frozenset(reached), {"expansions": expansions, "truncated": truncated}


def channel_rarity(ks: KnowledgeSpace):
    """Channels ordered rarest-first -- the selectivity heuristic operator_index.py uses.

    This is a NON-ORACLE policy: it reads only edge-type counts, which are a property of
    the space, not of the task or its answer.
    """
    counts: dict[str, int] = {}
    for e in ks.hyperedges:
        counts[e.relation_type] = counts.get(e.relation_type, 0) + 1
    return tuple(sorted(counts, key=lambda c: (counts[c], c))), counts


# ---------------------------------------------------------------------------
# Arms
# ---------------------------------------------------------------------------

def run(n_distractors: int = 60, budgets=(4, 8, 16, 32, 64, 128)) -> dict:
    ks = planted_world(n_distractors)
    rho = {a.atom_id: 1.0 for a in ks.atoms}
    seed_vec = [F(1) if a.atom_id == "seed" else F(0) for a in ks.atoms]
    order, counts = channel_rarity(ks)
    all_channels = tuple(sorted(counts))

    # --- Q1: unbounded arms, on production code ---------------------------------
    r0 = reacting_subgraph_from_surprise(ks, rho, seed_vec)
    index = ExtractionIndex(ks)
    r1, work = reacting_subgraph_from_support_indexed(
        ks, rho, ["seed"], index=index, with_work=True)
    prod_closure = gated_closure(ks, ["seed"])

    unbounded = {
        "R0_DENSE": {"reached": len(r0.atoms), "found_decisive": DECISIVE in r0.atoms},
        "R1_INDEXED": {"reached": len(r1.atoms), "found_decisive": DECISIVE in r1.atoms,
                       "query_work": work.as_dict(),
                       "build_work": dict(index.build_work)},
    }
    channel_arms = {}
    for ch in all_channels:
        sub = restrict(ks, [ch])
        reached = gated_closure(sub, ["seed"])
        channel_arms[f"R5_CHANNEL_{ch}"] = {
            "reached": len(reached), "found_decisive": DECISIVE in reached,
            "subset_of_full_closure": reached <= prod_closure}
    sub_common = restrict(ks, COMMON_CHANNELS)
    reached_common = gated_closure(sub_common, ["seed"])
    channel_arms["R5_COMMON_CHANNELS_ONLY"] = {
        "reached": len(reached_common), "found_decisive": DECISIVE in reached_common,
        "subset_of_full_closure": reached_common <= prod_closure}
    union = gated_closure(restrict(ks, all_channels), ["seed"])
    channel_arms["R5_UNION_ALL_CHANNELS"] = {
        "reached": len(union), "found_decisive": DECISIVE in union,
        "equals_undifferentiated_closure": union == prod_closure}

    # --- Q2: bounded arms -------------------------------------------------------
    slack, _ = bounded_closure(ks, ["seed"], None)
    bounded = {}
    for b in budgets:
        naive, wn = bounded_closure(ks, ["seed"], b, channel_order=None)
        rarity, wr = bounded_closure(ks, ["seed"], b, channel_order=order)
        oracle, wo = bounded_closure(ks, ["seed"], b, channel_order=(RARE_CHANNEL,) + COMMON_CHANNELS)
        bounded[str(b)] = {
            "budget_binds": wn["truncated"],
            "BOUNDED_NAIVE": {"reached": len(naive), "found_decisive": DECISIVE in naive, **wn},
            "BOUNDED_RARITY_FIRST": {"reached": len(rarity), "found_decisive": DECISIVE in rarity, **wr},
            "ORACLE_DECISIVE_CHANNEL_FIRST": {
                "reached": len(oracle), "found_decisive": DECISIVE in oracle, **wo,
                "authority": "ORACLE UPPER BOUND, NOT ACHIEVABLE, NEVER A RESULT"},
        }
    return {
        "schema": SCHEMA,
        "authority": ("Research-only. Runs main's own gated closure and indexed extraction. "
                      "No production source modified, no model trained, no router implemented. "
                      "#71 remains LEARNED_ROUTER_NOT_YET_AUTHORIZED."),
        "evidence_class": "E1 / L1 (planted world, single population, one author)",
        "proposition_3": PROPOSITION_3,
        "world": {"atoms": len(ks.atoms), "edges": len(ks.hyperedges),
                  "channel_counts": counts, "rarity_order": list(order),
                  "rare_channel": RARE_CHANNEL, "decisive_atom": DECISIVE,
                  "n_distractors": n_distractors},
        "harness_validation": {
            "bounded_closure_at_slack_budget_equals_production": slack == prod_closure,
            "why": ("The bounded arm is research-side code. If it disagreed with production "
                    "at an unbinding budget, every bounded result would be measuring the "
                    "reimplementation rather than the budget."),
        },
        "q1_unbounded": {**unbounded, **channel_arms},
        "q2_bounded": bounded,
    }


def verdict(doc: dict) -> dict:
    q1, q2 = doc["q1_unbounded"], doc["q2_bounded"]
    channels = {k: v for k, v in q1.items() if k.startswith("R5_CHANNEL_")}
    every_subset = all(v["subset_of_full_closure"] for v in channels.values())
    union_equals = q1["R5_UNION_ALL_CHANNELS"]["equals_undifferentiated_closure"]
    any_channel_added_reach = any(
        v["reached"] > q1["R1_INDEXED"]["reached"] for v in channels.values())

    binding = {b: r for b, r in q2.items() if r["budget_binds"]}
    rarity_wins = sorted(
        b for b, r in binding.items()
        if r["BOUNDED_RARITY_FIRST"]["found_decisive"] and not r["BOUNDED_NAIVE"]["found_decisive"])
    both_find = sorted(b for b, r in binding.items()
                       if r["BOUNDED_RARITY_FIRST"]["found_decisive"]
                       and r["BOUNDED_NAIVE"]["found_decisive"])
    out = {
        "proposition_3_holds_in_run": every_subset and not any_channel_added_reach,
        "every_channel_subset_is_a_subset_of_the_full_closure": every_subset,
        "union_of_channels_equals_undifferentiated_closure": union_equals,
        "any_channel_arm_added_reach": any_channel_added_reach,
        "harness_agrees_with_production": doc["harness_validation"][
            "bounded_closure_at_slack_budget_equals_production"],
        "budgets_where_budget_binds": sorted(binding),
        "budgets_where_rarity_first_finds_decisive_and_naive_does_not": rarity_wins,
        "budgets_where_both_find_it": both_find,
    }
    if not out["harness_agrees_with_production"]:
        out["terminal"] = "CANNOT_CHECK_BOUNDED_HARNESS_DISAGREES_WITH_PRODUCTION_CLOSURE"
        out["terminal_reason"] = (
            "The research-side bounded closure did not reproduce the production closure at "
            "an unbinding budget, so no bounded number is interpretable.")
    elif not out["proposition_3_holds_in_run"]:
        out["terminal"] = "CANNOT_CHECK_PROPOSITION_3_VIOLATED_HARNESS_DEFECT"
        out["terminal_reason"] = (
            "A channel-restricted closure reached something the undifferentiated closure "
            "did not. That is impossible by monotonicity, so the harness is defective and "
            "nothing downstream is interpretable.")
    elif rarity_wins:
        out["terminal"] = "NON_NEURAL_RESOURCE_ADVANTAGE_AT_REGISTERED_SCOPE"
        out["terminal_reason"] = (
            "UNBOUNDED: typed channels add NOTHING. Every channel subset is a subset of the "
            "exact closure, the union reproduces it exactly, and no channel arm reached more "
            "than the indexed parent. Proposition 3 holds and the reach question is closed "
            "negatively, structurally, for any channel policy whatsoever. "
            "BOUNDED: when the budget binds, channel ORDER decides what is inside it. A "
            f"rarity-first policy recovers the decisive item at budgets {rarity_wins} where a "
            "naive order does not. That policy is NOT an oracle -- it reads only edge-type "
            "counts, a property of the space and not of the task -- and it is the same "
            "selectivity heuristic runtime/operator_index.py already applies to operator "
            "inputs. So the advantage is owned by the classical IR parent, not by a bespoke "
            "OCM mechanism and not by multi-head attention, whose function the literature "
            "gives as ensemble variance reduction that an exact closure has no need of.")
    else:
        out["terminal"] = "PARENT_SUFFICIENT_FOR_TYPED_CHANNEL_RETRIEVAL"
        out["terminal_reason"] = (
            "Typed channels added no reach when unbounded (Proposition 3) and no non-oracle "
            "ordering policy changed what was found under any binding budget tested. The "
            "undifferentiated exact closure is sufficient at this scope.")
    out["what_this_does_not_establish"] = (
        "Not a claim about attention, Transformers or any neural system: no neural arm was "
        "run, and R3/R6/R7 remain absent. Not a lifetime result -- no acquisition, "
        "maintenance or revocation cost is amortised here. One planted world, one author, "
        "one population: E1/L1. The bounded advantage is contingent on a budget that binds "
        "and on the decisive item sitting on a rare channel; a decisive item on a COMMON "
        "channel would reverse the rarity policy's advantage, which is the obvious next "
        "hostile and is not run here.")
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--distractors", type=int, default=60)
    a = p.parse_args()
    doc = run(a.distractors)
    doc["verdict"] = verdict(doc)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    v = doc["verdict"]
    print(json.dumps({k: v[k] for k in (
        "terminal", "proposition_3_holds_in_run", "harness_agrees_with_production",
        "union_of_channels_equals_undifferentiated_closure",
        "budgets_where_budget_binds",
        "budgets_where_rarity_first_finds_decisive_and_naive_does_not",
        "budgets_where_both_find_it")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
