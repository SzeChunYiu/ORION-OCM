"""Test loading and representation extraction; expected values live in independent oracles."""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import core_v27 as core
import lts_v27 as lts
import events_v27 as events
import tests_v27 as tests
import tasks_v27 as tasks
import oracle_v27 as oracle


def event_data(event):
    return event.n, event.m, event.rows


def test_data(test):
    return test.n, test.m, tuple((label, event_data(event)) for label, event in test.outcomes)
