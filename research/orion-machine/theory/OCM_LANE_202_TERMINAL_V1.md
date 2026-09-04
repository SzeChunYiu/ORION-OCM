# Lane #202 terminal record — core–memory–time resource frontier

**Terminal: `TRADEOFF_FRONTIER_ONLY`.**
**Residual `STRICT_CORE_RESOURCE_RESIDUAL`: `NOT_EARNED`.**
**Comparator equivalence (`TRANSFORMER_EQUIVALENT_UNDER_MATCHED_RESOURCES`): `CANNOT_CHECK` — no matched
comparator manifest is registered; nothing was compiled, so nothing was compared.**

Date: 2026-09-04 · Umbrella: ORION-V2 #194 · Execution master: #197 · Lane: #202
Exact checker: `reference/ocm_lane202_core_frontier_exact.py` · Tests: `tests/unit/test_ocm_lane202_core_frontier_exact.py`

**Status: NO NOVELTY OR BREAKTHROUGH CLAIM.** Every exact figure below is from an exhaustive
enumeration on a deliberately tiny machine; every all-size statement is attributed to a named
parent. No review is issued or simulated; #199 and #245 remain unreturned.

## 0. Substrate-form restatement (operator directive, #194 comment 5539487737, 2026-09-04)

The lane was chartered as "the theorem object behind *fewer neurons*". Under the directive the
object of study is the substrate, so the question becomes **the cost of the substrate itself**:
what does a minimal self-extending machine pay, in immutable description bits, for the procedures it
learns — and how does that cost trade against the time and mutable memory it is allowed? The
quantity is `C_core*(F; t)`, the least description of a procedure that solves task family `F`
within time `t` on a fixed substrate. Theorem F4 below is the directive's word *minimal* made
exact: the substrate's own description enters every such cost as an additive interpreter constant,
so "a smaller core" is a statement relative to a substrate and is never free of that substrate's
size. Comparison with any named architecture (fixed/recurrent Transformer, SSM, NTM/DNC, retrieval)
is an *emergent-form* question the directive leaves open; it is recorded as `CANNOT_CHECK` here
because no matched manifest exists to compare against.

## 1. The exact object

Machine (checker docstring, §"Machine model"): input `x ∈ {0,1,2,3}`, accumulator mod 8, seven
opcodes × four operands = 28 instructions, `BITS_PER_INSTRUCTION = ceil(log2 28) = 5`; a run that
has not halted after `t` executed instructions fails the bound `t`. `C_core*(F; t)` is the minimum
of `5·len(P)` over every program `P` of length `1..4` that solves `F` within `t`, or
`UNSOLVABLE_WITHIN_CAP` (a distinct value, never `0`).

Denominators: `28 + 784 + 21,952 + 614,656 = 637,420` programs enumerated, `2,549,680` runs,
`1,831` distinct behaviour signatures; 14 registered families × `T_MAX = 8` = 112 `(F, t)` cells,
of which 32 are unsolvable within the cap. Two independent computations (signature-cached full
enumeration with `simulate_a`; iterative deepening with the separately written `simulate_b`, no
cache) agree on 112/112.

## 2. Exact tables (bits; `—` = unsolvable within cap)

| family | t=1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | witness at first finite t |
|---|---|---|---|---|---|---|---|---|---|
| `CONST_5` | — | 10 | 10 | 10 | 10 | 10 | 10 | 10 | `ADD 2; ADD 3` |
| `IDENTITY` | — | — | — | 5 | 5 | 5 | 5 | 5 | `REP 1` |
| `DOUBLE` | — | — | — | 5 | 5 | 5 | 5 | 5 | `REP 2` |
| `TRIPLE_MOD8` | — | — | — | 5 | 5 | 5 | 5 | 5 | `REP 3` |
| `IS_ZERO` | — | 15 | 15 | 15 | 15 | 15 | 15 | 15 | `JZ 2; OUT 0; OUT 1` |
| `PARITY` | — | — | — | — | — | — | — | — | none of length ≤ 4 |
| `SUCC` | — | — | — | — | 10 | 10 | 10 | 10 | `ADD 1; REP 1` |
| `IDENTITY_ENDPOINTS` | — | 10 | 10 | 5 | 5 | 5 | 5 | 5 | `JZ 2; OUT 3` then `REP 1` |
| `IS_ZERO_ZERO` | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | `OUT 1` |
| `IS_ZERO_NONZERO` | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | `OUT 0` |

(`DOUBLE_LO/HI`, `IDENTITY_LO/HI` are the half-domain pieces used by the subadditivity check.)

## 3. Theorems

**F1 (monotonicity).** `C_core*(F; t)` is non-increasing in `t` and non-decreasing in `F` under
inclusion (with `UNSOLVABLE` ordered as `+∞`). *Proof.* Both are minima over a feasible set that
grows with `t` and shrinks with `F`. ∎ Checked: 98 time comparisons, 72 subfamily comparisons, 0
violations. *Parent.* Time-bounded Kolmogorov complexity `C^t(x)` is non-increasing in `t`
(Li–Vitányi, *An Introduction to Kolmogorov Complexity*, ch. 7; Levin's `Kt`). `PARENT_OWNED`.

**F2 (trade-off frontier exists).** `IDENTITY_ENDPOINTS` costs 10 bits at `t = 2` (a two-instruction
dispatch `JZ 2; OUT 3`) and 5 bits at `t = 4` (the loop `REP 1`, which needs four steps on `x = 3`).
So a smaller core buys its saving with time: exactly the trade the lane was told to report as a
trade, not a win. *Parent.* Size–time trade-offs of resource-bounded description complexity
(Li–Vitányi ch. 7; the abstract form is Blum's speed-up phenomenon). `PARENT_OWNED`. **Cap
limitation, stated:** a census of all `9^4 − 1 = 6,560` task families on the 4-point domain finds
**0** with two finite-to-finite strict decreases at `L_MAX = 4` — the frontier available at this cap
is one level deep. This is a property of the cap, not a theorem about the machine; an earlier
`L_MAX = 3` pass found no finite-to-finite decrease at all, which is why the cap was raised once and
then frozen.

**F3 (subadditivity fails exactly).** With `F1 = IS_ZERO_NONZERO`, `F2 = IS_ZERO_ZERO` on disjoint
domains, `C(F1 ∪ F2; 2) = 15 > 5 + 5 = C(F1; 2) + C(F2; 2)`. The excess is the dispatch instruction
(`JZ`) that routes between the two one-instruction solutions: **sharing a core costs routing bits.**
The same code path also finds cells where subadditivity holds, so the check can fail in either
direction. *Parent.* Subadditivity of description complexity holds only up to an additive term —
`K(x, y) ≤ K(x) + K(y) + O(log)` — and the toy's `O(1)` is 5 bits per dispatch (Li–Vitányi §2.1,
§3.9). This is the *full-system honesty rule* of #194 §4 at the smallest scale: a resource moved
into a shared core reappears as control. `PARENT_OWNED`.

**F4 (invariance: the substrate's own cost).** For two substrates `U`, `U'` with interpreters of
each other, `|C_{U'}*(F; t') − C_U*(F; t)| ≤ c_{U,U'}` with `t'` a constant-factor slowdown of `t`
and `c` the interpreter's description. *Proof.* Kolmogorov's invariance theorem, with the time
overhead of interpretation charged. ∎ *Consequence for the directive.* "OCM needs a smaller immutable
core than `X`" is well-posed only as `C_OCM* + |interp_OCM| versus C_X* + |interp_X|`; the
substrate's own description is `B_static` in the #194 resource vector and can never be dropped
from the comparison. `PARENT_OWNED` (Kolmogorov 1965; Solomonoff 1964; Chaitin 1966).

## 4. What the lane's remaining checkboxes get

| #202 task | Disposition |
|---|---|
| define `C_core*(F; memory, time, verification, IO, precision)` | defined on the toy machine over `(description, time)`; the other coordinates are `0` on this machine (no memory, verifier, IO or precision model) and are *not* claimed |
| monotonicity / subadditivity | F1 proved and checked; F3 exact failure witness, and a holding cell, from one code path |
| natural task families with lower-bound machinery | the toy families are exhaustive, so lower bounds are by enumeration; no natural family with an asymptotic lower bound was registered — `NOT_OBTAINED` |
| OCM upper bounds and strongest-comparator lower bounds under matched manifests | `CANNOT_CHECK`: no comparator manifest (fixed Transformer, recurrent Transformer, SSM, NTM/DNC, retrieval) is registered, nothing was compiled |
| count static libraries, mutable memory, steps, verifier, preprocessing, training data | only `(B_theta, T_seq)` exist here; F4 places the interpreter in `B_static` |
| Warrant Lift / compiled-warrant state as coordinates | Warrant Lift is `H_0(L|B)` (lane #200, Thm A) and enters the resource vector as `B_mut` for the warrant store — see `OCM_OPERATIONAL_SEMANTICS_V1.md` §4 |
| frontier, not one point | F2 with the cap limitation stated |
| strongest-parent simulation/equivalence | F4 is the parent-owned equivalence-up-to-a-constant; no strict residual |
| mechanize finite lemmas | `CANNOT_CHECK` here: no proof-assistant toolchain provisioned (lane #203 record) |
| record terminal | `TRADEOFF_FRONTIER_ONLY` |

## 5. Controls

No-alarm: two independent computations agree 112/112. Planted: `P1` a claimed `DOUBLE` table off by
one instruction at `t = 4` is rejected against the enumerated table (mismatch listed); `P2` an
inconsistent family is refused with the distinct error `InconsistentFamily`, not reported
unsolvable. Mutations, each asserted applied on a concrete witness *before* its check: `M1`
simulator ignoring the time bound → frontier check fails (no qualifying family); `M2` enumerator
skipping every length-2 program → the two computations disagree (99/112); `M3` description cost
`len(P)` instead of bits → the registered witness `(5, 5, 15)` becomes `(1, 1, 3)` and the exact
assertion fails. `M0` unmutated passes. Exit contract: `0` pass, `1` fail, `2` `CANNOT_CHECK` (never a
pass). Runtime ≈ 7.6 s under Python 3.12.13.

## 6. Non-consequences and reopen conditions

Supported: F1–F4 on the toy machine, exactly; all-size forms are the parents'. Not supported:
parameter efficiency, "fewer neurons", any architecture comparison, novelty, priority, language,
quantum, publication readiness. No checkbox in #197 is closed by this file (OPS-012).

Reopens if: a matched comparator manifest is registered and compiled against the same task
families (then the terminal may become `TRANSFORMER_EQUIVALENT_UNDER_MATCHED_RESOURCES` or a named
residual); or a natural family with an asymptotic lower bound is registered and its OCM upper bound
proved; or an independent review finds a defect in F1–F4.
