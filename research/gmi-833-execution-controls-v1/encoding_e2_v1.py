#!/usr/bin/env python3
"""Encoding E2: a syntactically disjoint rule-list encoding of the #901 universe.

Registered in FREEZE_V1.md (D-X2).  Written independently of the #901 table
encoding E1 and of every other module of this package: it imports nothing but
the standard library, never reads an integer truth table, and scores each
candidate with its own symbolic interpreter.

Surface syntax (disjoint from E1's integer tables and `q%05d` ids):

* state symbols  P, R        (the register alphabet)
* mode symbols   U, V        (U: emit the current symbol; V: emit the previous one)
* data symbols   a, b        (input and output alphabet)
* a candidate is a rule list: `(state, mode, input) -> next state` rules plus
  `(state, mode, input) -> output` rules (stateful), or `(mode, input) -> output`
  rules (stateless);
* rules are listed in Gray-code address order and rule lists are enumerated
  in Gray-code order (consecutive candidates differ in exactly one rule);
* surface ids are `W` followed by four base-26 capital letters; the stateful
  block is enumerated before the stateless block.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import product
from typing import Dict, List, Tuple

STATES = ("P", "R")
MODES = ("U", "V")
DATA = ("a", "b")
SURFACE_ALPHABET = ("P", "R", "U", "V", "a", "b")
SURFACE_ID_PATTERN = "W[A-Z]{4}"
STATEFUL_COUNT = 256 * 256
STATELESS_COUNT = 16
CENSUS = STATEFUL_COUNT + STATELESS_COUNT
WORDS = tuple(product(DATA, repeat=3))


def gray(n: int) -> int:
    return n ^ (n >> 1)


def gray_inverse(g: int) -> int:
    n = 0
    while g:
        n ^= g
        g >>= 1
    return n


GRAY_ADDRESSES_3 = tuple(gray(i) for i in range(8))
GRAY_ADDRESSES_2 = tuple(gray(i) for i in range(4))


def key3(address: int) -> Tuple[str, str, str]:
    """E2's own 3-bit address layout: bit2 = mode, bit1 = state, bit0 = input."""
    return (STATES[(address >> 1) & 1], MODES[(address >> 2) & 1], DATA[address & 1])


def key2(address: int) -> Tuple[str, str]:
    """E2's 2-bit address layout: bit1 = mode, bit0 = input."""
    return (MODES[(address >> 1) & 1], DATA[address & 1])


def rule_list_3(code: int, alphabet: Tuple[str, str]) -> Tuple[Tuple[Tuple[str, str, str], str], ...]:
    """Rule i (in Gray address order) maps key3(GRAY_ADDRESSES_3[i]) to alphabet[bit i of code]."""
    return tuple((key3(GRAY_ADDRESSES_3[i]), alphabet[(code >> i) & 1]) for i in range(8))


def rule_list_2(code: int) -> Tuple[Tuple[Tuple[str, str], str], ...]:
    return tuple((key2(GRAY_ADDRESSES_2[i]), DATA[(code >> i) & 1]) for i in range(4))


def surface_id(j: int) -> str:
    if not 0 <= j < 26 ** 4:
        raise ValueError("surface index out of range")
    letters = []
    for _ in range(4):
        letters.append(chr(ord("A") + j % 26))
        j //= 26
    return "W" + "".join(reversed(letters))


def candidate(j: int) -> Dict[str, object]:
    """The rule-list candidate with enumeration index j."""
    if j < STATEFUL_COUNT:
        return {"surface_id": surface_id(j), "state_symbols": STATES,
                "step_rules": rule_list_3(gray(j >> 8), STATES),
                "emit_rules": rule_list_3(gray(j & 255), DATA)}
    if j < CENSUS:
        return {"surface_id": surface_id(j), "state_symbols": (), "step_rules": (),
                "emit_rules": rule_list_2(gray(j - STATEFUL_COUNT))}
    raise ValueError("candidate index out of range")


def state_width(cand: Dict[str, object]) -> int:
    """Register width in bits: log2 of the number of state symbols (0 or 1 here)."""
    n = len(cand["state_symbols"])  # type: ignore[arg-type]
    return 0 if n <= 1 else (n - 1).bit_length()


def _score_stateless(emit: Dict[Tuple[str, str], str]) -> Tuple[int, int]:
    errs = {"U": 0, "V": 0}
    for mode in MODES:
        for word in WORDS:
            for t in (1, 2):
                out = emit[(mode, word[t])]
                want = word[t] if mode == "U" else word[t - 1]
                if out != want:
                    errs[mode] += 1
    return errs["U"], errs["V"]


def evaluate_census(delay_error_scale: Fraction = Fraction(1), drop: Tuple[int, ...] = ()) -> List[Tuple[str, int, Fraction, Fraction]]:
    """(surface_id, state_width, now_errors, lag_errors) for every candidate, in E2 order.

    `delay_error_scale` and `drop` exist only to build the registered hostiles
    H2b (a cost-mutating evaluator) and H2a (an alleged encoding that silently
    deletes candidates); the registered E2 uses the defaults.
    """
    scale = Fraction(delay_error_scale)
    width = (len(STATES) - 1).bit_length()
    emit_tables = [dict(rule_list_3(gray(lo), DATA)) for lo in range(256)]
    out: List[Tuple[str, int, Fraction, Fraction]] = []
    for hi in range(256):
        step = dict(rule_list_3(gray(hi), STATES))
        # the scored keys of every episode under this step rule list
        scored: List[Tuple[str, Tuple[str, str, str], str]] = []
        for mode in MODES:
            for word in WORDS:
                st = STATES[0]
                for t, sym in enumerate(word):
                    key = (st, mode, sym)
                    if t >= 1:
                        scored.append((mode, key, sym if mode == "U" else word[t - 1]))
                    st = step[key]
        for lo in range(256):
            j = hi * 256 + lo
            if j in drop:
                continue
            emit = emit_tables[lo]
            now = lag = 0
            for mode, key, want in scored:
                if emit[key] != want:
                    if mode == "U":
                        now += 1
                    else:
                        lag += 1
            out.append((surface_id(j), width, Fraction(now), Fraction(lag) * scale))
    for k in range(STATELESS_COUNT):
        j = STATEFUL_COUNT + k
        if j in drop:
            continue
        now, lag = _score_stateless(dict(rule_list_2(gray(k))))
        out.append((surface_id(j), 0, Fraction(now), Fraction(lag) * scale))
    return out
