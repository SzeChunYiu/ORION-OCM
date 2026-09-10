"""Kernel-ablation independence, demonstrated on dynamics (issue #296 sec.2, sec.17 cond.2).

The frozen contract ships kernels.assert_independent_ablation, whose own
docstring concedes it is a "contract check on spec, not dynamics proof". It
returns ok=True for every input. run_ebf0.gate() counts only rows with
status == "FAIL", so that row can never contribute a failure, and sec.17
condition 2 is currently reported closed on an instrument that cannot fail.

This module (a) records that defect empirically and (b) replaces it with an
instrument that CAN fail:

  EFFECT       ablating the kernel changes the trajectory on >=1 world
  DEAD         ablating it changes nothing on any enumerated world
  UNRUNNABLE   ablating it raises -- the ablation is not independent
  NO-ALARM     ablating nothing must reproduce byte-identical trajectories
"""
from __future__ import annotations

import itertools
from typing import Iterable

import worlds as W

STATUS_EFFECT = "EFFECT"
STATUS_DEAD = "DEAD_KERNEL_NO_TRAJECTORY_EFFECT"
STATUS_UNRUNNABLE = "ABLATION_NOT_INDEPENDENT_RAISED"
CANNOT_CHECK_NO_WORLDS = "CANNOT_CHECK_NO_WORLDS_ENUMERATED"


def probe_frozen_checker(kernels_mod) -> dict:
    """Empirical receipt that the frozen ablation checker cannot fail."""
    all_on = {k: True for k in kernels_mod.KERNEL_NAMES}
    cases = {
        "identical_specs": (all_on, dict(all_on)),
        "one_bit_diff": (all_on, {**all_on, "K_social": False}),
        "five_bit_diff": (all_on, {**all_on, "K_social": False,
                                   "K_inherit": False, "K_mut": False,
                                   "K_world": False, "K_assemble": False}),
        "all_off": (all_on, {k: False for k in kernels_mod.KERNEL_NAMES}),
        "garbage_keys": ({"NOT_A_KERNEL": False}, {"ALSO_FAKE": True}),
        "empty_vs_empty": ({}, {}),
    }
    seen, rows = set(), []
    for name, (a, b) in cases.items():
        r = kernels_mod.assert_independent_ablation(a, b)
        seen.add(bool(r.get("ok")))
        rows.append({"case": name, "n_diffs": r.get("n_diffs"),
                     "ok": r.get("ok")})
    return {
        "instrument": "kernels.assert_independent_ablation",
        "cases": rows,
        "distinct_ok_values": sorted(seen),
        "can_fail": False in seen,
        "verdict": ("INSTRUMENT_CANNOT_FAIL" if False not in seen
                    else "INSTRUMENT_CAN_FAIL"),
        "gate_consequence": (
            "sec.17 condition 2 (kernel-ablation independence) is reported "
            "closed by run_ebf0.gate() on a row that is structurally "
            "incapable of status FAIL."),
    }


def _sig_or_raise(me_mod, spec, ticks):
    try:
        return W.signature(me_mod, spec, ticks), None
    except Exception as exc:  # ablation must not break unrelated physics
        return None, "%s: %s" % (type(exc).__name__, exc)


def no_alarm_control(me_mod, specs: Iterable[W.WorldSpec],
                     ticks: int = W.DEFAULT_TICKS) -> dict:
    """The clean control that must stay silent: same spec twice, same hash."""
    n, mismatched = 0, []
    for spec in specs:
        a, ea = _sig_or_raise(me_mod, spec, ticks)
        b, eb = _sig_or_raise(me_mod, spec, ticks)
        n += 1
        if ea or eb or a != b:
            mismatched.append({"spec": spec.key(), "a": a, "b": b,
                               "err_a": ea, "err_b": eb})
    return {
        "control": "identical_spec_reruns",
        "n_worlds": n,
        "n_mismatched": len(mismatched),
        "examples": mismatched[:5],
        "silent": (n > 0 and not mismatched),
        "status": ("OK" if n and not mismatched
                   else (CANNOT_CHECK_NO_WORLDS if not n else "FAIL")),
    }


def kernel_effect_matrix(me_mod, specs: Iterable[W.WorldSpec],
                         ticks: int = W.DEFAULT_TICKS) -> dict:
    """For each kernel, flip its bit on every enumerated world and compare.

    Every other kernel bit is held at the world's own value, so the check runs
    across the whole 2^9 ablation lattice rather than one reference config.
    """
    names = list(W.KERNEL_NAMES) + ["inherit_memory"]
    tally = {k: {"n_worlds": 0, "n_changed": 0, "n_unrunnable": 0,
                 "errors": [], "witness": None} for k in names}
    n_specs = 0
    for spec in specs:
        n_specs += 1
        base_sig, base_err = _sig_or_raise(me_mod, spec, ticks)
        for bit, name in enumerate(names):
            flipped = W.WorldSpec(spec.n, spec.genomes, spec.methods,
                                  spec.social, spec.leak, spec.regime,
                                  spec.kernel_id ^ (1 << bit), spec.seed)
            alt_sig, alt_err = _sig_or_raise(me_mod, flipped, ticks)
            t = tally[name]
            t["n_worlds"] += 1
            if base_err or alt_err:
                t["n_unrunnable"] += 1
                if len(t["errors"]) < 3:
                    t["errors"].append({"spec": spec.key(),
                                        "err": base_err or alt_err})
                continue
            if alt_sig != base_sig:
                t["n_changed"] += 1
                if t["witness"] is None:
                    t["witness"] = {"spec": spec.key(),
                                    "kernel_on": base_sig,
                                    "kernel_flipped": alt_sig}
    rows = []
    for name in names:
        t = tally[name]
        if t["n_worlds"] == 0:
            status = CANNOT_CHECK_NO_WORLDS
        elif t["n_unrunnable"]:
            status = STATUS_UNRUNNABLE
        elif t["n_changed"] == 0:
            status = STATUS_DEAD
        else:
            status = STATUS_EFFECT
        rows.append({
            "kernel": name, "status": status,
            "n_worlds": t["n_worlds"], "n_changed": t["n_changed"],
            "n_unrunnable": t["n_unrunnable"],
            "change_fraction": (round(t["n_changed"] / t["n_worlds"], 6)
                                if t["n_worlds"] else None),
            "witness": t["witness"], "errors": t["errors"],
        })
    ablatable = [r["kernel"] for r in rows if r["status"] == STATUS_EFFECT]
    dead = [r["kernel"] for r in rows if r["status"] == STATUS_DEAD]
    broken = [r["kernel"] for r in rows if r["status"] == STATUS_UNRUNNABLE]
    return {
        "instrument": "kernel_effect_matrix",
        "n_specs": n_specs, "ticks": ticks, "rows": rows,
        "ablatable_with_effect": ablatable,
        "dead_kernels": dead,
        "not_independently_ablatable": broken,
        "can_fail": True,
        "verdict": ("KERNELS_INDEPENDENTLY_ABLATABLE" if not broken
                    else "ABLATION_INDEPENDENCE_FAILS"),
    }


def lattice_completeness(me_mod, spec: W.WorldSpec,
                         ticks: int = W.DEFAULT_TICKS) -> dict:
    """Every one of the 2^9 kernel combinations must instantiate and run.

    This is the real content of "removable independently without rewriting
    unrelated physics": the ablation space is a product, not a set of blessed
    configurations. A single raise fails the row.
    """
    failures, n_ok, sigs = [], 0, {}
    for kid in range(W.N_KERNEL_SPECS):
        s = W.WorldSpec(spec.n, spec.genomes, spec.methods, spec.social,
                        spec.leak, spec.regime, kid, spec.seed)
        sig, err = _sig_or_raise(me_mod, s, ticks)
        if err:
            if len(failures) < 5:
                failures.append({"kernel_id": kid, "err": err})
        else:
            n_ok += 1
            sigs[kid] = sig
    return {
        "instrument": "lattice_completeness",
        "reference_spec": spec.key(),
        "n_kernel_specs": W.N_KERNEL_SPECS,
        "n_runnable": n_ok, "n_failed": W.N_KERNEL_SPECS - n_ok,
        "failures": failures,
        "n_distinct_trajectories": len(set(sigs.values())),
        "status": "HOLD" if n_ok == W.N_KERNEL_SPECS else "FAIL",
    }


def baseline_effect_matrix(me_mod, n: int, n_conditions: int = 400,
                           ticks: int = W.DEFAULT_TICKS,
                           mode: str = "MULTISET") -> dict:
    """Ablate each kernel FROM THE FULL-PHYSICS BASELINE, not from the lattice.

    Section 2's requirement is that each kernel be removable without rewriting
    unrelated physics. The meaningful test flips one kernel off while every
    other kernel is ON, across many initial conditions. Averaging over the
    whole 2^9 lattice dilutes this: in most lattice cells the world is already
    frozen (K_world and K_senseact off), so nothing can move and every kernel
    looks dead.
    """
    names = list(W.KERNEL_NAMES) + ["inherit_memory"]
    conditions = W.initial_conditions(n, n_conditions, mode)
    tally = {k: {"n": 0, "changed": 0, "unrunnable": 0, "witness": None,
                 "errors": []} for k in names}
    for base_kid in (W.ALL_ON, W.ALL_ON_INHERIT):
        for (g, m, social, leak, regime) in conditions:
            base = W.WorldSpec(n, g, m, social, leak, regime, base_kid)
            base_sig, base_err = _sig_or_raise(me_mod, base, ticks)
            for bit, name in enumerate(names):
                alt = W.WorldSpec(n, g, m, social, leak, regime,
                                  base_kid ^ (1 << bit))
                alt_sig, alt_err = _sig_or_raise(me_mod, alt, ticks)
                t = tally[name]
                t["n"] += 1
                if base_err or alt_err:
                    t["unrunnable"] += 1
                    if len(t["errors"]) < 3:
                        t["errors"].append({"spec": base.key(),
                                            "err": base_err or alt_err})
                elif alt_sig != base_sig:
                    t["changed"] += 1
                    if t["witness"] is None:
                        t["witness"] = {"spec": base.key(),
                                        "baseline_kernel_id": base_kid,
                                        "on": base_sig, "off": alt_sig}
    rows = []
    for name in names:
        t = tally[name]
        if t["n"] == 0:
            status = CANNOT_CHECK_NO_WORLDS
        elif t["unrunnable"]:
            status = STATUS_UNRUNNABLE
        elif t["changed"] == 0:
            status = STATUS_DEAD
        else:
            status = STATUS_EFFECT
        rows.append({"kernel": name, "status": status, "n_worlds": t["n"],
                     "n_changed": t["changed"],
                     "n_unrunnable": t["unrunnable"],
                     "change_fraction": (round(t["changed"] / t["n"], 6)
                                         if t["n"] else None),
                     "witness": t["witness"], "errors": t["errors"]})
    dead = [r["kernel"] for r in rows if r["status"] == STATUS_DEAD]
    broken = [r["kernel"] for r in rows if r["status"] == STATUS_UNRUNNABLE]
    return {
        "instrument": "baseline_effect_matrix",
        "n_org": n, "ticks": ticks,
        "n_conditions": len(conditions),
        "baselines": ["ALL_ON", "ALL_ON_INHERIT"],
        "rows": rows,
        "dead_kernels": dead,
        "not_independently_ablatable": broken,
        "can_fail": True,
        "verdict": ("KERNELS_INDEPENDENTLY_ABLATABLE" if not broken
                    else "ABLATION_INDEPENDENCE_FAILS"),
    }
