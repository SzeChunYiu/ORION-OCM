"""t11_module_v1.py -- HST-T11 finite exact certificate: major-transition / module-
promotion compression criterion. Generates T11_MODULE_PROMOTION_V1.json. Deterministic.

World (FW1 restricted): operators {a2, m2} on Z_16. Repeated pattern M = (m2, a2)
(function x -> 2x+2). Module token "MA" with that function; CALLING MA costs 1 op-slot
(like any operator). Frozen cost ledger (op-slot units, exact rationals):
  C_def   = 3      one-time module definition (body 2 + registration 1)
  C_iface = 1/2    per-call interface/dispatch overhead
  C_maint = 1      one-time maintenance over the horizon
  C_rev   = 0      expected revision cost (none in this frozen world)
Per-use gross saving = 2 op-slots -> 1 call; NET saving per use = 2 - 1 - 1/2 = 1/2.
T05 arithmetic: promote iff  h * (1/2) > 3 + 1 + 0  <=>  h > 8.  H* = 8 exactly.

Suite for reuse count h: tasks tau_s = (s, 2s+2 mod 16), s = 0..h-1; each exhibited
solution is exactly the pattern (m2, a2) (cost 2). Interface preservation is CHECKED:
f_(m2,a2) == f_MA as functions on ALL 16 states, for every substituted program.
"""
import json
import time
from fractions import Fraction
from typing import Dict, List, Tuple

import finite_world_v1 as fw

C_DEF = Fraction(3)
C_IFACE = Fraction(1, 2)
C_MAINT = Fraction(1)
C_REV = Fraction(0)
GROSS_SAVE = Fraction(2) - Fraction(1)   # 2 op-slots -> 1 call
NET_SAVE = GROSS_SAVE - C_IFACE          # 1/2


def main() -> dict:
    t0 = time.time()
    table = dict(fw.OPS)                                   # {a2, m2}
    ma_fn = tuple(table["a2"][v] for v in table["m2"])     # a2 after m2
    table_ma = dict(table)
    table_ma["MA"] = ma_fn

    # interface preservation: pattern function == module function on ALL states
    pattern_fn = fw.word_fn(("m2", "a2"), table)
    iface_ok_all_states = pattern_fn == ma_fn
    # and per-substituted-program equivalence is trivial here (single occurrence,
    # whole program), still checked program-by-program below per suite task.

    threshold = (C_DEF + C_MAINT + C_REV) / NET_SAVE       # 8
    regimes = []
    for h in (7, 8, 9):
        tasks = [("m%02d" % s, s, (2 * s + 2) % fw.N) for s in range(h)]
        prog_cost_unpromoted = Fraction(0)
        prog_cost_promoted = Fraction(0)
        iface_checks = []
        for tid, s, g in tasks:
            assert fw.adm(("m2", "a2"), (tid, s, g), table), "suite task unsolved by pattern"
            assert fw.adm(("MA",), (tid, s, g), table_ma), "suite task unsolved by module"
            # program-level interface preservation: same function on all 16 states
            iface_checks.append(fw.word_fn(("m2", "a2"), table) == fw.word_fn(("MA",), table_ma))
            prog_cost_unpromoted += Fraction(2)             # (m2,a2) = 2 op-slots
            prog_cost_promoted += Fraction(1) + C_IFACE     # MA call + interface
        total_unpromoted = prog_cost_unpromoted
        total_promoted = C_DEF + C_MAINT + C_REV + prog_cost_promoted
        regimes.append({
            "reuse_count_h": h,
            "n_programs": h,
            "total_cost_unpromoted": [str(total_unpromoted), float(total_unpromoted)],
            "total_cost_promoted": [str(total_promoted), float(total_promoted)],
            "promote": total_promoted < total_unpromoted,
            "interface_preservation_all_states_all_programs": all(iface_checks),
        })
    h_star = threshold
    flip_ok = (regimes[0]["promote"] is False and regimes[1]["promote"] is False
               and regimes[2]["promote"] is True
               and regimes[1]["total_cost_unpromoted"] == regimes[1]["total_cost_promoted"])

    doc = {
        "certificate_id": "T11_MODULE_PROMOTION_V1",
        "theorem_id": "HST-T11",
        "world": fw.WORLD_SPEC,
        "scope_statement": "P2 finite exact over universe FW1 with the frozen cost ledger "
                           "below and reuse suites of size h in {7,8,9}; the criterion is "
                           "ARITHMETIC at this scope; no claim that real development "
                           "discovers modules spontaneously (that stays P4).",
        "cost_ledger_frozen": {
            "C_def": [str(C_DEF), float(C_DEF)],
            "C_iface_per_call": [str(C_IFACE), float(C_IFACE)],
            "C_maint": [str(C_MAINT), float(C_MAINT)],
            "C_revision_expected": [str(C_REV), float(C_REV)],
            "gross_saving_per_use": [str(GROSS_SAVE), float(GROSS_SAVE)],
            "net_saving_per_use": [str(NET_SAVE), float(NET_SAVE)],
            "unit": "operator-slot cost units"},
        "module": {"token": "MA", "body": ["m2", "a2"], "function": "x -> 2x+2 mod 16",
                   "pattern_image_tuple": list(ma_fn),
                   "interface_preservation_all_16_states": iface_ok_all_states,
                   "interface_definition": "promoted program computes the SAME function "
                                           "on every state of Z_16 as the expanded "
                                           "program (checked by exhaustive evaluation on "
                                           "all 16 states, per program)"},
        "criterion": "promote iff h * net_saving > C_def + C_maint + C_rev",
        "threshold_H_star": [str(h_star), float(h_star)],
        "regimes": regimes,
        "flip_verified": flip_ok,
        "runtime_seconds": round(time.time() - t0, 3),
        "deterministic": True,
    }
    assert iface_ok_all_states, "interface preservation failed"
    assert flip_ok, "promotion decision did not flip across the threshold as derived"
    return doc


if __name__ == "__main__":
    doc = main()
    with open("T11_MODULE_PROMOTION_V1.json", "w") as fh:
        json.dump(doc, fh, sort_keys=True, indent=1)
    print("T11 OK: H*=%s regimes: %s" % (
        doc["threshold_H_star"][0],
        [(r["reuse_count_h"], r["promote"],
          r["total_cost_unpromoted"][0], r["total_cost_promoted"][0]) for r in doc["regimes"]]))
