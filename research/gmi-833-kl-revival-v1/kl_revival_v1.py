"""Route A executor for gmi-833-kl-revival-v1 (issue #833, body rows K and L).

Row K: the set-valued bridge SB-L* on SIGMA_REAL4 -- census, real-system
soundness and truthfulness against REAL_RUNS_V4, positive controls, null,
hostiles, decision rule of FREEZE_V1.md 3.6.
Row L: posterior custody FFA-1P over POSTERIOR_SOURCES_V1.json (window 1,
FREEZE_V1.md 4.5-4.6) and POSTERIOR_SOURCES_V2_EXTENDED.json (window 2,
FREEZE_V1_AMENDMENT_1.md 4-5; the frozen record's six admitted entries
continued to the single replacement P07 under FREEZE_V1.md 4.6 clause 2,
disclosed as D4), each with a replay of the mechanical source
rule PS-1, the frozen predictions EP-1/2/3 (and the amendment's EP-4) scored on
REAL_RUNS_L4 / REAL_RUNS_L5, nulls, hostiles, both decision rules and the
combined two-window record.

Stdlib only, Python 3.8, exact Fraction arithmetic.  Never trains, never
fetches.  Run:  python3 -I -B kl_revival_v1.py [--out RESULT_V1.json]
              [--sources-dir DIR] [--sources-dir-2 DIR] [--null-seeds 200]
"""

from fractions import Fraction
import argparse
import datetime
import glob
import hashlib
import itertools
import json
import os
import random
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import heldout_universes_real4_v1 as r4  # noqa: E402
import freeze_predictions_real4_v1 as fp  # noqa: E402

hu = r4.hu
UNSAT = "UNSATISFIED"
FREEZE_COMMIT = r4.FREEZE_COMMIT
SOURCE_MAIN = "f1e150ea89d1e3422d5ab18ec9a61d36ff17c3e5"
CLAIM_CEILING = fp.CLAIM_CEILING
PKG = "research/gmi-833-kl-revival-v1"
AMENDMENT_1_COMMIT = "65d0025765fef14d423d4e98e0194d23922c0b3d"
PROCEDURE_NULL = Fraction(1, 64) + Fraction(6, 64) * Fraction(1, 64)
WINDOWS = (
    {"id": "W1", "record": "POSTERIOR_SOURCES_V1.json", "runs": "REAL_RUNS_L4", "prefix": "cl4",
     "pos_base": 21, "neg_base": 31, "anchor_commit": FREEZE_COMMIT, "rule": "FREEZE_V1.md 4.5-4.6"},
    {"id": "W2", "record": "POSTERIOR_SOURCES_V2_EXTENDED.json", "runs": "REAL_RUNS_L5", "prefix": "cl5",
     "pos_base": 41, "neg_base": 51, "anchor_commit": AMENDMENT_1_COMMIT, "rule": "FREEZE_V1_AMENDMENT_1.md 4-5"},
)
GUARD_SECONDS = 60
NULL_FULL_TRUTHFUL_MAX = 2
MIN_SOURCES = 6
PS1_MIN_NEWLEN = 2000
PS1_MIN_BYTES = 410
PILOT_GRID = (60, 90, 120, 180, 240, 360, 540)
PILOT_LO = Fraction(9, 24)
PILOT_HI = Fraction(21, 24)
N_PROP = 24
STAGE_FILES = (
    ("freeze", "FREEZE_V1.md"),
    ("K_predictions", "FROZEN_PREDICTIONS_REAL4_V1.json"),
    ("K_receipt", "REAL_RUNS_V4/REAL_MEASURED_V4.json"),
    ("L_record", "POSTERIOR_SOURCES_V1.json"),
    ("L_receipt", "REAL_RUNS_L4/cl4_T21.json"),
    ("amendment_1", "FREEZE_V1_AMENDMENT_1.md"),
    ("L2_record", "POSTERIOR_SOURCES_V2.json"),
    ("L2_receipt", "REAL_RUNS_L5/cl5_T41.json"),
    ("L2_extended_record", "POSTERIOR_SOURCES_V2_EXTENDED.json"),
    ("L2_extended_receipt", "REAL_RUNS_L5/cl5_T47.json"),
)
PARENT_LANE_CANDIDATES = (
    "research/gmi-833-developmental-reuse-v1/FROZEN_FIXTURES_V1.json",
    "research/gmi-833-developmental-reuse-v1/DEVELOPMENTAL_REUSE_THEOREMS_V1.md",
    "research/gmi-833-real-developmental-validation-v1/REAL_SOURCE_PREFIXES_V1.json",
    "research/gmi-833-real-developmental-validation-v1/REAL_VALIDATION_THEOREMS_V1.md",
    "research/gmi-833-capability-predictor-evaluation-v1/heldout_universes_v3.py",
)
DISCLOSURES = (
    {"id": "D1", "materiality": "LOW",
     "what": "fetch_posterior_sources_v1.py (commit 2a) carried a personal e-mail address in "
             "its User-Agent constant; the fetch was run through run_fetch_v1.py, which imports "
             "the committed fetcher unchanged and replaces only the contact by the repository URL.",
     "effect": "no rule, admission test or recorded field changed; POSTERIOR_SOURCES_V1.json "
               "records the header actually sent."},
    {"id": "D2", "materiality": "LOW",
     "what": "FREEZE_V1.md 7 lists commit 2 (both rows' frozen material) before commit 3 (both "
             "rows' receipts); the chain was executed per row: 2a (K predictions) -> 3a (K "
             "receipt) -> 2b (L source record) -> 3b (L receipts).",
     "effect": "each row's frozen material still precedes that row's training receipt by "
               "committer time; the K receipt precedes the L record.  check_freeze_order_v1.py "
               "asserts the per-row order and records the interleaving.  The K and L "
               "instruments share no input, so neither receipt can inform the other's freeze."},
    {"id": "D3", "materiality": "LOW",
     "what": "window 2's single-pass T_fetch was chosen by polling only the COUNT of mainspace "
             "page creations with newlen >= 2000 since rcstart (no titles, ids or bytes were read "
             "before the registered fetch) and running the fetch once that count reached >= 8.",
     "effect": "T_fetch depends on the creation rate, not on any candidate's content or on any "
               "outcome; PS-1's admission order and test are unchanged and replayed by both routes."},
    {"id": "D4", "materiality": "LOW",
     "what": "window 2's sixth admitted source P06 was AT_FLOOR_OR_CEILING under PR-1 "
             "(REAL_RUNS_L5/pilot_T46.json: no grid budget with p0 in [9/24, 21/24]), so FREEZE_V1.md "
             "4.6 clause 2 excluded it by name and replaced it with the next admitted candidate P07 "
             "(revision 1375698478, created 2026-09-19T12:49:31Z). The registered window-2 fetch was a "
             "single pass; the replacement required continuing the same ordered list, so the committed "
             "fetcher PS-1 was re-run once from the same rcstart (12:26:23Z) with --k 12 at a later "
             "single T_fetch (2026-09-20T18:59:19Z). The continuation record "
             "POSTERIOR_SOURCES_V2_EXTENDED.json carries the frozen record's six admitted entries "
             "byte-identically as its first six, then P07; sources P08-P12 are recorded as unused and "
             "no receipt exists for them.",
     "effect": "the replacement is mechanical (the next admitted candidate in the same ordered list), "
               "posterior (12:49:31Z > amendment + 60 s) and attested (Wikimedia sha1 equals the sha1 "
               "of the scored bytes); the frozen POSTERIOR_SOURCES_V2.json is never edited; the "
               "exclusion count is reported in the receipts and both routes replay the continuation."},
)


def repo_root():
    return os.path.dirname(os.path.dirname(HERE))


def run_git(args, cwd=None):
    proc = subprocess.run(["git"] + list(args), cwd=cwd or repo_root(),
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return (proc.returncode, proc.stdout.decode("utf-8", "replace"),
            proc.stderr.decode("utf-8", "replace"))


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def git_blob_sha(data):
    return hashlib.sha1(("blob %d\0" % len(data)).encode("ascii") + data).hexdigest()


# ==========================================================================
# Row K
# ==========================================================================


def load_receipt_v4(path=None):
    path = path or os.path.join(HERE, "REAL_RUNS_V4", "REAL_MEASURED_V4.json")
    if not os.path.exists(path):
        return None
    with open(path) as handle:
        return json.load(handle)


def measured_bits_from_receipt(receipt, machines):
    table = receipt["measured_solved_bits"]
    return tuple(int(table[r4.machine_key(m)]) for m in machines)


def input_structure(parent):
    """Per registered input: (survivors, admissible, refused, contract).  World
    independent: survivor_mask never reads CAP."""
    n = parent.N
    full = (1 << n) - 1
    rows = []
    for entry in parent.main_grid():
        (k_index, r_value, d_value, b_value, h_value,
         _u_id, _u_kind, u_mask, _alpha, contract, _tau) = entry
        survivors = parent.survivor_mask(k_index, d_value, b_value, h_value, u_mask)
        if survivors == 0:
            rows.append((0, 0, 0, contract))
            continue
        res = parent.RES_MASKS[r_value]
        rows.append((survivors, survivors & res, survivors & ~res & full, contract))
    return rows


def bitmap_of_table(table, machines):
    return dict((r4.machine_key(m), r4.admissible_bits(table, m)) for m in machines)


def proto_bitmap(machines):
    return dict((r4.machine_key(m), r4.proto_admissible_bits(m)) for m in machines)


def images(parent, structure, bitmap, machines, mu):
    """Per input: None (inconsistent) or (I(x), I_PROTO(x)) under `bitmap`."""
    sets = {}
    proto = {}
    for contract in parent.CONTRACTS:
        verified = hu.VERIFIED[contract]
        sets[contract] = [r4.value_set(mu, verified, bitmap[r4.machine_key(m)]) for m in machines]
        proto[contract] = [r4.value_set(mu, verified, r4.proto_admissible_bits(m)) for m in machines]
    out = []
    for survivors, admissible, refused, contract in structure:
        if survivors == 0:
            out.append(None)
            continue
        image = set()
        ref = set()
        if refused:
            image.add(UNSAT)
            ref.add(UNSAT)
        for i in parent.bits_of(admissible):
            image |= sets[contract][i]
            ref |= proto[contract][i]
        out.append((frozenset(image), frozenset(ref)))
    return out


def has_positive(image):
    return any(v != UNSAT and v > 0 for v in image)


def is_nd1(image, ref):
    return (image < ref) and has_positive(image)


def is_nd2(image):
    if len(image) != 1:
        return False
    v = next(iter(image))
    return v != UNSAT and v > 0


def census_of(imgs, degenerate_is_point=False):
    out = {"inputs": 0, "inconsistent": 0, "point": 0, "set": 0, "nd1": 0, "nd2": 0,
           "point_degenerate": 0, "nd2_values": {}, "set_sizes": {}}
    for item in imgs:
        out["inputs"] += 1
        if item is None:
            out["inconsistent"] += 1
            continue
        image, ref = item
        if is_nd1(image, ref):
            out["nd1"] += 1
        if len(image) == 1:
            out["point"] += 1
            if is_nd2(image):
                out["nd2"] += 1
                v = str(next(iter(image)))
                out["nd2_values"][v] = out["nd2_values"].get(v, 0) + 1
            else:
                out["point_degenerate"] += 1
                if degenerate_is_point:
                    out["nd2"] += 1
        else:
            out["set"] += 1
            key = str(len(image))
            out["set_sizes"][key] = out["set_sizes"].get(key, 0) + 1
    return out


def stream_text(imgs, drop_at=None):
    """The frozen stream format of freeze_predictions_real4_v1 (route A's
    per-input record).  `drop_at` = (input index, value) removes one value from
    that input's I(x) -- the HK5 mutation."""
    lines = []
    for idx, item in enumerate(imgs):
        if item is None:
            lines.append("%d\tINCONSISTENT_REGISTERED_ASSUMPTIONS\t\t\t0\t0" % idx)
            continue
        image, ref = item
        if drop_at is not None and drop_at[0] == idx:
            image = frozenset(v for v in image if v != drop_at[1])
        disp = "IDENTIFIED" if len(image) == 1 else "CANNOT_IDENTIFY"
        lines.append("%d\t%s\t%s\t%s\t%d\t%d" % (idx, disp, fp.image_str(image), fp.image_str(ref),
                                                  int(is_nd1(image, ref)), int(is_nd2(image))))
    return "\n".join(lines) + "\n"


def extcap(i, refused, bits, contract, mu):
    if (refused >> i) & 1:
        return UNSAT
    return r4.cap_of_bits(mu, hu.VERIFIED[contract], bits)


def soundness(parent, structure, imgs, real_bits, mu):
    """(input, survivor) pairs where the survivor's externally evaluated real
    capability lies outside the emitted set."""
    pairs = 0
    viol_pairs = 0
    viol_inputs = 0
    first = None
    for idx, (survivors, _adm, refused, contract) in enumerate(structure):
        if survivors == 0:
            continue
        image = imgs[idx][0]
        bad = False
        for i in parent.bits_of(survivors):
            pairs += 1
            v = extcap(i, refused, real_bits[i], contract, mu)
            if v not in image:
                viol_pairs += 1
                bad = True
                if first is None:
                    first = {"input": idx, "machine": i, "extcap": str(v),
                             "image": sorted(str(x) for x in image)}
        if bad:
            viol_inputs += 1
    return {"pairs": pairs, "violating_pairs": viol_pairs, "violating_inputs": viol_inputs,
            "first_violation": first}


def truthfulness(bitmap, machines, real_bits):
    out = []
    for i, m in enumerate(machines):
        adm = bitmap[r4.machine_key(m)]
        out.append({"machine": r4.machine_key(m), "measured_bits": real_bits[i],
                    "admissible_bits": list(adm), "truthful": real_bits[i] in adm})
    return out


def cell_class(m, j):
    mech, size, _w, h = m
    if not (h >> j) & 1:
        return "untrained"
    if j == 0:
        return "T0_trained"
    if mech == "MLP":
        return "MLP_T%d_trained" % j
    return "GRU_T%d_trained_size_%d" % (j, size)


def falsified_cells(table, machines, real_bits):
    out = {}
    for i, m in enumerate(machines):
        for j in range(3):
            iv = r4.band_interval(table, m, j)
            if len(iv) != 1:
                continue
            if ((real_bits[i] >> j) & 1) != iv[0]:
                out.setdefault(cell_class(m, j), []).append(r4.machine_key(m))
    return out


def null_random_commit(parent, structure, table, machines, mu, real_bits, seeds):
    cells = set(r4.committed_cells(table, machines))
    results = []
    for s in range(seeds):
        rng = random.Random(70707 + s)
        per = {}
        for i, m in enumerate(machines):
            ivs = []
            for j in range(3):
                ivs.append((rng.randrange(2),) if (i, j) in cells else (0, 1))
            bits = []
            for bands in itertools.product(*ivs):
                b = 0
                for j, bb in enumerate(bands):
                    if bb:
                        b |= 1 << j
                bits.append(b)
            per[r4.machine_key(m)] = tuple(sorted(bits))
        truthful = sum(1 for i, m in enumerate(machines) if real_bits[i] in per[r4.machine_key(m)])
        c = census_of(images(parent, structure, per, machines, mu))
        results.append({"truthful_machines": truthful, "nd2": c["nd2"], "nd1": c["nd1"]})
    full = sum(1 for r in results if r["truthful_machines"] == len(machines))
    hist = {}
    for r in results:
        hist[str(r["truthful_machines"])] = hist.get(str(r["truthful_machines"]), 0) + 1
    return {"seeds": seeds, "committed_cells": len(cells),
            "fully_truthful_seeds": full,
            "max_truthful_machines": max(r["truthful_machines"] for r in results),
            "truthful_histogram": hist,
            "nd2_min": min(r["nd2"] for r in results), "nd2_max": max(r["nd2"] for r in results),
            "requirement_full_truthful_max": NULL_FULL_TRUTHFUL_MAX,
            "beaten": full <= NULL_FULL_TRUTHFUL_MAX}


def verify_parent_blob(path):
    """The parent F's file must carry the pinned blob sha; anything else is refused."""
    with open(path, "rb") as handle:
        data = handle.read()
    sha = git_blob_sha(data)
    if sha != hu.PARENT_BLOB_SHA:
        raise ValueError("parent blob refused: %s != %s" % (sha, hu.PARENT_BLOB_SHA))
    return sha


def hostile_hk6():
    """Run the freeze-order gate normally (must pass) and with its negative
    control neutralised (must fail).  Exit 2 = history unreachable."""
    gate = os.path.join(HERE, "check_freeze_order_v1.py")
    normal = subprocess.run([sys.executable, "-I", "-B", gate, repo_root()],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    typo = subprocess.run([sys.executable, "-I", "-B", gate, repo_root(), "--hostile-typo"],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    reachable = normal.returncode != 2
    return {"normal_exit": normal.returncode, "hostile_exit": typo.returncode,
            "detected": reachable and normal.returncode == 0 and typo.returncode == 1,
            "applicable": reachable,
            "state": "OK" if reachable else "UNREACHABLE",
            "note": "the gate with its wrong-path control replaced by a real file must fail"}


def row_k(null_seeds):
    table, evidence = r4.derive_bridge()
    out = {"bridge": {"derived": table, "matches_freeze": r4.bridge_matches_freeze(table),
                      "evidence": evidence}}
    if not out["bridge"]["matches_freeze"]:
        out["status"] = "BRIDGE_DERIVATION_DIFFERS_FROM_FREEZE"
        out["decision"] = {"closes_pending_route_b": False,
                           "attribution": {"stage": "commitment_rule",
                                           "note": "CR-1 no longer derives the frozen table"}}
        return out
    parent = hu.load_parent()
    out["parent_file_blob_sha"] = verify_parent_blob(hu.PARENT_FILE)
    baseline = hu.code_fingerprint(parent)
    spec = r4.sigma_real4(table)
    fingerprint = hu.install_universe(parent, r4.clean_spec(spec))
    out["parent_code_unchanged"] = fingerprint[0] == baseline[0]
    machines = r4.REAL4_MACHINES
    mu = hu.MU_REAL

    # Frozen stream: the committing module's sweep and this module's independent
    # image computation must both reproduce the frozen sha.
    totals, stream = fp.set_valued_sweep(parent, table, machines, mu)
    stream_sha = sha256_bytes(stream.encode("utf-8"))
    with open(os.path.join(HERE, "FROZEN_PREDICTIONS_REAL4_V1.json")) as handle:
        frozen = json.load(handle)
    structure = input_structure(parent)
    sb_bitmap = bitmap_of_table(table, machines)
    imgs = images(parent, structure, sb_bitmap, machines, mu)
    my_stream = stream_text(imgs)
    my_sha = sha256_bytes(my_stream.encode("utf-8"))
    out["frozen_stream"] = {"recomputed_sha256": stream_sha,
                            "executor_sha256": my_sha,
                            "frozen_sha256": frozen["stream_sha256"],
                            "reproduced": stream_sha == frozen["stream_sha256"] == my_sha,
                            "frozen_census": frozen["set_valued_census"],
                            "census_reproduced": totals == frozen["set_valued_census"]}
    census = census_of(imgs)
    out["census"] = census
    out["census_matches_frozen"] = census == frozen["set_valued_census"]
    out["resolved_machines"] = sum(1 for m in machines if len(sb_bitmap[r4.machine_key(m)]) == 1)
    out["committed_cells"] = len(r4.committed_cells(table, machines))

    # Positive controls on the prediction side.
    import heldout_universes_v3 as hv3
    v3_bitmap = dict((r4.machine_key(m), (hv3.real3_solved_law(m),)) for m in machines)
    v3_imgs = images(parent, structure, v3_bitmap, machines, mu)
    v3_census = census_of(v3_imgs)
    proto = proto_bitmap(machines)
    proto_imgs = images(parent, structure, proto, machines, mu)
    proto_census = census_of(proto_imgs)
    out["positive_controls"] = {
        "PK1_v3_point_law": {"nd2": v3_census["nd2"], "nd1": v3_census["nd1"],
                             "exceeds_sb": v3_census["nd2"] > census["nd2"]},
        "PK2_cb_proto": {"nd2": proto_census["nd2"], "nd1": proto_census["nd1"],
                         "both_zero": proto_census["nd2"] == 0 and proto_census["nd1"] == 0},
    }

    receipt = load_receipt_v4()
    if receipt is None:
        out["status"] = "RECEIPT_V4_UNAVAILABLE"
        out["decision"] = {"closes_pending_route_b": False,
                           "attribution": {"stage": "custody", "note": "no SIGMA_REAL4 receipt"}}
        return out
    real_bits = measured_bits_from_receipt(receipt, machines)
    out["receipt"] = {"schema": receipt.get("schema"), "torch_version": receipt.get("torch_version"),
                      "source_sha256_verified": receipt.get("source_sha256_verified"),
                      "band": receipt.get("band"), "freeze_commit": receipt.get("freeze_commit"),
                      "measured_solved_bits": receipt["measured_solved_bits"],
                      "untrained_heads_below_band": all(
                          Fraction(a["untrained"]) < r4.BAND
                          for a in receipt["per_head_exact_accuracy"].values()),
                      "max_untrained_accuracy": str(max(
                          Fraction(a["untrained"]) for a in receipt["per_head_exact_accuracy"].values()))}
    tr = truthfulness(sb_bitmap, machines, real_bits)
    n_truthful = sum(1 for t in tr if t["truthful"])
    out["truthfulness"] = {"machines": len(machines), "truthful": n_truthful,
                           "per_machine": tr,
                           "falsified_cells": falsified_cells(table, machines, real_bits)}
    snd = soundness(parent, structure, imgs, real_bits, mu)
    out["soundness"] = snd
    out["positive_controls"]["PK1_v3_point_law"]["truthful_machines"] = sum(
        1 for i, m in enumerate(machines) if real_bits[i] in v3_bitmap[r4.machine_key(m)])
    out["positive_controls"]["PK1_v3_point_law"]["soundness"] = soundness(
        parent, structure, v3_imgs, real_bits, mu)
    out["positive_controls"]["PK2_cb_proto"]["truthful_machines"] = sum(
        1 for i, m in enumerate(machines) if real_bits[i] in proto[r4.machine_key(m)])
    out["null"] = {"NULL_RANDOM_COMMIT": null_random_commit(parent, structure, table, machines,
                                                            mu, real_bits, null_seeds)}

    hostiles = {}
    # HK1: drop the protocol clause -> untrained heads free.
    t1 = dict(table)
    t1["untrained"] = "ABSTAIN"
    c1 = census_of(images(parent, structure, bitmap_of_table(t1, machines), machines, mu))
    hostiles["HK1_drop_protocol_clause"] = {
        "nd1": c1["nd1"], "nd2": c1["nd2"],
        "detected": c1["nd1"] < census["nd1"] and c1["nd2"] < census["nd2"], "applicable": True}
    # HK2: count degenerate points as ND-2.
    c2 = census_of(imgs, degenerate_is_point=True)
    hostiles["HK2_degenerate_counted"] = {"nd2": c2["nd2"], "detected": c2["nd2"] > census["nd2"],
                                          "applicable": census["point_degenerate"] > 0}
    # HK3: flip the MLP T1 commitment to SOLVED.
    t3 = dict(table)
    t3["MLP_T1_trained"] = "SOLVED"
    applicable3 = any(m[0] == "MLP" and (m[3] & 2) and not ((real_bits[i] >> 1) & 1)
                      for i, m in enumerate(machines))
    tr3 = truthfulness(bitmap_of_table(t3, machines), machines, real_bits)
    hostiles["HK3_planted_false_commitment"] = {
        "truthful": sum(1 for t in tr3 if t["truthful"]),
        "flagged": sum(1 for t in tr3 if not t["truthful"]),
        "detected": sum(1 for t in tr3 if not t["truthful"]) >= 1,
        "applicable": applicable3,
        "note": "applicable iff some MLP machine with head 1 trained measured UNSOLVED"}
    # HK4: complement one machine's measured bits -- the first machine (by
    # index) that is an admissible survivor at some ND-1 input.
    nd1_inputs = [idx for idx, item in enumerate(imgs) if item is not None and is_nd1(*item)]
    target = None
    for i in range(len(machines)):
        if any((structure[idx][1] >> i) & 1 for idx in nd1_inputs):
            target = i
            break
    if target is None:
        hostiles["HK4_receipt_mutation"] = {"detected": False, "applicable": False,
                                            "note": "no machine is an admissible survivor at an ND-1 input"}
    else:
        mutated = list(real_bits)
        mutated[target] = (~mutated[target]) & 7
        s4 = soundness(parent, structure, imgs, tuple(mutated), mu)
        hostiles["HK4_receipt_mutation"] = {
            "machine": r4.machine_key(machines[target]), "violating_pairs": s4["violating_pairs"],
            "violating_inputs": s4["violating_inputs"],
            "detected": s4["violating_pairs"] > snd["violating_pairs"], "applicable": True}
    # HK5: one value dropped from route A's I(x) at one input.  Route B decides
    # (its per-input stream must disagree with the mutated stream while agreeing
    # with the true one); route A only publishes the mutated stream's sha.
    set_inputs = [idx for idx, item in enumerate(imgs) if item is not None and len(item[0]) > 1]
    if set_inputs:
        idx = set_inputs[0]
        dropped = sorted(imgs[idx][0], key=fp.value_key)[0]
        hk5_sha = sha256_bytes(stream_text(imgs, drop_at=(idx, dropped)).encode("utf-8"))
        hostiles["HK5_route_disagreement"] = {
            "input": idx, "dropped_value": str(dropped), "mutated_stream_sha256": hk5_sha,
            "true_stream_sha256": my_sha, "mutation_changes_stream": hk5_sha != my_sha,
            "detected": None, "decided_by": "route B", "applicable": True}
    else:
        hostiles["HK5_route_disagreement"] = {"detected": False, "applicable": False}
    # HK6: the freeze-order gate with its negative control neutralised.
    hostiles["HK6_gate_typo"] = hostile_hk6()
    # HK7: a mutated parent blob must be refused by the same check the real one passes.
    with open(hu.PARENT_FILE, "rb") as handle:
        pdata = handle.read()
    fd, tmp = tempfile.mkstemp(suffix=".py")
    os.close(fd)
    try:
        with open(tmp, "wb") as handle:
            handle.write(pdata + b"\n# mutated\n")
        try:
            verify_parent_blob(tmp)
            refused = False
        except ValueError:
            refused = True
    finally:
        os.unlink(tmp)
    hostiles["HK7_parent_blob_mutation"] = {"true_blob": hu.PARENT_BLOB_SHA,
                                            "mutated_blob": git_blob_sha(pdata + b"\n# mutated\n"),
                                            "detected": refused, "applicable": True}
    out["hostiles"] = hostiles

    def hostile_ok(name, h):
        if h["detected"] is None:
            return True  # decided by route B (HK5)
        if h["detected"]:
            return True
        return (not h["applicable"]) and name.startswith("HK3")

    clauses = {
        "1_nd2_at_least_1": census["nd2"] >= 1,
        "2_zero_violations": snd["violating_pairs"] == 0,
        "3_truthful_32_of_32": n_truthful == len(machines),
        "5_null_beaten": out["null"]["NULL_RANDOM_COMMIT"]["beaten"],
        "controls": (out["positive_controls"]["PK1_v3_point_law"]["exceeds_sb"]
                     and out["positive_controls"]["PK2_cb_proto"]["both_zero"]),
        "frozen_stream_reproduced": out["frozen_stream"]["reproduced"] and out["census_matches_frozen"],
        "parent_unchanged": out["parent_code_unchanged"],
        "hostiles_detected_or_inapplicable_by_result": all(hostile_ok(k, h) for k, h in hostiles.items()),
    }
    closes = all(clauses.values())
    attribution = None
    if not closes:
        if not clauses["3_truthful_32_of_32"] or not clauses["2_zero_violations"]:
            attribution = {"stage": "commitment_rule",
                           "falsified_cells": out["truthfulness"]["falsified_cells"]}
        elif not clauses["1_nd2_at_least_1"]:
            attribution = {"stage": "population_design"}
        elif not clauses["controls"] or not clauses["hostiles_detected_or_inapplicable_by_result"]:
            attribution = {"stage": "counter"}
        else:
            attribution = {"stage": "custody_or_routes"}
    out["decision"] = {"clauses": clauses, "closes_pending_route_b": closes,
                       "attribution": attribution}
    out["status"] = "OK"
    return out


# ==========================================================================
# Row L
# ==========================================================================


def parse_iso(s):
    s = s.strip().replace("Z", "+00:00")
    if len(s) >= 6 and s[-3] == ":" and s[-6] in "+-":
        s = s[:-3] + s[-2:]
    try:
        t = datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S%z")
    except ValueError:
        t = datetime.datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S").replace(
            tzinfo=datetime.timezone.utc)
    return t.astimezone(datetime.timezone.utc)


def iso_utc(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def freeze_time(commit=FREEZE_COMMIT):
    rc, out, _err = run_git(["show", "-s", "--format=%cI", commit])
    if rc != 0 or not out.strip():
        return None
    return parse_iso(out.strip())


def blobs_at(commit):
    """{git blob sha: path} for every tracked path at commit (None if unreachable)."""
    rc, out, _err = run_git(["ls-tree", "-r", commit])
    if rc != 0:
        return None
    table = {}
    for line in out.splitlines():
        if not line.strip():
            continue
        meta, path = line.split("\t", 1)
        table[meta.split()[2]] = path
    return table


def sha256_of_blobs(shas):
    proc = subprocess.run(["git", "cat-file", "--batch"], cwd=repo_root(),
                          input="\n".join(shas).encode("ascii") + b"\n",
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    data = proc.stdout
    out = {}
    pos = 0
    for sha in shas:
        nl = data.index(b"\n", pos)
        parts = data[pos:nl].decode("ascii").split()
        if len(parts) < 3:
            pos = nl + 1
            continue
        size = int(parts[2])
        out[sha] = sha256_bytes(data[nl + 1:nl + 1 + size])
        pos = nl + 1 + size + 1
    return out


def blob_object_exists(sha):
    rc, _o, _e = run_git(["cat-file", "-e", sha])
    return rc == 0


class Custody(object):
    """FFA-1P, decided from the committed record's fields (reproducible on any
    host); byte re-verification is a separate, stronger check run where the
    off-repository bytes are available."""

    def __init__(self, freeze_commit=FREEZE_COMMIT):
        self.freeze_commit = freeze_commit
        self.t_freeze = freeze_time(freeze_commit)
        self.blobs = blobs_at(freeze_commit)
        self._sha256 = None

    def freeze_blob_sha256s(self):
        if self._sha256 is None and self.blobs is not None:
            self._sha256 = set(sha256_of_blobs(sorted(self.blobs)).values())
        return self._sha256

    def check(self, cand):
        """cand: creation_timestamp, wikimedia_sha1, sha1_of_bytes, sha256,
        authored_by_programme (bool), selected_by_rule (bool)."""
        v = {"clauses": {}, "admissible": False, "state": "OK"}
        ts = cand.get("creation_timestamp")
        v["clauses"]["1_dated"] = bool(ts) and bool(cand.get("wikimedia_sha1"))
        if self.t_freeze is None:
            v["clauses"]["2_posterior"] = None
            v["state"] = "FREEZE_COMMIT_UNREACHABLE"
        elif ts:
            v["clauses"]["2_posterior"] = (parse_iso(ts) >
                                           self.t_freeze + datetime.timedelta(seconds=GUARD_SECONDS))
        else:
            v["clauses"]["2_posterior"] = False
        not_ours = (not cand.get("authored_by_programme", False)) and bool(cand.get("selected_by_rule", False))
        if self.blobs is None:
            v["clauses"]["3_exogenous"] = None
            v["state"] = "FREEZE_COMMIT_UNREACHABLE"
        else:
            blob_free = cand.get("sha256") not in self.freeze_blob_sha256s()
            v["clauses"]["3_exogenous"] = not_ours and blob_free
        att = cand.get("wikimedia_sha1")
        mine = cand.get("sha1_of_bytes")
        v["clauses"]["4_attested"] = bool(att) and bool(mine) and att == mine
        v["admissible"] = all(v["clauses"].get(k) is True for k in
                              ("1_dated", "2_posterior", "3_exogenous", "4_attested"))
        return v

    def reverify_bytes(self, cand, path):
        """Where the off-repository bytes exist: the record's hashes must be the
        hashes of the bytes, and the bytes' git blob object must be absent from
        the whole repository object store (hence from every commit)."""
        if not path or not os.path.exists(path):
            return {"bytes_available": False}
        with open(path, "rb") as handle:
            data = handle.read()
        bsha = git_blob_sha(data)
        out = {"bytes_available": True, "bytes": len(data),
               "sha256_matches_record": sha256_bytes(data) == cand.get("sha256"),
               "sha1_matches_outside_record": hashlib.sha1(data).hexdigest() == cand.get("wikimedia_sha1"),
               "length_matches_record": len(data) == cand.get("bytes"),
               "prefix80_matches_record": data[:80].hex() == cand.get("prefix80_hex"),
               "git_blob_sha": bsha,
               "blob_absent_from_freeze_tree": (self.blobs is not None) and (bsha not in self.blobs),
               "blob_object_absent_from_repository": not blob_object_exists(bsha)}
        out["consistent"] = all(out[k] for k in ("sha256_matches_record", "sha1_matches_outside_record",
                                                 "length_matches_record", "prefix80_matches_record",
                                                 "blob_absent_from_freeze_tree",
                                                 "blob_object_absent_from_repository"))
        return out


def validate_custody_checker(cust):
    """Recall on a planted admissible candidate; no-alarm on HL1-HL3 and on the
    parent lane's six rejected candidates."""
    fixtures = {}
    posterior_ts = iso_utc(cust.t_freeze + datetime.timedelta(seconds=3600)) \
        if cust.t_freeze else "2099-01-01T00:00:00Z"
    planted_bytes = b"planted admissible candidate bytes " + posterior_ts.encode("ascii")
    planted = {"creation_timestamp": posterior_ts,
               "wikimedia_sha1": hashlib.sha1(planted_bytes).hexdigest(),
               "sha1_of_bytes": hashlib.sha1(planted_bytes).hexdigest(),
               "sha256": sha256_bytes(planted_bytes), "bytes": len(planted_bytes),
               "authored_by_programme": False, "selected_by_rule": True}
    fixtures["PLANTED_ADMISSIBLE"] = {"verdict": cust.check(planted), "expected": True}
    hl1 = dict(planted)
    hl1["creation_timestamp"] = "2026-09-18T00:00:00Z"
    fixtures["HL1_pre_freeze_timestamp"] = {"verdict": cust.check(hl1), "expected": False,
                                            "expected_failing_clause": "2_posterior"}
    hl1b = dict(planted)
    hl1b["creation_timestamp"] = iso_utc(cust.t_freeze + datetime.timedelta(seconds=30)) \
        if cust.t_freeze else "2026-09-18T00:00:00Z"
    fixtures["HL1b_inside_guard"] = {"verdict": cust.check(hl1b), "expected": False,
                                     "expected_failing_clause": "2_posterior"}
    with open(os.path.join(HERE, "FREEZE_V1.md"), "rb") as handle:
        fdata = handle.read()
    hl2 = dict(planted)
    hl2["sha256"] = sha256_bytes(fdata)
    hl2["sha1_of_bytes"] = hashlib.sha1(fdata).hexdigest()
    hl2["wikimedia_sha1"] = hl2["sha1_of_bytes"]
    fixtures["HL2_repository_blob"] = {"verdict": cust.check(hl2), "expected": False,
                                       "expected_failing_clause": "3_exogenous"}
    hl3 = dict(planted)
    hl3["wikimedia_sha1"] = "0" * 40
    fixtures["HL3_outside_hash_mismatch"] = {"verdict": cust.check(hl3), "expected": False,
                                             "expected_failing_clause": "4_attested"}
    for path in PARENT_LANE_CANDIDATES:
        full = os.path.join(repo_root(), path)
        name = "PARENT_" + os.path.basename(path)
        if not os.path.exists(full):
            fixtures[name] = {"verdict": {"state": "MISSING", "admissible": None}, "expected": False}
            continue
        with open(full, "rb") as handle:
            d = handle.read()
        c = {"creation_timestamp": None, "wikimedia_sha1": None,
             "sha1_of_bytes": hashlib.sha1(d).hexdigest(), "sha256": sha256_bytes(d),
             "bytes": len(d), "authored_by_programme": True, "selected_by_rule": False}
        fixtures[name] = {"verdict": cust.check(c), "expected": False}
    insess = {"creation_timestamp": posterior_ts, "wikimedia_sha1": None, "sha1_of_bytes": "ab" * 20,
              "sha256": "cd" * 32, "bytes": 10, "authored_by_programme": True, "selected_by_rule": False}
    fixtures["PARENT_IN_SESSION_AUTHORED"] = {"verdict": cust.check(insess), "expected": False}
    ok = True
    for fx in fixtures.values():
        got = fx["verdict"].get("admissible", False)
        fx["agrees"] = (got is fx["expected"])
        if "expected_failing_clause" in fx:
            fx["agrees"] = fx["agrees"] and (fx["verdict"]["clauses"].get(fx["expected_failing_clause"]) is False)
        ok = ok and fx["agrees"]
    return {"fixtures": fixtures, "validated_both_directions": ok}


def replay_ps1(record, t_freeze):
    """Re-derive every recorded verdict from the recorded fields and check the
    admitted set is exactly the first k admissible candidates in creation order."""
    out = {"checks": {}}
    rcstart = record["rcstart"]
    out["checks"]["rcstart_is_freeze_plus_guard"] = (
        t_freeze is not None and rcstart == iso_utc(t_freeze + datetime.timedelta(seconds=GUARD_SECONDS)))
    cands = record["candidates"]
    keys = [(c["rc"]["timestamp"], c["rc"]["revid"]) for c in cands]
    out["checks"]["ascending_creation_order"] = keys == sorted(keys)
    replayed = []
    mismatches = []
    for c in cands:
        rc = c["rc"]
        rev = c.get("revision") or {}
        if (rc.get("newlen") or 0) < PS1_MIN_NEWLEN:
            v = "SKIPPED_NEWLEN_BELOW_%d" % PS1_MIN_NEWLEN
        elif rc["timestamp"] <= rcstart:
            v = "REJECTED_CLAUSE2_NOT_POSTERIOR"
        elif not rev:
            v = "REJECTED_CLAUSE1_REVISION_UNAVAILABLE"
        elif rev.get("parentid") not in (0, None):
            v = "REJECTED_NOT_A_CREATION_REVISION"
        elif rev.get("sha1") != c.get("sha1_of_bytes"):
            v = "REJECTED_CLAUSE4_OUTSIDE_HASH_MISMATCH"
        elif rev["timestamp"] <= rcstart:
            v = "REJECTED_CLAUSE2_NOT_POSTERIOR"
        elif (c.get("bytes") or 0) < PS1_MIN_BYTES:
            v = "REJECTED_TOO_SHORT"
        else:
            v = "ADMITTED"
        replayed.append(v)
        if v != c["verdict"]:
            mismatches.append({"revid": rc["revid"], "recorded": c["verdict"], "replayed": v})
    out["verdict_mismatches"] = mismatches
    out["checks"]["every_verdict_replayed"] = not mismatches
    admitted_c = [c for c in cands if c["verdict"] == "ADMITTED"]
    adm = record["admitted"]
    out["checks"]["admitted_are_the_admitted_candidates_in_order"] = (
        [(c["revision"]["revid"], c["sha256_of_bytes"]) for c in admitted_c]
        == [(a["revid"], a["sha256"]) for a in adm])
    out["checks"]["k_admitted_consistent"] = (len(adm) == record["k_admitted"] == len(admitted_c)
                                              and len(adm) <= record["k_requested"])
    out["checks"]["stopped_at_k"] = (len(adm) < record["k_requested"]
                                     or (cands and cands[-1]["verdict"] == "ADMITTED"))
    out["checks"]["no_candidate_skipped_by_choice"] = all(
        c["verdict"] == "ADMITTED" or c["verdict"].startswith("SKIPPED_NEWLEN") or c["verdict"].startswith("REJECTED_")
        for c in cands)
    out["checks"]["fetch_after_freeze"] = (t_freeze is not None
                                           and parse_iso(record["T_fetch_utc"]) > t_freeze)
    out["checks"]["freeze_time_in_record_matches_git"] = (
        t_freeze is not None and record["freeze_committer_time_utc"] == iso_utc(t_freeze))
    out["replayed"] = replayed
    out["ok"] = all(out["checks"].values())
    return out


def load_posterior_record(name):
    path = os.path.join(HERE, name)
    if not os.path.exists(path):
        return None
    with open(path) as handle:
        return json.load(handle)


def load_l_receipts(runs_dir, prefix):
    out = {}
    for path in sorted(glob.glob(os.path.join(HERE, runs_dir, prefix + "_T*.json"))):
        with open(path) as handle:
            rec = json.load(handle)
        out[rec["sequence_id"]] = rec
    pilots = {}
    for path in sorted(glob.glob(os.path.join(HERE, runs_dir, "pilot_T*.json"))):
        with open(path) as handle:
            rec = json.load(handle)
        pilots[rec["sequence_id"]] = rec
    return out, pilots


def replay_pr1(pilot):
    """PR-1: smallest grid budget with p0 in [9/24, 21/24], baseline law only."""
    grid = pilot["pilot_grid"]
    chosen = None
    for b in PILOT_GRID:
        h = grid.get(str(b))
        if h is None:
            return {"ok": False, "reason": "grid budget %d missing" % b}
        if chosen is None and PILOT_LO <= Fraction(h, N_PROP) <= PILOT_HI:
            chosen = b
    return {"ok": chosen == pilot["B_prop"] and (pilot["status"] == ("OK" if chosen else "AT_FLOOR_OR_CEILING")),
            "replayed_B_prop": chosen, "recorded_B_prop": pilot["B_prop"]}


def count_hits(scores, crit):
    return sum(1 for x in scores if x >= crit)


def score_sources(record, receipts, pilots, pos_base, neg_base):
    """EP-1/EP-2/EP-3/EP-4 per admitted source, from the raw score lists."""
    scored = []
    for n, src in enumerate(record["admitted"]):
        pos_id = "T%02d" % (pos_base + n)
        neg_id = "T%02d" % (neg_base + n)
        pil = pilots.get(pos_id)
        entry = {"source_id": src["source_id"], "revid": src["revid"], "pos": pos_id, "neg": neg_id,
                 "pilot": None if pil is None else {"grid": pil["pilot_grid"], "B_prop": pil["B_prop"],
                                                    "status": pil["status"],
                                                    "PR1_replay": replay_pr1(pil)}}
        if pil is None or pil.get("B_prop") is None:
            entry["status"] = "AT_FLOOR_OR_CEILING" if pil is not None else "NO_PILOT"
            scored.append(entry)
            continue
        p = receipts.get(pos_id)
        q = receipts.get(neg_id)
        if p is None or q is None:
            entry["status"] = "RECEIPT_MISSING"
            scored.append(entry)
            continue
        if p["source_sha256"] != src["sha256"] or q["source_sha256"] != src["sha256"]:
            entry["status"] = "RECEIPT_SOURCE_MISMATCH"
            scored.append(entry)
            continue
        if pil["source_sha256"] != src["sha256"] or p["c"] != pil["B_prop"] or q["c"] != pil["B_prop"]:
            entry["status"] = "PILOT_RECEIPT_MISMATCH"
            scored.append(entry)
            continue
        n_prop = p["N_prop"]
        crit_p, crit_q = p["criterion_correct"], q["criterion_correct"]
        pH_pos = Fraction(count_hits(p["scores_QH_B2"], crit_p), n_prop)
        pH_neg = Fraction(count_hits(q["scores_QH_B2"], crit_q), q["N_prop"])
        p0_pos = Fraction(count_hits(p["scores_Q0_B2"], crit_p), n_prop)
        p0_neg = Fraction(count_hits(q["scores_Q0_B2"], crit_q), q["N_prop"])
        cpot_pos = max(p["scores_QH_B2"])
        cpot_neg = max(q["scores_QH_B2"])
        entry.update({
            "status": "SCORED",
            "receipt_counts_consistent": count_hits(p["scores_QH_B2"], crit_p) == p["successes_QH"]
            and count_hits(q["scores_QH_B2"], crit_q) == q["successes_QH"]
            and count_hits(p["scores_Q0_B2"], crit_p) == p["successes_Q0"]
            and count_hits(q["scores_Q0_B2"], crit_q) == q["successes_Q0"]
            and cpot_pos == p["C_pot_QH_B2"] and cpot_neg == q["C_pot_QH_B2"],
            "N_prop": n_prop, "criterion_correct": crit_p,
            "p0_pos": str(p0_pos), "pH_pos": str(pH_pos), "p0_neg": str(p0_neg), "pH_neg": str(pH_neg),
            "pH_pos_hits": count_hits(p["scores_QH_B2"], crit_p), "pH_neg_hits": count_hits(q["scores_QH_B2"], crit_q),
            "p0_pos_hits": count_hits(p["scores_Q0_B2"], crit_p),
            "Ev_Q_U_pos": str(pH_pos), "Ev_Q_U_neg": str(pH_neg),
            "C_pot_QH_pos": cpot_pos, "C_pot_QH_neg": cpot_neg,
            "EP1": pH_pos > pH_neg, "EP1_tie": pH_pos == pH_neg,
            "EP2": pH_neg == 0, "EP3": pH_pos > p0_pos, "EP4": cpot_pos > cpot_neg,
            "stored_solution_reaches_U_pos": p["stored_solution_reaches_U"],
            "stored_solution_reaches_U_neg": q["stored_solution_reaches_U"],
            "c": p["c"], "B1": p["B1"], "B2": p["B2"], "source_sha256": p["source_sha256"],
            "torch_version": p.get("torch_version"),
        })
        scored.append(entry)
    return scored


def binomial_tail(hits, n):
    """Exact P(X >= hits) for X ~ Binomial(n, 1/2)."""
    from math import comb
    return Fraction(sum(comb(n, j) for j in range(hits, n + 1)), 2 ** n)


def null_random_sign(k, seeds, need=None):
    """200 random sign assignments over k sources; count those with >= need hits
    (need = k, the registered k/k, unless given)."""
    need = k if need is None else need
    hits = 0
    for s in range(seeds):
        rng = random.Random(31337 + s)
        if sum(rng.randrange(2) for _ in range(k)) >= need:
            hits += 1
    bound = Fraction(seeds) * binomial_tail(need, k) + 5
    return {"seeds": seeds, "k": k, "need": need, "matches": hits, "bound": str(bound),
            "beaten": Fraction(hits) <= bound, "exact_null_probability": str(binomial_tail(need, k))}


def mutated_receipts(receipts, pos_id, neg_id, mode):
    """HL4: swap the POS and NEG history score lists; HL5: make NEG's equal POS's."""
    out = dict(receipts)
    p = dict(receipts[pos_id])
    q = dict(receipts[neg_id])
    if mode == "swap":
        p["scores_QH_B2"], q["scores_QH_B2"] = receipts[neg_id]["scores_QH_B2"], receipts[pos_id]["scores_QH_B2"]
        p["successes_QH"], q["successes_QH"] = receipts[neg_id]["successes_QH"], receipts[pos_id]["successes_QH"]
        p["C_pot_QH_B2"], q["C_pot_QH_B2"] = receipts[neg_id]["C_pot_QH_B2"], receipts[pos_id]["C_pot_QH_B2"]
    else:
        q["scores_QH_B2"] = list(receipts[pos_id]["scores_QH_B2"])
        q["successes_QH"] = receipts[pos_id]["successes_QH"]
        q["C_pot_QH_B2"] = receipts[pos_id]["C_pot_QH_B2"]
        q["criterion_correct"] = receipts[pos_id]["criterion_correct"]
    out[pos_id] = p
    out[neg_id] = q
    return out


def row_l_window(win, sources_dir, null_seeds, checker_validation):
    """One posterior window: custody, PS-1 replay, scores, hostiles, decision."""
    out = {"window": win["id"], "rule": win["rule"], "anchor_commit": win["anchor_commit"]}
    cust = Custody(win["anchor_commit"])
    out["anchor_committer_time_utc"] = None if cust.t_freeze is None else iso_utc(cust.t_freeze)
    out["anchor_reachable"] = cust.t_freeze is not None and cust.blobs is not None
    record = load_posterior_record(win["record"])
    if record is None:
        out["status"] = "POSTERIOR_RECORD_UNAVAILABLE"
        out["decision"] = {"closes_pending_route_b": False,
                           "attribution": {"stage": "custody_window",
                                           "note": "registered window awaiting posterior data"}}
        return out
    out["record"] = {"T_fetch_utc": record["T_fetch_utc"], "rcstart": record["rcstart"],
                     "k_requested": record["k_requested"], "k_admitted": record["k_admitted"],
                     "entries_scanned": record["recentchanges_entries_scanned"],
                     "entries_total": record["recentchanges_entries_total"],
                     "rule": record["rule"], "anchor_time_in_record": record["freeze_committer_time_utc"],
                     "user_agent": record["user_agent"]}
    out["ps1_replay"] = replay_ps1(record, cust.t_freeze)
    verdicts = []
    bytes_re = []
    for src in record["admitted"]:
        cand = dict(src)
        cand["authored_by_programme"] = False
        cand["selected_by_rule"] = out["ps1_replay"]["ok"]
        v = cust.check(cand)
        v["source_id"] = src["source_id"]
        v["revid"] = src["revid"]
        v["creation_timestamp"] = src["creation_timestamp"]
        v["wikimedia_sha1"] = src["wikimedia_sha1"]
        v["sha256"] = src["sha256"]
        v["bytes"] = src["bytes"]
        verdicts.append(v)
        path = os.path.join(sources_dir, os.path.basename(src["local_path"])) if sources_dir else None
        rv = cust.reverify_bytes(src, path)
        rv["source_id"] = src["source_id"]
        bytes_re.append(rv)
    n_adm = sum(1 for v in verdicts if v["admissible"])
    out["custody"] = {"verdicts": verdicts, "admissible": n_adm, "of": len(verdicts)}
    out["bytes_reverification"] = {"per_source": bytes_re,
                                   "bytes_available": all(b["bytes_available"] for b in bytes_re),
                                   "all_consistent": all(b.get("consistent", False) for b in bytes_re)}
    receipts, pilots = load_l_receipts(win["runs"], win["prefix"])
    scored = score_sources(record, receipts, pilots, win["pos_base"], win["neg_base"])
    out["scores"] = scored
    admissible_ids = set(v["source_id"] for v in verdicts if v["admissible"])
    scored_adm = [s for s in scored if s.get("status") == "SCORED" and s["source_id"] in admissible_ids]
    k = len(scored_adm)
    ep1 = sum(1 for s in scored_adm if s["EP1"])
    out["tally"] = {"scored_admissible_sources": k, "EP1_hits": ep1,
                    "EP1_misses": [s["source_id"] for s in scored_adm if not s["EP1"]],
                    "EP2_hits": sum(1 for s in scored_adm if s["EP2"]),
                    "EP3_hits": sum(1 for s in scored_adm if s["EP3"]),
                    "EP4_hits": sum(1 for s in scored_adm if s["EP4"]),
                    "EP4_misses": [s["source_id"] for s in scored_adm if not s["EP4"]],
                    "excluded_at_floor_or_ceiling": sum(1 for s in scored if s.get("status") == "AT_FLOOR_OR_CEILING"),
                    "pilot_replays_ok": all(s["pilot"]["PR1_replay"]["ok"] for s in scored if s.get("pilot")),
                    "receipt_counts_consistent": all(s["receipt_counts_consistent"] for s in scored_adm),
                    "exact_null_probability_k_of_k": str(Fraction(1, 2 ** k)) if k else None,
                    "exact_null_probability_observed_or_better": str(binomial_tail(ep1, k)) if k else None,
                    "pH_pos_hits": [s["pH_pos_hits"] for s in scored_adm], "pH_neg_hits": [s["pH_neg_hits"] for s in scored_adm],
                    "p0_pos_hits": [s["p0_pos_hits"] for s in scored_adm],
                    "C_pot_QH_pos": [s["C_pot_QH_pos"] for s in scored_adm], "C_pot_QH_neg": [s["C_pot_QH_neg"] for s in scored_adm],
                    "B_prop": [s["c"] for s in scored_adm]}
    out["null"] = {"NULL_LABEL_PERMUTATION": {"k": k, "probability_k_of_k": str(Fraction(1, 2 ** k)) if k else None},
                   "NULL_RANDOM_SIGN": null_random_sign(k, null_seeds) if k else None}

    hostiles = {}
    fx = checker_validation["fixtures"]
    for name in ("HL1_pre_freeze_timestamp", "HL2_repository_blob", "HL3_outside_hash_mismatch"):
        hostiles[name] = {"detected": fx[name]["agrees"], "applicable": True,
                          "failing_clause": fx[name]["expected_failing_clause"]}
    if scored_adm:
        s = scored_adm[0]
        sw = score_sources(record, mutated_receipts(receipts, s["pos"], s["neg"], "swap"), pilots,
                           win["pos_base"], win["neg_base"])
        sw = [x for x in sw if x["source_id"] == s["source_id"]][0]
        hostiles["HL4_swapped_receipt"] = {"source": s["source_id"], "EP1_true": s["EP1"],
                                           "EP1_after_swap": sw["EP1"], "EP4_after_swap": sw["EP4"],
                                           "detected": s["EP1"] and not sw["EP1"] and (not s["EP4"] or not sw["EP4"]),
                                           "applicable": s["EP1"]}
        tie = score_sources(record, mutated_receipts(receipts, s["pos"], s["neg"], "tie"), pilots,
                            win["pos_base"], win["neg_base"])
        tie = [x for x in tie if x["source_id"] == s["source_id"]][0]
        hostiles["HL5_tie_receipt"] = {"source": s["source_id"], "EP1_on_tie": tie["EP1"],
                                       "tie_flagged": tie["EP1_tie"], "EP4_on_tie": tie["EP4"],
                                       "detected": (not tie["EP1"]) and tie["EP1_tie"] and not tie["EP4"],
                                       "applicable": True}
    rc, head, _e = run_git(["rev-parse", "HEAD"])
    later = Custody(head.strip()) if rc == 0 else None
    if later is not None and later.t_freeze is not None and record["admitted"]:
        rejected = 0
        for src in record["admitted"]:
            c = dict(src)
            c["authored_by_programme"] = False
            c["selected_by_rule"] = True
            if later.check(c)["clauses"]["2_posterior"] is False:
                rejected += 1
        latest = max(parse_iso(s["creation_timestamp"]) for s in record["admitted"])
        applicable = (cust.t_freeze is not None and later.t_freeze > cust.t_freeze
                      and later.t_freeze + datetime.timedelta(seconds=GUARD_SECONDS) >= latest)
        hostiles["HL6_wrong_freeze_commit"] = {"later_commit": head.strip()[:12],
                                               "later_commit_time_utc": iso_utc(later.t_freeze),
                                               "rejected": rejected, "of": len(record["admitted"]),
                                               "detected": rejected == len(record["admitted"]),
                                               "applicable": applicable,
                                               "note": "applicable iff HEAD postdates the anchor and every source predates HEAD + guard"}
    out["hostiles"] = hostiles
    clauses = {
        "1_at_least_6_admissible": n_adm >= MIN_SOURCES,
        "checker_validated": checker_validation["validated_both_directions"],
        "ps1_replay_ok": out["ps1_replay"]["ok"],
        "2_pilot_interior_on_scored": (len(admissible_ids) > 0
                                       and all(s.get("status") in ("SCORED", "AT_FLOOR_OR_CEILING") for s in scored
                                               if s["source_id"] in admissible_ids)
                                       and out["tally"]["pilot_replays_ok"]
                                       and out["tally"]["receipt_counts_consistent"]
                                       and out["tally"]["scored_admissible_sources"] >= MIN_SOURCES),
        "3_EP1_k_of_k_with_k_at_least_6": k >= MIN_SOURCES and ep1 == k,
        "null_beaten": bool((out["null"]["NULL_RANDOM_SIGN"] or {}).get("beaten", False)),
        "hostiles_detected": bool(hostiles) and all(h["detected"] or not h["applicable"] for h in hostiles.values()),
        "bytes_reverification_consistent_where_available": (
            out["bytes_reverification"]["all_consistent"] if out["bytes_reverification"]["bytes_available"] else True),
    }
    closes = all(clauses.values())
    attribution = None
    if not closes:
        if k < MIN_SOURCES:
            attribution = {"stage": "custody_window", "note": "fewer than %d scored admissible sources" % MIN_SOURCES}
        elif ep1 < k:
            misses = [s for s in scored_adm if not s["EP1"]]
            attribution = {"stage": "prediction", "misses": [s["source_id"] for s in misses],
                           "sub_stage": ("instrument_threshold_resolution"
                                         if all(s["EP1_tie"] and s["pH_pos_hits"] == 0 and s["EP4"]
                                                and s["C_pot_QH_pos"] < s["criterion_correct"] for s in misses)
                                         else "transfer_mechanism"),
                           "miss_detail": [{"source_id": s["source_id"], "pH_pos": s["pH_pos_hits"],
                                            "pH_neg": s["pH_neg_hits"], "C_pot_QH_pos": s["C_pot_QH_pos"],
                                            "C_pot_QH_neg": s["C_pot_QH_neg"], "criterion": s["criterion_correct"]}
                                           for s in misses]}
        elif not clauses["2_pilot_interior_on_scored"]:
            attribution = {"stage": "pilot"}
        else:
            attribution = {"stage": "custody_or_routes"}
    out["decision"] = {"clauses": clauses, "closes_pending_route_b": closes, "attribution": attribution}
    out["status"] = "OK"
    return out


def parent_ep4():
    """EP-4 on the parent's seven in-session sources (post hoc, reported only)."""
    base = os.path.join(repo_root(), "research", "gmi-833-real-developmental-validation-v1", "REAL_RUNS")
    rows = []
    for i in range(1, 8):
        pp = os.path.join(base, "cl3_T%02d.json" % i)
        qp = os.path.join(base, "cl3_T%02d.json" % (10 + i))
        if not (os.path.exists(pp) and os.path.exists(qp)):
            return {"available": False}
        with open(pp) as h:
            p = json.load(h)
        with open(qp) as h:
            q = json.load(h)
        rows.append({"source": "T%02d/T%02d" % (i, 10 + i), "C_pot_QH_pos": max(p["scores_QH_B2"]),
                     "C_pot_QH_neg": max(q["scores_QH_B2"]), "pH_pos": p["successes_QH"], "pH_neg": q["successes_QH"],
                     "EP4": max(p["scores_QH_B2"]) > max(q["scores_QH_B2"]), "EP1": p["successes_QH"] > q["successes_QH"]})
    return {"available": True, "rows": rows, "EP4_hits": sum(1 for r in rows if r["EP4"]), "of": len(rows),
            "EP1_hits": sum(1 for r in rows if r["EP1"]), "post_hoc": True}


def row_l(sources_dirs, null_seeds):
    out = {"freeze_commit": FREEZE_COMMIT, "amendment_1_commit": AMENDMENT_1_COMMIT}
    cust = Custody(FREEZE_COMMIT)
    out["freeze_committer_time_utc"] = None if cust.t_freeze is None else iso_utc(cust.t_freeze)
    out["freeze_reachable"] = cust.t_freeze is not None and cust.blobs is not None
    out["checker_validation"] = validate_custody_checker(cust)
    out["windows"] = {}
    for win in WINDOWS:
        out["windows"][win["id"]] = row_l_window(win, sources_dirs.get(win["id"]), null_seeds,
                                                 out["checker_validation"])
    w1 = out["windows"]["W1"]
    w2 = out["windows"]["W2"]
    # Combined two-window record (never re-scored; concatenated and reported).
    scored = []
    for wid in ("W1", "W2"):
        w = out["windows"][wid]
        adm = set(v["source_id"] for v in (w.get("custody") or {}).get("verdicts", []) if v["admissible"])
        for s in w.get("scores", []):
            if s.get("status") == "SCORED" and s["source_id"] in adm:
                scored.append((wid, s))
    n = len(scored)
    ep1 = sum(1 for _w, s in scored if s["EP1"])
    ep4 = sum(1 for _w, s in scored if s["EP4"])
    out["combined"] = {"sources": n, "EP1_hits": ep1, "EP4_hits": ep4,
                       "EP2_hits": sum(1 for _w, s in scored if s["EP2"]),
                       "EP3_hits": sum(1 for _w, s in scored if s["EP3"]),
                       "EP1_misses": ["%s:%s" % (w, s["source_id"]) for w, s in scored if not s["EP1"]],
                       "record_level_null_observed_or_better": str(binomial_tail(ep1, n)) if n else None,
                       "procedure_level_null_two_windows": "70/4096",  # amendment 1 5: 1/64 + (6/64)(1/64)
                       "procedure_level_null_note": "closes on 6/6 in window 1, or on 5/6 then 6/6: 1/64 + (6/64)(1/64)",
                       "NULL_RANDOM_SIGN_combined": null_random_sign(n, null_seeds, ep1) if n else None}
    out["EP4_developmental_potential"] = {"parent_seven_sources_post_hoc": parent_ep4(),
                                          "window_1_post_hoc": {"hits": (w1.get("tally") or {}).get("EP4_hits"),
                                                                "of": (w1.get("tally") or {}).get("scored_admissible_sources")},
                                          "window_2_prospective": {"hits": (w2.get("tally") or {}).get("EP4_hits"),
                                                                   "of": (w2.get("tally") or {}).get("scored_admissible_sources")}}
    w1_closes = bool(w1.get("decision", {}).get("closes_pending_route_b"))
    w2_closes = bool(w2.get("decision", {}).get("closes_pending_route_b"))
    clauses = {
        "window_1_reported_verbatim": w1.get("status") == "OK",
        "window_1_closes_under_FREEZE_V1": w1_closes,
        "window_2_closes_under_AMENDMENT_1": w2_closes,
        "closure_rule": "FREEZE_V1 4.6 on window 1, else FREEZE_V1_AMENDMENT_1 5 on window 2; no third window",
    }
    closes = w1_closes or w2_closes
    attribution = None
    if not closes:
        attribution = {"stage": (w2.get("decision", {}).get("attribution") or {}).get("stage", "custody_window"),
                       "window_1": w1.get("decision", {}).get("attribution"),
                       "window_2": w2.get("decision", {}).get("attribution"),
                       "terminal_for_this_lane": w2.get("status") == "OK"}
    out["decision"] = {"clauses": clauses, "closes_pending_route_b": closes, "attribution": attribution,
                       "closing_window": "W1" if w1_closes else ("W2" if w2_closes else None)}
    out["status"] = "OK" if (w1.get("status") == "OK") else w1.get("status")
    return out


# ==========================================================================


def commit_chain():
    """First commit and committer time of every stage file; per-row ordering."""
    stages = {}
    for name, rel in STAGE_FILES:
        rc, out, _e = run_git(["log", "--reverse", "--format=%H %cI", "--", PKG + "/" + rel])
        lines = [ln for ln in out.splitlines() if ln.strip()]
        if rc != 0 or not lines:
            stages[name] = None
        else:
            sha, t = lines[0].split()
            stages[name] = {"commit": sha, "committer_time": t}

    def before(a, b):
        if stages.get(a) is None or stages.get(b) is None:
            return None
        return parse_iso(stages[a]["committer_time"]) <= parse_iso(stages[b]["committer_time"])

    return {"stages": stages,
            "K_predictions_before_K_receipt": before("K_predictions", "K_receipt"),
            "L_record_before_L_receipt": before("L_record", "L_receipt"),
            "freeze_before_everything": all(before("freeze", n) for n in
                                            ("K_predictions", "K_receipt", "L_record", "L_receipt")
                                            if stages.get(n) is not None),
            "K_receipt_before_L_record": before("K_receipt", "L_record"),
            "L_receipt_before_amendment_1": before("L_receipt", "amendment_1"),
            "amendment_1_before_L2_record": before("amendment_1", "L2_record"),
            "L2_record_before_L2_receipt": before("L2_record", "L2_receipt"),
            "L2_extended_record_before_L2_extended_receipt": before("L2_extended_record", "L2_extended_receipt"),
            "audit_shape_disclosed": "COMMIT_CHAIN_INTERLEAVED_PER_ROW"}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    ap.add_argument("--sources-dir", default=os.environ.get("KL_REVIVAL_SOURCES_DIR"))
    ap.add_argument("--sources-dir-2", default=os.environ.get("KL_REVIVAL_SOURCES_DIR_2"))
    ap.add_argument("--null-seeds", type=int, default=200)
    args = ap.parse_args(argv)
    result = {
        "schema": "GMI_833_KL_REVIVAL_RESULT_V1",
        "package": "gmi-833-kl-revival-v1",
        "route": "A",
        "issue": 833,
        "claim_ceiling": CLAIM_CEILING,
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "python": "%d.%d" % sys.version_info[:2],
        "disclosed_post_freeze_deviations": list(DISCLOSURES),
        "commit_chain": commit_chain(),
        "row_K": row_k(args.null_seeds),
        "row_L": row_l({"W1": args.sources_dir, "W2": args.sources_dir_2}, args.null_seeds),
    }
    text = json.dumps(result, indent=1, sort_keys=True)
    if args.out:
        with open(args.out, "w") as handle:
            handle.write(text)
            handle.write("\n")
    brief = {
        "K": {"status": result["row_K"].get("status"),
              "census": result["row_K"].get("census"),
              "truthful": (result["row_K"].get("truthfulness") or {}).get("truthful"),
              "violating_pairs": (result["row_K"].get("soundness") or {}).get("violating_pairs"),
              "decision": result["row_K"].get("decision")},
        "L": {"status": result["row_L"].get("status"),
              "windows": dict((wid, {"status": w.get("status"),
                                     "custody": dict((k, v) for k, v in (w.get("custody") or {}).items() if k != "verdicts"),
                                     "tally": w.get("tally"), "decision": w.get("decision")})
                              for wid, w in result["row_L"]["windows"].items()),
              "combined": result["row_L"].get("combined"),
              "EP4": result["row_L"].get("EP4_developmental_potential"),
              "decision": result["row_L"].get("decision")},
    }
    sys.stdout.write(json.dumps(brief, indent=1, sort_keys=True))
    sys.stdout.write("\n")


if __name__ == "__main__":
    main(sys.argv[1:])
