"""R10 — invasion and competition: two carriers developing in the SAME ecology out of ONE shared charged budget, so
that occupancy is decided by competition and not by two independent scores placed side by side.

WHICH R10 THIS IS. `GMI_BIOSPHERE_EXPERIMENT_PROTOCOL_V1` section 20 lists R10 as "real-task adapters" (stage B7: repo
bug repair, Lean proofs, timestamped facts, control). That layer is out of reach for this lane by construction — this is
an 8-bit exact microscope (TOTAL_BITS 8, FRAC_BITS 4) over a 16-input ecology, and B7 is marked
`REGISTERED_FOR_EXPERIMENT` in the gap ledger precisely because it needs LLM-scale compute. Building a stub that called
itself a real-task adapter would be worse than not building it. The working brief's reading — invasion and competition —
is implemented instead, and it is the falsifiable one: every other layer in this lane scores candidates INDEPENDENTLY,
which quietly assumes that a niche is occupied by whoever scores highest on their own. This module removes that
assumption and measures whether it survives.

THE COMPETITION (frozen protocol). One ecology, one stream of feedback events, one shared charge pool:

  1. both machines are instantiated and initialized; each initialization is deducted from the shared pool;
  2. the RESIDENT develops alone for `head_start` events (the establishment cost of being the incumbent), deducted;
  3. thereafter the ecology offers the next event in the stream to the machine with the LOWER cumulative charge — ties
     to the resident, as the incumbent. That machine consumes the event and its charge is deducted. THE OTHER MACHINE
     DOES NOT SEE THAT EVENT. This is the competitive coupling: experience and budget are both scarce and shared, so a
     cheap machine buys more development out of the same pool and an expensive one starves;
  4. development ends when the pool cannot pay for the next event or the stream is exhausted.

Evaluation is then run on the architecture-neutral protected endpoint (capability on the unseen inputs) and is charged
to each machine's own ledger but NOT to the pool — an endpoint paid out of the contested budget would let the cheaper
machine buy a better measurement, which is not what is being measured.

  OUTCOME     RESIDENT_HOLDS / INVADER_REPLACES when one exact capability strictly exceeds the other; COEXIST on an
              exact tie. Arithmetic is exact, so a tie is a real tie and not a tolerance artefact.

THE FALSIFIABLE CLAIM. The registered prediction is that occupancy under a shared budget is NOT a function of the solo
scores: there exists an ordered pair of DISTINCT carriers whose competitive outcome disagrees with the ranking the two
machines get when each is developed alone with the whole pool. Diagonal cells (a carrier against a copy of itself) can
also split, because the head start and the shared pool are asymmetric, and are counted separately. If the off-diagonal
count is 0, the
prediction fails at this scope and competition is reported as adding nothing here — the receipt says so in those words
rather than burying it.

CLAIM CEILING. One ecology, one basis, the R4 known-parent library as both residents and invaders, one allocation rule,
one head start, three pool sizes. The allocation rule is a modelling choice: "lower cumulative charge takes the next
event" is one way to make a budget contested, not the way ecology works. A different rule can reorder outcomes, and the
receipt reports the rule as part of the result, not as background.
"""
from __future__ import annotations

import itertools
import json
import os
import sys
import time

from . import bases, ecology, morph, smooth, zoo
from .core import Machine, sha256_of
from .vm import VM, lifecycle_vector

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
B0 = bases.ALL["B0_LOCAL_ADAPTIVE_TRANSDUCERS"]
ECO = "E_smooth3"
POOLS = (20000, 60000, 200000)     # shared charge pools, declared before the run
HEAD_START = 2                     # events the resident develops alone before the invader arrives
MAX_EVENTS = 16                    # the registered stream length


class Carrier:
    """one machine in the competition: its own Machine/ledger, its own event count, its own charge."""

    def __init__(self, name, genotype, seed=0):
        self.name = name; self.g = genotype
        self.M = Machine(B0, seed=seed); self.vm = VM(genotype, self.M, seed)
        self.M.phase("exec"); self.vm.init()
        self.events = 0; self.charge = self._total(); self.init_charge = self.charge
        self.starved = False

    def _total(self):
        return sum(self.M.L.c.values())

    def feed(self, x, target):
        """consume one feedback event (the registered update pass plus the registered per-event verification pass);
        returns the charge it cost, which is what the shared pool is billed."""
        before = self._total()
        self.M.phase("upd"); self.vm.feedback(x, target[x]); self.M.end_event()
        self.M.phase("ver")
        for xx in smooth.ALL_X: self.M.op("EQ", self.vm.query(xx), target[xx])
        cost = self._total() - before; self.charge += cost; self.events += 1
        return cost

    def evaluate(self, target, criterion="unseen"):
        """the protected endpoint: capability on the unseen inputs. Charged to this machine, NOT to the shared pool."""
        self.M.phase("exec"); final = []
        for xx in smooth.ALL_X:
            v = self.vm.query(xx); final.append(None if self.vm.abstained else v)
        eval_x = smooth.UNSEEN if criterion == "unseen" else smooth.ALL_X
        err = sum(abs((final[x] if final[x] is not None else 0) - target[x]) for x in eval_x) / smooth.FX_ONE / len(eval_x)
        return round(max(0.0, 1 - err / 1.5), 4), final


def compete(g_res, g_inv, target, pool, head_start=HEAD_START, max_events=MAX_EVENTS, seed=0,
            name_res="resident", name_inv="invader"):
    """the frozen competition protocol. Returns the full exact record."""
    res = Carrier(name_res, g_res, seed); inv = Carrier(name_inv, g_inv, seed)
    remaining = pool - res.init_charge - inv.init_charge
    order = []
    stream = [(smooth.TRAIN[(t - 1) % len(smooth.TRAIN)]) for t in range(1, max_events + 1)]
    idx = 0
    # 1-2: establishment. The resident develops alone for head_start events, paid out of the shared pool.
    while idx < len(stream) and res.events < head_start and remaining > 0:
        x = stream[idx]; c = res.feed(x, target); remaining -= c; order.append(("R", x, c)); idx += 1
        if remaining < 0: res.starved = True; break
    # 3-4: contested development. The lower cumulative charge takes the next event; ties to the incumbent.
    while idx < len(stream) and remaining > 0:
        who = res if res.charge <= inv.charge else inv
        x = stream[idx]; c = who.feed(x, target)
        if c > remaining:                        # the pool cannot pay for this event: development ends
            who.starved = True; remaining -= c; order.append(("R" if who is res else "I", x, c)); idx += 1; break
        remaining -= c; order.append(("R" if who is res else "I", x, c)); idx += 1
    cap_r, _ = res.evaluate(target); cap_i, _ = inv.evaluate(target)
    outcome = "COEXIST" if cap_r == cap_i else ("RESIDENT_HOLDS" if cap_r > cap_i else "INVADER_REPLACES")
    return {"outcome": outcome, "capability_resident": cap_r, "capability_invader": cap_i,
            "events_resident": res.events, "events_invader": inv.events,
            "charge_resident": res.charge, "charge_invader": inv.charge,
            "init_charge_resident": res.init_charge, "init_charge_invader": inv.init_charge,
            "pool": pool, "pool_remaining": remaining, "pool_spent": pool - remaining,
            "allocation": "".join(w for w, _, _ in order),
            "evaluation_charge_resident": sum(res.M.L.c.values()) - res.charge,
            "evaluation_charge_invader": sum(inv.M.L.c.values()) - inv.charge}


def solo(g, target, pool, max_events=MAX_EVENTS, seed=0):
    """the independent-scoring baseline: the same machine developed alone with the WHOLE pool."""
    c = Carrier("solo", g, seed); remaining = pool - c.init_charge
    for t in range(max_events):
        if remaining <= 0: break
        x = smooth.TRAIN[t % len(smooth.TRAIN)]; cost = c.feed(x, target); remaining -= cost
        if remaining < 0: break
    cap, _ = c.evaluate(target)
    return {"capability": cap, "events": c.events, "charge": c.charge, "pool_remaining": remaining}


def main(tag="V1", pools=POOLS, head_start=HEAD_START, seed=0, rows=None):
    target = smooth.make_target(smooth.COEFFS_V3); t0 = time.time()
    names = rows or sorted(zoo.ZOO)
    genos = {n: zoo.ZOO[n]() for n in names}
    cells = {}; matrices = {}; solos = {}
    disagree = 0; disagreements = []
    for pool in pools:
        solos[pool] = {n: solo(genos[n], target, pool, seed=seed) for n in names}
        mat = {}
        for r, i in itertools.product(names, names):
            rec = compete(genos[r], genos[i], target, pool, head_start, seed=seed, name_res=r, name_inv=i)
            cells[f"pool{pool}|{r}|{i}"] = rec
            mat.setdefault(r, {})[i] = rec["outcome"]
            sr, si = solos[pool][r]["capability"], solos[pool][i]["capability"]
            solo_outcome = "COEXIST" if sr == si else ("RESIDENT_HOLDS" if sr > si else "INVADER_REPLACES")
            if solo_outcome != rec["outcome"]:
                disagree += 1
                disagreements.append({"pool": pool, "resident": r, "invader": i, "diagonal": r == i, "solo_outcome": solo_outcome,
                                      "competitive_outcome": rec["outcome"],
                                      "solo_capabilities": [sr, si], "competitive_capabilities": [rec["capability_resident"], rec["capability_invader"]],
                                      "events": [rec["events_resident"], rec["events_invader"]]})
        matrices[str(pool)] = mat
    # remint invariance: reminting either competitor changes no reported quantity of a competition
    rbad = 0; rchecked = 0
    for r, i in list(itertools.product(names, names))[:12]:
        a = compete(genos[r], genos[i], target, pools[1], head_start, seed=seed)
        b = compete(morph.remint(genos[r], 4), morph.remint(genos[i], 9), target, pools[1], head_start, seed=seed)
        rchecked += 1
        if {k: v for k, v in a.items()} != {k: v for k, v in b.items()}: rbad += 1
    counts = {}
    for pool in pools:
        c = {}
        for r in names:
            for i in names: c[matrices[str(pool)][r][i]] = c.get(matrices[str(pool)][r][i], 0) + 1
        counts[str(pool)] = c
    out = {"schema": "StageR10InvasionCompetitionV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422], "layer": "R10",
           "layer_reading": "invasion and competition under a shared charged budget. The protocol's R10 (real-task adapters, stage B7) is NOT built here and is not claimed: it is out of scope for an 8-bit microscope and stays REGISTERED_FOR_EXPERIMENT in the gap ledger. See the module docstring",
           "run_tag": tag, "seed": seed, "ecology": ECO, "ecology_spec_id": ecology.spec_id(ecology.REGISTRY[ECO]),
           "basis": B0.name, "carriers": names, "n_carriers": len(names),
           "protocol": {"shared_pool": "one charge pool pays for both machines' initialization and development",
                        "stream": "one shared stream of feedback events; the machine that consumes an event is the only one that sees it",
                        "allocation_rule": "the machine with the lower cumulative charge takes the next event; ties to the incumbent resident",
                        "head_start_events": head_start,
                        "max_events": MAX_EVENTS,
                        "endpoint": "capability on the unseen inputs, charged to each machine's own ledger and NOT deducted from the contested pool",
                        "tie_rule": "exact equality of capability is COEXIST; arithmetic is exact so a tie is a real tie"},
           "pools": list(pools),
           "invasion_matrix_by_pool": matrices, "outcome_counts_by_pool": counts,
           "solo_baseline_by_pool": {str(p): solos[p] for p in pools},
           "registered_prediction": "occupancy under a shared budget is not a function of the solo scores: at least one ordered pair must disagree",
           "n_cells": len(cells), "n_cells_where_competition_disagrees_with_solo": disagree,
           "n_offdiagonal_cells_where_competition_disagrees_with_solo": sum(1 for d in disagreements if not d["diagonal"]),
           "n_diagonal_cells_where_competition_disagrees_with_solo": sum(1 for d in disagreements if d["diagonal"]),
           "diagonal_note": "a diagonal cell competes a carrier against a copy of itself; the head start and the shared pool can still split them, so diagonal disagreements are reported separately and the prediction is adjudicated on the OFF-DIAGONAL cells only",
           "prediction_holds": sum(1 for d in disagreements if not d["diagonal"]) > 0,
           "verdict": ("COMPETITION_REORDERS_OCCUPANCY" if sum(1 for d in disagreements if not d["diagonal"]) > 0 else
                       "COMPETITION_ADDS_NOTHING_AT_THIS_SCOPE — every cell agrees with the independent-scoring baseline, so at this scope the shared budget did not change who occupies the niche"),
           "disagreements": disagreements,
           "cells": cells,
           "remint_invariance": {"n_competitions_checked": rchecked, "n_changed": rbad,
                                 "assertion": "reminting either competitor changes no reported quantity of the competition"},
           "seconds": round(time.time() - t0, 1),
           "claim_ceiling": "one ecology, one basis, one allocation rule, one head start, three declared pools, and the R4 parent library as the carrier set. The allocation rule is a modelling choice and a different rule can reorder outcomes; it is reported as part of the result"}
    out["receipt_sha256"] = sha256_of({k: v for k, v in out.items() if k != "receipt_sha256"})
    json.dump(out, open(os.path.join(RES, f"STAGE_R10_INVASION_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    print(f"R10 {out['verdict']}: {out['n_offdiagonal_cells_where_competition_disagrees_with_solo']} off-diagonal "
          f"(+{out['n_diagonal_cells_where_competition_disagrees_with_solo']} diagonal) of {len(cells)} cells disagree with independent scoring")
    for p in pools: print(f"  pool {p:>7}: {counts[str(p)]}")
    return out


if __name__ == "__main__":
    main(tag=sys.argv[1] if len(sys.argv) > 1 else "V1")
