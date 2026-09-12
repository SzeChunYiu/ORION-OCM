"""Shared charged instrument for the stage-B2 microfeature atlas cells (issue #422, stage B2 of
GMI_BIOSPHERE_EXPERIMENT_PROTOCOL_V1.md section 9).

Everything in this module is EXACT: rational arithmetic (fractions.Fraction) or the registered 8-bit fixed-point
universe of gmi_microscope/core.py (TOTAL_BITS = 8, FRAC_BITS = 4). There is no randomness anywhere in stage B2.

It carries the five protocol rules that every B2 receipt has to satisfy, as executable helpers rather than as prose,
so that a receipt either calls them or visibly does not:

rule 21 (narrowed by RV-377-073)
    no admissible row may SERVE STATE WRITTEN DURING DEVELOPMENT without a charged operation. The original wording
    ("no admissible row has zero execution cost per query") is FALSIFIED_AND_REPLACED in
    GMI_GAP_LEDGER_EXECUTED_V1.md section 5: a machine serving a CONSTANT legitimately costs nothing to run, and
    rule 22 requires exactly such a row in every cell. `charged_serve_audit` therefore asserts the narrowed rule:
    every row that reads developed state has strictly positive charged execution cost per query, and every row with
    zero cost is declared constant-answer.

rule 22
    an obligation is only meaningful where the BEST CONSTANT ANSWER is below theta. `constant_control` returns the
    hindsight-optimal constant answer's capability; a cell whose control is admissible is VOID, not weak, and its
    clauses must not be evaluated there.

rule 24
    a GATE claim (precision, capacity, reliability, depth) must enumerate the REPRESENTATIONS of the carrier's state
    that the alphabet admits and test the strongest at the gated setting. `GateClaim` is a small record that forces a
    cell to list the encodings it tried and to name which one is the strongest.

rule 28 / DG-2
    every frontier grid must extend past the analytic crossover of every price vector it reports, and every receipt
    reporting a frontier must carry the PER-ROW COST COORDINATES that produced it. `crossovers` / `grid_for` /
    `check_dg2` are the dk_depth.py procedure (RV-377-065), reused verbatim in shape: compute every crossover FIRST in
    exact rationals, then build the grid to bracket each one and to reach at least 4x the largest, then assert
    max(grid) >= 2 * max(crossover). `frontier_block` emits the coordinates, the crossovers, the grid and the occupant
    together, so the receipt is auditable from its own contents.

rule 29
    a census count is meaningless outside the triple (alphabet, servability filter, ecology). `census` refuses to
    return a bare number.

Every cost line in stage B2 is AFFINE in the reuse horizon H: cost(H) = A + H*E, with A the description/fixed
coordinate and E the charged execution cost per query. That is the same shape the whole executed corpus uses and it
is what makes the crossovers exact.
"""
from __future__ import annotations

from fractions import Fraction as Fr

KIND = "SYNTHETIC_EXACT_MICROSCOPE__LAPTOP_SCOPE__NOT_EMPIRICAL_NEURAL_EVIDENCE"
MATH_KIND = "MATH_IMPLEMENTATION_CHECK__NOT_EMPIRICAL_NEURAL_EVIDENCE"

RULE_21 = ("rule 21 as NARROWED by RV-377-073: no admissible row may serve state written during development without a "
           "charged operation. The original wording ('no admissible row has zero execution cost per query') is "
           "FALSIFIED_AND_REPLACED -- a machine serving a constant legitimately costs nothing to run, and rule 22 "
           "requires exactly such a row in every cell.")
RULE_22 = ("rule 22: an obligation is meaningful only where the hindsight-optimal CONSTANT answer is below theta; a "
           "mode whose constant control is admissible is VOID, not weak, and its clauses are not evaluated there.")
RULE_24 = ("rule 24: a gate claim must enumerate the representations of the carrier's state the alphabet admits and "
           "test the strongest at the gated setting.")
RULE_28 = ("rule 28 / DG-2: the reuse grid is built from the analytic crossovers, computed first in exact rationals, "
           "and extends past twice the largest of them; the per-row cost coordinates (A, E) that produced the frontier "
           "are carried in the receipt.")
RULE_29 = ("rule 29: a census count is meaningless outside the triple (alphabet, servability filter, ecology) and must "
           "carry all three in the same sentence as the number.")


# ------------------------------------------------------------------------------------------------- rule 22
def constant_control(items, answer_of, value_of=None):
    """The hindsight-optimal CONSTANT answer and the capability it achieves.

    `items` is the enumerated obligation; `answer_of(item)` is the required answer. The best constant answer is the
    plurality required answer, and its capability is the fraction of items it gets exactly right. No learning, no
    fitting: it is the single best answer chosen with full hindsight, which is what rule 22 demands.
    """
    counts = {}
    for it in items:
        a = answer_of(it)
        counts[a] = counts.get(a, 0) + 1
    if not counts:
        return {"best_constant_answer": None, "capability": Fr(0), "n_items": 0}
    best = max(sorted(counts, key=str), key=lambda a: counts[a])
    return {"best_constant_answer": best, "capability": Fr(counts[best], len(items)), "n_items": len(items),
            "charged_serve_ops_per_query": 0,
            "why_zero_is_legal": "a constant-answer row reads NO developed state, so rule 21 as narrowed by "
                                 "RV-377-073 does not require it to be charged"}


def obligation_is_void(control_capability, theta):
    """rule 22: the obligation is VOID wherever the best constant answer already clears theta."""
    return Fr(control_capability) >= Fr(theta)


# ------------------------------------------------------------------------------------------------- rule 21
def charged_serve_audit(rows):
    """rows: {name: {"serves_developed_state": bool, "charged_serve_ops_per_query": Fraction|int, "admissible": bool}}.

    Returns the audit record and, as `passed`, the narrowed rule-21 verdict: every ADMISSIBLE row that serves state
    written during development has strictly positive charged execution cost per query.
    """
    offenders = sorted(n for n, r in rows.items()
                       if r.get("admissible") and r.get("serves_developed_state") and Fr(r["charged_serve_ops_per_query"]) <= 0)
    zero_cost = sorted(n for n, r in rows.items() if Fr(r["charged_serve_ops_per_query"]) == 0)
    return {"rule": RULE_21, "n_rows": len(rows),
            "admissible_rows_serving_developed_state_at_zero_cost": offenders,
            "zero_cost_rows": zero_cost,
            "zero_cost_rows_are_all_constant_answer": all(not rows[n].get("serves_developed_state") for n in zero_cost),
            "charged_serve_ops_per_query": {n: str(Fr(r["charged_serve_ops_per_query"])) for n, r in sorted(rows.items())},
            "passed": not offenders}


# ------------------------------------------------------------------------------------------------- rule 24
def gate_claim(name, gated_axis, gated_setting, encodings, strongest, verdict, note):
    """rule 24: a gate claim records EVERY state representation the alphabet admits, which one is strongest, and the
    verdict at the gated setting. `encodings` maps encoding name -> the capability it reaches at that setting."""
    caps = {k: str(Fr(v)) for k, v in encodings.items()}
    best = max(encodings, key=lambda k: (Fr(encodings[k]), k))
    return {"rule": RULE_24, "claim": name, "gated_axis": gated_axis, "gated_setting": str(gated_setting),
            "state_representations_enumerated": sorted(encodings), "capability_by_representation": caps,
            "declared_strongest_representation": strongest,
            "measured_strongest_representation": best,
            "declared_strongest_is_the_measured_strongest": strongest == best,
            "verdict": verdict, "note": note}


# ------------------------------------------------------------------------------------------------- rule 28 / DG-2
def crossovers(lines):
    """lines: {row: (A, E)} with cost(H) = A + H*E, all exact rationals. Every pairwise crossover H* > 0, computed
    BEFORE any grid exists. This is the dk_depth.py (RV-377-065) procedure that closed DG-2 by construction."""
    out = {}
    names = sorted(lines)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            Aa, Ea = (Fr(x) for x in lines[a])
            Ab, Eb = (Fr(x) for x in lines[b])
            if Ea == Eb:
                continue
            h = (Ab - Aa) / (Ea - Eb)
            if h > 0:
                out[f"{a}|{b}"] = h
    return out


BASE_GRID = (1, 4, 16, 64, 256, 1024)


def grid_for(cross, base=BASE_GRID):
    """DG-2: bracket every crossover from below and above and reach at least 4x the largest."""
    g = set(base)
    for h in cross.values():
        f = int(h)
        g.update({max(1, f), f + 1, 2 * f + 2})
    if cross:
        hmax = max(cross.values())
        g.update({2 * int(hmax) + 2, 4 * int(hmax) + 4})
    return sorted(g)


def check_dg2(cross, grid):
    """the DG-2 assertion: no crossover lies at or beyond half the grid's extent."""
    if not cross:
        return True
    return max(grid) >= 2 * max(cross.values())


def frontier_of(lines, grid):
    """occupants (exact ties included) at every H of the grid."""
    out = {}
    for H in grid:
        if not lines:
            out[H] = []
            continue
        c = {r: Fr(lines[r][0]) + Fr(H) * Fr(lines[r][1]) for r in lines}
        m = min(c.values())
        out[H] = sorted(r for r in lines if c[r] == m)
    return out


def frontier_set(contexts, note=""):
    """The rule-28 block for a WHOLE receipt: one shared reuse grid built from the crossovers of EVERY context, so
    that a single grid maximum is honest for all of them and gmi_microscope/grid_audit.py can grade the receipt
    against one grid. Returns (blocks, shared_grid)."""
    allcross = {}
    for cname, lines in contexts.items():
        for k, v in crossovers({r: (Fr(a), Fr(b)) for r, (a, b) in lines.items()}).items():
            allcross[f"{cname}|{k}"] = v
    grid = grid_for(allcross)
    return {cname: frontier_block(lines, note=note, grid=grid) for cname, lines in contexts.items()}, grid


def runs_of(front, grid):
    """The frontier as maximal runs of constant occupant over the grid: [H_low, H_high, occupants]."""
    out = []
    for H in grid:
        occ = front[H]
        if out and out[-1][2] == occ:
            out[-1][1] = H
        else:
            out.append([H, H, occ])
    return out


def frontier_block(lines, note="", grid=None):
    """The whole rule-28 block for ONE context: per-row cost coordinates, every crossover, the grid built from them,
    the DG-2 assertion, the occupant at every H, and the occupant for all sufficiently large H."""
    lines = {k: (Fr(v[0]), Fr(v[1])) for k, v in lines.items()}
    cross = crossovers(lines)
    if grid is None:
        grid = grid_for(cross)
    front = frontier_of(lines, grid)
    inf_occ = []
    if lines:
        e = min(v[1] for v in lines.values())
        flat = [r for r in lines if lines[r][1] == e]
        a = min(lines[r][0] for r in flat)
        inf_occ = sorted(r for r in flat if lines[r][0] == a)
    return {
        "rule": RULE_28,
        "cost_model": "cost(H) = A + H*E, A the description/fixed coordinate, E the charged execution cost per query",
        "cost_coordinates_A_E": {r: [str(v[0]), str(v[1])] for r, v in sorted(lines.items())},
        "crossovers_H_star": {k: str(v) for k, v in sorted(cross.items())},
        "crossovers_H_star_decimal": {k: round(float(v), 6) for k, v in sorted(cross.items())},
        "largest_crossover": str(max(cross.values())) if cross else None,
        "grid_H": grid, "grid_max_H": max(grid),
        "dg2_grid_covers_twice_every_crossover": check_dg2(cross, grid),
        "frontier_runs": runs_of(front, grid),
        "frontier_runs_format": "[H_low, H_high, occupants]: the occupant set is constant over every grid point in "
                                "[H_low, H_high]. Equivalent to one entry per grid point and exactly reconstructible "
                                "from grid_H; gmi_microscope/grid_audit.py expands it.",
        "occupants_on_grid": sorted({r for v in front.values() for r in v}),
        "occupant_for_all_sufficiently_large_H": inf_occ,
        "rows_never_occupying_a_cell": sorted(set(lines) - {r for v in front.values() for r in v}),
        "note": note,
    }


# ------------------------------------------------------------------------------------------------- rule 29
def census(n, alphabet, servability_filter, ecology, what):
    """rule 29: a count never travels without its triple, and a configuration count is never called a species count."""
    return {"rule": RULE_29, "count": n, "counts_what": what, "alphabet": alphabet,
            "servability_filter": servability_filter, "ecology": ecology,
            "not_a_species_count": "this is a count of %s under the triple above; it is NOT a count of species and NOT "
                                   "a count of forms" % what}


# ------------------------------------------------------------------------------------------------- exact linear algebra
def rank_and_consistency(rows, targets):
    """Exact rational Gaussian elimination. Returns (rank(Phi), rank([Phi|q]), consistent)."""
    A = [[Fr(x) for x in r] + [Fr(t)] for r, t in zip(rows, targets)]
    m = len(A)
    n = len(A[0]) - 1 if m else 0
    piv_rows = 0
    piv_cols = []
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if A[i][c] != 0), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        inv = Fr(1) / A[r][c]
        A[r] = [x * inv for x in A[r]]
        for i in range(m):
            if i != r and A[i][c] != 0:
                f = A[i][c]
                A[i] = [x - f * y for x, y in zip(A[i], A[r])]
        piv_cols.append(c)
        r += 1
        if r == m:
            break
    piv_rows = r
    consistent = all(any(A[i][c] != 0 for c in range(n)) or A[i][n] == 0 for i in range(m))
    aug_rank = piv_rows + (0 if consistent else 1)
    return piv_rows, aug_rank, consistent


def solve_exact(rows, targets, n):
    """One exact solution of Phi w = q (the least-index-pivot solution, free variables set to 0), or None."""
    A = [[Fr(x) for x in r] + [Fr(t)] for r, t in zip(rows, targets)]
    m = len(A)
    piv = {}
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if A[i][c] != 0), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        inv = Fr(1) / A[r][c]
        A[r] = [x * inv for x in A[r]]
        for i in range(m):
            if i != r and A[i][c] != 0:
                f = A[i][c]
                A[i] = [x - f * y for x, y in zip(A[i], A[r])]
        piv[c] = r
        r += 1
        if r == m:
            break
    for i in range(r, m):
        if A[i][n] != 0 and all(A[i][c] == 0 for c in range(n)):
            return None
    w = [Fr(0)] * n
    for c, i in piv.items():
        w[c] = A[i][n]
    return w
