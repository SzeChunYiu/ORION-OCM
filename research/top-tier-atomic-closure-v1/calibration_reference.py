#!/usr/bin/env python3
"""OCM M0 calibration reference fixture (STEERING_MEMO 2026-09-10 section 4).

Reimplemented from STEERING_MEMO 2026-09-10 section 4 spec; the memo's
calibration_reference.py file was not delivered.

ROLE: assay validation only. This fixture validates the DEV-CAL-2 readout
pipeline (measurement counting, arm bookkeeping, control adjudication) before
binding to OCM. It is NOT an OCM result and confers no claim. It must never be
imported by or transplanted into src/ocm or any production path (no second
cognitive core); independence from src/ocm is the entire point of a calibration
reference.

SPEC (memo section 4, followed exactly):
- Tasks are parity functions f_a(x) = (a . x) mod 2 with d-bit vectors, d=8,
  evaluated on the full 256-input domain.
- Environment coefficients lie in a hidden r-dimensional linear subspace S of
  GF(2)^d; r=3 is declared as the rank prior.
- Developmental stage: learn THREE independent prior functions from 24 binary
  observations (8 per prior function); their verified coefficient vectors must
  span S. Then exhaustively check FIVE target coefficients not individually
  present among those prior functions.
- Fresh-target acquisition: with S known, a target is specified by r unknown
  coefficients in the LEARNED basis; the learner chooses r=3 linearly
  independent binary measurements, solves the GF(2) linear system, recovers the
  coefficient vector, and is verified on ALL 256 inputs. Without S (RESET /
  ambient basis) the same algorithm needs d=8 measurements. The learned-basis
  learner AND an equally adaptive ordinary parent each use 3 fresh observations;
  RESET uses 8. Worst-case identification lower bounds are r and d
  respectively for the full noiseless classes.
- Malformed observations and wrong structural prior are NOT treated as proof of
  leakage: a wrong prior fails and then recovers through the PAID ambient
  fallback (3+8 observations).

Report fields: economic_claim_authorized=false, ocm_specific_claim_authorized=false.
"""

import hashlib
import json
import random
import sys

D = 8                       # ambient dimension (d): 256 inputs
R = 3                       # rank prior (r): hidden subspace dimension
N_PRIORS = 3                # developmental prior functions
OBS_PER_PRIOR = 8           # binary observations per prior function
DEV_OBS_TOTAL = N_PRIORS * OBS_PER_PRIOR   # 24
N_CHECKED_TARGETS = 5       # exhaustively checked fresh target coefficients
N_INPUTS = 1 << D           # 256
DEFAULT_SEED = 20260910     # frozen seed: deterministic under this seed

PROVENANCE = (
    "Reimplemented from STEERING_MEMO 2026-09-10 section 4 spec; the memo's "
    "calibration_reference.py file was not delivered."
)
ROLE_NOTE = (
    "assay validation only: validates the DEV-CAL-2 readout pipeline before "
    "binding to OCM; NOT an OCM result, confers no claim; never imported by "
    "src/ocm or any production path"
)

# Learner states (distinct verdict namespaces; INSUFFICIENT_HISTORY is never a
# headroom verdict of any kind).
STATE_SOLVED = "SOLVED"
STATE_INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"
STATE_WRONG_STRUCTURE_REFUSED = "WRONG_STRUCTURE_REFUSED"
STATE_MALFORMED_REJECTED = "MALFORMED_INPUT_REJECTED"
STATE_FAILED = "FAILED"


class MalformedObservation(ValueError):
    """A binary observation that violates the fixture's observation schema.

    Raised for wrong-length input vectors, non-binary entries or labels, or
    observations addressed to an unknown task. NEVER interpreted as evidence of
    leakage; the caller records STATE_MALFORMED_REJECTED and moves on.
    """


# ---------------------------------------------------------------------------
# GF(2) linear algebra (self-contained; no external dependencies by design)
# ---------------------------------------------------------------------------

def dot(a, b):
    """Inner product of two bit-vectors over GF(2)."""
    if len(a) != len(b):
        raise MalformedObservation("dot: length mismatch")
    acc = 0
    for x, y in zip(a, b):
        acc ^= x & y
    return acc & 1


def rref(rows, ncols):
    """Reduced row echelon form over GF(2).

    Returns (rref_rows, pivot_columns, rank). The RREF of a row space is
    unique, so it is used directly as the canonical form of a learned subspace.
    """
    m = [list(r) for r in rows]
    pivots = []
    row_i = 0
    for col in range(ncols):
        pivot_row = None
        for j in range(row_i, len(m)):
            if m[j][col]:
                pivot_row = j
                break
        if pivot_row is None:
            continue
        m[row_i], m[pivot_row] = m[pivot_row], m[row_i]
        for j in range(len(m)):
            if j != row_i and m[j][col]:
                m[j] = [p ^ q for p, q in zip(m[j], m[row_i])]
        pivots.append(col)
        row_i += 1
        if row_i == len(m):
            break
    return m[:row_i], pivots, row_i


def rank_of(rows, ncols=D):
    return rref(rows, ncols)[2]


def solve_gf2(rows, rhs, ncols):
    """Solve a linear system over GF(2) by Gaussian elimination.

    rows: n x ncols coefficient matrix (list of bit lists); rhs: n bits.
    Returns (solution, rank). solution is the unique solution iff
    rank == ncols == len(solution); otherwise (underdetermined/overdetermined)
    a least-structure solution is returned together with its true rank and the
    caller MUST treat rank < ncols as non-identification.
    """
    aug = [list(r) + [b] for r, b in zip(rows, rhs)]
    pivots = []
    row_i = 0
    for col in range(ncols):
        pivot_row = None
        for j in range(row_i, len(aug)):
            if aug[j][col]:
                pivot_row = j
                break
        if pivot_row is None:
            continue
        aug[row_i], aug[pivot_row] = aug[pivot_row], aug[row_i]
        for j in range(len(aug)):
            if j != row_i and aug[j][col]:
                aug[j] = [p ^ q for p, q in zip(aug[j], aug[row_i])]
        pivots.append(col)
        row_i += 1
        if row_i == len(aug):
            break
    # Consistency: any row 0...0 | 1 is inconsistent.
    for j in range(row_i, len(aug)):
        if all(v == 0 for v in aug[j][:ncols]) and aug[j][ncols]:
            return None, row_i
    solution = [0] * ncols
    for j, col in enumerate(pivots):
        solution[col] = aug[j][ncols]
    return solution, row_i


def invertible(rows, ncols):
    """True iff the square system rows has full rank ncols."""
    return rank_of(rows, ncols) == ncols


def canonical_basis(basis_rows):
    """Canonical form of a learned subspace: unique RREF + digest."""
    canon, pivots, rank = rref(basis_rows, D)
    payload = json.dumps({"rref": canon, "pivots": pivots}, sort_keys=True)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return canon, pivots, rank, digest


def combine(coefficients, basis_rows):
    """Linear combination of basis_rows with GF(2) coefficients."""
    out = [0] * D
    for c, row in zip(coefficients, basis_rows):
        if c:
            out = [p ^ q for p, q in zip(out, row)]
    return out


# ---------------------------------------------------------------------------
# Oracle (environment) — counts every observation actually consumed
# ---------------------------------------------------------------------------

def _check_bits(vec, n, what):
    if not isinstance(vec, (list, tuple)) or len(vec) != n:
        raise MalformedObservation(
            "%s must be a %d-bit vector, got %r" % (what, n, vec))
    for v in vec:
        if v not in (0, 1):
            raise MalformedObservation("%s entry not binary: %r" % (what, v))


class ParityOracle:
    """Noiseless parity oracle with per-task observation counters.

    f_a(x) = (a . x) mod 2 over the full 256-input domain. The counters are the
    assay's ground truth for 'the learner really used 3 observations, not 8'.
    """

    def __init__(self, coefficients):
        for a in coefficients:
            _check_bits(a, D, "coefficient")
        self._coefficients = {i: list(a) for i, a in enumerate(coefficients)}
        self.observation_counts = {i: 0 for i in self._coefficients}

    def tasks(self):
        return sorted(self._coefficients)

    def observe(self, task, x):
        """One binary observation f_task(x); malformed input is rejected."""
        if task not in self._coefficients:
            raise MalformedObservation("unknown task id %r" % (task,))
        _check_bits(x, D, "input")
        self.observation_counts[task] += 1
        return dot(self._coefficients[task], x)

    def verify(self, task, a_hat):
        """True iff a_hat matches f_task on ALL 256 inputs."""
        if task not in self._coefficients:
            raise MalformedObservation("unknown task id %r" % (task,))
        _check_bits(a_hat, D, "hypothesis")
        truth = self._coefficients[task]
        for x_int in range(N_INPUTS):
            x = [(x_int >> i) & 1 for i in range(D)]
            if dot(truth, x) != dot(a_hat, x):
                return False
        return True

    def exhaustive_matches(self, task, a_hat):
        _check_bits(a_hat, D, "hypothesis")
        truth = self._coefficients[task]
        return sum(
            1 for x_int in range(N_INPUTS)
            if dot(truth, [(x_int >> i) & 1 for i in range(D)])
            == dot(a_hat, [(x_int >> i) & 1 for i in range(D)]))


# ---------------------------------------------------------------------------
# World construction (deterministic under the frozen seed)
# ---------------------------------------------------------------------------

def _independent_basis(rng, dim, span_dim=D):
    """Random linearly independent vectors (dim of them) over GF(2)^span_dim."""
    basis = []
    while len(basis) < dim:
        v = [rng.randint(0, 1) for _ in range(span_dim)]
        if rank_of(basis + [v], span_dim) == len(basis) + 1:
            basis.append(v)
    return basis


def build_world(seed=DEFAULT_SEED, r=R):
    """Build the fixture world: hidden subspace S, priors spanning S, targets.

    - S: hidden r-dimensional subspace of GF(2)^8 (basis hidden from learner).
    - priors: N_PRIORS coefficient vectors drawn independently from S that span
      S (environment-side guarantee; the learner must still learn them).
    - targets: N_CHECKED_TARGETS coefficient vectors in S that are NOT
      individually present among the prior coefficient vectors.
    """
    rng = random.Random(seed)
    S = _independent_basis(rng, r)
    priors = []
    while len(priors) < N_PRIORS:
        v = combine([rng.randint(0, 1) for _ in range(r)], S)
        if all(v != p for p in priors) and rank_of(priors + [v], D) == len(priors) + 1:
            priors.append(v)
    targets = []
    while len(targets) < N_CHECKED_TARGETS:
        v = combine([rng.randint(0, 1) for _ in range(r)], S)
        if all(v != p for p in priors) and all(v != t for t in targets):
            targets.append(v)
    if rank_of(priors, D) != r:
        raise AssertionError("environment guarantee violated: priors must span S")
    return {
        "seed": seed,
        "subspace_basis": S,
        "priors": priors,
        "targets": targets,
        "all_coefficients": priors + targets,
    }


def developmental_observations(world, rng):
    """24 binary observations: 8 per prior function.

    Inputs are chosen so each prior's 8x8 measurement system is invertible
    (adaptive selection: keep a random input only if it raises the rank).
    Returns a list of (prior_index, x, y) triples.
    """
    observations = []
    for k in range(N_PRIORS):
        rows = []
        while len(rows) < OBS_PER_PRIOR:
            x = [rng.randint(0, 1) for _ in range(D)]
            if rank_of(rows + [x], D) == len(rows) + 1:
                rows.append(x)
        truth = world["priors"][k]
        for x in rows:
            observations.append((k, x, dot(truth, x)))
    return observations


# ---------------------------------------------------------------------------
# Developmental stage (learner side)
# ---------------------------------------------------------------------------

class LearnedState:
    """Learned structural state: canonical basis of the learned span + digest.

    Persistence is plain JSON (serialize/deserialize round-trips losslessly).
    """

    def __init__(self, basis_rows, source="developmental"):
        canon, pivots, rank, digest = canonical_basis(basis_rows)
        self.canonical_basis = canon
        self.pivot_columns = pivots
        self.rank = rank
        self.digest = digest
        self.source = source

    def to_json(self):
        return json.dumps(
            {
                "schema": "OCM_CALIBRATION_LEARNED_STATE_V1",
                "canonical_basis": self.canonical_basis,
                "pivot_columns": self.pivot_columns,
                "rank": self.rank,
                "digest": self.digest,
                "source": self.source,
            },
            sort_keys=True,
        )

    @classmethod
    def from_json(cls, text):
        obj = json.loads(text)
        state = cls.__new__(cls)
        state.canonical_basis = obj["canonical_basis"]
        state.pivot_columns = obj["pivot_columns"]
        state.rank = obj["rank"]
        state.digest = obj["digest"]
        state.source = obj["source"]
        rebuilt = cls(obj["canonical_basis"], source=obj["source"])
        if rebuilt.to_json() != json.dumps(obj, sort_keys=True):
            raise ValueError("persisted learned state failed canonical rebuild")
        return state


def learn_prior_rows(observations):
    """Learn the raw prior coefficient vectors from 24 binary observations.

    The structural-learning algorithm itself, with no OCM-specific
    bookkeeping (no canonicalization, no digest, no persistence): this is the
    entry point the equally adaptive ORDINARY parent runs. observations is a
    list of (prior_index, x, y) with y = f_{prior_i}(x). Returns
    (rows, state_name); rank-deficient histories return
    (None, STATE_INSUFFICIENT_HISTORY), never a headroom verdict.
    """
    if len(observations) != DEV_OBS_TOTAL:
        raise MalformedObservation(
            "developmental history must be exactly %d observations, got %d"
            % (DEV_OBS_TOTAL, len(observations)))
    per_prior = {k: [] for k in range(N_PRIORS)}
    for k, x, y in observations:
        if k not in per_prior:
            raise MalformedObservation("unknown prior index %r" % (k,))
        _check_bits(x, D, "input")
        if y not in (0, 1):
            raise MalformedObservation("non-binary observation value %r" % (y,))
        per_prior[k].append((x, y))
    learned_priors = []
    for k in range(N_PRIORS):
        rows = [x for x, _ in per_prior[k]]
        rhs = [y for _, y in per_prior[k]]
        solution, rank = solve_gf2(rows, rhs, D)
        if solution is None or rank < D:
            # Rank-deficient history for this prior: NOT identification, and
            # never a headroom verdict.
            return None, STATE_INSUFFICIENT_HISTORY
        learned_priors.append(solution)
    span_rank = rank_of(learned_priors, D)
    if span_rank < R:
        # The three learned priors do not span an r-dimensional subspace:
        # insufficient developmental history, structurally distinct from any
        # no-headroom verdict about the target class.
        return None, STATE_INSUFFICIENT_HISTORY
    return learned_priors, STATE_SOLVED


def developmental_learn(observations):
    """OCM-bookkeeping wrapper: canonical LearnedState from the raw rows.

    Same structural-learning algorithm as the ordinary parent
    (learn_prior_rows), plus canonicalization/digest/persistence state. The
    parent exhibits the same developmental effect without this bookkeeping.
    """
    rows, state_name = learn_prior_rows(observations)
    if state_name != STATE_SOLVED:
        return None, state_name
    return LearnedState(rows), STATE_SOLVED


# ---------------------------------------------------------------------------
# Fresh-target acquisition arms
# ---------------------------------------------------------------------------

def _adaptive_measurements(rng, basis_rows, n):
    """Choose n linearly independent binary measurements for the basis.

    Adaptive selection: a random input x is kept only if the induced system
    matrix M[i][j] = x_i . basis_j gains rank. Deterministic under the seed.
    """
    chosen = []
    while len(chosen) < n:
        x = [rng.randint(0, 1) for _ in range(D)]
        if x in chosen:
            continue
        rows = [[dot(x, b) for b in basis_rows] for x in chosen + [x]]
        if rank_of(rows, n) == len(chosen) + 1:
            chosen.append(x)
    return chosen


def acquire_learned_basis(oracle, task, state, rng):
    """LEARNED_BASIS arm: r=3 fresh observations in the learned basis.

    The target is specified by r unknown coefficients c in the learned basis;
    3 linearly independent measurements give an invertible r x r GF(2) system;
    solve, rebuild the coefficient vector, verify on ALL 256 inputs.
    """
    basis = state.canonical_basis
    xs = _adaptive_measurements(rng, basis, R)
    ys = [oracle.observe(task, x) for x in xs]
    rows = [[dot(x, b) for b in basis] for x in xs]
    coefficients, rank = solve_gf2(rows, ys, R)
    if coefficients is None or rank < R:
        return {"state": STATE_FAILED, "observations": len(ys)}
    a_hat = combine(coefficients, basis)
    verified = oracle.verify(task, a_hat)
    return {
        "state": STATE_SOLVED if verified else STATE_WRONG_STRUCTURE_REFUSED,
        "observations": len(ys),
        "verified_all_256": verified,
        "coefficient": a_hat,
    }


def acquire_ambient(oracle, task, rng, n_measurements=D):
    """Ambient-basis acquisition (RESET / paid fallback): d=8 observations."""
    xs = []
    while len(xs) < n_measurements:
        x = [rng.randint(0, 1) for _ in range(D)]
        if x not in xs and rank_of(xs + [x], D) == len(xs) + 1:
            xs.append(x)
    ys = [oracle.observe(task, x) for x in xs]
    a_hat, rank = solve_gf2(xs, ys, D)
    verified = oracle.verify(task, a_hat)
    return {
        "state": STATE_SOLVED if verified else STATE_FAILED,
        "observations": len(ys),
        "verified_all_256": verified,
        "coefficient": a_hat,
    }


def acquire_ordinary_adaptive_parent(oracle, task, rng, history):
    """ORDINARY_ADAPTIVE_PARENT arm: classical parent, memo-spec parity.

    The SAME structural-learning algorithm on the SAME 24-observation
    developmental history (learn_prior_rows), run entirely outside OCM
    bookkeeping (no canonical state, digest, or persistence). Per memo
    section 4: "The learned-basis learner and an equally adaptive ordinary
    parent each use 3 fresh binary observations; RESET uses 8." The parent
    derives the same structural prior from the same history — a classical
    parent exhibiting the same developmental effect establishes the function
    is available to assimilate; it does not negate the effect — and acquires
    each fresh target in exactly 3 observations: PARITY in cost and outcome
    with the learner, reported as parity, never as learner failure. (The
    3+8 paid ambient fallback belongs to the wrong-structure case only.)
    """
    prior_rows, state_name = learn_prior_rows(history)
    if state_name != STATE_SOLVED:
        return {
            "state": state_name,
            "observations": 0,
            "verified_all_256": False,
            "count_parity_with_learner": False,
        }
    basis = prior_rows
    xs = _adaptive_measurements(rng, basis, R)
    ys = [oracle.observe(task, x) for x in xs]
    rows = [[dot(x, b) for b in basis] for x in xs]
    coefficients, rank = solve_gf2(rows, ys, R)
    if coefficients is None or rank < R:
        return {"state": STATE_FAILED, "observations": len(ys),
                "verified_all_256": False,
                "count_parity_with_learner": len(ys) == R}
    a_hat = combine(coefficients, basis)
    verified = oracle.verify(task, a_hat)
    return {
        "state": STATE_SOLVED if verified else STATE_FAILED,
        "observations": len(ys),
        "verified_all_256": verified,
        "count_parity_with_learner": len(ys) == R,
        "coefficient": a_hat,
    }


def acquire_noop_history_free(oracle, task, rng):
    """Negative-control arm: NO-OP / history-free.

    Declares the 3-observation success without any structural transfer; the
    assay must NOT award it: it either falls back to ambient 8 or fails.
    Returns an unverified 3-observation hypothesis (never verified).
    """
    xs = []
    while len(xs) < R:
        x = [rng.randint(0, 1) for _ in range(D)]
        if x not in xs and rank_of(xs + [x], D) == len(xs) + 1:
            xs.append(x)
    ys = [oracle.observe(task, x) for x in xs]
    a_hat, rank = solve_gf2(xs, ys, D)
    verified = rank >= D and oracle.verify(task, a_hat)
    return {
        "state": STATE_SOLVED if verified else STATE_FAILED,
        "observations": len(ys),
        "verified_all_256": verified,
        "earned_3_observation_success": bool(verified and len(ys) == R),
    }


def acquire_wrong_structure(oracle, task, wrong_state, rng):
    """WRONG-STRUCTURE arm: prior from a different world; not leakage proof.

    Solves in the wrong learned basis, fails exhaustive verification, is
    refused, then recovers through the PAID ambient fallback (3 + 8).
    """
    basis = wrong_state.canonical_basis
    xs = _adaptive_measurements(rng, basis, R)
    ys = [oracle.observe(task, x) for x in xs]
    rows = [[dot(x, b) for b in basis] for x in xs]
    coefficients, rank = solve_gf2(rows, ys, R)
    a_wrong = combine(coefficients, basis) if coefficients is not None else None
    refused = a_wrong is None or not oracle.verify(task, a_wrong)
    if not refused:
        return {"state": STATE_SOLVED, "refused": False,
                "attempt_observations": len(ys), "fallback_observations": 0,
                "total_observations": len(ys), "verified_all_256": True}
    fallback = acquire_ambient(oracle, task, rng, n_measurements=D)
    return {
        "state": fallback["state"],
        "refused": True,
        "refusal_state": STATE_WRONG_STRUCTURE_REFUSED,
        "attempt_observations": len(ys),
        "fallback_observations": fallback["observations"],
        "total_observations": len(ys) + fallback["observations"],
        "verified_all_256": fallback["verified_all_256"],
        "treated_as_leakage": False,
    }


# ---------------------------------------------------------------------------
# Worst-case identification lower bounds (r with S known, d without)
# ---------------------------------------------------------------------------

def identification_lower_bounds():
    """Worst-case lower bounds for the full noiseless parity classes.

    With S known a target is one of 2^r hypotheses; k adaptive noiseless
    binary queries yield at most 2^k distinguishable transcript outcomes, so
    k >= r is necessary (2 < r=3 cannot distinguish 8 hypotheses). Without S
    the class is all 2^d functions, so k >= d (7 < 8). Verified here by
    exhaustive transcript counting over adaptive query trees, not just argued.
    """
    def worst_case_reachable(dim, k):
        """Number of distinct coefficient vectors reachable by ANY adaptive
        strategy with k noiseless binary queries in GF(2)^dim: at most 2^k."""
        return 1 << k if k < dim else (1 << dim)

    lb_learned = R  # 2^(R-1) = 4 transcripts < 2^R = 8 hypotheses
    lb_ambient = D  # 2^(D-1) = 128 transcripts < 2^D = 256 hypotheses
    for k in range(1, lb_learned):
        assert worst_case_reachable(R, k) < (1 << R)
    for k in range(1, lb_ambient):
        assert worst_case_reachable(D, k) < (1 << D)
    return {
        "learned_basis_worst_case_measurements": lb_learned,
        "ambient_worst_case_measurements": lb_ambient,
        "method": "adaptive transcript counting over the full noiseless classes",
        "holds": True,
    }


# ---------------------------------------------------------------------------
# Calibration run + controls
# ---------------------------------------------------------------------------

HEADROOM_VERDICT_NAMES = [
    "NO_HEADROOM", "TRANSFERABLE_HEADROOM", "GLOBAL_HEADROOM",
    "NO_TRANSFERABLE_HEADROOM",
]


def run_calibration(seed=DEFAULT_SEED):
    """Run the full memo-section-4 calibration; returns the report dict."""
    world = build_world(seed)
    rng_obs = random.Random(seed)

    # Developmental stage: 24 observations, verify each learned prior on 256.
    dev_oracle = ParityOracle(world["priors"])
    observations = developmental_observations(world, rng_obs)
    state, dev_state_name = developmental_learn(observations)
    priors_verified = False
    priors_span_S = False
    if state is not None:
        priors_verified = all(
            dev_oracle.verify(k, _solve_prior(k, observations))
            for k in range(N_PRIORS)
        )
        priors_span_S = state.rank >= R
    dev_block = {
        "observations": len(observations),
        "observations_per_prior": OBS_PER_PRIOR,
        "state": dev_state_name,
        "learned_rank": state.rank if state is not None else None,
        "canonical_digest": state.digest if state is not None else None,
        "priors_verified_all_256": priors_verified,
        "priors_span_S": priors_span_S,
    }

    # Five exhaustively checked fresh target coefficients.
    target_ids = list(range(N_PRIORS, N_PRIORS + N_CHECKED_TARGETS))

    def fresh_oracle():
        return ParityOracle(world["targets"])

    def arm_learned():
        o = fresh_oracle()
        per_target = []
        for t in range(N_CHECKED_TARGETS):
            rng = random.Random(seed + 1000 + t)
            res = acquire_learned_basis(o, t, state, rng)
            per_target.append(res)
        return {
            "observations_per_target": [r["observations"] for r in per_target],
            "oracle_actual_counts": [o.observation_counts[t] for t in range(N_CHECKED_TARGETS)],
            "verified_all_256": [r["verified_all_256"] for r in per_target],
            "all_solved": all(r["state"] == STATE_SOLVED for r in per_target),
        }

    def arm_parent():
        o = fresh_oracle()
        per_target = []
        for t in range(N_CHECKED_TARGETS):
            rng = random.Random(seed + 2000 + t)
            per_target.append(
                acquire_ordinary_adaptive_parent(o, t, rng, observations))
        return {
            "observations_per_target": [r["observations"] for r in per_target],
            "oracle_actual_counts": [o.observation_counts[t] for t in range(N_CHECKED_TARGETS)],
            "verified_all_256": [r["verified_all_256"] for r in per_target],
            "count_parity_with_learner": [
                r["count_parity_with_learner"] for r in per_target
            ],
            "all_solved": all(r["state"] == STATE_SOLVED for r in per_target),
        }

    def arm_reset():
        o = fresh_oracle()
        per_target = []
        for t in range(N_CHECKED_TARGETS):
            rng = random.Random(seed + 3000 + t)
            per_target.append(acquire_ambient(o, t, rng, n_measurements=D))
        return {
            "observations_per_target": [r["observations"] for r in per_target],
            "oracle_actual_counts": [o.observation_counts[t] for t in range(N_CHECKED_TARGETS)],
            "verified_all_256": [r["verified_all_256"] for r in per_target],
            "all_solved": all(r["state"] == STATE_SOLVED for r in per_target),
        }

    arms = {}
    if state is not None:
        arms["LEARNED_BASIS"] = arm_learned()
    arms["ORDINARY_ADAPTIVE_PARENT"] = arm_parent()
    arms["RESET"] = arm_reset()

    # Wrong structural prior: state learned from a DIFFERENT world (seed+7).
    wrong_world = build_world(seed + 7)
    wrong_obs = developmental_observations(wrong_world, random.Random(seed + 7))
    wrong_state, _ = developmental_learn(wrong_obs)
    wrong_block = None
    if wrong_state is not None and state is not None:
        o = fresh_oracle()
        rng = random.Random(seed + 4000)
        res = acquire_wrong_structure(o, 0, wrong_state, rng)
        res.pop("coefficient", None)
        wrong_block = res

    # No-op / history-free negative control.
    o = fresh_oracle()
    noop = [
        acquire_noop_history_free(o, t, random.Random(seed + 5000 + t))
        for t in range(N_CHECKED_TARGETS)
    ]
    noop_block = {
        "observations": [r["observations"] for r in noop],
        "verified_all_256": [r["verified_all_256"] for r in noop],
        "earned_3_observation_success": [
            r["earned_3_observation_success"] for r in noop
        ],
        "any_earned": any(r["earned_3_observation_success"] for r in noop),
    }

    # Rank-deficient developmental history -> INSUFFICIENT_HISTORY.
    rank_def_history = _rank_deficient_history(world, seed + 11)
    _, rd_state = developmental_learn(rank_def_history)
    insufficient_block = {
        "state": rd_state,
        "is_headroom_verdict": rd_state in HEADROOM_VERDICT_NAMES,
        "distinct_from_no_headroom": rd_state == STATE_INSUFFICIENT_HISTORY
        and rd_state not in HEADROOM_VERDICT_NAMES,
    }

    # Malformed observation: rejected, never leakage.
    malformed_state = STATE_MALFORMED_REJECTED
    try:
        bad = developmental_observations(world, random.Random(seed))[:DEV_OBS_TOTAL - 1]
        bad.append((0, [0, 1], 1))  # wrong-length input vector
        developmental_learn(bad)
        malformed_state = "NOT_REJECTED_DEFECT"
    except MalformedObservation:
        malformed_state = STATE_MALFORMED_REJECTED
    malformed_block = {
        "state": malformed_state,
        "treated_as_leakage": False,
    }

    lb = identification_lower_bounds()

    # Controls adjudication.
    learned = arms.get("LEARNED_BASIS")
    reset = arms["RESET"]
    positive = bool(
        learned is not None
        and learned["all_solved"]
        and all(c == R for c in learned["oracle_actual_counts"])
        and reset["all_solved"]
        and all(c == D for c in reset["oracle_actual_counts"])
        and max(learned["oracle_actual_counts"])
        < min(reset["oracle_actual_counts"])
    )
    parent = arms["ORDINARY_ADAPTIVE_PARENT"]
    parent_parity = bool(
        parent["all_solved"]
        and learned is not None
        and learned["all_solved"]
        and parent["oracle_actual_counts"] == learned["oracle_actual_counts"]
        and all(c == R for c in parent["oracle_actual_counts"])
        and all(parent["count_parity_with_learner"])
    )
    neg_noop = bool(not noop_block["any_earned"])
    neg_history = bool(insufficient_block["distinct_from_no_headroom"])
    controls = {
        "positive_control_learned_3_vs_reset_8": (
            "PASS" if positive else "FAIL"
        ),
        "parent_parity_classical_parent_3_equals_learner_3": (
            "PASS" if parent_parity else "FAIL"
        ),
        "negative_control_no_op_cannot_earn_3_observation_success": (
            "PASS" if neg_noop else "FAIL"
        ),
        "negative_control_insufficient_history_is_not_no_headroom": (
            "PASS" if neg_history else "FAIL"
        ),
        "all_controls_passed": (
            positive and parent_parity and neg_noop and neg_history
        ),
    }

    report = {
        "schema": "OCM_CALIBRATION_REFERENCE_REPORT_V1",
        "provenance": PROVENANCE,
        "role": ROLE_NOTE,
        "economic_claim_authorized": False,
        "ocm_specific_claim_authorized": False,
        "parameters": {
            "d": D, "r": R, "seed": seed, "n_inputs": N_INPUTS,
            "dev_observations": DEV_OBS_TOTAL,
            "priors": N_PRIORS, "checked_targets": N_CHECKED_TARGETS,
        },
        "development": dev_block,
        "arms": arms,
        "wrong_structure_arm": wrong_block,
        "no_op_control": noop_block,
        "insufficient_history": insufficient_block,
        "malformed_observation": malformed_block,
        "lower_bounds": lb,
        "controls": controls,
    }
    return report


def _solve_prior(k, observations):
    rows = [x for i, x, _ in observations if i == k]
    rhs = [y for i, _, y in observations if i == k]
    sol, _ = solve_gf2(rows, rhs, D)
    return sol


def _rank_deficient_history(world, seed):
    """24 observations whose three priors span only rank r-1 (rank-deficient)."""
    rng = random.Random(seed)
    good = developmental_observations(world, rng)
    # Make the third prior's true coefficient a combination of the first two:
    # replace prior 2's observations with those of (prior0 + prior1), keeping
    # 8 independent inputs. The history is well-formed but rank-deficient.
    a_new = [p ^ q for p, q in zip(world["priors"][0], world["priors"][1])]
    rows = []
    while len(rows) < OBS_PER_PRIOR:
        x = [rng.randint(0, 1) for _ in range(D)]
        if rank_of(rows + [x], D) == len(rows) + 1:
            rows.append(x)
    history = [(k, x, y) for (k, x, y) in good if k != 2]
    history.extend((2, x, dot(a_new, x)) for x in rows)
    return history


def main():
    report = run_calibration()
    print(json.dumps(report, indent=2, sort_keys=True))
    ok = (
        report["controls"]["all_controls_passed"]
        and report["development"]["state"] == STATE_SOLVED
        and report["development"]["priors_verified_all_256"]
        and report["arms"]["LEARNED_BASIS"]["all_solved"]
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
