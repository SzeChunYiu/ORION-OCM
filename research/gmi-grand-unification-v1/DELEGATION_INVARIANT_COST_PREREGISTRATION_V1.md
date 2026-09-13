# Delegation-invariant cost coordinate: preregistration and repair

Status: **REGISTERED COORDINATE REPAIR; FINITE STATIC WITNESSES; NO MEASUREMENT,
NO UNIVERSAL FAMILY VERDICT**

This document registers the coordinate before it is used to score any new task
family. It repairs the defect recorded as SN-7, and it does not re-open the
delegated-family exclusion that iteration 29 withdrew.

## 1. The original implication and its counterexample

`GRAND_GMI_STRUCTURAL_NEURAL_BOUND_RECEIPT_V1.json` registered the coordinate
`python_opcode_count_per_full_domain_sweep`. It counts opcodes executed in the
candidate's own frame. `sum` and `int` are C builtins with no `__code__`, so
work moved into them leaves the measure entirely. The receipt records the
consequence in its own fields:

| realization | opcodes per sweep | candidate-frame calls |
|---|---|---|
| written XOR | 88 | 0 |
| `sum(x) & 1` | 48 | 8 |
| written shared-sum threshold net | 312 | 32 |
| threshold net written with `s = sum(x)` | 256 | 40 |

So a non-neural realization that delegates its summation scores below the
written XOR it is supposed to lose to, and a member of the excluded class
scores below that class's derived per-sweep bound of 312. No minimality claim
and no coverage claim is sound in this coordinate while that holds.

## 2. The registered correction

**DIC-1 (coordinate).** `python_static_cost_vector_per_full_domain_sweep` is the
pair `(opcodes, unaccounted_calls)`, both totalled over the eight-input domain
sweep, computed statically from `dis` instructions over the same straight-line
grammar and the same opcode contract as STR-1–5.

**DIC-2 (accounting rule).** At each call the callee is resolved statically.
A callee carrying a Python code object is **accounted**: the instrument recurses
into it and adds its own accounted opcodes, so its work does not leave the
measure. A callee with no Python code object is **unaccounted**: its work cannot
be attributed at all, and the call is charged to the second component. The
instrument never estimates a callee's internal work.

**DIC-3 (refusal).** The instrument refuses, rather than guessing, on: an opcode
it does not model, a callee that is not a statically resolved named global, a
bound-method call, a recursive callee, nesting beyond the registered limit of 8,
and any realization outside the straight-line grammar. Refusal is proved in
`test_grand_gmi_delegation_invariant_cost_v1.py`, never on the registered path.

**DIC-4 (order).** One product order, written as minimization. `A` dominates `B`
when `A` is no greater in both components and strictly smaller in at least one.
Incomparability is a real outcome and is reported as such, not broken by a tie
rule.

**DIC-5 (anti-gaming monotonicity).** Let `R` be a registered realization and
`E(R)` any export of written work out of its frame. Either the callee carries a
Python code object, and DIC-2 charges its opcodes here, so `E(R)` pays `R`'s
opcodes plus the wrapper's and is dominated by `R`; or it does not, and the
unaccounted component strictly rises, so `E(R)` is incomparable to `R`. In
neither case does `E(R)` dominate `R`. A change that genuinely lowers both
components is a real improvement and is allowed to dominate; that is the
intended behaviour, not a gap.

**DIC-6 (bound transport).** `certified_lower` is a static syntactic count, so
the opcode component's proved minimum is unchanged: **39 per call, 312 per
sweep**. What changes is that the class bound is no longer a scalar: it is a
frontier in `(opcodes, unaccounted_calls)`, and the attaining written witness
carries 32 unaccounted calls per sweep.

## 3. Observed values under the registered coordinate

| realization | (opcodes, unaccounted calls) |
|---|---|
| written XOR | (88, 0) |
| `sum(x) & 1` | (48, 8) |
| written lookup table | (136, 0) |
| written shared-sum threshold net | (312, 32) |
| threshold net delegating the sum | (256, 40) |
| written four-threshold DNF net | (472, 40) |

Both SN-7 gaming realizations become **incomparable** to the realization they
previously beat. Both written-against-written exclusions survive: written XOR
dominates the written shared-sum net and the written DNF net.

## 4. Alternatives evaluated and rejected, on the record

**A scalar charge per delegated call.** Rejected. The smallest weight that
restores both SN-7 orderings is `w = 8`, and it is fitted from the very
comparison it is meant to decide. An outcome-fitted constant is not a derived
accounting rule. The threshold is retained in the receipt as a negative witness.

**A delegation-free normal form with a proof that every realization has one.**
Rejected as preregistered work: that is a universal coverage claim over an
unenumerated space, which CU-3b places outside what can be asserted without a
cover proof. It belongs to P2, not here.

**A dynamic `sys.setprofile` charge for C-level calls.** Not registered. The
39/312 derivation is static, so a dynamic count is not commensurable with it,
and opcode tracing in this sector has a recorded history of interpreter-specific
failure (the V1 first-frame defect and the CPython 3.13 priming workaround).
It remains available as an unregistered cross-check.

## 5. What this does not establish

- No universal exclusion of delegating realizations. Iteration 29 withdrew that,
  and this repair does not restore it. Two opaque wrappers with different
  descendants still score identically, and the coordinate abstains between them.
- No measurement of a callee's internal work, no timing, no memory, no physical
  cost ordering.
- No coverage of realizations outside the registered straight-line grammar.
- No independent replication: this is a static derivation on one interpreter
  family's opcode layout, and it refuses rather than guessing when that layout
  does not validate.

## 6. Boundaries this result does not cross

1. No total exact solver for unrestricted Turing-complete instances is claimed.
2. No development law is derived; this is a static cost coordinate only.
3. No universal family verdict without a coverage proof: the residue stays
   `ROBUST_WITHIN_COVERED_CLASSES_WITH_OPEN_RESIDUE`.
4. No timing envelope is converted into a bound; nothing here is timed.
5. No claim of independent replication by an independent party.
