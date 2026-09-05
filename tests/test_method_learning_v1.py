"""Methods, learned generators, exact checking, finite convergence and provenance."""
from dataclasses import replace
from fractions import Fraction
from itertools import product

import pytest

from ocm.learning import methods as M
from ocm.science.finite_identification import ModelClass, Observation, ExperimentLearner


def task(program):
    return M.PolynomialTask("/".join(program) or "identity", M.normal_form(program))


def learned():
    tasks = [task(p) for p in (("inc", "square", "inc"), ("inc", "square", "double"))]
    return M.learn_generator((t, M.solve(t)) for t in tasks)


def test_exact_symbolic_checker_agrees_with_independent_numeric_execution():
    for length in range(5):
        for program in product(M.PRIMITIVES, repeat=length):
            coefficients = M.normal_form(program)
            for x in (Fraction(-7, 3), Fraction(0), Fraction(2, 5), Fraction(3)):
                assert M.execute(program, x) == M.evaluate_polynomial(coefficients, x)


def test_example_fit_is_refuted_before_a_polynomial_identity_is_certified():
    t = task(("square",))
    result = M.solve(t)
    assert M.verify_solution(t, result)
    assert len(result.counterexamples) >= 2
    assert not M.verify_solution(t, replace(result, program=()))
    assert not M.verify_solution(task(("inc",)), result)


def test_learns_generator_from_distinct_verified_training_tasks_and_improves_held_out():
    method = learned()
    assert ("inc", "square") in method.fragments
    result = M.validate_generator(method, [task(("inc", "square", "dec")), task(("inc", "square", "square"))])
    assert result["accepted"], result


def test_training_copy_and_holdout_leakage_are_rejected():
    t = task(("inc", "square", "inc"))
    result = M.solve(t)
    with pytest.raises(ValueError):
        M.learn_generator([(t, result), (replace(t, task_id="renamed"), result)])
    with pytest.raises(ValueError):
        M.validate_generator(learned(), [t])
    with pytest.raises(ValueError):
        M.validate_generator(learned(), [])


def test_fair_fallback_finds_every_small_grammar_solution_within_twice_baseline_slots():
    method = M.GeneratorMethod((("square", "square"),))
    tasks = {task(p).fingerprint: task(p) for length in range(4) for p in product(M.PRIMITIVES, repeat=length)}
    for t in tasks.values():
        baseline = M.solve(t, M.SearchBudget(200, 3))
        guided = M.solve(t, M.SearchBudget(2 * baseline.slots, 3), method)
        assert M.verify_solution(t, guided)
        assert guided.slots <= 2 * baseline.slots


def test_budget_exhaustion_is_not_global_impossibility():
    t = task(("square",))
    assert M.solve(t, M.SearchBudget(0, 4)).status == "BUDGET_EXHAUSTED"
    assert M.solve(t, M.SearchBudget(100, 0)).status == "EXHAUSTED_DECLARED_GRAMMAR"
    assert M.solve(t, M.SearchBudget(100, 1)).status == "VERIFIED_POLYNOMIAL_IDENTITY"


def test_checked_method_enters_runtime_and_revocation_survives_restart(tmp_path):
    from ocm.runtime.ocm_runtime import OCMRuntime
    from ocm.kso.warrant import Liveness
    rt = OCMRuntime(tmp_path)
    t = task(("inc", "square"))
    receipt = M.admit_solution(rt, t, M.solve(t))
    assert rt.state.ks.atom_map()[receipt["method_id"]].liveness(rt.state.revoked) is Liveness.LIVE
    rt.revoke([receipt["evidence_id"]])
    rt = OCMRuntime(tmp_path)
    assert rt.state.ks.atom_map()[receipt["method_id"]].liveness(rt.state.revoked) is Liveness.DEAD
    assert rt.replay()["identical"]


def test_complete_method_learning_demo_survives_restart_and_support_revocation(tmp_path):
    from ocm.evaluation.method_learning_eval import evaluate
    result = evaluate(tmp_path)
    assert result["validation"]["accepted"]
    assert result["revocation"] == "REUSE_REFUSED_AFTER_RESTART"
    assert all(row["assessment"]["survivors"] == (row["simulated_truth"],) for row in result["science"])


def model_class():
    return ModelClass(("q0", "q1", "q2"), (("a", ("0", "0", "0")), ("b", ("0", "1", "1")), ("c", ("1", "1", "0"))))


def test_experiment_selection_converges_within_class_and_revocation_reopens_it():
    models = model_class()
    for name, outcomes in models.predictions:
        learner = ExperimentLearner(models)
        for i in range(len(models.predictions) - 1):
            result = learner.assess()
            if result["next_query"] is None:
                break
            query = result["next_query"]
            learner.observe(Observation(str(i), query, outcomes[models.queries.index(query)], "simulator:test", models.fingerprint))
        assert learner.assess()["survivors"] == (name,)
        assert learner.assess()["status"] == "IDENTIFIED_WITHIN_DECLARED_MODEL_CLASS"
        assert learner.assess(revoked=iter(learner.assess()["support"]))["status"] == "EXPERIMENT_REQUIRED"


def test_scientific_conflict_and_observational_equivalence_stay_visible():
    models = model_class()
    learner = ExperimentLearner(models)
    learner.observe(Observation("e0", "q0", "0", "host", models.fingerprint))
    learner.observe(Observation("e1", "q0", "1", "host", models.fingerprint))
    assert learner.assess()["status"] == "MODEL_CLASS_REFUTED_OR_OBSERVATIONS_CONFLICT"
    assert learner.assess(revoked=("e1",))["survivors"] == ("a", "b")
    same = ModelClass(("q",), (("a", ("0",)), ("b", ("0",))))
    assert ExperimentLearner(same).assess()["status"] == "OBSERVATIONALLY_EQUIVALENT"


def test_observation_identity_and_experiment_contract_cannot_be_rebound():
    models = model_class()
    learner = ExperimentLearner(models)
    obs = Observation("e", "q0", "0", "host", models.fingerprint)
    learner.observe(obs)
    for changed in (replace(obs, outcome="1"), replace(obs, model_class="other"), replace(obs, query="q9")):
        with pytest.raises(ValueError):
            learner.observe(changed)
