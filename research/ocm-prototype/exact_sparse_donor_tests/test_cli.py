"""Bounded untimed native JSON entry point; actual G1 uses the same Python API."""
import json
import subprocess
import sys
import pytest


@pytest.mark.parametrize("arm", ["reference", "sympy"])
def test_named_fixture_cli_has_complete_stage_and_channel_counts(arm, prototype_subprocess_env):
    run = subprocess.run([sys.executable, "-m", "exact_sparse_donor_consumer",
                          "--arm", arm, "--fixture", "base"],
                         capture_output=True, text=True, timeout=15, env=prototype_subprocess_env)
    assert run.returncode == 0, run.stderr
    assert run.stdout.strip(), "missing untimed JSON CLI output"
    result = json.loads(run.stdout)
    assert result["consumer"]["status"] == "COMPLETED"
    assert result["consumer"]["answer"]["result"] == 42
    assert result["consumer"]["committed"]
    assert result["logical_fixed_point_calls"] == 4
    assert len(result["stage_counts"]) == 10 and set(result["stage_counts"].values()) == {1}
    assert result["performance_authority"] == "NOT_TESTED"
