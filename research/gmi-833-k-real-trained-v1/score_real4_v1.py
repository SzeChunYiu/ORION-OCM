#!/usr/bin/env python3
"""Canonical executor for gmi-833-k-real-trained-v1 (#833 Section K, real trained systems).

Route A (structural): re-derives the frozen 51,840-input set-valued emission
stream of the UNMODIFIED parent predictor F on SIGMA_REAL4 under the SB-L*
bridge, refuses to proceed unless the stream sha256 matches the pinned freeze,
then scores soundness against the committed real-training receipt
REAL_MEASURED_V4.json (32 real trained systems) and the truthfulness of the
bridge, plus the NULL_RANDOM_COMMIT null and the HK1..HK7 hostiles.

Stdlib only, exact Fraction arithmetic, no torch (training receipts are
committed data, read-only).
"""

from fractions import Fraction
import hashlib
import json
import os
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVAL_PKG = str(HERE.parents[1] / "research" / "gmi-833-capability-predictor-evaluation-v1")
PRED_PKG = str(HERE.parents[1] / "research" / "gmi-833-capability-predictor-v1")
for p in (str(HERE), EVAL_PKG, PRED_PKG):
    if p not in sys.path:
        sys.path.insert(0, p)

import heldout_universes_v1 as hu            # noqa: E402
import heldout_universes_real4_v1 as r4      # noqa: E402  (vendored, byte-exact)

UNSAT = "UNSATISFIED"
CLAIM_CEILING = "CAPABILITY_PREDICTOR_VALIDATED_ON_REAL_TRAINED_SYSTEMS_AT_REGISTERED_SCOPE"
FORBIDDEN_PROMOTIONS = (
    "REAL_SCALE_FRONTIER_GENERALIZATION",
    "FULL_CAPABILITY_COVERAGE",
    "M5",
    "PREDICTOR_RETRAINED_OR_FITTED",
    "REAL_TRAINING_OUTCOMES_GENERALISE_BEYOND_THE_PINNED_SOURCE",
    "COMPLETE_GMI",
)
STREAM_SHA256 = "0c81049d6c75062bc9a6438f0bda57558743bec53e76e0c3c3f5677e12b6a854"
PARENT_BLOB_SHA = "7f1bb6808901be2291bf575ee3178247d14d01d4"


def value_key(v):
    return (1, Fraction(0)) if v == UNSAT else (0, v)


def image_str(image):
    return ",".join(str(v) for v in sorted(image, key=value_key))


def git_blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def vendored_blob_ok():
    checks = {}
    for name, expect in (
        ("heldout_universes_real4_v1.py", "d7b821441b1d64c49ddea67474f444d2de180618"),
        ("FROZEN_PREDICTIONS_REAL4_V1.json", "41661ff7bc63bad218679110de0bc713570ea6d1"),
        ("REAL_MEASURED_V4.json", "96457f37c5a67d6c8aab1fbb8cf7a740218f839a"),
    ):
        data = (HERE / name).read_bytes()
        checks[name] = git_blob_sha(data) == expect
    checks["parent_blob"] = git_blob_sha((Path(PRED_PKG) / "capability_predictor_v1.py").read_bytes()) == PARENT_BLOB_SHA
    return checks


def build_stream(parent, table, machines, mu):
    """Route A: recompute the set-valued stream exactly as frozen.

    Mirrors `freeze_predictions_real4_v1.py::set_valued_sweep` byte-for-byte:
    I_PROTO(x) is built from `proto_admissible_bits` (CB-PROTO), refused
    survivors add UNSATISFIED to both image and reference, and `& full` masks
    `~res` to the parent's realization width.
    """
    n = parent.N
    full = (1 << n) - 1
    sets = {}
    proto = {}
    for contract in parent.CONTRACTS:
        verified = hu.VERIFIED[contract]
        sets[contract] = [r4.value_set(mu, verified, r4.admissible_bits(table, m)) for m in machines]
        proto[contract] = [r4.value_set(mu, verified, r4.proto_admissible_bits(m)) for m in machines]
    totals = {"inputs": 0, "inconsistent": 0, "point": 0, "set": 0,
              "nd1": 0, "nd2": 0, "point_degenerate": 0, "set_sizes": {}, "nd2_values": {}}
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
        lines.append("%d\t%s\t%s\t%s\t%d\t%d" % (idx, disp, image_str(image), image_str(ref),
                                                 int(nd1), int(nd2)))
    return totals, ("\n".join(lines) + "\n")


def measured_cap(bits, mu, contract):
    verified = hu.VERIFIED[contract]
    total = Fraction(0)
    for j in range(3):
        if verified[j] and ((bits >> j) & 1):
            total += mu[j]
    return total


def route_a_soundness(parent, table, machines, mu, measured, stream_images):
    """Soundness: extcap(x, b_real) in I(x) over every input with survivors.

    With b_real(i) the measured solved bits of the trained system i, the actual
    external capability under (E,R) is UNSATISFIED outside the budget else the
    measured contract value.  An over-budget system is scored UNSATISFIED, never
    deleted (KP-1B discipline).
    """
    violations = 0
    inputs = 0
    if stream_images is None:
        return 0, 0
    sets = {}
    for contract in parent.CONTRACTS:
        verified = hu.VERIFIED[contract]
        sets[contract] = [r4.value_set(mu, verified, r4.admissible_bits(table, m)) for m in machines]
    for idx, entry in enumerate(parent.main_grid()):
        (k_index, r_value, d_value, b_value, h_value,
         u_id, u_kind, u_mask, alpha, contract, tau) = entry
        survivors = parent.survivor_mask(k_index, d_value, b_value, h_value, u_mask)
        if survivors == 0:
            continue
        inputs += 1
        res = parent.RES_MASKS[r_value]
        image = stream_images[idx]
        for i in parent.bits_of(survivors):
            if (res >> i) & 1:
                val = measured_cap(measured[i], mu, contract)
            else:
                val = UNSAT
            if val not in image:
                violations += 1
    return inputs, violations


def truthfulness(table, machines, measured):
    """b_real(i) in Adm(i) for every machine."""
    good = 0
    fails = []
    for i, m in enumerate(machines):
        adm = r4.admissible_bits(table, m)
        if measured[i] in adm:
            good += 1
        else:
            fails.append((r4.machine_key(m), measured[i], list(adm)))
    return good, fails


def null_random_commit(table, machines, measured, seeds=200, seed0=833):
    """NULL_RANDOM_COMMIT (FREEZE_V1 3.8): 200 seeded bridges with EXACTLY the
    same committed (machine, head) cell set as SB-L*, each committed singleton
    drawn uniformly from {UNSOLVED, SOLVED}.  Draws per (machine, head) cell --
    never at the table-parameter level, which would collapse cells and change
    the committed-cell set (the misspecification that inflated the old null).
    """
    committed = set(r4.committed_cells(table, machines))
    bands = (0, 1)  # UNSOLVED, SOLVED
    truthful = 0
    for s in range(seeds):
        draw = random.Random(seed0 + 1 + s)
        good = True
        for i, m in enumerate(machines):
            out = [None, None, None]
            for j in range(3):
                if (i, j) in committed:
                    out[j] = draw.choice(bands)
            in_adm = False
            for bits in range(8):
                ok = True
                for j in range(3):
                    if out[j] is not None and ((bits >> j) & 1) != out[j]:
                        ok = False
                        break
                if ok:
                    in_adm = True
                    break
            if not in_adm or measured[i] not in {b for b in range(8)
                    if all(out[j] is None or ((b >> j) & 1) == out[j] for j in range(3))}:
                good = False
                break
        if good:
            truthful += 1
    return truthful


def hostile_hk1(table, machines, mu, measured):
    """Drop the protocol clause: untrained heads free -> ND-1/ND-2 must fall."""
    base_tot, _ = build_stream_ctx(table, machines, mu)
    alt = dict(table); alt["untrained"] = "ABSTAIN"
    alt_tot, _ = build_stream_ctx(alt, machines, mu)
    return {"nd1_fell": alt_tot["nd1"] < base_tot["nd1"],
            "nd2_fell": alt_tot["nd2"] < base_tot["nd2"],
            "base": (base_tot["nd1"], base_tot["nd2"]),
            "hostile": (alt_tot["nd1"], alt_tot["nd2"]),
            "detected": alt_tot["nd1"] < base_tot["nd1"] and alt_tot["nd2"] < base_tot["nd2"]}


def build_stream_ctx(table, machines, mu):
    parent = hu.load_parent()
    spec = r4.clean_spec(r4.sigma_real4(table))
    hu.install_universe(parent, spec)
    return build_stream(parent, table, machines, mu)


def hostile_hk2(table, machines, mu):
    """Count {0} and {UNSATISFIED} as ND-2 -> ND-2 must rise."""
    _, stream = build_stream_ctx(table, machines, mu)
    inflated = sum(1 for line in stream.splitlines()
                   if "\tIDENTIFIED\t" in line and line.split("\t")[2] in ("0", UNSAT))
    _, stream_frozen = build_stream_ctx(table, machines, mu)
    base_nd2 = sum(1 for line in stream_frozen.splitlines()
                   if line.split("\t")[-1] == "1")
    return {"base_nd2": base_nd2, "inflated_count": inflated,
            "detected": inflated > base_nd2}


def hostile_hk3(table, machines, measured):
    """Flip MLP T1 commitment to SOLVED -> truthfulness must flag >= 1 machine."""
    alt = dict(table); alt["MLP_T1_trained"] = "SOLVED"
    good, fails = truthfulness(alt, machines, measured)
    return {"flagged": len(machines) - good, "detected": good < len(machines)}


def hostile_hk4(table, machines, measured):
    """Complement one machine's measured bits -> violations must appear."""
    flipped = list(measured)
    i = 0
    flipped[i] = 7 - flipped[i]  # complement of a 3-bit subset
    parent = hu.load_parent()
    spec = r4.clean_spec(r4.sigma_real4(table))
    hu.install_universe(parent, spec)
    sets = {}
    for contract in parent.CONTRACTS:
        verified = hu.VERIFIED[contract]
        sets[contract] = [r4.value_set(hu.MU_REAL, verified, r4.admissible_bits(table, m)) for m in machines]
    violations = 0
    for idx, entry in enumerate(parent.main_grid()):
        (k_index, r_value, d_value, b_value, h_value,
         u_id, u_kind, u_mask, alpha, contract, tau) = entry
        survivors = parent.survivor_mask(k_index, d_value, b_value, h_value, u_mask)
        if survivors == 0:
            continue
        res = parent.RES_MASKS[r_value]
        image = set()
        if survivors & ~res:
            image.add(UNSAT)
        for j in parent.bits_of(survivors & res):
            image |= sets[contract][j]
        if (res >> i) & 1:
            val = measured_cap(flipped[i], hu.MU_REAL, contract)
        else:
            val = UNSAT
        if val not in image:
            violations += 1
    return {"violations": violations, "detected": violations > 0}


def hostile_hk7():
    """Mutate the parent F blob -> blob-sha mismatch refused.

    Self-test of the custody detector: the actual parent file must match the
    pinned blob, and a synthetic one-byte mutation of the same bytes must
    produce a different sha (so a real mutation would be refused).
    """
    data = (Path(PRED_PKG) / "capability_predictor_v1.py").read_bytes()
    blob = git_blob_sha(data)
    mutated = bytearray(data)
    mutated[0] ^= 0x01
    mutated_blob = git_blob_sha(bytes(mutated))
    detected = (blob == PARENT_BLOB_SHA) and (mutated_blob != PARENT_BLOB_SHA) and (mutated_blob != blob)
    return {"parent_blob": blob, "mutated_blob": mutated_blob, "detected": detected}


def main():
    vend = vendored_blob_ok()
    if not all(vend.values()):
        raise SystemExit("vendored blob drift: %r" % vend)

    frozen = json.loads((HERE / "FROZEN_PREDICTIONS_REAL4_V1.json").read_text())
    measured_payload = json.loads((HERE / "REAL_MEASURED_V4.json").read_text())

    table, evidence = r4.derive_bridge()
    assert r4.bridge_matches_freeze(table), table

    parent = hu.load_parent()
    baseline = hu.code_fingerprint(parent)
    spec = r4.clean_spec(r4.sigma_real4(table))
    fingerprint = hu.install_universe(parent, spec)

    totals, stream = build_stream(parent, table, r4.REAL4_MACHINES, hu.MU_REAL)
    stream_sha = hashlib.sha256(stream.encode("utf-8")).hexdigest()
    stream_matches = stream_sha == STREAM_SHA256

    measured = [measured_payload["measured_solved_bits"][r4.machine_key(m)]
                for m in r4.REAL4_MACHINES]
    inputs, violations = (0, 0)
    good, fails = truthfulness(table, r4.REAL4_MACHINES, measured)
    null_truthful = null_random_commit(table, r4.REAL4_MACHINES, measured)

    # stream_images for soundness reuse: recompute images per input
    sets = {}
    for contract in parent.CONTRACTS:
        verified = hu.VERIFIED[contract]
        sets[contract] = [r4.value_set(hu.MU_REAL, verified, r4.admissible_bits(table, m))
                          for m in r4.REAL4_MACHINES]
    stream_images = []
    for idx, entry in enumerate(parent.main_grid()):
        (k_index, r_value, d_value, b_value, h_value,
         u_id, u_kind, u_mask, alpha, contract, tau) = entry
        survivors = parent.survivor_mask(k_index, d_value, b_value, h_value, u_mask)
        if survivors == 0:
            stream_images.append(frozenset())
            continue
        res = parent.RES_MASKS[r_value]
        image = set()
        if survivors & ~res:
            image.add(UNSAT)
        for j in parent.bits_of(survivors & res):
            image |= sets[contract][j]
        stream_images.append(frozenset(image))

    # recompute soundness with actual images
    violations = 0
    checked = 0
    for idx, entry in enumerate(parent.main_grid()):
        (k_index, r_value, d_value, b_value, h_value,
         u_id, u_kind, u_mask, alpha, contract, tau) = entry
        survivors = parent.survivor_mask(k_index, d_value, b_value, h_value, u_mask)
        if survivors == 0:
            continue
        checked += 1
        res = parent.RES_MASKS[r_value]
        image = stream_images[idx]
        for i in parent.bits_of(survivors):
            if (res >> i) & 1:
                val = measured_cap(measured[i], hu.MU_REAL, contract)
            else:
                val = UNSAT
            if val not in image:
                violations += 1

    hk = {
        "HK1_drop_protocol_clause": hostile_hk1(table, r4.REAL4_MACHINES, hu.MU_REAL, measured),
        "HK2_include_degenerate_nd2": hostile_hk2(table, r4.REAL4_MACHINES, hu.MU_REAL),
        "HK3_flip_mlp_t1": hostile_hk3(table, r4.REAL4_MACHINES, measured),
        "HK4_complement_receipt": hostile_hk4(table, r4.REAL4_MACHINES, measured),
        "HK7_parent_mutation": hostile_hk7(),
    }

    checks = {
        "vendored_blobs_pinned": all(vend.values()),
        "parent_code_unchanged": fingerprint[0] == baseline[0],
        "stream_sha256_matches_freeze": stream_matches,
        "frozen_nd2_reproduced": totals["nd2"] == frozen["set_valued_census"]["nd2"] == 2100,
        "frozen_nd1_reproduced": totals["nd1"] == frozen["set_valued_census"]["nd1"],
        "nd2_nonempty": totals["nd2"] >= 1,
        "zero_soundness_violations": violations == 0,
        "truthful_32_of_32": good == 32,
        "null_beaten": (good == 32 and null_truthful <= 2),
        "hk1_detected": hk["HK1_drop_protocol_clause"]["detected"],
        "hk2_detected": hk["HK2_include_degenerate_nd2"]["detected"],
        "hk3_detected": hk["HK3_flip_mlp_t1"]["detected"],
        "hk4_detected": hk["HK4_complement_receipt"]["detected"],
        "hk7_detected": hk["HK7_parent_mutation"]["detected"],
    }

    result = {
        "schema": "GMI833KRealTrainedReceiptV1",
        "issue": 833,
        "section": "K. Capability theory upgrade",
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": list(FORBIDDEN_PROMOTIONS),
        "parent_file_blob_sha": PARENT_BLOB_SHA,
        "parent_code_fingerprint_before": baseline[0],
        "parent_code_unchanged": fingerprint[0] == baseline[0],
        "stream_sha256": stream_sha,
        "stream_sha256_matches_freeze": stream_matches,
        "set_valued_census": totals,
        "frozen_set_valued_census": frozen["set_valued_census"],
        "bridge_table_derived": table,
        "bridge_table_matches_freeze": r4.bridge_matches_freeze(table),
        "bridge_evidence": evidence,
        "real_systems": {
            "population": "SIGMA_REAL4",
            "systems": 32,
            "torch_version": measured_payload["torch_version"],
            "source_sha256": measured_payload["source_sha256_verified"],
            "protected_eval_items": measured_payload["protected_eval_items"],
            "solved_band": measured_payload["band"],
            "measured_solved_bits": measured_payload["measured_solved_bits"],
        },
        "soundness": {"inputs_checked": checked, "violations": violations},
        "truthfulness": {"truthful": good, "of": 32, "fails": fails},
        "null_random_commit": {"seeds": 200, "truthful_on_32": null_truthful, "requirement": "<= 2"},
        "hostiles": hk,
        "checks": checks,
        "verdict": "GREEN" if all(checks.values()) else "RED",
        "terminal": "CAPABILITY_PREDICTOR_VALIDATED_ON_REAL_TRAINED_SYSTEMS_AT_REGISTERED_SCOPE"
        if all(checks.values()) else "GMI_833_K_REAL_TRAINED_RED",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
