"""Pytest plugin that records every incumbent selection point the suite exercises.

The repository's own test suite is the study population: it is the real, current
workload the runtime is actually run on, and #152 requires real workloads rather
than an invented benchmark. The plugin installs the read-only instrument for the
whole session and tags each record with the test that produced it, so every row
in the receipt is traceable to a named source.
"""
from __future__ import annotations

import json
import os
import pathlib

import instrument
from ocm.runtime import solve as S

_CAP = instrument.Capture()
_ORIGINAL = (S.compose_stage, S.check_stage)


def pytest_configure(config):
    _CAP._compose, _CAP._check = _ORIGINAL
    S.compose_stage, S.check_stage = _CAP.compose, _CAP.check


def pytest_runtest_setup(item):
    _CAP.source = item.nodeid


def pytest_runtest_teardown(item, nextitem):
    _CAP.flush_uncchecked()


def pytest_unconfigure(config):
    S.compose_stage, S.check_stage = _ORIGINAL
    _CAP.flush_uncchecked()
    out = pathlib.Path(os.environ.get("RRO_OUT", "rro_raw.json"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps([r.as_dict() for r in _CAP.records], indent=1) + "\n")
