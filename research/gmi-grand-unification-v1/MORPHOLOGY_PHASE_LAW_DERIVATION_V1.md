# Grand GMI Morphology Phase Law — Derivation Layer V1

Status: **THEOREM / ONE-SIDED DERIVATION OF FAMILY-CONDITIONED BOUNDS + EXACT FINITE WITNESSES**
Date: 2026-09-13

Correction and scope authority: `RECURSIVE_GAP_AUDIT_20260913.md`,
`FAMILY_PHASE_SOUNDNESS_CORRECTION_V1.md`.

## 1. Gap addressed

`FAMILY_FRONTIER_PHASE_THEOREM_V1.md` compares family-conditioned bounds. Its
own §13 states the boundary plainly: the theorem "does not manufacture the
functions `L_F(s)` and `U_F(s)` for real substrates". The same holds of the
derivation certificate, whose C6 registers physical resource evidence as an
**input**. So the last arrow of the master chain,

`(kappa, tau, rho) => morphology`,

was a declared schema plus a comparator. Nothing in the package turned proved
cut and transformation necessities into a family bound.

This layer supplies that arrow, and proves exactly how far it reaches. It is
**one sided**: it derives lower bounds, never upper bounds. It therefore
explains exclusion, not selection.

## 2. Registered derivation instance

A derivation instance is

\[
\mathcal I=(\mathcal N,\ \Sigma_{\mathcal F},\ A,\ J,\ X),
\]

where:

- `N` is the set of **proved necessities** on an allocation vector `x`. Each
  necessity is a lower bound already established by the semantic-cut,
  transformation-complexity, symmetry, physical or developmental layers. A
  coordinate with no proved lower bound admits non-negativity only.
- `Sigma_F = {sigma_F}` are **structural family predicates** on morphology
  descriptors, in the sense of `MORPHOLOGY_SELECTION_THEOREM_V1.md` §2. A
  family is the extension of its predicate, never a historical name (MS-5).
- `A` is the declared **resource accounting map** from allocations to
  registered resource coordinates, nondecreasing in every argument.
- `J` is the declared scalar selection functional, nondecreasing in every
  resource coordinate.
- `X` is the registered allocation domain.

The **accounting-soundness contract** is a hypothesis of this layer:

> For every admitted machine `m` with allocation `x(m)`,
> `rho(m) >= A(x(m))` coordinatewise.

The accounting map must undercharge. It is a budget floor, not an estimate.

## 3. PL-1 — the relaxed accounting program

Define, for each family predicate,

\[
\boxed{
L_F=\inf\{J(A(x)):x\in X,\ x\models\mathcal N,\ \sigma_F(x)\}.
}
\]

Only the proved necessities and the structural predicate constrain `x`. Every
other feasibility condition — joint realizability, legality, reachability,
deployment adequacy — is **dropped**. The program is therefore a relaxation,
and its value is computable whenever `X` is finite and `J`, `A` are decidable.

## 4. PL-2 — derived family lower bound

> **PL-2.** Let `m` be any admitted machine that is physically legal, adequate,
> reachable and satisfies `sigma_F`. Under the accounting-soundness contract,
> `J(rho(m)) >= L_F`.

### Proof

`m` is admitted, so its allocation `x(m)` satisfies every proved necessity,
because a necessity holds of every admitted machine. It satisfies `sigma_F` by
assumption. Hence `x(m)` lies in the feasible set of the program, so
`J(A(x(m))) >= L_F`. Accounting soundness gives `rho(m) >= A(x(m))`
coordinatewise, and `J` is nondecreasing, so `J(rho(m)) >= J(A(x(m)))`.
Chaining the two inequalities gives the claim. QED.

Two consequences matter.

**It covers machines nobody has built.** The proof quantifies over the
structural predicate, not over a registered list of candidates. Any future,
undiscovered or exotic realization satisfying `sigma_F` is already bounded by
`L_F`. This is the only sense in which the present package makes a prospective
claim about unknown forms, and it is confined to the registered structure
class — see `CANDIDATE_UNIVERSE_COVERAGE_CORRECTION_V1.md` for the residue.

**Accounting soundness is load bearing.** If the map may overcharge in any
coordinate, the last inequality reverses and the bound fails. The checker
includes a machine whose accounting undercharges by construction; its scalar
cost is `10` against a derived bound of `18`.

## 5. PL-3 — relaxation looseness, and two causes of abstention

`L_F` can be strictly below every attainable cost, because the relaxation may
combine coordinates that no single feasible realization can combine. This is
the family-level form of the attainment defect that the master already
records: componentwise lower envelopes need not be attained.

Therefore an `UNDECIDED_FROM_CURRENT_EVIDENCE` verdict has **two distinct
causes**, which FP-2 did not separate:

1. **epistemic** — the derived bounds are loose, and a valid necessity not yet
   registered would resolve the comparison;
2. **physical** — the attainable sets genuinely overlap, and no additional
   necessity can separate them.

The exact witness exhibits cause 1. The registered non-neural construction
costs `16`. Against the relaxed neural bound `15` the comparison abstains;
against the refined neural bound `18`, obtained by registering one further
valid joint necessity, the same construction robustly excludes the neural
class. The physics never changed, only the evidence.

> **PL-3b — tightness certificate.** If every compared family's derived bound
> is attained by a registered construction, so that `L_F = U_F`, then the
> verdict computed from the intervals equals the verdict computed from the true
> family optima.

### Proof

Each interval is the singleton `{L_F}`, which is by hypothesis the family's
attained optimum. The strict-separation test on singletons is exactly the
comparison of optima. QED.

So abstention under tight bounds is physical, and abstention under untight
bounds is uninformative about physics. A phase diagram must therefore publish
its tightness status per region; otherwise its boundary regions cannot be
interpreted.

## 6. PL-4 — evidence refines monotonically; candidates do not

> **PL-4a.** Adding a valid necessity to the program cannot lower `L_F`.
> Hence a robust exclusion established from valid necessities is never lost by
> registering further valid necessities.

### Proof

A further necessity shrinks the feasible set, and an infimum over a subset is
at least the infimum over the set. The exclusion test `U_A < L_B` is
monotone in `L_B`. QED.

> **PL-4b.** Weakening a structural predicate cannot raise `L_F`, so a robust
> verdict **can** be lost by enlarging the structure class.

### Proof

A weaker predicate enlarges the feasible set and an infimum over a superset is
at most the infimum over the set. QED.

Together these give the exact asymmetry that DC-4 states informally: more
evidence is always safe, more candidates never are. The witness makes it
arithmetic. Dropping the shared-kernel restriction from the neural predicate —
admitting a heterogeneous-kernel neural form that no one had registered — drops
the derived bound from `18` to `12`, and the non-neural verdict is withdrawn.

## 7. PL-5 — the derivation is one sided

> **PL-5.** No relaxation program of this form can select a family. Two
> substrate worlds sharing every proved necessity share every derived lower
> bound, and can still have different verdicts.

### Proof

The program's value depends only on `N`, `sigma_F`, `A`, `J` and `X`. A verdict
additionally requires an upper bound, which only a construction supplies. The
witness exhibits two worlds with identical derived bounds `L_NEURAL = 18`,
`L_NON_NEURAL = 14`: where a non-neural construction of cost `16` exists the
verdict is `NON_NEURAL`; where instead only a neural construction of cost `18`
exists the verdict abstains, since `18 < 14` is false. QED.

Hence necessities exclude; constructions select. A phase diagram built from
necessities alone has robust-exclusion regions and abstention regions, and no
selection regions at all.

## 8. Exact finite witness

The registered witness instance has two cuts with widths `w1, w2`, two
transformation sites with costs `t1, t2`, allocation domain `0..7` in each
coordinate (`4096` allocations enumerated exhaustively), proved necessities
`w1 >= 2`, `w2 >= 1`, `t1 >= 3`, no proved lower bound on `t2`, accounting
`memory = w1 + w2`, `compute = t1 + t2`, and `J = memory + 2 * compute`.

Structural predicates: the neural class charges one shared kernel at both
sites (`t1 = t2`) with a widest-first carrier (`w1 >= w2`); the non-neural
class places a lookup at site 2 (`t2 = 0`) and carries the full key across cut
2 (`w2 >= 3`).

| Evidence state | `L_NEURAL` | `L_NON_NEURAL` |
|---|---:|---:|
| proved necessities only | 15 | 11 |
| plus the joint necessity `w1 + t1 >= 8` | 18 | 14 |

The enlarged heterogeneous-kernel neural class gives `12` in the refined
state. Four registered machines with sound accounting each respect their
family's derived bound; the undercharging machine breaks it at `10`.

These numbers verify the derivation logic. They are not measurements of any
real substrate.

## 9. What this adds, and what it does not

The master chain's final arrow is now a theorem rather than a schema, in one
direction:

\[
(\mathcal N\ \text{from}\ \kappa,\tau,G,\rho)\ +\ \sigma_F\ +\ A\ +\ J
\;\Longrightarrow\;
L_F
\;\Longrightarrow\;
\text{robust family exclusion}.
\]

It does **not** supply `U_F`, does not measure any substrate, does not produce
a selection from necessities, does not make the relaxation tight, and does not
establish that the registered structure classes cover the physically legal
set. The last of those is the subject of the candidate-universe coverage
correction. Real resource maps and large-scale learning evidence remain the
empirical obligations already listed in the recursive audit.

Terminal: `GRAND_GMI_MORPHOLOGY_PHASE_LAW_DERIVATION_GREEN_AT_FINITE_SCOPE`.

## 10. Parent mathematics and contribution boundary

The parent results are elementary: monotonicity of an infimum under set
inclusion, relaxation as a lower-bound technique in mathematical programming,
and monotone composition of nondecreasing maps. No novelty is claimed for
them. The contribution is the identification of the missing generator arrow in
the registered phase law, its one-sided repair under an explicit
accounting-soundness contract, the separation of epistemic from physical
abstention with a tightness certificate, and the exact evidence/candidate
asymmetry, each with an exhaustive finite witness.
