"""Independent re-evaluation of PR #150's factorized-arm quality.

PR #150's headline lifetime comparison scores its two arms with different
instruments.  ``evolutionary_search`` calls ``NK.fitness`` and is oracle
evaluated.  ``local_search`` returns ``sum(comps) / n`` from a component vector
it maintains incrementally from ``inferred`` edges, and never re-checks that
vector against the oracle.  When ``inferred`` is incomplete the vector drifts
from truth and the returned number is a self-report.

PR #150's own published output shows ``mean_structure_recall`` below one in every
drift regime, so ``inferred`` is demonstrably incomplete there.  This module asks
what the factorized arm's states are actually worth.

The one thing that makes the answer trustworthy is the faithfulness gate.  The
traced search below must return a score and a cost **bit identical** to the
original function on the same RNG stream and the same landscape; a test asserts
it, and the whole audit is void if it fails.  Only then is ``NK.fitness`` of the
final state computed.  The oracle calls this audit adds are charged to the audit
and never to either arm.

Nothing here re-implements PR #150's algorithm differently or improves it.  The
traced function is the original with one extra return value.
"""

from __future__ import annotations

import random
import statistics
from dataclasses import dataclass

import pr150_source as SRC

__all__ = ["local_search_traced", "lifetime_audited", "audit_sweeps", "AUDIT_CONDITIONS"]


def local_search_traced(land, rng, affected, budget=16):
    """``SRC.local_search`` verbatim, returning the final state as well.

    Every line below is the original.  The only change is that ``x`` is returned
    alongside the reported score, so the state can be evaluated independently.
    """
    x = rng.randrange(1 << land.n)
    comps = land.components(x)
    cost = 1.0
    while True:
        best_delta, best_bit, best_changes = 0.0, None, None
        exhausted = False
        for bit in range(land.n):
            inds = affected[bit]
            add = len(inds) / land.n
            if cost + add > budget:
                exhausted = True
                break
            y = x ^ (1 << bit)
            delta, changes = 0.0, []
            for i in inds:
                nv = land.comp(y, i)
                delta += nv - comps[i]
                changes.append((i, nv))
            cost += add
            if delta > best_delta + 1e-12:
                best_delta, best_bit, best_changes = delta, bit, changes
        if best_bit is None:
            break
        x ^= 1 << best_bit
        for i, nv in best_changes:
            comps[i] = nv
        if exhausted or cost >= budget:
            break
    return sum(comps) / land.n, cost, x


@dataclass(frozen=True)
class GenerationRecord:
    """One generation of one repetition, reported and true side by side."""

    generation: int
    optimum: float
    reported_quality: float
    true_quality: float
    inflation: float
    structure_recall: float
    structure_precision: float
    inferred_is_exact: bool
    staleness_check_fired: bool
    rediscovered: bool


def lifetime_audited(seed, K, drift, evo_budget, generations=30, reps=8, n=10):
    """``SRC.lifetime`` with identical RNG consumption, plus an oracle read.

    ``NK.fitness`` draws no randomness, so adding it does not perturb the stream.
    The reported aggregates this returns must therefore equal PR #150's published
    ones, and ``test_audit.py`` asserts that against the committed output.
    """
    master = random.Random(seed)
    rows, records = [], []
    for rep in range(reps):
        rng = random.Random(master.randrange(1 << 60))
        scopes, inferred = None, None
        fq, eq = [], []
        fc = ec = 0.0
        rediscoveries = 0
        recalls = []
        for g in range(generations):
            if scopes is not None and drift:
                scopes = SRC.drift_scopes(scopes, n, K, rng, drift)
            land = SRC.NK(n, K, rng, scopes=scopes)
            scopes = land.scopes
            opt = land.optimum()

            staleness_fired = False
            rediscovered = False
            if inferred is None:
                inferred, c = SRC.discover_factorization(land, rng)
                fc += c
                rediscoveries += 1
                rediscovered = True
            else:
                x = rng.randrange(1 << n)
                base = land.components(x)
                fc += 1
                bit = rng.randrange(n)
                changed = land.components(x ^ (1 << bit))
                fc += 1
                observed = {i for i, (u, v) in enumerate(zip(base, changed))
                            if abs(u - v) > 1e-12}
                if observed != set(inferred[bit]):
                    staleness_fired = True
                    inferred, c = SRC.discover_factorization(land, rng)
                    fc += c
                    rediscoveries += 1
                    rediscovered = True

            tp = den = 0
            pred_total = 0
            exact = True
            for bit in range(n):
                true, pred = set(land.affected[bit]), set(inferred[bit])
                tp += len(true & pred)
                den += len(true)
                pred_total += len(pred)
                if true != pred:
                    exact = False
            recall = tp / den
            precision = (tp / pred_total) if pred_total else 1.0
            recalls.append(recall)

            f, c, state = local_search_traced(land, rng, inferred, budget=16)
            fc += c
            true_f = land.fitness(state)          # the audit's own oracle call
            e, c = SRC.evolutionary_search(land, rng, budget=evo_budget)
            ec += c
            fq.append(f / opt)
            eq.append(e / opt)
            records.append(GenerationRecord(
                generation=g, optimum=opt,
                reported_quality=f / opt, true_quality=true_f / opt,
                inflation=(f - true_f) / opt,
                structure_recall=recall, structure_precision=precision,
                inferred_is_exact=exact, staleness_check_fired=staleness_fired,
                rediscovered=rediscovered))
        rows.append((statistics.mean(fq), statistics.mean(eq), fc, ec,
                     rediscoveries, statistics.mean(recalls)))

    reported = statistics.mean(r[0] for r in rows)
    true_mean = statistics.mean(r.true_quality for r in records)
    inflated = [r for r in records if r.inflation > 1e-12]
    return {
        "K": K, "drift": drift, "generations": generations, "reps": reps,
        "evolutionary_budget_per_generation": evo_budget,
        # the four fields below must reproduce PR #150's published values exactly
        "factor_quality_over_optimum": reported,
        "evolutionary_quality_over_optimum": statistics.mean(r[1] for r in rows),
        "factor_total_full_equivalent_cost": statistics.mean(r[2] for r in rows),
        "evolutionary_total_full_eval_cost": statistics.mean(r[3] for r in rows),
        "mean_refactorizations": statistics.mean(r[4] for r in rows),
        "mean_structure_recall": statistics.mean(r[5] for r in rows),
        # everything below is new
        "factor_TRUE_quality_over_optimum": true_mean,
        "mean_inflation": reported - true_mean,
        "max_inflation": max(r.inflation for r in records),
        "generations_inflated": len(inflated),
        "generations_total": len(records),
        "fraction_inflated": len(inflated) / len(records),
        "mean_structure_precision": statistics.mean(r.structure_precision for r in records),
        "generations_with_exact_structure": sum(1 for r in records if r.inferred_is_exact),
        "inflation_when_structure_exact": statistics.mean(
            [r.inflation for r in records if r.inferred_is_exact] or [0.0]),
        "inflation_when_structure_inexact": statistics.mean(
            [r.inflation for r in records if not r.inferred_is_exact] or [0.0]),
        # does the comparison's direction change once the arm is scored honestly?
        "factor_beats_parent_as_reported": reported > statistics.mean(r[1] for r in rows),
        "factor_beats_parent_when_true": true_mean > statistics.mean(r[1] for r in rows),
    }


#: PR #150's own conditions and seeds, copied from ``SRC.lifetime_sweeps``.
AUDIT_CONDITIONS = [(1, 0.0), (2, 0.0), (2, 0.03), (2, 0.10), (5, 0.0), (5, 0.03), (5, 0.10)]
MATCHED_CONDITIONS = [(1, 0.0), (2, 0.0), (2, 0.03), (5, 0.0)]


def audit_sweeps():
    high = [lifetime_audited(20260908 + K * 100 + int(d * 1000), K, d, 48)
            for K, d in AUDIT_CONDITIONS]
    matched = [lifetime_audited(999 + K * 10 + int(d * 100), K, d, 18)
               for K, d in MATCHED_CONDITIONS]
    return {"high_budget_parent": high, "approximately_matched_cost_parent": matched}
