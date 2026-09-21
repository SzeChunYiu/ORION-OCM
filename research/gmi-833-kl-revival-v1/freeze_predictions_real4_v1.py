"""Freeze the set-valued emissions of F on SIGMA_REAL4 under SB-L* BEFORE any
SIGMA_REAL4 training exists (FREEZE_V1.md section 3.5, commit 2).

Route A (structural): never enumerates a world.  Contains no outcome oracle and
cannot see any measured capability of any SIGMA_REAL4 machine.

Run:  python3 -I -B freeze_predictions_real4_v1.py
"""

from fractions import Fraction
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import heldout_universes_real4_v1 as r4  # noqa: E402

hu = r4.hu
UNSAT = "UNSATISFIED"

CLAIM_CEILING = ("GMI_833_KL_REVIVAL_SET_VALUED_BRIDGE_AND_POSTERIOR_DATED_FUTURITY"
                 "_AT_REGISTERED_FINITE_SCOPE")


def value_key(v):
    return (1, Fraction(0)) if v == UNSAT else (0, v)


def image_str(image):
    return ",".join(str(v) for v in sorted(image, key=value_key))


def set_valued_sweep(parent, table, machines, mu):
    """Per input: the set-valued emission I(x) under `table`, its CB-PROTO
    reference I_PROTO(x), and the ND-1 / ND-2 flags."""
    n = parent.N
    full = (1 << n) - 1
    sets = {}
    proto = {}
    for contract in parent.CONTRACTS:
        verified = hu.VERIFIED[contract]
        sets[contract] = [r4.value_set(mu, verified, r4.admissible_bits(table, m))
                          for m in machines]
        proto[contract] = [r4.value_set(mu, verified, r4.proto_admissible_bits(m))
                           for m in machines]
    totals = {"inputs": 0, "inconsistent": 0, "point": 0, "set": 0,
              "nd1": 0, "nd2": 0, "point_degenerate": 0,
              "set_sizes": {}, "nd2_values": {}}
    lines = []
    for idx, entry in enumerate(parent.main_grid()):
        (k_index, r_value, d_value, b_value, h_value,
         u_id, u_kind, u_mask, alpha, contract, tau) = entry
        totals["inputs"] += 1
        survivors = parent.survivor_mask(k_index, d_value, b_value, h_value, u_mask)
        if survivors == 0:
            totals["inconsistent"] += 1
            lines.append("%d\tINCONSISTENT_REGISTERED_ASSUMPTIONS\t\t\t0\t0" % idx)
            continue
        res = parent.RES_MASKS[r_value]
        admissible = survivors & res
        refused = survivors & ~res & full
        image = set()
        ref = set()
        if refused:
            image.add(UNSAT)
            ref.add(UNSAT)
        for i in parent.bits_of(admissible):
            image |= sets[contract][i]
            ref |= proto[contract][i]
        has_positive = any(v != UNSAT and v > 0 for v in image)
        nd1 = (image < ref) and has_positive
        if len(image) == 1:
            v = next(iter(image))
            nd2 = (v != UNSAT and v > 0)
            totals["point"] += 1
            if nd2:
                totals["nd2"] += 1
                totals["nd2_values"][str(v)] = totals["nd2_values"].get(str(v), 0) + 1
            else:
                totals["point_degenerate"] += 1
            disp = "IDENTIFIED"
        else:
            nd2 = False
            totals["set"] += 1
            totals["set_sizes"][str(len(image))] = totals["set_sizes"].get(str(len(image)), 0) + 1
            disp = "CANNOT_IDENTIFY"
        if nd1:
            totals["nd1"] += 1
        lines.append("%d\t%s\t%s\t%s\t%d\t%d" % (idx, disp, image_str(image),
                                                  image_str(ref), int(nd1), int(nd2)))
    stream = "\n".join(lines) + "\n"
    return totals, stream


def main():
    table, evidence = r4.derive_bridge()
    if not r4.bridge_matches_freeze(table):
        raise SystemExit("derived bridge differs from FREEZE_V1 3.3: %r" % (table,))
    parent = hu.load_parent()
    base = hu.sigma_1()
    baseline = hu.code_fingerprint(parent)
    spec = r4.sigma_real4(table)
    import heldout_universes_v2 as hv2
    import heldout_universes_v3 as hv3
    import heldout_universes_v4 as hv4
    certs = [
        hu.disjointness_certificate(base, "SIGMA_1", spec["UNIVERSE"], "SIGMA_REAL4"),
        hu.disjointness_certificate(hu.SYN_RAW, "SIGMA_SYN", spec["UNIVERSE"], "SIGMA_REAL4"),
        hu.disjointness_certificate(hu.ARCH_RAW, "SIGMA_ARCH", spec["UNIVERSE"], "SIGMA_REAL4"),
        hu.disjointness_certificate(hu.REAL_RAW, "SIGMA_REAL", spec["UNIVERSE"], "SIGMA_REAL4"),
        hu.disjointness_certificate(hv2.REAL2_RAW, "SIGMA_REAL2", spec["UNIVERSE"], "SIGMA_REAL4"),
        hu.disjointness_certificate(hv3.REAL3_RAW, "SIGMA_REAL3", spec["UNIVERSE"], "SIGMA_REAL4"),
        hu.disjointness_certificate(hv4.SYN2_RAW, "SIGMA_SYN2", spec["UNIVERSE"], "SIGMA_REAL4"),
        hu.disjointness_certificate(hv4.ARCH2_RAW, "SIGMA_ARCH2", spec["UNIVERSE"], "SIGMA_REAL4"),
    ]
    fingerprint = hu.install_universe(parent, r4.clean_spec(spec))
    totals, stream = set_valued_sweep(parent, table, r4.REAL4_MACHINES, hu.MU_REAL)
    stream_sha = hashlib.sha256(stream.encode("utf-8")).hexdigest()

    bridge = {}
    for m in r4.REAL4_MACHINES:
        bridge[r4.machine_key(m)] = {
            "intervals": [list(r4.band_interval(table, m, j)) for j in range(3)],
            "admissible_bits": list(r4.admissible_bits(table, m)),
            "resolved": len(r4.admissible_bits(table, m)) == 1,
        }
    out = {
        "schema": "GMI_833_KL_REVIVAL_FROZEN_PREDICTIONS_REAL4_V1",
        "claim_ceiling": CLAIM_CEILING,
        "freeze_commit": r4.FREEZE_COMMIT,
        "parent_file_blob_sha": hu.git_blob_sha(hu.PARENT_FILE),
        "parent_code_fingerprint_before": baseline[0],
        "parent_code_unchanged": fingerprint[0] == baseline[0],
        "bridge_rule": "CR-1 (FREEZE_V1.md 3.3)",
        "bridge_table_derived": table,
        "bridge_table_matches_freeze": True,
        "bridge_evidence": evidence,
        "bridge_per_machine": bridge,
        "committed_cells": len(r4.committed_cells(table, r4.REAL4_MACHINES)),
        "resolved_machines": sum(1 for v in bridge.values() if v["resolved"]),
        "population": {
            "name": "SIGMA_REAL4",
            "machines": [list(m) for m in r4.REAL4_MACHINES],
            "sizes": list(r4.REAL4_SIZES),
            "rho3_values": sorted(set(rec[4][3] for rec in spec["UNIVERSE"])),
            "grid": dict((k, [str(x) for x in v] if k == "tau_values" else
                          [list(x) if isinstance(x, tuple) else x for x in v])
                         for k, v in r4.REAL4_GRID.items()),
            "disjointness": certs,
            "all_disjoint": all(c["disjoint"] for c in certs),
        },
        "real_system_protocol": {
            "source": hu.REAL_SOURCE,
            "word_length": hu.REAL_WORD_LEN,
            "train_windows": list(hu.REAL_TRAIN_WINDOWS),
            "protected_eval_windows": list(hu.REAL_EVAL_WINDOWS),
            "training": hu.REAL_TRAINING,
            "training_budget_unchanged_from_v1": True,
            "solved_band": str(r4.REAL4_BAND),
            "mu": [str(x) for x in hu.MU_REAL],
        },
        "set_valued_census": totals,
        "stream_rows": totals["inputs"],
        "stream_sha256": stream_sha,
        "stream_columns": "index\tdisposition\tI(x)\tI_PROTO(x)\tND1\tND2",
    }
    text = json.dumps(out, indent=2, sort_keys=True)
    with open(os.path.join(HERE, "FROZEN_PREDICTIONS_REAL4_V1.json"), "w") as handle:
        handle.write(text)
        handle.write("\n")
    lines = stream.rstrip("\n").split("\n")
    sample = ["# universe=SIGMA_REAL4 rows=%d rule=every_101st_row stream_sha256=%s"
              % (len(lines), stream_sha)]
    for i in range(0, len(lines), 101):
        sample.append(lines[i])
    with open(os.path.join(HERE, "FROZEN_PREDICTION_SAMPLE_REAL4_V1.tsv"), "w") as handle:
        handle.write("\n".join(sample) + "\n")
    sys.stdout.write(json.dumps({"census": totals, "stream_sha256": stream_sha,
                                 "resolved_machines": out["resolved_machines"],
                                 "all_disjoint": out["population"]["all_disjoint"],
                                 "parent_code_unchanged": out["parent_code_unchanged"]},
                                indent=1, sort_keys=True))
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
