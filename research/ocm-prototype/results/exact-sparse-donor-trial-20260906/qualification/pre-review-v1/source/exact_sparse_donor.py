"""Research-only exact donor: ADAPT current kernel, ADOPT SymPy 1.14 QQ RREF.

No cross-call cache, custom elimination, float arithmetic or dense candidate
assembly. Supplied matrices and callable relevance retain the original route.
SymPy imports are lazy so the reference consumer does not load an unused donor.
The independent original dense residual is required and charged checker work.
"""
from fractions import Fraction as F
from ocm.kso import navigation as N
from ocm.kso.warrant import CannotCheck
from exact_sparse_donor_check import verify

ORIGINAL = N.fixed_point


def assemble(ks, seed, alpha, *, revoked=(), relevance=None,
             mode=N.NavigationMode.WARRANTED):
    """Direct sparse A = I-(1-alpha)P.T and B = alpha*gated_seed over QQ."""
    from sympy.polys.domains import QQ
    from sympy.polys.matrices import DomainMatrix
    if callable(relevance):
        raise ValueError("CALLABLE_RELEVANCE_REQUIRES_ORIGINAL_ROUTE")
    rv, ids = frozenset(revoked), ks.ids
    index, atoms = {x: i for i, x in enumerate(ids)}, ks.atom_map()
    # Original structural denominators are evaluated before all warrant gates.
    denominators = N.structural_denominators(ks, relevance)
    a = {i: {i: F(1)} for i in range(len(ids))}
    for edge in ks.hyperedges:
        mass = edge.weight * N._beta(relevance, edge.relation_type)
        if mass == 0:
            continue
        edge_gate = N._gate(edge.liveness(rv), mode)
        tails_gate = min((N._gate(atoms[t].liveness(rv), mode) for t in edge.tails), default=F(0))
        if edge_gate == 0 or tails_gate == 0:
            continue
        weights = edge.normalized_head_weights()
        for tail in edge.tails:
            if denominators[tail] == 0:
                continue
            probability = mass / denominators[tail]
            for head, weight in zip(edge.heads, weights, strict=True):
                gate = N._gate(atoms[head].liveness(rv), mode)
                contribution = -(1-alpha)*edge_gate*tails_gate*gate*probability*weight
                row, col = index[head], index[tail]
                if contribution:
                    a[row][col] = a[row].get(col, F(0)) + contribution
                    if a[row][col] == 0:
                        del a[row][col]
    gated = N.gated_seed(ks, seed, rv, mode)
    if not (F(0) < alpha <= F(1)):
        raise ValueError("alpha must be in (0,1]")
    if len(gated) != len(ids) or any(x < 0 for x in gated) or sum(gated, F(0)) > 1:
        raise ValueError("seed must be a non-negative sub-probability vector")
    rational = lambda v: QQ(F(v).numerator, F(v).denominator)
    A = DomainMatrix.from_dod({i: {j: rational(v) for j, v in row.items()}
                               for i, row in a.items() if row}, (len(ids), len(ids)), QQ)
    B = DomainMatrix.from_dod({i: {0: rational(alpha*x)}
                               for i, x in enumerate(gated) if x}, (len(ids), 1), QQ)
    return A, B


def solve_checked(ks, seed, alpha, *, revoked=(), relevance=None,
                  mode=N.NavigationMode.WARRANTED, matrix=None):
    """Return the original full dict plus explicit solver/checker custody."""
    if callable(relevance) or matrix is not None or not isinstance(alpha, (F, int)):
        reason = ("CALLABLE_RELEVANCE" if callable(relevance) else
                  "SUPPLIED_MATRIX" if matrix is not None else "NONRATIONAL_ALPHA")
        values = ORIGINAL(ks, seed, alpha, revoked=revoked, relevance=relevance,
                          mode=mode, matrix=matrix)
        return values, {"route": "ORIGINAL_"+reason, "donor_solve_calls": 0,
                        "independent_residual": "ORIGINAL_BEHAVIOR_NO_ADDED_CHECK"}
    from sympy.polys.matrices.exceptions import DMNonInvertibleMatrixError
    rv = frozenset(revoked)
    A, B = assemble(ks, seed, alpha, revoked=rv, relevance=relevance, mode=mode)
    values = {}
    if ks.ids:
        try:
            numerator, denominator = A.solve_den(B, method="rref")
        except DMNonInvertibleMatrixError as exc:
            raise CannotCheck("singular exact system") from exc
        if denominator == 0 or A * numerator != B * denominator:
            raise CannotCheck("EXACT_DONOR_ALGEBRAIC_CERTIFICATE_FAILED")
        # Access every coordinate; do not truncate zero outputs or reorder IDs.
        for i, atom_id in enumerate(ks.ids):
            q = numerator[i, 0].element / denominator
            values[atom_id] = F(int(q.numerator), int(q.denominator))
    checked = verify(ks, seed, alpha, values, revoked=rv, relevance=relevance, mode=mode)
    return values, {"route": "SYMPY_QQ_RREF", "donor_solve_calls": int(bool(ks.ids)),
                    "donor_method": "DomainMatrix.solve_den(method='rref')",
                    "coefficient_nnz": A.nnz(), "rhs_nnz": B.nnz(),
                    "candidate_assembly": "DIRECT_SPARSE",
                    "transient_solver_fill": "UNKNOWN", **checked}


def fixed_point(ks, seed, alpha, *, revoked=(), relevance=None,
                mode=N.NavigationMode.WARRANTED, matrix=None):
    return solve_checked(ks, seed, alpha, revoked=revoked, relevance=relevance,
                         mode=mode, matrix=matrix)[0]
