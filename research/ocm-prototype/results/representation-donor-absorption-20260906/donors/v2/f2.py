"""Exact rational checker for MEG-09 parent reduction to strong lumpability/intertwining.

Exit 0 PASS, 1 FAIL, 2 CANNOT_CHECK. No novelty claim.
"""
from __future__ import annotations

import json
import sys
from collections.abc import Mapping
from fractions import Fraction

LIVE, DEAD, UNKNOWN = "LIVE", "DEAD", "UNKNOWN"


class CannotCheck(ValueError):
    """The supplied object does not meet this finite exact checker's contract."""


def _sequence(value):
    if not isinstance(value, (tuple, list)):
        raise CannotCheck("explicit finite sequence required")
    return value


def _rational(value):
    if type(value) is not int and not isinstance(value, Fraction):
        raise CannotCheck("exact rational required; floats and booleans are unsupported")
    return Fraction(value)


def _kernel(P):
    _sequence(P)
    if not P:
        raise CannotCheck("empty fine state space")
    n = len(P)
    for row in P:
        if len(_sequence(row)) != n:
            raise CannotCheck("kernel must be square")
        exact = [_rational(x) for x in row]
        if any(x < 0 for x in exact) or sum(exact) > 1:
            raise CannotCheck("kernel must be nonnegative and substochastic")
    return n


def _partition(blocks, n):
    _sequence(blocks)
    if not blocks:
        raise CannotCheck("empty partition")
    seen = set()
    for block in blocks:
        if not _sequence(block):
            raise CannotCheck("empty fibre")
        for i in block:
            if type(i) is not int or not 0 <= i < n or i in seen:
                raise CannotCheck("invalid or duplicate fine state in partition")
            seen.add(i)
    if seen != set(range(n)):
        raise CannotCheck("partition omits a fine state")


def _vector(vec, n):
    if len(_sequence(vec)) != n or any(_rational(x) < 0 for x in vec):
        raise CannotCheck("seed/vector must be nonnegative with one entry per fine state")


def row_block_sums(P, blocks):
    _partition(blocks, _kernel(P))
    return [[sum(P[i][j] for j in block) for block in blocks] for i in range(len(P))]


def strong_lumpable(P, blocks):
    sums = row_block_sums(P, blocks)
    for block in blocks:
        if any(sums[i] != sums[block[0]] for i in block[1:]):
            return False
    return True


def quotient(P, blocks):
    if not strong_lumpable(P, blocks):
        raise ValueError("NON_LUMPABLE")
    sums = row_block_sums(P, blocks)
    return [[sums[block[0]][b] for b in range(len(blocks))] for block in blocks]


def push(vec, blocks):
    _partition(blocks, len(_sequence(vec)))
    _vector(vec, len(vec))
    return [sum(vec[i] for i in block) for block in blocks]


def fixed_point(P, seed, alpha=Fraction(1, 3)):
    # Exact closed-form Gaussian solve of (I-(1-a)P^T)x = a s.
    n = _kernel(P)
    _vector(seed, n)
    alpha = _rational(alpha)
    if not 0 < alpha <= 1:
        raise CannotCheck("restart alpha must satisfy 0 < alpha <= 1")
    A = [[Fraction(int(i == j)) - (1-alpha)*P[j][i] for j in range(n)] for i in range(n)]
    b = [alpha*x for x in seed]
    aug = [A[i][:] + [b[i]] for i in range(n)]
    for c in range(n):
        pivot = next((r for r in range(c, n) if aug[r][c] != 0), None)
        if pivot is None:
            raise ValueError("SINGULAR")
        aug[c], aug[pivot] = aug[pivot], aug[c]
        z = aug[c][c]
        aug[c] = [x/z for x in aug[c]]
        for r in range(n):
            if r == c:
                continue
            z = aug[r][c]
            if z:
                aug[r] = [x-z*y for x, y in zip(aug[r], aug[c])]
    return [aug[i][-1] for i in range(n)]


def measurable(blocks, values):
    _partition(blocks, len(_sequence(values)))
    return all(all(values[i] == values[block[0]] for i in block[1:]) for block in blocks)


def validate_multiscale_certificate(P_by_revocation, liveness_by_revocation, answer_by_revocation, blocks, revocation_family):
    """MEG-09 + MEG-20 gate over the *whole registered revocation family*.

    Transition commutation is parent-owned lumpability. KSO additionally requires that liveness and
    the registered answer/decision observable factor through the same fibre projection.
    """
    try:
        family = _sequence(revocation_family)
        if not family or len(set(family)) != len(family):
            raise CannotCheck("registered revocation family must be nonempty and distinct")
        if any(not isinstance(d, Mapping) for d in (P_by_revocation, liveness_by_revocation, answer_by_revocation)):
            raise CannotCheck("registered state maps required")
    except (CannotCheck, TypeError):
        return "CANNOT_CHECK_MALFORMED_REGISTERED_SCOPE"
    for R in family:
        if R not in P_by_revocation or R not in liveness_by_revocation or R not in answer_by_revocation:
            return "CANNOT_CHECK_MISSING_REGISTERED_STATE"
    # Validate the whole contract before claiming a counterexample or a certificate.
    try:
        for R in family:
            n = _kernel(P_by_revocation[R])
            _partition(blocks, n)
            lives = _sequence(liveness_by_revocation[R])
            answers = _sequence(answer_by_revocation[R])
            if len(lives) != n or len(answers) != n or any(type(x) is not str or x not in (LIVE, DEAD, UNKNOWN) for x in lives):
                raise CannotCheck("malformed warrant/answer observations")
    except CannotCheck:
        return "CANNOT_CHECK_MALFORMED_REGISTERED_STATE"
    for R in family:
        if not strong_lumpable(P_by_revocation[R], blocks):
            return "REFINE_REQUIRED_NON_LUMPABLE"
        if not measurable(blocks, liveness_by_revocation[R]):
            return "REFINE_REQUIRED_WARRANT_NONMEASURABLE"
        if not measurable(blocks, answer_by_revocation[R]):
            return "REFINE_REQUIRED_ANSWER_NONFACTORING"
        # This validator claims WARRANTED atom navigation. Parent lumpability
        # alone can also hold for an ungated/exploratory kernel, which cannot
        # be relabelled as warranted by attaching fibre-constant labels.
        P, lives = P_by_revocation[R], liveness_by_revocation[R]
        if any(value > 0 and (lives[i] != LIVE or lives[j] != LIVE)
               for i, row in enumerate(P) for j, value in enumerate(row)):
            return "CANNOT_CHECK_WARRANT_KERNEL_MISMATCH"
    return "CERTIFIED"


def cemetery_embed(P):
    n = _kernel(P)
    out = [[Fraction(0) for _ in range(n+1)] for _ in range(n+1)]
    for i,row in enumerate(P):
        for j,x in enumerate(row):
            out[i][j] = x
        missing = Fraction(1) - sum(row)
        if missing < 0:
            raise ValueError("SUPERSTOCHASTIC")
        out[i][n] = missing
    out[n][n] = Fraction(1)
    return out


def check_meg09():
    F = ((0,1),(2,3))
    P = [
        [Fraction(1,2),0,Fraction(1,2),0],
        [0,Fraction(1,2),0,Fraction(1,2)],
        [Fraction(1,4),0,Fraction(3,4),0],
        [0,Fraction(1,4),0,Fraction(3,4)],
    ]
    assert strong_lumpable(P,F)
    Q = quotient(P,F)
    assert Q == [[Fraction(1,2),Fraction(1,2)],[Fraction(1,4),Fraction(3,4)]]
    s = [Fraction(1),0,0,0]
    a = fixed_point(P,s)
    aq = fixed_point(Q,push(s,F))
    assert push(a,F) == aq

    # The certificate must hold for every registered revocation state, not merely the nominal state.
    family = ("none", "rev")
    # Revoke only the first fibre. Keep structural denominators frozen:
    # incoming/outgoing dead-atom mass disappears, and surviving 3/4 stays 3/4.
    Prev = [[x if i >= 2 and j >= 2 else Fraction(0) for j,x in enumerate(row)]
            for i,row in enumerate(P)]
    P_by_R = {"none": P, "rev": Prev}
    live_good = {"none": [LIVE,LIVE,LIVE,LIVE], "rev": [DEAD,DEAD,LIVE,LIVE]}
    answer_good = {"none": ["A","A","B","B"], "rev": ["C","C","D","D"]}
    assert validate_multiscale_certificate(P_by_R, live_good, answer_good, F, family) == "CERTIFIED"

    bad = [row[:] for row in P]
    bad[1] = [0,Fraction(3,4),0,Fraction(1,4)]
    assert not strong_lumpable(bad,F)
    P_bad = {"none": bad, "rev": Prev}
    assert validate_multiscale_certificate(P_bad, live_good, answer_good, F, family) == "REFINE_REQUIRED_NON_LUMPABLE"
    try:
        quotient(bad,F)
    except ValueError as e:
        assert str(e) == "NON_LUMPABLE"
    else:
        raise AssertionError("non-lumpable cross-fibre mutant accepted")

    live_bad = {"none": [LIVE,LIVE,LIVE,LIVE], "rev": [LIVE,DEAD,LIVE,LIVE]}
    assert validate_multiscale_certificate(P_by_R, live_bad, answer_good, F, family) == "REFINE_REQUIRED_WARRANT_NONMEASURABLE"

    answer_bad = {"none": ["A","A","B","B"], "rev": ["C","X","D","D"]}
    assert validate_multiscale_certificate(P_by_R, live_good, answer_bad, F, family) == "REFINE_REQUIRED_ANSWER_NONFACTORING"

    assert validate_multiscale_certificate({"none": P}, live_good, answer_good, F, family) == "CANNOT_CHECK_MISSING_REGISTERED_STATE"

    # Substochastic parent: missing mass becomes a cemetery state without changing live-state solve.
    Psub = [
        [Fraction(1,4),0,Fraction(1,4),0],
        [0,Fraction(1,4),0,Fraction(1,4)],
        [Fraction(1,4),0,Fraction(3,4),0],
        [0,Fraction(1,4),0,Fraction(3,4)],
    ]
    assert strong_lumpable(Psub,F)
    sub = fixed_point(Psub,s)
    Pcem = cemetery_embed(Psub)
    cem = fixed_point(Pcem,s+[Fraction(0)])
    assert cem[:4] == sub
    Fcem = ((0,1),(2,3),(4,))
    assert strong_lumpable(Pcem,Fcem)

    return {
        "fine_states":4,"fibres":2,"registered_revocation_states":len(family),"lumpable":1,
        "pushforward_fixed_point_exact":1,"full_certificate_no_alarm":1,
        "cross_fibre_nonlumpable_mutant_caught":1,"warrant_nonmeasurable_refine_required":1,
        "answer_nonfactoring_refine_required":1,"missing_registered_state_cannot_check":1,
        "substochastic_cemetery_live_projection_equal":1,
        "terminal":"PARENT_LUMPABILITY_SUFFICIENT__KSO_ADDS_WARRANT_AND_ANSWER_MEASURABILITY",
        "GENERAL_NOVELTY":"NOT_ESTABLISHED"
    }


def main():
    try:
        if sys.flags.optimize:
            raise CannotCheck("assertions disabled by optimized Python")
        out=check_meg09()
    except CannotCheck as e:
        print(json.dumps({"status":"CANNOT_CHECK","reason":str(e)},sort_keys=True)); return 2
    except Exception as e:
        print(json.dumps({"status":"FAIL","type":type(e).__name__,"reason":str(e)},sort_keys=True)); return 1
    print(json.dumps({"status":"PASS","result":out},sort_keys=True)); return 0

if __name__ == "__main__": raise SystemExit(main())
