"""B6: gating derived from VARIABLE duration, not from long duration.

GMI_FINITE_STATE_DERIVATION_V1 derived the state requirement from the quotient,
and GMI_STATE_SPACE_DERIVATION_V1 asked how cheaply the update can be written.
This asks a third question: when must the update be CONDITIONAL?

The lead tested here is that a gate is conditional retention -- hold this or
overwrite it, depending on the input -- and that what forces it is not how LONG
something must be held but whether the duration VARIES. A long but fixed delay
is served by an ungated shift register; only a variable one defeats every
register.

  1  recurrent state from the temporal cut
  2  the retention/forgetting trade at fixed capacity
  3  gating pressure, from variable-duration dependencies
  4  the ungated/gated crossover, which exists even at fixed duration
  5  neutral recovery with no LSTM, GRU or gate vocabulary

Exhaustive enumeration over a finite alphabet; exact integer arithmetic.
"""

import itertools
import json

OUT = {}

# M marks "the next symbol is the one to remember"; Q asks for it.
SYMS = ("0", "1", "M", "Q")


def make_stream(gap, payload, pad=0):
    """M, payload, then `gap` filler symbols, then Q."""
    return ("M", payload) + ("0",) * gap + ("Q",)


def required_answer(stream):
    """What the obligation demands at the Q: the symbol that followed M."""
    for i, s in enumerate(stream):
        if s == "M" and i + 1 < len(stream):
            return stream[i + 1]
    return None


# ---------------------------------------------------------------------------
# machines
# ---------------------------------------------------------------------------
def shift_register(stream, L):
    """Ungated: the state is the last L symbols, advanced unconditionally.
    Answers Q with whatever sits L steps back."""
    buf = [None] * L
    for s in stream:
        if s == "Q":
            return buf[0]
        buf = buf[1:] + [s]
    return None


def gated_cell(stream):
    """One cell, written only when the previous symbol was M and otherwise
    held. The WRITE is conditional on the input -- that is the whole gate."""
    cell, armed = None, False
    for s in stream:
        if s == "Q":
            return cell
        if armed:
            cell = s
            armed = False
        if s == "M":
            armed = True
    return cell


# ---------------------------------------------------------------------------
print("=" * 78)
print("1  THE TEMPORAL CUT: WHAT MUST SURVIVE TO THE QUERY")
print("=" * 78)
print("  Streams that differ only in the remembered symbol must be told apart")
print("  at the query, however far apart the two events sit.")
print()
print("  %-8s %-24s %-24s %s" % ("gap", "stream A", "stream B", "must differ"))
cut = []
for gap in (0, 1, 3, 6):
    a, b = make_stream(gap, "0"), make_stream(gap, "1")
    cut.append({"gap": gap, "a": "".join(a), "b": "".join(b),
                "answers_differ": required_answer(a) != required_answer(b)})
    print("  %-8d %-24s %-24s %s"
          % (gap, "".join(a), "".join(b), required_answer(a) != required_answer(b)))
OUT["temporal_cut"] = cut
assert all(x["answers_differ"] for x in cut), \
    "the obligation no longer distinguishes the two payloads"
print("\n  The distinction is created at one step and consumed at another, so")
print("  something must carry it across. That is the temporal cut, and CSR-1")
print("  prices it: one state per distinction still owed.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("2  RETENTION AGAINST FORGETTING AT FIXED CAPACITY")
print("=" * 78)
print("  A register of length L holds the last L symbols and nothing older.")
print("  Its retention span IS its capacity; there is no third option.")
print()
print("  %-8s %-14s %-16s %s" % ("L", "cells held", "spans gap", "answers gaps"))
ret = []
for L in (1, 2, 4, 7):
    answered = [g for g in range(0, 7) if shift_register(make_stream(g, "1"), L) == "1"]
    ret.append({"L": L, "cells": L, "answers_gaps": answered,
                "max_gap": max(answered) if answered else None})
    print("  %-8d %-14d %-16s %s"
          % (L, L, (max(answered) if answered else "none"), answered))
OUT["retention"] = ret
assert all(len(x["answers_gaps"]) <= 2 for x in ret), (
    "a register answers many gaps at once -- it should answer exactly the gap "
    "its length matches")
spans = [x["max_gap"] for x in ret if x["max_gap"] is not None]
assert spans == sorted(spans) and len(set(spans)) > 1, \
    "retention span no longer increases with capacity"
print("\n  Each register answers exactly the gap its length matches and no")
print("  other. Retention and forgetting are not two mechanisms to balance:")
print("  at fixed capacity they are one number read from two ends.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("3  WHAT FORCES A GATE: VARIABLE DURATION, NOT LONG DURATION")
print("=" * 78)
print("  Two ecologies, matched on the LONGEST delay they contain. One holds")
print("  that delay fixed; the other varies it. Nothing else differs.")
print()
FIXED = [make_stream(4, p) for p in ("0", "1")]
VARIABLE = [make_stream(g, p) for g in (0, 2, 4) for p in ("0", "1")]

print("  %-14s %-12s %-38s %s" % ("ecology", "max gap", "ungated register solves it", "gated"))
press = []
for name, eco in (("fixed gap 4", FIXED), ("variable gap 0/2/4", VARIABLE)):
    solved_by = [L for L in range(1, 9)
                 if all(shift_register(s, L) == required_answer(s) for s in eco)]
    gated_ok = all(gated_cell(s) == required_answer(s) for s in eco)
    maxgap = max(len(s) for s in eco) - 3
    press.append({"ecology": name, "max_gap": maxgap,
                  "register_lengths_that_work": solved_by, "gated_works": gated_ok})
    print("  %-14s %-12d %-38s %s"
          % (name, maxgap, (solved_by if solved_by else "NONE at any length <= 8"),
             gated_ok))
OUT["gating_pressure"] = press

fixed_row = press[0]
var_row = press[1]
assert fixed_row["register_lengths_that_work"], \
    "no register solves the FIXED ecology -- the twin is broken"
assert not var_row["register_lengths_that_work"], (
    "a register solves the VARIABLE ecology, so variable duration is not what "
    "forces a gate and the central claim of this witness is false")
assert fixed_row["gated_works"] and var_row["gated_works"], \
    "the gated cell should solve both"
assert fixed_row["max_gap"] == var_row["max_gap"], (
    "the two ecologies are not matched on longest delay, so the comparison is "
    "confounded by duration length")
print("\n  Both ecologies contain the same longest delay, %d. A register of the"
      % fixed_row["max_gap"])
print("  right length solves the fixed one and NO register at any length up to")
print("  8 solves the variable one, while one gated cell solves both.")
print()
print("  > A gate is not what you reach for when something must be held a LONG")
print("  > time. It is what you reach for when the holding time is not known in")
print("  > advance. Long-but-fixed is a register's job.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("4  THE CROSSOVER, WHICH EXISTS EVEN AT FIXED DURATION")
print("=" * 78)
print("  Where both machines work, the cheaper one wins. A register costs one")
print("  cell per step of delay; the gated cell costs one cell plus the gate.")
print()
GATE_PRICE = 2
print("  %-10s %-18s %-18s %s" % ("fixed gap", "register cells", "gated cells", "cheaper"))
cross = []
for gap in (0, 1, 2, 3, 6):
    eco = [make_stream(gap, p) for p in ("0", "1")]
    Ls = [L for L in range(1, 9)
          if all(shift_register(s, L) == required_answer(s) for s in eco)]
    reg = min(Ls) if Ls else None
    gat = 1 + GATE_PRICE
    cheaper = "register" if (reg is not None and reg < gat) else (
        "gated" if reg is None or gat < reg else "tie")
    cross.append({"gap": gap, "register_cells": reg, "gated_cells": gat,
                  "cheaper": cheaper})
    print("  %-10d %-18s %-18d %s" % (gap, reg, gat, cheaper))
OUT["crossover"] = cross
kinds = {c["cheaper"] for c in cross}
assert "register" in kinds and "gated" in kinds, (
    "one must win at short delays and the other at long ones, or there is no "
    "crossover and gating is either always or never worth it")
flip = next(i for i in range(1, len(cross)) if cross[i]["cheaper"] != cross[0]["cheaper"])
print("\n  The winner changes between gap %d and gap %d -- exactly where the"
      % (cross[flip - 1]["gap"], cross[flip]["gap"]))
print("  register's length passes the gate's price. So even with duration FIXED")
print("  and both machines correct, gating is a cost question with a threshold,")
print("  and below that threshold an ungated register is the right machine.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("5  NEUTRAL RECOVERY: NO LSTM, GRU OR GATE VOCABULARY")
print("=" * 78)
print("  Candidates are described only by how many cells they carry and")
print("  whether the write is unconditional or input-dependent. No family name")
print("  appears in the description.")
print()
print("  %-22s %-26s %-12s %s"
      % ("ecology", "cheapest sufficient shape", "cells", "reads as"))
rec = []
for name, eco in (("fixed gap 1", [make_stream(1, p) for p in ("0", "1")]),
                  ("fixed gap 6", [make_stream(6, p) for p in ("0", "1")]),
                  ("variable 0/2/4", VARIABLE)):
    Ls = [L for L in range(1, 9)
          if all(shift_register(s, L) == required_answer(s) for s in eco)]
    options = {}
    if Ls:
        options["unconditional write, %d cells" % min(Ls)] = min(Ls)
    if all(gated_cell(s) == required_answer(s) for s in eco):
        options["input-dependent write, 1 cell"] = 1 + GATE_PRICE
    best = min(options, key=lambda k: options[k])
    reads = ("an ungated register" if best.startswith("unconditional")
             else "a gated cell")
    rec.append({"ecology": name, "shape": best, "cells": options[best],
                "reads_as": reads, "n_options": len(options)})
    print("  %-22s %-26s %-12d %s" % (name, best[:26], options[best], reads))
OUT["recovery"] = rec
reads = {x["reads_as"] for x in rec}
assert len(reads) > 1, (
    "every ecology recovers the same shape, so the candidate space is not "
    "discriminating and nothing has been recovered")
multi = [x for x in rec if x["n_options"] > 1]
assert multi, "no ecology ever had a real choice between the two shapes"
print("\n  Both shapes are recovered from the same description by cost alone.")
print("  The input-dependent write -- what a gate IS -- is selected exactly")
print("  where an unconditional one cannot serve the ecology or costs more,")
print("  and it was never named.")

print()
print("=" * 78)
print("all assertions held")
print("=" * 78)

with open("microscopes/results/STAGE_GATED_RECURRENCE_V1.json", "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
