from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, product
import json
from typing import Sequence

CLAIM_CEILING = "GMI_FINITE_MORPHOLOGY_SELECTION_AND_AFFINE_PHASE_SCHEMA_AT_REGISTERED_SCOPE"


class SelectionError(ValueError):
    pass


def F(x: int | str | Fraction) -> Fraction:
    return x if isinstance(x, Fraction) else Fraction(x)


@dataclass(frozen=True)
class Candidate:
    cid: str
    resources: tuple[Fraction, ...]
    viable: bool = True
    reachable: bool = True


@dataclass(frozen=True)
class AffineCandidate:
    cid: str
    intercept: Fraction
    slope: Fraction

    def value(self, theta: Fraction) -> Fraction:
        return self.intercept + self.slope * theta


def make_candidate(cid: str, resources: Sequence[int | str | Fraction], viable: bool = True,
                   reachable: bool = True) -> Candidate:
    if not cid:
        raise SelectionError("EMPTY_CANDIDATE_ID")
    rr = tuple(F(x) for x in resources)
    if not rr:
        raise SelectionError("EMPTY_RESOURCE_VECTOR")
    if any(x < 0 for x in rr):
        raise SelectionError("NEGATIVE_RESOURCE")
    return Candidate(cid, rr, bool(viable), bool(reachable))


def make_affine(cid: str, intercept: int | str | Fraction,
                slope: int | str | Fraction) -> AffineCandidate:
    if not cid:
        raise SelectionError("EMPTY_CANDIDATE_ID")
    return AffineCandidate(cid, F(intercept), F(slope))


def _unique_ids(cands) -> None:
    ids = [c.cid for c in cands]
    if len(set(ids)) != len(ids):
        raise SelectionError("DUPLICATE_CANDIDATE_ID")


def dominates(a: Sequence[Fraction], b: Sequence[Fraction]) -> bool:
    if len(a) != len(b) or not a:
        raise SelectionError("RESOURCE_DIMENSION_MISMATCH")
    return all(x <= y for x, y in zip(a, b, strict=True)) and any(
        x < y for x, y in zip(a, b, strict=True)
    )


def viable_set(cands: Sequence[Candidate], *, reachable_only: bool) -> tuple[Candidate, ...]:
    _unique_ids(cands)
    dims = {len(c.resources) for c in cands}
    if len(dims) > 1:
        raise SelectionError("RESOURCE_DIMENSION_MISMATCH")
    return tuple(c for c in cands if c.viable and (c.reachable if reachable_only else True))


def pareto_front(cands: Sequence[Candidate]) -> tuple[str, ...]:
    _unique_ids(cands)
    if not cands:
        return ()
    dims = {len(c.resources) for c in cands}
    if len(dims) != 1:
        raise SelectionError("RESOURCE_DIMENSION_MISMATCH")
    return tuple(sorted(
        c.cid for c in cands
        if not any(d.cid != c.cid and dominates(d.resources, c.resources) for d in cands)
    ))


def scalar_scores(cands: Sequence[Candidate], weights: Sequence[int | str | Fraction]) -> dict[str, Fraction]:
    if not cands:
        return {}
    ww = tuple(F(w) for w in weights)
    if any(w <= 0 for w in ww):
        raise SelectionError("WEIGHTS_MUST_BE_STRICTLY_POSITIVE")
    dims = {len(c.resources) for c in cands}
    if len(dims) != 1 or next(iter(dims)) != len(ww):
        raise SelectionError("RESOURCE_DIMENSION_MISMATCH")
    return {
        c.cid: sum((w * x for w, x in zip(ww, c.resources, strict=True)), Fraction(0))
        for c in cands
    }


def scalar_argmin(cands: Sequence[Candidate], weights: Sequence[int | str | Fraction]) -> tuple[str, ...]:
    scores = scalar_scores(cands, weights)
    if not scores:
        return ()
    best = min(scores.values())
    return tuple(sorted(k for k, v in scores.items() if v == best))


def selection_record(cands: Sequence[Candidate], weights: Sequence[int | str | Fraction],
                     *, reachable_only: bool = True) -> dict[str, object]:
    active = viable_set(cands, reachable_only=reachable_only)
    if not active:
        return {"terminal": "NO_VIABLE_MORPHOLOGY", "pareto_front": [], "scalar_argmin": []}
    return {
        "terminal": "SELECTION_DEFINED",
        "pareto_front": list(pareto_front(active)),
        "scalar_argmin": list(scalar_argmin(active, weights)),
    }


def componentwise_universal_winner(cands: Sequence[Candidate]) -> str | None:
    if not cands:
        return None
    _unique_ids(cands)
    for c in cands:
        good = True
        for d in cands:
            if c.cid == d.cid:
                continue
            if not all(x <= y for x, y in zip(c.resources, d.resources, strict=True)):
                good = False
                break
            if not any(x < y for x, y in zip(c.resources, d.resources, strict=True)):
                good = False
                break
        if good:
            return c.cid
    return None


def coordinatewise_infimum(cands: Sequence[Candidate]) -> tuple[Fraction, ...]:
    if not cands:
        raise SelectionError("EMPTY_CANDIDATE_SET")
    d = len(cands[0].resources)
    if any(len(c.resources) != d for c in cands):
        raise SelectionError("RESOURCE_DIMENSION_MISMATCH")
    return tuple(min(c.resources[i] for c in cands) for i in range(d))


def affine_argmin(cands: Sequence[AffineCandidate], theta: int | str | Fraction) -> tuple[str, ...]:
    _unique_ids(cands)
    if not cands:
        raise SelectionError("EMPTY_AFFINE_CANDIDATE_SET")
    t = F(theta)
    vals = {c.cid: c.value(t) for c in cands}
    best = min(vals.values())
    return tuple(sorted(k for k, v in vals.items() if v == best))


def pairwise_crossings(cands: Sequence[AffineCandidate], lo, hi) -> tuple[Fraction, ...]:
    _unique_ids(cands)
    L, U = F(lo), F(hi)
    if L > U:
        raise SelectionError("INVALID_INTERVAL")
    out: set[Fraction] = set()
    for a, b in combinations(cands, 2):
        db = a.slope - b.slope
        if db == 0:
            continue
        t = (b.intercept - a.intercept) / db
        if L <= t <= U:
            out.add(t)
    return tuple(sorted(out))


def phase_cells(cands: Sequence[AffineCandidate], lo, hi):
    L, U = F(lo), F(hi)
    if L > U:
        raise SelectionError("INVALID_INTERVAL")
    points = [L] + [t for t in pairwise_crossings(cands, L, U) if L < t < U] + [U]
    points = sorted(set(points))
    return tuple(
        (a, b, affine_argmin(cands, (a + b) / 2))
        for a, b in zip(points, points[1:], strict=False) if a < b
    )


def critical_samples(cands: Sequence[AffineCandidate], lo, hi) -> tuple[Fraction, ...]:
    L, U = F(lo), F(hi)
    if L > U:
        raise SelectionError("INVALID_INTERVAL")
    bounds = [L] + [t for t in pairwise_crossings(cands, L, U) if L < t < U] + [U]
    bounds = sorted(set(bounds))
    pts = set(bounds)
    for a, b in zip(bounds, bounds[1:], strict=False):
        if a < b:
            pts.add((a + b) / 2)
    return tuple(sorted(pts))


def possible_winners(cands: Sequence[AffineCandidate], lo, hi) -> tuple[str, ...]:
    out: set[str] = set()
    for t in critical_samples(cands, lo, hi):
        out.update(affine_argmin(cands, t))
    return tuple(sorted(out))


def uncertainty_terminal(cands: Sequence[AffineCandidate], lo, hi) -> dict[str, object]:
    winners = possible_winners(cands, lo, hi)
    return {
        "terminal": "ROBUST_UNIQUE" if len(winners) == 1 else "AMBIGUOUS",
        "possible_winners": list(winners),
    }


def endpoint_strict_dominance(cands: Sequence[AffineCandidate], winner: str, lo, hi) -> bool:
    L, U = F(lo), F(hi)
    by = {c.cid: c for c in cands}
    if winner not in by or L > U:
        return False
    w = by[winner]
    return all(
        c.cid == winner or (w.value(L) < c.value(L) and w.value(U) < c.value(U))
        for c in cands
    )


def _selection_fixture() -> tuple[Candidate, ...]:
    return (
        make_candidate("A", (1, 4)), make_candidate("B", (4, 1)),
        make_candidate("C", (2, 2)), make_candidate("D", (5, 5)),
    )


def _phase_fixture() -> tuple[AffineCandidate, ...]:
    return (
        make_affine("A", 0, 1), make_affine("B", 1, -1), make_affine("C", "2/5", 0),
    )


def finite_certificate() -> dict[str, object]:
    checks: dict[str, bool] = {}
    sel = _selection_fixture()
    pf = pareto_front(sel)
    checks["pareto_coexistence_preserved"] = pf == ("A", "B", "C")
    checks["price_conditional_winners"] = (
        scalar_argmin(sel, (4, 1)) == ("A",)
        and scalar_argmin(sel, (1, 4)) == ("B",)
        and scalar_argmin(sel, (1, 1)) == ("C",)
    )
    pseudo = coordinatewise_infimum(sel[:2])
    checks["coordinatewise_infimum_hostile"] = (
        pseudo == (F(1), F(1)) and all(c.resources != pseudo for c in sel[:2])
    )
    strong = (
        make_candidate("P", (1, 1)), make_candidate("Q", (1, 2)), make_candidate("R", (2, 1)),
    )
    checks["componentwise_universal_winner"] = (
        componentwise_universal_winner(strong) == "P"
        and pareto_front(strong) == ("P",)
        and all(scalar_argmin(strong, w) == ("P",) for w in ((1, 1), (7, 1), (1, 9)))
    )
    no_viable = (make_candidate("X", (1, 1), viable=False), make_candidate("Y", (2, 2), viable=False))
    checks["empty_viable_fails_closed"] = selection_record(no_viable, (1, 1))["terminal"] == "NO_VIABLE_MORPHOLOGY"
    global_set = (
        make_candidate("G", (1, 1), reachable=False), make_candidate("R1", (2, 2)), make_candidate("R2", (3, 1)),
    )
    global_score = min(scalar_scores(viable_set(global_set, reachable_only=False), (1, 1)).values())
    reach_score = min(scalar_scores(viable_set(global_set, reachable_only=True), (1, 1)).values())
    checks["reachable_optimum_not_better_than_global"] = global_score <= reach_score

    points = tuple((F(i), F(j)) for i, j in product(range(3), repeat=2))
    weights = ((F(1), F(1)), (F(1), F(2)), (F(2), F(1)), (F(3), F(2)))
    subset_checks = 0
    for mask in range(1, 1 << len(points)):
        cs = tuple(make_candidate(f"p{k}", p) for k, p in enumerate(points) if mask & (1 << k))
        front = set(pareto_front(cs))
        for w in weights:
            if not set(scalar_argmin(cs, w)) <= front:
                raise AssertionError("positive scalarization selected dominated candidate")
            subset_checks += 1
    checks["exhaustive_scalar_minimizer_pareto"] = subset_checks == 2044

    phase = _phase_fixture()
    crossings = pairwise_crossings(phase, 0, 1)
    cells = phase_cells(phase, 0, 1)
    checks["analytic_crossings_exact"] = crossings == (F("2/5"), F("1/2"), F("3/5"))
    checks["phase_cells_expected"] = tuple(w for _, _, w in cells) == (("A",), ("C",), ("C",), ("B",))
    checks["boundary_ties_expected"] = (
        affine_argmin(phase, F("2/5")) == ("A", "C")
        and affine_argmin(phase, F("3/5")) == ("B", "C")
        and affine_argmin(phase, F("1/2")) == ("C",)
    )
    phase_sample_checks = 0
    for a, b, expected in cells:
        for q in (F("1/4"), F("1/2"), F("3/4")):
            if affine_argmin(phase, a + (b - a) * q) != expected:
                raise AssertionError("phase argmin changed inside crossing-free cell")
            phase_sample_checks += 1
    checks["phase_cell_direct_checks"] = phase_sample_checks == 12

    robust = uncertainty_terminal(phase, F("9/20"), F("11/20"))
    ambiguous = uncertainty_terminal(phase, F("1/3"), F("2/3"))
    checks["uncertainty_robust_unique"] = robust == {"terminal": "ROBUST_UNIQUE", "possible_winners": ["C"]}
    checks["uncertainty_ambiguous"] = ambiguous == {"terminal": "AMBIGUOUS", "possible_winners": ["A", "B", "C"]}
    checks["endpoint_strict_dominance_sufficient"] = endpoint_strict_dominance(phase, "C", F("9/20"), F("11/20"))

    midpoint_hostile = (make_affine("M", 0, 0), make_affine("N", "-3/4", 1))
    mid = affine_argmin(midpoint_hostile, F("1/2"))
    allw = possible_winners(midpoint_hostile, 0, 1)
    checks["midpoint_only_hostile"] = mid == ("N",) and allw == ("M", "N")

    funcs = tuple(make_affine(f"f{i}", a, b) for i, (a, b) in enumerate(product((F(-1), F(0), F(1)), repeat=2)))
    affine_triples = affine_cell_checks = 0
    for idxs in combinations(range(len(funcs)), 3):
        fs = tuple(AffineCandidate(f"c{j}", funcs[i].intercept, funcs[i].slope) for j, i in enumerate(idxs))
        for a, b, expected in phase_cells(fs, F(-1), F(1)):
            for q in (F("1/4"), F("1/2"), F("3/4")):
                if affine_argmin(fs, a + (b - a) * q) != expected:
                    raise AssertionError("affine census cell violation")
                affine_cell_checks += 1
        affine_triples += 1
    checks["affine_census_no_cell_violations"] = affine_triples == 84 and affine_cell_checks > 0

    if not all(checks.values()):
        raise AssertionError(checks)
    return {
        "schema": "GMI_833_MORPHOLOGY_SELECTION_SCHEMA_RESULT_V1",
        "claim_ceiling": CLAIM_CEILING,
        "verdict": "GREEN",
        "checks": checks,
        "counts": {
            "small_grid_nonempty_subsets": 511,
            "small_grid_scalar_checks": subset_checks,
            "phase_fixture_cells": len(cells),
            "phase_direct_interior_checks": phase_sample_checks,
            "affine_triples": affine_triples,
            "affine_cell_checks": affine_cell_checks,
        },
        "witnesses": {
            "pareto_front": list(pf),
            "coordinatewise_infimum_unattainable": [str(x) for x in pseudo],
            "phase_crossings": [str(x) for x in crossings],
            "robust_interval": robust,
            "ambiguous_interval": ambiguous,
            "midpoint_winner": list(mid),
            "midpoint_interval_possible_winners": list(allw),
        },
        "forbidden_promotions": [
            "UNIVERSAL_INTELLIGENCE_UTILITY", "UNIVERSAL_PRICE_VECTOR",
            "NONAFFINE_PHASE_LAWS_PROVED", "STOCHASTIC_PHASE_LAWS_PROVED",
            "REAL_WORLD_PHASE_CALIBRATION", "HISTORY_HYSTERESIS_CLOSED",
            "ALL_KNOWN_FORM_RECOVERY_COMPLETE", "COMPLETE_GMI",
        ],
    }


def main() -> None:
    print(json.dumps(finite_certificate(), sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
