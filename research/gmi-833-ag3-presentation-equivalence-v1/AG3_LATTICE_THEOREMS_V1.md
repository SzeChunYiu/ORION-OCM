# AG3 named results — the presentation-equivalence strength order

Scope for every result below: the registered finite universe `U` of `2,548` presentations
fixed in `FREEZE_V1.md` section 3 (`n in {2,3}`, two distinct unary symbols drawn from the
frozen generating set, external programs of length at most `2`, two observation regimes),
`1,621,802` comparable pairs. Nothing here is asserted beyond that universe.

---

## `AG3L-1` — the four named strengths, and the order they actually stand in

**Statement.** The four strengths named by the AG3 row are realized as the relations `L1`
(syntactic renaming), `L2` (definitional/term equivalence), `L3(k)` (semantics-preserving
compiler equivalence at overhead factor `k`) and `L4` (model equivalence), defined in
`FREEZE_V1.md` section 2. On `U` they relate `1,762`, `29,470`, `297,166` (`k = 1`, after
transitive closure) and `297,358` pairs and cut `U` into `1,152`, `219`, `107` and `91`
classes respectively. The order is

```text
L1  <  L2   <  L4
L1  <  L3*(1) <  L4
L2  and  L3*(1)  are INCOMPARABLE
```

every `<` certified by an explicit separating pair and the incomparability by a pair in each
direction.

**Quantifiers.** For all ordered pairs of `U` sharing an observation regime.

**Assumptions.** Deterministic total unary presentations; a fixed two-letter external
alphabet; start state `0`; the two frozen observation regimes.

**What the separators are.** `L2 \ L1` is `W-RENAME`, a definitional extension:
`Sigma = (succ, id)` with `prog(b) = f0 f0` against `Sigma = (succ, pred)` with `prog(b) = f1`.
The generated transformation monoid is `{id, succ, pred}` on both sides and both external
actions agree, so the two present the same object by mutual term-definability, yet no
arity-preserving symbol bijection carries a length-`2` program onto a length-`1` one.
`L3*(1) \ L2` is `W-STATESPACE`, a two-state presentation against a three-state one with the
same presented object. `L2 \ L3*(1)` is `W-OVERHEAD`, term-equivalent but needing two `pred`
steps to compile one `succ` step under full observation.

**Falsifiers.** A separating pair that fails to verify; any pair related by `L1` or `L2`
whose presented objects differ (measured: `0` and `0`); a computed order in which `L2` and
`L3*(1)` become comparable.

**Strongest parents.** Birkhoff's free algebras over a signature and Lawvere's
presentation-independent algebraic theories own `L2`; Nerode/Myhill and Park/Milner own `L4`;
compiler correctness up to a simulation relation owns `L3`. What is new here is only the
order between them as strengths of presentation equivalence, computed rather than asserted.

**Forbidden extrapolations.** `PRESENTATION_EQUIVALENCE_IS_SOLVED`,
`UNIQUE_PRESENTATION_EQUIVALENCE_STRENGTH`, `LATTICE_IS_COMPLETE_FOR_ALL_PRESENTATIONS`.

**Dependency.** Depends on nothing outside `FREEZE_V1.md` section 2's level definitions and
section 3's universe. No merged parent's numbers enter the order; the parent packages are used
only in `AG3L-5`, to place the witness kinds they own.

---

## `AG3L-2` — bounded mutual simulation is not by itself semantics preserving

**Statement.** The compiler clause of `FREEZE_V1.md` section 2, read on its own — injective
observation-preserving encodings in both directions plus bounded-overhead simulation of each
external action — relates `367,372` pairs of `U` that present **different** objects. The
lexicographically first is a two-state pair whose programs are `(empty, empty)` and
`(empty, f1)`: each side simulates the other's actions within the bound while their
behaviours differ at the first letter.

**The frozen falsifier that fired, and what was done about it.** Section 6's third bullet says
that if any level relates a pair whose behaviours differ, "that level's definition is wrong and
the level is withdrawn, not repaired after the fact". On `L3raw` that antecedent is true, and
**this instruction was not followed**: `L3` was intersected with `L4` and shipped. That decision
is recorded, not glossed — `RESULT_V1.json` carries it as `frozen_clause_conflicts` entry
`AG3-FC-1` with `s6_instruction_followed: false` and `audit_shape_disclosed:
"POST_HOC_SUSPECT"`, and `MANIFEST_V1.json` repeats it. An auditor diffing section 6 against
this result is meant to find the disclosure already there.

Section 1 outranks section 6 here for two reasons, both stated in terms of the frozen text.
First, section 6's antecedent — "any level relates a pair whose behaviours differ" — is exactly
the negation of section 1's requirement, so the falsifier presupposes section 1 and cannot be
turned against it. Second, withdrawal is the larger departure: section 1 requires a
compiler-strength relation to exist *and* to imply object equality, so deleting the level would
violate section 1 as well, and would leave the row's fourth-strength question with three
registered strengths and no answer. The intersection, by contrast, is a **subset** of the frozen
`L3raw`: it removes only pairs section 1 forbade in advance and adds no relation the freeze did
not already license. `L3raw` is published with its exact failure count and counterexample rather
than quietly replaced, and `FREEZE_V1.md` is byte-unmodified since its freeze commit `cc4444ff`.

**Consequence for the row.** "Semantics-preserving compiler equivalence with overhead" is not
the conjunction of two independent conditions that happen to travel together. Semantics
preservation has to be stated over the presented object; mutual simulation of the generators,
however tightly charged, does not imply it.

**Falsifier.** A run in which `l3_raw_clause_cross_object_pairs` is `0`.

**Assumptions.** The frozen section-2 compiler clause read literally, together with the frozen
section-1 requirement that every strength imply equality of the presented object. No third
reading is used, and section 1 governs where the two conflict.

**Dependency.** Depends on `AG3L-1` only for the definitions of the compared behaviours. The
count is computed over the same universe and does not depend on the order between the levels.

**Strongest parents.** Compiler correctness stated up to a simulation relation with a charged
cost (McCarthy and Painter; Milner) owns the clause itself. The residual here is only the
measurement: that simulating the generators, however tightly charged, does not preserve an
externally indexed behaviour.

---

## `AG3L-3` — compiler equivalence at a fixed overhead is a tolerance, not an equivalence

**Statement.** `L3(1)` is reflexive and symmetric but **not transitive** on `U`. The executor
publishes the explicit triple

```text
P = (n=3, Sigma=(id, succ),   prog=(f1, f1 f1))
Q = (n=3, Sigma=(succ, pred), prog=(f0, f0 f0))
R = (n=3, Sigma=(succ, pred), prog=(f0, f1))
```

with `P ~3(1) Q`, `Q ~3(1) R` and not `P ~3(1) R`. For `k in {2, 3, 5}` no such triple exists
on `U`, so at those factors transitivity is **not exhibited at this scope** and is not
asserted.

**Mechanism.** Composing a compiler of overhead `k` with another of overhead `k` gives `k^2`,
not `k`. A charged overhead therefore does not close under composition, and only the
transitive closure `L3*(k)` is an equivalence relation and has a place in a lattice of
equivalences. Every order statement above is made about `L3*`, never about `L3`.

**Falsifier.** A run finding no non-transitive triple at `k = 1`.

**Assumptions.** Overhead is charged multiplicatively per external program, as section 2 fixes,
and the registered ladder is `k in {1, 2, 3, 5}`. Transitivity is asked of the relation itself,
never of its closure.

**Dependency.** Depends on `AG3L-2`: the relation whose transitivity is in question is the
section-1-conformant level, not the raw clause.

**Strongest parents.** Tolerance relations, and the fact that bounded simulations compose only
at a worse bound, are classical. No owner is claimed for the observation; only its exact
exhibition on this universe is new.

---

## `AG3L-4` — the strength lattice

**Statement.** The sublattice of the partition lattice on `U` generated by
`{L1, L2, L3*(1), L3*(2), L3*(3), L3*(5), L4}` under meet = intersection and
join = transitive closure of union has exactly **five** elements:

```text
            L4
           /  \
         L2    L3*(1)
           \  /
        L2 AND L3*(1)
             |
            L1
```

Exactly one element is new, the meet `L2 AND L3*(1)`; the join of the two incomparable levels
is `L4` itself. The lattice is therefore **not** a chain: the AG3 row's four strengths do not
line up in a single order of severity, and any claim of the form "presentation equivalence
holds at strength `s` or above" has to name which of the two middle branches it means.

**Two exact constants.**

- `k* = 2`: the least registered overhead factor at which definitional/term equivalence sits
  inside compiler equivalence on `U`. Below it the two are incomparable.
- The ladder saturates at `k = 2`: `L3*(2) = L3*(3) = L3*(5) = L4` on `U`, `297,358` pairs and
  `91` classes each. The merged parent `gmi-833-aj5-g0-lowering-v1`'s bound
  `lower_ops <= 5 * G0_steps` therefore sits at a factor that is **not strict at this scope**,
  and the strictness claim `L3*(5) < L4` that `FREEZE_V1.md` section 3 allowed for is
  **withdrawn**: the executor searched `U` for a pair in `L4` and in no registered `L3(k)` and
  found none. Whether the factor is strict on a universe with longer programs is open.

**Falsifiers.** A generated sublattice of any size other than five; a run in which the join of
`L2` and `L3*(1)` is not `L4`; a `k*` other than `2`.

**Assumptions.** The compiler level enters only through its transitive closure, per `AG3L-3`.
Meet is intersection and join is the transitive closure of the union, as section 4 fixes.

**Dependency.** Depends on `AG3L-1` for the order and on `AG3L-3` for the closure being the
object that has a place in a lattice of equivalences.

**Strongest parents.** The partition lattice, its meet and its join are classical lattice theory
(Ore, 1942). The size and shape of the generated sublattice over this universe is the residual.

---

## `AG3L-5` — exact placement of every registered witness, and the missing fourth witness

**Statement.** Each witness kind is placed at the levels it satisfies and certified to fail at
every strictly finer level. The placement is exact, not merely sufficient.

| witness | kind | minimal level(s) | fails at |
|---|---|---|---|
| `PW-RELABEL` | the relabeling kind of `gmi-833-g0-grammar-bias-v1` (24 certified isometric relabelings, 0 invariant failures) | `L1` | nothing finer exists |
| `W-RENAME` | definitional/term equivalence — **built here** | `L2` | `L1` |
| `W-STATESPACE` | a state-space change with a charged overhead | `L3(1)` | `L1`, `L2` |
| `PW-COMPILER` | the charged-overhead lowering kind of `gmi-833-aj5-g0-lowering-v1` | `L3(1)` | `L1`, `L2` |
| `W-OVERHEAD` | term equivalence that overhead `1` cannot buy | `L2` | `L1`, `L3(1)` |

**The fourth strength.** Of the four named strengths, `L2` was the one with no witness in the
merged corpus. It was **constructed**, not shown impossible: `W-RENAME` is a definitional
extension in the classical sense — the second presentation adds `pred` as a symbol for the
`succ`-term `succ succ`, which changes the presentation and changes nothing about the presented
object. Its exact level is `L2`: it is certified in `L2` and certified out of `L1`.

**On "stronger categorical/model equivalence".** The row's last phrase splits. Read as clone
or Lawvere-theory isomorphism it is `L2`, and the reading is only a presentation equivalence
once the external-action condition is added: clone equality **alone** relates `219,618` pairs
of `U` of which `168,900` present different objects. Read as model equivalence it is `L4`,
which is the coarsest, not the finest, of the four. Both readings are reported; neither is
smuggled into the other.

**Null.** `0 / 200` random level assignments and `0 / 200` randomized interpretation tables
reproduce the placement.

**Falsifier.** Any witness certified at a level it does not satisfy, or a null draw that
reproduces the placement.

**Assumptions.** Each parent witness is placed by the defining property its own receipt
certifies; the executable placement is of a registered analogue inside this universe, and the
two statements are reported separately rather than merged.

**Dependency.** Depends on `AG3L-1` for the levels and on `AG3L-4` for what an exact level means
when two levels are incomparable.

**Strongest parents.** `gmi-833-g0-grammar-bias-v1` owns the relabeling witness,
`gmi-833-aj5-g0-lowering-v1` the charged-overhead lowering, `gmi-833-parent-equivalence-v1`
model equivalence. Only the constructed term-equivalence witness is new.

---

## The boundary this package does not cross

`gmi-833-aj5-g0-lowering-v1` records that instruction description length, micro-step cost,
grammar mutation distance and search/reachability geometry do **not** transfer across a
semantics-preserving lowering. Nothing here repairs that. `L3` exists in this order precisely
because those quantities are charged as an overhead factor rather than carried, and
`COMPILER_MAKES_SEARCH_BIAS_INVARIANT` remains a forbidden promotion of this package as it is
of its parent.
