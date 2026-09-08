from __future__ import annotations

import pathlib
import random
import sys

HERE = pathlib.Path(__file__).parent
DEV = HERE.parent / "developmental-spine"
COG = HERE.parent / "cognitive-ladder"
for path in (DEV, COG, HERE):
    sys.path.insert(0, str(path))

import dev6_arms as A
import run_dev6 as D6
import shortcircuit_parent as S
from dev4 import build_level_world, d1_stream
from retain import demand_stream


def _fixture(level=3, d1_length=100, budget=1024, skew=1.0, rep=0):
    seed = D6._seed(f"dev6-{level}-{d1_length}-{budget}-{skew}", rep)
    world, _truth = build_level_world(
        D6.SW["rule_count"], D6.SW["extension"], level, random.Random(seed ^ 0xA1)
    )
    d0 = demand_stream(world.base, D6.SW["d0_length"], skew, random.Random(seed ^ 0xB2))
    d1 = d1_stream(world, d1_length, skew, random.Random(seed ^ 0xC3))
    return world, d0, d1, budget


def test_source_transform_is_exactly_one_substitution():
    fidelity = S.source_fidelity()
    assert fidelity["donor_blob_sha"] == S.DONOR_BLOB_SHA
    assert fidelity["old_fragment_occurrences"] == 1
    assert fidelity["new_fragment_occurrences"] == 1
    assert fidelity["substitution_only"] is True


def test_shortcircuit_preserves_semantics_and_never_scans_more():
    world, d0, d1, budget = _fixture()
    _a0, fullscan, _c0, full_m = A._run(world, d0, d1, budget, "unanimity_naive")
    _a1, short, _c1, short_m = S.run_shortcircuit(world, d0, d1, budget)
    assert S.phase_semantics(fullscan) == S.phase_semantics(short)
    assert fullscan.correctness() == short.correctness() == 1.0
    assert fullscan.verifications == short.verifications
    assert full_m["consultations"] == short_m["consultations"]
    assert full_m["maintenance"] == short_m["maintenance"] == 0
    assert short_m["consultation_charge"] <= full_m["consultation_charge"]
    assert short.total_work(0.0) <= fullscan.total_work(0.0)


def test_shortcircuit_is_strict_on_a_large_language_cell():
    world, d0, d1, budget = _fixture(level=3, d1_length=400, budget=1024)
    _a0, fullscan, _c0, full_m = A._run(world, d0, d1, budget, "unanimity_naive")
    _a1, short, _c1, short_m = S.run_shortcircuit(world, d0, d1, budget)
    assert short_m["consultation_charge"] < full_m["consultation_charge"]
    assert short.total_work(0.0) < fullscan.total_work(0.0)
