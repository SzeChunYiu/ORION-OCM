import json
import subprocess
import sys
from pathlib import Path

import signature_hole_census as shc

HERE = Path(__file__).resolve().parent


def test_constraints_reject_known_incoherent_cells():
    assert shc.coherent(("DISCRETE_FINITE", "NONE", ("scalar_loss",), "BOUNDED_LOOP", "NONE")) == (False, "C1")
    assert shc.coherent(("DISCRETE_FINITE", "LOCAL_O1", (), "ACYCLIC_FIXED_DEPTH", "PARAMETER_ARRAY")) == (False, "C2")
    assert shc.coherent(("DISCRETE_FINITE", "LOCAL_O1", (), "ACYCLIC_FIXED_DEPTH", "TRACE_DISTRIBUTION")) == (False, "C3")
    assert shc.coherent(("DISCRETE_FINITE", "LOCAL_O1", (), "ENUMERATE_TEST_CYCLE", "RULE_SET")) == (False, "C4")
    assert shc.coherent(("DISCRETE_FINITE", "DENSE_LINEAR", ("exact_counterexample",), "ACYCLIC_FIXED_DEPTH", "RULE_SET")) == (False, "C5")


def test_every_registered_occupant_is_coherent_and_unique_by_name():
    names = [o[0] for o in shc.OCCUPANTS]
    assert len(names) == len(set(names))
    for o in shc.OCCUPANTS:
        ok, why = shc.coherent(shc.cell_of(o))
        assert ok, (o[0], why)


def test_receipt_is_reproducible_and_counts_stable(tmp_path):
    # run the census in a temp dir twice; receipts must be byte-identical
    outs = []
    for _ in range(2):
        subprocess.run([sys.executable, str(HERE / "signature_hole_census.py")], cwd=tmp_path, check=True, capture_output=True)
        outs.append((tmp_path / "SIGNATURE_HOLE_CENSUS_V1.json").read_bytes())
    assert outs[0] == outs[1]
    d = json.loads(outs[0])
    assert d["raw_cells"] == 3 * 4 * 16 * 5 * 6
    assert d["coherent_cells"] + sum(d["incoherent_by_constraint"].values()) == d["raw_cells"]
    assert d["occupied_cells"] + d["hole_cells"] == d["coherent_cells"]
    assert d["registered_occupants"] == len(shc.OCCUPANTS)
    # the committed receipt must match the code
    committed = json.loads((HERE / "SIGNATURE_HOLE_CENSUS_V1.json").read_text())
    for k in ("coherent_cells", "occupied_cells", "hole_cells", "registered_occupants"):
        assert committed[k] == d[k]


def test_frontier_holes_are_holes_adjacent_to_occupants():
    d = json.loads((HERE / "SIGNATURE_HOLE_CENSUS_V1.json").read_text())
    occ = {shc.cell_of(o) for o in shc.OCCUPANTS}
    for r in d["frontier_holes_distance1_closing_structural_projection"]:
        c = r["cell"]
        cell = (c["theta_type"], c["update_locality"], tuple(sorted(c["feedback_dependence"])), c["execution_shape"], c["store_discipline"])
        assert cell not in occ
        assert shc.coherent(cell)[0]
        assert min(shc.hamming(cell, o) for o in occ) == 1
        assert r["structural_pairwise_holes_closed"] >= 1
