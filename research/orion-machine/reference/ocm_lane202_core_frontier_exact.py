#!/usr/bin/env python3
"""Lane #202 exact checker: the core-memory-time resource frontier on a tiny,
fully enumerable machine.

Quantity under test (``theory/OCM_LANE_202_TERMINAL_V1.md``):

    C_core*(F; t) = min { description_bits(P) : P solves task family F within
                          time bound t }

where ``description_bits(P) = len(P) * BITS_PER_INSTRUCTION`` and the minimum
is taken over every program of length ``1..L_MAX`` (exhaustive enumeration, no
sampling).  ``C_core*(F; t)`` is ``None`` (reported as ``UNSOLVABLE_WITHIN_CAP``)
when no program of length ``<= L_MAX`` solves ``F`` within ``t``; ``None`` is a
distinct value, never ``0`` and never a pass.

Machine model (deliberately tiny so the enumeration is exhaustive):

* input register ``x in {0,1,2,3}``; accumulator ``a in {0..7}`` (arithmetic
  mod 8); program counter ``pc``; the run starts at ``(x, a=0, pc=0)``.
* instruction = (opcode, 2-bit operand), 7 opcodes x 4 operands = 28 distinct
  pairs, so ``BITS_PER_INSTRUCTION = ceil(log2 28) = 5``:

    OUT c   : a := c; halt (output a)
    ADD c   : a := (a + c) mod 8; pc += 1
    REP c   : if x > 0: a := (a + c) mod 8; x := x - 1; pc unchanged (loop)
              else: pc += 1
    DEC     : x := max(x - 1, 0); pc += 1
    JZ k    : if x == 0: pc := k else pc += 1
    JMP k   : pc := k
    HALT    : halt (output a)

  ``DEC`` and ``HALT`` ignore their operand but still carry it in the encoding
  (each has four encodings, all counted, so the 28-pair alphabet and the 5-bit
  cost are honest).  Running off the end of the program halts.  A run that has
  not halted after ``t`` executed instructions FAILS the time bound ``t``.
* a task family ``F`` is a finite set of (input, required_output) pairs with at
  most one output per input; ``P`` solves ``F`` within ``t`` iff for every
  ``(x, y)`` in ``F`` the run from ``(x, 0, 0)`` halts within ``t`` executed
  instructions with ``a == y``.

What is verified exactly (every count carries its denominator):

1. monotonicity in time: ``C(F; t)`` is non-increasing in ``t`` for every
   registered family and every ``t in 1..T_MAX`` (``None`` ordered as +inf);
2. monotonicity in the family: ``F' subset F`` implies ``C(F'; t) <= C(F; t)``;
3. a genuine trade-off frontier: a registered family whose exact table strictly
   decreases at two or more distinct ``t`` (extended order, ``None`` = +inf) and
   has at least one finite-to-finite strict decrease.  A census over every
   family on the 4-point domain (``9^4 - 1 = 6560`` families) records how many
   have two finite-to-finite decreases within the cap (measured: none at
   ``L_MAX = 4``; the finite trade-off available at this cap is one level deep);
4. exact failure of naive subadditivity: registered ``F1, F2`` on disjoint
   domains with ``C(F1 u F2; t) > C(F1; t) + C(F2; t)`` (witness triple with
   exact values), and a pair/time where subadditivity holds, found by the same
   code path;
5. infeasibility is a distinct value: every ``(F, t)`` unsolvable within the
   cap is listed with the cap stated.

No-alarm control: two independent computations of ``C(F; t)`` must agree on
every registered ``(F, t)`` -- (i) full enumeration with a signature cache and
``simulate_a``; (ii) iterative deepening by length that stops at the first
solvable length, using the separately written ``simulate_b`` and no cache.

Planted failures (each must fire in the same call as the no-alarm cases):

* ``P1`` a claimed table for ``DOUBLE`` off by one instruction at one ``t`` is
  rejected against the enumerated table;
* ``P2`` an inconsistent family (same input, two outputs) is refused with the
  distinct error ``InconsistentFamily``, not reported unsolvable.

Mutation controls (each asserted applied on a concrete witness before the
check runs, then the check must fail for its registered reason):

* ``M1`` simulator that ignores the time bound -> the frontier check fails;
* ``M2`` enumerator that skips every length-2 program (in the iterative
  deepening path) -> the two independent computations disagree;
* ``M3`` description-bits function returning ``len(P)`` instead of bits -> the
  recorded subadditivity witness values change and the assertion on the exact
  registered values fails;
* ``M0`` unmutated -> everything passes.

Exit codes: ``0`` pass, ``1`` a check failed for its registered reason,
``2`` could not check (``CANNOT_CHECK``; never a pass).

Authority: finite toy model only.  Establishes no novelty, priority or
architecture claim; the all-size statement is the hand proof in the theory
record (parent-owned Kolmogorov invariance / conservation argument).
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import time
from collections.abc import Callable, Iterable, Sequence

# ----------------------------------------------------------------------------
# Machine constants
# ----------------------------------------------------------------------------

OPCODES: tuple[str, ...] = ("OUT", "ADD", "REP", "DEC", "JZ", "JMP", "HALT")
OUT, ADD, REP, DEC, JZ, JMP, HALT = range(7)
OPERANDS: tuple[int, ...] = (0, 1, 2, 3)
INSTRUCTIONS: tuple[tuple[int, int], ...] = tuple((op, c) for op in range(len(OPCODES)) for c in OPERANDS)
BITS_PER_INSTRUCTION: int = math.ceil(math.log2(len(INSTRUCTIONS)))
MOD: int = 8
INPUTS: tuple[int, ...] = (0, 1, 2, 3)
L_MAX: int = 4
T_MAX: int = 8
UNSOLVABLE = "UNSOLVABLE_WITHIN_CAP"

Program = tuple[tuple[int, int], ...]
RunResult = tuple[bool, int, int]  # (halted, executed_instructions, accumulator)


class CannotCheck(RuntimeError):
    """A check could not be run.  Never reported as a pass."""


class InconsistentFamily(ValueError):
    """A 'family' assigns two outputs to one input.  Distinct from unsolvable."""


class ClaimedTableRejected(AssertionError):
    """A claimed exact table disagrees with the enumerated table."""


# ----------------------------------------------------------------------------
# Two independently written simulators
# ----------------------------------------------------------------------------

def simulate_a(program: Program, x: int, budget: int) -> RunResult:
    """Simulator A: if/elif chain.  Returns (halted, steps, a).

    A run halts when OUT/HALT executes or pc leaves the program.  If ``budget``
    instructions have executed and pc is still inside the program the run has
    not halted within the bound."""
    a = 0
    pc = 0
    steps = 0
    n = len(program)
    while True:
        if pc >= n:
            return (True, steps, a)
        if steps == budget:
            return (False, steps, a)
        op, c = program[pc]
        steps += 1
        if op == OUT:
            return (True, steps, c)
        if op == HALT:
            return (True, steps, a)
        if op == ADD:
            a = (a + c) % MOD
            pc += 1
        elif op == REP:
            if x > 0:
                a = (a + c) % MOD
                x -= 1
            else:
                pc += 1
        elif op == DEC:
            x = max(x - 1, 0)
            pc += 1
        elif op == JZ:
            pc = c if x == 0 else pc + 1
        elif op == JMP:
            pc = c
        else:  # pragma: no cover - alphabet is closed
            raise CannotCheck(f"unknown opcode {op}")


def _step_b(op: int, c: int, pc: int, a: int, x: int) -> tuple[int, int, int] | tuple[str, int]:
    """One transition of simulator B, written as a pure state function.

    Returns the next ``(pc, a, x)`` or ``("halt", output)``."""
    match op:
        case 0:  # OUT
            return ("halt", c)
        case 6:  # HALT
            return ("halt", a)
        case 1:  # ADD
            return (pc + 1, (a + c) % MOD, x)
        case 2:  # REP
            return (pc, (a + c) % MOD, x - 1) if x > 0 else (pc + 1, a, x)
        case 3:  # DEC
            return (pc + 1, a, x - 1 if x > 0 else 0)
        case 4:  # JZ
            return (c if x == 0 else pc + 1, a, x)
        case 5:  # JMP
            return (c, a, x)
    raise CannotCheck(f"unknown opcode {op}")  # pragma: no cover


def simulate_b(program: Program, x: int, budget: int) -> RunResult:
    """Simulator B: state-tuple + match-based transition function.  Same
    contract as ``simulate_a`` but written separately (no shared code)."""
    state = (0, 0, x)
    for executed in range(budget + 1):
        pc, a, cur_x = state
        if pc >= len(program):
            return (True, executed, a)
        if executed == budget:
            return (False, executed, a)
        nxt = _step_b(program[pc][0], program[pc][1], pc, a, cur_x)
        if nxt[0] == "halt":
            return (True, executed + 1, int(nxt[1]))
        state = nxt  # type: ignore[assignment]
    raise CannotCheck("simulate_b fell through")  # pragma: no cover


def simulate_ignoring_time_bound(program: Program, x: int, budget: int) -> RunResult:
    """M1: a broken simulator that ignores the time bound -- every halting run
    is reported as having executed 0 instructions (``T_MAX`` is only a
    termination guard here)."""
    halted, _steps, a = simulate_a(program, x, T_MAX)
    return (halted, 0, a)


# ----------------------------------------------------------------------------
# Programs, description length, enumerators
# ----------------------------------------------------------------------------

def description_bits(program: Program) -> int:
    return len(program) * BITS_PER_INSTRUCTION


def description_len_not_bits(program: Program) -> int:
    """M3: a broken cost function that returns the instruction count."""
    return len(program)


def format_program(program: Program) -> str:
    return "; ".join(f"{OPCODES[op]} {c}" for op, c in program)


def enumerate_programs(length: int) -> Iterable[Program]:
    return itertools.product(INSTRUCTIONS, repeat=length)


def enumerate_programs_skipping_length_2(length: int) -> Iterable[Program]:
    """M2: a broken enumerator that yields no length-2 program."""
    if length == 2:
        return iter(())
    return enumerate_programs(length)


# ----------------------------------------------------------------------------
# Task families
# ----------------------------------------------------------------------------

class TaskFamily:
    """A finite task family {input -> required output} on a subset of INPUTS."""

    def __init__(self, name: str, pairs: Iterable[tuple[int, int]]) -> None:
        mapping: dict[int, int] = {}
        for x, y in pairs:
            if x not in INPUTS:
                raise ValueError(f"{name}: input {x} outside {INPUTS}")
            if not 0 <= y < MOD:
                raise ValueError(f"{name}: output {y} outside 0..{MOD - 1}")
            if x in mapping and mapping[x] != y:
                raise InconsistentFamily(f"{name}: input {x} required to output both {mapping[x]} and {y}")
            mapping[x] = y
        if not mapping:
            raise ValueError(f"{name}: empty family")
        self.name = name
        self.pairs: tuple[tuple[int, int], ...] = tuple(sorted(mapping.items()))
        self.domain: frozenset[int] = frozenset(mapping)

    def is_subfamily_of(self, other: TaskFamily) -> bool:
        return set(self.pairs) <= set(other.pairs)

    def union(self, other: TaskFamily) -> TaskFamily:
        if self.domain & other.domain:
            raise ValueError(f"{self.name} and {other.name} do not have disjoint domains")
        return TaskFamily(f"{self.name}+{other.name}", self.pairs + other.pairs)

    def as_dict(self) -> dict[str, object]:
        return {"name": self.name, "pairs": [list(p) for p in self.pairs]}


def registered_families() -> tuple[TaskFamily, ...]:
    """Whole families, their half-domain pieces used for subadditivity, and the
    endpoint piece of IDENTITY that carries the trade-off frontier."""
    return (
        TaskFamily("CONST_5", [(x, 5) for x in INPUTS]),
        TaskFamily("IDENTITY", [(x, x) for x in INPUTS]),
        TaskFamily("DOUBLE", [(x, 2 * x) for x in INPUTS]),
        TaskFamily("TRIPLE_MOD8", [(x, (3 * x) % MOD) for x in INPUTS]),
        TaskFamily("IS_ZERO", [(0, 1), (1, 0), (2, 0), (3, 0)]),
        TaskFamily("PARITY", [(x, x % 2) for x in INPUTS]),
        TaskFamily("SUCC", [(x, x + 1) for x in INPUTS]),
        TaskFamily("DOUBLE_LO", [(0, 0), (1, 2)]),
        TaskFamily("DOUBLE_HI", [(2, 4), (3, 6)]),
        TaskFamily("IDENTITY_LO", [(0, 0), (1, 1)]),
        TaskFamily("IDENTITY_HI", [(2, 2), (3, 3)]),
        TaskFamily("IDENTITY_ENDPOINTS", [(0, 0), (3, 3)]),
        TaskFamily("IS_ZERO_ZERO", [(0, 1)]),
        TaskFamily("IS_ZERO_NONZERO", [(1, 0), (2, 0), (3, 0)]),
    )


# ----------------------------------------------------------------------------
# Computation (i): full enumeration with a signature cache
# ----------------------------------------------------------------------------

Signature = tuple[RunResult, ...]


class SignatureCache:
    """signature (per-input run result at budget T_MAX) -> shortest program
    realising it, in enumeration order.  Every ``t <= T_MAX`` is answered from
    this single enumeration."""

    def __init__(
        self,
        simulate: Callable[[Program, int, int], RunResult] = simulate_a,
        enumerate_fn: Callable[[int], Iterable[Program]] = enumerate_programs,
        l_max: int = L_MAX,
        t_max: int = T_MAX,
    ) -> None:
        self.t_max = t_max
        self.l_max = l_max
        self.programs_enumerated = 0
        self.runs_executed = 0
        self.programs_per_length: dict[int, int] = {}
        self.table: dict[Signature, Program] = {}
        for length in range(1, l_max + 1):
            count = 0
            for program in enumerate_fn(length):
                count += 1
                sig = tuple(simulate(program, x, t_max) for x in INPUTS)
                self.runs_executed += len(INPUTS)
                if sig not in self.table:
                    self.table[sig] = program
            self.programs_per_length[length] = count
            self.programs_enumerated += count
        if self.programs_enumerated == 0:
            raise CannotCheck("no programs enumerated")

    def exact_table(self, family: TaskFamily, bits: Callable[[Program], int] = description_bits) -> dict[str, object]:
        """C(F; t) for t = 1..T_MAX with the witness program at each t."""
        best: list[Program | None] = [None] * self.t_max
        for sig, program in self.table.items():
            t_solve = 0
            for x, y in family.pairs:
                halted, steps, out = sig[x]
                if not halted or out != y:
                    t_solve = -1
                    break
                t_solve = max(t_solve, steps)
            if t_solve < 0:
                continue
            for t in range(max(t_solve, 1), self.t_max + 1):
                cur = best[t - 1]
                if cur is None or (len(program), program) < (len(cur), cur):
                    best[t - 1] = program
        return {
            "family": family.name,
            "C_bits": [None if p is None else bits(p) for p in best],
            "witness": [None if p is None else format_program(p) for p in best],
            "unsolvable_t": [t for t, p in enumerate(best, start=1) if p is None],
            "cap": {"L_MAX": self.l_max, "max_bits": self.l_max * BITS_PER_INSTRUCTION, "T_MAX": self.t_max},
        }


# ----------------------------------------------------------------------------
# Computation (ii): iterative deepening by length, separate simulator, no cache
# ----------------------------------------------------------------------------

def iterative_deepening_tables(
    families: Sequence[TaskFamily],
    simulate: Callable[[Program, int, int], RunResult] = simulate_b,
    enumerate_fn: Callable[[int], Iterable[Program]] = enumerate_programs,
    bits: Callable[[Program], int] = description_bits,
    l_max: int = L_MAX,
    t_max: int = T_MAX,
) -> dict[str, object]:
    """For every (F, t): the first length at which some program solves F within
    t, scanning lengths 1, 2, ... and stopping for a family as soon as all its
    t-entries are resolved.  Unresolved entries after L_MAX stay None."""
    best: dict[str, list[int | None]] = {f.name: [None] * t_max for f in families}
    getters = {f.name: [x for x, _ in f.pairs] for f in families}
    required = {f.name: tuple(y for _, y in f.pairs) for f in families}
    programs = 0
    runs = 0
    for length in range(1, l_max + 1):
        unresolved = [f.name for f in families if any(v is None for v in best[f.name])]
        if not unresolved:
            break
        for program in enumerate_fn(length):
            programs += 1
            results = [simulate(program, x, t_max) for x in INPUTS]
            runs += len(INPUTS)
            outs = tuple(r[2] if r[0] else -1 for r in results)
            for name in unresolved:
                idx = getters[name]
                if tuple(outs[i] for i in idx) != required[name]:
                    continue
                t_solve = max(1, max(results[i][1] for i in idx))
                cost = bits(program)
                row = best[name]
                for t in range(t_solve, t_max + 1):
                    if row[t - 1] is None:
                        row[t - 1] = cost
    return {"tables": best, "programs_enumerated": programs, "runs_executed": runs}


# ----------------------------------------------------------------------------
# Ordering helpers (None = +inf)
# ----------------------------------------------------------------------------

def _le(a: int | None, b: int | None) -> bool:
    if b is None:
        return True
    if a is None:
        return False
    return a <= b


def _lt(a: int | None, b: int | None) -> bool:
    return _le(a, b) and a != b


# ----------------------------------------------------------------------------
# The checks
# ----------------------------------------------------------------------------

def check_monotone_in_time(tables: dict[str, dict[str, object]]) -> dict[str, object]:
    comparisons = 0
    violations = []
    for name, row in tables.items():
        c = row["C_bits"]
        for t in range(1, len(c)):
            comparisons += 1
            if not _le(c[t], c[t - 1]):
                violations.append({"family": name, "t": t, "t_plus_1": t + 1, "C_t": c[t - 1], "C_t_plus_1": c[t]})
    return {"comparisons": comparisons, "violations": violations, "holds": comparisons > 0 and not violations}


def check_monotone_in_family(families: Sequence[TaskFamily], tables: dict[str, dict[str, object]]) -> dict[str, object]:
    pairs = [(a, b) for a in families for b in families if a is not b and a.is_subfamily_of(b)]
    comparisons = 0
    violations = []
    for sub, sup in pairs:
        for t in range(1, T_MAX + 1):
            comparisons += 1
            c_sub = tables[sub.name]["C_bits"][t - 1]
            c_sup = tables[sup.name]["C_bits"][t - 1]
            if not _le(c_sub, c_sup):
                violations.append({"sub": sub.name, "sup": sup.name, "t": t, "C_sub": c_sub, "C_sup": c_sup})
    return {
        "subfamily_pairs": [[a.name, b.name] for a, b in pairs],
        "comparisons": comparisons,
        "violations": violations,
        "holds": len(pairs) > 0 and not violations,
    }


def strict_decreases(c: Sequence[int | None]) -> dict[str, list[int]]:
    ext = [t + 1 for t in range(1, len(c)) if _lt(c[t], c[t - 1])]
    fin = [t + 1 for t in range(1, len(c)) if c[t] is not None and c[t - 1] is not None and c[t] < c[t - 1]]
    return {"extended": ext, "finite": fin}


def frontier_census(cache: SignatureCache) -> dict[str, object]:
    """Every family on the 4-point domain: how many show >= 2 finite-to-finite
    strict decreases within the cap?  A measured fact about the cap, with its
    denominator."""
    scanned = 0
    two_finite = []
    for mask in range(1, 1 << len(INPUTS)):
        dom = [x for x in INPUTS if mask >> x & 1]
        for outs in itertools.product(range(MOD), repeat=len(dom)):
            scanned += 1
            fam = TaskFamily("census", zip(dom, outs))
            dec = strict_decreases(cache.exact_table(fam)["C_bits"])
            if len(dec["finite"]) >= 2:
                two_finite.append({"pairs": list(fam.pairs), "t": dec["finite"]})
    return {"families_scanned": scanned, "with_two_finite_strict_decreases": len(two_finite), "examples": two_finite[:5]}


def check_frontier(tables: dict[str, dict[str, object]]) -> dict[str, object]:
    per_family = {}
    qualifying = []
    for name, row in tables.items():
        dec = strict_decreases(row["C_bits"])
        per_family[name] = dec
        if len(dec["extended"]) >= 2 and len(dec["finite"]) >= 1:
            qualifying.append(name)
    witness = None
    if qualifying:
        name = sorted(qualifying)[0]
        witness = {
            "family": name,
            "C_bits": tables[name]["C_bits"],
            "witness_programs": tables[name]["witness"],
            "strict_decrease_t_extended": per_family[name]["extended"],
            "strict_decrease_t_finite": per_family[name]["finite"],
        }
    return {
        "families_examined": len(tables),
        "strict_decreases_per_family": per_family,
        "qualifying_families": sorted(qualifying),
        "witness": witness,
        "holds": witness is not None,
        "convention": "None (UNSOLVABLE_WITHIN_CAP) is ordered as +inf; a qualifying family needs >= 2 strict decreases in that order and >= 1 finite-to-finite strict decrease",
    }


def check_subadditivity(
    families: Sequence[TaskFamily], cache: SignatureCache, bits: Callable[[Program], int] = description_bits
) -> dict[str, object]:
    """Over every unordered pair of registered families with disjoint domains
    and every t: classify C(F1 u F2; t) vs C(F1; t) + C(F2; t)."""
    by_name = {f.name: f for f in families}
    by_pairs = {f.pairs: f.name for f in families}
    tables = {f.name: cache.exact_table(f, bits)["C_bits"] for f in families}
    pairs = [
        (a, b)
        for a, b in itertools.combinations(sorted(families, key=lambda f: f.name), 2)
        if not (a.domain & b.domain)
    ]
    holds: list[dict[str, object]] = []
    fails: list[dict[str, object]] = []
    union_unsolvable: list[dict[str, object]] = []
    indeterminate = 0
    comparisons = 0
    for a, b in pairs:
        u = a.union(b)
        cu = cache.exact_table(u, bits)["C_bits"]
        for t in range(1, T_MAX + 1):
            comparisons += 1
            c1, c2, c12 = tables[a.name][t - 1], tables[b.name][t - 1], cu[t - 1]
            rec = {
                "F1": a.name,
                "F2": b.name,
                "union_registered_as": by_pairs.get(u.pairs),
                "t": t,
                "C_F1": c1,
                "C_F2": c2,
                "C_union": c12,
            }
            if c1 is None or c2 is None:
                indeterminate += 1
            elif c12 is None:
                union_unsolvable.append(rec)
            elif c12 > c1 + c2:
                fails.append(rec)
            else:
                holds.append(rec)
    fails.sort(key=lambda r: (r["t"], r["F1"], r["F2"]))
    holds.sort(key=lambda r: (r["t"], r["F1"], r["F2"]))
    return {
        "disjoint_pairs": len(pairs),
        "comparisons": comparisons,
        "holds_count": len(holds),
        "fails_count": len(fails),
        "union_unsolvable_parts_solvable_count": len(union_unsolvable),
        "indeterminate_count": indeterminate,
        "failure_witness": fails[0] if fails else None,
        "all_failures": fails,
        "holding_witness": holds[0] if holds else None,
        "union_unsolvable_examples": union_unsolvable[:3],
        "found_failure_and_holding_pair": bool(fails) and bool(holds),
        "_family_names": sorted(by_name),
    }


# Exact registered expectation for the subadditivity failure witness (the
# minimal-t, name-ordered failure).  M3 must change these values.
REGISTERED_SUBADDITIVITY_FAILURE: dict[str, object] = {
    "F1": "IS_ZERO_NONZERO",
    "F2": "IS_ZERO_ZERO",
    "t": 2,
    "C_F1": 5,
    "C_F2": 5,
    "C_union": 15,
}


def compare_claimed_table(name: str, claimed: Sequence[int | None], enumerated: Sequence[int | None]) -> dict[str, object]:
    mismatches = [
        {"t": t, "claimed": c, "enumerated": e}
        for t, (c, e) in enumerate(zip(claimed, enumerated, strict=True), start=1)
        if c != e
    ]
    return {"family": name, "entries_compared": len(claimed), "mismatches": mismatches, "rejected": bool(mismatches)}


def unsolvable_report(tables: dict[str, dict[str, object]]) -> dict[str, object]:
    entries = [{"family": n, "t": t} for n, row in tables.items() for t in row["unsolvable_t"]]
    return {
        "value": None,
        "label": UNSOLVABLE,
        "cap": {"L_MAX": L_MAX, "max_bits": L_MAX * BITS_PER_INSTRUCTION, "T_MAX": T_MAX},
        "entries": entries,
        "count": len(entries),
        "denominator": sum(len(r["C_bits"]) for r in tables.values()),
        "fully_unsolvable_families": sorted(n for n, r in tables.items() if len(r["unsolvable_t"]) == T_MAX),
    }


# ----------------------------------------------------------------------------
# Controls
# ----------------------------------------------------------------------------

def no_alarm_agreement(tables_a: dict[str, dict[str, object]], tables_b: dict[str, list[int | None]]) -> dict[str, object]:
    denominator = 0
    agree = 0
    disagreements = []
    for name, row in tables_a.items():
        for t, (va, vb) in enumerate(zip(row["C_bits"], tables_b[name], strict=True), start=1):
            denominator += 1
            if va == vb:
                agree += 1
            else:
                disagreements.append({"family": name, "t": t, "enumeration": va, "iterative_deepening": vb})
    return {"agree": agree, "denominator": denominator, "disagreements": disagreements, "holds": denominator > 0 and agree == denominator}


def planted_failures(tables: dict[str, dict[str, object]]) -> dict[str, object]:
    out: dict[str, object] = {}
    # P1: claimed DOUBLE table off by one instruction at one t.
    enumerated = list(tables["DOUBLE"]["C_bits"])
    first_solvable = next(t for t, v in enumerate(enumerated, start=1) if v is not None)
    claimed = list(enumerated)
    claimed[first_solvable - 1] = enumerated[first_solvable - 1] + BITS_PER_INSTRUCTION
    cmp = compare_claimed_table("DOUBLE", claimed, enumerated)
    if not cmp["rejected"]:
        raise AssertionError("P1 planted wrong DOUBLE table was not rejected")
    out["P1_wrong_claimed_table_rejected"] = {"claimed": claimed, "comparison": cmp, "fired": True}
    # P2: inconsistent family refused with the distinct error.
    try:
        TaskFamily("INCONSISTENT", [(1, 0), (1, 1)])
    except InconsistentFamily as exc:
        out["P2_inconsistent_family_refused"] = {"error_type": type(exc).__name__, "message": str(exc), "fired": True}
    else:
        raise AssertionError("P2 inconsistent family was accepted")
    return out


def mutation_controls(
    families: Sequence[TaskFamily], honest_tables: dict[str, dict[str, object]], honest_cache: SignatureCache
) -> dict[str, object]:
    out: dict[str, object] = {}

    # M1 simulator ignoring the time bound: applied iff the reported step count
    # differs from the honest one on a concrete witness (REP 1 on x=3: 4 steps).
    witness = ((REP, 1),)
    honest_run = simulate_a(witness, 3, T_MAX)
    mutated_run = simulate_ignoring_time_bound(witness, 3, T_MAX)
    if honest_run == mutated_run or honest_run[1] != 4:
        raise AssertionError("M1 not applied")
    cache_m1 = SignatureCache(simulate=simulate_ignoring_time_bound)
    tables_m1 = {f.name: cache_m1.exact_table(f) for f in families}
    frontier_m1 = check_frontier(tables_m1)
    out["M1_simulator_ignores_time_bound"] = {
        "applied": True,
        "witness": {"program": format_program(witness), "x": 3, "honest": list(honest_run), "mutated": list(mutated_run)},
        "programs_enumerated": cache_m1.programs_enumerated,
        "frontier_holds_under_mutation": frontier_m1["holds"],
        "qualifying_families_under_mutation": frontier_m1["qualifying_families"],
        "detected": frontier_m1["holds"] is False,
        "registered_reason": "frontier check (strict decreases) must fail",
    }

    # M2 enumerator skipping length 2 in the iterative-deepening path.
    n_honest = sum(1 for _ in enumerate_programs(2))
    n_mut = sum(1 for _ in enumerate_programs_skipping_length_2(2))
    if not (n_honest == len(INSTRUCTIONS) ** 2 and n_mut == 0):
        raise AssertionError("M2 not applied")
    id_m2 = iterative_deepening_tables(families, enumerate_fn=enumerate_programs_skipping_length_2)
    agreement_m2 = no_alarm_agreement(honest_tables, id_m2["tables"])
    out["M2_enumerator_skips_length_2"] = {
        "applied": True,
        "witness": {"length_2_programs_honest": n_honest, "length_2_programs_mutated": n_mut},
        "programs_enumerated": id_m2["programs_enumerated"],
        "agreement": {"agree": agreement_m2["agree"], "denominator": agreement_m2["denominator"]},
        "disagreement_examples": agreement_m2["disagreements"][:3],
        "detected": agreement_m2["holds"] is False,
        "registered_reason": "the two independent computations must disagree",
    }

    # M3 cost function returning len(program) instead of bits.
    if description_len_not_bits(witness) == description_bits(witness) or description_len_not_bits(witness) != 1:
        raise AssertionError("M3 not applied")
    sub_m3 = check_subadditivity(families, honest_cache, bits=description_len_not_bits)
    w = sub_m3["failure_witness"]
    matches_registered = w is not None and all(w[k] == v for k, v in REGISTERED_SUBADDITIVITY_FAILURE.items())
    out["M3_bits_function_returns_len"] = {
        "applied": True,
        "witness": {"program": format_program(witness), "honest_bits": description_bits(witness), "mutated": description_len_not_bits(witness)},
        "recorded_witness_under_mutation": w,
        "registered_expectation": REGISTERED_SUBADDITIVITY_FAILURE,
        "detected": matches_registered is False,
        "registered_reason": "assertion on the exact recorded witness values must fail",
    }

    for name, row in out.items():
        if not row["detected"]:
            raise AssertionError(f"{name} not detected")
    return out


# ----------------------------------------------------------------------------
# Runner
# ----------------------------------------------------------------------------

_CACHE: dict[str, object] | None = None


def run_exact_calibration(use_cache: bool = True) -> dict[str, object]:
    global _CACHE
    if use_cache and _CACHE is not None:
        return _CACHE
    t0 = time.perf_counter()
    families = registered_families()
    cache = SignatureCache()
    tables = {f.name: cache.exact_table(f) for f in families}
    ident = iterative_deepening_tables(families)
    agreement = no_alarm_agreement(tables, ident["tables"])
    mono_t = check_monotone_in_time(tables)
    mono_f = check_monotone_in_family(families, tables)
    frontier = check_frontier(tables)
    census = frontier_census(cache)
    sub = check_subadditivity(families, cache)
    unsolv = unsolvable_report(tables)
    planted = planted_failures(tables)
    mutations = mutation_controls(families, tables, cache)

    if not agreement["holds"]:
        raise AssertionError(f"independent computations disagree: {agreement['disagreements'][:3]}")
    if not mono_t["holds"]:
        raise AssertionError(f"monotonicity in time violated: {mono_t['violations'][:3]}")
    if not mono_f["holds"]:
        raise AssertionError(f"monotonicity in the family violated: {mono_f['violations'][:3]}")
    if not frontier["holds"]:
        raise AssertionError("no registered family shows a trade-off frontier")
    if not sub["found_failure_and_holding_pair"]:
        raise AssertionError("subadditivity: failure witness or holding pair not found")
    w = sub["failure_witness"]
    if any(w[k] != v for k, v in REGISTERED_SUBADDITIVITY_FAILURE.items()):
        raise AssertionError(f"subadditivity failure witness {w} != registered {REGISTERED_SUBADDITIVITY_FAILURE}")
    if any(v == 0 for row in tables.values() for v in row["C_bits"]):
        raise AssertionError("a C(F; t) of 0 was recorded; unsolvable must be None, not 0")
    if unsolv["count"] == 0:
        raise AssertionError("no unsolvable (F, t) within cap; the infeasibility path was not exercised")

    result: dict[str, object] = {
        "schema": "orion.ocm.lane202-core-frontier.exact-results.v1",
        "terminal": "PASS_TOY_CORE_FRONTIER_EXACT",
        "model": {
            "isa": {
                "OUT c": "a := c; halt",
                "ADD c": "a := (a + c) mod 8; pc += 1",
                "REP c": "if x > 0: a := (a + c) mod 8; x -= 1; pc unchanged else pc += 1",
                "DEC": "x := max(x - 1, 0); pc += 1 (operand carried, ignored)",
                "JZ k": "pc := k if x == 0 else pc + 1",
                "JMP k": "pc := k",
                "HALT": "halt (operand carried, ignored)",
                "off_end": "halt",
            },
            "inputs": list(INPUTS),
            "accumulator_modulus": MOD,
            "distinct_instructions": len(INSTRUCTIONS),
            "bits_per_instruction": BITS_PER_INSTRUCTION,
            "L_MAX": L_MAX,
            "T_MAX": T_MAX,
            "programs_enumerated": cache.programs_enumerated,
            "programs_per_length": cache.programs_per_length,
            "distinct_signatures": len(cache.table),
            "runs_executed": cache.runs_executed,
            "iterative_deepening_programs_enumerated": ident["programs_enumerated"],
            "iterative_deepening_runs_executed": ident["runs_executed"],
        },
        "families": [f.as_dict() for f in families],
        "tables": tables,
        "monotone_in_time": mono_t,
        "monotone_in_family": mono_f,
        "frontier": frontier,
        "frontier_census": census,
        "subadditivity": {k: v for k, v in sub.items() if not k.startswith("_")},
        "unsolvable": unsolv,
        "controls": {
            "no_alarm_independent_agreement": agreement,
            "planted_failures": planted,
            "mutation_controls": mutations,
            "M0_unmutated": {"applied": True, "all_checks_pass": True},
        },
        "runtime_seconds": round(time.perf_counter() - t0, 3),
        "authority": {
            "finite_toy_model_only": True,
            "all_size_authority": "hand proof in theory/OCM_LANE_202_TERMINAL_V1.md (Kolmogorov invariance / conservation; parent-owned)",
            "novelty_established": False,
            "architecture_separation": False,
            "transformer_equivalence_proved_here": False,
        },
    }
    _CACHE = result
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = run_exact_calibration()
    except CannotCheck as exc:
        print(json.dumps({"terminal": "CANNOT_CHECK", "reason": str(exc)}, indent=2))
        return 2
    except AssertionError as exc:
        print(json.dumps({"terminal": "FAIL", "error": str(exc)}, indent=2))
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, default=str))
    else:
        m = result["model"]
        sub = result["subadditivity"]["failure_witness"]
        fr = result["frontier"]["witness"]
        print(
            f"PASS lane-202 core frontier: {m['programs_enumerated']} programs enumerated "
            f"({m['runs_executed']} runs) at L_MAX={m['L_MAX']}, T_MAX={m['T_MAX']}; "
            f"frontier witness {fr['family']} {fr['C_bits']}; subadditivity fails at "
            f"{sub['F1']} u {sub['F2']}, t={sub['t']}: {sub['C_union']} > {sub['C_F1']} + {sub['C_F2']}; "
            f"{result['unsolvable']['count']}/{result['unsolvable']['denominator']} (F,t) unsolvable within cap; "
            f"{len(result['controls']['mutation_controls'])} mutations detected; {result['runtime_seconds']} s"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
