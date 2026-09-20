# V14 adjudication: one original optional-structure requirement

Only **GMI2-R1-008 — formalize stochastic/nondeterministic optional structure**
is eligible. Its original evidence_kind is FORMAL_OR_FINITE and its owner is
#1068/R1. Neither title nor historical record is rewritten. #833 remains a
historical parent; it does not become the successor control plane.

Original source: ../gmi-1068-grand-unified-v2-r0/ATOMIC_CHECKLIST_V1.json.
Original scope: ../gmi-1068-r1-minimal-process-core-v1/FREEZE_V1.md, result4,
with result6 parent ownership and results7-8 formal/executable evidence.
V14 freeze: `dc138c35bd37949ff5845c92532fe597437e93dd`.
Mathematical warrants: [THEORY_V14.md](THEORY_V14.md).

## Exact formalization being earned

Finite normalized nonnegative matrices, with first-then-second matrix product,
form a category including empty objects. Total relations on arbitrary types,
with existential composition, form another category. Functions embed faithfully
as Dirac matrices on finite sets and as singleton relations on arbitrary types.
The category laws and preservation properties are derived from actual operations.

Under explicitly declared zero-sum-free addition and no zero divisors, support
preserves identity and composition and gives a total relation. These support
hypotheses are primitive scalar facts; finite-sum support is derived from them.
They are not silently inferred from row normalization. Signed cancellation and
zero-divisor controls exhibit why the hypotheses cannot be erased.

The seven actual Bool kernels I,F,K_p, for p in {0,1/3,1/2,2/3,1}, form a closed
category with a faithful rational matrix interpretation. It includes all four
Bool functions and three genuinely stochastic kernels.
Two kernels with identical full support give event {true} probabilities 1/3 and 2/3.
Thus preserving possibility is insufficient to preserve probability information.
Uniformizing finite relations does not preserve sequential composition, as the
registered (1/2,1/4,1/4) versus (1/3,1/3,1/3) witness demonstrates.

These constructions fulfill the optional-instance formalization component of
the original requirement. They neither promote probability/nondeterministic
choice to universal primitives nor establish their elimination from every model.
They do not close the entirety of original R1 freeze result4, which also names
other structures and has separate atomic requirements.

## Required mathematical and executable evidence

The closure decision requires all frozen components, not this document alone:

- General finite-matrix proofs from primitive scalar laws; total relation proofs;
  faithful deterministic embeddings; support identity/composition/totality with
  a derived finite-sum lemma and explicit assumptions.
- Actual Std.Internal.Rat entries for the closed seven-arrow model; normalization,
  interpreted composition, faithful interpretation, category laws and the actual
  same-support/different-probability witness checked by the kernel.
- Complete independent Fraction calibration over all registered kernels, relations
  and maps of dimensions 0,1,2, including every typed pair/triple and identities.
  Intermediate kernels may leave the entry grid and must not be rounded or dropped.
- Empty-source/codomain distinction, tiny-positive support, reversed composition,
  malformed dimensions/scalars/maps/relations, support-hypothesis failures and
  the nonfunctorial uniformization counterexample.
- Exact Lean statement-type registrations, axiom/source inspection and source-valid
  proof mutants that compile as sources but fail the typed audit. A failed hash
  check alone does not demonstrate this proof-registration protection.
- Normal and optimized integrated receipts must agree; missing inputs/tools remain
  CANNOT_CHECK rather than success or ordinary checked-invalid evidence.

General nonnegative rational/real algebra-law instances are paper specializations,
not kernel theorems merely because the generic interface is quantified over S.
A concrete Nat instance checks consistency but cannot substitute for genuine
probability; normalized Nat rows are deterministic. The separate rational witness
fills that narrower nontrivial-instance requirement. No general measurable-space,
conditioning, disintegration or infinite-series theorem is claimed.

The generic interface includes Boolean weights. Therefore it does not imply
that every normalized {0,1}-valued matrix is a function. Faithful Dirac inclusion
is general; the usual {0,1}-matrix characterization additionally uses ordinary
rational/real probabilities. Exactly-one-supported-entry remains the general
Dirac-row criterion, proved on paper. The kernel matrix laws carry the full
Weight interface even where its support premises are unused. FORMAL_SCOPE_V14
records the precise proved interfaces.

## Preserved authority and counts

Original V13 baseline: 15 CLOSED (8 governance, 7 scientific), 207 unresolved.
After successful evidence and independent review, only R1-008 may become CLOSED:
16 CLOSED (8 governance, 8 scientific), 206 unresolved. Every other original atom,
its disposition, title and witness remains unchanged by this adjudication.
R1 and the overall GMI programme remain OPEN; only R0 is whole-round EARNED.

Classical mathematics remains parent-owned in [PARENTS_V14.json](PARENTS_V14.json).
No empirical novelty, canonical probability/prior, architecture recovery,
absolute primitive minimality, higher-cell elimination or complete GMI follows.
