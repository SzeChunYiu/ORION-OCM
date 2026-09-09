"""E4 lever (engineering-chain pass, post-freeze): demand-driven counting closure.

Stage attribution (ONE stage): the per-query counting-closure work. The frozen base
closure re-scans the whole qedge list to a global fixpoint and pre-evaluates liveness
for EVERY block; on this population (482 blocks over 488 atoms) that schedule dominates
the Q2/Q5 object cost while the partition is near-singleton.

Mechanism lever (real, fully charged):
  * work-list enabling -- a quotient edge can newly enable only when one of its TAIL
    blocks' counts grows, so qedges are examined from a tail-incidence index seeded at
    the seed block, each count-growth event once, instead of every pass over all qedges;
  * lazy block liveness -- a block's warrant is evaluated on first need and memoized
    per query, instead of eagerly for the whole partition.

Decision equivalence (proved, and asserted per task by the pass runner): the counting
closure is a monotone update system, so sequential iteration to fixpoint computes its
least fixpoint independent of visit order. At that fixpoint every reachable block's
count has saturated to its block size (any enabled qedge pumps +k per pass, capped only
by size), so enabling on tail multiset {B: k} is equivalent to reachable(B) and
len(B) >= k; fire-once reachability over that enabling rule yields the same counted-
positive set, hence the same refuted flag and the same decisions, with only the charged
schedule changed (the eliminated re-scans and eager checks are exactly the redundant
work the lever removes). Firings, warrant checks and examinations are still charged one
object each -- the accounting rule is the frozen arm's own formula.

Python 3.8-compatible syntax.
"""
from __future__ import annotations

from collections import deque
from typing import Dict, FrozenSet, List

from arms import Q2Quotient, Q5Composed
from quotient import Quotient


class WorklistView(object):
    """Ephemeral per-query view wrapper: same counting semantics, demand-driven schedule."""

    def __init__(self, inner):
        self._inner = inner

    def __getattr__(self, name):
        return getattr(self._inner, name)

    def counting_closure(self, seed: str, revoked: FrozenSet, target: str,
                         early_stop: bool = False) -> dict:
        view = self._inner
        m = {"quotient_expansions": 0, "quotient_firings": 0,
             "block_warrant_checks": 0, "qedge_warrant_checks": 0, "early_stopped": False}
        live_cache: Dict[int, bool] = {}

        def live(b: int) -> bool:
            if b not in live_cache:
                m["block_warrant_checks"] += 1
                live_cache[b] = view.parent.block_warrants[b].is_live(revoked)
            return live_cache[b]

        counts: Dict[int, int] = {b: 0 for b in view.blocks}
        sb, tb = view.partition[seed], view.partition[target]
        tails_of: Dict[int, List] = {}
        for q in view.qedges:
            for b, _ in q.tails:
                tails_of.setdefault(b, []).append(q)
        if not live(sb):
            return {"counts": counts, "m": m, "refuted": True, "fired": [],
                    "parent_edge": {}}
        counts[sb] = 1
        parent_edge: Dict[int, tuple] = {}
        fired_log: List[int] = []
        fired: Dict[int, bool] = {}
        dq = deque([sb])
        while dq:
            b = dq.popleft()
            for q in tails_of.get(b, ()):
                if fired.get(q.qid):
                    continue
                m["quotient_expansions"] += 1
                m["qedge_warrant_checks"] += 1
                if not q.warrant.is_live(revoked):
                    continue
                if any((not live(bt)) for bt, _ in q.tails):
                    continue  # dead tail block: a dead tail atom can never be reached
                if not any(live(hb) for hb, _ in q.heads):
                    continue  # no admissible head: firing would admit nothing
                if any(counts.get(bt, 0) < 1 for bt, _ in q.tails):
                    continue  # some tail block not yet counted reached
                if any(len(view.blocks[bt]) < k for bt, k in q.tails):
                    continue  # multiplicity unsatisfiable even at saturation (mirrors the cap)
                fired[q.qid] = True
                fired_log.append(q.qid)
                m["quotient_firings"] += 1
                for hb, k in q.heads:
                    if not live(hb):
                        continue
                    if counts.get(hb, 0) < 1:
                        counts[hb] = 1
                        if hb not in parent_edge:
                            parent_edge[hb] = (q.qid,)
                        dq.append(hb)
                if early_stop and counts.get(tb, 0) >= 1:
                    m["early_stopped"] = True
                    break
            if early_stop and counts.get(tb, 0) >= 1:
                break
        refuted = counts.get(tb, 0) == 0
        return {"counts": counts, "m": m, "refuted": refuted, "fired": fired_log,
                "parent_edge": parent_edge}


class WorklistQuotient(Quotient):
    """Quotient whose per-query views use the E4 demand-driven counting closure."""

    def split_singletons(self, atoms):
        return WorklistView(Quotient.split_singletons(self, atoms))


class Q2E4(Q2Quotient):
    """Q2 with the E4 lever (work-list enabling + lazy liveness), costs fully charged."""

    def __init__(self):
        Q2Quotient.__init__(self)
        self.name = "Q2_QUOTIENT_E4"

    def on_field(self, ks):
        self.ks = ks
        self.q = WorklistQuotient(ks)
        self.rebuilds += 1
        self._charge_build(self.q)

    def on_admission(self, ks, new_edges):
        # rebuild path: WorklistQuotient.rebuild reinitializes in place (type preserved)
        Q2Quotient.on_admission(self, ks, new_edges)
        assert isinstance(self.q, WorklistQuotient)


class Q5E4(Q5Composed):
    """Q5 with the same E4 lever on its quotient stage."""

    def __init__(self):
        Q5Composed.__init__(self)
        self.name = "Q5_COMPOSED_E4"

    def on_field(self, ks):
        self.ks = ks
        self.q = WorklistQuotient(ks)
        self._charge_quotient_build()
        if self.use_probe:
            from probing import ProbeField
            self.pf = ProbeField(ks)
            self.lifetime["build_work"] += len(ks.ids) + \
                sum(len(ks.outgoing_edges(v)) for v in ks.ids)

    def on_admission(self, ks, new_edges):
        Q5Composed.on_admission(self, ks, new_edges)
        assert isinstance(self.q, WorklistQuotient)
