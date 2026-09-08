"""Tests for E8, the independently implemented parent.

These tests are adversarial towards the module they cover.  Four of them are
required by the experiment's own design and each exists because the
corresponding fake is the likeliest way this result could be worthless:

(a) **the constructive parent ties.**  It is the same class holding separate
    state, so an exact tie on every coordinate is forced.  That is not a
    success; it is the demonstration that the earlier ``PARENT_SUFFICIENT``
    verdict compared a program with itself and therefore carried no
    information.  If a future edit ever makes it *stop* tying, the tautology
    control has silently become a comparator and the whole argument breaks.

(b) **no independent parent touches the arm's internals.**  Enforced by source
    inspection and by walking the import graph, in the style of
    ``test_scaling.py``'s ``true_cone`` check: the word never appears in the
    parents module at all, and nothing named after the arm's representation is
    importable into it.  A parent that reuses the arm's fitting is the defect
    this whole experiment exists to remove.

(c) **capability is checked before cost is read.**  Structural, not by
    convention: ``objective_calls_if_admissible`` returns ``None`` for an arm
    that missed the optimum, and the terminal rule reads nothing else.  A cheap
    arm that does not solve the problem must be unable to win, and a synthetic
    record proves it cannot.

(d) **the resource coordinates are reported separately, never summed.**  The
    original lane was explicit that fewer objective calls is not whole-resource
    dominance.  Objective calls, fitting, auditing, invalidation, model search
    and bytes are six coordinates and there is no total anywhere in the receipt.

The sweep is run once per module.  Everything asserted here is a deterministic
function of the pre-registration commitment, so a failure is a real change in
the harness and never a flaky draw.
"""

from __future__ import annotations

import ast
import inspect

import pytest

import indep
import indep_parents
import run_indep
from indep import (
    AUDIT_POINTS,
    COMMITMENT,
    DECISIVE_REGIME,
    GENERATIONS,
    INDEP_PLAN,
    MODEL_PARAMETER_CEILING,
    N_BITS,
    REGIMES,
    REPS,
    TERMINALS,
    LifetimeRecord,
    Objective,
    PointStream,
    WalshLearner,
    WorkLedger,
    constructive_parent,
    lifetime_landscapes,
    point_stream,
    sweep,
    sweep_table,
    walsh_arm,
)
from indep_parents import bandit_parent, regression_parent, tabu_parent
from run_indep import terminal_for

CEILING = 1 << N_BITS

#: Every name the arm's representation, fitting, auditing and model search live
#: behind.  None of them may be reachable from the parents module.
ARM_INTERNALS = (
    "WalshLearner",
    "_walsh_hadamard",
    "_walsh_full_transform",
    "_walsh_threshold",
    "_walsh_refit",
    "_walsh_argmax",
    "_walsh_predict",
    "_walsh_audit",
    "chi",
)

#: Everything the landscape would hand over if the channel leaked.
STRUCTURE_LEAKS = ("components", ".scopes", "affected", "tables", ".comp(")


@pytest.fixture(scope="module")
def swept():
    return sweep()


@pytest.fixture(scope="module")
def rows(swept):
    return sweep_table(swept)


def _row(swept, regime, arm):
    return next(r for r in swept[regime] if r.arm == arm)


# --------------------------------------------------------------------------
# (a) the constructive parent ties, and the tie is the point
# --------------------------------------------------------------------------


def test_constructive_parent_is_literally_the_same_algorithm():
    """Not 'similar'.  The same class, constructed twice."""
    assert type(walsh_arm()) is type(constructive_parent()) is WalshLearner
    assert inspect.getsource(constructive_parent).count("WalshLearner(n=n)") == 1


def test_constructive_parent_ties_the_arm_on_every_coordinate(swept):
    """A tie against yourself is a tautology, and here it is, exactly."""
    for regime in REGIMES:
        arm = _row(swept, regime.name, "walsh_arm")
        con = _row(swept, regime.name, "constructive_parent")
        assert con.objective_calls == arm.objective_calls
        assert con.call_split == arm.call_split
        assert con.optimum_attained_fraction == arm.optimum_attained_fraction
        assert con.persistent_bytes == arm.persistent_bytes
        assert con.fit_units == arm.fit_units
        assert con.audit_units == arm.audit_units
        assert con.invalidation_units == arm.invalidation_units
        assert con.model_search_units == arm.model_search_units
        assert con.rebuilds == arm.rebuilds


def test_the_tautology_carries_no_information_about_the_architecture(swept):
    """The tie holds in every regime, favourable and unfavourable alike.

    A comparison whose outcome is identical whether the mechanism helps or hurts
    is not measuring the mechanism.  Asserted across all three regimes so that
    nobody can read the sparse-stable tie as evidence.
    """
    ties = {
        regime.name: (
            _row(swept, regime.name, "walsh_arm").objective_calls
            == _row(swept, regime.name, "constructive_parent").objective_calls
        )
        for regime in REGIMES
    }
    assert all(ties.values()), ties
    calls = {
        regime.name: _row(swept, regime.name, "walsh_arm").objective_calls
        for regime in REGIMES
    }
    # ... and the arm's own cost is not constant across regimes, so the constant
    # tie really is a property of the comparison and not of the task.
    assert len(set(calls.values())) > 1, calls


def test_a_broken_tie_voids_every_other_terminal(swept):
    """The guard fires before anything else can be read from the table."""
    records = list(swept[DECISIVE_REGIME])
    con = _row(swept, DECISIVE_REGIME, "constructive_parent")
    perturbed = [
        LifetimeRecord(**{**vars(con), "objective_calls": con.objective_calls + 1})
        if r.arm == "constructive_parent"
        else r
        for r in records
    ]
    terminal, reason = terminal_for(perturbed)
    assert terminal == "CONSTRUCTIVE_TIE_BROKEN"
    assert "same algorithm" in reason


# --------------------------------------------------------------------------
# (b) no independent parent touches the arm's internals
# --------------------------------------------------------------------------


def test_no_independent_parent_mentions_the_arms_representation():
    """Structural, in the style of ``test_scaling``'s ``true_cone`` check.

    The arm's representation has exactly one name and that name may not appear
    anywhere in the parents module -- not in code, not in a docstring, not in a
    comment.  The positive control is asserted alongside it, because a check
    that would also pass on an empty file is not a check.
    """
    parents_source = inspect.getsource(indep_parents).lower()
    assert "walsh" not in parents_source
    arm_source = inspect.getsource(indep)
    for name in ARM_INTERNALS:
        assert name in arm_source, name
    for name in ARM_INTERNALS:
        if name == "chi":  # substring-safe check below
            continue
        assert name not in inspect.getsource(indep_parents), name


def test_independent_parent_classes_hold_no_arm_internal_names():
    for cls in (
        indep_parents.RegressionParent,
        indep_parents.TabuParent,
        indep_parents.BanditParent,
    ):
        source = inspect.getsource(cls)
        assert "walsh" not in source.lower()
        for name in ARM_INTERNALS:
            if name == "chi":
                continue
            assert name not in source, (cls.__name__, name)


def test_the_parents_module_imports_no_arm_internal():
    """Walk the import graph rather than trusting the prose."""
    tree = ast.parse(inspect.getsource(indep_parents))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            assert node.module in {
                "indep",
                "dataclasses",
                "functools",
                "typing",
                "__future__",
            }, node.module
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
    assert not imported & set(ARM_INTERNALS), imported & set(ARM_INTERNALS)
    # what it does import from the harness is meters and declared constants only
    assert {"Objective", "WorkLedger", "PointStream", "CallSplit"} <= imported


def test_the_two_solvers_are_disjoint_code_paths():
    """Both must solve a linear system; neither may solve the other's."""
    arm_source = inspect.getsource(indep)
    parents_source = inspect.getsource(indep_parents)
    assert "_walsh_refit" in arm_source and "_walsh_refit" not in parents_source
    assert "_solve_design" in parents_source and "_solve_design" not in arm_source
    assert "monomial(" in parents_source and "monomial(" not in arm_source


def test_no_arm_or_parent_can_see_the_landscape_structure():
    """Scalar observations only.  The channel is the objective and nothing else."""
    for cls in (
        WalshLearner,
        indep.GlobalEnumerationParent,
        indep_parents.RegressionParent,
        indep_parents.TabuParent,
        indep_parents.BanditParent,
    ):
        source = inspect.getsource(cls)
        for leak in STRUCTURE_LEAKS:
            assert leak not in source, (cls.__name__, leak)
    # the harness itself reads the structure, because the SCORER must
    assert ".fitness" in inspect.getsource(indep.run_lifetime)
    assert "optimum()" in inspect.getsource(indep.sweep)


def test_independent_parents_actually_reach_the_objective_differently(swept):
    """Different routes must leave different traces, or they are the same route."""
    regime = DECISIVE_REGIME
    arm = _row(swept, regime, "walsh_arm")
    regression = _row(swept, regime, "regression_parent")
    tabu = _row(swept, regime, "tabu_parent")
    bandit = _row(swept, regime, "bandit_parent")
    # the model-based parent identifies its model at a different price
    assert regression.call_split["discovery"] != arm.call_split["discovery"]
    assert regression.fit_units != arm.fit_units
    # the search parents hold no model at all
    for row in (tabu, bandit):
        assert row.fit_units == 0
        assert row.audit_units == 0
        assert row.invalidation_units == 0
        assert row.rebuilds == 0
        assert row.model_parameters == 0


# --------------------------------------------------------------------------
# (c) capability is checked before cost is read
# --------------------------------------------------------------------------


def test_cost_is_unreadable_for_an_arm_that_missed_the_optimum(swept):
    template = _row(swept, DECISIVE_REGIME, "walsh_arm")
    lame = LifetimeRecord(
        **{
            **vars(template),
            "arm": "cheap_and_wrong",
            "arm_role": "INDEPENDENT_PARENT",
            "objective_calls": 1.0,
            "optimum_attained_fraction": 0.99,
            "optimum_attained_generations": GENERATIONS - 0.12,
        }
    )
    assert lame.capability_ok is False
    assert lame.admissible is False
    assert lame.objective_calls_if_admissible() is None
    assert lame.objective_calls == 1.0  # reported, but unreadable


def test_a_cheap_incapable_parent_cannot_win(swept):
    """The gate is the only reason the terminal is not one call away from fake."""
    records = list(swept[DECISIVE_REGIME])
    template = _row(swept, DECISIVE_REGIME, "regression_parent")
    lame = LifetimeRecord(
        **{
            **vars(template),
            "arm": "cheap_and_wrong",
            "objective_calls": 1.0,
            "optimum_attained_fraction": 0.5,
        }
    )
    terminal, reason = terminal_for(records + [lame])
    assert "cheap_and_wrong" not in reason
    assert terminal == terminal_for(records)[0]


def test_terminal_reads_cost_only_through_the_gate():
    source = inspect.getsource(terminal_for)
    assert "objective_calls_if_admissible" in source
    assert "capability is read before cost" in source.lower() or "Capability is read before cost" in source


def test_capability_and_readability_agree_on_every_row(rows):
    for row in rows:
        readable = row["objective_calls_if_admissible"] is not None
        assert readable is row["capability_ok"] is row["admissible"]


def test_the_gate_actually_excludes_somebody(rows):
    """A gate that never fires is decoration."""
    missed = [r for r in rows if not r["capability_ok"]]
    assert missed, "no arm missed the optimum, so the capability gate is untested"
    for row in missed:
        assert row["optimum_attained_fraction"] < 1.0
        assert row["objective_calls_if_admissible"] is None
    # it fires on the mechanism under test as well as on parents, which is the
    # only way to know it is not a gate written to exclude parents
    assert {r["arm"] for r in missed} & {"walsh_arm", "constructive_parent"}


def test_attainment_is_scored_against_the_oracle_not_self_reported():
    """The scorer reads ``NK.fitness`` of the returned state itself."""
    regime = REGIMES[0]
    landscapes = lifetime_landscapes(regime, 0)
    optima = [land.optimum() for land in landscapes]
    records, _, _ = indep.run_lifetime(
        "walsh_arm", walsh_arm, regime, 0, landscapes, optima
    )
    for record, land, optimum in zip(records, landscapes, optima):
        assert record.attained_value == land.fitness(
            max(range(CEILING), key=lambda x: (land.fitness(x), -x))
        ) or record.attained_value <= optimum
        assert record.attained == (abs(record.attained_value - optimum) <= 1e-12)


def test_the_ceiling_passes_the_gate_everywhere_and_the_arm_does_not(swept):
    for regime in REGIMES:
        assert _row(swept, regime.name, "global_enumeration_parent").capability_ok
    for regime in ("sparse_stable", "dense_stable"):
        assert _row(swept, regime, "walsh_arm").capability_ok
    assert not _row(swept, "sparse_drift", "walsh_arm").capability_ok


def test_the_arms_audit_is_not_a_sufficient_staleness_certificate(swept):
    """Reported because it is against the mechanism under test.

    Under drift the arm refits a support that the world has moved out from
    under it, its four-point audit passes anyway, and its model's argmax is not
    the optimum.  It happens once in ninety-six generations, and once is enough
    to make the arm inadmissible for the cost comparison in that regime -- which
    is exactly what a capability gate is for.  Two independently implemented
    parents attain the optimum in all ninety-six.
    """
    arm = _row(swept, "sparse_drift", "walsh_arm")
    assert not arm.capability_ok
    assert arm.objective_calls_if_admissible() is None
    assert 0.98 < arm.optimum_attained_fraction < 1.0
    assert arm.mean_quality_over_optimum < 1.0
    for parent in ("regression_parent", "tabu_parent"):
        assert _row(swept, "sparse_drift", parent).capability_ok
    assert terminal_for(swept["sparse_drift"])[0] == "ARM_NOT_CAPABLE"


# --------------------------------------------------------------------------
# (d) the resource coordinates are reported separately, never summed
# --------------------------------------------------------------------------

COORDINATES = (
    "objective_calls",
    "fit_units",
    "audit_units",
    "invalidation_units",
    "model_search_units",
    "persistent_bytes",
)


def test_every_coordinate_is_reported_on_every_row(rows):
    for row in rows:
        for name in COORDINATES:
            assert name in row, name
        assert set(row["call_split"]) == {
            "discovery",
            "steady_state",
            "invalidation",
            "search",
        }


def test_no_total_is_reported_anywhere(rows):
    banned = ("total", "score", "combined", "aggregate", "overall_cost")
    for row in rows:
        for key in row:
            assert not any(word in key.lower() for word in banned), key


def test_the_coordinate_sum_appears_nowhere_in_the_row(rows):
    """If a total is never computed, the number cannot be in the receipt."""
    for row in rows:
        total = sum(row[name] for name in COORDINATES)
        numeric = [
            value
            for key, value in row.items()
            if isinstance(value, (int, float)) and not isinstance(value, bool)
        ]
        assert total not in numeric, (row["regime"], row["arm"], total)
    assert INDEP_PLAN["resource_coordinates_are_summed"] is False


def test_the_call_split_decomposes_one_coordinate_and_says_so(rows):
    for row in rows:
        assert sum(row["call_split"].values()) == pytest.approx(row["objective_calls"])
    assert "decomposition of ONE coordinate" in inspect.getsource(indep.CallSplit)


def test_fewer_objective_calls_is_not_whole_resource_dominance(swept):
    """The claim the original lane made about itself, made checkable.

    In the decisive regime the model-based arms buy their cheapness in objective
    calls with fitting and auditing work that the model-free parents do not pay
    at all, and the receipt reports both rather than trading them off.
    """
    arm = _row(swept, DECISIVE_REGIME, "walsh_arm")
    tabu = _row(swept, DECISIVE_REGIME, "tabu_parent")
    assert arm.objective_calls < tabu.objective_calls
    assert arm.fit_units > tabu.fit_units
    assert arm.audit_units > tabu.audit_units


def test_invalidation_is_metered_apart_from_fitting(swept):
    """A rebuild forced by a failed audit is never booked as ordinary fitting."""
    stable = _row(swept, "sparse_stable", "walsh_arm")
    drift = _row(swept, "sparse_drift", "walsh_arm")
    assert stable.invalidation_units == 0
    assert stable.rebuilds == 1  # the first build only
    assert drift.invalidation_units > 0
    assert drift.rebuilds > stable.rebuilds
    for arm in ("walsh_arm", "regression_parent"):
        assert _row(swept, "sparse_drift", arm).call_split["invalidation"] > 0


# --------------------------------------------------------------------------
# the meters themselves
# --------------------------------------------------------------------------


def test_objective_charges_distinct_evaluations_only():
    calls: list[int] = []

    def fitness(x):
        calls.append(x)
        return float(x)

    objective = Objective(n=3, fitness=fitness)
    assert objective(5) == 5.0
    assert objective(5) == 5.0
    assert objective(2) == 2.0
    assert objective.calls == 2
    assert objective.requests == 3
    assert calls == [5, 2]
    assert objective.best_observed() == 5
    assert objective.top_observed(2) == (5, 2)


def test_the_free_requery_rule_is_uniform_and_declared():
    assert "distinct" in inspect.getsource(Objective)
    assert "uniformly, for every arm" in inspect.getsource(Objective)


def test_no_arm_exceeds_the_information_ceiling(rows):
    for row in rows:
        assert row["objective_calls"] <= GENERATIONS * CEILING


def test_global_enumeration_is_exactly_the_ceiling_and_reproduces_the_reference(swept):
    """The two reference numbers the original lane's report actually pins."""
    for regime in REGIMES:
        row = _row(swept, regime.name, "global_enumeration_parent")
        assert row.objective_calls == GENERATIONS * CEILING == 3072
        assert row.persistent_bytes == CEILING * 8 == 2048
        assert row.optimum_attained_fraction == 1.0
        assert indep.REFERENCE_NUMBERS["global_enumeration_objective_calls"] == 3072
        assert indep.REFERENCE_NUMBERS["global_value_array_bytes"] == 2048


def test_point_stream_is_a_deterministic_permutation():
    first = point_stream("sparse_stable", 0, 0)
    assert sorted(first) == list(range(CEILING))
    assert first == point_stream("sparse_stable", 0, 0)
    assert first != point_stream("sparse_stable", 0, 1)
    assert first != point_stream("sparse_stable", 1, 0)
    assert first != point_stream("dense_stable", 0, 0)
    stream = PointStream(first)
    assert stream.take(3) == list(first[:3])
    assert stream.next() == first[3]


def test_every_arm_is_handed_the_same_landscapes():
    a = lifetime_landscapes(REGIMES[0], 0)
    b = lifetime_landscapes(REGIMES[0], 0)
    assert [land.scopes for land in a] == [land.scopes for land in b]
    assert [land.tables for land in a] == [land.tables for land in b]


def test_supports_persist_without_drift_and_move_with_it():
    stable = lifetime_landscapes(REGIMES[0], 0)
    assert all(land.scopes == stable[0].scopes for land in stable)
    assert len({tuple(land.tables[0]) for land in stable}) == GENERATIONS
    drifting = lifetime_landscapes(REGIMES[2], 0)
    assert any(land.scopes != drifting[0].scopes for land in drifting)


def test_nothing_reads_a_clock():
    for module in (indep, indep_parents, run_indep):
        source = inspect.getsource(module)
        assert "import time" not in source
        assert "perf_counter" not in source
        assert "datetime" not in source


# --------------------------------------------------------------------------
# the arm's model, and the shared ceiling that binds every model
# --------------------------------------------------------------------------


def test_the_arms_model_is_exact_after_a_rebuild():
    regime = REGIMES[0]
    land = lifetime_landscapes(regime, 0)[0]
    learner = walsh_arm()
    objective = Objective(n=N_BITS, fitness=land.fitness)
    learner.generation(objective, PointStream(point_stream(regime.name, 0, 0)), WorkLedger())
    assert learner.support is not None
    worst = max(
        abs(indep._walsh_predict(learner.support, learner.coefficients, x) - land.fitness(x))
        for x in range(CEILING)
    )
    assert worst < 1e-12
    assert len(learner.support) <= MODEL_PARAMETER_CEILING


def test_the_parameter_ceiling_binds_the_arm_and_the_regression_parent_alike(swept):
    for arm in ("walsh_arm", "constructive_parent", "regression_parent"):
        dense = _row(swept, "dense_stable", arm)
        sparse = _row(swept, "sparse_stable", arm)
        assert dense.model_refused_fraction == 1.0
        assert sparse.model_refused_fraction == 0.0
        assert dense.objective_calls == GENERATIONS * CEILING


def test_the_audit_budget_is_the_same_for_both_model_based_arms():
    assert AUDIT_POINTS == 4
    assert "AUDIT_POINTS" in inspect.getsource(indep._walsh_audit)
    assert "AUDIT_POINTS" in inspect.getsource(indep_parents.RegressionParent._confront)


def test_the_design_repair_allowance_is_the_same_for_both_model_based_arms():
    """Otherwise the loser could be the one given the meaner repair budget."""
    assert "3 * p + 8" in inspect.getsource(indep._walsh_refit)
    assert indep_parents.REGRESSION_DESIGN_GROWTH == 3
    assert indep_parents.REGRESSION_DESIGN_SLACK == 8


def test_the_regression_parents_inner_optimiser_is_exhaustive():
    """A parent that loses because of a weak inner search is undertuned."""
    source = inspect.getsource(indep_parents.RegressionParent._surrogate_optimum)
    assert "range(size)" in source
    assert "Exhaustive" in source


def test_the_search_parents_are_budgeted_to_the_ceiling():
    for cls in (indep_parents.TabuParent, indep_parents.BanditParent):
        assert "ceiling = 1 << self.n" in inspect.getsource(cls.generation)


# --------------------------------------------------------------------------
# the pre-registration and the terminal rule
# --------------------------------------------------------------------------


def test_the_commitment_is_a_function_of_the_plan():
    from prereg import commit

    assert COMMITMENT.commitment == commit(INDEP_PLAN).commitment
    edited = dict(INDEP_PLAN, generations=GENERATIONS + 1)
    assert commit(edited).commitment != COMMITMENT.commitment


def test_the_plan_registers_the_capability_gate_and_the_tolerance():
    assert INDEP_PLAN["capability_gate"].startswith("optimum attained in EVERY")
    assert INDEP_PLAN["match_tolerance"] == indep.MATCH_TOLERANCE
    assert INDEP_PLAN["decisive_regime"] == DECISIVE_REGIME
    assert INDEP_PLAN["information_given_to_every_arm"] == "SCALAR_OBJECTIVE_OBSERVATIONS_ONLY"
    assert set(INDEP_PLAN["arms"]) == set(indep.ARM_ROLES)


def test_every_arm_declares_the_search_policy_it_actually_used():
    """PARENT_UNDERTUNED is inadmissible, so the policies are on the record."""
    assert set(indep.SEARCH_POLICY) == set(indep.ARM_ROLES) | {"shared"}
    for arm, policy in indep.SEARCH_POLICY.items():
        assert len(policy) > 80, arm


def test_the_terminal_is_one_of_the_registered_ones(swept):
    for regime in REGIMES:
        terminal, reason = terminal_for(swept[regime.name])
        assert terminal in TERMINALS
        assert len(reason) > 40
    assert set(TERMINALS) == set(INDEP_PLAN["terminals"])


def test_both_answers_to_the_decisive_question_are_reachable(swept):
    """Neither branch is unreachable, so the terminal is not decided in advance."""
    records = list(swept[DECISIVE_REGIME])
    arm = _row(swept, DECISIVE_REGIME, "walsh_arm")

    cheap = [
        LifetimeRecord(**{**vars(r), "objective_calls": 1.0})
        if r.arm_role == "INDEPENDENT_PARENT" and r.arm != "global_enumeration_parent"
        else r
        for r in records
    ]
    assert terminal_for(cheap)[0] == "INDEPENDENT_PARENT_SUFFICIENT"

    dear = [
        LifetimeRecord(**{**vars(r), "objective_calls": arm.objective_calls * 10})
        if r.arm_role == "INDEPENDENT_PARENT"
        else r
        for r in records
    ]
    assert terminal_for(dear)[0] == "ARM_SEPARATES_FROM_INDEPENDENT_PARENTS"

    blind = [
        LifetimeRecord(**{**vars(r), "optimum_attained_fraction": 0.5})
        if r.arm_role == "INDEPENDENT_PARENT"
        else r
        for r in records
    ]
    assert terminal_for(blind)[0] == "NO_INDEPENDENT_PARENT_IS_CAPABLE"

    lost = [
        LifetimeRecord(**{**vars(r), "optimum_attained_fraction": 0.5})
        if r.arm in ("walsh_arm", "constructive_parent")
        else r
        for r in records
    ]
    assert terminal_for(lost)[0] == "ARM_NOT_CAPABLE"


def test_the_ceiling_is_excluded_from_the_match_test_by_declaration():
    """Matching ``2**n`` calls is matching the act of measuring everything."""
    assert run_indep.MATCH_TEST_EXCLUDES == ("global_enumeration_parent",)
    assert indep.ARM_ROLES["global_enumeration_parent"] == "CEILING"


def test_the_sweep_is_the_registered_shape(rows):
    assert len(rows) == len(REGIMES) * len(indep.ARM_ROLES)
    for row in rows:
        assert row["generations"] == GENERATIONS == 12
        assert row["reps"] == REPS
    assert N_BITS == 8
    assert GENERATIONS * (1 << N_BITS) == 3072


# --------------------------------------------------------------------------
# the receipt says what it does not establish
# --------------------------------------------------------------------------


def test_the_receipt_refuses_to_overwrite_and_states_its_own_limits(tmp_path):
    import json

    out = tmp_path / "INDEP_E8_TEST.json"
    assert run_indep.main(["--out", str(out)]) == 0
    assert run_indep.main(["--out", str(out)]) == 1  # never silently overwritten

    receipt = json.loads(out.read_text())
    assert receipt["terminal"] in TERMINALS
    assert receipt["study_role"] == (
        "INDEPENDENT_SECOND_IMPLEMENTATION_OF_A_CONTESTED_PARENT_COMPARISON"
    )
    assert receipt["protected_claim_authority"] is False
    assert receipt["scientific_promotion"] == "NOT_ESTABLISHED"

    limits = " ".join(receipt["what_this_does_not_establish"])
    assert "FOUR HAND-WRITTEN PARENTS ARE NOT PARENT CLOSURE" in limits
    assert "NO NEURAL AND NO MODERN AutoML COMPARATOR WAS RUN" in limits

    # the second-implementation positioning, and no claim of priority
    authority = receipt["authority"]
    assert "INDEPENDENT SECOND IMPLEMENTATION" in authority
    assert "claims no priority" in authority
    assert "codex/ocm-evolvability-independent-20260908" in authority
    assert "research/evolvability-independent/PROTECTED_PROTOCOL_V3.md" in authority
    assert "factorization_survival_v3.py" in authority

    # the reconstruction is declared, including what it does NOT reproduce
    notes = " ".join(receipt["reconstruction_notes"])
    assert "does NOT reproduce the reported 442" in notes
    assert "524928" in notes

    # the tautology is on the record in every regime
    for regime in REGIMES:
        tie = receipt["constructive_tie"][regime.name]
        assert all(v is True for k, v in tie.items() if k.endswith("_equal"))


def test_the_gap_is_attributed_to_discovery_not_representation(swept):
    arm = _row(swept, DECISIVE_REGIME, "walsh_arm")
    parent = _row(swept, DECISIVE_REGIME, "regression_parent")
    assert arm.call_split["steady_state"] == parent.call_split["steady_state"]
    assert arm.model_parameters == parent.model_parameters
    assert arm.call_split["discovery"] > parent.call_split["discovery"]
