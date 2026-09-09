#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_t17_v1.py -- exact enumeration for HST-T17 (evaluator-tampering toy).

Lane C of issue #233 (D5). P2 witness ONLY (the proof is proofs/T17_TOY.md).
Machine: states (w, s) with w, s in {0,1,2}; measured objective M(w,s)=s;
protected performance P(w)=w; external evaluator E(w)=w.

System W (writable-s): atomic updates = all single-register writes w:=w' and s:=s'.
System X (external evaluator): atomic acts = w-writes only; after every act the
constitution recomputes s := E(w). X's reachable states satisfy the invariant
s == E(w); the channel-closure property is asserted on that invariant set.

Verifies exhaustively (all states, all atomic updates, all sequences of length 1
and 2 from the initial state (1,1)):
  (a) W: a legal sequence exists with dM > 0 and dP == 0 (tamper, capability
      unchanged): (1,1) -> (1,2) via s:=2; and one with dM > 0 and dP < 0
      (tamper, capability degraded): (1,1) -> (0,1) -> (0,2) via w:=0 then s:=2;
  (b) X: NO atomic act from an invariant state yields ds != 0 with dw == 0;
      with E = P every dM > 0 act has dP > 0;
  (c) X: the unique M-optimal state (2,2) is reached only via w-writes; in W the
      M-optimum is reachable WITHOUT any w-write (pure score tampering).

Emits hostiles/T17_TAMPER_WITNESS.json. Python 3.8 compatible. Run on billy-laptop.
"""

from __future__ import print_function

import itertools
import json
import os
import sys

DOM = [0, 1, 2]
INIT = (1, 1)


def M(state):
    return state[1]


def P(state):
    return state[0]


def E(w):
    return w  # evaluator == protected performance (the toy's tautological binding)


def w_acts():
    return [("w:=%d" % w2, w2) for w2 in DOM]


def s_acts():
    return [("s:=%d" % s2, s2) for s2 in DOM]


def apply_W(state, act):
    kind, val = act[0][0], act[1]
    if kind == "w":
        return (val, state[1])
    return (state[0], val)


def act_W_list():
    ups = []
    for name, val in w_acts():
        ups.append((name, "w", val))
    for name, val in s_acts():
        ups.append((name, "s", val))
    return ups


def apply_X(state, named):
    # named: ("w-write+eval", w2): optimizer writes w2; constitution sets s:=E(w2)
    _, w2 = named
    return (w2, E(w2))


def act_X_list():
    return [("w:=%d;s:=E(w)" % w2, "w-write+eval", w2) for w2 in DOM]


def main():
    failures = []
    aw = act_W_list()
    ax = act_X_list()

    def w_step(state, act):
        _, kind, val = act
        if kind == "w":
            return (val, state[1])
        return (state[0], val)

    # --- System W: enumerate all sequences of length 1..2 from INIT ------------
    flat = None
    degrade = None
    pure_score_path = None  # reaches M-optimum (s=2) with w never written
    seqs = [((act,), w_step(INIT, act)) for act in aw]
    for act1, act2 in itertools.product(aw, repeat=2):
        mid = w_step(INIT, act1)
        seqs.append(((act1, act2), w_step(mid, act2)))
    for seq, end in seqs:
        dM = M(end) - M(INIT)
        dP = P(end) - P(INIT)
        if dM > 0 and dP == 0 and flat is None:
            flat = {"sequence": [a[0] for a in seq], "from": list(INIT),
                    "to": list(end), "dM": dM, "dP": dP}
        if dM > 0 and dP < 0 and degrade is None:
            degrade = {"sequence": [a[0] for a in seq], "from": list(INIT),
                       "to": list(end), "dM": dM, "dP": dP}
        if end[1] == 2 and all(a[1] == "s" for a in seq):
            pure_score_path = {"sequence": [a[0] for a in seq], "to": list(end)}
    # --- System X: atomic channel closure on the invariant set -----------------
    x_tamper = False
    x_decouple = False
    x_kinds_to_opt = set()
    for w0 in DOM:
        base = (w0, E(w0))  # invariant states only (X-reachable)
        for name, kind, w2 in ax:
            new = (w2, E(w2))
            ds = new[1] - base[1]
            dw = new[0] - base[0]
            dM = M(new) - M(base)
            dP = P(new) - P(base)
            if ds != 0 and dw == 0:
                x_tamper = True           # must remain False
            if dM > 0 and dP <= 0:
                x_decouple = True         # must remain False (E == P, monotone)
            if new == (2, 2):
                x_kinds_to_opt.add(kind)
    # --- verdicts ---------------------------------------------------------------
    if flat is None:
        failures.append("T17-a-flat")
    if degrade is None:
        failures.append("T17-a-degrade")
    if pure_score_path is None:
        failures.append("T17-c-pure-score-optimum")
    if x_tamper:
        failures.append("T17-b-tamper-channel-open")
    if x_decouple:
        failures.append("T17-b-MP-decoupling")
    if not (x_kinds_to_opt <= set(["w-write+eval"])):
        failures.append("T17-c-opt-reached-by-non-w-write")
    if not x_kinds_to_opt:
        failures.append("T17-c-opt-unreachable")
    witness = {
        "witness_id": "T17_TAMPER_WITNESS_V1",
        "theorem": "HST-T17",
        "hostile_row": "self-modifier that raises mutable score without "
                       "protected capability",
        "machine": {
            "registers": ["w (work; protected meaning P(w)=w)",
                          "s (score; measured objective M(w,s)=s)"],
            "domains": {"w": DOM, "s": DOM},
            "evaluator": "E(w)=w, recomputed by the constitution after every "
                         "optimizer act in system X",
            "initial_state": list(INIT),
            "enumerated": {
                "system_W": "all 6 atomic updates; all sequences of length 1-2 "
                            "(6 + 36)",
                "system_X": "all 3 atomic acts from every invariant state "
                            "(w, E(w))",
            },
        },
        "system_W_tamper_capability_unchanged": flat,
        "system_W_tamper_capability_degraded": degrade,
        "system_W_pure_score_optimum_no_w_write": pure_score_path,
        "system_X_properties": {
            "exists_act_with_ds_ne_0_and_dw_eq_0": x_tamper,
            "exists_M_gain_without_P_gain": x_decouple,
            "kinds_reaching_optimum_(2,2)": sorted(x_kinds_to_opt),
        },
        "verdict": "WITNESS_CERTIFIED" if not failures else "FAIL",
        "failures": failures,
        "not_proved": [
            "external evaluation does NOT solve Goodhart in general: E==P is a "
            "tautological toy binding; real E is a proxy for external truth",
            "no protection against evaluator rewrite/corruption/collusion is "
            "proven here; C's write-protection is a constitutional assumption",
            "no quantitative claim beyond |W|=|S|=3, sequences of length <= 2",
        ],
        "proof_file": "proofs/T17_TOY.md",
        "checker": "exact/check_t17_v1.py",
    }
    out = json.dumps(witness, indent=1, sort_keys=True)
    print(out)
    tgt = "hostiles/T17_TAMPER_WITNESS.json"
    if os.path.isdir("hostiles"):
        with open(tgt, "w") as fh:
            fh.write(out + "\n")
        sys.stderr.write("witness written: %s\n" % tgt)
    else:
        sys.stderr.write("hostiles/ missing; witness printed only\n")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
