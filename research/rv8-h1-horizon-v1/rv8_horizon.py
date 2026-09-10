"""RV-8 H1 horizon: does a learned library ever repay its own acquisition?

FNA-4 established the PER-TASK inequality at 16 tasks and PROJECTED a break-even at
~6,123 tasks. That is a 380x extrapolation, so
``LIBRARY_ACQUISITION_EXCEEDS_LATER_SAVINGS`` is currently PROJECTED, NOT OBSERVED.
This study runs the horizon directly on a (horizon x same-family-mix) grid.

Nothing in FNA-4's world, solver, learners, arms or cost model changes. This module
IMPORTS them (``fna4``, ``fna4_solver``, ``fna4_learners``, ``run_fna4``); it never
copies or re-implements them. Every cost term FNA-4 charges is still charged:
simulations, checker calls, posting reads, learner steps, macro-body simulations,
hole-domain enumeration, misfire probes and CEGIS refinements.

Execute on LUNARC (never on the Mac):

    python3 rv8_horizon.py preflight  <out_dir>
    python3 rv8_horizon.py replicate  <out_dir>      # frozen-receipt determinism gate
    python3 rv8_horizon.py cell <cell_index> <out_dir>

Python 3.8-compatible syntax, stdlib only, no network.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import pickle
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
FNA4 = HERE.parents[0] / "functional-neural-absorption-v1" / "fna4_library_synthesis"
if str(FNA4) not in sys.path:
    sys.path.insert(0, str(FNA4))

from fna4 import (CATALOGUE, PRIMITIVES, Work, family_of, gen_task,  # noqa: E402
                  make_macro, name_params)
from fna4_solver import MisfireRegistry, solve_task, validate_selection_mirror  # noqa: E402
import fna4_learners as L  # noqa: E402
import run_fna4 as R  # noqa: E402

SCHEMA = "ocm.rv8.h1-horizon.v1"

# ---------------------------------------------------------------------------
# FROZEN DESIGN.  Every constant below is fixed before any scored run.
# ---------------------------------------------------------------------------

#: Stream salt, disjoint from every FNA-4 salt (620001 / 630001 / 640001 / 650001 and
#: the revival sweep's SALT_SWEEP+2000). Fresh tasks = new payloads + new parameter
#: draws, and the acquisition stream is untouched, so acquisition and stream stay
#: disjoint exactly as FNA4_PROTOCOL.md requires.
SALT_RV8 = 810001

#: Same-family share of the stream. F2 (MERGE-AC) is the only family on which the
#: library pays in FNA-4's frozen per-task deltas, so "same-family share" IS the F2
#: share. The grid spans below, through and past the 11.8-17.0% critical band
#: (STITCH_NOGOOD_CEGIS balanced 0.1176 .. STITCH balanced 0.1696) and past the
#: all-F1 edges (0.1740 and 0.2417).
MIX_GRID = (0.0, 0.05, 0.10, 0.12, 0.15, 0.17, 0.20, 0.25, 0.35, 0.50, 0.75, 1.0)

#: Composition of the non-F2 remainder: FNA-4's own two conventions.
COMPOSITIONS = ("balanced", "f1_only")

#: Frozen tie-break order for the prefix-preserving deficit allocator.
FAMILY_ORDER = ("F2", "F1", "F3")

STREAM_SEEDS = (0, 1, 2, 3, 4)
NULL_SEEDS = (0, 1, 2)

#: Horizon ceiling, sized BEFORE any scored cell from two pre-existing sources:
#:   (a) FNA-4's frozen per-family deltas: saving/task = m*34998 - (1-m)*(11153+3146)/2
#:       gives N* = 240,294,343 / saving  ->  ~17,257 at m=0.50 balanced, ~6,866 at m=1.
#:   (b) An unscored timing probe on a disjoint salt (999001, 3 draws/family) gives
#:       STITCH saving/task ~1,184 at m=0.50 balanced -> N* ~203,000.
#: The two disagree by >10x because FNA-4's per-family deltas rest on 8/4/4 draws of a
#: heavy-tailed cost distribution. 131,072 contains (a) with ~7.6x margin and reaches
#: well into (b). If no crossing appears by 131,072 the answer is "no crossover within
#: the horizon reached", stated with that horizon and never extrapolated further.
N_FULL = 131072
N_REDUCED = 4096
HORIZON_LADDER = (16, 64, 256, 1024, 4096, 16384, 32768, 65536, 131072)

#: Pre-registered reduced horizon. An arm runs the reduced horizon iff FNA-4's frozen
#: per-family deltas make its saving/task negative at EVERY point of MIX_GRID under both
#: compositions, so no horizon can cross. Recomputed and asserted in preflight():
#:   CHUNK    F1 +856    F2 +47980   F3 -96    -> max saving/task = -380  (m=0 balanced)
#:   AU_PAIR  F1 +29904  F2 +986944  F3 +5808  -> max saving/task = -17856
#:   EGGRAPH  F1 +20492  F2 +1126800 F3 +3403  -> max saving/task = -11947
#: The independent timing probe agrees on all three (AU_PAIR 15x, EGGRAPH 12x, CHUNK
#: 1.7x the incumbent's F2 cost). The sign is established with a tight CI on a
#: 4,096-task prefix of the SAME paired stream; the freed budget goes to the arms where
#: a crossover is possible. PRE-REGISTERED ESCALATION: if any reduced arm's measured
#: saving/task CI includes zero at any grid point, that arm is escalated to the full
#: horizon in a NEW frozen study -- never by extending this grid.
REDUCED_ARMS = ("CHUNK", "AU_PAIR", "EGGRAPH")

FULL_ARMS = ("NO_LIBRARY", "STITCH", "STITCH_NOGOOD_CEGIS", "NOGOOD_ONLY_per_batch")
NULL_ARMS = ("SHUFFLE_NULL", "SHUFFLE_NULL_NC")
ARMS = FULL_ARMS + REDUCED_ARMS + NULL_ARMS

#: FNA-4 frozen per-family per-task deltas vs NO_LIBRARY (FNA4_RESULTS.json,
#: per_task_delta_vs_no_library). Used ONLY to derive REDUCED_ARMS and to size N_FULL.
FROZEN_DELTAS = {
    "CHUNK": {"F1": 856, "F2": 47980, "F3": -96},
    "AU_PAIR": {"F1": 29904, "F2": 986944, "F3": 5808},
    "EGGRAPH": {"F1": 20492, "F2": 1126800, "F3": 3403},
    "STITCH": {"F1": 11153, "F2": -34998, "F3": 3146},
    "STITCH_NOGOOD_CEGIS": {"F1": 9594, "F2": -45550, "F3": 2552},
    "NOGOOD_ONLY_per_batch": {"F1": 0, "F2": -857, "F3": 0},
}

#: HARD GATE. Acquisition is deterministic and must reproduce FNA-4 run 3 exactly
#: (FNA4_RESULTS.json phases.main.arms[*].acquisition_work). Any drift terminates with
#: CANNOT_CHECK_ACQUISITION_DRIFT and NO cost number is filed.
FROZEN_ACQUISITION = {
    "NO_LIBRARY": {"total_units": 13549261, "learner_steps": 64305},
    "CHUNK": {"total_units": 13550768, "learner_steps": 65812},
    "AU_PAIR": {"total_units": 14684038, "learner_steps": 1199082},
    "EGGRAPH": {"total_units": 13565306, "learner_steps": 80350},
    "STITCH": {"total_units": 253779299, "learner_steps": 240294343},
    "NOGOOD_ONLY_per_batch": {"total_units": 13495472, "learner_steps": 173186},
    "STITCH_NOGOOD_CEGIS": {"total_units": 253725510, "learner_steps": 240403224},
}

#: HARD GATE. FNA-4's repeat-rate sweep r=0 point (FNA4_RESULTS.json
#: repeat_rate_sweep_frozen_axis.points[0] and r0_economics) must reproduce exactly.
#: This certifies that the ~6,123 projection and this study come from one machine.
FROZEN_SWEEP_R0 = {"no_library_total": 1711950, "with_library_test_work": 770026,
                   "saving": 941924, "macro_hits": 19,
                   "break_even_tasks_marginal": 6122.6}

TERMINALS = ("CANNOT_CHECK_ACQUISITION_DRIFT",
             "CANNOT_CHECK_SELECTION_MIRROR_DISAGREES_WITH_PRODUCTION_INDEX",
             "CANNOT_CHECK_FROZEN_SWEEP_REPLICATION_DRIFT")

#: Progressive dump interval: a timed-out or crashed cell still yields a usable,
#: honestly-labelled prefix (defect runs preserved, never edited).
DUMP_EVERY = 4096


# ---------------------------------------------------------------------------
# stream construction (frozen)
# ---------------------------------------------------------------------------


def mix_targets(mix, composition):
    """Family target shares. F2 carries the same-family share; the remainder splits by
    the frozen composition convention."""
    rest = 1.0 - mix
    if composition == "balanced":
        return {"F2": mix, "F1": rest / 2.0, "F3": rest / 2.0}
    if composition == "f1_only":
        return {"F2": mix, "F1": rest, "F3": 0.0}
    raise ValueError(composition)


def family_sequence(mix, composition, n):
    """Prefix-preserving deficit allocation: after EVERY prefix length the realised
    family shares match the targets to within one task. That is what makes the horizon
    ladder readable as prefixes of a single stream without the mix drifting. Ties break
    by the frozen FAMILY_ORDER."""
    tgt = mix_targets(mix, composition)
    live = [f for f in FAMILY_ORDER if tgt[f] > 0.0]
    count = dict((f, 0) for f in FAMILY_ORDER)
    out = []
    for i in range(n):
        best, best_d = None, None
        for f in live:                      # FAMILY_ORDER scan == frozen tie-break
            d = tgt[f] * (i + 1) - count[f]
            if best_d is None or d > best_d + 1e-12:
                best, best_d = f, d
        out.append(best)
        count[best] += 1
    return out


def stream_task(mix_idx, composition, seed, pos, family):
    """One fresh task at stream position ``pos``.

    DECLARED DIFFERENCE from FNA-4's stream builders, frozen here with its reason:
    FNA-4 draws a stream from ONE shared ``random.Random``; this study seeds a fresh
    ``random.Random`` per position from (SALT_RV8, mix_idx, composition, seed, pos).
    The marginal draw distribution is identical (the same ``gen_task`` over the same
    parameter spaces), but any worker can regenerate any prefix independently, which is
    what makes a 131,072-task ladder parallelisable and prefix-reproducible.

    No parameter tuple is ever FORCED. FNA-4's sweep builder fills its uncovered quota
    from ``_f1_param_space()`` in product order, so at r=0 its twelve F1 tasks are
    near-identical draws from one corner of a 648-tuple space. These are natural draws.
    """
    h = hashlib.sha256(("|".join([str(SALT_RV8), str(mix_idx), composition,
                                  str(seed), str(pos)])).encode("utf-8")).digest()
    rng = random.Random(int.from_bytes(h[:8], "big"))
    uid = "RV8-%d-%s-%d-%d-%s" % (mix_idx, composition, seed, pos, family)
    return gen_task(rng, family, uid)


# ---------------------------------------------------------------------------
# shuffle-equal-n null (frozen)
# ---------------------------------------------------------------------------


def _family_slot_values():
    """Legal parameter values per (family, arity, slot index), read off the catalogue.
    ``agg`` appears at two arities (agg:count vs agg:sum:fK), so arity is part of the
    key."""
    out = {}
    for n in CATALOGUE:
        params = name_params(n)[1:]
        key = (family_of(n), len(params))
        slots = out.setdefault(key, [])
        while len(slots) < len(params):
            slots.append(set())
        for i, v in enumerate(params):
            slots[i].add(v)
    return dict((k, tuple(tuple(sorted(s)) for s in v)) for k, v in out.items())


FAMILY_SLOTS = _family_slot_values()


def _io_of(key):
    fam, arity = key
    for n in CATALOGUE:
        if family_of(n) == fam and len(name_params(n)[1:]) == arity:
            return PRIMITIVES[n][0], PRIMITIVES[n][1]
    raise KeyError(key)


def shuffle_null_library(macros, null_seed):
    """Shuffle-equal-n null: a library matched to ``macros`` on everything except where
    its content came from.

    Matched: macro COUNT, body LENGTH per macro, hole POSITIONS, hole DOMAIN SIZES
    (hence the number of enumerated assignments -- the real per-attempt burden), and
    type coherence (each step's primary input type equals the previous step's output
    type, the property the learned macros have). Randomised: which catalogue families
    and constants fill those slots.

    Matching enumeration burden and not merely macro count is the point: 24-element
    domains cost far more per attempt than 2-element ones, so a count-only match would
    make the null look artificially bad and the "not selectivity" conclusion unearned.

    Returns (library, profile). ``profile`` records the match, including any slot whose
    family could not host the required domain size, so the null is auditable rather
    than assumed.
    """
    rng = random.Random(int.from_bytes(hashlib.sha256(
        ("RV8-NULL|%d" % null_seed).encode("utf-8")).digest()[:8], "big"))
    keys = sorted(FAMILY_SLOTS)
    out, profile = [], []
    for m in macros:
        want = []            # per step: (arity, slot marks, required domain sizes)
        h = 0
        for _fam, slots in m.skeleton:
            marks, sizes = [], []
            for s in slots:
                if s is None:
                    marks.append(None)
                    sizes.append(len(m.domains[h]))
                    h += 1
                else:
                    marks.append("const")
                    sizes.append(1)
            want.append((len(slots), marks, sizes))

        best, best_short = None, None
        for _try in range(400):
            chain, prev_out, ok = [], None, True
            for (arity, _marks, _sizes) in want:
                cands = [k for k in keys if k[1] == arity and
                         (prev_out is None or _io_of(k)[0][0] == prev_out)]
                if not cands:
                    ok = False
                    break
                k = cands[rng.randrange(len(cands))]
                chain.append(k)
                prev_out = _io_of(k)[1]
            if not ok:
                continue
            short, skel, doms = 0, [], []
            for (k, (_arity, marks, sizes)) in zip(chain, want):
                vals = FAMILY_SLOTS[k]
                slots_out = []
                for i, mk in enumerate(marks):
                    pool = list(vals[i])
                    if mk == "const":
                        slots_out.append(pool[rng.randrange(len(pool))])
                    else:
                        need = sizes[i]
                        if len(pool) < need:
                            short += need - len(pool)
                            pick = pool
                        else:
                            pick = rng.sample(pool, need)
                        slots_out.append(None)
                        doms.append(tuple(sorted(pick)))
                skel.append((k[0], tuple(slots_out)))
            cand = (tuple(skel), tuple(doms), short)
            if best is None or short < best_short:
                best, best_short = cand, short
            if short == 0:
                break
        skel, doms, short = best
        nm = make_macro(skel, [], label="SHUFFLE_NULL", domains=doms)
        out.append(nm)
        profile.append({"source_macro_id": m.macro_id,
                        "source_len": len(m.skeleton), "null_len": len(nm.skeleton),
                        "assignments_source": len(m.assignments()),
                        "assignments_null": len(nm.assignments()),
                        "domain_shortfall_values": short,
                        "source_families": list(m.families()),
                        "null_families": list(nm.families())})
    return out, profile


# ---------------------------------------------------------------------------
# arms (frozen; run_fna4.run_arm's structure, reproduced not re-invented)
# ---------------------------------------------------------------------------

ARM_SPEC = {
    # name: (learner, registry_granularity, use_cegis, nulls_this_arm)
    "NO_LIBRARY": (None, None, False, None),
    "CHUNK": (L.learn_chunk, None, False, None),
    "AU_PAIR": (L.learn_au, None, False, None),
    "EGGRAPH": (L.learn_egraph, None, False, None),
    "STITCH": (L.learn_stitch, None, False, None),
    "NOGOOD_ONLY_per_batch": (None, "per_batch", False, None),
    "STITCH_NOGOOD_CEGIS": (L.learn_stitch, "per_batch", True, None),
    "SHUFFLE_NULL": (L.learn_stitch, None, False, "STITCH"),
    "SHUFFLE_NULL_NC": (L.learn_stitch, "per_batch", True, "STITCH_NOGOOD_CEGIS"),
}


def acquire(arm, null_seed=None):
    """Acquisition exactly as ``run_fna4.run_arm`` does it: ONE shared Work across the
    acquisition solves and the learner call (so the marginal figure includes the
    collect_all bookkeeping the solver charges in goal_found), and ONE MisfireRegistry
    constructed here and carried into every later task.

    Returns (library, acq_work_dict, registry, use_cegis, null_profile).
    """
    learner, gran, use_cegis, nulls = ARM_SPEC[arm]
    work_acq = Work()
    registry = MisfireRegistry(gran) if gran else None
    acq_receipts = [solve_task(t, macros=(), registry=registry, work=work_acq,
                               collect_all=True)
                    for t in R.acquisition_stream()]
    macros = learner(acq_receipts, work_acq) if learner is not None else []
    acq = work_acq.as_dict()
    profile = None
    if nulls is not None:
        # The null pays the SAME acquisition it nulls: the question is whether the
        # library's CONTENT earns the saving, not whether acquisition can be skipped.
        macros, profile = shuffle_null_library(macros, null_seed)
    return list(macros), acq, registry, use_cegis, profile


def acquisition_gate(arm, acq):
    """Hard gate: acquisition must reproduce FNA-4 run 3 exactly."""
    ref = FROZEN_ACQUISITION[ARM_SPEC[arm][3] or arm]
    ok = (acq["total_units"] == ref["total_units"] and
          acq["learner_steps"] == ref["learner_steps"])
    return ok, {"expected": ref,
                "observed": {"total_units": acq["total_units"],
                             "learner_steps": acq["learner_steps"]}}


def run_stream(arm, macros, registry, use_cegis, families, mix_idx, composition, seed,
               on_chunk=None):
    """Solve the stream sequentially, recording per-task cost. Sequential is mandatory:
    the misfire registry saturates and CEGIS shrinks hole domains across tasks, so an
    arm's cost at position i genuinely depends on positions < i."""
    lib = list(macros)
    units, capped, hits, misf = [], [], [], []
    for pos, fam in enumerate(families):
        t = stream_task(mix_idx, composition, seed, pos, fam)
        w = Work()
        r = solve_task(t, macros=lib, registry=registry, work=w)
        if use_cegis:
            for att in r["macro_attempts"]:
                if att["misfires"] > 0 and not att["hit"] \
                        and att["first_failed_assignment"] is not None:
                    m = next((m for m in lib if m.macro_id == att["macro_id"]), None)
                    if m is not None:
                        m2, ok = L.specialize(
                            m, tuple(att["first_failed_assignment"]), w)
                        if ok:
                            lib[lib.index(m)] = m2
            r["work"] = w.as_dict()     # refinement charged into THIS task, once
        units.append(r["work"]["total_units"])
        capped.append(1 if r["capped"] else 0)
        hits.append(r["macro_hits"])
        misf.append(r["misfires"])
        if on_chunk is not None and (pos + 1) % DUMP_EVERY == 0:
            on_chunk(units, capped, hits, misf, len(lib))
    return {"units": units, "capped": capped, "macro_hits": hits, "misfires": misf,
            "library_size_final": len(lib)}


# ---------------------------------------------------------------------------
# cell inventory (frozen)
# ---------------------------------------------------------------------------


def cell_inventory():
    cells = []
    for mi, mix in enumerate(MIX_GRID):
        for comp in COMPOSITIONS:
            for arm in FULL_ARMS + REDUCED_ARMS:
                n = N_REDUCED if arm in REDUCED_ARMS else N_FULL
                for s in STREAM_SEEDS:
                    cells.append({"arm": arm, "mix_idx": mi, "mix": mix,
                                  "composition": comp, "seed": s, "n": n,
                                  "null_seed": None})
            for arm in NULL_ARMS:
                # nulls: full horizon, every mix, every null seed, ONE stream seed
                for ns in NULL_SEEDS:
                    cells.append({"arm": arm, "mix_idx": mi, "mix": mix,
                                  "composition": comp, "seed": STREAM_SEEDS[0],
                                  "n": N_FULL, "null_seed": ns})
    return cells


def lib_key(arm, null_seed):
    return arm if null_seed is None else "%s#%d" % (arm, null_seed)


# ---------------------------------------------------------------------------
# entry points
# ---------------------------------------------------------------------------


def preflight(out):
    """Harness validation, both hard gates, the reduced-arm derivation and the library
    pickle -- all before any scored cell runs.

    The pickle exists so 984 cells do not each repay a deterministic 253,779,299-unit
    acquisition (~8 min each). It is written by this preflight on the compute host and
    read only by this study's own cells, which verify its sha256 against the preflight
    receipt before loading; it never crosses a trust boundary.
    """
    res = {"schema": SCHEMA, "phase": "preflight", "terminals": list(TERMINALS),
           "n_full": N_FULL, "n_reduced": N_REDUCED,
           "horizon_ladder": list(HORIZON_LADDER), "mix_grid": list(MIX_GRID)}
    res["selection_mirror_ok"] = validate_selection_mirror(__import__("fna4").INDEX)
    res["smoke_solves"] = all(solve_task(t).get("solved")
                              for t in R.acquisition_stream()[:2] + R.test_stream()[:2])
    if not (res["selection_mirror_ok"] and res["smoke_solves"]):
        res["terminal"] = \
            "CANNOT_CHECK_SELECTION_MIRROR_DISAGREES_WITH_PRODUCTION_INDEX"
        (out / "RV8_PREFLIGHT.json").write_text(
            json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
        return res

    # reduced-arm derivation, recomputed from the frozen deltas (never asserted by hand)
    derived = []
    for arm, d in sorted(FROZEN_DELTAS.items()):
        worst = None
        for mix in MIX_GRID:
            for comp in COMPOSITIONS:
                t = mix_targets(mix, comp)
                sv = -(t["F2"] * d["F2"] + t["F1"] * d["F1"] + t["F3"] * d["F3"])
                worst = sv if worst is None else max(worst, sv)
        derived.append({"arm": arm, "max_saving_per_task_over_grid": worst,
                        "reduced": worst < 0})
    res["reduced_arm_derivation"] = derived
    res["reduced_arms_frozen"] = list(REDUCED_ARMS)
    res["reduced_arms_derivation_agrees"] = sorted(
        [r["arm"] for r in derived if r["reduced"]]) == sorted(REDUCED_ARMS)

    libs, gates = {}, {}
    for arm in ARMS:
        for ns in (NULL_SEEDS if arm in NULL_ARMS else (None,)):
            t0 = time.time()
            macros, acq, registry, _cg, prof = acquire(arm, ns)
            ok, detail = acquisition_gate(arm, acq)
            key = lib_key(arm, ns)
            gates[key] = {"ok": ok, "detail": detail, "sec": time.time() - t0,
                          "library_size": len(macros), "acquisition_work": acq,
                          "null_profile": prof}
            libs[key] = (macros, registry)
    res["acquisition_gate"] = gates
    res["acquisition_gate_all_ok"] = all(g["ok"] for g in gates.values())
    if not res["acquisition_gate_all_ok"]:
        res["terminal"] = "CANNOT_CHECK_ACQUISITION_DRIFT"
        (out / "RV8_PREFLIGHT.json").write_text(
            json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
        return res

    blob = pickle.dumps(libs, protocol=4)
    (out / "RV8_LIBRARIES.pkl").write_bytes(blob)
    res["libraries_pkl_sha256"] = hashlib.sha256(blob).hexdigest()
    res["cells_total"] = len(cell_inventory())
    (out / "RV8_PREFLIGHT.json").write_text(
        json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
    return res


def replicate(out):
    """Determinism gate against a frozen SCORED receipt: rebuild FNA-4's repeat-rate
    sweep r=0 point and require exact reproduction. This certifies that the ~6,123
    projection and this study's numbers come from the same machine.

    It also isolates the projection's stream construction. FNA-4's builder fills its
    uncovered quota from ``_f1_param_space()`` in PRODUCT ORDER, so at r=0 the twelve
    F1 tasks are near-identical draws from one corner of a 648-tuple space. The same
    library is then run over a natural-draw stream at the same mix and length, and both
    numbers are reported side by side."""
    res = {"schema": SCHEMA, "phase": "replicate_frozen_sweep_r0"}
    macros = L.learn_stitch([solve_task(t, collect_all=True)
                             for t in R.acquisition_stream()], Work())
    tasks = R.build_sweep_streams(macros, 0.0, 0)
    no_w = arm_w = hits = 0
    for t in tasks:
        no_w += solve_task(t)["work"]["total_units"]
        rr = solve_task(t, macros=macros)
        arm_w += rr["work"]["total_units"]
        hits += rr["macro_hits"]
    obs = {"no_library_total": no_w, "with_library_test_work": arm_w,
           "saving": no_w - arm_w, "macro_hits": hits, "n": len(tasks)}
    res["observed"] = obs
    res["expected"] = FROZEN_SWEEP_R0
    res["exact"] = all(obs[k] == FROZEN_SWEEP_R0[k]
                       for k in ("no_library_total", "with_library_test_work",
                                 "saving", "macro_hits"))
    if not res["exact"]:
        res["terminal"] = "CANNOT_CHECK_FROZEN_SWEEP_REPLICATION_DRIFT"

    mi = MIX_GRID.index(0.50)
    nat = family_sequence(0.50, "f1_only", 24)
    nno = narm = nhits = 0
    for pos, fam in enumerate(nat):
        t = stream_task(mi, "f1_only", 0, pos, fam)
        nno += solve_task(t)["work"]["total_units"]
        rr = solve_task(t, macros=macros)
        narm += rr["work"]["total_units"]
        nhits += rr["macro_hits"]
    res["natural_draw_same_mix_n24"] = {
        "no_library_total": nno, "with_library_test_work": narm,
        "saving": nno - narm, "saving_per_task": (nno - narm) / 24.0,
        "macro_hits": nhits,
        "note": "same library, same 12F1+12F2 mix, same length; natural draws instead "
                "of product-order forced parameter tuples"}
    (out / "RV8_REPLICATION.json").write_text(
        json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
    return res


def cell(idx, out):
    cells = cell_inventory()
    c = dict(cells[idx])
    pf = json.loads((out / "RV8_PREFLIGHT.json").read_text())
    blob = (out / "RV8_LIBRARIES.pkl").read_bytes()
    if hashlib.sha256(blob).hexdigest() != pf["libraries_pkl_sha256"]:
        raise SystemExit("CANNOT_CHECK_ACQUISITION_DRIFT: library pickle sha mismatch")
    key = lib_key(c["arm"], c["null_seed"])
    macros, registry = pickle.loads(blob)[key]
    _learner, _gran, use_cegis, _n = ARM_SPEC[c["arm"]]
    fams = family_sequence(c["mix"], c["composition"], c["n"])
    gate = pf["acquisition_gate"][key]
    c.update({"schema": SCHEMA, "cell_index": idx,
              "acquisition_full_units": gate["acquisition_work"]["total_units"],
              "acquisition_marginal_units": gate["acquisition_work"]["learner_steps"],
              "acquisition_work": gate["acquisition_work"],
              "family_seq_counts": dict((f, fams.count(f)) for f in FAMILY_ORDER),
              "family_seq_sha256": hashlib.sha256(
                  "".join(fams).encode("utf-8")).hexdigest(),
              "libraries_pkl_sha256": pf["libraries_pkl_sha256"],
              "complete": False})
    path = out / "cells" / ("cell_%05d.json.gz" % idx)
    path.parent.mkdir(parents=True, exist_ok=True)

    def write(row, complete):
        c["per_task"] = row
        c["complete"] = complete
        c["tasks_done"] = len(row["units"])
        with gzip.open(str(path) + ".tmp", "wt") as fh:
            json.dump(c, fh, sort_keys=True, default=str)
        Path(str(path) + ".tmp").replace(path)

    def on_chunk(units, capped, hits, misf, libn):
        write({"units": list(units), "capped": list(capped),
               "macro_hits": list(hits), "misfires": list(misf),
               "library_size_final": libn}, False)

    t0 = time.time()
    row = run_stream(c["arm"], macros, registry, use_cegis, fams, c["mix_idx"],
                     c["composition"], c["seed"], on_chunk=on_chunk)
    c["sec"] = time.time() - t0
    write(row, True)
    return c


def main(argv):
    mode = argv[1]
    if mode == "inventory":
        print(json.dumps({"cells_total": len(cell_inventory())}))
        return
    out = Path(argv[-1]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    if mode == "preflight":
        r = preflight(out)
        print(json.dumps({k: v for k, v in r.items()
                          if k not in ("acquisition_gate", "reduced_arm_derivation")},
                         indent=1, default=str))
    elif mode == "replicate":
        print(json.dumps(replicate(out), indent=1, default=str))
    elif mode == "cell":
        r = cell(int(argv[2]), out)
        print(json.dumps({"cell_index": r["cell_index"], "arm": r["arm"],
                          "mix": r["mix"], "composition": r["composition"],
                          "seed": r["seed"], "null_seed": r["null_seed"],
                          "n": r["n"], "sec": r["sec"],
                          "total_units": sum(r["per_task"]["units"]),
                          "capped": sum(r["per_task"]["capped"])}, default=str))
    else:
        raise SystemExit("unknown mode %r" % mode)


if __name__ == "__main__":
    main(sys.argv)
