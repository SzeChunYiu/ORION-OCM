# FREEZE_V1 amendment 1 — exact formalization of `P-a` .. `P-d` and of the
# family lift, fixed before any receipt exists

`FREEZE_V1` §2 fixed the universe, the scored window, the next-state reading and
the two dominance metrics, but left the four frozen properties in the prose form
`Z13-P1` states them in. Scoring cannot proceed on prose. This amendment fixes
the formalization **before any receipt, RESULT file or verdict exists in this
package**; git order proves it. No rule of §2–§5 is weakened.

Write `out_m(st, cur)` and `next_m(st, cur)` for the mode-indexed tables of a
candidate at budget `b`, and `r_now, r_delay1, r_delay2` for its exact rational
error rates on the declared scored window.

- **`P-a`** — "output depends on both the state and the current input, and on
  neither alone in a way that makes the other redundant" is scored as: there
  exists a mode `m` with both
  `exists cur: out_m(0, cur) != out_m(1, cur)` and
  `exists st: out_m(st, 0) != out_m(st, 1)`.
  The per-mode truth table is reported, not only the disjunction.

- **`P-b`** — "its next-state function is the current input" is scored under two
  lifts, both reported, the first primary:
  - `P-b/all` : `next_m(st, cur) = cur` for **every** mode `m`;
  - `P-b/determined` : `next_m(st, cur) = cur` for every mode whose next-state
    function affects the candidate's cost (at `b = 1` the immediate-copy mode's
    next-state function does not).
  `P-b/all` is primary because `Z13-P1` says "its next-state function", of the
  morphology, without restriction.

- **`P-c`** — `r_now = 0` and `r_delay1 = 0` and
  `0 < r_delay2 = R0(delay2 | b = 1)`, all as exact rationals.

- **`P-d`** — no candidate that is a member of any of the six registered named
  families simultaneously satisfies `P-a`, `P-b`, `P-c` **and** is a unique cost
  minimiser somewhere in the predicted niche. The six families are lifted from
  Z6's address map `a = 4*st + 2*mode + cur` to the three-mode map
  `(st, mode, cur)` entry-for-entry:
  - `F_STATELESS` : `b = 0`;
  - `F_DEAD_TABLE` : `out_m(0, cur) = out_m(1, cur)` for all `m, cur`;
  - `F_FROZEN_STATE` : every `next_m` is constant (Z6's `nxt in {0, 255}`);
  - `F_MOORE` : `out_m(st, 0) = out_m(st, 1)` for all `m, st`;
  - `F_MEALY_PURE` : not `F_MOORE`;
  - `F_IDENTITY_STATE` : `next_m(st, cur) = cur` for all `m` (Z6's
    `nxt = 0b10101010`, whose set bits are exactly the odd addresses, i.e.
    `cur = 1`).

  Per `FREEZE_V1` §3 `H-4`, if the bundle `P-a and P-b and P-c` is unsatisfiable
  at `b = 1` then `P-d` is recorded `VACUOUSLY_TRUE` and `H-4` fails.

**A consequence that follows from the lift alone and is recorded now, before the
enumeration runs:** under `P-b/all` the predicate `P-b` is *definitionally
identical* to membership in `F_IDENTITY_STATE`. Whether that makes `H-3` and
`H-4` jointly unsatisfiable is a question of logic, not of data, and the executor
must report it as a derivation with its premises, never as a measurement.

No neighboring row is earned by this amendment.
