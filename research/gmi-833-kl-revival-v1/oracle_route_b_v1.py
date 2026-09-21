"""Route B -- materially independent oracle for gmi-833-kl-revival-v1.

Imports NOTHING from this package's route A (``kl_revival_v1``,
``heldout_universes_real4_v1``, ``freeze_predictions_real4_v1``).  It imports
only the parent evaluation package's universe scaffolding (``make_spec``,
``install_universe``, ``load_parent``) and the parent predictor, which it drives
BLACK-BOX: concrete worlds are installed on the registration surface and
``predict`` is run end to end on every input.

Row K: re-derives the bridge from the receipts with its own code, re-declares
SIGMA_REAL4 with its own descriptor, takes the union of F's emitted identified
sets over the value-index worlds, checks seeded random product worlds for
consistency, recomputes census / soundness / truthfulness from the receipt,
and writes the per-input stream in route A's frozen format so the two routes
are compared input by input (sha256).
Row L: recomputes every p0/pH/EP verdict by integer counting over the raw
score lists, replays PS-1 and PR-1, and re-checks custody with string-compared
ISO timestamps and a second git query form (size-prefiltered ls-tree + show).

Run:  python3 -I -B oracle_route_b_v1.py [--out ORACLE_RESULT_V1.json]
         [--random-worlds 8] [--route-a RESULT_V1.json]
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

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
EVAL_PKG = os.path.join(REPO, "research", "gmi-833-capability-predictor-evaluation-v1")
if EVAL_PKG not in sys.path:
    sys.path.insert(0, EVAL_PKG)

import heldout_universes_v1 as hu  # noqa: E402

UNSAT = "UNSATISFIED"
FREEZE_COMMIT = "233bb38a504f7ba10a1a75578840c0416b2e5c0d"
AMENDMENT_1_COMMIT = "65d0025765fef14d423d4e98e0194d23922c0b3d"
PKG = "research/gmi-833-kl-revival-v1"
BAND = Fraction(99, 100)
SIZES = (6, 48)
HEADS = (1, 3, 5, 7)
GRID = {
    "budgets": ((6, 1, 2, 15), (48, 2, 3, 16), (48, 2, 4, 16)),
    "charges": ((0, 0, 0, 0), (1, 0, 0, 0)),
    "d_values": (10, 14, 99),
    "b_values": (0, 8, 16, 24, 32),
    "h_values": ("NO_OBSERVATION", (1, 0), (2, 1)),
    "tau_values": (Fraction(3, 17), Fraction(8, 17), Fraction(11, 17), Fraction(1)),
}
PILOT_GRID = (60, 90, 120, 180, 240, 360, 540)


def git(args):
    p = subprocess.run(["git"] + args, cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode, p.stdout.decode("utf-8", "replace")


def git_bytes(args):
    p = subprocess.run(["git"] + args, cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode, p.stdout


# --------------------------------------------------------------------------
# Row K: independent bridge derivation (a different implementation of CR-1)
# --------------------------------------------------------------------------


def receipts():
    paths = [os.path.join(EVAL_PKG, "REAL_RUNS", "REAL_MEASURED_V1.json"),
             os.path.join(EVAL_PKG, "REAL_RUNS_V2", "REAL_MEASURED_V2.json"),
             os.path.join(EVAL_PKG, "REAL_RUNS_V3", "REAL_MEASURED_V3.json")]
    heads = {}
    for p in paths:
        with open(p) as h:
            d = json.load(h)
        for key, acc in d["per_head_exact_accuracy"].items():
            mech, size, w, task = key.split("|")
            heads[(mech, int(size), int(w), int(task))] = (Fraction(acc["trained"]) >= BAND,
                                                           Fraction(acc["untrained"]) >= BAND)
    return heads


def unanimous(items, want):
    if len(items) < 4 or len(set(k[1] for k in items)) < 2:
        return False
    return all(v == want for v in items.values())


def derive_intervals(heads):
    untrained_any = any(u for (_t, u) in heads.values())
    t0 = dict((k, v[0]) for k, v in heads.items() if k[3] == 0)
    t0_solved = unanimous(t0, True)
    mlp = {}
    for j in (1, 2):
        cells = dict((k, v[0]) for k, v in heads.items() if k[0] == "MLP" and k[3] == j)
        mlp[j] = unanimous(cells, False)
    gru_thr = {}
    for j in (1, 2):
        cells = dict((k, v[0]) for k, v in heads.items() if k[0] == "GRU" and k[3] == j)
        thr = None
        for s in sorted(set(k[1] for k in cells)):
            sub = dict((k, v) for k, v in cells.items() if k[1] >= s)
            if unanimous(sub, True):
                thr = s
                break
        gru_thr[j] = thr

    def intervals(machine):
        mech, size, _w, h = machine
        out = []
        for j in range(3):
            if not (h >> j) & 1:
                out.append((0,) if not untrained_any else (0, 1))
            elif j == 0:
                out.append((1,) if t0_solved else (0, 1))
            elif mech == "MLP":
                out.append((0,) if mlp[j] else (0, 1))
            else:
                thr = gru_thr[j]
                out.append((1,) if (thr is not None and size >= thr) else (0, 1))
        return tuple(out)

    summary = {"untrained_all_unsolved": not untrained_any, "T0_solved": t0_solved,
               "MLP_T1_unsolved": mlp[1], "MLP_T2_unsolved": mlp[2],
               "GRU_T1_threshold": gru_thr[1], "GRU_T2_threshold": gru_thr[2]}
    return intervals, summary


def bits_of_intervals(ivs):
    out = []
    for bands in itertools.product(*ivs):
        b = 0
        for j, x in enumerate(bands):
            if x:
                b |= 1 << j
        out.append(b)
    return tuple(sorted(out))


def machines_real4():
    out = []
    for mech in ("MLP", "GRU"):
        for size in SIZES:
            for w in (0, 1):
                for h in HEADS:
                    out.append((mech, size, w, h))
    return tuple(out)


def descriptor(m):
    mech, size, w, h = m
    pc = bin(h).count("1")
    k = 0 if mech == "MLP" else (1 if size < 12 else 2)
    rho = [0] * hu.RHO_DIM_HELDOUT
    rho[0], rho[1], rho[2], rho[3] = size, 1 + w, 1 + pc, 15 + (1 if mech == "GRU" else 0)
    dev = size + pc + w + (2 if mech == "GRU" else 0)
    return k, tuple(rho), dev, (1 + w, 1 if mech == "GRU" else 0)


def build_spec(machines, world):
    raw = []
    for m in machines:
        k, rho, dev, obs = descriptor(m)
        raw.append((m[1], m[2], m[3], k, rho, dev, obs))
    order = sorted(range(len(raw)), key=lambda i: (raw[i][4][0], raw[i][4][3], raw[i][0], raw[i][1], raw[i][2]))
    rank = [0] * len(raw)
    for pos, idx in enumerate(order):
        rank[idx] = pos
    table = dict(zip(machines, world))
    spec = hu.make_spec("SIGMA_REAL4_B", tuple(raw), tuple(rank), machines, hu.MU_REAL,
                        lambda m: table[m], GRID, lambda rec: rec[1] == 0)
    return dict((k, v) for k, v in spec.items() if not k.startswith("__"))


def run_f(parent):
    """Per input: F's identified set (frozenset) or None if not identified/set."""
    out = []
    for entry in parent.main_grid():
        (k_index, r_value, d_value, b_value, h_value,
         _u_id, u_kind, u_mask, alpha, contract, _tau) = entry
        em = parent.predict(k_index, contract, r_value, h_value, d_value, b_value,
                            u_kind, u_mask, alpha, "REGISTERED")
        if em.disposition == "IDENTIFIED":
            out.append(frozenset([em.value]))
        elif em.disposition == "CANNOT_IDENTIFY":
            out.append(frozenset(em.identified_set))
        else:
            out.append(None)
    return out


def blackbox_union(parent, machines, adm, random_worlds, seed=4242):
    maxlen = max(len(a) for a in adm)
    unions = None
    for t in range(maxlen):
        world = tuple(adm[i][t % len(adm[i])] for i in range(len(machines)))
        hu.install_universe(parent, build_spec(machines, world))
        sets = run_f(parent)
        if unions is None:
            unions = [None if s is None else set(s) for s in sets]
        else:
            for i, s in enumerate(sets):
                if (s is None) != (unions[i] is None):
                    raise ValueError("disposition class changed across worlds at input %d" % i)
                if s is not None:
                    unions[i] |= s
    rng = random.Random(seed)
    inconsistent = 0
    checked = 0
    for _ in range(random_worlds):
        world = tuple(rng.choice(adm[i]) for i in range(len(machines)))
        hu.install_universe(parent, build_spec(machines, world))
        for i, s in enumerate(run_f(parent)):
            if s is None:
                continue
            checked += 1
            if not s <= unions[i]:
                inconsistent += 1
    return ([None if u is None else frozenset(u) for u in unions],
            {"random_worlds": random_worlds, "checked": checked, "inconsistent": inconsistent})


def positive(v):
    return v != UNSAT and v > 0


def census(unions, proto_unions):
    c = {"inputs": len(unions), "inconsistent": 0, "point": 0, "set": 0, "nd1": 0, "nd2": 0,
         "point_degenerate": 0, "nd2_values": {}, "set_sizes": {}}
    for u, pr in zip(unions, proto_unions):
        if u is None:
            c["inconsistent"] += 1
            continue
        if any(positive(v) for v in u) and u < pr:
            c["nd1"] += 1
        if len(u) == 1:
            c["point"] += 1
            v = next(iter(u))
            if positive(v):
                c["nd2"] += 1
                c["nd2_values"][str(v)] = c["nd2_values"].get(str(v), 0) + 1
            else:
                c["point_degenerate"] += 1
        else:
            c["set"] += 1
            c["set_sizes"][str(len(u))] = c["set_sizes"].get(str(len(u)), 0) + 1
    return c


def vkey(v):
    return (1, Fraction(0)) if v == UNSAT else (0, v)


def stream_in_route_a_format(unions, proto_unions):
    """Route A's frozen per-input record, rebuilt from black-box unions."""
    lines = []
    for idx, (u, pr) in enumerate(zip(unions, proto_unions)):
        if u is None:
            lines.append("%d\tINCONSISTENT_REGISTERED_ASSUMPTIONS\t\t\t0\t0" % idx)
            continue
        nd1 = int(any(positive(v) for v in u) and u < pr)
        nd2 = int(len(u) == 1 and positive(next(iter(u))))
        disp = "IDENTIFIED" if len(u) == 1 else "CANNOT_IDENTIFY"
        lines.append("%d\t%s\t%s\t%s\t%d\t%d" % (
            idx, disp, ",".join(str(v) for v in sorted(u, key=vkey)),
            ",".join(str(v) for v in sorted(pr, key=vkey)), nd1, nd2))
    return "\n".join(lines) + "\n"


def cap(bits, contract):
    ver = hu.VERIFIED[contract]
    return sum((hu.MU_REAL[j] for j in range(3) if ver[j] and (bits >> j) & 1), Fraction(0))


def soundness_b(parent, machines, unions, real_bits):
    hu.install_universe(parent, build_spec(machines, real_bits))
    n = parent.N
    pairs = 0
    bad_pairs = 0
    bad_inputs = 0
    for idx, entry in enumerate(parent.main_grid()):
        (k_index, r_value, d_value, b_value, h_value,
         _u_id, _u_kind, u_mask, _alpha, contract, _tau) = entry
        surv = parent.survivor_mask(k_index, d_value, b_value, h_value, u_mask)
        if surv == 0:
            continue
        res = parent.RES_MASKS[r_value]
        bad = False
        for i in range(n):
            if not (surv >> i) & 1:
                continue
            pairs += 1
            v = cap(real_bits[i], contract) if (res >> i) & 1 else UNSAT
            if v not in unions[idx]:
                bad_pairs += 1
                bad = True
        if bad:
            bad_inputs += 1
    return {"pairs": pairs, "violating_pairs": bad_pairs, "violating_inputs": bad_inputs}


def row_k(random_worlds):
    heads = receipts()
    intervals, summary = derive_intervals(heads)
    machines = machines_real4()
    adm = [bits_of_intervals(intervals(m)) for m in machines]
    proto = [tuple(b for b in range(8) if not (b & ~m[3])) for m in machines]
    parent = hu.load_parent()
    before = hu.code_fingerprint(parent)
    unions, consistency = blackbox_union(parent, machines, adm, random_worlds)
    proto_unions, _pc = blackbox_union(parent, machines, proto, 0)
    after = hu.code_fingerprint(parent)
    c = census(unions, proto_unions)
    stream = stream_in_route_a_format(unions, proto_unions)
    out = {"bridge_summary": summary, "resolved_machines": sum(1 for a in adm if len(a) == 1),
           "committed_cells": sum(len([iv for iv in intervals(m) if len(iv) == 1]) for m in machines),
           "census": c, "random_world_consistency": consistency,
           "parent_code_unchanged": before[0] == after[0],
           "proto_census": census(proto_unions, proto_unions),
           "stream_sha256_route_a_format": hashlib.sha256(stream.encode("utf-8")).hexdigest()}
    path = os.path.join(HERE, "REAL_RUNS_V4", "REAL_MEASURED_V4.json")
    if os.path.exists(path):
        with open(path) as h:
            rec = json.load(h)
        real_bits = tuple(int(rec["measured_solved_bits"]["|".join(str(x) for x in m)]) for m in machines)
        out["truthful"] = sum(1 for i in range(len(machines)) if real_bits[i] in adm[i])
        out["untruthful_machines"] = ["|".join(str(x) for x in machines[i])
                                      for i in range(len(machines)) if real_bits[i] not in adm[i]]
        out["soundness"] = soundness_b(parent, machines, unions, real_bits)
        import heldout_universes_v3 as hv3
        v3 = [(hv3.real3_solved_law(m),) for m in machines]
        v3_unions, _ = blackbox_union(parent, machines, v3, 0)
        out["PK1_v3_point_law"] = {"nd2": census(v3_unions, proto_unions)["nd2"],
                                   "truthful": sum(1 for i in range(len(machines)) if real_bits[i] in v3[i])}
        out["PK2_cb_proto"] = {"nd1": out["proto_census"]["nd1"], "nd2": out["proto_census"]["nd2"],
                               "truthful": sum(1 for i in range(len(machines)) if real_bits[i] in proto[i])}
    else:
        out["truthful"] = None
        out["soundness"] = None
    return out


# --------------------------------------------------------------------------
# Row L
# --------------------------------------------------------------------------


def iso_norm(s):
    """Normalise to 'YYYY-MM-DDTHH:MM:SS' in UTC, comparable as a string."""
    s = s.strip()
    if s.endswith("Z"):
        return s[:-1]
    if len(s) >= 6 and s[-6] in "+-" and s[-3] == ":":
        sign = 1 if s[-6] == "+" else -1
        hh, mm = int(s[-5:-3]), int(s[-2:])
        base = datetime.datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S")
        base = base - sign * datetime.timedelta(hours=hh, minutes=mm)
        return base.strftime("%Y-%m-%dT%H:%M:%S")
    return s[:19]


def plus_seconds(norm, seconds):
    t = datetime.datetime.strptime(norm, "%Y-%m-%dT%H:%M:%S") + datetime.timedelta(seconds=seconds)
    return t.strftime("%Y-%m-%dT%H:%M:%S")


def freeze_blob_sha256_by_size(anchor, sizes):
    """Second query form: `ls-tree -r -l` lists blob sizes; only blobs whose size
    is one of `sizes` can share a sha256 with a source, so only those are shown."""
    rc, out = git(["ls-tree", "-r", "-l", anchor])
    if rc != 0:
        return None, None
    found = set()
    tracked = 0
    for line in out.splitlines():
        if not line.strip():
            continue
        meta, path = line.split("\t", 1)
        parts = meta.split()
        tracked += 1
        if parts[1] != "blob" or parts[3] == "-":
            continue
        if int(parts[3]) in sizes:
            rc2, data = git_bytes(["show", "%s:%s" % (anchor, path)])
            if rc2 == 0:
                found.add(hashlib.sha256(data).hexdigest())
    return found, tracked


WINDOWS = (
    ("W1", FREEZE_COMMIT, "POSTERIOR_SOURCES_V1.json", "REAL_RUNS_L4", "cl4", 21, 31),
    ("W2", AMENDMENT_1_COMMIT, "POSTERIOR_SOURCES_V2_EXTENDED.json", "REAL_RUNS_L5", "cl5", 41, 51),
)


def row_l_window(wid, anchor, record_name, runs, prefix, pos_base, neg_base):
    out = {"window": wid, "anchor": anchor}
    rc, ft = git(["log", "-1", "--format=%cI", anchor])
    if rc != 0 or not ft.strip():
        out["status"] = "ANCHOR_UNREACHABLE"
        return out
    t_anchor = iso_norm(ft)
    guard = plus_seconds(t_anchor, 60)
    out["anchor_time_utc"] = t_anchor
    path = os.path.join(HERE, record_name)
    if not os.path.exists(path):
        out["status"] = "POSTERIOR_RECORD_UNAVAILABLE"
        return out
    with open(path) as h:
        rec = json.load(h)
    sizes = set(s["bytes"] for s in rec["admitted"])
    found, tracked = freeze_blob_sha256_by_size(anchor, sizes)
    out["tracked_paths_at_anchor"] = tracked
    out["size_matched_blobs_hashed"] = None if found is None else len(found)
    cands = rec["candidates"]
    adm_c = [c for c in cands if c["verdict"] == "ADMITTED"]
    ps1 = {
        "rcstart_matches_anchor_plus_60s": rec["rcstart"] == guard + "Z",
        "ascending": [(c["rc"]["timestamp"], c["rc"]["revid"]) for c in cands]
        == sorted((c["rc"]["timestamp"], c["rc"]["revid"]) for c in cands),
        "admitted_match_candidates": [(c["revision"]["revid"], c["sha256_of_bytes"], c["revision"]["timestamp"]) for c in adm_c]
        == [(a["revid"], a["sha256"], a["creation_timestamp"]) for a in rec["admitted"]],
        "k": len(rec["admitted"]) == rec["k_admitted"] == min(rec["k_requested"], len(adm_c)),
        "every_admitted_is_a_large_creation_revision": all(
            c["rc"]["newlen"] >= 2000 and c["bytes"] >= 410 and c["revision"]["parentid"] == 0
            and c["revision"]["sha1"] == c["sha1_of_bytes"] and c["rc"]["timestamp"] > rec["rcstart"]
            for c in adm_c),
        "every_non_admitted_has_a_reason": all(
            (c["rc"]["newlen"] < 2000 and c["verdict"].startswith("SKIPPED_NEWLEN"))
            or c["verdict"].startswith("REJECTED_") for c in cands if c["verdict"] != "ADMITTED"),
        "fetch_after_anchor": iso_norm(rec["T_fetch_utc"]) > t_anchor,
    }
    ps1["ok"] = all(ps1.values())
    out["ps1_replay"] = ps1
    verdicts = []
    for s in rec["admitted"]:
        posterior = iso_norm(s["creation_timestamp"]) > guard
        attested = bool(s.get("wikimedia_sha1")) and s.get("wikimedia_sha1") == s.get("sha1_of_bytes")
        exogenous = (found is not None) and (s["sha256"] not in found) and ps1["ok"]
        verdicts.append({"source_id": s["source_id"], "posterior": posterior, "attested": attested,
                         "exogenous": exogenous, "dated": bool(s.get("creation_timestamp")) and bool(s.get("wikimedia_sha1")),
                         "admissible": posterior and attested and exogenous})
    out["custody"] = verdicts
    out["admissible"] = sum(1 for v in verdicts if v["admissible"])
    scores = {}
    for p in glob.glob(os.path.join(HERE, runs, prefix + "_T*.json")):
        with open(p) as h:
            d = json.load(h)
        crit = d["criterion_correct"]
        pH = sum(1 for x in d["scores_QH_B2"] if x >= crit)
        p0 = sum(1 for x in d["scores_Q0_B2"] if x >= crit)
        scores[d["sequence_id"]] = {"p0": p0, "pH": pH, "src": d["source_sha256"], "n": d["N_prop"],
                                    "c": d["c"], "cpot": max(d["scores_QH_B2"]),
                                    "counts_consistent": (pH == d["successes_QH"] and p0 == d["successes_Q0"]
                                                          and max(d["scores_QH_B2"]) == d["C_pot_QH_B2"])}
    pilots = {}
    for p in glob.glob(os.path.join(HERE, runs, "pilot_T*.json")):
        with open(p) as h:
            d = json.load(h)
        chosen = None
        for b in PILOT_GRID:
            hits = d["pilot_grid"].get(str(b))
            if chosen is None and hits is not None and 9 <= hits <= 21:
                chosen = b
        pilots[d["sequence_id"]] = {"B_prop": d["B_prop"], "replayed": chosen, "src": d["source_sha256"],
                                    "ok": chosen == d["B_prop"]}
    per = []
    for n, s in enumerate(rec["admitted"]):
        pos, neg = "T%02d" % (pos_base + n), "T%02d" % (neg_base + n)
        if pos in scores and neg in scores and pos in pilots:
            a, b, pl = scores[pos], scores[neg], pilots[pos]
            per.append({"source_id": s["source_id"], "EP1": a["pH"] > b["pH"], "EP2": b["pH"] == 0,
                        "EP3": a["pH"] > a["p0"], "EP4": a["cpot"] > b["cpot"],
                        "pH_pos": "%d/%d" % (a["pH"], a["n"]),
                        "pH_neg": "%d/%d" % (b["pH"], b["n"]), "p0_pos": "%d/%d" % (a["p0"], a["n"]),
                        "C_pot_QH_pos": a["cpot"], "C_pot_QH_neg": b["cpot"], "B_prop": a["c"],
                        "source_ok": a["src"] == s["sha256"] == b["src"] == pl["src"],
                        "pilot_ok": pl["ok"] and a["c"] == pl["B_prop"] == b["c"],
                        "counts_consistent": a["counts_consistent"] and b["counts_consistent"]})
    out["scores"] = per
    out["EP1_hits"] = sum(1 for x in per if x["EP1"])
    out["EP4_hits"] = sum(1 for x in per if x["EP4"])
    out["scored"] = len(per)
    out["all_pilots_ok"] = all(x["pilot_ok"] for x in per)
    out["all_sources_ok"] = all(x["source_ok"] for x in per)
    out["status"] = "OK"
    return out


def row_l():
    out = {"windows": {}}
    for wid, anchor, record_name, runs, prefix, pos_base, neg_base in WINDOWS:
        out["windows"][wid] = row_l_window(wid, anchor, record_name, runs, prefix, pos_base, neg_base)
    out["EP1_hits_combined"] = sum(w.get("EP1_hits", 0) for w in out["windows"].values())
    out["scored_combined"] = sum(w.get("scored", 0) for w in out["windows"].values())
    out["status"] = "OK"
    return out


def compare_window(aw, bw):
    if aw is None or bw is None:
        return {"present_in_both": False}
    agree = {"present_in_both": True,
             "status": aw.get("status") == bw.get("status")}
    if aw.get("status") != "OK" or bw.get("status") != "OK":
        return agree
    agree["admissible"] = (aw.get("custody") or {}).get("admissible") == bw.get("admissible")
    agree["EP1_hits"] = (aw.get("tally") or {}).get("EP1_hits") == bw.get("EP1_hits")
    agree["EP4_hits"] = (aw.get("tally") or {}).get("EP4_hits") == bw.get("EP4_hits")
    agree["scored"] = (aw.get("tally") or {}).get("scored_admissible_sources") == bw.get("scored")
    agree["ps1_replay"] = (aw.get("ps1_replay") or {}).get("ok") == (bw.get("ps1_replay") or {}).get("ok")
    a_v = dict((v["source_id"], v) for v in (aw.get("custody") or {}).get("verdicts", []))
    ok = len(a_v) == len(bw.get("custody", []))
    for v in bw.get("custody", []):
        av = a_v.get(v["source_id"])
        if av is None:
            ok = False
            continue
        cl = av["clauses"]
        ok = ok and (cl["2_posterior"] == v["posterior"] and cl["4_attested"] == v["attested"]
                     and cl["3_exogenous"] == v["exogenous"] and cl["1_dated"] == v["dated"]
                     and av["admissible"] == v["admissible"])
    agree["per_source_custody_clauses"] = ok
    a_s = dict((s["source_id"], s) for s in aw.get("scores", []) if s.get("status") == "SCORED")
    ok = len(a_s) == len(bw.get("scores", []))
    for s in bw.get("scores", []):
        x = a_s.get(s["source_id"])
        if x is None:
            ok = False
            continue
        ok = ok and (Fraction(x["pH_pos"]) == Fraction(s["pH_pos"]) and Fraction(x["pH_neg"]) == Fraction(s["pH_neg"])
                     and Fraction(x["p0_pos"]) == Fraction(s["p0_pos"]) and x["EP1"] == s["EP1"]
                     and x["EP2"] == s["EP2"] and x["EP3"] == s["EP3"] and x["EP4"] == s["EP4"]
                     and x["C_pot_QH_pos"] == s["C_pot_QH_pos"] and x["C_pot_QH_neg"] == s["C_pot_QH_neg"]
                     and x["c"] == s["B_prop"])
    agree["per_source_p0_pH_Cpot_verdicts"] = ok
    return agree


def compare(a, k, l):
    ak = a["row_K"]
    agree_k = {
        "inputs": ak["census"]["inputs"] == k["census"]["inputs"],
        "inconsistent": ak["census"]["inconsistent"] == k["census"]["inconsistent"],
        "point": ak["census"]["point"] == k["census"]["point"],
        "set": ak["census"]["set"] == k["census"]["set"],
        "nd1": ak["census"]["nd1"] == k["census"]["nd1"],
        "nd2": ak["census"]["nd2"] == k["census"]["nd2"],
        "nd2_values": ak["census"]["nd2_values"] == k["census"]["nd2_values"],
        "per_input_stream": ak["frozen_stream"]["executor_sha256"] == k["stream_sha256_route_a_format"],
        "resolved_machines": ak.get("resolved_machines") == k.get("resolved_machines"),
        "committed_cells": ak.get("committed_cells") == k.get("committed_cells"),
        "truthful": (ak.get("truthfulness") or {}).get("truthful") == k.get("truthful"),
        "violating_pairs": (ak.get("soundness") or {}).get("violating_pairs") == (k.get("soundness") or {}).get("violating_pairs"),
        "pairs": (ak.get("soundness") or {}).get("pairs") == (k.get("soundness") or {}).get("pairs"),
        "PK1_nd2": ak["positive_controls"]["PK1_v3_point_law"]["nd2"] == (k.get("PK1_v3_point_law") or {}).get("nd2"),
        "PK1_truthful": ak["positive_controls"]["PK1_v3_point_law"].get("truthful_machines") == (k.get("PK1_v3_point_law") or {}).get("truthful"),
        "PK2_zero": ak["positive_controls"]["PK2_cb_proto"]["both_zero"] == (k["proto_census"]["nd1"] == 0 and k["proto_census"]["nd2"] == 0),
    }
    hk5 = (ak.get("hostiles") or {}).get("HK5_route_disagreement") or {}
    hk5_detected = None
    if hk5.get("applicable") and hk5.get("mutated_stream_sha256"):
        hk5_detected = (hk5["mutated_stream_sha256"] != k["stream_sha256_route_a_format"]
                        and hk5["true_stream_sha256"] == k["stream_sha256_route_a_format"])
    al = a["row_L"]
    agree_l = {}
    for wid in ("W1", "W2"):
        agree_l[wid] = compare_window((al.get("windows") or {}).get(wid), l["windows"].get(wid))
    agree_l["combined_EP1_hits"] = (al.get("combined") or {}).get("EP1_hits") == l.get("EP1_hits_combined")
    agree_l["combined_sources"] = (al.get("combined") or {}).get("sources") == l.get("scored_combined")
    flat_l = all(all(v for kk, v in w.items()) if isinstance(w, dict) else w for w in agree_l.values())
    return {"row_K": agree_k, "row_L": agree_l, "HK5_route_disagreement_detected": hk5_detected,
            "all": all(agree_k.values()) and flat_l and hk5_detected is True}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    ap.add_argument("--random-worlds", type=int, default=8)
    ap.add_argument("--route-a", default=None)
    args = ap.parse_args(argv)
    k = row_k(args.random_worlds)
    l = row_l()
    res = {"schema": "GMI_833_KL_REVIVAL_ORACLE_RESULT_V1", "route": "B", "row_K": k, "row_L": l}
    if args.route_a and os.path.exists(args.route_a):
        with open(args.route_a) as h:
            a = json.load(h)
        res["agreement"] = compare(a, k, l)
    text = json.dumps(res, indent=1, sort_keys=True, default=str)
    if args.out:
        with open(args.out, "w") as h:
            h.write(text)
            h.write("\n")
    sys.stdout.write(json.dumps({
        "K": dict((k2, v) for k2, v in k.items() if k2 in ("census", "truthful", "soundness", "resolved_machines",
                                                          "random_world_consistency", "PK1_v3_point_law")),
        "L": dict((wid, dict((k2, v) for k2, v in w.items() if k2 in ("admissible", "EP1_hits", "EP4_hits", "scored", "status")))
                  for wid, w in l["windows"].items()),
        "agreement": res.get("agreement")}, indent=1, sort_keys=True, default=str))
    sys.stdout.write("\n")


if __name__ == "__main__":
    main(sys.argv[1:])
