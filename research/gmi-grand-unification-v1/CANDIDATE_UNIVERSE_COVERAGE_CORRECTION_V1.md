# Candidate-universe coverage correction — recursive audit CU-1

Date: 2026-09-13. Authority for the derived bounds used below:
`MORPHOLOGY_PHASE_LAW_DERIVATION_V1.md`.

## 1. Gap addressed

DC-4 of `NN_NONNN_DERIVATION_CERTIFICATE_AND_BOUNDARY_THEOREM_V1.md` states
that a family verdict is relative to the registered candidate universe
"unless a separate completeness theorem proves that all relevant physical
realizations have been covered". No such theorem existed. The recursive audit
recorded the same hole as an open-ended obligation: "a point verdict never
enumerates all physical machines."

Stated as enumeration, that obligation can never be discharged — the set of
physically legal machines is not finite, and unbuilt machines cannot be
listed. This correction replaces enumeration with a **decidable coverage
predicate over structure classes**, proves what a verdict means with it and
without it, and proves that the upgrade cannot be made without it.

## 2. CU-1 — coverage is validity of a disjunction

A family is the extension of a structural predicate (MS-5, PL-1), not a list.
So the registered classes `{sigma_F}` **cover** a population `Phys` exactly
when

\[
\boxed{\forall m\in Phys.\ \bigvee_F \sigma_F(m).}
\]

This is a logical condition on predicates. It can be discharged by a
structural dichotomy without enumerating members, and it remains meaningful
when `Phys` is infinite or unknown. Adjoining the complement predicate
`not(sigma_1) and ... and not(sigma_k)` always completes a cover, so the real
question is never whether a cover exists but whether every class in it carries
a derived bound.

That reframing is the whole content of this correction: coverage is cheap,
**bounded** coverage is not.

## 3. CU-2 — a covered dominating witness excludes all of physics

> **CU-2.** Suppose `{sigma_F}` covers `Phys`, each class has a PL-2 derived
> lower bound `L_F`, and a construction in class `A` has cost
> `U_A < L_F` for every `F != A`. Then no member of `Phys` outside `A` has
> cost at most `U_A`, whether or not anyone has built it.

### Proof

Let `m` in `Phys` lie outside `A`. By coverage `m` satisfies some `sigma_F`.
Since `m` is outside `A`, that class can be taken with `F != A`. PL-2 gives
`J(rho(m)) >= L_F`, and `L_F > U_A` by hypothesis. QED.

This is the statement DC-4 said requires "stronger coverage evidence", now
with an explicit and checkable premise. Its strength is exactly the strength
of the weakest derived bound in the cover.

## 4. CU-3 — without coverage, a verdict is not about physics

The witness instance makes the failure arithmetic. Over the registered
instance with the joint necessity registered, the two registered classes have
derived bounds `L_NEURAL = 18` and `L_NON_NEURAL = 14`, and a registered
non-neural construction of cost `16` robustly dominates both. The verdict over
those two classes is `NON_NEURAL`.

But the two predicates do not cover the admitted population: of `1344`
admitted allocations, `1105` satisfy neither. Adjoining the complement class
gives `L_RESIDUE = 12`, and `16 < 12` is false, so the verdict is **withdrawn**.
The residue is not a technicality: `19` admitted allocations in it cost strictly
less than the construction, and its bound `12` is attained by one of them.

So the earlier verdict was an artifact of incomplete coverage, not a fact about
the instance. The required report in that situation is

`ROBUST_WITHIN_COVERED_CLASSES_WITH_OPEN_RESIDUE`,

naming the covered classes, and it may not be printed as a family verdict.

> **CU-3b — non-upgradability.** Without a coverage proof, the covered-class
> verdict carries no information about the residue.

### Proof

Two extensions of the registered classes are each consistent with all
registered evidence and give opposite verdicts. Extending by the expensive
exotic class `{residue, t1 >= 6, t2 >= 6}` keeps `NON_NEURAL`; extending by the
full residue class withdraws it. Registered evidence does not distinguish
them, so no inference from the covered classes to the residue is licensed. QED.

## 5. CU-4 — coverage must be proved at the verdict's resolution

A cover of components does not lift to a cover of composites.

The single-site predicates `t = 0` and `t >= 1` cover every site cost. Lifted
across two sites by conjunction — `t1 = t2 = 0` and `t1, t2 >= 1` — they leave
`896` two-site allocations uncovered, among them `(w1,w2,t1,t2) = (2,1,0,1)`.

Mixed realizations are exactly what escapes such a lift, which is why hybrid
morphologies are the standard counterexample to a pure-family verdict. A
coverage proof must therefore be discharged at the resolution at which the
verdict is stated, not at the resolution of its components.

## 6. CU-5 — overlap is harmless, gaps are not

A cover need not be a partition. If `m` satisfies both `sigma_F` and
`sigma_G`, then PL-2 applies to each, so

\[
J(\rho(m))\ \ge\ \max(L_F,L_G).
\]

Overlapping classes therefore only strengthen the applicable bound, and
nothing in CU-2 requires disjointness. In the witness, the neural class and
the wider carrier class share `119` admitted allocations, and every one of
them respects the stronger bound `18` rather than the weaker `12`.

This matters practically: a registry may add a new overlapping structure class
freely, but may never leave a structural gap.

## 7. What this closes and what it does not

Closed: the coverage obligation is no longer an unbounded enumeration
requirement. It is a decidable predicate; a cover always exists; a verdict over
a proved bounded cover extends to unbuilt machines (CU-2); a verdict without one
must be reported with its residue and cannot be upgraded (CU-3, CU-3b);
coverage must be proved at the verdict's own resolution (CU-4); and overlap is
free (CU-5).

Not closed, and not closable this way:

- coverage is proved here for **one registered finite instance**, not for the
  physically legal set of any real substrate;
- a cover is only as strong as its weakest derived bound, and the complement
  class typically has a weak one, so completing a cover often *withdraws* a
  verdict rather than confirming it;
- PL-5 still applies: the residue class's bound cannot select anything without
  a construction;
- no enumeration, measurement or replication obligation in
  `RECURSIVE_GAP_AUDIT_20260913.md` is discharged.

Terminal: `GRAND_GMI_CANDIDATE_UNIVERSE_COVERAGE_GREEN_AT_FINITE_SCOPE`.

## 8. Parent mathematics and contribution boundary

The parent facts are elementary: validity of a disjunction, case analysis over
a cover, and monotonicity of an infimum under set inclusion. No novelty is
claimed for them. The contribution is the reframing of the registered
candidate-universe obligation from enumeration to a bounded-cover condition,
the CU-2 transfer theorem, the CU-3b non-upgradability proof, the
composition-resolution counterexample, and the exact finite witnesses.
