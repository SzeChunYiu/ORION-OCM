#!/usr/bin/env python3
"""Lane #200 exact checker: rectangularity, oracle blindness and direct-product
decomposition of every registered natural lifecycle class.

Theorem under test (``theory/OCM_LANE_200_TERMINAL_V1.md``, Theorem D):

    For a finite lifecycle class ``Omega`` with current-behaviour map ``B`` and
    warrant map ``Z``, *full current-function blindness* (every current-function
    transcript is identical across all warrant values within a behaviour fibre)
    holds iff the class is **rectangular**, ``{(B(w), Z(w))} = B(Omega) x Z(Omega)``.
    On a rectangular class the lifecycle target is a Cartesian product, so
    Warrant Lift equals ``log2 |Z(Omega)|``, the deterministic exact query
    complexity is additive, and a *product of two parent learners* (one for the
    current function, one for the warrant object) attains the registered
    lifecycle query bound.  There is no interaction term for a joint theorem to
    own.

The three registered classes are imported from their committed modules, not
re-encoded here:

* ``ocm_warranted_parity_exact``               (WPL V1, p=3, h=2)
* ``ocm_warranted_parity_distinct_paths_exact`` (WPL V2, p=3, h=2)
* ``ocm_warranted_graph_parity_exact``          (WGPL, n=4)

Planted failures (each must *fire* in the same call as the no-alarm cases):

* ``COUPLED_FULL``  — ``z_k := theta_{k mod p}``: not rectangular; blindness fails
  on every warrant coordinate; Warrant Lift 0.
* ``COUPLED_HALF``  — ``z_0 := theta_0``, rest free: not rectangular; blindness
  fails on coordinate 0 only; Warrant Lift ``N - 1``.
* ``COUPLED_FORCED`` — ``z_0 := 1`` when ``theta_0 = 1``, free otherwise: not
  rectangular; behaviour fibres of unequal size (max ``2^N``, min ``2^(N-1)``).

Mutation controls (each asserted applied on a witness before the check runs):

* ``M1`` marginals-only rectangularity test (ignores pairing) — caught by
  ``COUPLED_HALF``;
* ``M2`` blindness test over an empty query set — caught by ``COUPLED_FULL``;
* ``M3`` Warrant Lift from the *average* fibre instead of the maximum — caught by
  ``COUPLED_FORCED``;
* ``M4`` product learner that skips the last warrant query — caught on every
  registered class.

Exit codes: ``0`` pass, ``1`` a check failed for its registered reason,
``2`` could not check (a committed module failed to import).  A ``2`` is never
a pass.

Authority: finite enumeration only.  Establishes no novelty, priority or
architecture claim; the theorem's all-size authority is the hand proof in the
theory record.
"""

from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import math
import sys
from collections.abc import Callable, Hashable, Sequence
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent


class CannotCheck(RuntimeError):
    """A check could not be run.  Never reported as a pass."""


def _load(name: str) -> ModuleType:
    path = HERE / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise CannotCheck(f"cannot load committed module {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # pragma: no cover - the CANNOT_CHECK route
        raise CannotCheck(f"committed module {name} failed to import: {exc}") from exc
    return module


# ----------------------------------------------------------------------------
# Uniform view of a lifecycle class: worlds with (B, Z, L) maps
# ----------------------------------------------------------------------------

class LifecycleClass:
    """A finite lifecycle class in the (behaviour, warrant, lifecycle) view.

    ``behaviour(w)``   the complete current-function table of world ``w``;
    ``warrant(w)``     the hidden warrant profile of ``w``;
    ``lifecycle(w)``   the registered lifecycle target of ``w`` (from the module);
    ``transcript(w, queries)`` the current-function oracle transcript;
    ``current_learner``/``warrant_learner`` the two parent learners, each
    returning ``(recovered_value, queries_used)``.
    """

    def __init__(
        self,
        name: str,
        worlds: Sequence[object],
        behaviour: Callable[[object], Hashable],
        warrant: Callable[[object], tuple[int, ...]],
        lifecycle: Callable[[object], tuple[int, ...]],
        transcript: Callable[[object, Sequence[object]], tuple[int, ...]],
        all_queries: Sequence[object],
        current_learner: Callable[[object], tuple[Hashable, int]],
        warrant_learner: Callable[[object], tuple[tuple[int, ...], int]],
        registered_query_complexity: dict[str, int],
        parents: dict[str, str],
    ) -> None:
        self.name = name
        self.worlds = tuple(worlds)
        self.behaviour = behaviour
        self.warrant = warrant
        self.lifecycle = lifecycle
        self.transcript = transcript
        self.all_queries = tuple(all_queries)
        self.current_learner = current_learner
        self.warrant_learner = warrant_learner
        self.registered_query_complexity = registered_query_complexity
        self.parents = parents
        if not self.worlds:
            raise CannotCheck(f"{name}: empty class")


# ----------------------------------------------------------------------------
# The checks, each with an injectable implementation so mutations can be planted
# ----------------------------------------------------------------------------

def rectangularity(cls: LifecycleClass) -> dict[str, object]:
    pairs = {(cls.behaviour(w), cls.warrant(w)) for w in cls.worlds}
    b_values = {cls.behaviour(w) for w in cls.worlds}
    z_values = {cls.warrant(w) for w in cls.worlds}
    return {
        "pairs": len(pairs),
        "behaviour_values": len(b_values),
        "warrant_values": len(z_values),
        "product": len(b_values) * len(z_values),
        "rectangular": len(pairs) == len(b_values) * len(z_values),
    }


def rectangularity_marginals_only(cls: LifecycleClass) -> dict[str, object]:
    """M1: a broken test that only checks the marginals exist (ignores pairing)."""
    out = rectangularity(cls)
    out["rectangular"] = out["behaviour_values"] > 0 and out["warrant_values"] > 0
    return out


def blindness(cls: LifecycleClass, queries: Sequence[object] | None = None) -> dict[str, object]:
    """Within every behaviour fibre, is the current-function transcript constant
    across all warrant values, and does the fibre carry every warrant value?"""
    if queries is None:
        queries = cls.all_queries
    fibres: dict[Hashable, dict[str, set]] = {}
    for w in cls.worlds:
        b = cls.behaviour(w)
        entry = fibres.setdefault(b, {"transcripts": set(), "warrants": set()})
        entry["transcripts"].add(tuple(cls.transcript(w, queries)))
        entry["warrants"].add(cls.warrant(w))
    all_warrants = {cls.warrant(w) for w in cls.worlds}
    transcript_constant = all(len(e["transcripts"]) == 1 for e in fibres.values())
    fibres_full = all(e["warrants"] == all_warrants for e in fibres.values())
    # Leak: does the transcript, over the whole class, determine any warrant coordinate?
    width = len(next(iter(all_warrants)))
    by_transcript: dict[tuple[int, ...], list[tuple[int, ...]]] = {}
    for w in cls.worlds:
        by_transcript.setdefault(tuple(cls.transcript(w, queries)), []).append(cls.warrant(w))
    leaked = [
        k
        for k in range(width)
        if any(len({z[k] for z in zs}) == 1 for zs in by_transcript.values())
        and any(len({z[k] for z in zs}) < len({cls.warrant(w)[k] for w in cls.worlds}) for zs in by_transcript.values())
    ]
    return {
        "queries": len(queries),
        "fibres": len(fibres),
        "transcript_constant_on_every_fibre": transcript_constant,
        "every_fibre_carries_every_warrant": fibres_full,
        "blind": transcript_constant and fibres_full,
        "leaked_warrant_coordinates": leaked,
    }


def blindness_empty_queries(cls: LifecycleClass) -> dict[str, object]:
    """M2: a broken blindness test — no queries (vacuously constant transcripts)
    and the fibre-completeness requirement dropped."""
    out = blindness(cls, queries=())
    out["blind"] = out["transcript_constant_on_every_fibre"]
    return out


def warrant_lift(cls: LifecycleClass) -> dict[str, object]:
    """Warrant Lift = log2 max_b |{L(w) : B(w) = b}| (worst-case conditional Hartley)."""
    fibres: dict[Hashable, set[tuple[int, ...]]] = {}
    for w in cls.worlds:
        fibres.setdefault(cls.behaviour(w), set()).add(cls.lifecycle(w))
    sizes = [len(s) for s in fibres.values()]
    largest = max(sizes)
    return {
        "max_fibre": largest,
        "min_fibre": min(sizes),
        "warrant_lift_bits": math.log2(largest),
        "rectangular_formula_bits": math.log2(len({cls.warrant(w) for w in cls.worlds})),
        "fibres_equal_size": min(sizes) == largest,
    }


def warrant_lift_average(cls: LifecycleClass) -> dict[str, object]:
    """M3: Warrant Lift computed from the average fibre (wrong: worst case is required)."""
    out = warrant_lift(cls)
    fibres: dict[Hashable, set[tuple[int, ...]]] = {}
    for w in cls.worlds:
        fibres.setdefault(cls.behaviour(w), set()).add(cls.lifecycle(w))
    avg = sum(len(s) for s in fibres.values()) / len(fibres)
    out["warrant_lift_bits"] = math.log2(avg)
    return out


def product_learner(
    cls: LifecycleClass, warrant_learner: Callable[[object], tuple[tuple[int, ...], int]] | None = None
) -> dict[str, object]:
    """Run (current parent learner) x (warrant parent learner) on every world and
    count queries.  Exactness is computed by comparing to the world's own maps."""
    if warrant_learner is None:
        warrant_learner = cls.warrant_learner
    exact = 0
    queries_current = set()
    queries_warrant = set()
    for w in cls.worlds:
        b_hat, q_b = cls.current_learner(w)
        z_hat, q_z = warrant_learner(w)
        queries_current.add(q_b)
        queries_warrant.add(q_z)
        if b_hat == cls.behaviour(w) and z_hat == cls.warrant(w):
            exact += 1
    return {
        "worlds": len(cls.worlds),
        "exact_recoveries": exact,
        "all_exact": exact == len(cls.worlds),
        "current_queries": sorted(queries_current),
        "warrant_queries": sorted(queries_warrant),
    }


def additivity(cls: LifecycleClass) -> dict[str, object]:
    n_worlds = len(cls.worlds)
    n_b = len({cls.behaviour(w) for w in cls.worlds})
    n_z = len({cls.warrant(w) for w in cls.worlds})
    reg = cls.registered_query_complexity
    lb = math.ceil(math.log2(n_worlds))
    return {
        "worlds": n_worlds,
        "decision_tree_lower_bound_bits": lb,
        "log2_behaviours": math.log2(n_b),
        "log2_warrants": math.log2(n_z),
        "registered_current": reg["current"],
        "registered_warrant": reg["warrant"],
        "registered_lifecycle": reg["lifecycle"],
        "registered_is_additive": reg["lifecycle"] == reg["current"] + reg["warrant"],
        "registered_meets_lower_bound": reg["lifecycle"] == lb,
        "factor_bounds_match": reg["current"] == math.log2(n_b) and reg["warrant"] == math.log2(n_z),
    }


# ----------------------------------------------------------------------------
# Registered classes, built from the committed modules
# ----------------------------------------------------------------------------

def _parity_class(module: ModuleType, name: str, p: int, h: int, complexity: dict[str, int]) -> LifecycleClass:
    worlds = module.enumerate_worlds(p, h)
    all_x = tuple(itertools.product((0, 1), repeat=p))
    basis = tuple(module.standard_basis(p, i) for i in range(p))

    def behaviour(w: object) -> Hashable:
        return tuple(w.current_label(x) for x in all_x)  # type: ignore[attr-defined]

    def warrant(w: object) -> tuple[int, ...]:
        return tuple(w.backup_bits)  # type: ignore[attr-defined]

    def transcript(w: object, queries: Sequence[object]) -> tuple[int, ...]:
        return tuple(module.current_function_transcript(w, tuple(queries)))

    def current_learner(w: object) -> tuple[Hashable, int]:
        theta = tuple(w.current_label(e) for e in basis)  # type: ignore[attr-defined]
        return tuple(module.dot(x, theta) for x in all_x), len(basis)

    def warrant_learner(w: object) -> tuple[tuple[int, ...], int]:
        bits = tuple(w.backup_bit(i, j) for i in range(p) for j in range(h))  # type: ignore[attr-defined]
        return bits, p * h

    return LifecycleClass(
        name,
        worlds,
        behaviour,
        warrant,
        lambda w: tuple(module.lifecycle_profile(w)),
        transcript,
        all_x,
        current_learner,
        warrant_learner,
        complexity,
        {
            "current_factor": "exact learning of parity over F_2^p from membership queries (Gaussian elimination; standard-basis queries)",
            "warrant_factor": "INDEX / bitwise coordinate queries on an independent {0,1}^N cube",
            "lower_bound": "decision-tree cardinality bound log2 |Omega|",
        },
    )


def _graph_class(module: ModuleType, n: int) -> LifecycleClass:
    universe = module.optional_edge_universe(n)
    worlds = tuple(
        module.GraphParityWorld(theta, bits)
        for theta in itertools.product((0, 1), repeat=n)
        for bits in itertools.product((0, 1), repeat=len(universe))
    )
    vertices = tuple(range(1, n + 1))
    qc = module.query_complexity(n)

    def behaviour(w: object) -> Hashable:
        return tuple(w.current_function(v) for v in vertices)  # type: ignore[attr-defined]

    def warrant(w: object) -> tuple[int, ...]:
        return tuple(w.optional_bits)  # type: ignore[attr-defined]

    def transcript(w: object, queries: Sequence[object]) -> tuple[int, ...]:
        return tuple(w.current_function(v) for v in queries)  # type: ignore[attr-defined]

    def current_learner(w: object) -> tuple[Hashable, int]:
        return tuple(w.current_function(v) for v in vertices), len(vertices)  # type: ignore[attr-defined]

    def warrant_learner(w: object) -> tuple[tuple[int, ...], int]:
        return tuple(w.optional_bit(e) for e in universe), len(universe)  # type: ignore[attr-defined]

    return LifecycleClass(
        "WGPL_n4",
        worlds,
        behaviour,
        warrant,
        lambda w: tuple(module.lifecycle_profile(w)),
        transcript,
        vertices,
        current_learner,
        warrant_learner,
        {
            "current": qc["current_function_queries"],
            "warrant": qc["additional_warrant_queries"],
            "lifecycle": qc["lifecycle_queries"],
        },
        {
            "current_factor": "vertex-label queries (n independent bits)",
            "warrant_factor": "hidden-graph edge queries / INDEX on binom(n,2) independent bits",
            "lower_bound": "decision-tree cardinality bound; Fano/INDEX for the summary bound",
        },
    )


def registered_classes() -> tuple[LifecycleClass, ...]:
    wpl1 = _load("ocm_warranted_parity_exact")
    wpl2 = _load("ocm_warranted_parity_distinct_paths_exact")
    wgpl = _load("ocm_warranted_graph_parity_exact")
    c1 = wpl1.deterministic_query_complexity(3, 2)
    c2 = wpl2.query_complexity(3, 2)
    return (
        _parity_class(
            wpl1,
            "WPL_V1_p3_h2",
            3,
            2,
            {
                "current": c1["exact_current_parity_membership_queries"],
                "warrant": c1["additional_warrant_queries"],
                "lifecycle": c1["exact_lifecycle_queries_total"],
            },
        ),
        _parity_class(
            wpl2,
            "WPL_V2_p3_h2",
            3,
            2,
            {
                "current": c2["current_function_queries"],
                "warrant": c2["additional_warrant_queries"],
                "lifecycle": c2["lifecycle_queries"],
            },
        ),
        _graph_class(wgpl, 4),
    )


# ----------------------------------------------------------------------------
# Planted coupled classes (must fail rectangularity and blindness)
# ----------------------------------------------------------------------------

class _CoupledWorld:
    __slots__ = ("theta", "z")

    def __init__(self, theta: tuple[int, ...], z: tuple[int, ...]) -> None:
        self.theta = theta
        self.z = z


def _coupled_class(name: str, p: int, N: int, admit: Callable[[tuple[int, ...], tuple[int, ...]], bool]) -> LifecycleClass:
    all_x = tuple(itertools.product((0, 1), repeat=p))
    worlds = [
        _CoupledWorld(theta, z)
        for theta in itertools.product((0, 1), repeat=p)
        for z in itertools.product((0, 1), repeat=N)
        if admit(theta, z)
    ]

    def dot(a: Sequence[int], b: Sequence[int]) -> int:
        return sum(x * y for x, y in zip(a, b, strict=True)) % 2

    def behaviour(w: object) -> Hashable:
        return tuple(dot(x, w.theta) for x in all_x)  # type: ignore[attr-defined]

    def transcript(w: object, queries: Sequence[object]) -> tuple[int, ...]:
        return tuple(dot(x, w.theta) for x in queries)  # type: ignore[attr-defined]

    basis = tuple(tuple(1 if j == i else 0 for j in range(p)) for i in range(p))

    def current_learner(w: object) -> tuple[Hashable, int]:
        theta = tuple(dot(e, w.theta) for e in basis)  # type: ignore[attr-defined]
        return tuple(dot(x, theta) for x in all_x), p

    return LifecycleClass(
        name,
        worlds,
        behaviour,
        lambda w: w.z,  # type: ignore[attr-defined]
        lambda w: w.theta + w.z,  # type: ignore[attr-defined]
        transcript,
        all_x,
        current_learner,
        lambda w: (w.z, N),  # type: ignore[attr-defined]
        {"current": p, "warrant": N, "lifecycle": p + N},
        {"planted": "coupled class; no parent assignment"},
    )


def planted_classes(p: int = 3, N: int = 6) -> tuple[LifecycleClass, ...]:
    return (
        _coupled_class("COUPLED_FULL", p, N, lambda t, z: all(z[k] == t[k % p] for k in range(N))),
        _coupled_class("COUPLED_HALF", p, N, lambda t, z: z[0] == t[0]),
        _coupled_class("COUPLED_FORCED", p, N, lambda t, z: (t[0] == 0) or (z[0] == 1)),
    )


# ----------------------------------------------------------------------------
# Runner
# ----------------------------------------------------------------------------

def check_registered(cls: LifecycleClass) -> dict[str, object]:
    rect = rectangularity(cls)
    blind = blindness(cls)
    lift = warrant_lift(cls)
    add = additivity(cls)
    learner = product_learner(cls)
    if not rect["rectangular"]:
        raise AssertionError(f"{cls.name}: registered class is not rectangular")
    if not blind["blind"] or blind["leaked_warrant_coordinates"]:
        raise AssertionError(f"{cls.name}: registered class is not current-function blind")
    if lift["warrant_lift_bits"] != lift["rectangular_formula_bits"]:
        raise AssertionError(f"{cls.name}: Warrant Lift differs from log2 |Z|")
    if lift["warrant_lift_bits"] != add["registered_warrant"]:
        raise AssertionError(f"{cls.name}: Warrant Lift differs from registered warrant queries")
    if not (add["registered_is_additive"] and add["registered_meets_lower_bound"] and add["factor_bounds_match"]):
        raise AssertionError(f"{cls.name}: registered query complexity is not the additive product bound")
    if not learner["all_exact"]:
        raise AssertionError(f"{cls.name}: product of parent learners is not exact")
    if learner["current_queries"] != [add["registered_current"]] or learner["warrant_queries"] != [add["registered_warrant"]]:
        raise AssertionError(f"{cls.name}: product learner query counts differ from registered")
    return {
        "name": cls.name,
        "rectangularity": rect,
        "blindness": blind,
        "warrant_lift": lift,
        "additivity": add,
        "product_learner": learner,
        "parents": cls.parents,
        "disposition": "DIRECT_PRODUCT_OF_PARENT_PROBLEMS",
    }


def check_planted(cls: LifecycleClass, expected_lift: float, expect_leak: Sequence[int], expect_equal_fibres: bool) -> dict[str, object]:
    rect = rectangularity(cls)
    blind = blindness(cls)
    lift = warrant_lift(cls)
    if rect["rectangular"]:
        raise AssertionError(f"{cls.name}: planted coupled class passed rectangularity")
    if blind["blind"]:
        raise AssertionError(f"{cls.name}: planted coupled class passed blindness")
    if sorted(blind["leaked_warrant_coordinates"]) != sorted(expect_leak):
        raise AssertionError(f"{cls.name}: leak set {blind['leaked_warrant_coordinates']} != {list(expect_leak)}")
    if lift["warrant_lift_bits"] != expected_lift:
        raise AssertionError(f"{cls.name}: Warrant Lift {lift['warrant_lift_bits']} != {expected_lift}")
    if lift["fibres_equal_size"] != expect_equal_fibres:
        raise AssertionError(f"{cls.name}: fibre-size shape unexpected")
    return {
        "name": cls.name,
        "worlds": len(cls.worlds),
        "rectangularity": rect,
        "blindness": blind,
        "warrant_lift": lift,
        "fired": True,
    }


def mutation_controls(registered: Sequence[LifecycleClass], planted: Sequence[LifecycleClass]) -> dict[str, object]:
    half = next(c for c in planted if c.name == "COUPLED_HALF")
    full = next(c for c in planted if c.name == "COUPLED_FULL")
    forced = next(c for c in planted if c.name == "COUPLED_FORCED")
    out: dict[str, object] = {}

    # M1 marginals-only rectangularity: applied iff it returns a different verdict on COUPLED_HALF.
    applied = rectangularity_marginals_only(half)["rectangular"] != rectangularity(half)["rectangular"]
    if not applied:
        raise AssertionError("M1 not applied")
    out["M1_marginals_only_rectangularity"] = {"applied": True, "caught_by": "COUPLED_HALF", "detected": rectangularity_marginals_only(half)["rectangular"] is True}

    # M2 empty-query blindness: applied iff verdict flips on COUPLED_FULL.
    applied = blindness_empty_queries(full)["blind"] != blindness(full)["blind"]
    if not applied:
        raise AssertionError("M2 not applied")
    out["M2_empty_query_blindness"] = {"applied": True, "caught_by": "COUPLED_FULL", "detected": blindness_empty_queries(full)["blind"] is True}

    # M3 average-fibre Warrant Lift: applied iff the value differs on COUPLED_FORCED.
    applied = warrant_lift_average(forced)["warrant_lift_bits"] != warrant_lift(forced)["warrant_lift_bits"]
    if not applied:
        raise AssertionError("M3 not applied")
    out["M3_average_fibre_warrant_lift"] = {
        "applied": True,
        "caught_by": "COUPLED_FORCED",
        "detected": warrant_lift_average(forced)["warrant_lift_bits"] < warrant_lift(forced)["warrant_lift_bits"],
    }

    # M4 product learner skipping the last warrant query: applied on a witness world; caught on every registered class.
    detections = []
    for cls in registered:
        def skipping(w: object, _cls: LifecycleClass = cls) -> tuple[tuple[int, ...], int]:
            z, q = _cls.warrant_learner(w)
            return z[:-1] + (0,), q - 1
        witness = next(w for w in cls.worlds if cls.warrant(w)[-1] == 1)
        if skipping(witness) == cls.warrant_learner(witness):
            raise AssertionError(f"M4 not applied on {cls.name}")
        detections.append(not product_learner(cls, skipping)["all_exact"])
    out["M4_learner_skips_last_warrant_query"] = {"applied": True, "caught_by": [c.name for c in registered], "detected": all(detections)}

    for name, row in out.items():
        if not row["detected"]:
            raise AssertionError(f"{name} not detected")
    return out


def run_exact_calibration() -> dict[str, object]:
    registered = registered_classes()
    planted = planted_classes()
    reg_rows = [check_registered(c) for c in registered]
    N = 6
    planted_rows = [
        check_planted(planted[0], 0.0, [k for k in range(N)], True),
        check_planted(planted[1], N - 1, [0], True),
        check_planted(planted[2], N, [0], False),
    ]
    mutations = mutation_controls(registered, planted)
    return {
        "schema": "orion.ocm.lane200-decomposition.exact-results.v1",
        "terminal": "PASS_EVERY_REGISTERED_CLASS_IS_A_DIRECT_PRODUCT_OF_PARENT_PROBLEMS",
        "registered_classes": reg_rows,
        "planted_coupled_classes": planted_rows,
        "mutation_controls": mutations,
        "denominators": {
            "registered_classes": len(registered),
            "registered_worlds": sum(len(c.worlds) for c in registered),
            "planted_classes": len(planted),
            "planted_worlds": sum(len(c.worlds) for c in planted),
            "mutations_planted": len(mutations),
        },
        "authority": {
            "finite_enumeration_only": True,
            "all_size_authority": "hand proof, theory/OCM_LANE_200_TERMINAL_V1.md Theorem D",
            "novelty_established": False,
            "architecture_separation": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = run_exact_calibration()
    except CannotCheck as exc:
        print(json.dumps({"terminal": "CANNOT_CHECK", "reason": str(exc)}, indent=2))
        return 2
    except AssertionError as exc:
        print(json.dumps({"terminal": "FAIL", "error": str(exc)}, indent=2))
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, default=str))
    else:
        d = result["denominators"]
        print(
            f"PASS lane-200 decomposition: {d['registered_classes']} registered classes "
            f"({d['registered_worlds']} worlds) are direct products; {d['planted_classes']} planted "
            f"coupled classes fired; {d['mutations_planted']} mutations detected"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
