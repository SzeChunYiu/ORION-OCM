"""Operational public-chat regression across actual process boundaries."""
from persistent_language_smoke import run


def test_learned_composition_and_support_changes_survive_process_restart():
    receipt = run()
    failures = [case for case in receipt["checks"] if not case["passed"]]
    assert not failures, failures
    assert receipt["passed"]
