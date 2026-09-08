"""Bounded exact serving attempt; the dense KSO API remains the reference.

Two rational restart steps are candidates, never convergence authority. A third
whole-field matvec must give exactly zero residual for the same operator. Plain
nonnegative weights, no relevance callback, and 0 < alpha <= 1 make that operator
substochastic, so this fixed point is unique. Every other case uses the reference.
"""
from fractions import Fraction as F

from ocm.kso import navigation as N
from ocm.kso import navigation_matrix_free as MF
from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace
from ocm.kso.warrant import WarrantProfile


def _supported(ks, seed, alpha, rv, relevance, mode, work):
    if (type(ks) is not KnowledgeSpace or relevance is not None
            or type(alpha) not in (int, F) or not 0 < alpha <= 1
            or type(seed) not in (list, tuple) or len(seed) != len(ks.ids)
            or type(mode) is not N.NavigationMode):
        return False
    for value in seed:
        work["eligibility_values"] += 1
        if type(value) not in (int, F):
            return False
    for value in rv:
        work["eligibility_values"] += 1
        if type(value) not in (str, int):
            return False
    for objects, cls in ((ks.atoms, Atom), (ks.hyperedges, Hyperedge)):
        for obj in objects:
            work["eligibility_objects"] += 1
            if type(obj) is not cls or type(obj.warrant) is not WarrantProfile:
                return False
            for profile in (obj.warrant.lower, obj.warrant.upper):
                for warrant in profile:
                    for evidence in warrant:
                        work["eligibility_values"] += 1
                        if type(evidence) not in (str, int):
                            return False
            if cls is Atom:
                values = (obj.atom_id,)
            else:
                work["structural_tail_count"] += len(obj.tails)
                values = (obj.edge_id, obj.relation_type, *obj.tails, *obj.heads)
                for weight in (obj.weight, *obj.head_weights):
                    work["eligibility_values"] += 1
                    if type(weight) not in (int, F) or weight < 0:
                        return False
            for value in values:
                work["eligibility_values"] += 1
                if type(value) is not str:
                    return False
    return True


def fixed_point(ks, seed, alpha, *, revoked=(), relevance=None,
                mode=N.NavigationMode.WARRANTED, work):
    """Serving-only wrapper; no matrix override and no cross-call operator cache.

    Counters are this call's structural work. Successful matvecs expose all-field
    index/denominator preparation plus existing incidence counters. Partial
    internals and dense arithmetic are explicitly unavailable, not zero-cost.
    """
    rv = frozenset(revoked)
    work.update(terminal="STARTED", reason="UNSUPPORTED_INPUT", mode=mode.value if
                type(mode) is N.NavigationMode else "UNSUPPORTED", residual_l1=None,
                eligibility_objects=0, eligibility_values=0, structural_tail_count=0, seed_gate_entries=0,
                matvec_attempts=0, matvec_completed=0, index_entries=0,
                denominator_atom_entries=0, denominator_edge_visits=0, denominator_tail_visits=0,
                hyperedges_examined=0, live_tail_terms=0, head_terms_examined=0,
                restart_entries=0, residual_entries=0, dense_calls=0,
                dense_matrix_entries=0, partial_matvec_work=None, attempt_error=None, dense_internal_work=None,
                arithmetic_and_warrant_internals="NOT_INSTRUMENTED")
    if _supported(ks, seed, alpha, rv, relevance, mode, work):
        try:
            gated = N.gated_seed(ks, seed, rv, mode)
            work["seed_gate_entries"] += len(gated)
            # Match the dense API's validation AFTER warrant gating.
            if any(value < 0 for value in gated) or sum(gated, F(0)) > 1:
                work["reason"] = "INVALID_GATED_SEED"
            else:
                current = gated
                for step in range(3):
                    work["matvec_attempts"] += 1
                    transition, counts = MF.transpose_matvec(
                        ks, current, revoked=rv, mode=mode, with_work=True)
                    work["matvec_completed"] += 1
                    work["index_entries"] += len(ks.ids)
                    work["denominator_atom_entries"] += len(ks.ids)
                    work["denominator_edge_visits"] += len(ks.hyperedges)
                    work["denominator_tail_visits"] += work["structural_tail_count"]
                    for key in ("hyperedges_examined", "live_tail_terms", "head_terms_examined"):
                        work[key] += getattr(counts, key)
                    nxt = [alpha * s + (1-alpha) * t
                           for s, t in zip(gated, transition, strict=True)]
                    work["restart_entries"] += len(nxt)
                    if step < 2:
                        current = nxt
                residual = sum((abs(a-b) for a, b in zip(nxt, current, strict=True)), F(0))
                work["residual_entries"] += len(current)
                work["residual_l1"] = str(residual)
                if residual == 0:
                    work.update(terminal="MATRIX_FREE_EXACT", reason="ZERO_RESIDUAL")
                    return dict(zip(ks.ids, current, strict=True))
                work["reason"] = "NONZERO_RESIDUAL"
        except Exception as exc:
            work["reason"] = "ATTEMPT_REFUSED"
            work["attempt_error"] = type(exc).__name__ + ": " + str(exc)
            if work["matvec_attempts"] != work["matvec_completed"]:
                work["partial_matvec_work"] = "UNAVAILABLE"
    work["dense_calls"] += 1
    try:
        result = N.fixed_point(ks, seed, alpha, revoked=rv, relevance=relevance, mode=mode)
    except Exception:
        work.update(terminal="REFUSED", dense_internal_work="UNAVAILABLE")
        raise
    # Exactly the reference's completed transition matrix, not all dense work.
    work.update(terminal="DENSE_REFERENCE", dense_matrix_entries=len(ks.ids)**2,
                dense_internal_work="NOT_INSTRUMENTED")
    return result
