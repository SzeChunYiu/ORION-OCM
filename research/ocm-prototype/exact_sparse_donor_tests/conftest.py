"""Expose this research directory in pytest and in its explicit child controls."""
import os
from pathlib import Path
import sys
import pytest

PROTOTYPE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROTOTYPE))


@pytest.fixture
def prototype_subprocess_env():
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(filter(None, (str(PROTOTYPE), env.get("PYTHONPATH"))))
    return env
