#!/usr/bin/env python3
"""Route A: the registered #901 execution substrate and its grammar/ecology variants.

The #901 package `gmi-833-heldout-20-transitions-v1` is reused, not rebuilt:
its frozen case grid, its full-enumeration searcher (S1) and its
risk-frontier branch-and-bound searcher (S2) are loaded by file path.  This
module adds only what #859 needs on top of that substrate:

* the grammar variants of D-X1 (the positive grammar `G+`, the in-place
  state-register ablation `G-`, and the registered hostiles H1a-H1d), each
  evaluated by one factorised exact evaluator whose `G+` risk histogram is
  checked against #901's own full enumeration;
* the non-K capacity descriptor `D(G)` and the ecology descriptor `Ec(E)`;
* exact outcomes per registered world, computed from the rho projection.

Canonical projection: rho(c) = (s, en, ed), with en/ed exact integer error
counts over the scored steps.  Resource vector order: r(c) = (en, ed, s).
No floating point anywhere; stdlib only.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
import importlib.util
from itertools import product
from math import gcd
from pathlib import Path
import sys
from typing import Any, Dict, Iterable, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
H901_DIR = RESEARCH / "gmi-833-heldout-20-transitions-v1"
NS855_DIR = RESEARCH / "gmi-833-no-smuggling-audit-v1"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError("cannot load %s" % path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# #901 (the frozen case grid plus S1/S2, loaded exactly as #901 loads them)
h901 = _load("gmi859_h901_heldout_transition_v1", H901_DIR / "heldout_transition_v1.py")
full = h901.full          # S1: FULL_ENUMERATION
frontier = h901.frontier  # S2: RISK_FRONTIER_BRANCH_BOUND
CASES = h901.CASES        # (case, p, eta, lambda*, lambda_low, lambda_high)
# #855 (the no-smuggling auditor, consumed as-is)
ns_audit = _load("gmi859_h855_audit_core_v1", NS855_DIR / "audit_core_v1.py")

F = Fraction
STATELESS = "STATELESS"
PERSISTENT = "PERSISTENT_STATE"
PROPERTY_OF_STATE_BITS = {0: STATELESS, 1: PERSISTENT}
CENSUS = 65552
REGISTERED_SEQUENCES = tuple(product((0, 1), repeat=3))
CURRENT, PREVIOUS = "CURRENT", "PREVIOUS"
E_PLUS_TARGETS = (CURRENT, PREVIOUS)
E_MINUS_TARGETS = (CURRENT, CURRENT)
K_MECHANISM = "K_DATA_DEPENDENT_INTERNAL_STATE"
K_FINGERPRINT = "state_data_dependent: next-state table not constant over (S,M,X)"
K_TARGET = "ed < 8"
TIE_RULE = "COMPLETE_ARGMIN_SET"
STOPPING_RULE = "EXHAUSTIVE_FULL_BUDGET"
SHAPE_STATELESS = "OUT_TABLE[address_bits=2;table_bits=4]"
SHAPE_STATEFUL = "NEXT_TABLE[address_bits=3;table_bits=8]+OUT_TABLE[address_bits=3;table_bits=8]+REGISTER[bits=1]"
OPS_STATELESS = ("OUT_LOOKUP", "READ_INPUT", "READ_MODE")
OPS_STATELESS_PREV = ("OUT_LOOKUP", "READ_INPUT", "READ_MODE", "READ_PREV")
OPS_STATEFUL = ("NEXT_LOOKUP", "OUT_LOOKUP", "READ_INPUT", "READ_MODE", "REGISTER_READ", "REGISTER_WRITE")


# --------------------------------------------------------------------------
# registered worlds
# --------------------------------------------------------------------------
def worlds() -> List[Dict[str, Any]]:
    """The 60 registered worlds: per frozen case, the low and high endpoints
    and the exact boundary lambda = lambda* = eta*p/2."""
    out = []
    for case_id, p, eta, thr, low, high in CASES:
        if thr != eta * p / 2 or not (low < thr < high):
            raise ValueError("frozen #901 case grid changed")
        for kind, lam in (("low", low), ("high", high), ("boundary", thr)):
            out.append({"world_id": "c%02d_%s" % (case_id, kind), "case": case_id, "kind": kind,
                        "p": p, "eta": eta, "lambda": lam, "threshold": thr})
    return out


def world_weights(w: Dict[str, Any], scored_per_mode: int = 16) -> Tuple[Fraction, Fraction, Fraction]:
    """Weights on r = (en, ed, s) for J = eta*((1-p)*en/N + p*ed/N) + lambda*s."""
    return (w["eta"] * (1 - w["p"]) / scored_per_mode, w["eta"] * w["p"] / scored_per_mode, w["lambda"])


def claimed_properties(w: Dict[str, Any]) -> Tuple[str, ...]:
    """The frozen #901 phase law lambda* = eta*p/2 (price-conditional)."""
    thr = w["eta"] * w["p"] / 2
    if w["lambda"] < thr:
        return (PERSISTENT,)
    if w["lambda"] > thr:
        return (STATELESS,)
    return (PERSISTENT, STATELESS)


def rho_id(rho: Tuple[int, Any, Any]) -> str:
    s, en, ed = rho
    return "s%sn%sd%s" % (s, en, ed)


# --------------------------------------------------------------------------
# grammar variants (D-X1)
# --------------------------------------------------------------------------
def grammar(grammar_id: str, *, include_stateful: bool = True, ablate_next: bool = False,
            prev_macro: bool = False, sequences: Sequence[Tuple[int, int, int]] = REGISTERED_SEQUENCES,
            mode_targets: Tuple[str, str] = E_PLUS_TARGETS, budget: int | None = None) -> Dict[str, Any]:
    count = 16 + (65536 if include_stateful else 0)
    return {"grammar_id": grammar_id, "include_stateful": include_stateful, "ablate_next": ablate_next,
            "prev_macro": prev_macro, "sequences": tuple(sequences), "mode_targets": tuple(mode_targets),
            "budget": count if budget is None else budget}


G_PLUS = grammar("G_PLUS")
G_MINUS = grammar("G_MINUS", ablate_next=True)
H1A_CAPACITY = grammar("H1A_CAPACITY_DELETE_STATEFUL", include_stateful=False)
H1B_MACRO = grammar("H1B_MACRO_PREV", ablate_next=True, prev_macro=True)
H1C_SEQUENCES = grammar("H1C_HALVED_SEQUENCE_SET", ablate_next=True,
                        sequences=tuple(x for x in REGISTERED_SEQUENCES if x[0] == 0))
H1D_BUDGET = grammar("H1D_HALVED_BUDGET", ablate_next=True, budget=65552 // 2)
G_PLUS_IN_E_MINUS = grammar("G_PLUS_IN_E_MINUS", mode_targets=E_MINUS_TARGETS)


def _bit(table: int, index: int) -> int:
    return (table >> index) & 1


def _scored_steps(next_table: int | None, g: Dict[str, Any]) -> List[Tuple[int, int, int, int]]:
    """(mode, address-or-code, target, prev) for every scored step, in episode order.

    For a stateful candidate the address is 4s+2m+x (the #901 table layout),
    with the state trajectory driven by `next_table`.  For a stateless
    candidate `next_table` is None and the address is 2m+x, or 2+prev in mode 1
    when the H1b PREV macro is wired in.
    """
    out = []
    for mode in (0, 1):
        for seq in g["sequences"]:
            state = 0
            for t, x in enumerate(seq):
                if next_table is None:
                    addr = 2 * mode + (seq[t - 1] if (g["prev_macro"] and mode == 1 and t >= 1) else x)
                else:
                    addr = 4 * state + 2 * mode + x
                if t >= 1:
                    target = x if g["mode_targets"][mode] == CURRENT else seq[t - 1]
                    out.append((mode, addr, target, seq[t - 1]))
                if next_table is not None:
                    state = _bit(next_table, addr)
    return out


def evaluate_grammar(g: Dict[str, Any]) -> List[Tuple[str, int, int, int, bool, int | None]]:
    """Exact census of a grammar variant.

    Returns (surface_id, s, en, ed, k_fingerprint, scored_signature) per
    candidate in #901 enumeration order; the signature (an int over the scored
    output bits) is computed for K-free candidates only.
    """
    out: List[Tuple[str, int, int, int, bool, int | None]] = []
    steps = _scored_steps(None, g)
    for table in range(16):
        en = ed = 0
        sig = 0
        for i, (mode, addr, target, _prev) in enumerate(steps):
            y = _bit(table, addr)
            sig |= y << i
            if y != target:
                if mode == 0:
                    en += 1
                else:
                    ed += 1
        out.append(("q%05d" % table, 0, en, ed, False, sig))
    if not g["include_stateful"]:
        return out
    cache: Dict[int, Tuple[List[Tuple[int, int, int, int]], List[List[List[int]]]]] = {}
    for next_table in range(256):
        effective = 0 if g["ablate_next"] else next_table
        if effective not in cache:
            st = _scored_steps(effective, g)
            cnt = [[[0, 0] for _ in range(8)] for _ in range(2)]
            for mode, addr, target, _prev in st:
                cnt[mode][addr][target] += 1
            cache[effective] = (st, cnt)
        st, cnt = cache[effective]
        k = effective not in (0, 255)
        c0, c1 = cnt
        for out_table in range(256):
            en = ed = 0
            for addr in range(8):
                y = (out_table >> addr) & 1
                en += c0[addr][1 - y]
                ed += c1[addr][1 - y]
            sig = None
            if not k:
                sig = 0
                for i, (_m, addr, _t, _p) in enumerate(st):
                    sig |= ((out_table >> addr) & 1) << i
            out.append(("q%05d" % (16 + next_table * 256 + out_table), 1, en, ed, k, sig))
    return out


def scored_per_mode(g: Dict[str, Any]) -> int:
    return 2 * len(g["sequences"])


def descriptor(g: Dict[str, Any], census: Sequence[Tuple[str, int, int, int, bool, int | None]]) -> Dict[str, Any]:
    """The frozen D-X1 non-K capacity descriptor D(G), computed from the grammar."""
    shapes: Counter = Counter()
    shapes[SHAPE_STATELESS] += 16
    if g["include_stateful"]:
        shapes[SHAPE_STATEFUL] += 65536
    width = 2 * scored_per_mode(g)
    sigs = sorted({c[5] for c in census if not c[4]})
    return {
        "candidate_count": len(census),
        "primitive_envelope": [[k, v] for k, v in sorted(shapes.items())],
        "non_k_operator_inventory": sorted(operators(g)),
        "evaluator_id": "GMI901_BINARY_TRANSDUCER_EXACT_EVALUATOR:initial_state=0:scored_steps=1,2:"
                        "error_normalizer=%d:eta_scale=1:mode_targets=%s" % (scored_per_mode(g), ",".join(g["mode_targets"])),
        "sequence_set": ["".join(map(str, s)) for s in sorted(g["sequences"])],
        "budget": g["budget"],
        "tie_rule": TIE_RULE,
        "stopping_rule": STOPPING_RULE,
        "representable_k_free_behaviour_set": [format(s, "0%dx" % ((width + 3) // 4)) for s in sigs],
    }


def operators(g: Dict[str, Any]) -> List[str]:
    ops = set(OPS_STATELESS_PREV if g["prev_macro"] else OPS_STATELESS)
    if g["include_stateful"]:
        ops |= set(OPS_STATEFUL)
    return sorted(ops)


def k_free_multiplicity(census: Sequence[Tuple[str, int, int, int, bool, int | None]]) -> Dict[str, int]:
    c = Counter(x[5] for x in census if not x[4])
    return {"classes": len(c), "min_per_class": min(c.values()), "max_per_class": max(c.values()),
            "total_k_free": sum(c.values())}


def compress(census: Iterable[Tuple[Any, ...]]) -> Dict[Tuple[int, int, int], int]:
    """rho-quotient: (s, en, ed) -> multiplicity."""
    return dict(sorted(Counter((c[1], c[2], c[3]) for c in census).items()))


def outcome(points: Dict[Tuple[int, Any, Any], int], w: Dict[str, Any], per_mode: int = 16,
            weights: Tuple[Fraction, Fraction, Fraction] | None = None) -> Dict[str, Any]:
    """Exact argmin over the rho-quotient at one world."""
    a, b, c = weights if weights is not None else world_weights(w, per_mode)
    # exact: scale the weights to integers by their common denominator (order-preserving);
    # rho coordinates are integers, or integral Fractions for the E2 tables
    den = 1
    for x in (a, b, c):
        d = Fraction(x).denominator
        den = den * d // gcd(den, d)
    ia, ib, ic = int(a * den), int(b * den), int(c * den)
    integral = all(Fraction(r[1]).denominator == 1 and Fraction(r[2]).denominator == 1 for r in points)
    if integral:
        vals = {rho: ia * int(rho[1]) + ib * int(rho[2]) + ic * int(rho[0]) for rho in points}
    else:
        vals = {rho: ia * rho[1] + ib * rho[2] + ic * rho[0] for rho in points}
    low = min(vals.values())
    best = Fraction(low) / den
    win = sorted(rho for rho, v in vals.items() if v == low)
    return {"best": best, "winners": win,
            "properties": tuple(sorted({PROPERTY_OF_STATE_BITS[r[0]] for r in win}))}


# --------------------------------------------------------------------------
# ecology twin (D-X1E)
# --------------------------------------------------------------------------
def ecology(ecology_id: str, *, mode_targets: Tuple[str, str], sequences=REGISTERED_SEQUENCES,
            eta_scale: Fraction = F(1)) -> Dict[str, Any]:
    return {"ecology_id": ecology_id, "mode_targets": tuple(mode_targets), "sequences": tuple(sequences),
            "eta_scale": eta_scale}


E_PLUS = ecology("E_PLUS", mode_targets=E_PLUS_TARGETS)
E_MINUS = ecology("E_MINUS", mode_targets=E_MINUS_TARGETS)
E_MINUS_HALVED = ecology("E_MINUS_HOSTILE_HALVED_SEQUENCES", mode_targets=E_MINUS_TARGETS,
                         sequences=tuple(x for x in REGISTERED_SEQUENCES if x[0] == 0))
E_MINUS_ETA = ecology("E_MINUS_HOSTILE_ETA_RESCALED", mode_targets=E_MINUS_TARGETS, eta_scale=F(2))


def ecology_descriptor(e: Dict[str, Any]) -> Dict[str, Any]:
    n = 2 * len(e["sequences"])
    return {
        "sequence_set": ["".join(map(str, s)) for s in sorted(e["sequences"])],
        "mode_count": 2,
        "scoring_events": [n, n],
        "mixing_parameter_p": sorted({str(c[1]) for c in CASES}, key=Fraction),
        "evaluator_id": "GMI901_BINARY_TRANSDUCER_EXACT_EVALUATOR:initial_state=0:scored_steps=1,2:"
                        "error_normalizer=%d:eta_scale=%s" % (n, e["eta_scale"]),
        "tie_rule": TIE_RULE,
        "budget": CENSUS,
    }
