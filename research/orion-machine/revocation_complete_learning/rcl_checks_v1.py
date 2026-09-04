"""Revocation-Complete Learning exact checks V1.

Repairs the three ``VACUOUS_CONTRAST`` controls recorded against the V0 checkers
(``OCM_FAILURE_LEDGER.md``, audit row ``IA-07`` of ``OCM_SNAPSHOT_V1.json``,
deliverable ``D09`` of ``OCM_TASK_LEDGER_V1.json``):

1. ``rcl_checks_core.verify_storage_query_frontier`` reconstructed from
   ``bits[:stored] + bits[stored:]`` (the identity for every ``stored``) and wrote
   ``"exact": True`` as a literal.  Here the summary really withholds the
   unstored coordinates, the queries are issued against the *profile* through a
   charged coordinate oracle, the reconstructor returns the full *deduplicated*
   candidate set compatible with what it holds, and exactness is *computed*.
   Splits with ``S + Q < N`` must exhibit an explicit collision pair and a
   candidate set of exactly ``2^(N-S-Q)`` distinct members containing the truth;
   splits with ``S + Q >= N`` must reconstruct every profile.  Every arm can fail
   (a first draft's below-frontier arm could not — VACUOUS_CONTRAST, Cursor
   Bugbot on PR #281 — repaired here with mutation M6 registered against it).
2. ``rcl_checks_finish.verify_controls`` flipped one bit of a *copied* signature
   and compared the copy to the original (true for every boolean vector).  Here
   each mutation is applied to the object under test (``live``, ``signature``,
   the coordinate oracle, the reconstructor), the mutation is asserted applied on
   a witness *before* the check runs, and the check must then fail for the
   registered semantic reason.
3. The same function built its no-alarm control from ``live(full, revoked)``
   stored twice (``x == x``).  Here three *distinct* complete updaters are
   compared over every antichain and every revocation at ``n = 4``, and a
   fourth, deliberately incomplete updater (positive-only) is required to
   disagree on the RCL-2b case inside the same call.

The V0 modules are not modified: they are hash-bound inside
``RCL_INDEPENDENT_REVIEW_PACKET_V0.json`` / ``_V1.json`` and checkbox RCL-R03 of
issue #245 is chartered to test exactly them.  This module imports V0's *model*
(``rcl_model``) so the objects checked are the committed ones.

Exit-code contract (``run_v1_self_test`` / ``rcl_oracle_v1.py``):
``0`` every check passed; ``1`` a check failed for its registered reason;
``2`` a check could not be run (missing module, cap violated).  ``2`` is never
reported as a pass.

Withdrawal scope carried forward from the ledger: the
``FINITE_CONSTRUCTION_GREEN`` half of RCL-1c and the figure ``5329`` are withdrawn
with V0; the hand proof of RCL-1c is untouched.  This module supplies a *new*
finite construction receipt with its own denominators; it does not restore the
withdrawn figure.
"""

from __future__ import annotations

import itertools
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

_LANE = Path(__file__).resolve().parent
if str(_LANE) not in sys.path:
    sys.path.insert(0, str(_LANE))

try:  # pragma: no cover - import guard is the CANNOT_CHECK route
    from rcl_model import (  # type: ignore[import-not-found]
        MAX_EXHAUSTIVE_N,
        Profile,
        alternative_bits,
        canonical_profile,
        enumerate_antichains,
        first_difference,
        fixed_certificate_profiles,
        live,
        live_via_active_set,
        powerset,
        profile_from_bits,
        signature,
    )
except Exception as exc:  # pragma: no cover
    raise ImportError(f"CANNOT_CHECK: rcl_model V0 unavailable: {exc}") from exc


class CannotCheck(RuntimeError):
    """Raised when a check cannot be run.  Never a pass."""


LiveFn = Callable[[Profile, frozenset[int]], bool]
SignatureFn = Callable[[Profile, int], tuple[bool, ...]]
OracleFn = Callable[[Profile, int, int], bool]
ReconstructFn = Callable[[Sequence[bool], int], Profile]


# ----------------------------------------------------------------------------
# 1. Storage / query frontier with a real withheld summary and a real oracle
# ----------------------------------------------------------------------------

def coordinate_oracle(profile: Profile, index: int, n: int, live_fn: LiveFn = live) -> bool:
    """One charged coordinate query: is alternative warrant ``J_index`` present?

    Implemented through the RCL-1b revocation ``R_index = E \\ J_index`` applied to
    the *profile* through ``live_fn`` — the query reads the object, not a
    precomputed bit vector.
    """
    _, alternatives, _ = fixed_certificate_profiles(n)
    if not 0 <= index < len(alternatives):
        raise ValueError("coordinate index out of range")
    revocation = frozenset(range(n)) - alternatives[index]
    return bool(live_fn(profile, revocation))


def candidate_profiles(
    known: dict[int, bool], n: int, reconstruct: ReconstructFn = profile_from_bits
) -> tuple[Profile, ...]:
    """Every profile compatible with the coordinates the protocol actually holds."""
    _, alternatives, _ = fixed_certificate_profiles(n)
    total = len(alternatives)
    unknown = [j for j in range(total) if j not in known]
    out: dict[Profile, None] = {}  # deduplicated, insertion-ordered: distinct hypotheses only
    for fill in itertools.product((False, True), repeat=len(unknown)):
        bits = [False] * total
        for j, value in known.items():
            bits[j] = value
        for j, value in zip(unknown, fill, strict=True):
            bits[j] = value
        out[reconstruct(tuple(bits), n)] = None
    return tuple(out)


def verify_storage_query_frontier_v1(
    max_n: int = 5,
    *,
    live_fn: LiveFn = live,
    oracle: OracleFn | None = None,
    reconstruct: ReconstructFn = profile_from_bits,
) -> dict[str, object]:
    """RCL-1c finite construction, redone with a withheld summary.

    For every ``n <= max_n``, every stored prefix length ``S`` and every query
    budget ``Q`` with ``S + Q <= N``:

    * the summary stores coordinates ``0..S-1`` (the rest are withheld);
    * the protocol queries coordinates ``S..S+Q-1`` through ``oracle``;
    * the reconstructor returns the full candidate set;
    * ``exact`` is computed as ``len(candidates) == 1 and candidates[0] == profile``.

    The theorem predicts ``exact`` iff ``S + Q >= N``.  Below the frontier the
    check must additionally *exhibit* a collision pair: two profiles with
    identical stored bits and identical oracle answers whose full revocation
    signatures differ.

    Two further assertions make the below-frontier arm falsifiable rather than
    true by construction (a first draft asserted only "not every profile is
    exact", which no reconstructor could violate because the candidate list was
    never deduplicated -- VACUOUS_CONTRAST, found by Cursor Bugbot on PR #281):

    * soundness: the true profile is among the (deduplicated) candidates;
    * completeness: the candidate set has exactly ``2^(N - S - Q)`` *distinct*
      members -- a reconstructor that collapses fillings (mutation M6) or drops a
      coordinate (M4) makes this fail below the frontier.
    """
    if oracle is None:
        def oracle(profile: Profile, index: int, n: int) -> bool:
            return coordinate_oracle(profile, index, n, live_fn)
    if max_n < 1:
        raise CannotCheck("max_n must be at least 1")
    cases: list[dict[str, object]] = []
    exact_checks = 0
    completeness_checks = 0
    collision_pairs = 0
    below_frontier_splits = 0
    on_frontier_splits = 0
    for n in range(1, max_n + 1):
        _, alternatives, profiles = fixed_certificate_profiles(n)
        total = len(alternatives)
        points: list[dict[str, object]] = []
        for stored in range(total + 1):
            for queries in range(total - stored + 1):
                predicted_exact = stored + queries >= total
                observed_exact_all = True
                transcripts: dict[tuple[tuple[bool, ...], tuple[bool, ...]], Profile] = {}
                collision: dict[str, object] | None = None
                for profile in profiles:
                    truth = alternative_bits(profile, n)
                    stored_bits = tuple(truth[:stored])
                    answers = tuple(oracle(profile, j, n) for j in range(stored, stored + queries))
                    known = {j: stored_bits[j] for j in range(stored)}
                    known.update({stored + k: answers[k] for k in range(queries)})
                    candidates = candidate_profiles(known, n, reconstruct)
                    exact_here = len(candidates) == 1 and candidates[0] == profile
                    exact_checks += 1
                    if predicted_exact and not exact_here:
                        raise AssertionError(
                            f"n={n} S={stored} Q={queries}: theorem predicts exact "
                            f"reconstruction, observed candidate set of size {len(candidates)}"
                        )
                    if profile not in candidates:
                        raise AssertionError(
                            f"n={n} S={stored} Q={queries}: reconstruction unsound, true profile "
                            "not among the candidates"
                        )
                    expected_distinct = 2 ** (total - stored - queries)
                    if len(candidates) != expected_distinct:
                        raise AssertionError(
                            f"n={n} S={stored} Q={queries}: expected {expected_distinct} distinct "
                            f"candidates, observed {len(candidates)}"
                        )
                    completeness_checks += 1
                    observed_exact_all = observed_exact_all and exact_here
                    key = (stored_bits, answers)
                    if key in transcripts and collision is None:
                        other = transcripts[key]
                        if other == profile:
                            raise AssertionError("duplicate profile in fixed-certificate family")
                        witness = first_difference(other, profile, n)
                        if witness is None:
                            raise AssertionError("colliding transcripts but identical signatures")
                        collision = {
                            "profile_a_bits": alternative_bits(other, n),
                            "profile_b_bits": truth,
                            "distinguishing_revocation": sorted(witness),
                        }
                    transcripts.setdefault(key, profile)
                if predicted_exact:
                    on_frontier_splits += 1
                    if not observed_exact_all:
                        raise AssertionError("frontier split not exact")
                else:
                    below_frontier_splits += 1
                    if observed_exact_all:
                        raise AssertionError(
                            f"n={n} S={stored} Q={queries}: below the frontier yet every "
                            "profile reconstructed exactly"
                        )
                    if collision is None:
                        raise AssertionError(
                            f"n={n} S={stored} Q={queries}: below the frontier but no "
                            "collision pair exhibited"
                        )
                    collision_pairs += 1
                points.append(
                    {
                        "stored_bits": stored,
                        "queried_coordinates": queries,
                        "sum": stored + queries,
                        "theorem_predicts_exact": predicted_exact,
                        "observed_exact": observed_exact_all,
                        "collision": collision,
                    }
                )
        cases.append(
            {
                "n": n,
                "variable_warrant_bits": total,
                "profile_count": len(profiles),
                "frontier_points": points,
            }
        )
    return {
        "max_n": max_n,
        "reconstruction_checks": exact_checks,
        "distinct_candidate_completeness_checks": completeness_checks,
        "splits_on_or_above_frontier": on_frontier_splits,
        "splits_below_frontier": below_frontier_splits,
        "collision_pairs_exhibited": collision_pairs,
        "all_predictions_matched": True,
        "cases": cases,
    }


# ----------------------------------------------------------------------------
# 2. Mutation controls applied to the object under test
# ----------------------------------------------------------------------------

def _witness_profile() -> tuple[Profile, frozenset[int]]:
    return canonical_profile([{0, 1}, {2, 3}]), frozenset({0, 2})


def verify_injectivity_with(sig_fn: SignatureFn, n: int = 4) -> bool:
    profiles = enumerate_antichains(n)
    return len({sig_fn(profile, n) for profile in profiles}) == len(profiles)


def verify_mutation_controls_v1() -> dict[str, object]:
    """Each mutation: assert applied on a witness, then assert the check fails."""
    if MAX_EXHAUSTIVE_N < 4:
        raise CannotCheck("exhaustive enumeration cap below n=4")
    witness, revoked = _witness_profile()
    results: dict[str, dict[str, object]] = {}

    # M1: live() that ignores the revocation set.
    def live_ignoring_revocation(profile: Profile, _revoked: frozenset[int]) -> bool:
        return len(profile) > 0

    applied = live_ignoring_revocation(witness, revoked) != live(witness, revoked)
    if not applied:
        raise AssertionError("M1 mutation not applied on witness")

    def sig_m1(profile: Profile, n: int) -> tuple[bool, ...]:
        return tuple(live_ignoring_revocation(profile, r) for r in powerset(tuple(range(n))))

    results["M1_live_ignores_revocation"] = {
        "applied": True,
        "injectivity_survives": verify_injectivity_with(sig_m1),
    }
    if results["M1_live_ignores_revocation"]["injectivity_survives"]:
        raise AssertionError("M1 not detected: injectivity survived a liveness that ignores revocation")

    # M2: signature() that is constant.
    def sig_m2(profile: Profile, n: int) -> tuple[bool, ...]:
        return tuple(True for _ in powerset(tuple(range(n))))

    applied = sig_m2(witness, 4) != signature(witness, 4)
    if not applied:
        raise AssertionError("M2 mutation not applied on witness")
    results["M2_constant_signature"] = {
        "applied": True,
        "injectivity_survives": verify_injectivity_with(sig_m2),
    }
    if results["M2_constant_signature"]["injectivity_survives"]:
        raise AssertionError("M2 not detected")

    # M3: coordinate oracle that negates the answer.
    def oracle_m3(profile: Profile, index: int, n: int) -> bool:
        return not coordinate_oracle(profile, index, n)

    _, alternatives, profiles = fixed_certificate_profiles(4)
    probe = next(p for p in profiles if alternative_bits(p, 4)[0])
    applied = oracle_m3(probe, 0, 4) != coordinate_oracle(probe, 0, 4)
    if not applied:
        raise AssertionError("M3 mutation not applied on witness")
    try:
        verify_storage_query_frontier_v1(4, oracle=oracle_m3)
        detected = False
    except AssertionError:
        detected = True
    results["M3_negated_coordinate_oracle"] = {"applied": True, "detected": detected}
    if not detected:
        raise AssertionError("M3 not detected: negated oracle passed the frontier check")

    # M4: reconstructor that drops the last coordinate.
    def reconstruct_m4(bits: Sequence[bool], n: int) -> Profile:
        if not bits:
            return profile_from_bits(bits, n)
        return profile_from_bits(tuple(bits[:-1]) + (False,), n)

    full_bits = tuple(True for _ in alternatives)
    applied = reconstruct_m4(full_bits, 4) != profile_from_bits(full_bits, 4)
    if not applied:
        raise AssertionError("M4 mutation not applied on witness")
    try:
        verify_storage_query_frontier_v1(4, reconstruct=reconstruct_m4)
        detected = False
    except AssertionError:
        detected = True
    results["M4_reconstructor_drops_last_coordinate"] = {"applied": True, "detected": detected}
    if not detected:
        raise AssertionError("M4 not detected")

    # M6: reconstructor that collapses every filling to one profile — the
    # below-frontier completeness arm must fail (candidate set of size 1 where
    # 2^(N-S-Q) distinct members are required), and soundness fails as well.
    def reconstruct_m6(bits: Sequence[bool], n: int) -> Profile:
        return profile_from_bits(tuple(False for _ in bits), n)

    applied = reconstruct_m6(full_bits, 4) != profile_from_bits(full_bits, 4)
    if not applied:
        raise AssertionError("M6 mutation not applied on witness")
    probe_known = {0: True}
    applied = applied and len(candidate_profiles(probe_known, 4, reconstruct_m6)) == 1 < len(candidate_profiles(probe_known, 4))
    if not applied:
        raise AssertionError("M6 mutation not applied: candidate set did not collapse")
    try:
        verify_storage_query_frontier_v1(4, reconstruct=reconstruct_m6)
        detected = False
        reason = ""
    except AssertionError as exc:
        detected = True
        reason = str(exc)
    results["M6_reconstructor_collapses_fillings"] = {"applied": True, "detected": detected, "failure": reason}
    if not detected or "candidates" not in reason:
        raise AssertionError("M6 not detected for the registered reason (candidate-set size)")

    # M5: a live() that is the *complement* — a broken updater the no-alarm
    # control must catch (used again in verify_no_alarm_v1).
    def live_complement(profile: Profile, r: frozenset[int]) -> bool:
        return not live(profile, r)

    applied = live_complement(witness, revoked) != live(witness, revoked)
    if not applied:
        raise AssertionError("M5 mutation not applied on witness")
    agreement = _updater_agreement((live, live_complement), 4)
    results["M5_complement_updater"] = {
        "applied": True,
        "agreement_fraction": agreement["agreement"] / agreement["denominator"],
        "detected": agreement["agreement"] != agreement["denominator"],
    }
    if not results["M5_complement_updater"]["detected"]:
        raise AssertionError("M5 not detected")

    # M0: unmutated — every check passes (the no-alarm half of the mutation suite).
    results["M0_unmutated"] = {
        "injectivity": verify_injectivity_with(signature),
        "frontier": verify_storage_query_frontier_v1(4)["all_predictions_matched"],
    }
    if not all(results["M0_unmutated"].values()):
        raise AssertionError("M0 unmutated suite failed")
    return {"mutations_planted": 6, "mutations_detected": 6, "cases": results}


# ----------------------------------------------------------------------------
# 3. No-alarm control across distinct complete updaters, with a planted
#    incomplete updater that must disagree in the same call
# ----------------------------------------------------------------------------

def live_from_signature(profile: Profile, revoked: frozenset[int], n: int) -> bool:
    """Third complete updater: look the answer up in the compiled signature."""
    atoms = tuple(range(n))
    index = next(i for i, r in enumerate(powerset(atoms)) if r == frozenset(revoked))
    return signature(profile, n)[index]


def _updater_agreement(updaters: Sequence[Callable[..., bool]], n: int) -> dict[str, int]:
    profiles = enumerate_antichains(n)
    agreement = 0
    denominator = 0
    for profile in profiles:
        for revoked in powerset(tuple(range(n))):
            answers = {bool(u(profile, revoked)) for u in updaters}
            denominator += 1
            agreement += int(len(answers) == 1)
    return {"agreement": agreement, "denominator": denominator}


def verify_no_alarm_v1(n: int = 4) -> dict[str, object]:
    if n > MAX_EXHAUSTIVE_N:
        raise CannotCheck("n above exhaustive cap")

    def u_scan(profile: Profile, revoked: frozenset[int]) -> bool:
        return live(profile, revoked)

    def u_active(profile: Profile, revoked: frozenset[int]) -> bool:
        return live_via_active_set(profile, revoked, n)

    def u_compiled(profile: Profile, revoked: frozenset[int]) -> bool:
        return live_from_signature(profile, revoked, n)

    complete = _updater_agreement((u_scan, u_active, u_compiled), n)
    if complete["agreement"] != complete["denominator"]:
        raise AssertionError("distinct complete updaters disagree")

    # Planted incomplete updater: sees only the first emitted warrant (RCL-2b).
    def u_positive_only(profile: Profile, revoked: frozenset[int]) -> bool:
        return live(profile[:1], revoked) if profile else False

    planted = _updater_agreement((u_scan, u_positive_only), n)
    full, revoked = _witness_profile()
    rcl_2b_fires = u_scan(full, frozenset({0})) and not u_positive_only(full, frozenset({0}))
    if planted["agreement"] == planted["denominator"] or not rcl_2b_fires:
        raise AssertionError("planted positive-only updater did not disagree")
    return {
        "n": n,
        "complete_updaters": 3,
        "agreement": complete["agreement"],
        "denominator": complete["denominator"],
        "planted_incomplete_updater_disagreements": planted["denominator"] - planted["agreement"],
        "rcl_2b_over_retraction_fires": rcl_2b_fires,
    }


# ----------------------------------------------------------------------------
# 3b. RSD is a fibre-wise VC dimension (Theorem E of the lane-200 record)
# ----------------------------------------------------------------------------

def vc_dimension(functions: Sequence[tuple[bool, ...]], domain_size: int, cap: int) -> int:
    """Brute-force VC dimension of a finite class of {0,1}-valued functions given as
    truth tables over ``range(domain_size)``; searches shattered sets up to ``cap``."""
    best = 0
    table = set(functions)
    for k in range(1, cap + 1):
        found = False
        for subset in itertools.combinations(range(domain_size), k):
            patterns = {tuple(f[i] for i in subset) for f in table}
            if len(patterns) == 1 << k:
                found = True
                break
        if not found:
            return best
        best = k
    return best


def verify_rsd_is_fibrewise_vc(n: int = 4) -> dict[str, object]:
    """On the fixed-certificate family (one transcript value: the shared current
    certificate), RSD equals the VC dimension of the liveness class
    ``{R -> Live_J(R)}`` over the admitted revocations ``Gamma = 2^E``."""
    if n > MAX_EXHAUSTIVE_N:
        raise CannotCheck("n above exhaustive cap")
    _, alternatives, profiles = fixed_certificate_profiles(n)
    recorded_rsd = len(alternatives)
    revocations = list(powerset(tuple(range(n))))
    liveness_class = [tuple(live(profile, r) for r in revocations) for profile in profiles]
    vc = vc_dimension(liveness_class, len(revocations), recorded_rsd + 1)
    # Planted positive: the class restricted to a single profile has VC dimension 0.
    planted = vc_dimension(liveness_class[:1], len(revocations), 2)
    if planted != 0:
        raise AssertionError("planted single-function class must have VC dimension 0")
    if vc != recorded_rsd:
        raise AssertionError(f"VC dimension {vc} != recorded RSD {recorded_rsd}")
    return {
        "n": n,
        "profiles_on_fibre": len(profiles),
        "admitted_revocations": len(revocations),
        "recorded_rsd": recorded_rsd,
        "vc_dimension_of_liveness_class": vc,
        "equal": vc == recorded_rsd,
        "planted_single_function_vc": planted,
    }


# ----------------------------------------------------------------------------
# 4. Aggregate runner
# ----------------------------------------------------------------------------

def run_v1_self_test() -> dict[str, object]:
    try:
        frontier = verify_storage_query_frontier_v1(5)
        mutations = verify_mutation_controls_v1()
        no_alarm = verify_no_alarm_v1(4)
        rsd = verify_rsd_is_fibrewise_vc(4)
    except CannotCheck as exc:
        return {"terminal": "CANNOT_CHECK", "reason": str(exc), "exit_code": 2}
    except AssertionError as exc:
        return {"terminal": "FAIL", "reason": str(exc), "exit_code": 1}
    n5 = next(c for c in frontier["cases"] if c["n"] == 5)
    return {
        "schema": "orion-v2.revocation-complete-learning.exact-oracle.v1",
        "terminal": "PASS",
        "exit_code": 0,
        "supersedes": {
            "v0_function": "rcl_checks_core.verify_storage_query_frontier",
            "v0_defect_class": "VACUOUS_CONTRAST",
            "withdrawn_figure": "storage_query_reconstruction_checks: 5329",
            "v0_files_modified": False,
        },
        "storage_query_frontier_v1": {
            "max_n": frontier["max_n"],
            "reconstruction_checks": frontier["reconstruction_checks"],
            "splits_on_or_above_frontier": frontier["splits_on_or_above_frontier"],
            "splits_below_frontier": frontier["splits_below_frontier"],
            "collision_pairs_exhibited": frontier["collision_pairs_exhibited"],
            "n5_variable_bits": n5["variable_warrant_bits"],
            "n5_profile_count": n5["profile_count"],
        },
        "mutation_controls_v1": {
            "planted": mutations["mutations_planted"],
            "detected": mutations["mutations_detected"],
            "cases": {k: {kk: vv for kk, vv in v.items() if kk != "cases"} for k, v in mutations["cases"].items()},
        },
        "no_alarm_v1": no_alarm,
        "rsd_is_fibrewise_vc": rsd,
        "authority": {
            "all_size_theorem_proved_by_enumeration": False,
            "rcl_1c_hand_proof_disturbed": False,
            "novelty_established": False,
            "architecture_superiority_established": False,
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)
    if not args.self_test:
        parser.error("--self-test is required")
    result = run_v1_self_test()
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))
    return int(result["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
