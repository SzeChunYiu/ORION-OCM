"""Custody amendment: correct the Phi_countdisp rows in FROZEN_FIXTURES_E1.json.

The design probe implemented Phi_countdisp as |u|+kappa+rho*(symbols in the
opcost table), which counts BASE symbols as dispatches; the freeze text
defines Phi_countdisp = |u|+kappa+rho*(#macro symbols in u).  This patch
rewrites the informational charge_paths.countdisp rows to the freeze-text
conformant values recomputed by the (corrected) implementation, and records
the old values under charge_paths_countdisp_superseded_probe_values.
"""
import json

fx = json.load(open("FROZEN_FIXTURES_E1.json"))
receipt = json.load(open("RESULT_E1.json"))

for cid, entry in fx["corpora"].items():
    old = entry["charge_paths"]["countdisp"]
    new = receipt["corpora"][cid]["charge_paths"]["countdisp"]
    entry["charge_paths_countdisp_superseded_probe_values"] = old
    entry["charge_paths"]["countdisp"] = new

out = json.dumps(fx, indent=1, sort_keys=True) + "\n"
open("FROZEN_FIXTURES_E1.json", "w").write(out)
import hashlib
print("patched; sha256:", hashlib.sha256(out.encode()).hexdigest())
