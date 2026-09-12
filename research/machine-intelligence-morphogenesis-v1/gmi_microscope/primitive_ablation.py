"""RV-377-110 / critical-path item 1 -- leave-one-out ablation of the primitive alphabet.

The zero-prior question is: are the 36 primitive kinds in `morph.KINDS` derivable from one
another, or is some subset irreducible?  This module answers it by construction rather than
by argument.  For each kind k it DELETES k from the alphabet, rebuilds the operator grammar
over the reduced alphabet, and re-runs the B1 neutral search on the registered discriminating
ecologies.  If the reduced alphabet still reaches an admissible witness, k was not needed --
it is REDUCIBLE.  If admissibility is lost, k is IRREDUCIBLE at registered scope and is an
axiom candidate: something the theory must assume rather than derive.

Rule 40 discipline: only ecologies that SURVIVE the best-constant control are used.  Per
RV-377-108, E_sym3 is NON_DISCRIMINATING and E_parity is WITHIN_QUANTIZATION on both
criteria, so neither can certify anything and both are excluded.
"""
from __future__ import annotations

import importlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))

# Discriminating at >= 1 fx unit, per the RV-377-108 constant-control audit.
DISCRIMINATING = ("E_wit1", "E_smooth1", "E_smooth3", "E_sym5")

# Excluded, with the reason recorded so the omission is visible rather than silent.
EXCLUDED = {"E_sym3": "NON_DISCRIMINATING on both criteria (best constant 0.9062 / 0.8750)",
            "E_parity": "WITHIN_QUANTIZATION on both criteria (0.401 fx units)"}

# The I/O boundary. morphgen already refuses to propose these, and no ecology is well-formed
# without them, so ablating them tests nothing about derivability.
STRUCTURAL = ("INPUT", "OUTPUT", "TARGET")


def _fresh(drop=None):
    """reload morph + morphgen + b1 with `drop` removed from the alphabet."""
    for m in ("gmi_microscope.b1", "gmi_microscope.morphgen", "gmi_microscope.morph"):
        sys.modules.pop(m, None)
    morph = importlib.import_module("gmi_microscope.morph")
    if drop is not None:
        if drop not in morph.KINDS:
            raise KeyError(drop)
        del morph.KINDS[drop]
        if hasattr(morph, "CLASS_OF"):
            morph.CLASS_OF.pop(drop, None)
    morphgen = importlib.import_module("gmi_microscope.morphgen")
    b1 = importlib.import_module("gmi_microscope.b1")
    return morph, morphgen, b1


def run_one(drop, eco, seed, evaluations, tag_prefix="ABL"):
    t = time.perf_counter()
    try:
        _, _, b1 = _fresh(drop)
        r = b1.main(seed=seed, evaluations=evaluations, eco_name=eco,
                    tag=f"{tag_prefix}_{drop or 'FULL'}")
        best = max((v["capability"] for v in r["best_by_carrier"].values()), default=0.0)
        return {"drop": drop, "ecology": eco, "seed": seed, "status": "OK",
                "best_capability": best,
                "admissible": best >= b1.THETA,
                "carriers_recovered": r["mechanism_classes_recovered"],
                "n_carriers_admissible": sum(1 for v in r["best_by_carrier"].values() if v["admissible"]),
                "wall": round(time.perf_counter() - t, 2)}
    except KeyError as e:
        # RV-377-118 Lane C instrument note: `morphgen`'s mutation operators construct some
        # kinds BY NAME (ABSTAIN, VERIFY, LOOKUP, LINEAR, PROGEXEC, ...), so deleting such a
        # kind from the alphabet is not a leave-one-out test of derivability -- the generator
        # crashes on its own hard-coded reference.  Recorded as its own status and written as
        # a receipt so the unit is EXECUTED, not silently absent (18 of 33 kinds on E_wit1 in
        # RV-377-110 left no receipt for exactly this reason).  Repairing the generator is a
        # separate frozen revival, never a silent edit of this instrument.
        if e.args and e.args[0] == drop:
            rec = {"drop": drop, "ecology": eco, "seed": seed, "status": "STRUCTURAL_TO_GENERATOR", "tag_prefix": tag_prefix,
                   "error": repr(e)[:300],
                   "reason": "morphgen constructs this kind by name; ablation is a generator crash, not a derivability test",
                   "wall": round(time.perf_counter() - t, 2)}
            _write_structural_receipt(rec)
            return rec
        return {"drop": drop, "ecology": eco, "seed": seed, "status": "ERROR",
                "error": repr(e)[:300], "wall": round(time.perf_counter() - t, 2)}
    except Exception as e:
        return {"drop": drop, "ecology": eco, "seed": seed, "status": "ERROR",
                "error": repr(e)[:300], "wall": round(time.perf_counter() - t, 2)}


def _write_structural_receipt(rec):
    res = os.path.join(os.path.dirname(HERE), "microscopes", "results")
    os.makedirs(res, exist_ok=True)
    path = os.path.join(res, f"STAGE_B1_{rec.get('tag_prefix', 'ABL')}_{rec['drop']}_{rec['ecology']}_S{rec['seed']}.json")
    with open(path, "w") as f:
        json.dump({"schema": "GMIPrimitiveAblationStructuralReceiptV1", "revival_id": "RV-377-118",
                   "lane": "RV118-C", **rec}, f, indent=1, sort_keys=True)


def alphabet():
    _, _, _ = None, None, None
    m = importlib.import_module("gmi_microscope.morph")
    return sorted(m.KINDS)
